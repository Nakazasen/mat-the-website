import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('backend/.env')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

sb = create_client(url, key)
res = sb.table('novel_settings').select('ai_api_key').eq('id', 1).single().execute()
api_key = res.data['ai_api_key']

with open('temp_key.txt', 'w') as f:
    f.write(api_key)
print("Key written to temp_key.txt")
