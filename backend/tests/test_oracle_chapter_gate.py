# backend/tests/test_oracle_chapter_gate.py
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def patch_oracle(monkeypatch, name, value):
    for module_name in ["routes.ai_oracle", "backend.routes.ai_oracle"]:
        if module_name in sys.modules:
            monkeypatch.setattr(f"{module_name}.{name}", value)

@pytest.fixture
def mock_supabase_db(monkeypatch):
    """Mocks Supabase database queries for max chapter and chapter existence checks."""
    mock_client = MagicMock()
    
    # Simple default mock setup
    def mock_table(name):
        mock_t = MagicMock()
        mock_t.select.return_value = mock_t
        mock_t.order.return_value = mock_t
        mock_t.limit.return_value = mock_t
        mock_t.eq.return_value = mock_t
        
        # Determine query return values based on table name
        if name == "chapters":
            # Default max chapter = 829
            mock_res_max = MagicMock()
            mock_res_max.data = [{"chapter_number": 829}]
            mock_t.execute.return_value = mock_res_max
        elif name == "story_chunks":
            # Default empty chunks
            mock_res_chunks = MagicMock()
            mock_res_chunks.data = []
            mock_t.execute.return_value = mock_res_chunks
        else:
            mock_res = MagicMock()
            mock_res.data = []
            mock_t.execute.return_value = mock_res
            
        return mock_t
        
    mock_client.table.side_effect = mock_table
    
    # Patch main and backend.main supabase client references
    for module_name in ["main", "backend.main"]:
        if module_name in sys.modules:
            monkeypatch.setattr(sys.modules[module_name], "supabase", mock_client)
            
    # Mock rate limit globally for all oracle tests as an async function
    async def mock_rate_limit(*args, **kwargs):
        return True
    patch_oracle(monkeypatch, "check_rate_limit", mock_rate_limit)

    return mock_client

def test_gate_explicit_unavailable_chapter(mock_supabase_db, monkeypatch):
    """1. Explicit 'tóm tắt chương 830', max=829: abstain chapter_unavailable, no retrieval, no LLM."""
    payload = {
        "question": "tóm tắt chương 830",
        "chapter_progress": 830
    }
    
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["abstained"] is True
    assert data["abstain_reason"] == "chapter_unavailable"
    assert "chưa được đăng" in data["answer"]
    assert data["source"] == "gate"

def test_gate_implicit_unavailable_chapter(mock_supabase_db, monkeypatch):
    """2. 'nội dung chương này là gì?', chapter_progress=830, max=829: abstain, no retrieval, no LLM."""
    payload = {
        "question": "nội dung chương này là gì?",
        "chapter_progress": 830
    }
    
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["abstained"] is True
    assert data["abstain_reason"] == "chapter_unavailable"
    assert "chưa được đăng" in data["answer"]
    assert data["source"] == "gate"

def test_gate_available_chapter_retrieval(mock_supabase_db, monkeypatch):
    """3. 'tóm tắt chương 829': retrieves successfully using effective chapter cap 829."""
    # Mock verify_chapter_exists_in_db to return True for 829
    async def mock_exists(db, chapter_num):
        return True
    patch_oracle(monkeypatch, "verify_chapter_exists_in_db", mock_exists)
    
    # Mock RAG retrieval
    def mock_get_rag(question, cap, limit=5):
        return {
            "context_text": "[CHƯƠNG 829 - Đàm phán | chunk 0] Nội dung thương lượng...",
            "citations": [{"chapter_number": 829, "chunk_index": 0, "source": "story_chunks"}]
        }
    patch_oracle(monkeypatch, "get_rag_context_for_oracle", mock_get_rag)
    
    # Mock LLM call response
    async def mock_ai_call(*args, **kwargs):
        class MockAIResult:
            status = "success"
            text = "Bản tóm tắt chương 829 chuẩn."
            attempts = []
            model = "mock-model"
        return MockAIResult()
    patch_oracle(monkeypatch, "call_ai_provider_result", mock_ai_call)
    
    payload = {
        "question": "tóm tắt chương 829",
        "chapter_progress": 829
    }
    
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["abstained"] is False
    assert data["answer"] == "Bản tóm tắt chương 829 chuẩn."
    assert data["source"] == "ai_provider"

def test_gate_general_question_clamping(mock_supabase_db, monkeypatch):
    """4. General entity question với chapter_progress=830: clamps effective progress to 829."""
    # Mock RAG to return lore context <= 829
    def mock_get_rag(question, cap, limit=5):
        # Assert clamping is enforced
        assert cap == 829
        return {
            "context_text": "Hạ Huyền Sương là thủ lĩnh...",
            "citations": []
        }
    patch_oracle(monkeypatch, "get_rag_context_for_oracle", mock_get_rag)
    
    async def mock_ai_call(*args, **kwargs):
        class MockAIResult:
            status = "success"
            text = "Hạ Huyền Sương là nhân vật hỗ trợ."
            attempts = []
            model = "mock-model"
        return MockAIResult()
    patch_oracle(monkeypatch, "call_ai_provider_result", mock_ai_call)
    
    payload = {
        "question": "Hạ Huyền Sương là ai?",
        "chapter_progress": 830
    }
    
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["abstained"] is False
    assert "Hạ Huyền Sương" in data["answer"]

def test_gate_missing_chapter_chunks(mock_supabase_db, monkeypatch):
    """5. Chapter tồn tại trong chapters nhưng không có story_chunks: abstain missing_chapter_chunks."""
    # Mock: chapter 820 is <= 829, but verify_chapter_exists_in_db returns False (no chunks)
    async def mock_exists(db, chapter_num):
        return False
    patch_oracle(monkeypatch, "verify_chapter_exists_in_db", mock_exists)
    
    payload = {
        "question": "tóm tắt chương 820",
        "chapter_progress": 820
    }
    
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["abstained"] is True
    assert data["abstain_reason"] == "missing_chapter_chunks"
    assert "chưa được đăng" in data["answer"]
    assert data["source"] == "gate"

def test_gate_explicit_chapter_lower_than_progress(mock_supabase_db, monkeypatch):
    """6. Explicit requested chapter thấp hơn progress: dùng đúng requested chapter."""
    # Mock exists for 800
    async def mock_exists(db, chapter_num):
        assert chapter_num == 800
        return True
    patch_oracle(monkeypatch, "verify_chapter_exists_in_db", mock_exists)
    
    # Mock RAG to assert target cap
    def mock_get_rag(question, cap, limit=5):
        assert cap == 800
        return {
            "context_text": "Nội dung chương 800...",
            "citations": []
        }
    patch_oracle(monkeypatch, "get_rag_context_for_oracle", mock_get_rag)
    
    async def mock_ai_call(*args, **kwargs):
        class MockAIResult:
            status = "success"
            text = "Tóm tắt chương 800 hoàn tất."
            attempts = []
            model = "mock-model"
        return MockAIResult()
    patch_oracle(monkeypatch, "call_ai_provider_result", mock_ai_call)
    
    payload = {
        "question": "tóm tắt chương 800",
        "chapter_progress": 829
    }
    
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["abstained"] is False
    assert data["requested_chapter"] == 800

def test_gate_trace_default_off(mock_supabase_db, monkeypatch):
    """8. Trace mặc định tắt."""
    monkeypatch.setenv("ORACLE_RAG_TRACE", "0")
    
    # Mock admin verify
    async def mock_verify_admin(*args):
        return True
    patch_oracle(monkeypatch, "is_admin_request", mock_verify_admin)
    
    payload = {
        "question": "tóm tắt chương 830",
        "chapter_progress": 830
    }
    
    response = client.post("/oracle/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "trace" not in data or data["trace"] is None

def test_gate_trace_admin_on(mock_supabase_db, monkeypatch):
    """9. Trace bật có đủ trường nhưng không có secret (khi admin truy cập)."""
    monkeypatch.setenv("ORACLE_RAG_TRACE", "1")
    
    async def mock_verify_admin(*args):
        return True
    patch_oracle(monkeypatch, "is_admin_request", mock_verify_admin)
    
    payload = {
        "question": "tóm tắt chương 830",
        "chapter_progress": 830
    }
    
    response = client.post("/oracle/ask", json=payload, headers={"Authorization": "Bearer admin-token"})
    assert response.status_code == 200
    data = response.json()
    assert data["trace"] is not None
    trace = data["trace"]
    
    required_fields = [
        "original_question", "normalized_question", "detected_intent",
        "explicit_requested_chapter", "chapter_progress", "max_available_chapter",
        "effective_chapter_progress", "chapter_exists", "candidate_chunk_ids",
        "candidate_chapters", "candidate_scores", "selected_chunk_ids",
        "selected_chapters", "abstain_reason", "llm_called"
    ]
    for field in required_fields:
        assert field in trace
        
    # Check trace content
    assert trace["detected_intent"] == "chapter_summary"
    assert trace["explicit_requested_chapter"] == 830
    assert trace["llm_called"] is False
