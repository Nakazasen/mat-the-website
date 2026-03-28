print("BOOTING LOCALIZATION SCRIPT...")
import asyncio
import os
import sys
from datetime import datetime, timezone

# Add the current directory to sys.path so we can import main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import (
    supabase,
    upsert_novel_translations,
    upsert_homepage_translations,
    upsert_wiki_translations,
    upsert_chapter_translations,
    SUPPORTED_LOCALES,
    DEFAULT_LOCALE,
    TRANSLATION_TARGET_LOCALES,
)

async def full_localize():
    print("STARTING FULL SITE LOCALIZATION...")
    
    # 1. Localize Novel Settings (Title, Author, Description)
    print("\n--- 1. LOCALIZING NOVEL METADATA ---")
    resp = supabase.table("novel_settings").select("*").eq("id", 1).single().execute()
    if resp.data:
        result = await upsert_novel_translations(resp.data, list(TRANSLATION_TARGET_LOCALES))
        print(f"DONE: Translated Novel Metadata to: {result['translated_locales']}")
        if result['failed_translations']:
            print(f"FAILED: Novel Metadata translations: {result['failed_translations']}")
    else:
        print("WARNING: Novel settings not found.")

    # 2. Localize Homepage Settings
    print("\n--- 2. LOCALIZING HOMEPAGE CMS ---")
    resp = supabase.table("homepage_settings").select("*").eq("id", 1).single().execute()
    if resp.data:
        result = await upsert_homepage_translations(resp.data, list(TRANSLATION_TARGET_LOCALES))
        print(f"DONE: Translated Homepage to: {result['translated_locales']}")
        if result['failed_translations']:
            print(f"FAILED: Homepage translations: {result['failed_translations']}")
    else:
        print("WARNING: Homepage settings not found.")

    # 3. Localize Wiki Entries
    print("\n--- 3. LOCALIZING WIKI ENTRIES ---")
    wiki_resp = supabase.table("wiki_entries").select("*").execute()
    entries = wiki_resp.data or []
    print(f"Found {len(entries)} wiki entries.")
    
    for entry in entries:
        print(f"Translating Wiki Entry: {entry['title']}...")
        result = await upsert_wiki_translations(entry, list(TRANSLATION_TARGET_LOCALES))
        print(f"  - Done: {result['translated_locales']}")
        if result['failed_translations']:
            print(f"  - Failed: {result['failed_translations']}")
        await asyncio.sleep(2) # Prevent rate limiting between entries

    # 4. Localize Chapters (Only missing ones for Chapters 1-100 to start)
    # The user mentioned chapters 33-814 are untranslated.
    # We'll batch them gradually to avoid massive token consumption in one go.
    print("\n--- 4. LOCALIZING CHAPTERS (Batch 33-816) ---")
    start_ch = 33
    end_ch = 816 # Process all remaining chapters
    
    for ch_num in range(start_ch, end_ch + 1):
        print(f"Translating Chapter {ch_num}...")
        try:
            # Check if already translated
            trans_resp = supabase.table("chapter_translations").select("locale").eq("chapter_number", ch_num).eq("translation_status", "published").execute()
            existing_locales = {r["locale"] for r in trans_resp.data}
            needed_locales = [l for l in TRANSLATION_TARGET_LOCALES if l not in existing_locales]
            
            if not needed_locales:
                print(f"  - Chapter {ch_num} already fully translated. Skipping.")
                continue
                
            result = await upsert_chapter_translations(ch_num, needed_locales)
            print(f"  - Done: {result['translated_locales']}")
            if result.get('failed_translations'):
                 print(f"  - Failed: {result['failed_translations']}")
            
            # Wait a bit between chapters
            await asyncio.sleep(10)
        except Exception as e:
            print(f"  - Error translating chapter {ch_num}: {e}")

    print("\nFULL LOCALIZATION COMPLETED!")

if __name__ == "__main__":
    asyncio.run(full_localize())
