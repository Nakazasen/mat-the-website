import os
import json
from supabase import create_client
from dotenv import load_dotenv

# Load from backend/.env
load_dotenv('backend/.env')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if not url or not key:
    print("Missing SUPABASE_URL or SUPABASE_KEY in backend/.env")
    exit(1)

supabase = create_client(url, key)

try:
    res = supabase.table('novel_settings').select('*').eq('id', 1).maybe_single().execute()
    if res.data:
        # Hide the actual key for security but show if it EXISTS and its length
        api_key = res.data.get('ai_api_key')
        api_keys = res.data.get('ai_api_keys')
        print(f"Settings found for ID 1:")
        print(f"  ai_model_name: {res.data.get('ai_model_name')} (Type: {type(res.data.get('ai_model_name'))})")
        print(f"  ai_api_key: {'EXISTS (len=' + str(len(api_key)) + ')' if api_key else 'MISSING'} (Type: {type(api_key)})")
        print(f"  ai_api_keys: {'EXISTS (len=' + str(len(api_keys)) if api_keys else 'MISSING'} (Type: {type(api_keys)})")
        if isinstance(api_keys, str):
            print(f"  ai_api_keys is a STRING! Content starts with: {api_keys[:20]}...")
        elif isinstance(api_keys, list):
            print(f"  ai_api_keys is a LIST! Count: {len(api_keys)}")
            if api_keys:
                print(f"  First key length: {len(str(api_keys[0]))}")
        
        print(f"  ai_model_catalog: {res.data.get('ai_model_catalog')} (Type: {type(res.data.get('ai_model_catalog'))})")
    else:
        print("No novel_settings found for ID 1")
except Exception as e:
    print(f"Error querying novel_settings: {e}")
