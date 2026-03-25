import os
from supabase import create_client
from dotenv import load_dotenv

# Run from root dir
load_dotenv('backend/.env')
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if not url or not key:
    print("Cannot find Supabase credentials")
    exit(1)

supabase = create_client(url, key)

try:
    res = supabase.table('hq_snapshots').select('*').limit(1).execute()
    print("Success! Data:", res.data)
except Exception as e:
    print("Database Error:", e)
