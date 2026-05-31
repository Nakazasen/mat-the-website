import os
from dotenv import load_dotenv
from supabase import create_client

def main():
    load_dotenv(override=True)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        print("Missing SUPABASE_URL or SUPABASE_KEY")
        return
        
    supabase = create_client(url, key)
    
    # 1. Get all chapters
    print("Fetching chapters...")
    chapters_resp = supabase.table("chapters").select("id, chapter_number, title").order("chapter_number").execute()
    chapters = chapters_resp.data or []
    print(f"Total chapters in database: {len(chapters)}")
    if not chapters:
        return
        
    min_chapter = chapters[0]["chapter_number"]
    max_chapter = chapters[-1]["chapter_number"]
    print(f"Chapter range: {min_chapter} to {max_chapter}")
    
    # 2. Get all published translations
    print("Fetching published translations...")
    translations_resp = supabase.table("chapter_translations").select("chapter_id, locale").eq("translation_status", "published").execute()
    translations = translations_resp.data or []
    print(f"Total published translation rows: {len(translations)}")
    
    # Map chapter_id -> set of locales translated
    translation_map = {}
    for row in translations:
        cid = row["chapter_id"]
        locale = row["locale"]
        translation_map.setdefault(cid, set()).add(locale)
        
    target_locales = {"en", "ja", "zh-CN"}
    missing_by_chapter = []
    
    for ch in chapters:
        cid = ch["id"]
        ch_num = ch["chapter_number"]
        title = ch["title"]
        existing = translation_map.get(cid, set())
        missing = target_locales - existing
        if missing:
            missing_by_chapter.append({
                "chapter_number": ch_num,
                "title": title,
                "missing": list(missing)
            })
            
    print(f"\nTotal chapters missing one or more translations: {len(missing_by_chapter)}")
    if missing_by_chapter:
        print("\nFirst 10 missing chapters:")
        for m in missing_by_chapter[:10]:
            print(f"  Chapter {m['chapter_number']}: {m['title']} - Missing: {m['missing']}")
        if len(missing_by_chapter) > 10:
            print(f"  ... and {len(missing_by_chapter) - 10} more.")

if __name__ == "__main__":
    main()
