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
    # 2. Server-side source and trust_level fields grant trust ONLY with verified provenance
    assert determine_trust_level({
        "source": "author_feedback",
        "trust_verified": True,
        "trust_verification_method": "jwt_author_profile"
    }) == "author"
    assert determine_trust_level({
        "trust_level": "author",
        "trust_verified": True,
        "trust_verification_method": "jwt_author_profile"
    }) == "author"
    assert determine_trust_level({
        "is_author": True,
        "trust_verified": True,
        "trust_verification_method": "jwt_author_profile"
    }) == "author"
    assert determine_trust_level({
        "is_author": "true",
        "trust_verified": True,
        "trust_verification_method": "jwt_author_profile"
    }) == "author"

    assert determine_trust_level({
        "source": "system_detected_failure",
        "source_verified": True,
        "trust_verification_method": "internal_backend_cron"
    }) == "system"
    assert determine_trust_level({
        "trust_level": "system",
        "trust_verified": True,
        "trust_verification_method": "internal_backend_cron"
    }) == "system"

    assert determine_trust_level({
        "trust_level": "trusted_reader",
        "trust_verified": True,
        "trust_verification_method": "jwt_trusted_reader_profile"
    }) == "trusted_reader"
    assert determine_trust_level({
        "is_trusted_reader": True,
        "trust_verified": True,
        "trust_verification_method": "jwt_trusted_reader_profile"
    }) == "trusted_reader"
    assert determine_trust_level({
        "is_trusted_reader": "true",
        "trust_verified": True,
        "trust_verification_method": "jwt_trusted_reader_profile"
    }) == "trusted_reader"

    assert determine_trust_level({
        "trust_level": "reader",
        "trust_verified": True,
        "trust_verification_method": "jwt_reader_profile"
    }) == "reader"


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
            "trust_level": "author",
            "trust_verified": True,
            "trust_verification_method": "jwt_author_profile",
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
            "trust_level": "author",
            "trust_verified": True,
            "trust_verification_method": "jwt_author_profile",
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
            "trust_verified": True,
            "trust_verification_method": "jwt_reader_profile",
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
            "trust_verified": True,
            "trust_verification_method": "jwt_reader_profile",
            "user_comment": "must_not_contain: [\"trash\"]",
            "status": "pending"
        },
        {
            "id": "fb2",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "trust_level": "reader",
            "trust_verified": True,
            "trust_verification_method": "jwt_reader_profile",
            "status": "pending"
        },
        {
            "id": "fb3",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "trust_level": "reader",
            "trust_verified": True,
            "trust_verification_method": "jwt_reader_profile",
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


# --- New Security & Trust Provenance Tests for Phase 11E-SEC2 ---

from fastapi.testclient import TestClient
try:
    from main import app
except ImportError:
    from backend.main import app

from backend.rag.feedback_trust_provenance import (
    determine_provenance,
    get_system_provenance,
    TRUST_AUTHOR,
    TRUST_TRUSTED_READER,
    TRUST_READER,
    TRUST_ANONYMOUS,
    TRUST_SYSTEM
)

client = TestClient(app)

def test_client_malicious_payload_fails_to_elevate():
    # 1. Anonymous request with spoofed trust params -> stored as anonymous
    payload = {
        "question": "Hàn Phong là ai?",
        "answer": "Hàn Phong...",
        "source": "author_feedback",  # Spoofed source
        "citations": [],
        "chapter_progress": 1,
        "feedback_type": "wrong",
        "user_comment": "Malicious attempt to elevate trust"
    }

    mock_supabase = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = [{"id": "fb-test-uuid"}]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_resp

    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase):

         # Mock auth to return no user (anonymous)
         mock_supabase.auth.get_user.side_effect = Exception("No auth header")

         response = client.post("/oracle/feedback", json=payload)
         assert response.status_code == 200

         # Verify inserted payload
         called_insert = mock_supabase.table.return_value.insert.call_args[0][0]
         # The source is sanitized to anonymous_feedback because client is not an author
         assert called_insert["source"] == "anonymous_feedback"
         assert called_insert["trust_level"] == TRUST_ANONYMOUS
         assert called_insert["trust_verified"] is False
         assert called_insert["is_author"] is False
         assert called_insert["is_trusted_reader"] is False


def test_authenticated_reader_payload_fails_to_elevate():
    # 2. Authenticated reader attempts to send privileged values -> gets reader trust only
    payload = {
        "question": "Hàn Phong là ai?",
        "answer": "Hàn Phong...",
        "source": "author_feedback",
        "citations": [],
        "chapter_progress": 1,
        "feedback_type": "wrong",
        "user_comment": "Privileged attempt"
    }

    mock_supabase = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = [{"id": "fb-test-uuid"}]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_resp

    # Mock user response for reader
    mock_user = MagicMock()
    mock_user.user.id = "reader-uuid-1234"
    mock_user.user.email = "reader@reader.com"
    mock_supabase.auth.get_user.return_value = mock_user

    # Mock profile to return reader role
    mock_profile_resp = MagicMock()
    mock_profile_resp.data = [{"role": "reader"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_profile_resp

    headers = {"Authorization": "Bearer reader-jwt-token"}

    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase):

         response = client.post("/oracle/feedback", json=payload, headers=headers)
         assert response.status_code == 200

         called_insert = mock_supabase.table.return_value.insert.call_args[0][0]
         # Strip malicious author_feedback source and keep reader_feedback
         assert called_insert["source"] == "anonymous_feedback"
         assert called_insert["trust_level"] == TRUST_READER
         assert called_insert["trust_verified"] is True
         assert called_insert["trust_verification_method"] == "jwt_reader_profile"
         assert called_insert["is_author"] is False


def test_verified_author_jwt_grants_author_trust():
    # 4. Verified author JWT -> server writes author provenance
    mock_supabase = MagicMock()

    mock_user = MagicMock()
    mock_user.user.id = "author-uuid"
    mock_user.user.email = "author@novel.com"
    mock_supabase.auth.get_user.return_value = mock_user

    mock_profile_resp = MagicMock()
    mock_profile_resp.data = [{"role": "author"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_profile_resp

    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase):
        provenance = determine_provenance("Bearer author-token", "author_feedback", caller_context="authenticated_public")
        assert provenance["trust_level"] == TRUST_AUTHOR
        assert provenance["trust_verified"] is True
        assert provenance["trust_verification_method"] == "jwt_author_profile"
        assert provenance["is_author"] is True
        assert provenance["source"] == "author_feedback"


def test_verified_trusted_reader_jwt_grants_trusted_reader_trust():
    # 5. Verified trusted reader profile -> trusted_reader provenance
    mock_supabase = MagicMock()

    mock_user = MagicMock()
    mock_user.user.id = "tr-uuid"
    mock_user.user.email = "trusted@novel.com"
    mock_supabase.auth.get_user.return_value = mock_user

    mock_profile_resp = MagicMock()
    mock_profile_resp.data = [{"role": "trusted_reader"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_profile_resp

    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase):
        provenance = determine_provenance("Bearer tr-token", "custom_source", caller_context="authenticated_public")
        assert provenance["trust_level"] == TRUST_TRUSTED_READER
        assert provenance["trust_verified"] is True
        assert provenance["trust_verification_method"] == "jwt_trusted_reader_profile"
        assert provenance["is_trusted_reader"] is True
        assert provenance["source"] == "custom_source"


def test_system_cron_provenance():
    # 6. Internal system function -> system provenance
    provenance = get_system_provenance()
    assert provenance["trust_level"] == TRUST_SYSTEM
    assert provenance["trust_verified"] is True
    assert provenance["trust_verification_method"] == "internal_backend_cron"
    assert provenance["source_verified"] is True
    assert provenance["source"] == "system_detected_failure"


def test_builder_rejects_unverified_elevated_feedback():
    # 9. Builder receives source=author_feedback but trust_verified=false -> anonymous & observing
    feedbacks = [
        {
            "id": "fb1",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "source": "author_feedback",
            "trust_level": "author",
            "is_author": True,
            "trust_verified": False,  # Spoofed / Unverified
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
         # Demoted to anonymous
         assert called_payload["trust_level"] == TRUST_ANONYMOUS
         assert called_payload["promotion_score"] == 0.2
         assert called_payload["promotion_status"] == "observing"
         # Evidence entry records unverified metadata claim
         assert called_payload["evidence"]["feedbacks"][0]["unverified_elevated_metadata_claim"] is True


def test_builder_accepts_verified_elevated_feedback():
    # 10. Builder receives verified author provenance -> auto_promote_ready
    feedbacks = [
        {
            "id": "fb1",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "source": "author_feedback",
            "trust_level": "author",
            "is_author": True,
            "trust_verified": True,
            "trust_verification_method": "jwt_author_profile",
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
         # Authenticated author verified
         assert called_payload["trust_level"] == TRUST_AUTHOR
         assert called_payload["promotion_score"] == 1.0
         assert called_payload["promotion_status"] == "auto_promote_ready"
         assert called_payload["evidence"]["feedbacks"][0]["unverified_elevated_metadata_claim"] is False


def test_builder_rejects_existing_unverified_feedbacks():
    # 11. Existing feedbacks without provenance -> anonymous
    feedbacks = [
        {
            "id": "fb1",
            "question": "Chiến dịch Lệ Giang là gì?",
            "chapter_progress": 829,
            "feedback_type": "wrong",
            "source": "author_feedback",
            "trust_level": "author",
            "is_author": True,
            # trust_verified field is missing completely (legacy feedback rows)
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
         assert called_payload["trust_level"] == TRUST_ANONYMOUS
         assert called_payload["promotion_status"] == "observing"
         assert called_payload["evidence"]["feedbacks"][0]["unverified_elevated_metadata_claim"] is True


# --- Restored/Hardened Security, RLS & Route Payload Tests for Phase 11E-SEC2-FIX1 ---

def test_rls_sql_migration_contains_all_10_constraints():
    # Verify statically that the SQL migration file contains all 10 security constraints
    sql_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sql", "harden_rag_feedback_trust_provenance.sql")
    assert os.path.exists(sql_path)
    with open(sql_path, "r", encoding="utf-8") as f:
        content = f.read()

    # The exact name of the policy
    assert "feedback_anonymous_insert" in content

    # Check 10 RLS constraints
    assert "trust_level IS NULL OR trust_level = 'anonymous'" in content
    assert "trust_verified IS NULL OR trust_verified = false" in content
    assert "source_verified IS NULL OR source_verified = false" in content
    assert "is_author IS NULL OR is_author = false" in content
    assert "is_trusted_reader IS NULL OR is_trusted_reader = false" in content
    assert "status IS NULL OR status = 'pending'" in content
    assert "source IS NULL OR source = 'anonymous_feedback'" in content
    assert "trust_verification_method IS NULL" in content
    assert "trust_verified_at IS NULL" in content
    assert "trust_subject_user_id IS NULL" in content


def test_anonymous_payload_spoofed_fields_ignored_in_route():
    # 2, 3, 4. Send anonymous feedback payload with spoofed fields directly to route
    payload = {
        "question": "Hàn Phong là ai?",
        "answer": "Hàn Phong...",
        "source": "author_feedback",
        "citations": [],
        "chapter_progress": 1,
        "feedback_type": "wrong",
        "user_comment": "Spoofed attempt",
        # Extra fields that are not in Pydantic schema or must not be accepted
        "trust_verification_method": "jwt_author_profile",
        "trust_subject_user_id": "00000000-0000-0000-0000-000000000000",
        "trust_verified_at": "2026-06-13T07:50:20Z",
        "trust_verified": True,
        "is_author": True,
        "is_trusted_reader": True
    }

    mock_supabase = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = [{"id": "fb-uuid-123"}]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_resp

    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase):

         # Mock auth to return no user (anonymous)
         mock_supabase.auth.get_user.side_effect = Exception("No auth header")

         response = client.post("/oracle/feedback", json=payload)
         assert response.status_code == 200

         # Verify inserted payload
         called_insert = mock_supabase.table.return_value.insert.call_args[0][0]
         # The extra fields must be stripped/ignored/sanitized by FastAPI route
         assert called_insert["source"] == "anonymous_feedback"
         assert called_insert["trust_level"] == "anonymous"
         assert called_insert["trust_verified"] is False
         assert called_insert["trust_verification_method"] == "none"
         assert called_insert["trust_verified_at"] is None
         assert called_insert["trust_subject_user_id"] is None
         assert called_insert["is_author"] is False
         assert called_insert["is_trusted_reader"] is False


def test_internal_system_source_requires_valid_provenance():
    # 7. Internal system source is only valid when verified provenance says so
    mock_supabase = MagicMock()
    mock_user = MagicMock()
    mock_user.user.id = "system-user-id"
    mock_user.user.email = "system@system.local"
    mock_supabase.auth.get_user.return_value = mock_user

    # Mock user profile as standard reader role
    mock_profile_resp = MagicMock()
    mock_profile_resp.data = [{"role": "reader"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_profile_resp

    # Attempt to determine provenance with standard JWT but claiming system source
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase):
         provenance = determine_provenance("Bearer reader-token", "system_detected_failure", caller_context="internal_system")
         # Because they are not system role or backend script, trust level remains reader
         # and the source is demoted/not verified as system source
         assert provenance["trust_level"] == "reader"
         assert provenance["source"] == "system_detected_failure"
         assert provenance["source_verified"] is True  # standard reader feedback source is verified as reader, but not system level

         # Now test system cron provenance explicitly
         system_prov = get_system_provenance()
         assert system_prov["trust_level"] == "system"
         assert system_prov["source_verified"] is True
         assert system_prov["trust_verification_method"] == "internal_backend_cron"
         assert system_prov["source"] == "system_detected_failure"


def test_privileged_fields_not_in_request_body_model():
    # 9. Ensure the Pydantic request model OracleFeedbackRequest does not expose privileged fields
    from backend.routes.ai_oracle import OracleFeedbackRequest
    fields = OracleFeedbackRequest.model_fields
    assert "trust_level" not in fields
    assert "trust_verified" not in fields
    assert "trust_verification_method" not in fields
    assert "trust_verified_at" not in fields
    assert "trust_subject_user_id" not in fields
    assert "source_verified" not in fields
    assert "is_author" not in fields
    assert "is_trusted_reader" not in fields


# --- Phase 11E-3: Verified Provenance Autonomous Promotion Canary Tests ---

from backend.scripts.create_verified_golden_canary import main as canary_builder_main

def test_canary_public_payload_fails_to_create_system_canary_provenance():
    # 1. public payload không tạo system_canary provenance.
    provenance = determine_provenance(None, "system_canary", caller_context="public")
    assert provenance["source"] == "anonymous_feedback"
    assert provenance["trust_level"] == "anonymous"

def test_create_canary_dry_run_no_db_write():
    # 2. create canary dry-run không ghi DB.
    mock_supabase = MagicMock()
    mock_response = MockResponse({"answer": "Safe answer: chiến dịch thanh tẩy Thể Thôn Phệ Lệ Giang."}, 200)
    with patch("backend.scripts.create_verified_golden_canary.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["create_verified_golden_canary.py", "--dry-run", "--json"]):
         try:
             canary_builder_main()
         except SystemExit as e:
             assert e.code == 0
         mock_supabase.table.assert_not_called()

def test_canary_write_idempotent():
    # 3. canary write idempotent.
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"candidate_key": "canary_verified_le_giang_campaign"}]
    mock_response = MockResponse({"answer": "Safe answer: chiến dịch thanh tẩy Thể Thôn Phệ Lệ Giang."}, 200)
    with patch("backend.scripts.create_verified_golden_canary.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["create_verified_golden_canary.py", "--write", "--json"]):
         try:
             canary_builder_main()
         except SystemExit as e:
             assert e.code == 0
         mock_supabase.table.assert_any_call("oracle_golden_regression_candidates")
         mock_supabase.table.return_value.update.assert_called()

def test_canary_pre_validation_requires_3_of_3_pass():
    # 4. pre-validation cần 3/3 PASS.
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    mock_response = MockResponse({"answer": "Safe answer: chiến dịch thanh tẩy Thể Thôn Phệ Lệ Giang."}, 200)
    with patch("backend.scripts.create_verified_golden_canary.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["create_verified_golden_canary.py", "--write", "--json"]):
         try:
             canary_builder_main()
         except SystemExit as e:
             assert e.code == 0
         called_args = mock_supabase.table.return_value.insert.call_args[0][0]
         assert called_args["promotion_status"] == "auto_promote_ready"

def test_canary_pre_validation_fails_on_2_of_3_pass():
    # 5. 2/3 PASS không được promote (status canary_validation_failed).
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    resp1 = MockResponse({"answer": "Safe answer: chiến dịch thanh tẩy Thể Thôn Phệ Lệ Giang."}, 200)
    resp2 = MockResponse({"answer": "Contains [DỮ LIỆU HỆ THỐNG] which is forbidden"}, 200)

    with patch("backend.scripts.create_verified_golden_canary.supabase", mock_supabase), \
         patch("urllib.request.urlopen", side_effect=[resp1, resp2]), \
         patch("sys.argv", ["create_verified_golden_canary.py", "--write", "--json"]), \
         pytest.raises(SystemExit) as excinfo:
         canary_builder_main()
    assert excinfo.value.code == 1
    called_args = mock_supabase.table.return_value.insert.call_args[0][0]
    assert called_args["promotion_status"] == "canary_validation_failed"

def test_only_one_canary_planned():
    # 6. chỉ một canary được planned.
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    mock_response = MockResponse({"answer": "Safe answer: chiến dịch thanh tẩy Thể Thôn Phệ Lệ Giang."}, 200)
    with patch("backend.scripts.create_verified_golden_canary.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["create_verified_golden_canary.py", "--dry-run", "--json"]):
         try:
             canary_builder_main()
         except SystemExit as e:
             assert e.code == 0

def test_anonymous_candidates_not_promoted_with_canary():
    # 7. anonymous candidates không được promote cùng canary.
    candidates = [
        {
            "id": "cand1",
            "candidate_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "trust_level": "system",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "chapter_progress": 829,
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "promotion_status": "auto_promote_ready",
            "promotion_score": 1.0,
            "feedback_ids": []
        },
        {
            "id": "cand2",
            "candidate_key": "anonymous_bug_1",
            "source": "anonymous_feedback",
            "trust_level": "anonymous",
            "question": "What is hope town?",
            "chapter_progress": 10,
            "must_not_contain": ["hope town"],
            "promotion_status": "observing",
            "promotion_score": 0.2,
            "feedback_ids": ["fb2"]
        }
    ]
    mock_supabase = MockSupabase(candidates=candidates)
    mock_response = MockResponse({"answer": "Safe answer: chiến dịch Lệ Giang"}, 200)
    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["promote_golden_candidates.py", "--write", "--json"]):
         promoter_main()

    assert any(x.get("case_key") == "canary_verified_le_giang_campaign" for x in mock_supabase.upserted_cases)
    assert not any(x.get("case_key") == "anonymous_bug_1" for x in mock_supabase.upserted_cases)

def test_canary_promotion_requires_runtime_validation_passed():
    # 8. promotion cần runtime_validation_passed.
    candidates = [
        {
            "id": "cand1",
            "candidate_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "trust_level": "system",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "chapter_progress": 829,
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "promotion_status": "auto_promote_ready",
            "promotion_score": 1.0,
            "feedback_ids": []
        }
    ]
    mock_supabase = MockSupabase(candidates=candidates)
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)
    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["promote_golden_candidates.py", "--write", "--json"]):
         promoter_main()

    assert not any(x.get("case_key") == "canary_verified_le_giang_campaign" for x in mock_supabase.upserted_cases)
    assert any(x.get("promotion_status") == "canary_validation_failed" for x in mock_supabase.updated_candidates)

def test_runtime_failure_reproduced_alone_not_enough_for_canary_promotion():
    # 9. runtime_failure_reproduced một mình không đủ promote.
    candidates = [
        {
            "id": "cand1",
            "candidate_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "trust_level": "system",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "chapter_progress": 829,
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "promotion_status": "auto_promote_ready",
            "promotion_score": 1.0,
            "feedback_ids": []
        }
    ]
    mock_supabase = MockSupabase(candidates=candidates)
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)
    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["promote_golden_candidates.py", "--write", "--json"]):
         promoter_main()

    assert not any(x.get("case_key") == "canary_verified_le_giang_campaign" for x in mock_supabase.upserted_cases)

def test_active_golden_insert_has_correct_payload():
    # 10. active golden insert đúng payload.
    candidates = [
        {
            "id": "cand1",
            "candidate_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "trust_level": "system",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "chapter_progress": 829,
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "promotion_status": "auto_promote_ready",
            "promotion_score": 1.0,
            "feedback_ids": []
        }
    ]
    mock_supabase = MockSupabase(candidates=candidates)
    mock_response = MockResponse({"answer": "Safe answer: chiến dịch Lệ Giang"}, 200)
    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["promote_golden_candidates.py", "--write", "--json"]):
         promoter_main()

    inserted_case = mock_supabase.upserted_cases[0]
    assert inserted_case["case_key"] == "canary_verified_le_giang_campaign"
    assert inserted_case["status"] == "active"
    assert inserted_case["source"] == "system_canary"

def test_post_promotion_runner_failure_disables_case():
    # 11. post-promotion runner fail sẽ disable case.
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "candidate_key": "canary_verified_le_giang_campaign",
            "promotion_status": "auto_promoted",
            "trust_level": "system",
            "source": "system_canary",
            "evidence": {
                "trust_verification": {
                    "trust_verified": True,
                    "source_verified": True,
                    "trust_verification_method": "internal_backend_canary"
                }
            }
        }
    ]

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--rollback-mode", "verified-canary"]), \
         pytest.raises(SystemExit) as excinfo:
         run_regression()

    assert excinfo.value.code == 1
    mock_query_cases.update.assert_any_call({"status": "disabled"})

def test_rollback_does_not_delete_audit_trail():
    # 12. rollback không delete audit trail.
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "candidate_key": "canary_verified_le_giang_campaign",
            "promotion_status": "auto_promoted",
            "trust_level": "system",
            "source": "system_canary",
            "evidence": {
                "trust_verification": {
                    "trust_verified": True,
                    "source_verified": True,
                    "trust_verification_method": "internal_backend_canary"
                }
            }
        }
    ]

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--rollback-mode", "verified-canary"]), \
         pytest.raises(SystemExit):
         run_regression()

    for call in mock_query_cases.mock_calls:
        assert "delete" not in str(call)
    for call in mock_query_candidates.mock_calls:
        assert "delete" not in str(call)

def test_successful_3_run_canary_remains_active():
    # 13. successful 3-run canary giữ active.
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "candidate_key": "canary_verified_le_giang_campaign",
            "promotion_status": "auto_promoted",
            "trust_level": "system",
            "source": "system_canary",
            "evidence": {
                "trust_verification": {
                    "trust_verified": True,
                    "source_verified": True,
                    "trust_verification_method": "internal_backend_canary"
                }
            }
        }
    ]

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Safe answer: chiến dịch Lệ Giang"}, 200)
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--rollback-mode", "verified-canary"]):
         try:
             run_regression()
         except SystemExit as e:
             assert e.code == 0

    for call in mock_query_cases.update.mock_calls:
        assert "disabled" not in str(call)

def test_no_wiki_provisional_or_feedback_modified():
    # 14. không sửa wiki/provisional/rag_feedback.
    mock_supabase = MagicMock()
    mock_response = MockResponse({"answer": "Safe answer"}, 200)

    mock_res = MagicMock()
    mock_res.data = []
    mock_res.count = 0
    mock_supabase.table.return_value.select.return_value.execute.return_value = mock_res

    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["promote_golden_candidates.py", "--write"]):
         promoter_main()

    for call in mock_supabase.table.mock_calls:
        call_str = str(call)
        if any(table in call_str for table in ["wiki_entries", "provisional_library", "rag_feedback"]):
            assert "insert" not in call_str
            assert "update" not in call_str
            assert "delete" not in call_str
            assert "upsert" not in call_str

# --- Phase 11E-3-FIX1: 19 Mandatory Test Cases ---

def test_fix1_1_dry_run_empty_db_yields_zero_promotions():
    # 1. dry-run DB rỗng → planned_promotions=0
    backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mock_supabase = MagicMock()
    mock_res = MagicMock()
    mock_res.data = []
    mock_res.count = 0
    mock_supabase.table.return_value.select.return_value.execute.return_value = mock_res
    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("sys.argv", ["promote_golden_candidates.py", "--dry-run", "--json"]):
         try:
             promoter_main()
         except SystemExit as e:
             assert e.code == 0

    report_path = os.path.join(backend_root, "rag", "generated_feedback_to_golden_promotion_report.json")
    with open(report_path, "r", encoding="utf-8") as f:
        rep = json.load(f)
    assert rep["planned_promotions"] == 0

def test_fix1_2_dry_run_no_synthetic_candidate():
    # 2. dry-run không append synthetic candidate
    backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mock_supabase = MagicMock()
    mock_res = MagicMock()
    mock_res.data = []
    mock_res.count = 0
    mock_supabase.table.return_value.select.return_value.execute.return_value = mock_res
    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("sys.argv", ["promote_golden_candidates.py", "--dry-run", "--json"]):
         try:
             promoter_main()
         except SystemExit as e:
             assert e.code == 0

    report_path = os.path.join(backend_root, "rag", "generated_feedback_to_golden_promotion_report.json")
    with open(report_path, "r", encoding="utf-8") as f:
        rep = json.load(f)
    assert rep["synthetic_candidates_added"] == 0
    assert rep["candidates_built"] == 0

def test_fix1_3_mock_candidate_dependency_injection_only():
    # 3. test mock candidate phải qua dependency injection, không qua production CLI
    backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mock_supabase = MagicMock()
    mock_res = MagicMock()
    mock_res.data = []
    mock_res.count = 0
    mock_supabase.table.return_value.select.return_value.execute.return_value = mock_res
    with patch("backend.scripts.promote_golden_candidates.supabase", mock_supabase), \
         patch("sys.argv", ["promote_golden_candidates.py", "--dry-run", "--json"]):
         try:
             promoter_main()
         except SystemExit as e:
             assert e.code == 0

    report_path = os.path.join(backend_root, "rag", "generated_feedback_to_golden_promotion_report.json")
    with open(report_path, "r", encoding="utf-8") as f:
        rep = json.load(f)
    assert rep["candidate_source_count"] == 0

def test_fix1_4_semantic_fail_canary_disabled():
    # 4. semantic fail của system_canary → đúng canary bị disabled
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "candidate_key": "canary_verified_le_giang_campaign",
            "promotion_status": "auto_promoted",
            "trust_level": "system",
            "source": "system_canary",
            "evidence": {
                "trust_verification": {
                    "trust_verified": True,
                    "source_verified": True,
                    "trust_verification_method": "internal_backend_canary"
                }
            }
        }
    ]

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--rollback-mode", "verified-canary"]), \
         pytest.raises(SystemExit) as excinfo:
         run_regression()

    assert excinfo.value.code == 1
    mock_query_cases.update.assert_any_call({"status": "disabled"})

def test_fix1_5_infra_timeout_canary_not_disabled():
    # 5. infrastructure timeout của system_canary → không disable
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "candidate_key": "canary_verified_le_giang_campaign",
            "promotion_status": "auto_promoted",
            "trust_level": "system",
            "source": "system_canary",
            "evidence": {
                "trust_verification": {
                    "trust_verified": True,
                    "source_verified": True,
                    "trust_verification_method": "internal_backend_canary"
                }
            }
        }
    ]

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", side_effect=TimeoutError("Request timed out")), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--infra-retries", "0"]), \
         pytest.raises(SystemExit) as excinfo:
         run_regression()

    assert excinfo.value.code == 2
    for call in mock_query_cases.update.mock_calls:
        assert "disabled" not in str(call)

def test_fix1_6_http_503_canary_not_disabled():
    # 6. HTTP 503 của system_canary → không disable
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "candidate_key": "canary_verified_le_giang_campaign",
            "promotion_status": "auto_promoted",
            "trust_level": "system",
            "source": "system_canary",
            "evidence": {
                "trust_verification": {
                    "trust_verified": True,
                    "source_verified": True,
                    "trust_verification_method": "internal_backend_canary"
                }
            }
        }
    ]

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    import urllib.error
    err = urllib.error.HTTPError("url", 503, "Service Unavailable", {}, None)
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", side_effect=err), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--infra-retries", "0"]), \
         pytest.raises(SystemExit) as excinfo:
         run_regression()

    assert excinfo.value.code == 2
    for call in mock_query_cases.update.mock_calls:
        assert "disabled" not in str(call)

def test_fix1_7_config_failure_not_disabled():
    # 7. configuration failure → không disable
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("DB connection error")
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db"]), \
         pytest.raises(SystemExit) as excinfo:
         run_regression()

    assert excinfo.value.code == 3

def test_fix1_8_semantic_fail_manual_regression_not_disabled():
    # 8. semantic fail của manual_regression → không disable
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "manual_case_1",
            "source": "manual_regression",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = []

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db"]), \
         pytest.raises(SystemExit) as excinfo:
         run_regression()

    assert excinfo.value.code == 1
    for call in mock_query_cases.update.mock_calls:
        assert "disabled" not in str(call)

def test_fix1_9_semantic_fail_original_case_not_disabled():
    # 9. semantic fail của original Lệ Giang case → không auto-disable
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "le_giang_campaign_location_pollution",
            "source": "manual_regression",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = []

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db"]), \
         pytest.raises(SystemExit) as excinfo:
         run_regression()

    assert excinfo.value.code == 1
    for call in mock_query_cases.update.mock_calls:
        assert "disabled" not in str(call)

def test_fix1_10_rollback_updates_using_exact_case_key():
    # 10. rollback update dùng exact case_key
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "candidate_key": "canary_verified_le_giang_campaign",
            "promotion_status": "auto_promoted",
            "trust_level": "system",
            "source": "system_canary",
            "evidence": {
                "trust_verification": {
                    "trust_verified": True,
                    "source_verified": True,
                    "trust_verification_method": "internal_backend_canary"
                }
            }
        }
    ]

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--rollback-mode", "verified-canary"]), \
         pytest.raises(SystemExit):
         run_regression()

    mock_query_cases.update.return_value.eq.assert_any_call("case_key", "canary_verified_le_giang_campaign")
    mock_query_candidates.update.return_value.eq.assert_any_call("candidate_key", "canary_verified_le_giang_campaign")

def test_fix1_11_linked_candidate_status_rolled_back():
    # 11. linked candidate duy nhất thành canary_rolled_back
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "candidate_key": "canary_verified_le_giang_campaign",
            "promotion_status": "auto_promoted",
            "trust_level": "system",
            "source": "system_canary",
            "evidence": {
                "trust_verification": {
                    "trust_verified": True,
                    "source_verified": True,
                    "trust_verification_method": "internal_backend_canary"
                }
            }
        }
    ]

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--rollback-mode", "verified-canary"]), \
         pytest.raises(SystemExit):
         run_regression()

    update_calls = mock_query_candidates.update.call_args_list
    candidate_updated = False
    for c in update_calls:
        payload = c[0][0]
        if payload.get("promotion_status") == "canary_rolled_back":
            candidate_updated = True
    assert candidate_updated is True

def test_fix1_12_rollback_no_deletion():
    # 12. rollback không delete case/candidate
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "candidate_key": "canary_verified_le_giang_campaign",
            "promotion_status": "auto_promoted",
            "trust_level": "system",
            "source": "system_canary",
            "evidence": {
                "trust_verification": {
                    "trust_verified": True,
                    "source_verified": True,
                    "trust_verification_method": "internal_backend_canary"
                }
            }
        }
    ]

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--rollback-mode", "verified-canary"]), \
         pytest.raises(SystemExit):
         run_regression()

    for call in mock_query_cases.mock_calls:
        assert "delete" not in str(call)
    for call in mock_query_candidates.mock_calls:
        assert "delete" not in str(call)

def test_fix1_13_remaining_active_cases_rerun():
    # 13. remaining active cases được rerun
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()
    cases_calls = []

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            cases_calls.append(True)
            if len(cases_calls) == 1:
                mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
                    {
                        "case_key": "canary_verified_le_giang_campaign",
                        "source": "system_canary",
                        "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
                        "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
                        "status": "active"
                    },
                    {
                        "case_key": "manual_case_1",
                        "source": "manual_regression",
                        "question": "Ai là Lâm Phong?",
                        "must_not_contain": [],
                        "status": "active"
                    }
                ]
            else:
                mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
                    {
                        "case_key": "manual_case_1",
                        "source": "manual_regression",
                        "question": "Ai là Lâm Phong?",
                        "must_not_contain": [],
                        "status": "active"
                    }
                ]
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
                {
                    "candidate_key": "canary_verified_le_giang_campaign",
                    "promotion_status": "auto_promoted",
                    "trust_level": "system",
                    "source": "system_canary",
                    "evidence": {
                        "trust_verification": {
                            "trust_verified": True,
                            "source_verified": True,
                            "trust_verification_method": "internal_backend_canary"
                        }
                    }
                }
            ]
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    requested_questions = []

    def mock_urlopen(req, *args, **kwargs):
        body = json.loads(req.data.decode("utf-8"))
        requested_questions.append(body["question"])
        return MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG] for Lệ Giang, Lâm Phong is safe"}, 200)

    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", side_effect=mock_urlopen), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--rollback-mode", "verified-canary"]), \
         pytest.raises(SystemExit) as excinfo:
         run_regression()

    assert excinfo.value.code == 1
    assert "Hãy kể lại diễn biến của chiến dịch Lệ Giang." in requested_questions
    assert "Ai là Lâm Phong?" in requested_questions

def test_fix1_14_public_author_feedback_no_author_trust():
    # 14. public source=author_feedback không được author trust
    provenance = determine_provenance(None, "author_feedback", caller_context="public")
    assert provenance["source"] == "anonymous_feedback"
    assert provenance["trust_level"] == "anonymous"

def test_fix1_15_public_system_detected_failure_no_system_trust():
    # 15. public source=system_detected_failure không được system trust
    provenance = determine_provenance(None, "system_detected_failure", caller_context="public")
    assert provenance["source"] == "anonymous_feedback"
    assert provenance["trust_level"] == "anonymous"

def test_fix1_16_public_system_canary_no_system_trust():
    # 16. public source=system_canary không được system trust
    provenance = determine_provenance(None, "system_canary", caller_context="public")
    assert provenance["source"] == "anonymous_feedback"
    assert provenance["trust_level"] == "anonymous"

def test_fix1_17_internal_authenticated_canary_valid():
    # 17. internal authenticated canary path vẫn hợp lệ
    provenance = determine_provenance(None, "system_canary", caller_context="internal_canary")
    assert provenance["source"] == "system_canary"

def test_fix1_18_report_separates_rollback_reasons():
    # 18. report phân biệt rollback_performed và rollback_skipped_reason
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()
    backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "manual_case_1",
            "source": "manual_regression",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = []

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--write-report", "--rollback-mode", "verified-canary"]), \
         pytest.raises(SystemExit):
         run_regression()

    report_path = os.path.join(backend_root, "rag", "generated_golden_oracle_regression_report.json")
    with open(report_path, "r", encoding="utf-8") as f:
        rep = json.load(f)
    summary = rep["summary"]
    assert "rollback_performed" in summary
    assert "rollback_skipped_reasons" in summary
    assert summary["rollback_performed"] is False
    assert "manual_case_1" in summary["rollback_skipped_reasons"]

def test_fix1_19_no_wiki_provisional_or_feedback_mutation_on_run():
    # 19. verify no wiki/provisional/rag_feedback mutation on regression run
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()

    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "candidate_key": "canary_verified_le_giang_campaign",
            "promotion_status": "auto_promoted",
            "trust_level": "system",
            "source": "system_canary",
            "evidence": {
                "trust_verification": {
                    "trust_verified": True,
                    "source_verified": True,
                    "trust_verification_method": "internal_backend_canary"
                }
            }
        }
    ]

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)
    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--rollback-mode", "verified-canary"]), \
         pytest.raises(SystemExit):
         run_regression()

    for call in mock_supabase.table.mock_calls:
        call_str = str(call)
        if any(table in call_str for table in ["wiki_entries", "provisional_library", "rag_feedback"]):
            assert "insert" not in call_str
            assert "update" not in call_str
            assert "delete" not in call_str
            assert "upsert" not in call_str

# --- Phase 11E-4: Dual-Source Golden Regression Gate & Explicit Rollback Mode Tests ---

def test_11e4_caller_context_omitted_raises_type_error():
    # 1. omitted caller_context bị reject (raises TypeError)
    with pytest.raises(TypeError):
        determine_provenance(None, "system_canary")

def test_11e4_unknown_caller_context_fail_closed():
    # 2. unknown caller_context bị reject/fail-closed
    provenance = determine_provenance(None, "system_canary", caller_context="invalid_context")
    assert provenance["trust_level"] == "anonymous"
    assert provenance["source"] == "anonymous_feedback"

def test_11e4_public_cannot_create_system_canary():
    # 3. public không tạo system_canary
    provenance = determine_provenance(None, "system_canary", caller_context="public")
    assert provenance["source"] == "anonymous_feedback"

def test_11e4_public_cannot_create_system_detected_failure():
    # 4. public không tạo system_detected_failure
    provenance = determine_provenance(None, "system_detected_failure", caller_context="public")
    assert provenance["source"] == "anonymous_feedback"

def test_11e4_public_cannot_create_author_feedback_via_string():
    # 5. public không tạo author_feedback bằng source string
    provenance = determine_provenance(None, "author_feedback", caller_context="public")
    assert provenance["source"] == "anonymous_feedback"

def test_11e4_internal_canary_is_valid():
    # 6. internal canary vẫn hợp lệ
    provenance = determine_provenance(None, "system_canary", caller_context="internal_canary")
    assert provenance["source"] == "system_canary"

def test_11e4_internal_system_is_valid():
    # 7. internal system vẫn hợp lệ
    provenance = determine_provenance(None, "system_detected_failure", caller_context="internal_system")
    assert provenance["source"] == "system_detected_failure"

# Explicit Rollback Mode Tests
def test_11e4_rollback_mode_off_does_not_mutate():
    # 1. source=db + semantic canary fail + rollback-mode=off -> không disable
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()
    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "candidate_key": "canary_verified_le_giang_campaign",
            "promotion_status": "auto_promoted",
            "trust_level": "system",
            "source": "system_canary",
            "evidence": {
                "trust_verification": {
                    "trust_verified": True,
                    "source_verified": True,
                    "trust_verification_method": "internal_backend_canary"
                }
            }
        }
    ]

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)

    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--rollback-mode", "off"]), \
         pytest.raises(SystemExit) as excinfo:
         run_regression()

    assert excinfo.value.code == 1
    mock_query_cases.update.assert_not_called()
    mock_query_candidates.update.assert_not_called()

def test_11e4_rollback_mode_verified_canary_performs_rollback():
    # 2. source=db + semantic canary fail + verified-canary -> rollback đúng case
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()
    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "candidate_key": "canary_verified_le_giang_campaign",
            "promotion_status": "auto_promoted",
            "trust_level": "system",
            "source": "system_canary",
            "evidence": {
                "trust_verification": {
                    "trust_verified": True,
                    "source_verified": True,
                    "trust_verification_method": "internal_backend_canary"
                }
            }
        }
    ]

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)

    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--rollback-mode", "verified-canary"]), \
         pytest.raises(SystemExit) as excinfo:
         run_regression()

    assert excinfo.value.code == 1
    mock_query_cases.update.assert_any_call({"status": "disabled"})
    mock_query_candidates.update.assert_any_call({
        "promotion_status": "canary_rolled_back",
        "promotion_reason": "Rollback: Regression failed. Reason: Answer contains forbidden term: \'[DỮ LIỆU HỆ THỐNG]\'"
    })

def test_11e4_infra_failure_no_rollback_in_any_mode():
    # 3. infra fail + verified-canary -> không rollback
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()
    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "canary_verified_le_giang_campaign",
            "source": "system_canary",
            "question": "Hãy kể lại diễn biến của chiến dịch Lệ Giang.",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "candidate_key": "canary_verified_le_giang_campaign",
            "promotion_status": "auto_promoted",
            "trust_level": "system",
            "source": "system_canary",
            "evidence": {
                "trust_verification": {
                    "trust_verified": True,
                    "source_verified": True,
                    "trust_verification_method": "internal_backend_canary"
                }
            }
        }
    ]

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    from urllib.error import URLError
    mock_err = URLError("timed out")

    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", side_effect=mock_err), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--rollback-mode", "verified-canary", "--infra-backoff-seconds", "0"]), \
         pytest.raises(SystemExit) as excinfo:
         run_regression()

    assert excinfo.value.code == 2
    mock_query_cases.update.assert_not_called()
    mock_query_candidates.update.assert_not_called()

def test_11e4_original_case_fail_no_rollback():
    # 4. original case fail + verified-canary -> không rollback
    from backend.scripts.run_golden_oracle_regression_cases import run_regression
    mock_supabase = MagicMock()
    mock_query_cases = MagicMock()
    mock_query_candidates = MagicMock()

    mock_query_cases.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "case_key": "le_giang_campaign_location_pollution",
            "source": "manual_regression",
            "question": "chiến dịch lệ giang diễn ra như thế nào?",
            "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
            "status": "active"
        }
    ]
    mock_query_candidates.select.return_value.eq.return_value.execute.return_value.data = []

    def mock_table(table_name):
        if table_name == "oracle_golden_regression_cases":
            return mock_query_cases
        elif table_name == "oracle_golden_regression_candidates":
            return mock_query_candidates
        return MagicMock()

    mock_supabase.table.side_effect = mock_table
    mock_response = MockResponse({"answer": "Violating [DỮ LIỆU HỆ THỐNG]"}, 200)

    with patch("backend.main.supabase", mock_supabase), \
         patch("main.supabase", mock_supabase), \
         patch("urllib.request.urlopen", return_value=mock_response), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "https://mat-the-website.onrender.com", "--source", "db", "--rollback-mode", "verified-canary"]), \
         pytest.raises(SystemExit) as excinfo:
         run_regression()

    assert excinfo.value.code == 1
    mock_query_cases.update.assert_not_called()
    mock_query_candidates.update.assert_not_called()
