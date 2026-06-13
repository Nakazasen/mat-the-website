# backend/tests/test_oracle_cache.py
# Enforces exact chapter retrieval, cache logic, bypass rules, and gate priorities.

import os
import sys
import pytest
import hashlib
import re
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import backend.main
try:
    import main
except ImportError:
    pass
from backend.main import app
from backend.routes import ai_oracle

client = TestClient(app)

def patch_oracle(monkeypatch, name, value):
    for module_name in ["routes.ai_oracle", "backend.routes.ai_oracle"]:
        if module_name in sys.modules:
            monkeypatch.setattr(f"{module_name}.{name}", value)

@pytest.fixture
def mock_supabase_cache_suite(monkeypatch):
    """Sets up standard mock DB client, rate limit, and admin validation."""
    mock_client = MagicMock()
    
    # 12. Absolute rule: No autonomous DB writes in tests
    def prevent_writes(*args, **kwargs):
        raise RuntimeError("CRITICAL: Write operation attempted on database during test execution!")
    
    # Configure read operations
    def mock_table(name):
        mock_t = MagicMock()
        mock_t.insert.side_effect = prevent_writes
        mock_t.update.side_effect = prevent_writes
        mock_t.upsert.side_effect = prevent_writes
        mock_t.delete.side_effect = prevent_writes
        
        mock_t.select.return_value = mock_t
        mock_t.order.return_value = mock_t
        mock_t.limit.return_value = mock_t
        mock_t.eq.return_value = mock_t
        
        if name == "chapters":
            # Default max chapter = 830
            mock_res_max = MagicMock()
            mock_res_max.data = [{"chapter_number": 830}]
            mock_t.execute.return_value = mock_res_max
        elif name == "story_chunks":
            mock_res_chunks = MagicMock()
            mock_res_chunks.data = []
            mock_t.execute.return_value = mock_res_chunks
        elif name == "oracle_cache":
            mock_res_cache = MagicMock()
            mock_res_cache.data = []
            mock_t.execute.return_value = mock_res_cache
            
        return mock_t

    mock_client.table.side_effect = mock_table

    # Patch Supabase client
    for module_name in ["main", "backend.main"]:
        if module_name in sys.modules:
            monkeypatch.setattr(sys.modules[module_name], "supabase", mock_client)

    # Disable rate limits
    async def mock_rate_limit(*args, **kwargs):
        return True
    patch_oracle(monkeypatch, "check_rate_limit", mock_rate_limit)

    return mock_client

def test_exact_chapter_uses_eq_filter_and_filtering(mock_supabase_cache_suite, monkeypatch):
    """
    1. chapter_summary exact chapter dùng eq filter, không lte-only.
    2. exact chapter có chunks -> candidate chapters chỉ target.
    """
    # Mock verify_chapter_exists_in_db to return True
    async def mock_exists(db, chapter_num):
        return True
    patch_oracle(monkeypatch, "verify_chapter_exists_in_db", mock_exists)

    # Enable trace
    monkeypatch.setenv("ORACLE_RAG_TRACE", "1")
    monkeypatch.setenv("ORACLE_RAG_ENABLED", "1")

    # Mock admin
    async def mock_is_admin(*args):
        return True
    patch_oracle(monkeypatch, "is_admin_request", mock_is_admin)

    # Mock retrieval results
    mock_chunks = [
        {"id": "chunk1", "chapter_number": 830, "content_plain": "Chương 830 diễn biến trộm trứng.", "score": 0.9}
    ]
    
    # Spy on search_story_chunks_hybrid_lexical calls
    spy_search = MagicMock(return_value=mock_chunks)
    monkeypatch.setattr("backend.rag.retrieval.search_story_chunks_hybrid_lexical", spy_search)

    # Mock LLM call
    async def mock_llm(*args, **kwargs):
        class Result:
            status = "success"
            text = "Bản tóm tắt chương 830 giả lập."
            attempts = []
        return Result()
    patch_oracle(monkeypatch, "call_ai_provider_result", mock_llm)

    payload = {"question": "tóm tắt chương 830", "chapter_progress": 830}
    response = client.post("/oracle/ask", json=payload)
    print("RESPONSE DATA:", repr(response.json()).encode('ascii', errors='backslashreplace').decode('ascii'))
    assert spy_search.call_count >= 1
    call_args = spy_search.call_args[1]
    assert call_args.get("exact_chapter") == 830

    data = response.json()
    assert data["trace"] is not None
    # Candidate chapters must ONLY contain 830
    assert data["trace"]["candidate_chapters"] == [830]
    assert data["trace"]["selected_chapters"] == [830]

def test_exact_chapter_no_chunks_abstains(mock_supabase_cache_suite, monkeypatch):
    """3. exact chapter không có chunks -> abstain, không global fallback."""
    # verify_chapter_exists_in_db returns False (e.g. no chunks)
    async def mock_exists(db, chapter_num):
        return False
    patch_oracle(monkeypatch, "verify_chapter_exists_in_db", mock_exists)

    # Mock admin
    async def mock_is_admin(*args):
        return True
    patch_oracle(monkeypatch, "is_admin_request", mock_is_admin)

    payload = {"question": "tóm tắt chương 830", "chapter_progress": 830}
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["abstained"] is True
    assert data["abstain_reason"] == "missing_chapter_chunks"
    assert "chưa thể tóm tắt" in data["answer"]

def test_cache_hit_does_not_bypass_availability_gate(mock_supabase_cache_suite, monkeypatch):
    """4. cache hit không bypass availability gate (gate check chạy trước)."""
    # Max chapter is 830. Querying chapter 831 (unavailable)
    # Mock cache to return a fake answer for chapter 831 (which shouldn't happen, but we test gate priority)
    async def mock_check_cache(db, q_hash, cap):
        return "Cached summary of 831."
    patch_oracle(monkeypatch, "check_cache", mock_check_cache)

    async def mock_exists(db, chapter_num):
        return False
    patch_oracle(monkeypatch, "verify_chapter_exists_in_db", mock_exists)

    payload = {"question": "tóm tắt chương 831", "chapter_progress": 831}
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Should still abstain because gate rejects 831 before cache check
    assert data["abstained"] is True
    assert data["abstain_reason"] == "chapter_unavailable"
    assert data["source"] == "gate"

def test_cache_key_differs_between_chapters(mock_supabase_cache_suite, monkeypatch):
    """5. cache key phân biệt chapter 829 và 830."""
    from backend.routes.ai_oracle import hash_question
    hash_829 = hash_question("tóm tắt chương này", chapter_cap=829, target_chapter=829, intent="chapter_summary")
    hash_830 = hash_question("tóm tắt chương này", chapter_cap=830, target_chapter=830, intent="chapter_summary")
    assert hash_829 != hash_830

def test_cache_bypass_forces_retrieval(mock_supabase_cache_suite, monkeypatch):
    """
    6. cache bypass admin gọi retrieval thật.
    7. public không được nhận raw trace.
    8. trace ghi cache/retrieval state.
    """
    monkeypatch.setenv("ORACLE_RAG_TRACE", "1")
    monkeypatch.setenv("ORACLE_RAG_ENABLED", "1")

    # Mock verify_chapter_exists_in_db to return True
    async def mock_exists(db, chapter_num):
        return True
    patch_oracle(monkeypatch, "verify_chapter_exists_in_db", mock_exists)

    # Mock cache check to return a cached answer
    async def mock_check_cache(db, q_hash, cap):
        return "Cached result"
    patch_oracle(monkeypatch, "check_cache", mock_check_cache)

    # Mock retrieval results
    mock_chunks = [{"id": "chunk1", "chapter_number": 830, "content_plain": "Content"}]
    spy_search = MagicMock(return_value=mock_chunks)
    monkeypatch.setattr("backend.rag.retrieval.search_story_chunks_hybrid_lexical", spy_search)

    # Mock LLM call
    async def mock_llm(*args, **kwargs):
        class Result:
            status = "success"
            text = "Fresh RAG result with sufficient length for caching."
            attempts = []
        return Result()
    patch_oracle(monkeypatch, "call_ai_provider_result", mock_llm)

    # Scenario A: Admin requests bypass using debug_bypass_cache field
    async def mock_is_admin(*args):
        return True
    patch_oracle(monkeypatch, "is_admin_request", mock_is_admin)

    payload = {"question": "tóm tắt chương 830", "chapter_progress": 830, "debug_bypass_cache": True}
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "ai_provider"  # verified bypass worked (didn't use "cache")
    assert data["trace"] is not None
    assert data["trace"]["cache_bypassed"] is True
    assert data["trace"]["cache_checked"] is True
    assert data["trace"]["cache_hit"] is False
    assert data["trace"]["retrieval_called"] is True
    assert spy_search.call_count >= 1

    # Scenario B: Public requests bypass (should be ignored)
    async def mock_is_public(*args):
        return False
    patch_oracle(monkeypatch, "is_admin_request", mock_is_public)

    payload = {"question": "tóm tắt chương 830", "chapter_progress": 830, "debug_bypass_cache": True}
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "cache"  # bypass ignored, returned cached answer
    assert "trace" not in data or data["trace"] is None  # public doesn't receive trace

def test_general_lore_clamping_dynamically(mock_supabase_cache_suite, monkeypatch):
    """9. general lore clamp dùng max_reader_visible_chapter, không hardcode 829."""
    # Verify max chapter is fetched from chapters table
    # Set max available chapter in mock DB to 830
    def mock_table(name):
        mock_t = MagicMock()
        mock_t.select.return_value = mock_t
        mock_t.order.return_value = mock_t
        mock_t.limit.return_value = mock_t
        mock_t.eq.return_value = mock_t
        
        if name == "chapters":
            mock_res_max = MagicMock()
            mock_res_max.data = [{"chapter_number": 830}]  # 830 visible
            mock_t.execute.return_value = mock_res_max
        elif name == "story_chunks":
            mock_res_chunks = MagicMock()
            mock_res_chunks.data = []
            mock_t.execute.return_value = mock_res_chunks
        return mock_t
    mock_supabase_cache_suite.table.side_effect = mock_table

    async def mock_exists(db, chapter_num):
        return True
    patch_oracle(monkeypatch, "verify_chapter_exists_in_db", mock_exists)

    # Enable trace
    monkeypatch.setenv("ORACLE_RAG_TRACE", "1")
    async def mock_is_admin(*args):
        return True
    patch_oracle(monkeypatch, "is_admin_request", mock_is_admin)

    # Mock RAG retrieval
    spy_search = MagicMock(return_value=[])
    monkeypatch.setattr("backend.rag.retrieval.search_story_chunks_hybrid_lexical", spy_search)

    # Question is general lore
    payload = {"question": "Hạ Huyền Sương là ai?", "chapter_progress": 9999}
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Effective progress should be clamped to 830 dynamically
    assert data["trace"]["effective_chapter_progress"] == 830

def test_chapter_831_abstains_immediately(mock_supabase_cache_suite, monkeypatch):
    """
    10. chapter 831 không gọi retrieval/LLM.
    """
    # Max chapter is 830. Target 831.
    async def mock_exists(db, chapter_num):
        return False
    patch_oracle(monkeypatch, "verify_chapter_exists_in_db", mock_exists)

    spy_search = MagicMock(return_value=[])
    monkeypatch.setattr("backend.rag.retrieval.search_story_chunks_hybrid_lexical", spy_search)
    
    spy_llm = MagicMock()
    patch_oracle(monkeypatch, "call_ai_provider_result", spy_llm)

    payload = {"question": "tóm tắt chương 831", "chapter_progress": 831}
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["abstained"] is True
    assert spy_search.call_count == 0
    assert spy_llm.call_count == 0

def test_chapter_830_retrieval_evidence_isolated(mock_supabase_cache_suite, monkeypatch):
    """11. chapter 830 answer evidence chỉ từ chapter 830."""
    monkeypatch.setenv("ORACLE_RAG_TRACE", "1")
    monkeypatch.setenv("ORACLE_RAG_ENABLED", "1")

    async def mock_exists(db, chapter_num):
        return True
    patch_oracle(monkeypatch, "verify_chapter_exists_in_db", mock_exists)

    async def mock_is_admin(*args):
        return True
    patch_oracle(monkeypatch, "is_admin_request", mock_is_admin)

    # Let retrieval return chunks from multiple chapters (simulating potential logic error)
    mock_chunks = [
        {"id": "chunk1", "chapter_number": 830, "content_plain": "Chương 830 trộm trứng."},
        {"id": "chunk2", "chapter_number": 3, "content_plain": "Chương 3 bắt đầu."},
        {"id": "chunk3", "chapter_number": 411, "content_plain": "Chương 411 đối thoại."}
    ]
    # In search_story_chunks_hybrid_lexical we mock the return
    def mock_search_exact(*args, exact_chapter=None, **kwargs):
        # If exact chapter is specified, filter by it
        if exact_chapter is not None:
            return [c for c in mock_chunks if c["chapter_number"] == exact_chapter]
        return mock_chunks

    monkeypatch.setattr("backend.rag.retrieval.search_story_chunks_hybrid_lexical", mock_search_exact)

    # Mock LLM call
    async def mock_llm(*args, **kwargs):
        class Result:
            status = "success"
            text = "Tóm tắt chương 830 sạch."
            attempts = []
        return Result()
    patch_oracle(monkeypatch, "call_ai_provider_result", mock_llm)

    payload = {"question": "tóm tắt chương 830", "chapter_progress": 830}
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    # selected_chapters must only contain 830
    assert data["trace"]["selected_chapters"] == [830]
    assert 3 not in data["trace"]["selected_chapters"]
    assert 411 not in data["trace"]["selected_chapters"]
