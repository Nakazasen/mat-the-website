import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from supabase import create_client

def check_chapters(start, end):
    load_dotenv(override=True)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        print("Missing SUPABASE_URL or SUPABASE_KEY")
        return
        
    supabase = create_client(url, key)
    
    res = supabase.table("chapters").select("id, chapter_number").gte("chapter_number", start).lte("chapter_number", end).execute()
    if not res.data:
        print("No chapters found in range.")
        return
        
    chapter_ids = [r['id'] for r in res.data]
    id_to_num = {r['id']: r['chapter_number'] for r in res.data}
    
    trans_res = supabase.table("chapter_translations").select("chapter_id, locale, translation_status").in_("chapter_id", chapter_ids).execute()
    
    status_map = {}
    for r in trans_res.data:
        cid = r['chapter_id']
        if cid not in status_map: status_map[cid] = []
        status_map[cid].append(f"{r['locale']}:{r['translation_status']}")
    
    print(f"{'Chapter':<10} | {'Status':<50}")
    print("-" * 65)
    for cid in sorted(id_to_num.keys(), key=lambda x: id_to_num[x]):
        cnum = id_to_num[cid]
        statuses = status_map.get(cid, ["None"])
        print(f"{cnum:<10} | {', '.join(statuses)}")

if __name__ == "__main__":
    check_chapters(800, 817)
