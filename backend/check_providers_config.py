import os
import sys
from dotenv import load_dotenv

# Configure standard streams to use UTF-8 encoding on Windows to prevent UnicodeEncodeError
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
try:
    from main import supabase
except ImportError:
    from backend.main import supabase

def check_providers():
    res = supabase.table("novel_settings").select("*").eq("id", 1).execute()
    if not res.data:
        print("No novel settings row id=1 found.")
        return
        
    settings = res.data[0]
    print("========== NOVEL SETTINGS (id=1) ==========")
    for key, value in settings.items():
        if "key" in key.lower() or "token" in key.lower():
            # mask key values
            print(f"{key}: [Redacted / count={len(value) if isinstance(value, list) else 'masked'}]")
        else:
            print(f"{key}: {value}")
            
    print("\n========== ROUTER STATUS ==========")
    try:
        from main import get_provider_router
    except ImportError:
        from backend.main import get_provider_router
        
    router = get_provider_router()
    print(f"Registered Providers count: {len(router._providers)}")
    for name, provider in router._providers.items():
        print(f"- {name}: enabled={provider.profile.enabled}, default_model={provider.profile.default_model}, models={provider.profile.model_pool}")

if __name__ == "__main__":
    check_providers()
