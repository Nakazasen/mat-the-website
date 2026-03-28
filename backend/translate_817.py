import asyncio
import os
import json
import traceback
from dotenv import load_dotenv

# Import our refined main logic
import main

async def translate_817():
    chapter_num = 817
    print(f"Targeting Chapter {chapter_num} for re-translation...")
    
    try:
        # 1. Get chapter row
        resp = main.supabase.table("chapters").select("*").eq("chapter_number", chapter_num).single().execute()
        if not resp.data:
            print(f"Error: Chapter {chapter_num} not found in database.")
            return
        
        chapter_row = resp.data
        print(f"Found Chapter: {chapter_row['title']}")
        
        # 2. Fetch source content from R2
        content_text = main.fetch_r2_content(chapter_row["content_url"])
        print(f"Fetched content: {len(content_text)} chars")
        
        # 3. Call the hardened translation logic
        # This will handle the 3 locales (en, ja, zh-CN) simultaneously
        result = await main.upsert_chapter_translations(
            chapter_row=chapter_row,
            title=chapter_row["title"],
            content=content_text,
            locales=list(main.TRANSLATION_TARGET_LOCALES)
        )
        
        print(f"\nResult for Chapter {chapter_num}:")
        print(f"  Success Locales: {result.get('translated_locales')}")
        print(f"  Failed Locales: {result.get('failed_translations')}")
        
    except Exception as e:
        print(f"Critical error processing Chapter {chapter_num}:")
        traceback.print_exc()

if __name__ == "__main__":
    load_dotenv(override=True)
    asyncio.run(translate_817())
