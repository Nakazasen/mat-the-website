import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def update_schema():
    print("Adding ai_model_name column to novel_settings...")
    # SQL can't be run directly via the supabase-py client easily without the 'rpc' or 'table' tricks
    # But novel_settings only has one row, we can try to upsert a column if supabase-py allows it
    # Actually, the regular client might fail if the column doesn't exist yet.
    
    # We will try to add it via a direct SQL query if possible, but the client doesn't support raw SQL easily.
    # Instruction to user is safer if we can't run it.
    # However, let's try to upsert with the new field to see if it works (unlikely to create column).
    
    try:
        # This will fail if column doesn't exist
        resp = supabase.table("novel_settings").update({"ai_model_name": "gemini-1.5-flash"}).eq("id", 1).execute()
        print("Column already exists or added successfully.")
    except Exception as e:
        print(f"Failed to update (normal if column missing): {e}")
        print("\nACTION REQUIRED: Please run the following SQL in your Supabase SQL Editor:")
        print("ALTER TABLE novel_settings ADD COLUMN IF NOT EXISTS ai_model_name TEXT DEFAULT 'gemini-1.5-flash';")

if __name__ == "__main__":
    update_schema()
