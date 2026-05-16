import os
import sys
from dotenv import load_dotenv

# Add current dir so it can find things
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("Fixing NULL values in chapters table...")
# Fix chapters table likes_count and view_count
# Supabase python client doesn't easily let us update where IS NULL.
# But we can fetch them and update.
def fix_chapters():
    resp = supabase.table("chapters").select("id, likes_count, view_count").execute()
    for row in resp.data:
        needs_update = False
        payload = {}
        if row.get("likes_count") is None:
            payload["likes_count"] = 0
            needs_update = True
        if row.get("view_count") is None:
            payload["view_count"] = 0
            needs_update = True
        if needs_update:
            supabase.table("chapters").update(payload).eq("id", row["id"]).execute()
            print(f"Fixed chapter {row['id']}")

def fix_profiles():
    print("Fixing NULL values in profiles table...")
    resp = supabase.table("profiles").select("id, exp, chapters_read").execute()
    for row in resp.data:
        needs_update = False
        payload = {}
        if row.get("exp") is None:
            payload["exp"] = 0
            needs_update = True
        if row.get("chapters_read") is None:
            payload["chapters_read"] = 0
            needs_update = True
        if needs_update:
            supabase.table("profiles").update(payload).eq("id", row["id"]).execute()
            print(f"Fixed profile {row['id']}")

if __name__ == "__main__":
    fix_chapters()
    fix_profiles()
    print("Done fixing nulls.")
