# test_oracle_feedback_to_golden_promotion.py
# Unit tests for Autonomous Feedback-to-Golden Promotion Engine

import sys
import os
import json
import pytest
from unittest.mock import MagicMock, patch

# Ensure repo root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scripts.build_golden_candidates_from_feedback import main as builder_main
from backend.scripts.promote_golden_candidates import main as promoter_main
from backend.rag.golden_promotion_policy import determine_trust_level, parse_constraints_from_comment

def test_determine_trust_level():
    assert determine_trust_level({"user_comment": "This is a bug [AUTHOR]"}) == "author"
    assert determine_trust_level({"user_comment": "Bug found [SYSTEM]"}) == "system"
    assert determine_trust_level({"user_comment": "Nice app [TRUSTED]"}) == "trusted_reader"
    assert determine_trust_level({"user_comment": "Error [READER]"}) == "reader"
    assert determine_trust_level({"user_comment": "Normal feedback"}) == "anonymous"

def test_parse_constraints_from_comment():
    comment = 'must_not_contain: ["waste", "trash"]\nforbidden_patterns: ["sông Lệ Giang"]'
    suggested = 'required_terms: ["chiến dịch"]\nexpected_abstain: "Chưa đủ dữ liệu"'
    
    mnc, sfp, srt, eat = parse_constraints_from_comment(comment, suggested)
    assert "waste" in mnc
    assert "sông Lệ Giang" in sfp
    assert "chiến dịch" in srt
    assert eat == "Chưa đủ dữ liệu"

class MockResponse:
    def __init__(self, data):
        self.data = data
        self.count = len(data)

class MockSupabase:
    def __init__(self, feedbacks=None, candidates=None, cases=None):
        self.feedbacks = feedbacks or []
        self.candidates = candidates or []
        self.cases = cases or []
        self.upserted_candidates = []
        self.upserted_cases = []
        self.updated_candidates = []
        self.current_table = ""

    def table(self, name):
        self.current_table = name
        return self

    def select(self, *args, **kwargs):
        return self

    def in_(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def execute(self):
        if self.current_table == "rag_feedback":
            return MockResponse(self.feedbacks)
        elif self.current_table == "oracle_golden_regression_candidates":
            return MockResponse(self.candidates)
        elif self.current_table == "oracle_golden_regression_cases":
            return MockResponse(self.cases)
        return MockResponse([])

    def upsert(self, payload, *args, **kwargs):
        if self.current_table == "oracle_golden_regression_candidates":
            self.upserted_candidates.append(payload)
        elif self.current_table == "oracle_golden_regression_cases":
            self.upserted_cases.append(payload)
        return self

    def update(self, payload, *args, **kwargs):
        if self.current_table == "oracle_golden_regression_candidates":
            self.updated_candidates.append(payload)
        return self

def test_builder_dry_run_no_writes():
    feedbacks = [
        {
            "id": "fb1",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "user_comment": "[AUTHOR] must_not_contain: [\"trash\"]",
            "status": "pending"
        }
    ]
    mock_supabase = MockSupabase(feedbacks=feedbacks)

    with patch("backend.scripts.build_golden_candidates_from_feedback.supabase", mock_supabase), \
         patch("sys.argv", ["build_golden_candidates_from_feedback.py", "--dry-run", "--json"]):
         
         builder_main()
         assert len(mock_supabase.upserted_candidates) == 0

def test_builder_author_feedback_score_ready():
    feedbacks = [
        {
            "id": "fb1",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "user_comment": "[AUTHOR] must_not_contain: [\"trash\"]",
            "status": "pending"
        }
    ]
    mock_supabase = MockSupabase(feedbacks=feedbacks)

    with patch("backend.scripts.build_golden_candidates_from_feedback.supabase", mock_supabase), \
         patch("sys.argv", ["build_golden_candidates_from_feedback.py", "--write", "--json"]):
         
         builder_main()
         assert len(mock_supabase.upserted_candidates) == 1
         called_payload = mock_supabase.upserted_candidates[0]
         assert called_payload["trust_level"] == "author"
         assert called_payload["promotion_score"] == 1.0
         assert called_payload["promotion_status"] == "auto_promote_ready"
         assert "trash" in called_payload["must_not_contain"]

def test_builder_reader_feedback_quorum_scoring():
    # 1 Reader feedback -> score 0.34 (observing)
    feedbacks_single = [
        {
            "id": "fb1",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "user_comment": "[READER] must_not_contain: [\"trash\"]",
            "status": "pending"
        }
    ]
    mock_supabase = MockSupabase(feedbacks=feedbacks_single)

    with patch("backend.scripts.build_golden_candidates_from_feedback.supabase", mock_supabase), \
         patch("sys.argv", ["build_golden_candidates_from_feedback.py", "--write", "--json"]):
         
         builder_main()
         called_payload = mock_supabase.upserted_candidates[0]
         assert called_payload["promotion_score"] == 0.34
         assert called_payload["promotion_status"] == "observing"

    # 3 Reader feedbacks -> score 1.02 >= 1.0 (auto_promote_ready)
    feedbacks_quorum = [
        {
            "id": "fb1",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "user_comment": "[READER] must_not_contain: [\"trash\"]",
            "status": "pending"
        },
        {
            "id": "fb2",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "user_comment": "[READER]",
            "status": "pending"
        },
        {
            "id": "fb3",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "user_comment": "[READER]",
            "status": "pending"
        }
    ]
    mock_supabase = MockSupabase(feedbacks=feedbacks_quorum)
    with patch("backend.scripts.build_golden_candidates_from_feedback.supabase", mock_supabase), \
         patch("sys.argv", ["build_golden_candidates_from_feedback.py", "--write", "--json"]):
         
         builder_main()
         called_payload = mock_supabase.upserted_candidates[0]
         assert called_payload["promotion_score"] == 1.02
         assert called_payload["promotion_status"] == "auto_promote_ready"

def test_builder_anonymous_feedback_observing():
    feedbacks = [
        {
            "id": "fb1",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "user_comment": "Normal comment must_not_contain: [\"trash\"]",
            "status": "pending"
        }
    ]
    mock_supabase = MockSupabase(feedbacks=feedbacks)

    with patch("backend.scripts.build_golden_candidates_from_feedback.supabase", mock_supabase), \
         patch("sys.argv", ["build_golden_candidates_from_feedback.py", "--write", "--json"]):
         
         builder_main()
         called_payload = mock_supabase.upserted_candidates[0]
         assert called_payload["trust_level"] == "anonymous"
         assert called_payload["promotion_score"] == 0.2
         assert called_payload["promotion_status"] == "observing"

def test_builder_skips_ambiguous_or_short_question():
    feedbacks = [
        {
            "id": "fb1",
            "question": "Lệ",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "user_comment": "[AUTHOR] must_not_contain: [\"trash\"]",
            "status": "pending"
        }
    ]
    mock_supabase = MockSupabase(feedbacks=feedbacks)

    with patch("backend.scripts.build_golden_candidates_from_feedback.supabase", mock_supabase), \
         patch("sys.argv", ["build_golden_candidates_from_feedback.py", "--write", "--json"]):
         
         builder_main()
         assert len(mock_supabase.upserted_candidates) == 0

def test_promoter_author_repro_promotes():
    candidates = [
        {
            "id": "cand1",
            "candidate_key": "candidate_author_test",
            "source": "author_feedback",
            "trust_level": "author",
            "question": "Chiến dịch Lệ Giang?",
            "chapter_progress": 829,
            "must_not_contain": ["trash"],
            "semantic_forbidden_patterns": [],
            "semantic_required_any_terms": [],
            "acceptable_abstain": True,
            "expected_abstain_text": "",
            "promotion_status": "auto_promote_ready",
            "promotion_score": 1.0,
            "feedback_ids": ["fb1"]
        }
    ]
    mock_supabase = MockSupabase(candidates=candidates)

    mock_response = MagicMock()
    mock_response.__enter__.return_value.status = 200
    mock_response.__enter__.return_value.read.return_value = json.dumps({
        "answer": "This is a trash response containing toxic waste.",
        "source": "local_wiki"
    }).encode("utf-8")

    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["promote_golden_candidates.py", "--write", "--json"]):
         
         promoter_main()
         
         # Should update candidate status to auto_promoted
         assert len(mock_supabase.updated_candidates) == 1
         assert mock_supabase.updated_candidates[0]["promotion_status"] == "auto_promoted"
         
         # Should insert regression case
         assert len(mock_supabase.upserted_cases) == 1
         assert mock_supabase.upserted_cases[0]["case_key"] == "candidate_author_test"
         assert mock_supabase.upserted_cases[0]["status"] == "active"

def test_promoter_fails_runtime_no_promotion():
    candidates = [
        {
            "id": "cand1",
            "candidate_key": "candidate_author_test",
            "source": "author_feedback",
            "trust_level": "author",
            "question": "Chiến dịch Lệ Giang?",
            "chapter_progress": 829,
            "must_not_contain": ["trash"],
            "promotion_status": "auto_promote_ready",
            "promotion_score": 1.0,
            "feedback_ids": ["fb1"]
        }
    ]
    mock_supabase = MockSupabase(candidates=candidates)

    # HTTP response fails
    mock_response = MagicMock()
    mock_response.__enter__.return_value.status = 500

    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["promote_golden_candidates.py", "--write", "--json"]):
         
         promoter_main()
         
         assert len(mock_supabase.updated_candidates) == 1
         assert mock_supabase.updated_candidates[0]["promotion_status"] == "failed_runtime"
         assert len(mock_supabase.upserted_cases) == 0

def test_promoter_stale_fixed_no_repro():
    candidates = [
        {
            "id": "cand1",
            "candidate_key": "candidate_author_test",
            "source": "author_feedback",
            "trust_level": "author",
            "question": "Chiến dịch Lệ Giang?",
            "chapter_progress": 829,
            "must_not_contain": ["trash"],
            "promotion_status": "auto_promote_ready",
            "promotion_score": 1.0,
            "feedback_ids": ["fb1"]
        }
    ]
    mock_supabase = MockSupabase(candidates=candidates)

    # Clean response (does not contain forbidden term "trash")
    mock_response = MagicMock()
    mock_response.__enter__.return_value.status = 200
    mock_response.__enter__.return_value.read.return_value = json.dumps({
        "answer": "This is a clean and verified response.",
        "source": "local_wiki"
    }).encode("utf-8")

    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["promote_golden_candidates.py", "--write", "--json"]):
         
         promoter_main()
         
         assert len(mock_supabase.updated_candidates) == 1
         assert mock_supabase.updated_candidates[0]["promotion_status"] == "observing"
         assert "Stale" in mock_supabase.updated_candidates[0]["promotion_reason"]
         assert len(mock_supabase.upserted_cases) == 0

def test_promoter_blocked_on_conflict():
    candidates = [
        {
            "id": "cand1",
            "candidate_key": "candidate_author_test",
            "source": "author_feedback",
            "trust_level": "author",
            "question": "Chiến dịch Lệ Giang?",
            "chapter_progress": 829,
            "must_not_contain": ["trash"],
            "promotion_status": "auto_promote_ready",
            "promotion_score": 1.0,
            "feedback_ids": ["fb1"]
        }
    ]
    # Active case with same key
    cases = [
        {
            "case_key": "candidate_author_test",
            "status": "active"
        }
    ]
    mock_supabase = MockSupabase(candidates=candidates, cases=cases)

    mock_response = MagicMock()
    mock_response.__enter__.return_value.status = 200
    mock_response.__enter__.return_value.read.return_value = json.dumps({
        "answer": "trash response",
        "source": "local_wiki"
    }).encode("utf-8")

    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["promote_golden_candidates.py", "--write", "--json"]):
         
         promoter_main()
         
         assert len(mock_supabase.updated_candidates) == 1
         assert mock_supabase.updated_candidates[0]["promotion_status"] == "blocked_conflict"
         assert len(mock_supabase.upserted_cases) == 0

def test_promoter_preserves_disabled_case():
    candidates = [
        {
            "id": "cand1",
            "candidate_key": "candidate_author_test",
            "source": "author_feedback",
            "trust_level": "author",
            "question": "Chiến dịch Lệ Giang?",
            "chapter_progress": 829,
            "must_not_contain": ["trash"],
            "promotion_status": "auto_promote_ready",
            "promotion_score": 1.0,
            "feedback_ids": ["fb1"]
        }
    ]
    # Existing case is disabled
    cases = [
        {
            "case_key": "candidate_author_test",
            "status": "disabled"
        }
    ]
    mock_supabase = MockSupabase(candidates=candidates, cases=cases)

    mock_response = MagicMock()
    mock_response.__enter__.return_value.status = 200
    mock_response.__enter__.return_value.read.return_value = json.dumps({
        "answer": "trash response",
        "source": "local_wiki"
    }).encode("utf-8")

    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["promote_golden_candidates.py", "--write", "--json"]):
         
         promoter_main()
         
         # Upsert should not be called to avoid overwriting status disabled to active
         assert len(mock_supabase.upserted_cases) == 0
