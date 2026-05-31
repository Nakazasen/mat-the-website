import asyncio
import os
import sys

# Configure standard streams to use UTF-8 encoding on Windows to prevent UnicodeEncodeError
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

try:
    from main import supabase
except ImportError:
    from backend.main import supabase

from routes.ai_oracle import get_wiki_context, get_chapter_context, ask_oracle, OracleRequest
from fastapi import Request

class FakeClient:
    def __init__(self, host="127.0.0.1"):
        self.host = host

class FakeRequest:
    def __init__(self, host="127.0.0.1"):
        self.client = FakeClient(host)

async def run_tests():
    print("====================================================")
    print("STARTING AI ORACLE RAG SYSTEM VERIFICATION TESTS")
    print("====================================================\n")

    # Clear cache entries related to our tests
    print("Clearing cache for test questions...")
    try:
        supabase.table("oracle_cache").delete().neq("id", 0).execute()
        print("Cache cleared successfully.\n")
    except Exception as e:
        print(f"Failed to clear cache: {e}\n")

    # Test 1: get_wiki_context for Hàn Phong
    print("Test 1: Fetching wiki context for 'Hàn Phong'...")
    wiki_ctx = await get_wiki_context(supabase, "Hàn Phong là ai?", 828)
    print("--- Wiki Context Result ---")
    print(wiki_ctx)
    print("---------------------------\n")

    # Test 2: get_chapter_context for Chapter 827
    print("Test 2: Fetching chapter context for Chapter 827...")
    chapter_ctx = await get_chapter_context(supabase, 827)
    print("--- Chapter Context Result (First 500 chars) ---")
    print(chapter_ctx[:500] + ("..." if len(chapter_ctx) > 500 else ""))
    print("------------------------------------------------\n")

    # Test 3: RAG asking about Hàn Phong (Conversational prompt)
    print("Test 3: Querying AI Oracle about 'Hàn Phong là ai?'...")
    req_body = OracleRequest(question="Hàn Phong là ai?", chapter_progress=827)
    req = FakeRequest()
    
    try:
        response = await ask_oracle(req_body, req)
        print("--- AI Oracle Response ---")
        print(f"Source: {response.source}")
        print(f"Answer:\n{response.answer}")
        print("--------------------------\n")
    except Exception as e:
        print(f"Oracle Ask Error: {e}\n")

    # Test 4: Spoiler Protection / Future chapters constraint
    print("Test 4: Testing future query trigger (expecting 'Dự liệu chưa được giải mã.')...")
    req_body_spoiler = OracleRequest(question="Thế lực nào xuất hiện sau chương này?", chapter_progress=827)
    
    try:
        response_spoiler = await ask_oracle(req_body_spoiler, req)
        print("--- AI Oracle Spoiler Response ---")
        print(f"Source: {response_spoiler.source}")
        print(f"Answer:\n{response_spoiler.answer}")
        print("----------------------------------\n")
        
        # Verify if it returns the exact accented Vietnamese fallback
        expected_fallback = "Dữ liệu chưa được giải mã."
        if expected_fallback in response_spoiler.answer:
            print("SUCCESS: Correctly returned accented Vietnamese fallback!")
        else:
            print(f"WARNING: Did not find exact fallback string: '{expected_fallback}'")
    except Exception as e:
        print(f"Oracle Spoiler Error: {e}\n")

    # Test 5: RAG asking about Hàn Phong with a long question (expecting conversational AI response)
    print("Test 5: Querying AI Oracle with a long question about 'Hàn Phong' to trigger AI RAG...")
    req_body_long = OracleRequest(
        question="Xin hãy cho tôi biết Hàn Phong là nhân vật như thế nào trong tác phẩm này?",
        chapter_progress=827
    )
    
    try:
        response_long = await ask_oracle(req_body_long, req)
        print("--- AI Oracle Conversational Response ---")
        print(f"Source: {response_long.source}")
        print(f"Answer:\n{response_long.answer}")
        print("------------------------------------------\n")
    except Exception as e:
        print(f"Oracle Long Query Error: {e}\n")

    print("====================================================")
    print("ALL VERIFICATION TESTS COMPLETED!")
    print("====================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
