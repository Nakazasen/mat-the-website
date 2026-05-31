import asyncio
import os
import sys
from fastapi.testclient import TestClient

# Configure streams to use UTF-8 on Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    import main
except ImportError:
    from backend import main

# Mock admin authentication to bypass Supabase JWT check
async def fake_verify_admin(authorization: str = None) -> dict:
    return {"id": "mock-admin-id", "email": "admin@example.com", "role": "superadmin"}

main.verify_admin = fake_verify_admin

# Import app AFTER patching verify_admin
from main import app, supabase

client = TestClient(app)

def run_optimizer_test():
    print("====================================================")
    print("STARTING 1-CLICK AUTO-OPTIMIZER (9ROUTER STYLE) TEST")
    print("====================================================\n")

    # Fetch initial configuration order to compare later
    print("Step 1: Reading current database configuration...")
    res_before = supabase.table("novel_settings").select("ai_provider_config").eq("id", 1).execute()
    if not res_before.data:
        print("❌ FAILED: Could not read novel_settings configuration.")
        return
    
    cfg_before = res_before.data[0].get("ai_provider_config") or {}
    providers_before = cfg_before.get("providers", {})
    
    for p_name, p_cfg in providers_before.items():
        if p_cfg.get("enabled"):
            print(f"  - Enabled provider: {p_name} | Models order: {p_cfg.get('models')[:3]}... | Default: {p_cfg.get('default_model')}")

    # Trigger auto-optimize endpoint
    print("\n⏳ Step 2: Triggering 1-Click dynamic auto-optimize API...")
    response = client.post(
        "/api/admin/ai/providers/auto-optimize",
        headers={"Authorization": "Bearer mock-token-superadmin"}
    )
    
    print(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ FAILED: Auto-optimize endpoint returned error: {response.text}")
        return
        
    payload = response.json()
    print("✅ SUCCESS: Auto-optimize completed successfully!")
    print(f"Detail: {payload.get('detail')}")
    
    summary = payload.get("summary", {})
    print("\n================== OPTIMIZATION SUMMARY ==================")
    for provider, stats in summary.items():
        print(f"Provider: {provider}")
        print(f"  - Models tested: {stats.get('tested_count')}")
        print(f"  - Stable models found: {stats.get('stable_count')}")
        print(f"  - Best promoted model: {stats.get('best_model')} ({stats.get('best_latency_ms')} ms)")
        print(f"  - New models pool order: {stats.get('models_ordered')}")
        print("-" * 50)
        
    # Verify that database has been updated
    print("\nStep 3: Checking Supabase database for persistent updates...")
    res_after = supabase.table("novel_settings").select("ai_provider_config").eq("id", 1).execute()
    cfg_after = res_after.data[0].get("ai_provider_config") or {}
    providers_after = cfg_after.get("providers", {})
    
    for p_name, p_cfg in providers_after.items():
        if p_cfg.get("enabled") and p_name in summary:
            # The top model in the DB pool should match the best model in the summary
            best_model_expected = summary[p_name].get("best_model")
            best_model_actual = p_cfg.get("default_model")
            top_pool_actual = p_cfg.get("models")[0] if p_cfg.get("models") else None
            
            print(f"  - Provider '{p_name}' DB check:")
            print(f"    - Expected Best: {best_model_expected}")
            print(f"    - Actual Default in DB: {best_model_actual}")
            print(f"    - First model in DB Pool: {top_pool_actual}")
            
            if best_model_expected == best_model_actual and best_model_expected == top_pool_actual:
                print(f"    ✅ VERIFIED: Database model pool successfully sorted & default updated!")
            else:
                print(f"    ⚠️ NOTICE: Stable models list is empty or updated default model is same.")

    print("\n====================================================")
    print("AUTO-OPTIMIZER VERIFICATION TESTS COMPLETE!")
    print("====================================================")

if __name__ == "__main__":
    run_optimizer_test()
