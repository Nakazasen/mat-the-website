import asyncio
import os
import sys
from dotenv import load_dotenv

# Configure streams to use UTF-8 on Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from main import get_provider_router, resolve_ai_provider_config, AIRequest
except ImportError:
    from backend.main import get_provider_router, resolve_ai_provider_config, AIRequest

async def test_translation_routing():
    load_dotenv(override=True)
    router = get_provider_router()
    
    print("========== DIAGNOSING MULTI-PROVIDER ROUTING ==========")
    print(f"Registered Providers: {list(router._providers.keys())}")
    
    # Try a simple translation request
    user_prompt = "Hãy dịch câu này sang tiếng Anh: 'Tôi muốn sinh tồn trong mạt thế.'"
    system_instruction = "Bạn là biên dịch viên chuyên nghiệp."
    
    request = AIRequest(
        text=user_prompt,
        mode="translation",
        system_instruction=system_instruction,
        max_output_tokens=1000,
        temperature=0.1,
    )
    
    config = resolve_ai_provider_config()
    policy = config.get("translation_policy", {"mode": "waterfall"})
    print(f"Policy: {policy}")
    
    print("\n⏳ Routing translation request...")
    result = await router.route(request, policy=policy)
    
    print(f"\nResult Status: {result.status}")
    if result.status == "success":
        print(f"SUCCESS! Output text:\n{result.text}")
    else:
        print(f"❌ FAILED! error_type: {result.error_type}, message: {result.error_message}")
        
    print("\n========== ATTEMPTS DETAILS ==========")
    for index, a in enumerate(result.attempts):
        print(f"\nAttempt {index+1}: Provider='{a.get('provider')}', Model='{a.get('model')}'")
        print(f"  - Status: {a.get('status')}")
        print(f"  - Reason: {a.get('reason')}")
        print(f"  - Message: {a.get('message')}")
        print(f"  - Metadata: {a.get('metadata')}")

if __name__ == "__main__":
    asyncio.run(test_translation_routing())
