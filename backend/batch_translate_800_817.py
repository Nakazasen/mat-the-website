import asyncio
import os
import traceback
import time
from dotenv import load_dotenv

# Import our refined main logic
import main

async def batch_translate(start_chapter: int, end_chapter: int):
    print(f"Starting batched translation for chapters {start_chapter} to {end_chapter}...")
    
    target_locales = ["en", "zh-CN", "ja"]
    print(f"Target locales: {target_locales}")

    for chapter_num in range(start_chapter, end_chapter + 1):
        try:
            # 1. Get chapter metadata
            resp = main.supabase.table("chapters").select("id, title, content_url").eq("chapter_number", chapter_num).single().execute()
            if not resp.data:
                print(f"Chapter {chapter_num} not found. Skipping.")
                continue
            chapter_row = resp.data
            
            # 2. Check existing translations status
            trans_resp = main.supabase.table("chapter_translations")\
                .select("locale, translation_status")\
                .eq("chapter_id", chapter_row['id'])\
                .in_("locale", target_locales).execute()
            
            existing_locales = {r['locale']: r['translation_status'] for r in trans_resp.data}
            
            # We translate if status is not 'translated' or 'published' or if it doesn't exist
            locales_to_translate = [l for l in target_locales if existing_locales.get(l) not in ['translated', 'published']]
            
            if not locales_to_translate:
                print(f"Chapter {chapter_num} already translated ({existing_locales}). Skipping.")
                continue

            print(f"\n--- Processing Chapter {chapter_num} for {locales_to_translate} ---")
            
            # 3. Fetch source content from R2
            content_text = main.fetch_r2_content(chapter_row["content_url"])
            if not content_text:
                print(f"Error: Could not fetch content for Chapter {chapter_num}")
                continue
            
            # 4. Attempt translation with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = await main.upsert_chapter_translations(
                        chapter_row=chapter_row,
                        title=chapter_row["title"],
                        content=content_text,
                        locales=locales_to_translate
                    )
                    
                    print(f"Result for Chapter {chapter_num}:")
                    print(f"  Success: {result.get('translated_locales')}")
                    print(f"  Failed: {result.get('failed_translations')}")
                    
                    # If some failed due to 503, we might want to retry those specifically, 
                    # but upsert_chapter_translations handles all at once.
                    # If everything succeeded or some failed but not with 503, we break.
                    break
                except Exception as e:
                    if "503" in str(e) or "high demand" in str(e).lower():
                        print(f"  Attempt {attempt+1} failed due to AI demand. Retrying in 10s...")
                        await asyncio.sleep(10)
                    else:
                        print(f"  Attempt {attempt+1} failed: {str(e)}")
                        break
            
            # Small delay between chapters to avoid rate limits
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"Critical error at Chapter {chapter_num}:")
            traceback.print_exc()
            await asyncio.sleep(5)

if __name__ == "__main__":
    load_dotenv(override=True)
    asyncio.run(batch_translate(800, 817))
