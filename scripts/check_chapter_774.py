
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, 'backend', '.env')
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print(f"Missing Supabase credentials in {env_path}")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_chapters():
    # Get all translation statuses for chapters >= 774
    print(f"Checking translation statuses for chapters >= 774...")
    # First get chapter IDs
    ch_res = supabase.table("chapters").select("id, chapter_number").gte("chapter_number", 774).execute()
    ch_map = {c['id']: c['chapter_number'] for c in ch_res.data}
    ch_ids = list(ch_map.keys())
    
    if not ch_ids:
        print("No chapters >= 774 found.")
        return

    # Now get translations
    trans_res = supabase.table("chapter_translations").select("chapter_id, locale, translation_status, translation_source, last_error").in_("chapter_id", ch_ids).execute()
    
    status_counts = {}
    details = []
    for t in trans_res.data:
        status = t['translation_status']
        status_counts[status] = status_counts.get(status, 0) + 1
        if status != 'published':
            err = t.get('last_error', 'No error message')
            details.append(f"Chapter {ch_map[t['chapter_id']]} ({t['locale']}): {status}\n    ERROR: {err}")
    
    print(f"Summary of translation statuses:")
    for status, count in status_counts.items():
        print(f"  - {status}: {count}")
    
    if details:
        print(f"\nNon-published details (first 20):")
        for d in details[:20]:
            print(f"  {d}")
    else:
        print("\nAll found translations are published.")
    
    return # Stop here
    
    chapters = result.data
    if not chapters:
        print("No chapters found >= 774")
        return

    print(f"Found {len(chapters)} chapters.")
    max_num = 0
    for ch in chapters:
        ch_id = ch['id']
        ch_num = ch['chapter_number']
        ch_url = ch.get('content_url', 'MISSING')
        if ch_num > max_num: max_num = ch_num
        
        # Check translations for this chapter
        trans_result = supabase.table("chapter_translations").select("locale, translation_status, translation_source, translated_at").eq("chapter_id", ch_id).execute()
        trans_info = []
        for t in trans_result.data:
            source = t.get('translation_source', 'n/a')
            status = t.get('translation_status', 'n/a')
            at = t.get('translated_at', 'n/a')
            trans_info.append(f"{t['locale']} (Status: {status}, Source: {source}, At: {at})")
        
        print(f"Chapter {ch_num}: {ch['title']} (ID: {ch_id})")
        print(f"  URL: {ch_url}")
        if trans_info:
            for info in trans_info:
                print(f"    {info}")
        else:
            print("    NONE")
    
    print(f"\nMax chapter found: {max_num}")

if __name__ == "__main__":
    check_chapters()
