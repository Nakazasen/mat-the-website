import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from supabase import create_client

def check_settings():
    load_dotenv(override=True)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        print("Missing SUPABASE_URL or SUPABASE_KEY")
        return
        
    supabase = create_client(url, key)
    
    res = supabase.table("novel_settings").select("ai_model_name, ai_model_catalog, ai_api_key_catalog").eq("id", 1).execute()
    if not res.data:
        print("No novel settings found.")
        return
        
    settings = res.data[0]
    print(f"Current AI Model: {settings.get('ai_model_name')}")
    print(f"Model Catalog: {settings.get('ai_model_catalog')}")
    
    keys = settings.get('ai_api_key_catalog') or []
    print(f"API Keys count: {len(keys)}")

if __name__ == "__main__":
    check_settings()
