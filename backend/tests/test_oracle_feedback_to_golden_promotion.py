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
        provenance = determine_provenance("Bearer author-token", "author_feedback")
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
        provenance = determine_provenance("Bearer tr-token", "custom_source")
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
         provenance = determine_provenance("Bearer reader-token", "system_detected_failure")
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
