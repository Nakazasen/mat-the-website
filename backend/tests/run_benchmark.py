# backend/tests/run_benchmark.py
import sys
import os
from unittest.mock import MagicMock
import pytest

# Ensure path includes root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set dummy env vars before importing main/app
os.environ["SUPABASE_URL"] = "https://mock-prevent-production-writes.supabase.co"
os.environ["SUPABASE_KEY"] = "mock-prevent-production-writes"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "mock-prevent-production-writes"

# Setup mock DB client manually
mock_client = MagicMock()

def mock_table(name):
    mock_t = MagicMock()
    mock_t.select.return_value = mock_t
    mock_t.order.return_value = mock_t
    mock_t.limit.return_value = mock_t
    mock_t.eq.return_value = mock_t
    
    if name == "chapters":
        mock_res_max = MagicMock()
        mock_res_max.data = [{"chapter_number": 829}]
        mock_t.execute.return_value = mock_res_max
    elif name == "story_chunks":
        mock_res_chunks = MagicMock()
        mock_res_chunks.data = []
        mock_t.execute.return_value = mock_res_chunks
    else:
        mock_res = MagicMock()
        mock_res.data = []
        mock_t.execute.return_value = mock_res
        
    return mock_t

mock_client.table.side_effect = mock_table

import supabase
supabase.create_client = lambda *args, **kwargs: mock_client

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def patch_oracle(name, value):
    for module_name in ["routes.ai_oracle", "backend.routes.ai_oracle"]:
        if module_name in sys.modules:
            setattr(sys.modules[module_name], name, value)

# Patch main and backend.main supabase client references
for module_name in ["main", "backend.main"]:
    if module_name in sys.modules:
        setattr(sys.modules[module_name], "supabase", mock_client)
        
# Mock rate limit globally
async def mock_rate_limit(*args, **kwargs):
    return True
patch_oracle("check_rate_limit", mock_rate_limit)

# Mock verify_chapter_exists_in_db to return True for any valid chapter (1 <= ch <= 829)
async def mock_exists(db, chapter_num):
    return 1 <= chapter_num <= 829
patch_oracle("verify_chapter_exists_in_db", mock_exists)

# Mock RAG retrieval
def mock_get_rag(question, cap, limit=5):
    return {
        "context_text": f"[CHƯƠNG {cap}] Nội dung giả lập cho chương {cap}...",
        "citations": [{"chapter_number": cap, "chunk_index": 0, "source": "story_chunks"}]
    }
patch_oracle("get_rag_context_for_oracle", mock_get_rag)

# Mock LLM call
async def mock_ai_call(*args, **kwargs):
    class MockAIResult:
        status = "success"
        text = "Phản hồi giả lập từ LLM."
        attempts = []
        model = "mock-model"
    return MockAIResult()
patch_oracle("call_ai_provider_result", mock_ai_call)

# Mock admin verify
async def mock_verify_admin(*args):
    return True
patch_oracle("is_admin_request", mock_verify_admin)


def run_benchmark():
    os.environ["ORACLE_RAG_TRACE"] = "1"
    
    # 12 Test Cases
    cases = [
        # Group 1: 3 existing chapters
        {"question": "tóm tắt chương 1", "chapter_progress": 1, "expected_abstain": False, "expected_chapter": 1},
        {"question": "tóm tắt chương 400", "chapter_progress": 400, "expected_abstain": False, "expected_chapter": 400},
        {"question": "tóm tắt chương 829", "chapter_progress": 829, "expected_abstain": False, "expected_chapter": 829},
        
        # Group 2: 3 non-existing chapters
        {"question": "tóm tắt chương 0", "chapter_progress": 0, "expected_abstain": True, "expected_chapter": 0},
        {"question": "tóm tắt chương 830", "chapter_progress": 830, "expected_abstain": True, "expected_chapter": 830},
        {"question": "tóm tắt chương 9999", "chapter_progress": 9999, "expected_abstain": True, "expected_chapter": 9999},
        
        # Group 3: 3 general entity queries with chapter_progress > max
        {"question": "Hạ Huyền Sương là ai?", "chapter_progress": 830, "expected_abstain": False, "expected_clamp": 829},
        {"question": "Chu Vấn là ai?", "chapter_progress": 9999, "expected_abstain": False, "expected_clamp": 829},
        {"question": "Trấn Hy Vọng là gì?", "chapter_progress": 830, "expected_abstain": False, "expected_clamp": 829},
        
        # Group 4: 3 chapter summary queries with different wording
        {"question": "kể diễn biến chương 829", "chapter_progress": 829, "expected_abstain": False, "expected_chapter": 829},
        {"question": "tóm lược chương 829", "chapter_progress": 829, "expected_abstain": False, "expected_chapter": 829},
        {"question": "nội dung chương 829", "chapter_progress": 829, "expected_abstain": False, "expected_chapter": 829},
    ]
    
    total_cases = len(cases)
    correct_availability = 0
    correct_abstain = 0
    wrong_chapter_retrievals = 0
    leakages = 0
    
    results = []
    for c in cases:
        payload = {
            "question": c["question"],
            "chapter_progress": c["chapter_progress"]
        }
        
        response = client.post("/oracle/ask", json=payload, headers={"Authorization": "Bearer admin-token"})
        data = response.json()
        
        abstained = data.get("abstained")
        requested_ch = data.get("requested_chapter")
        chapter_cap = data.get("chapter_cap")
        
        trace = data.get("trace")
        effective_cap = trace.get("effective_chapter_progress") if trace else None
        
        # Check availability gate accuracy
        if c["expected_abstain"]:
            if abstained is True:
                correct_availability += 1
                correct_abstain += 1
            else:
                pass
        else:
            if abstained is False:
                correct_availability += 1
            else:
                pass
                
        # Check leakage (> 829)
        if not abstained and effective_cap is not None and effective_cap > 829:
            leakages += 1
            
        # Check wrong-chapter retrieval for summary exact chapter
        if not abstained and "expected_chapter" in c:
            if effective_cap != c["expected_chapter"]:
                wrong_chapter_retrievals += 1
                
        citation_info = "None"
        if trace and trace.get("selected_chapters"):
            citation_info = str(trace["selected_chapters"])
            
        results.append({
            "question": c["question"],
            "chapter_progress": c["chapter_progress"],
            "expected_abstain": c["expected_abstain"],
            "abstained": abstained,
            "effective_cap": effective_cap,
            "citation_info": citation_info,
            "response": data
        })

    chapter_availability_accuracy = correct_availability / total_cases
    wrong_chapter_retrieval_rate = wrong_chapter_retrievals / total_cases
    total_unavailable = sum(1 for c in cases if c["expected_abstain"])
    unavailable_chapter_abstain_accuracy = correct_abstain / total_unavailable if total_unavailable > 0 else 1.0
    future_chapter_leakage_rate = leakages / total_cases
    
    print("--- RUN RESULTS ---")
    for r in results:
        q_safe = r["question"].encode("ascii", "backslashreplace").decode("ascii")
        ans_safe = str(r["response"].get("answer", "")).encode("ascii", "backslashreplace").decode("ascii")
        reason_safe = str(r["response"].get("abstain_reason", "")).encode("ascii", "backslashreplace").decode("ascii")
        print(f"Q: {q_safe}")
        print(f"  Progress: {r['chapter_progress']} | Expected Abstain: {r['expected_abstain']} | Abstained: {r['abstained']}")
        print(f"  Effective Cap: {r['effective_cap']} | Citations: {r['citation_info']}")
        print(f"  Answer: {ans_safe}")
        print(f"  Abstain Reason: {reason_safe}")
        
    print("\n--- METRICS ---")
    print(f"Chapter Availability Accuracy: {chapter_availability_accuracy:.2%}")
    print(f"Wrong-Chapter Retrieval Rate: {wrong_chapter_retrieval_rate:.2%}")
    print(f"Unavailable-Chapter Abstain Accuracy: {unavailable_chapter_abstain_accuracy:.2%}")
    print(f"Future Chapter Leakage Rate: {future_chapter_leakage_rate:.2%}")

if __name__ == "__main__":
    run_benchmark()
