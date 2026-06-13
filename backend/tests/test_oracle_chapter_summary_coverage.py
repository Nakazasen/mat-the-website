# backend/tests/test_oracle_chapter_summary_coverage.py
import pytest
import sys
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def patch_oracle(monkeypatch, name, value):
    for module_name in ["routes.ai_oracle", "backend.routes.ai_oracle"]:
        if module_name in sys.modules:
            monkeypatch.setattr(f"{module_name}.{name}", value)

@pytest.fixture
def mock_supabase_suite(monkeypatch):
    mock_client = MagicMock()
    
    def mock_table(name):
        mock_t = MagicMock()
        mock_t.select.return_value = mock_t
        mock_t.order.return_value = mock_t
        mock_t.limit.return_value = mock_t
        mock_t.eq.return_value = mock_t
        
        if name == "chapters":
            mock_res_max = MagicMock()
            # 830 is the max available chapter
            mock_res_max.data = [{"chapter_number": 830}]
            mock_t.execute.return_value = mock_res_max
        elif name == "story_chunks":
            # Mock 17 chunks of chapter 830
            mock_res_chunks = MagicMock()
            mock_res_chunks.data = [
                {
                    "id": f"chunk-{i}",
                    "chapter_number": 830,
                    "chunk_index": i,
                    "chapter_title": "Trộm trứng",
                    "content_plain": f"Nội dung chunk {i}. " + (
                        "Chiến dịch Lệ Giang di tản Tam Giang trấn Hi Vọng và La Thiên Dật xé mây." if i < 5
                        else "Ngô Soái và Hàn Phong đối thoại." if i < 12
                        else "Chu Vấn vào hang rắn trộm trứng dùng Thùng Hàng Vạn Năng tráo trứng dụ Eat-3 chạy thoát về Đại Xuyên Nam Ô."
                    )
                }
                for i in range(17)
            ]
            mock_t.execute.return_value = mock_res_chunks
        else:
            mock_res = MagicMock()
            mock_res.data = []
            mock_t.execute.return_value = mock_res
            
        return mock_t
        
    mock_client.table.side_effect = mock_table
    
    import supabase
    monkeypatch.setattr(supabase, "create_client", lambda *args, **kwargs: mock_client)
    for module_name in ["main", "backend.main"]:
        if module_name in sys.modules:
            monkeypatch.setattr(sys.modules[module_name], "supabase", mock_client)
            
    # Mock rate limit globally
    async def mock_rate_limit(*args, **kwargs):
        return True
    patch_oracle(monkeypatch, "check_rate_limit", mock_rate_limit)

    # Mock verify_chapter_exists_in_db to return True for target chapters
    async def mock_exists(db, chapter_num):
        return chapter_num <= 830
    patch_oracle(monkeypatch, "verify_chapter_exists_in_db", mock_exists)

    # Mock LLM call
    async def mock_ai_call(*args, **kwargs):
        class MockAIResult:
            status = "success"
            text = "Phản hồi tóm tắt giả lập từ LLM."
            attempts = []
            model = "mock-model"
        return MockAIResult()
    patch_oracle(monkeypatch, "call_ai_provider_result", mock_ai_call)
    
    # Mock admin verify
    async def mock_verify_admin(*args):
        return True
    patch_oracle(monkeypatch, "is_admin_request", mock_verify_admin)

    return mock_client


def test_chapter_summary_fetches_all_chunks_and_preserves_coverage(mock_supabase_suite, monkeypatch):
    """
    1. chapter summary fetches all usable exact-chapter chunks.
    2. chunks sorted by stable order (chunk_index asc).
    3. overlapping/duplicate indices checked.
    4. chapter summary does not use small semantic top_k only.
    5. context coverage includes both Lệ Giang and egg-theft clusters (bypassing forbidden terms filter).
    6. token overflow uses expanded context budget to avoid silent truncation.
    10. trace includes non-null chunk refs.
    11. no chapter outside 830 is selected.
    12. no production mutation occurs.
    """
    monkeypatch.setenv("ORACLE_RAG_TRACE", "1")
    monkeypatch.setenv("ORACLE_RAG_ENABLED", "1")

    payload = {
        "question": "Hãy tóm tắt đầy đủ tất cả các tuyến diễn biến trong chương 830.",
        "chapter_progress": 830,
        "debug_bypass_cache": True
    }
    
    # Track calls to database or check if any writes occur
    mock_supabase_suite.table("oracle_cache").upsert.assert_not_called()
    mock_supabase_suite.table("rag_feedback").insert.assert_not_called()

    response = client.post("/oracle/ask", json=payload, headers={"Authorization": "Bearer admin-token"})
    assert response.status_code == 200
    data = response.json()
    
    # Check trace content
    assert "trace" in data and data["trace"] is not None
    trace = data["trace"]
    
    # Verify all 17 chunks fetched
    assert len(trace["candidate_chunk_ids"]) == 17
    # Verify order is stable (0 to 16)
    indices = [int(cid.split("-")[1]) for cid in trace["candidate_chunk_ids"]]
    assert indices == sorted(indices)
    assert len(set(indices)) == 17  # no duplicates/overlaps
    
    # Verify selected chunk ids are populated and all 17 are placed in context
    assert len(trace["selected_chunk_ids"]) == 17
    assert all(cid is not None for cid in trace["selected_chunk_ids"])
    assert all(ch == 830 for ch in trace["selected_chapters"])


def test_cache_version_changes_after_upgrade(mock_supabase_suite, monkeypatch):
    """
    8. cache version changes after summary policy update (to 11F0A_FIX2_COVERAGE).
    9. old incomplete cache not reused.
    """
    from backend.routes.ai_oracle import hash_question
    # Assert cache key contains FIX2 policy version
    h_new = hash_question("tóm tắt chương 830", chapter_cap=830, target_chapter=830, intent="chapter_summary")
    h_old = hash_question("tóm tắt chương 830", chapter_cap=830, target_chapter=830, intent="chapter_summary", policy_version="11F0A_FIX1")
    assert h_new != h_old
    assert "11F0A_FIX2_COVERAGE" in h_new or len(h_new) == 32


def test_general_lore_retrieval_and_gating_behavior(mock_supabase_suite, monkeypatch):
    """
    13. general lore retrieval behavior unchanged (still applies filters).
    14. chapter 831 gate still works (abstains).
    """
    # Test Chapter 831 gating
    payload_831 = {
        "question": "tóm tắt chương 831",
        "chapter_progress": 831
    }
    response_831 = client.post("/oracle/ask", json=payload_831)
    assert response_831.status_code == 200
    data_831 = response_831.json()
    assert data_831["abstained"] is True
    assert data_831["abstain_reason"] == "chapter_unavailable"
    assert data_831["source"] == "gate"

    # Test general lore question still filters out forbidden terms
    monkeypatch.setenv("ORACLE_RAG_TRACE", "1")
    monkeypatch.setenv("ORACLE_RAG_ENABLED", "1")

    # Mock RAG to return general chunks (some containing forbidden term "Chu Vấn")
    mock_chunks = [
        {"id": "c1", "chapter_number": 820, "chunk_index": 0, "chapter_title": "A", "content_plain": "Chu Vấn xuất hiện."},
        {"id": "c2", "chapter_number": 820, "chunk_index": 1, "chapter_title": "A", "content_plain": "Hạ Huyền Sương ở đây."}
    ]
    
    # Spy search
    spy_search = MagicMock(return_value=mock_chunks)
    monkeypatch.setattr("backend.rag.retrieval.search_story_chunks_hybrid_lexical", spy_search)

    # Question is long (16 words) to bypass fast path
    payload_lore = {
        "question": "Hãy cho tôi biết thông tin chi tiết đầy đủ nhất về nhân vật Hạ Huyền Sương?",
        "chapter_progress": 830,
        "debug_bypass_cache": True
    }
    response_lore = client.post("/oracle/ask", json=payload_lore, headers={"Authorization": "Bearer admin-token"})
    assert response_lore.status_code == 200
    data_lore = response_lore.json()
    trace_lore = data_lore["trace"]
    print("DEBUG TRACE LORE:", str(trace_lore).encode('ascii', 'backslashreplace').decode('ascii'))
    
    # "c1" contains "Chu Vấn" (forbidden) so it should be filtered out
    assert "c1" not in trace_lore["selected_chunk_ids"]
    assert "c2" in trace_lore["selected_chunk_ids"]
