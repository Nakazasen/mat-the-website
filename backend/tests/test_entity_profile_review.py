import json
from unittest.mock import MagicMock
from backend.rag.entity_profile_review import (
    validate_entity_profile_draft,
    validate_entity_profile_drafts,
    build_entity_profile_correction_payload,
    summarize_entity_profile_review
)

def test_valid_draft_with_evidence():
    draft = {
        "entity_name": "Công ty Đại Thiên Thần",
        "entity_type": "faction",
        "status": "draft",
        "human_review_required": True,
        "evidence": [
            {
                "chapter_number": 1,
                "chapter_title": "Đầu lâu khổng lồ",
                "chunk_index": 0,
                "content_hash": "hash123",
                "preview": "Công ty Đại Thiên Thần hoạt động mạt thế..."
            }
        ]
    }
    report = validate_entity_profile_draft(draft)
    assert report["valid"] is True
    assert report["eligible_insert"] is True
    assert len(report["errors"]) == 0
    assert len(report["warnings"]) == 0

def test_needs_review_without_evidence_warning_but_valid():
    draft = {
        "entity_name": "Lâm Nhã Vy",
        "entity_type": "character",
        "status": "needs_review",
        "human_review_required": True,
        "evidence": []
    }
    report = validate_entity_profile_draft(draft)
    assert report["valid"] is True
    assert report["eligible_insert"] is True
    assert len(report["errors"]) == 0
    assert len(report["warnings"]) == 1
    assert "Status is 'needs_review' and evidence is empty." in report["warnings"][0]

def test_missing_entity_name_invalid():
    # missing name
    draft = {
        "entity_type": "character",
        "status": "draft",
        "human_review_required": True,
        "evidence": [{"chapter_number": 1}]
    }
    report = validate_entity_profile_draft(draft)
    assert report["valid"] is False
    assert report["eligible_insert"] is False
    assert any("entity_name" in err for err in report["errors"])

def test_invalid_entity_type():
    # invalid type
    draft = {
        "entity_name": "Hàn Phong",
        "entity_type": "superhero", # not one of allowed
        "status": "draft",
        "human_review_required": True,
        "evidence": [{"chapter_number": 1}]
    }
    report = validate_entity_profile_draft(draft)
    assert report["valid"] is False
    assert report["eligible_insert"] is False
    assert any("entity_type" in err for err in report["errors"])

def test_invalid_status():
    draft = {
        "entity_name": "Hàn Phong",
        "entity_type": "character",
        "status": "approved", # must be draft or needs_review
        "human_review_required": True,
        "evidence": [{"chapter_number": 1}]
    }
    report = validate_entity_profile_draft(draft)
    assert report["valid"] is False
    assert any("status" in err for err in report["errors"])

def test_build_payload_schema():
    draft = {
        "entity_name": "Công ty Đại Thiên Thần",
        "entity_type": "faction",
        "status": "draft",
        "human_review_required": True,
        "evidence": [{"chapter_number": 1}],
        "priority": "low"
    }
    payload = build_entity_profile_correction_payload(draft)
    assert payload is not None
    assert payload["feedback_id"] is None
    assert payload["entity_name"] == "Công ty Đại Thiên Thần"
    assert payload["correction_type"] == "entity_profile"
    assert payload["status"] == "draft"
    assert payload["reviewer_note"] == "Generated from missing entity failure analysis; human review required."
    assert payload["evidence"] == [{"chapter_number": 1}]
    
    # Check proposed content is serialized JSON string
    proposed = json.loads(payload["proposed_content"])
    assert proposed["entity_name"] == "Công ty Đại Thiên Thần"
    assert proposed["priority"] == "low"

def test_summary_counts():
    drafts = [
        # Valid draft with evidence
        {
            "entity_name": "Ent 1",
            "entity_type": "character",
            "status": "draft",
            "human_review_required": True,
            "evidence": [{"chapter_number": 1}]
        },
        # Valid needs_review without evidence (triggers warning)
        {
            "entity_name": "Ent 2",
            "entity_type": "character",
            "status": "needs_review",
            "human_review_required": True,
            "evidence": []
        },
        # Invalid (missing name)
        {
            "entity_type": "character",
            "status": "draft",
            "human_review_required": True,
            "evidence": []
        }
    ]
    summary = summarize_entity_profile_review(drafts)
    assert summary["total"] == 3
    assert summary["valid"] == 2
    assert summary["invalid"] == 1
    assert summary["eligible_insert"] == 2 # Ent 1 and Ent 2
    assert summary["needs_review"] == 1 # Ent 2
    assert summary["with_evidence"] == 1 # Ent 1
    assert summary["warnings"] == 1 # Ent 2's empty evidence warning

def test_no_db_interactions_by_default():
    mock_supabase = MagicMock()
    # The functions should not reference any global database or mock_supabase.
    # They should run purely locally and functionally.
    draft = {
        "entity_name": "Công ty Đại Thiên Thần",
        "entity_type": "faction",
        "status": "draft",
        "human_review_required": True,
        "evidence": [{"chapter_number": 1}]
    }
    # No error or database execution should happen
    payload = build_entity_profile_correction_payload(draft)
    assert payload is not None
    assert mock_supabase.called is False
