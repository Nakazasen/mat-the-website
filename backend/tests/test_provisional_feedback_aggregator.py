import pytest
from backend.rag.provisional_feedback_aggregator import (
    normalize_feedback_type,
    group_feedback_by_provisional_id,
    count_unique_user_agents,
    calculate_dispute_score,
    decide_effective_status,
    build_feedback_summary_payload,
    summarize_feedback
)

def test_normalize_feedback_type():
    assert normalize_feedback_type("wrong_info") == "wrong_info"
    assert normalize_feedback_type("WRONG_EVIDENCE ") == "wrong_evidence"
    assert normalize_feedback_type("invalid_type") == "other"
    assert normalize_feedback_type(None) == "other"
    assert normalize_feedback_type(123) == "other"

def test_group_feedback_by_provisional_id():
    rows = [
        {"provisional_id": "pid-1", "user_comment": "comment 1"},
        {"provisional_id": "pid-2", "user_comment": "comment 2"},
        {"provisional_id": "pid-1", "user_comment": "comment 3"},
        {"provisional_id": None, "user_comment": "comment 4"},
        {"provisional_id": 123, "user_comment": "comment 5"},
    ]
    groups = group_feedback_by_provisional_id(rows)
    assert "pid-1" in groups
    assert "pid-2" in groups
    assert len(groups["pid-1"]) == 2
    assert len(groups["pid-2"]) == 1
    assert len(groups) == 2

def test_count_unique_user_agents():
    rows = [
        {"user_agent": "Mozilla/5.0"},
        {"user_agent": "mozilla/5.0 "}, # lowercase/trimmed duplicate
        {"user_agent": "Chrome/100"},
        {"user_agent": ""},
        {"user_agent": None},
    ]
    assert count_unique_user_agents(rows) == 2

def test_calculate_dispute_score():
    group = [
        {"feedback_type": "wrong_info"},
        {"feedback_type": "wrong_evidence"},
        {"feedback_type": "wrong_type"},
        {"feedback_type": "spoiler"},
        {"feedback_type": "duplicate"},
        {"feedback_type": "missing_info"},
        {"feedback_type": "other"},
        {"feedback_type": "unknown_val"} # default to other weight
    ]
    score, counts = calculate_dispute_score(group)
    # Weights: 1.5 + 1.5 + 1.2 + 1.0 + 1.0 + 0.5 + 0.3 + 0.3 = 7.3
    assert score == 7.3
    assert counts["wrong_info"] == 1
    assert counts["wrong_type"] == 1
    assert counts["other"] == 2 # other + unknown_val normalized

def test_decide_effective_status():
    # 1. Block policy
    s_block_info = {"wrong_info_count": 5}
    status, policy = decide_effective_status(s_block_info)
    assert status == "hidden_from_oracle" and policy == "block"

    s_block_evidence = {"wrong_evidence_count": 5}
    status, policy = decide_effective_status(s_block_evidence)
    assert status == "hidden_from_oracle" and policy == "block"

    # 2. Deprioritize policy
    s_deprioritize = {
        "total_feedback": 5,
        "unique_user_agent_count": 3,
        "wrong_info_count": 2,
        "wrong_evidence_count": 2
    }
    status, policy = decide_effective_status(s_deprioritize)
    assert status == "needs_review" and policy == "deprioritize"

    # 3. Warn policy (disputed)
    s_warn_dispute = {
        "total_feedback": 3,
        "dispute_score": 3.2
    }
    status, policy = decide_effective_status(s_warn_dispute)
    assert status == "disputed" and policy == "warn"

    # 4. Warn policy (duplicate)
    s_warn_duplicate = {
        "duplicate_count": 3
    }
    status, policy = decide_effective_status(s_warn_duplicate)
    assert status == "duplicate_suspected" and policy == "warn"

    # 5. Trusted (total < 3)
    s_trusted = {
        "total_feedback": 2,
        "dispute_score": 3.0,
        "unique_user_agent_count": 2
    }
    status, policy = decide_effective_status(s_trusted)
    assert status == "trusted" and policy == "allow"

def test_build_feedback_summary_payload():
    group = [
        {
            "provisional_id": "pid-123",
            "record_name": "Test Entry",
            "feedback_type": "wrong_info",
            "user_comment": "comment 1",
            "suggested_correction": "correction 1",
            "user_agent": "ua-1",
            "created_at": "2026-06-07T12:00:00Z"
        },
        {
            "provisional_id": "pid-123",
            "record_name": "Test Entry",
            "feedback_type": "wrong_info",
            "user_comment": "comment 2",
            "user_agent": "ua-2",
            "created_at": "2026-06-07T12:05:00Z"
        }
    ]
    summary = build_feedback_summary_payload(group)
    assert summary["provisional_id"] == "pid-123"
    assert summary["record_name"] == "Test Entry"
    assert summary["total_feedback"] == 2
    assert summary["wrong_info_count"] == 2
    assert summary["unique_user_agent_count"] == 2
    assert summary["dispute_score"] == 3.0
    assert summary["effective_status"] == "trusted" # total_feedback < 3
    assert summary["oracle_policy"] == "allow"
    assert len(summary["top_comments"]) == 2
    # Check ordering of top comments: recent first
    assert summary["top_comments"][0]["user_comment"] == "comment 2"
    assert summary["top_comments"][1]["user_comment"] == "comment 1"

def test_summarize_feedback():
    rows = [
        {"provisional_id": "p-1", "record_name": "E1", "feedback_type": "wrong_info"},
        {"provisional_id": "p-1", "record_name": "E1", "feedback_type": "wrong_info"},
        {"provisional_id": "p-2", "record_name": "E2", "feedback_type": "other"},
    ]
    summaries = summarize_feedback(rows)
    assert len(summaries) == 2
    p1 = next(s for s in summaries if s["provisional_id"] == "p-1")
    p2 = next(s for s in summaries if s["provisional_id"] == "p-2")
    assert p1["total_feedback"] == 2
    assert p2["total_feedback"] == 1
