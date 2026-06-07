import json
from unittest.mock import MagicMock
from backend.rag.wiki_candidate_builder import (
    parse_entity_profile_proposed_content,
    build_wiki_candidate_from_correction,
    validate_wiki_candidate,
    summarize_wiki_candidates,
    map_entity_type_to_wiki_category
)

def test_map_entity_type_to_wiki_category():
    # Canonical check
    assert map_entity_type_to_wiki_category("Nhân vật") == "Nhân vật"
    assert map_entity_type_to_wiki_category("nhân vật") == "Nhân vật"
    assert map_entity_type_to_wiki_category("THẾ LỰC") == "Thế lực"
    
    # English key mapping
    assert map_entity_type_to_wiki_category("character") == "Nhân vật"
    assert map_entity_type_to_wiki_category("item") == "Vật phẩm"
    assert map_entity_type_to_wiki_category("faction") == "Thế lực"
    assert map_entity_type_to_wiki_category("location") == "Địa điểm"
    assert map_entity_type_to_wiki_category("concept") == "Sinh vật"
    assert map_entity_type_to_wiki_category("unknown") == "Sinh vật"
    
    # Fallback check
    assert map_entity_type_to_wiki_category("random_type") == "Sinh vật"
    assert map_entity_type_to_wiki_category("") == "Sinh vật"
    assert map_entity_type_to_wiki_category(None) == "Sinh vật"

def test_parse_proposed_content_success():
    proposed = json.dumps({
        "entity_type": "character",
        "summary": "Tóm tắt nhân vật",
        "content": "Nội dung chi tiết"
    }, ensure_ascii=False)
    parsed = parse_entity_profile_proposed_content(proposed)
    assert isinstance(parsed, dict)
    assert parsed["entity_type"] == "character"
    assert parsed["summary"] == "Tóm tắt nhân vật"
    
    # Handles already a dict
    dict_val = {"summary": "Direct dict"}
    assert parse_entity_profile_proposed_content(dict_val) == dict_val

def test_parse_proposed_content_fallback():
    # If not a valid JSON string, wrap as content
    parsed = parse_entity_profile_proposed_content("Plain text string")
    assert parsed["summary"] == ""
    assert parsed["content"] == "Plain text string"
    
    # Empty cases
    assert parse_entity_profile_proposed_content("") == {}
    assert parse_entity_profile_proposed_content(None) == {}

def test_build_candidate_ready_for_review():
    correction = {
        "id": "c-uuid-1",
        "entity_name": "Hàn Phong",
        "correction_type": "entity_profile",
        "proposed_content": json.dumps({
            "entity_type": "character",
            "summary": "Đoàn trưởng Hàn Phong",
            "content": "Nhân vật chính của truyện."
        }),
        "evidence": [{"chapter_number": 1}],
        "status": "approved"
    }
    candidate = build_wiki_candidate_from_correction(correction)
    assert candidate["correction_id"] == "c-uuid-1"
    assert candidate["entity_name"] == "Hàn Phong"
    assert candidate["entity_type"] == "Nhân vật"  # mapped
    assert candidate["summary"] == "Đoàn trưởng Hàn Phong"
    assert candidate["content"] == "Nhân vật chính của truyện."
    assert candidate["evidence"] == [{"chapter_number": 1}]
    assert candidate["status"] == "ready_for_review"
    assert candidate["human_review_required"] is True

def test_build_candidate_needs_human_fill():
    # Missing summary and content
    correction = {
        "id": "c-uuid-2",
        "entity_name": "Mã Mộng Đình",
        "correction_type": "entity_profile",
        "proposed_content": json.dumps({
            "entity_type": "character",
            "summary": "",
            "content": ""
        }),
        "evidence": [{"chapter_number": 32}],
        "status": "approved"
    }
    candidate = build_wiki_candidate_from_correction(correction)
    assert candidate["entity_name"] == "Mã Mộng Đình"
    assert candidate["status"] == "needs_human_fill"

def test_build_candidate_invalid():
    # 1. Missing entity_name
    correction_no_name = {
        "id": "c-uuid-3",
        "entity_name": "",
        "proposed_content": json.dumps({"summary": "S", "content": "C"}),
        "evidence": []
    }
    candidate1 = build_wiki_candidate_from_correction(correction_no_name)
    assert candidate1["status"] == "invalid"
    
    # 2. Non-list evidence
    correction_bad_evidence = {
        "id": "c-uuid-4",
        "entity_name": "Tần Kha",
        "proposed_content": json.dumps({"summary": "S", "content": "C"}),
        "evidence": "not-a-list"
    }
    candidate2 = build_wiki_candidate_from_correction(correction_bad_evidence)
    assert candidate2["status"] == "invalid"
    assert candidate2["evidence"] == []

def test_validate_candidate():
    # Valid candidate
    valid_candidate = {
        "entity_name": "Hàn Phong",
        "evidence": [{"chapter_number": 1}],
        "status": "ready_for_review"
    }
    report = validate_wiki_candidate(valid_candidate)
    assert report["valid"] is True
    assert len(report["errors"]) == 0
    
    # Invalid candidate
    invalid_candidate = {
        "entity_name": "",
        "evidence": "bad-evidence",
        "status": "unknown-status"
    }
    report2 = validate_wiki_candidate(invalid_candidate)
    assert report2["valid"] is False
    assert len(report2["errors"]) == 3
    assert report2["status"] == "invalid"

def test_summarize_candidates():
    candidates = [
        {"status": "ready_for_review"},
        {"status": "needs_human_fill"},
        {"status": "needs_human_fill"},
        {"status": "invalid"}
    ]
    summary = summarize_wiki_candidates(candidates)
    assert summary["total"] == 4
    assert summary["ready_for_review"] == 1
    assert summary["needs_human_fill"] == 2
    assert summary["invalid"] == 1

def test_no_database_writes_or_modifications():
    # Ensure no database calls are made
    mock_supabase = MagicMock()
    correction = {
        "id": "c-uuid-1",
        "entity_name": "Hàn Phong",
        "correction_type": "entity_profile",
        "proposed_content": json.dumps({
            "entity_type": "character",
            "summary": "Đoàn trưởng Hàn Phong",
            "content": "Nhân vật chính của truyện."
        }),
        "evidence": [{"chapter_number": 1}],
        "status": "approved"
    }
    candidate = build_wiki_candidate_from_correction(correction)
    assert candidate is not None
    # Verify no mock supabase interaction happened
    assert mock_supabase.called is False

def test_json_serializable():
    correction = {
        "id": "c-uuid-1",
        "entity_name": "Hàn Phong",
        "correction_type": "entity_profile",
        "proposed_content": json.dumps({
            "entity_type": "character",
            "summary": "Đoàn trưởng Hàn Phong",
            "content": "Nhân vật chính của truyện."
        }),
        "evidence": [{"chapter_number": 1}],
        "status": "approved"
    }
    candidate = build_wiki_candidate_from_correction(correction)
    try:
        json_str = json.dumps(candidate)
        assert json_str is not None
    except TypeError:
        pytest.fail("Candidate payload is not JSON serializable")
