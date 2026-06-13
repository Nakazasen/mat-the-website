# test_oracle_feedback_to_golden_promotion.py
# Unit tests for Autonomous Feedback-to-Golden Promotion Engine with Hardened Security

import sys
import os
import json
import pytest
import urllib.error
import ssl
from unittest.mock import MagicMock, patch

# Ensure repo root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scripts.build_golden_candidates_from_feedback import main as builder_main
from backend.scripts.promote_golden_candidates import main as promoter_main, verify_runtime_repro
from backend.rag.golden_promotion_policy import determine_trust_level, parse_constraints_from_comment


def test_determine_trust_level_ignores_comments():
    # 1. Comment tags do not grant trust
    assert determine_trust_level({"user_comment": "Bug [AUTHOR]"}) == "anonymous"
    assert determine_trust_level({"user_comment": "Bug [SYSTEM]"}) == "anonymous"
    assert determine_trust_level({"user_comment": "Bug [TRUSTED]"}) == "anonymous"
    assert determine_trust_level({"user_comment": "Bug [READER]"}) == "anonymous"


def test_determine_trust_level_server_side_fields():
    # 2. Server-side source and trust_level fields grant trust
    assert determine_trust_level({"source": "author_feedback"}) == "author"
    assert determine_trust_level({"trust_level": "author"}) == "author"
    assert determine_trust_level({"is_author": True}) == "author"
    assert determine_trust_level({"is_author": "true"}) == "author"

    assert determine_trust_level({"source": "system_detected_failure"}) == "system"
    assert determine_trust_level({"trust_level": "system"}) == "system"

    assert determine_trust_level({"trust_level": "trusted_reader"}) == "trusted_reader"
    assert determine_trust_level({"is_trusted_reader": True}) == "trusted_reader"
    assert determine_trust_level({"is_trusted_reader": "true"}) == "trusted_reader"

    assert determine_trust_level({"trust_level": "reader"}) == "reader"


def test_parse_constraints_from_comment():
    comment = 'must_not_contain: ["waste", "trash"]\nforbidden_patterns: ["sông Lệ Giang"]'
    suggested = 'required_terms: ["chiến dịch"]\nexpected_abstain: "Chưa đủ dữ liệu"'

    mnc, sfp, srt, eat = parse_constraints_from_comment(comment, suggested)
    assert "waste" in mnc
    assert "sông Lệ Giang" in sfp
    assert "chiến dịch" in srt
    assert eat == "Chưa đủ dữ liệu"


class MockResponse:
    def __init__(self, data, status=200):
        self.data = data
        self.status = status
        self.count = len(data)

    def read(self):
        return json.dumps(self.data).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


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
            "source": "author_feedback",
            "user_comment": "must_not_contain: [\"trash\"]",
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
            "source": "author_feedback",
            "user_comment": "must_not_contain: [\"trash\"]",
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
            "trust_level": "reader",
            "user_comment": "must_not_contain: [\"trash\"]",
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
            "trust_level": "reader",
            "user_comment": "must_not_contain: [\"trash\"]",
            "status": "pending"
        },
        {
            "id": "fb2",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "trust_level": "reader",
            "status": "pending"
        },
        {
            "id": "fb3",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "trust_level": "reader",
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
            "source": "author_feedback",
            "user_comment": "must_not_contain: [\"trash\"]",
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

    mock_response = MockResponse({
        "answer": "This is a trash response containing toxic waste.",
        "source": "local_wiki"
    }, 200)

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
    mock_response = MockResponse({
        "answer": "This is a clean and verified response.",
        "source": "local_wiki"
    }, 200)

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

    mock_response = MockResponse({
        "answer": "trash response",
        "source": "local_wiki"
    }, 200)

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

    mock_response = MockResponse({
        "answer": "trash response",
        "source": "local_wiki"
    }, 200)

    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["promote_golden_candidates.py", "--write", "--json"]):

         promoter_main()

         # Upsert should not be called to avoid overwriting status disabled to active
         assert len(mock_supabase.upserted_cases) == 0


def test_builder_spoofed_author_remains_observing():
    # 7. Spoofed author candidate remains observing
    # Feedback has [AUTHOR] tag in comments but no server-side author status (is_author=False)
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
         # Should remain observing, with trust level anonymous (comment ignored)
         assert called_payload["trust_level"] == "anonymous"
         assert called_payload["promotion_score"] == 0.2
         assert called_payload["promotion_status"] == "observing"
         # Evidence entry role claim is not verified
         assert called_payload["evidence"]["feedbacks"][0]["untrusted_claimed_role_hint"] == ["author"]
         assert called_payload["evidence"]["feedbacks"][0]["verified"] is False


def test_builder_reports_spoofed_claims():
    # 9. Builder report counts spoofed role claims
    feedbacks = [
        {
            "id": "fb1",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "user_comment": "[AUTHOR] [SYSTEM] [TRUSTED] must_not_contain: [\"trash\"]",
            "status": "pending"
        }
    ]
    mock_supabase = MockSupabase(feedbacks=feedbacks)

    with patch("backend.scripts.build_golden_candidates_from_feedback.supabase", mock_supabase), \
         patch("sys.argv", ["build_golden_candidates_from_feedback.py", "--write", "--json"]), \
         patch("builtins.print") as mock_print:

         builder_main()

         # Grab summary printed
         called_args = mock_print.call_args_list[0][0][0]
         summary = json.loads(called_args)
         assert summary["spoofed_trust_tags_detected"] == 1
         assert summary["untrusted_author_claims"] == 1
         assert summary["untrusted_system_claims"] == 1
         assert summary["untrusted_trusted_reader_claims"] == 1


def test_promoter_ssl_context_default():
    # 10. Runtime verification uses SSL verification by default
    mock_response = MockResponse({"answer": "clean"}, 200)

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        verify_runtime_repro(
            base_url="https://mat-the-website.onrender.com",
            question="Chiến dịch Lệ Giang?",
            chapter_progress=829,
            must_not_contain=["trash"],
            semantic_forbidden_patterns=[],
            semantic_required_any_terms=[],
            expected_abstain_text="",
            acceptable_abstain=True
        )

        # Verify that default context is passed and verify_mode is default (not CERT_NONE)
        called_ctx = mock_urlopen.call_args[1]["context"]
        assert called_ctx.verify_mode != ssl.CERT_NONE
        assert called_ctx.check_hostname is True


def test_promoter_rejects_insecure_on_prod_domain():
    # 11. Production URLs reject insecure flag and exit non-zero
    candidates = []
    mock_supabase = MockSupabase(candidates=candidates)

    for url in ["https://mat-the-website.onrender.com", "https://matthesinhhoa.vercel.app"]:
        with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
             patch("sys.argv", ["promote_golden_candidates.py", "--base-url", url, "--insecure-dev-no-ssl-verify"]):

             with pytest.raises(SystemExit) as excinfo:
                 promoter_main()
             assert excinfo.value.code == 1


def test_promoter_dry_run_no_writes():
    # 14. Dry-run does not write to database
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

    mock_response = MockResponse({
        "answer": "This is a trash response containing toxic waste.",
        "source": "local_wiki"
    }, 200)

    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["promote_golden_candidates.py", "--dry-run", "--json"]):

         promoter_main()
         assert len(mock_supabase.updated_candidates) == 0
         assert len(mock_supabase.upserted_cases) == 0
