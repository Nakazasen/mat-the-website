import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Path resolution
sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.rag.retrieval import score_lexical_result, search_story_chunks_hybrid_lexical
from backend.rag.evaluator import load_eval_cases, evaluate_case_retrieval

def test_query_phrase_boosts():
    """Verify that exact query phrase in title and content gets significantly boosted."""
    row = {
        "chapter_number": 1,
        "chapter_title": "Đầu lâu khổng lồ xuất hiện",
        "content_plain": "Hàn Phong thấy một đầu lâu khổng lồ xuất hiện bên ngoài cửa sổ.",
        "content_hash": "hash_test",
        "temp_fts_match": False
    }
    keywords = ["đầu", "lâu", "khổng", "lồ"]
    
    score, reasons = score_lexical_result(row, "đầu lâu khổng lồ", keywords)
    assert "title_phrase" in reasons
    assert "content_phrase" in reasons
    # Should get phrase title boost (+150) + phrase content boost (+100) + keywords matches
    assert score >= 250.0

def test_exact_word_chapter_title_boost():
    """Verify exact keyword matching in title awards extra boost using boundaries."""
    row = {
        "chapter_number": 1,
        "chapter_title": "Hàn Phong",
        "content_plain": "Văn phòng giám đốc công ty.",
        "content_hash": "hash_test_exact"
    }
    keywords = ["diệp", "hàn", "phong"]
    score, reasons = score_lexical_result(row, "Diệp Hàn Phong", keywords)
    assert any("title_exact_keyword" in r for r in reasons)
    # 2 non-stop keywords match in title + 2 exact boundaries matches + title ngram boost
    assert score >= 180.0

def test_chapter_cap_retrieval():
    """Verify spoiler guard (chapter_cap) prevents retrieving later chapters."""
    # Mock supabase client
    mock_supabase = MagicMock()
    # Mock select().lte() chain
    mock_select = mock_supabase.table.return_value.select
    mock_lte = mock_select.return_value.lte
    mock_limit = mock_lte.return_value.limit
    
    mock_execute = mock_limit.return_value.execute
    mock_execute.return_value.data = []
    
    # Run retrieval with chapter_cap = 5
    search_story_chunks_hybrid_lexical(mock_supabase, "Hàn Phong", chapter_cap=5)
    
    # Assert lte("chapter_number", 5) was called on the mock chain
    assert mock_select.called
    mock_lte.assert_called_with("chapter_number", 5)

def test_load_feedback_eval_cases_still_works():
    """Verify feedback eval cases can still be loaded without errors."""
    cases = load_eval_cases("feedback")
    assert isinstance(cases, list)

@pytest.mark.asyncio
async def test_weak_match_should_abstain_triggers_fail_reason():
    """Verify that a low-score retrieval on should_abstain=True triggers weak_match_should_abstain."""
    case = {
        "id": "feedback_abstain_test",
        "intent": "no_data",
        "question": "Random question about future",
        "chapter_progress": 10,
        "expected_sources": [],
        "must_include": [],
        "must_not_include": [],
        "expected_chapters": [],
        "should_abstain": True,
        "notes": "Test abstain"
    }
    
    # We mock search_story_chunks_hybrid_lexical to return a chunk with a very low score (< 40)
    mock_weak_chunk = [
        {
            "chapter_number": 2,
            "chapter_title": "Chương 2",
            "chunk_index": 0,
            "content_plain": "Match only one random stopword.",
            "content_hash": "hash_weak",
            "score": 15.0, # Weak score
            "source": "story_chunks_hybrid_lexical",
            "match_reasons": ["content_keyword"]
        }
    ]
    
    mock_supabase = MagicMock()
    with patch("backend.rag.evaluator.search_story_chunks_hybrid_lexical", return_value=mock_weak_chunk):
        res = await evaluate_case_retrieval(case, mock_supabase)
        assert res["passed"] is False
        assert any("weak_match_should_abstain" in reason for reason in res["fail_reasons"])
        
@pytest.mark.asyncio
async def test_strong_match_should_abstain_triggers_fail_reason():
    """Verify that a high-score retrieval on should_abstain=True triggers no_data_should_abstain_but_retrieved."""
    case = {
        "id": "feedback_abstain_test_2",
        "intent": "no_data",
        "question": "Hàn Phong là ai?",
        "chapter_progress": 10,
        "expected_sources": [],
        "must_include": [],
        "must_not_include": [],
        "expected_chapters": [],
        "should_abstain": True,
        "notes": "Test abstain strong"
    }
    
    # We mock search_story_chunks_hybrid_lexical to return a chunk with a high score (>= 40)
    mock_strong_chunk = [
        {
            "chapter_number": 1,
            "chapter_title": "Chương 1",
            "chunk_index": 0,
            "content_plain": "Hàn Phong là nhân vật chính.",
            "content_hash": "hash_strong",
            "score": 120.0, # Strong score
            "source": "story_chunks_hybrid_lexical",
            "match_reasons": ["content_phrase"]
        }
    ]
    
    mock_supabase = MagicMock()
    with patch("backend.rag.evaluator.search_story_chunks_hybrid_lexical", return_value=mock_strong_chunk):
        res = await evaluate_case_retrieval(case, mock_supabase)
        assert res["passed"] is False
        assert any("no_data_should_abstain_but_retrieved" in reason for reason in res["fail_reasons"])
