import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def sync_profiles():
    print("Syncing profiles from user_chapter_reads...")
    # Fetch all reads
    # Note: user_chapter_reads might be large, but we can aggregate them locally
    reads_resp = supabase.table("user_chapter_reads").select("user_id, chapter_id").execute()
    reads = reads_resp.data

    user_stats = {}
    for r in reads:
        uid = r["user_id"]
        cid = r["chapter_id"]
        if uid not in user_stats:
            user_stats[uid] = set()
        user_stats[uid].add(cid)

    # Now update profiles
    for uid, chapters in user_stats.items():
        count = len(chapters)
        exp = count * 10
        print(f"User {uid}: {count} chapters, {exp} exp")
        supabase.table("profiles").update({
            "chapters_read": count,
            "exp": exp
        }).eq("id", uid).execute()

    print("Done syncing profiles.")

if __name__ == "__main__":
    sync_profiles()
