import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from backend.routes.ai_oracle import (
    is_oracle_rag_enabled,
    get_rag_context_for_oracle,
    call_ai_provider_result,
)

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
