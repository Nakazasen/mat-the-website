import pytest
from backend.rag.effective_patch_engine import (
    build_patch_payloads,
    group_feedback_by_target,
    extract_target_entity_from_feedback
)

def test_extract_target_entity():
    # Test "câu hỏi X là ai"
    ent, pattern = extract_target_entity_from_feedback("Trả lời lan man, câu hỏi Hàn Phong là ai?", "Hàn Phong đang")
    assert ent == "Hàn Phong"
    assert pattern == "Hàn Phong là ai?"

    # Test "không liên quan đến X"
    ent, pattern = extract_target_entity_from_feedback("Mục này không liên quan đến Hàn Phong.", "Hàn Phong nhìn")
    assert ent == "Hàn Phong"
    assert pattern == "Hàn Phong là ai?"

    # Fallback to proper nouns in record name
    ent, pattern = extract_target_entity_from_feedback("Lan man quá.", "đệ Hàn Phong")
    assert ent == "Hàn Phong"
    assert pattern == "Hàn Phong là ai?"

def test_wrong_info_creates_hide_or_deprioritize():
    # 5 wrong_info feedback rows should create a hide_record patch
    feedback_rows = [
        {"id": f"fb-{i}", "provisional_id": "pid-1", "feedback_type": "wrong_info", "user_comment": "Sai rồi"}
        for i in range(5)
    ]
    provisional_records = {
        "pid-1": {"id": "pid-1", "name": "Bàng Lâm", "summary": "Nhân vật phản diện"}
    }
    patches = build_patch_payloads(feedback_rows, provisional_records)
    assert len(patches) == 1
    assert patches[0]["patch_type"] == "hide_record"
    assert patches[0]["oracle_policy"] == "block"
    assert patches[0]["confidence"] == 1.0
    assert "pid-1" in patches[0]["feedback_ids"] or len(patches[0]["feedback_ids"]) == 5

    # 3 wrong_info feedback rows should create a deprioritize_record patch
    feedback_rows_deprio = [
        {"id": f"fb-{i}", "provisional_id": "pid-1", "feedback_type": "wrong_info", "user_comment": "Sai rồi"}
        for i in range(3)
    ]
    patches_deprio = build_patch_payloads(feedback_rows_deprio, provisional_records)
    assert len(patches_deprio) == 1
    assert patches_deprio[0]["patch_type"] == "deprioritize_record"
    assert patches_deprio[0]["oracle_policy"] == "deprioritize"
    assert patches_deprio[0]["confidence"] == 0.8

def test_duplicate_feedback_creates_warn():
    # 3 duplicate feedback rows should create a warn_record patch
    feedback_rows = [
        {"id": f"fb-{i}", "provisional_id": "pid-1", "feedback_type": "duplicate", "user_comment": "Trùng mục"}
        for i in range(3)
    ]
    provisional_records = {
        "pid-1": {"id": "pid-1", "name": "Bàng Lâm", "summary": "Nhân vật phản diện"}
    }
    patches = build_patch_payloads(feedback_rows, provisional_records)
    assert len(patches) == 1
    assert patches[0]["patch_type"] == "warn_record"
    assert patches[0]["oracle_policy"] == "warn"
    assert patches[0]["confidence"] == 0.7

def test_no_summary_without_strong_correction():
    # If corrections are weak or non-identical, effective_summary patch is NOT created
    feedback_rows = [
        {"id": "fb-1", "provisional_id": "pid-1", "feedback_type": "missing_info", "suggested_correction": "A"},
        {"id": "fb-2", "provisional_id": "pid-1", "feedback_type": "missing_info", "suggested_correction": "B"}
    ]
    provisional_records = {
        "pid-1": {"id": "pid-1", "name": "Bàng Lâm", "summary": "Nhân vật phản diện"}
    }
    patches = build_patch_payloads(feedback_rows, provisional_records)
    # No patches should be created because suggested corrections are too short and don't match
    assert not any(p["patch_type"] == "effective_summary" for p in patches)

    # 2 identical corrections of length >= 10 should create an effective_summary patch
    feedback_rows_strong = [
        {"id": "fb-1", "provisional_id": "pid-1", "feedback_type": "wrong_info", "suggested_correction": "Đây là nhân vật chính diện của tông môn"},
        {"id": "fb-2", "provisional_id": "pid-1", "feedback_type": "wrong_info", "suggested_correction": "Đây là nhân vật chính diện của tông môn"}
    ]
    patches_strong = build_patch_payloads(feedback_rows_strong, provisional_records)
    summary_patches = [p for p in patches_strong if p["patch_type"] == "effective_summary"]
    assert len(summary_patches) == 1
    assert summary_patches[0]["effective_summary"] == "Đây là nhân vật chính diện của tông môn"
    assert summary_patches[0]["confidence"] == 0.9

def test_noisy_feedback_creates_suppress_related():
    # Feedback containing "lan man/không liên quan" should create suppress_related_for_identity_query patch
    feedback_rows = [
        {
            "id": "fb-1",
            "provisional_id": "pid-noisy",
            "feedback_type": "wrong_info",
            "user_comment": "Trả lời lan man, các mục này không liên quan đến câu hỏi Hàn Phong là ai."
        }
    ]
    provisional_records = {
        "pid-noisy": {"id": "pid-noisy", "name": "Hàn Phong đang", "summary": "Hàn Phong đang đi"}
    }
    patches = build_patch_payloads(feedback_rows, provisional_records)
    
    suppress_patches = [p for p in patches if p["patch_type"] == "suppress_related_for_identity_query"]
    assert len(suppress_patches) == 1
    assert suppress_patches[0]["target_name"] == "Hàn Phong"
    assert suppress_patches[0]["query_pattern"] == "Hàn Phong là ai?"
    assert "pid-noisy" in suppress_patches[0]["suppress_record_ids"]
