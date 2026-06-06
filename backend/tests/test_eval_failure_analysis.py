import os
import sys
import json
import pytest
from unittest.mock import patch

# Path resolution
sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.rag.eval_failure_analysis import analyze_evaluation_failures

def test_failure_analysis_categorization_and_counting():
    """Verify that evaluate failures are categorized correctly by reason and counted."""
    mock_results = {
        "case_source": "all",
        "duplicate_ids": ["feedback_dup_1"],
        "results": [
            # 1. Passed case (should be ignored in failure counts)
            {
                "id": "base-01",
                "intent": "event",
                "passed": True,
                "chunks_used": 2,
                "fail_reasons": []
            },
            # 2. Spoiler leak
            {
                "id": "base-02",
                "intent": "anti_spoiler",
                "passed": False,
                "chunks_used": 1,
                "fail_reasons": ["Spoiler detected: chapter 11 > chapter_progress 10"]
            },
            # 3. Missing entity context (explicit fail reason)
            {
                "id": "feedback_01",
                "intent": "identity",
                "passed": False,
                "chunks_used": 0,
                "missing_entity_context": True,
                "entity_name": "Lâm Nhã Vy",
                "fail_reasons": ["Expected source 'entity_context' was not retrieved."]
            },
            # 4. Chapters not retrieved
            {
                "id": "base-04",
                "intent": "event",
                "passed": False,
                "chunks_used": 2,
                "fail_reasons": ["No matching expected chapters. Expected [3, 4], got [1, 2]."]
            },
            # 5. Retrieve when should abstain
            {
                "id": "feedback_02",
                "intent": "no_data",
                "passed": False,
                "chunks_used": 3,
                "fail_reasons": ["Expected abstain (should_abstain=True) but chunks_used was 3."]
            },
            # 6. Intent mismatch
            {
                "id": "base-06",
                "intent": "identity",
                "passed": False,
                "chunks_used": 1,
                "fail_reasons": ["Intent is identity but is_identity_question returned False."]
            },
            # 7. Source mismatch
            {
                "id": "base-07",
                "intent": "event",
                "passed": False,
                "chunks_used": 1,
                "fail_reasons": ["Expected source 'story_chunks' was not retrieved."]
            },
            # 8. No chunks retrieved (when not expecting abstain)
            {
                "id": "base-08",
                "intent": "event",
                "passed": False,
                "chunks_used": 0,
                "fail_reasons": ["Expected source 'story_chunks' was not retrieved."]
            }
        ]
    }

    analysis = analyze_evaluation_failures(mock_results)
    
    # 7 failed cases total (8 minus 1 passed)
    assert analysis["total_failures"] == 7
    # 2 feedback cases failed (feedback_01, feedback_02)
    assert analysis["feedback_failures"] == 2
    
    # Check failure reasons
    assert analysis["by_reason"]["anti_spoiler_violation"] == 1
    assert analysis["by_reason"]["missing_entity_context"] == 1
    assert analysis["by_reason"]["expected_chapter_not_retrieved"] == 1
    assert analysis["by_reason"]["no_data_should_abstain_but_retrieved"] == 1
    assert analysis["by_reason"]["intent_detection_mismatch"] == 1
    assert analysis["by_reason"]["source_mismatch"] == 2 # base-07 and base-08
    assert analysis["by_reason"]["no_chunks_retrieved"] == 2 # feedback_01 and base-08 have chunks_used == 0 and not abstain
    assert analysis["by_reason"]["duplicate_id"] == 1
    
    # Top missing entities
    assert len(analysis["top_missing_entities"]) == 1
    assert analysis["top_missing_entities"][0]["entity"] == "Lâm Nhã Vy"
    assert analysis["top_missing_entities"][0]["count"] == 1
    
    # Verify recommendations
    actions = analysis["recommended_next_actions"]
    assert "Add missing entity profiles to wiki_entries table." in actions
    assert "Improve hybrid lexical retrieval logic and check chunk indexing." in actions
    assert "Debug spoiler protection logic in search_story_chunks_hybrid_lexical." in actions
    assert "Refine abstain threshold and search matching rules." in actions
    assert "Resolve duplicate evaluation case IDs." in actions

def test_json_serialization():
    """Verify that failure analysis report is fully JSON-serializable."""
    mock_results = {
        "case_source": "feedback",
        "duplicate_ids": [],
        "results": [
            {
                "id": "feedback_01",
                "intent": "identity",
                "passed": False,
                "chunks_used": 0,
                "missing_entity_context": True,
                "entity_name": "Hàn Phong",
                "fail_reasons": ["Expected source 'entity_context' was not retrieved."]
            }
        ]
    }
    analysis = analyze_evaluation_failures(mock_results)
    try:
        json_str = json.dumps(analysis)
        assert json_str is not None
    except TypeError as e:
        pytest.fail(f"Failure analysis dict is not JSON serializable: {e}")
