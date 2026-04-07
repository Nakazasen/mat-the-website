
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add current directory to path so we can import database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import supabase

async def check_chapter_805():
    chapter_num = 805
    target_locales = ["en", "zh-CN", "ja"]
    
    print(f"--- Checking Chapter {chapter_num} ---")
    
    # 1. Get chapter metadata (Vietnamese original)
    resp = supabase.table("chapters").select("id, title, content_url").eq("chapter_number", chapter_num).single().execute()
    if not resp.data:
        print(f"Chapter {chapter_num} not found in 'chapters' table.")
        return
    
    chapter_id = resp.data['id']
    vi_title = resp.data['title']
    print(f"Vietnamese Title: {vi_title}")
    
    # 2. Get translations
    trans_resp = supabase.table("chapter_translations") \
        .select("locale, title, content") \
        .eq("chapter_id", chapter_id) \
        .in_("locale", target_locales).execute()
    
    if not trans_resp.data:
        print(f"No translations found for Chapter {chapter_num} in locales {target_locales}.")
        return

    for trans in trans_resp.data:
        locale = trans['locale']
        title = trans['title']
        content = trans['content']
        
        print(f"\n--- Locale: {locale} ---")
        print(f"Title: {title}")
        
        # Take a snippet of content (first 500 characters)
        snippet = content[:500] if content else "(Empty content)"
        print(f"Content Snippet:\n{snippet}...")
        
        # Check for mojibake markers
        mojibake_markers = ['Ã', 'Â', 'ê', 'â', 'ô', 'ư', 'ơ', 'đ'] 
        # Note: 'ê', 'â', 'ô', 'ư', 'ơ', 'đ' are valid in Vietnamese but might be mojibake in en/zh/ja 
        # if they appear unexpectedly. 
        # Actually, mojibake often looks like 'Ã³', 'Ãª', etc.
        
        found_markers = []
        if locale != 'vi':
            # In English, Chinese, and Japanese, we don't expect many Vietnamese-specific characters 
            # unless they are names. But 'Ã' is a very common mojibake indicator.
            for char in ['Ã', 'Â', 'ê', 'â', 'ô', 'ư', 'ơ', 'đ']:
                 if char in title or char in content:
                     # Be careful: Names might have these. But 'Ã' is almost always bad.
                     if char == 'Ã':
                         found_markers.append(char)
                     elif locale in ['en', 'zh-CN', 'ja']:
                         # If we see many of these in non-Vietnamese, it's suspicious
                         found_markers.append(char)
        
        if found_markers:
            print(f"Potential Mojibake detected: {list(set(found_markers))}")
        else:
            print("No obvious mojibake detected.")

if __name__ == "__main__":
    asyncio.run(check_chapter_805())
