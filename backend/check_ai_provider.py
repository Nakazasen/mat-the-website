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
    res = supabase.table("novel_settings").select("ai_provider_config").eq("id", 1).execute()
    if not res.data:
        print("No settings found.")
        return
        
    config = res.data[0].get("ai_provider_config")
    print(f"ai_provider_config value: {config}")

if __name__ == "__main__":
    main()
