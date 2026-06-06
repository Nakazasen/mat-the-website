import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from contextlib import contextmanager

from backend.routes.ai_oracle import (
    is_oracle_rag_enabled,
    get_rag_context_for_oracle,
    call_ai_provider_result,
)

@contextmanager
def patch_oracle_func(func_name, **kwargs):
    import sys
    patched = []
    targets = []
    for mod_name in list(sys.modules.keys()):
        if mod_name.endswith("routes.ai_oracle"):
            targets.append(f"{mod_name}.{func_name}")
    if not targets:
        targets = [f"routes.ai_oracle.{func_name}", f"backend.routes.ai_oracle.{func_name}"]

    is_async = func_name != "get_rag_context_for_oracle"
    mock_obj = AsyncMock(**kwargs) if is_async else MagicMock(**kwargs)
    for target in targets:
        try:
            p = patch(target, mock_obj)
            p.start()
            patched.append(p)
        except Exception:
            pass
    try:
        yield mock_obj
    finally:
        for p in patched:
            try:
                p.stop()
            except Exception:
                pass

# Test 1 & 2: is_oracle_rag_enabled default and values
def test_is_oracle_rag_enabled():
    # Clear env
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]

    # Default is False
    assert is_oracle_rag_enabled() is False

    # Test true values (case-insensitive)
    for true_val in ["1", "true", "yes", "on", "TRUE", "Yes", "ON"]:
        os.environ["ORACLE_RAG_ENABLED"] = true_val
        assert is_oracle_rag_enabled() is True

    # Test false values
    for false_val in ["0", "false", "no", "off", "anything_else", ""]:
        os.environ["ORACLE_RAG_ENABLED"] = false_val
        assert is_oracle_rag_enabled() is False

    # Cleanup
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]

# Test 3: get_rag_context_for_oracle returns None when flag is OFF
def test_get_rag_context_for_oracle_returns_none_when_disabled():
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]

    context = get_rag_context_for_oracle("Hàn Phong", chapter_cap=5)
    assert context is None

# Test 4: get_rag_context_for_oracle catches exceptions and returns None safely
def test_get_rag_context_for_oracle_handles_error_safely():
    os.environ["ORACLE_RAG_ENABLED"] = "true"

    # Mock search function to raise Exception
    with patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", side_effect=Exception("Database down")):
        context = get_rag_context_for_oracle("Hàn Phong", chapter_cap=5)
        # Should catch exception, print warning, and return None (no crash)
        assert context is None

    # Cleanup
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]

# Test 5 & 7: get_rag_context_for_oracle returns formatted context and citations when ON
def test_get_rag_context_for_oracle_success():
    os.environ["ORACLE_RAG_ENABLED"] = "true"

    mock_results = [
        {
            "chapter_number": 1,
            "chapter_title": "Đầu lâu khổng lồ ngoài cửa sổ",
            "chunk_index": 0,
            "content_plain": "Hàn Phong đứng trước bàn giám đốc.",
            "content_hash": "hash123"
        }
    ]

    with patch("backend.rag.retrieval.search_story_chunks_hybrid_lexical", return_value=mock_results):
        context_data = get_rag_context_for_oracle("Hàn Phong", chapter_cap=5)
        assert context_data is not None
        assert context_data["chunks_used"] == 1
        assert "[CHƯƠNG 1 - Đầu lâu khổng lồ ngoài cửa sổ | chunk 0]" in context_data["context_text"]
        assert "Hàn Phong đứng trước bàn giám đốc." in context_data["context_text"]
        assert len(context_data["citations"]) == 1
        assert context_data["citations"][0]["content_hash"] == "hash123"

    # Cleanup
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]

# Test 6: call_ai_provider_result formats prompt correctly and keeps old prompt when rag_context is empty
@pytest.mark.asyncio
async def test_call_ai_provider_result_prompt_formatting():
    try:
        import main
        patch_path = "main.get_provider_router"
    except ImportError:
        patch_path = "backend.main.get_provider_router"

    # 1. Without RAG context
    with patch(patch_path) as mock_router_getter:
        mock_router = MagicMock()
        mock_router.route = AsyncMock()
        mock_router_getter.return_value = mock_router

        await call_ai_provider_result(
            question="Hàn Phong là ai?",
            chapter_cap=2,
            wiki_context="Wiki info",
            chapter_context="Chapter info",
            rag_context=""
        )

        # Check that system_instruction does not contain RAG section
        args, kwargs = mock_router.route.call_args
        ai_request = args[0]
        assert "[RAG_CONTEXT_STORY_CHUNKS]" not in ai_request.system_instruction
        assert "Wiki info" in ai_request.system_instruction

    # 2. With RAG context (Flag ON behavior)
    with patch(patch_path) as mock_router_getter:
        mock_router = MagicMock()
        mock_router.route = AsyncMock()
        mock_router_getter.return_value = mock_router

        await call_ai_provider_result(
            question="Hàn Phong là ai?",
            chapter_cap=2,
            wiki_context="Wiki info",
            chapter_context="Chapter info",
            rag_context="RAG content"
        )

        # Check that system_instruction contains RAG section
        args, kwargs = mock_router.route.call_args
        ai_request = args[0]
        assert "[RAG_CONTEXT_STORY_CHUNKS]" in ai_request.system_instruction
        assert "RAG content" in ai_request.system_instruction
        assert "Wiki info" in ai_request.system_instruction

@pytest.mark.asyncio
async def test_ask_oracle_endpoint_rag_routing():
    import sys
    print("\nALL AI ORACLE MODULES IN SYS:", [k for k in sys.modules.keys() if "ai_oracle" in k])
    try:
        from main import app
    except ImportError:
        from backend.main import app

    from fastapi.testclient import TestClient
    client = TestClient(app)

    # 1. When ORACLE_RAG_ENABLED is OFF
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]

    with patch_oracle_func("call_ai_provider_result") as mock_call, \
         patch_oracle_func("check_cache", return_value=None), \
         patch_oracle_func("get_wiki_context", return_value=""), \
         patch_oracle_func("get_chapter_context", return_value=""), \
         patch_oracle_func("check_rate_limit", return_value=True):

        mock_result = MagicMock()
        mock_result.status = "success"
        mock_result.text = "Mock answer that is long enough to pass validation"
        mock_call.return_value = mock_result

        response = client.post("/oracle/ask", json={
            "question": "Hàn Phong là ai?",
            "chapter_progress": 10
        })

        print("DEBUG RESPONSE status:", response.status_code)
        print("DEBUG RESPONSE text:", response.text.encode('ascii', errors='backslashreplace').decode('ascii'))
        print("DEBUG mock_call called:", mock_call.called)
        if mock_call.called:
            print("DEBUG mock_call call_args:", str(mock_call.call_args).encode('ascii', errors='backslashreplace').decode('ascii'))

        assert response.status_code == 200
        assert response.json()["answer"] == "Mock answer that is long enough to pass validation"
        assert response.json()["source"] == "ai_provider"

        args, kwargs = mock_call.call_args
        assert len(args) < 5 or args[4] == ""

    # 2. When ORACLE_RAG_ENABLED is ON
    os.environ["ORACLE_RAG_ENABLED"] = "true"

    with patch_oracle_func("call_ai_provider_result") as mock_call, \
         patch_oracle_func("check_cache", return_value=None), \
         patch_oracle_func("get_wiki_context", return_value=""), \
         patch_oracle_func("get_chapter_context", return_value=""), \
         patch_oracle_func("check_rate_limit", return_value=True), \
         patch_oracle_func("get_rag_context_for_oracle", return_value={"context_text": "Mock RAG Context", "citations": []}):

        mock_result = MagicMock()
        mock_result.status = "success"
        mock_result.text = "Mock RAG answer that is long enough to pass validation"
        mock_call.return_value = mock_result

        response = client.post("/oracle/ask", json={
            "question": "Hàn Phong là ai?",
            "chapter_progress": 10
        })

        assert response.status_code == 200
        assert response.json()["answer"] == "Mock RAG answer that is long enough to pass validation"

        args, kwargs = mock_call.call_args
        assert args[4] == "Mock RAG Context"

    # Cleanup
    if "ORACLE_RAG_ENABLED" in os.environ:
        del os.environ["ORACLE_RAG_ENABLED"]
