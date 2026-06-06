import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from backend.rag.evaluator import evaluate_case_retrieval, evaluate_all_cases

@pytest.mark.asyncio
async def test_evaluator_does_not_call_llm():
    """Verify evaluator processes pipeline without calling LLM (AI router mock should not be called)."""
    try:
        import main
        patch_path = "main.get_provider_router"
    except ImportError:
        patch_path = "backend.main.get_provider_router"
        
    case = {
        "id": "test-llm-call",
        "intent": "event",
        "question": "Con zombie đột biến",
        "chapter_progress": 5,
        "expected_sources": ["story_chunks"],
        "must_include": ["zombie"],
        "must_not_include": [],
        "expected_chapters": [1],
        "should_abstain": False,
        "notes": "Test LLM calls"
    }
    
    mock_results = [
        {
            "chapter_number": 1,
            "chapter_title": "Chapter 1",
            "chunk_index": 0,
            "content_plain": "Con zombie đột biến khổng lồ.",
            "content_hash": "hash1"
        }
    ]
    
    mock_supabase = MagicMock()
    
    with patch("backend.rag.evaluator.search_story_chunks_hybrid_lexical", return_value=mock_results), \
         patch(patch_path) as mock_router_getter:
         
         res = await evaluate_case_retrieval(case, mock_supabase)
         assert res["passed"] is True
         assert mock_router_getter.called is False  # LLM router getter was not invoked


@pytest.mark.asyncio
async def test_evaluator_output_fields():
    """Verify that case evaluation output contains all required schema fields."""
    case = {
        "id": "test-fields",
        "intent": "event",
        "question": "test question",
        "chapter_progress": 5,
        "expected_sources": [],
        "must_include": [],
        "must_not_include": [],
        "expected_chapters": [],
        "should_abstain": False,
        "notes": ""
    }
    
    mock_supabase = MagicMock()
    with patch("backend.rag.evaluator.search_story_chunks_hybrid_lexical", return_value=[]):
        res = await evaluate_case_retrieval(case, mock_supabase)
        assert "id" in res
        assert "intent" in res
        assert "passed" in res
        assert "chunks_used" in res
        assert "retrieved_chapters" in res
        assert "expected_chapters" in res
        assert "sources_observed" in res
        assert "fail_reasons" in res


@pytest.mark.asyncio
async def test_evaluator_anti_spoiler_spoiled():
    """Verify anti-spoiler case fails if a chunk beyond chapter_progress is retrieved."""
    case = {
        "id": "test-spoiler",
        "intent": "anti_spoiler",
        "question": "Ai chết ở chương 11?",
        "chapter_progress": 10,
        "expected_sources": [],
        "must_include": [],
        "must_not_include": [],
        "expected_chapters": [],
        "should_abstain": True,
        "notes": ""
    }
    
    # Mock retrieval returns a chunk from chapter 11 (which is a spoiler since progress is 10)
    mock_results = [
        {
            "chapter_number": 11,
            "chapter_title": "Chương tương lai",
            "chunk_index": 0,
            "content_plain": "Vương Mạnh hy sinh ở chương 11.",
            "content_hash": "hash11"
        }
    ]
    
    mock_supabase = MagicMock()
    with patch("backend.rag.evaluator.search_story_chunks_hybrid_lexical", return_value=mock_results):
        res = await evaluate_case_retrieval(case, mock_supabase)
        assert res["passed"] is False
        assert any("Spoiler detected" in reason for reason in res["fail_reasons"])


@pytest.mark.asyncio
async def test_evaluator_no_data_abstain():
    """Verify no_data case fails if chunks are retrieved despite should_abstain=True."""
    case = {
        "id": "test-nodata",
        "intent": "no_data",
        "question": "Hàn Phong kết hôn?",
        "chapter_progress": 10,
        "expected_sources": [],
        "must_include": [],
        "must_not_include": [],
        "expected_chapters": [],
        "should_abstain": True,
        "notes": ""
    }
    
    mock_results = [
        {
            "chapter_number": 5,
            "chapter_title": "Chương 5",
            "chunk_index": 0,
            "content_plain": "Random text matching keyword.",
            "content_hash": "hash5"
        }
    ]
    
    mock_supabase = MagicMock()
    with patch("backend.rag.evaluator.search_story_chunks_hybrid_lexical", return_value=mock_results):
        res = await evaluate_case_retrieval(case, mock_supabase)
        assert res["passed"] is False
        assert any("Expected abstain" in reason for reason in res["fail_reasons"])


@pytest.mark.asyncio
async def test_evaluator_expected_chapters_match():
    """Verify expected_chapters match calculations (passed when overlap exists, failed when no overlap)."""
    case = {
        "id": "test-chapters",
        "intent": "event",
        "question": "Tìm Trương Hạo",
        "chapter_progress": 10,
        "expected_sources": ["story_chunks"],
        "must_include": [],
        "must_not_include": [],
        "expected_chapters": [3, 4],
        "should_abstain": False,
        "notes": ""
    }
    
    mock_supabase = MagicMock()
    
    # Scenario A: Overlap exists (chapter 3 matches expected_chapters [3, 4]) -> Passed
    mock_results_ok = [
        {
            "chapter_number": 3,
            "chapter_title": "Chương 3",
            "chunk_index": 0,
            "content_plain": "Trương Hạo xuất hiện.",
            "content_hash": "hash3"
        }
    ]
    with patch("backend.rag.evaluator.search_story_chunks_hybrid_lexical", return_value=mock_results_ok):
        res = await evaluate_case_retrieval(case, mock_supabase)
        assert res["passed"] is True
        
    # Scenario B: No overlap (chapter 5 retrieved, expected [3, 4]) -> Failed
    mock_results_fail = [
        {
            "chapter_number": 5,
            "chapter_title": "Chương 5",
            "chunk_index": 0,
            "content_plain": "Trương Hạo không có ở đây.",
            "content_hash": "hash5"
        }
    ]
    with patch("backend.rag.evaluator.search_story_chunks_hybrid_lexical", return_value=mock_results_fail):
        res = await evaluate_case_retrieval(case, mock_supabase)
        assert res["passed"] is False
        assert any("No matching expected chapters" in reason for reason in res["fail_reasons"])


@pytest.mark.asyncio
async def test_evaluator_by_intent_aggregation():
    """Verify evaluate_all_cases groups statistics correctly by intent."""
    cases = [
        {
            "id": "case-1",
            "intent": "summary",
            "question": "Q1",
            "chapter_progress": 10,
            "expected_sources": [],
            "expected_chapters": [],
            "should_abstain": False
        },
        {
            "id": "case-2",
            "intent": "summary",
            "question": "Q2",
            "chapter_progress": 10,
            "expected_sources": [],
            "expected_chapters": [],
            "should_abstain": False
        },
        {
            "id": "case-3",
            "intent": "identity",
            "question": "Q3",
            "chapter_progress": 10,
            "expected_sources": [],
            "expected_chapters": [],
            "should_abstain": False
        }
    ]
    
    mock_supabase = MagicMock()
    with patch("backend.rag.evaluator.search_story_chunks_hybrid_lexical", return_value=[]), \
         patch("backend.routes.ai_oracle.get_entity_context_for_oracle", AsyncMock(return_value=None)):
         
         summary = await evaluate_all_cases(cases, mock_supabase)
         assert summary["total"] == 3
         assert "summary" in summary["by_intent"]
         assert "identity" in summary["by_intent"]
         assert summary["by_intent"]["summary"]["total"] == 2
         assert summary["by_intent"]["identity"]["total"] == 1
