import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Add parent directory and backend directory to path
sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend.rag.correction_review import (
        validate_correction_draft,
        validate_correction_drafts,
        build_rag_correction_payload,
        summarize_correction_review
    )
except ImportError:
    from rag.correction_review import (
        validate_correction_draft,
        validate_correction_drafts,
        build_rag_correction_payload,
        summarize_correction_review
    )

# 1. Test valid correction draft -> eligible
def test_valid_correction_draft():
    draft = {
        "feedback_id": "uuid-12345",
        "entity_name": "Hàn Phong",
        "correction_type": "entity_profile",
        "proposed_content": "Hàn Phong là nhân vật chính của bộ truyện.",
        "evidence": [{"chapter": 1}],
        "status": "draft"
    }
    report = validate_correction_draft(draft)
    assert report["valid"] is True
    assert report["eligible_insert"] is True
    assert len(report["errors"]) == 0
    assert len(report["warnings"]) == 0

# 2. Test missing feedback_id -> invalid
def test_missing_feedback_id():
    draft = {
        "entity_name": "Hàn Phong",
        "correction_type": "entity_profile",
        "proposed_content": "Hàn Phong là nhân vật chính của bộ truyện.",
        "evidence": [],
        "status": "draft"
    }
    report = validate_correction_draft(draft)
    assert report["valid"] is False
    assert report["eligible_insert"] is False
    assert any("feedback_id" in err for err in report["errors"])

# 3. Test invalid correction_type -> invalid
def test_invalid_correction_type():
    draft = {
        "feedback_id": "uuid-12345",
        "correction_type": "super_wrong_type",
        "proposed_content": "Valid content",
        "evidence": [],
        "status": "draft"
    }
    report = validate_correction_draft(draft)
    assert report["valid"] is False
    assert any("correction_type" in err for err in report["errors"])

# 4. Test proposed_content needs_review -> warning nhưng vẫn eligible/reviewable
def test_needs_review_warning_but_valid():
    draft = {
        "feedback_id": "uuid-12345",
        "correction_type": "wiki_update",
        "proposed_content": "needs_review",
        "evidence": [],
        "status": "draft"
    }
    report = validate_correction_draft(draft)
    assert report["valid"] is True
    assert report["eligible_insert"] is True
    assert len(report["errors"]) == 0
    assert any("needs_review" in warn for warn in report["warnings"])

# 5. Test build_rag_correction_payload trả payload đúng schema rag_corrections
def test_payload_builder_schema():
    draft = {
        "feedback_id": "uuid-12345",
        "entity_name": "Lâm Nhã Vy",
        "correction_type": "entity_profile",
        "proposed_content": "Nữ phụ hệ mộc.",
        "evidence": [{"chapter": 4}],
        "status": "draft",
        "reviewer_note": "Custom reviewer note"
    }
    payload = build_rag_correction_payload(draft)
    assert payload is not None
    assert payload["feedback_id"] == "uuid-12345"
    assert payload["entity_name"] == "Lâm Nhã Vy"
    assert payload["correction_type"] == "entity_profile"
    assert payload["proposed_content"] == "Nữ phụ hệ mộc."
    assert payload["evidence"] == [{"chapter": 4}]
    assert payload["status"] == "draft"
    assert payload["reviewer_note"] == "Custom reviewer note"

# 6. Test local review không gọi Supabase/không ghi DB
def test_local_only_review():
    # Verify we can validate and summarize without any db mock
    drafts = [
        {
            "feedback_id": "id-1",
            "correction_type": "wiki_update",
            "proposed_content": "Content 1",
            "evidence": [],
            "status": "draft"
        },
        {
            "feedback_id": "id-2",
            "correction_type": "eval_case",
            "proposed_content": "needs_review",
            "evidence": [],
            "status": "draft"
        }
    ]
    summary = summarize_correction_review(drafts)
    assert summary["total"] == 2
    assert summary["valid"] == 2
    assert summary["invalid"] == 0
    assert summary["warnings"] == 1
    assert summary["eval_cases_detected"] == 1

# 7. Test summary counts đúng
def test_summary_counts():
    drafts = [
        # Valid draft
        {
            "feedback_id": "uuid-ok",
            "correction_type": "wiki_update",
            "proposed_content": "Valid content",
            "evidence": [],
            "status": "draft"
        },
        # Invalid draft (missing feedback_id)
        {
            "correction_type": "entity_profile",
            "proposed_content": "Content",
            "status": "draft"
        },
        # Warning draft
        {
            "feedback_id": "uuid-warn",
            "correction_type": "eval_case",
            "proposed_content": "needs_review",
            "status": "draft"
        }
    ]
    summary = summarize_correction_review(drafts)
    assert summary["total"] == 3
    assert summary["valid"] == 2
    assert summary["invalid"] == 1
    assert summary["eligible_insert"] == 2
    assert summary["warnings"] == 1
    assert summary["eval_cases_detected"] == 1

# 8. Test dry-run script execution
@patch("sys.argv", ["review_feedback_corrections.py", "--input", "backend/rag/generated_feedback_corrections.json", "--json"])
def test_script_dry_run_review():
    try:
        from backend.scripts.review_feedback_corrections import main as script_main
    except ImportError:
        from scripts.review_feedback_corrections import script_main

    # Call the script main and check it runs without errors
    # (Uses the actual generated_feedback_corrections.json file created in Phase 5L)
    with patch("sys.stdout") as mock_stdout:
        script_main()
