import asyncio
import os
import sys
import argparse
import traceback
from datetime import datetime, timezone
from dotenv import load_dotenv

# Ensure stdout handles UTF-8 correctly on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add the current directory to sys.path so we can import main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import main

async def process_chapter(chapter_row: dict, target_locales: list[str], semaphore: asyncio.Semaphore):
    ch_num = chapter_row["chapter_number"]
    cid = chapter_row["id"]
    
    async with semaphore:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Bắt đầu dịch Chương {ch_num}: {chapter_row['title']}...")
        
        # 1. Fetch source content from R2
        try:
            content_text = main.fetch_r2_content(chapter_row["content_url"])
            if not content_text:
                print(f"  ❌ Lỗi: Không thể lấy nội dung R2 cho Chương {ch_num}")
                return False, f"Empty R2 content"
        except Exception as e:
            print(f"  ❌ Lỗi lấy nội dung R2 cho Chương {ch_num}: {e}")
            return False, f"R2 Fetch Error: {e}"

        # 2. Translate using main logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Rebuild router dynamically for fresh key config state
                main.build_provider_router_from_config(force_rebuild=True)
                
                result = await main.upsert_chapter_translations(
                    chapter_row=chapter_row,
                    title=chapter_row["title"],
                    content=content_text,
                    locales=target_locales
                )
                
                success_locales = result.get('translated_locales') or []
                failed_locales = result.get('failed_translations') or []
                
                if success_locales:
                    print(f"  ✅ Chương {ch_num} dịch thành công các ngôn ngữ: {success_locales}")
                if failed_locales:
                    print(f"  ⚠️ Chương {ch_num} có một số locale thất bại: {[f.get('locale') for f in failed_locales]}")
                    
                if not failed_locales:
                    return True, "Success"
                elif success_locales:
                    return True, f"Partial Success: {success_locales}"
                else:
                    return False, f"All target locales failed"
                    
            except Exception as e:
                err_str = str(e)
                if "503" in err_str or "high demand" in err_str.lower() or "rate limit" in err_str.lower() or "cooldown" in err_str.lower():
                    wait_time = 10 + attempt * 10
                    print(f"  ⚠️ Lượt {attempt+1} Chương {ch_num} lỗi quá tải hoặc Cooldown. Đang thử lại sau {wait_time} giây...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"  ❌ Lượt {attempt+1} Chương {ch_num} lỗi: {err_str}")
                    return False, f"Attempt failed: {e}"
        
        return False, "Failed after max retries"

async def main_async():
    parser = argparse.ArgumentParser(description="Ép dịch toàn bộ chương còn thiếu sang EN/ZH/JA")
    parser.add_argument("--start", type=int, default=1, help="Chương bắt đầu")
    parser.add_argument("--end", type=int, default=1000, help="Chương kết thúc")
    parser.add_argument("--limit", type=int, default=None, help="Giới hạn số chương dịch trong lần chạy này")
    parser.add_argument("--concurrency", type=int, default=3, help="Số luồng dịch song song")
    parser.add_argument("--only-missing", type=bool, default=True, help="Chỉ dịch những locale còn thiếu")
    args = parser.parse_args()

    load_dotenv(override=True)
    
    print("=" * 60)
    print("      HỆ THỐNG DỊCH CHƯƠNG TỰ ĐỘNG - MẠT THẾ SINH HOÁ NGUY CƠ      ")
    print("=" * 60)
    print(f"Tham số:")
    print(f" - Phạm vi chương: {args.start} -> {args.end}")
    print(f" - Luồng song song (Concurrency): {args.concurrency}")
    print(f" - Giới hạn số chương xử lý: {args.limit or 'Không giới hạn'}")
    print(f" - Chỉ dịch phần còn thiếu: {args.only_missing}")
    print("=" * 60)

    # 1. Fetch all chapters in range
    print("\n🔍 Đang truy vấn danh sách chương từ database...")
    chapters_resp = main.supabase.table("chapters")\
        .select("id, chapter_number, title, content_url")\
        .gte("chapter_number", args.start)\
        .lte("chapter_number", args.end)\
        .order("chapter_number")\
        .execute()
        
    all_chapters = chapters_resp.data or []
    print(f"-> Tìm thấy {len(all_chapters)} chương trong phạm vi cấu hình.")
    if not all_chapters:
        print("❌ Không tìm thấy chương nào!")
        return

    # 2. Get existing published translations to filter missing
    target_locales = ["en", "zh-CN", "ja"]
    translation_map = {}
    
    if args.only_missing:
        print("\n🔍 Đang kiểm tra trạng thái dịch các ngôn ngữ...")
        trans_resp = main.supabase.table("chapter_translations")\
            .select("chapter_id, locale")\
            .eq("translation_status", "published")\
            .in_("chapter_id", [ch["id"] for ch in all_chapters])\
            .execute()
            
        for row in (trans_resp.data or []):
            translation_map.setdefault(row["chapter_id"], set()).add(row["locale"])

    # 3. Filter list of chapters that actually need translation
    queue = []
    for ch in all_chapters:
        cid = ch["id"]
        ch_num = ch["chapter_number"]
        existing = translation_map.get(cid, set())
        missing = [l for l in target_locales if l not in existing]
        
        if missing:
            queue.append((ch, missing))
        elif not args.only_missing:
            queue.append((ch, target_locales))

    total_to_process = len(queue)
    print(f"-> Phát hiện {total_to_process} chương còn thiếu bản dịch.")
    
    if args.limit:
        queue = queue[:args.limit]
        print(f"-> Giới hạn xử lý {len(queue)} chương đầu tiên trong hàng đợi.")
        
    if not queue:
        print("🎉 Tuyệt vời! Toàn bộ chương trong phạm vi đã được dịch đầy đủ.")
        return

    print(f"\n🚀 Bắt đầu hàng đợi dịch song song (luồng: {args.concurrency})...")
    print("-" * 60)
    
    semaphore = asyncio.Semaphore(args.concurrency)
    
    success_count = 0
    failed_count = 0
    
    tasks = []
    for ch_item, missing_locales in queue:
        # Wrap task
        async def run_task(ch=ch_item, locales=missing_locales):
            nonlocal success_count, failed_count
            ok, msg = await process_chapter(ch, locales, semaphore)
            if ok:
                success_count += 1
            else:
                failed_count += 1
                
        tasks.append(run_task())
        
    # Execute with concurrency control
    await asyncio.gather(*tasks)
    
    print("\n" + "=" * 60)
    print("                     BÁO CÁO KẾT QUẢ                           ")
    print("=" * 60)
    print(f" - Tổng số chương đã xử lý: {success_count + failed_count}")
    print(f" - Thành công: {success_count}")
    print(f" - Thất bại: {failed_count}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main_async())
