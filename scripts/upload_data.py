#!/usr/bin/env python3
"""
upload_data.py - Data Pipeline cho truyện Mạt Thế Sinh Hoá Nguy Cơ
Phiên bản 2.0 - Xử lý file .docx

Chức năng:
  1. Đọc file tổng (VD: 1-767.docx) và dùng Regex tách thành 767 chương
  2. Đọc các file lẻ (VD: chuong-768.docx, 768.docx...) rồi ghép vào
  3. Upload từng chương lên Cloudflare R2 (JSON)
  4. Upsert metadata (số chương, tiêu đề, URL) vào Supabase

Cài đặt thư viện:
  pip install python-docx boto3 supabase python-dotenv

Cách dùng:
  python upload_data.py                        # Upload tất cả
  python upload_data.py --dry-run              # Kiểm tra danh sách không upload
  python upload_data.py --start 100 --end 200  # Chỉ upload chương 100-200
  python upload_data.py --folder /path/to/dir  # Chỉ định thư mục khác
"""

import re
import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from docx import Document
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# === CONFIG ===
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
R2_ENDPOINT  = os.getenv("R2_ENDPOINT")
R2_ACCESS    = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET    = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET    = os.getenv("R2_BUCKET_NAME", "mat-the-chapters")
R2_PUBLIC    = os.getenv("R2_PUBLIC_BASE_URL", "").rstrip("/")

# === REGEX NHẬN DIỆN CHƯƠNG ===
# Nhận dạng cả các dòng có tiền tố như link web, tên truyện...
CHAPTER_HEADER_RE = re.compile(
    r"(?:.*?)Ch[uư][oơ]ng\s+(\d+)\s*[:\-–—]?\s*(.*)$",
    re.IGNORECASE,
)

# Regex nhận diện số chương từ tên file
FILE_NUMBER_RE = re.compile(r"(\d+)")


# ============================================================
# BÓC TÁCH NỘI DUNG TỪ FILE DOCX
# ============================================================

def read_docx(path: Path) -> str:
    """Đọc text từ file .docx, bỏ qua ảnh/bảng."""
    try:
        doc = Document(str(path))
        lines = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                lines.append(text)
        return "\n".join(lines)
    except Exception as e:
        log.error(f"❌ Không đọc được file {path.name}: {e}")
        return ""


# ============================================================
# TÁCH CHƯƠNG TỪ FILE TỔNG
# ============================================================

def split_chapters_from_text(text: str) -> list[dict]:
    """
    Dùng regex tách text thành danh sách chương.
    Trả về: [{"number": int, "title": str, "content": str, "word_count": int}, ...]
    """
    chapters = []
    lines = text.split("\n")
    
    current_number = None
    current_title  = None
    current_lines  = []

    for line in lines:
        stripped_line = line.strip()
        match = CHAPTER_HEADER_RE.match(stripped_line)
        # Giới hạn dòng < 150 ký tự để không lấy nhầm vào nội dung truyện
        if match and len(stripped_line) < 150:
            # Lưu chương trước đó (nếu có)
            if current_number is not None:
                content = "\n".join(current_lines).strip()
                chapters.append({
                    "number": current_number,
                    "title":  current_title or f"Chương {current_number}",
                    "content": content,
                    "word_count": len(content.split()),
                })
                log.info(f"  📖 Đã tách - Chương {current_number}: {current_title[:50]}")

            current_number = int(match.group(1))
            current_title  = match.group(2).strip() or f"Chương {current_number}"
            current_lines  = []
        else:
            if current_number is not None:
                current_lines.append(line)

    # Lưu chương cuối cùng
    if current_number is not None and current_lines:
        content = "\n".join(current_lines).strip()
        chapters.append({
            "number": current_number,
            "title":  current_title or f"Chương {current_number}",
            "content": content,
            "word_count": len(content.split()),
        })
        log.info(f"  📖 Đã tách - Chương {current_number}: {current_title[:50]}")

    return chapters


def parse_bulk_docx(file_path: Path) -> list[dict]:
    """Đọc file .docx gộp nhiều chương, tách ra từng chương."""
    log.info(f"📂 Đọc file tổng: {file_path.name} ({file_path.stat().st_size / 1024:.0f} KB)")
    text = read_docx(file_path)
    if not text:
        return []
    log.info(f"  🔍 Đang tách chương bằng Regex...")
    chapters = split_chapters_from_text(text)
    log.info(f"  ✅ Tìm thấy {len(chapters)} chương trong file tổng")
    return chapters


# ============================================================
# TÁCH CHƯƠNG TỪ FILE LẺ
# ============================================================

def guess_chapter_number_from_filename(filename: str) -> Optional[int]:
    """Đoán số chương từ tên file. VD: chuong-768.docx → 768"""
    numbers = FILE_NUMBER_RE.findall(Path(filename).stem)
    if numbers:
        # Lấy số lớn nhất (thường là số chương)
        return max(int(n) for n in numbers)
    return None


def guess_chapter_number_from_content(text: str) -> Optional[int]:
    """Tìm số chương từ dòng đầu tiên của nội dung."""
    for line in text.split("\n")[:10]:
        stripped_line = line.strip()
        match = CHAPTER_HEADER_RE.match(stripped_line)
        if match and len(stripped_line) < 150:
            return int(match.group(1))
    return None


def parse_single_docx(file_path: Path, override_number: Optional[int] = None) -> Optional[dict]:
    """Đọc file .docx chứa 1 chương duy nhất."""
    log.info(f"📄 Đọc file lẻ: {file_path.name}")
    text = read_docx(file_path)
    if not text:
        return None

    # Thử phát hiện số chương và tiêu đề từ nội dung
    chapter_number = override_number
    title = None

    for line in text.split("\n")[:10]:
        stripped_line = line.strip()
        match = CHAPTER_HEADER_RE.match(stripped_line)
        if match and len(stripped_line) < 150:
            chapter_number = chapter_number or int(match.group(1))
            title = match.group(2).strip() or None
            # Bỏ dòng tiêu đề ra khỏi nội dung
            text = text[text.index(line) + len(line):].strip()
            break

    # Nếu vẫn chưa tìm được số chương, thử từ tên file
    if chapter_number is None:
        chapter_number = guess_chapter_number_from_filename(file_path.name)

    if chapter_number is None:
        log.warning(f"  ⚠️  Không xác định được số chương: {file_path.name} - BỎ QUA")
        return None

    title = title or f"Chương {chapter_number}"
    content = text.strip()

    log.info(f"  📖 Chương {chapter_number}: {title[:50]}")
    return {
        "number": chapter_number,
        "title": title,
        "content": content,
        "word_count": len(content.split()),
    }


# ============================================================
# SCAN THƯ MỤC VÀ PHÂN LOẠI FILE
# ============================================================

def scan_folder(folder: Path) -> tuple[Optional[Path], list[Path]]:
    """
    Quét thư mục, phân loại file tổng và file lẻ.
    Returns: (bulk_file_or_None, [list_of_single_files])
    """
    if not folder.exists():
        log.error(f"❌ Thư mục không tồn tại: {folder}")
        return None, []

    docx_files = sorted(folder.glob("*.docx"))
    log.info(f"📁 Tìm thấy {len(docx_files)} file .docx trong {folder}")

    bulk_file   = None
    single_files = []

    for f in docx_files:
        stem = f.stem.lower()
        # File tổng: tên chứa dấu gạch nối giữa 2 số (VD: "1-767", "1 767")
        if re.search(r"\d+\s*[-–—]\s*\d+", stem):
            if bulk_file is None:
                bulk_file = f
                log.info(f"  📦 File tổng nhận diện: {f.name}")
            else:
                log.warning(f"  ⚠️  Có nhiều file tổng? Sẽ chỉ dùng: {bulk_file.name}")
        else:
            single_files.append(f)
            log.info(f"  📄 File lẻ: {f.name}")

    return bulk_file, single_files


# ============================================================
# CLOUDFLARE R2 UPLOAD
# ============================================================

def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS,
        aws_secret_access_key=R2_SECRET,
        region_name="auto",
    )


def upload_to_r2(s3, chapter_number: int, title: str, content: str, dry_run: bool) -> Optional[str]:
    key = f"chapters/chuong-{chapter_number:05d}.txt"
    payload = content

    if dry_run:
        log.info(f"    [DRY-RUN] R2: {key} ({len(payload.encode('utf-8'))} bytes)")
        return f"{R2_PUBLIC}/{key}"

    try:
        s3.put_object(
            Bucket=R2_BUCKET,
            Key=key,
            Body=payload.encode("utf-8"),
            ContentType="text/plain; charset=utf-8",
            CacheControl="public, max-age=31536000, immutable",
        )
        return f"{R2_PUBLIC}/{key}"
    except ClientError as e:
        log.error(f"    ❌ R2 upload thất bại ch.{chapter_number}: {e}")
        return None


# ============================================================
# SUPABASE UPSERT
# ============================================================

def upsert_supabase(sb, chapter_number: int, title: str, content_url: str, word_count: int, dry_run: bool) -> bool:
    row = {
        "chapter_number": chapter_number,
        "title": title,
        "content_url": content_url,
        "word_count": word_count,
    }

    if dry_run:
        log.info(f"    [DRY-RUN] Supabase upsert: ch.{chapter_number} - {title[:40]}")
        return True

    try:
        sb.table("chapters").upsert(row, on_conflict="chapter_number").execute()
        return True
    except Exception as e:
        log.error(f"    ❌ Supabase thất bại ch.{chapter_number}: {e}")
        return False


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Upload truyện Mạt Thế (.docx) lên R2 + Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--folder",
        default="mat-the-truyen",
        help="Thư mục chứa các file .docx (mặc định: mat-the-truyen/)",
    )
    parser.add_argument("--start", type=int, default=1,   help="Chương bắt đầu upload")
    parser.add_argument("--end",   type=int, default=99999, help="Chương kết thúc upload")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ kiểm tra, không upload thật")
    parser.add_argument("--delay", type=float, default=0.1, help="Giây nghỉ giữa các lần upload (tránh rate limit)")
    args = parser.parse_args()

    # Đường dẫn thư mục (relative từ vị trí của script này)
    script_dir = Path(__file__).parent
    folder = (script_dir / args.folder).resolve()

    # === VALIDATE ENV ===
    if not args.dry_run:
        missing = [k for k in ["SUPABASE_URL", "R2_ENDPOINT", "R2_ACCESS_KEY_ID",
                                "R2_SECRET_ACCESS_KEY", "R2_PUBLIC_BASE_URL"]
                   if not os.getenv(k)]
        if not (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")):
            missing.append("SUPABASE_SERVICE_KEY")
        if missing:
            log.error(f"Thiếu ENV variables: {', '.join(missing)}")
            sys.exit(1)

    if args.dry_run:
        log.info("🔸 DRY-RUN MODE — Sẽ không upload thật sự")

    # === SCAN THƯ MỤC ===
    bulk_file, single_files = scan_folder(folder)

    # === BÓC TÁCH CHƯƠNG ===
    all_chapters: list[dict] = []

    if bulk_file:
        log.info(f"\n📦 Bóc tách file tổng...")
        bulk_chapters = parse_bulk_docx(bulk_file)
        # Gom các số chương đã có để tránh trùng với file lẻ
        bulk_numbers = {c["number"] for c in bulk_chapters}
        all_chapters.extend(bulk_chapters)
    else:
        bulk_numbers = set()
        log.warning("⚠️  Không tìm thấy file tổng, chỉ xử lý file lẻ")

    if single_files:
        log.info(f"\n📄 Bóc tách {len(single_files)} file lẻ...")
        for f in single_files:
            ch = parse_single_docx(f)
            if ch and ch["number"] not in bulk_numbers:
                all_chapters.append(ch)
            elif ch:
                log.info(f"  ⏩ Chương {ch['number']} đã có trong file tổng, bỏ qua")

    # Sắp xếp theo số chương
    all_chapters.sort(key=lambda c: c["number"])

    # === LỌC THEO RANGE ===
    all_chapters = [c for c in all_chapters if args.start <= c["number"] <= args.end]

    log.info(f"\n{'='*55}")
    log.info(f"✅ Tổng cộng {len(all_chapters)} chương sẽ được xử lý")
    log.info(f"   Từ chương {all_chapters[0]['number']} đến {all_chapters[-1]['number']}" if all_chapters else "   (Không có chương nào)")
    log.info(f"{'='*55}\n")

    if not all_chapters:
        log.warning("Không có chương nào để xử lý!")
        sys.exit(0)

    if args.dry_run:
        log.info("📋 DANH SÁCH CHƯƠNG (DRY-RUN):")
        for c in all_chapters:
            log.info(f"  Ch.{c['number']:04d} | {c['word_count']:>5} từ | {c['title'][:60]}")
        log.info(f"\n🎯 Thực thi 'python upload_data.py' (không có --dry-run) để upload thật.")
        return

    # === INIT CLIENTS ===
    s3 = get_r2_client()
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)

    # === UPLOAD LOOP ===
    ok_count   = 0
    fail_count = 0
    total      = len(all_chapters)

    log.info("🚀 Bắt đầu upload...\n")
    for i, ch in enumerate(all_chapters):
        num   = ch["number"]
        title = ch["title"]
        bar_progress = int((i + 1) / total * 30)
        bar = f"[{'█' * bar_progress}{'░' * (30 - bar_progress)}]"

        print(f"\r{bar} {i+1}/{total} - Ch.{num:04d} '{title[:30]}...'", end="", flush=True)

        # 1. Upload nội dung lên R2
        url = upload_to_r2(s3, num, title, ch["content"], dry_run=False)
        if not url:
            fail_count += 1
            continue

        # 2. Upsert metadata lên Supabase
        ok = upsert_supabase(sb, num, title, url, ch["word_count"], dry_run=False)
        if ok:
            ok_count += 1
        else:
            fail_count += 1

        if args.delay > 0 and i < total - 1:
            time.sleep(args.delay)

    print()  # Newline sau progress bar
    log.info(f"\n{'='*55}")
    log.info(f"🎉 HOÀN TẤT!")
    log.info(f"   ✅ Thành công: {ok_count} chương")
    if fail_count:
        log.warning(f"   ❌ Thất bại:   {fail_count} chương")
    log.info(f"{'='*55}")


if __name__ == "__main__":
    main()
