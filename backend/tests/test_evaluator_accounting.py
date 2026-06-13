import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.scripts.evaluate_chapter_bot_quality import quota_tracker, call_judge_llm, evaluate_case

@pytest.mark.asyncio
async def test_quota_tracker_accounting():
    # Reset quota tracker
    quota_tracker["oracle_calls"] = 0
    quota_tracker["judge_calls"] = 0
    quota_tracker["provider_calls"] = 0
    quota_tracker["retries"] = 0
    quota_tracker["timeouts"] = 0
    quota_tracker["rate_limits"] = 0

    # 1. Test mock call_judge_llm success
    mock_router = MagicMock()
    mock_router.route = AsyncMock()
    mock_res = MagicMock()
    mock_res.status = "success"
    mock_res.text = '{"required_fact_recall": 1.0, "optional_fact_recall": 1.0, "important_cluster_recall": 1.0, "unsupported_claims": false, "contradiction_count": 0, "relevance": 1.0, "completeness": 1.0, "human_score": 3, "reasoning": "Perfect"}'
    mock_router.route.return_value = mock_res

    with patch("backend.scripts.evaluate_chapter_bot_quality.get_provider_router", return_value=mock_router):
        case = {
            "case_id": "test-01",
            "question": "Test question?",
            "human_reference_answer": "Golden answer",
            "acceptable_abstain": False,
            "required_facts": [],
            "optional_facts": [],
            "forbidden_facts": [],
            "important_event_clusters": []
        }
        res = await call_judge_llm(case, "Bot answer", "Context")
        assert res is not None
        assert res["human_score"] == 3
        assert quota_tracker["judge_calls"] == 1
        assert quota_tracker["provider_calls"] == 1

    # 2. Test mock evaluate_case
    mock_ask_oracle = AsyncMock()
    mock_bot_res = MagicMock()
    mock_bot_res.answer = "Bot answer"
    mock_bot_res.source = "test"
    mock_bot_res.abstained = False
    mock_bot_res.trace = {"candidate_chapters": [1], "selected_chapters": [1]}
    mock_ask_oracle.return_value = mock_bot_res

    with patch("backend.scripts.evaluate_chapter_bot_quality.ask_oracle", mock_ask_oracle), \
         patch("backend.scripts.evaluate_chapter_bot_quality.call_judge_llm", AsyncMock(return_value={"human_score": 3, "required_fact_recall": 1.0, "optional_fact_recall": 1.0, "important_cluster_recall": 1.0, "unsupported_claims": False, "contradiction_count": 0, "relevance": 1.0, "completeness": 1.0, "reasoning": "Ok"})):
        
        # Test case with allowed_chapter_range
        case = {
            "case_id": "test-02",
            "question": "Test question?",
            "chapter_progress": 10,
            "allowed_chapter_range": [1, 3]
        }
        sem = AsyncMock()
        res_case = await evaluate_case(1, case, sem)
        
        assert res_case["case_id"] == "test-02"
        # Verify expected_chapters is populated in trace
        assert res_case["trace"]["expected_chapters"] == [1, 2, 3]
        assert quota_tracker["oracle_calls"] == 1
        assert quota_tracker["provider_calls"] == 2  # 1 judge call + 1 oracle call
