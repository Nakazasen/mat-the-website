import os
import sys
import json
import pytest
from unittest.mock import MagicMock, patch

# Configure path imports
sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.rag.wiki_apply_dry_run import (
    generate_slug,
    build_wiki_entry_payload,
    validate_wiki_entry_payload,
    detect_existing_wiki_entry,
    build_apply_plan
)

def test_generate_slug_stability():
    assert generate_slug("Tinh thể zombie") == "tinh-the-zombie"
    assert generate_slug("Hàn Phong") == "han-phong"
    assert generate_slug("Vũ khí tối thượng!") == "vu-khi-toi-thuong"
    # đ should map to d
    assert generate_slug("Đoàn quân") == "doan-quan"
    assert generate_slug("") == ""
    assert generate_slug(None) == ""

def test_build_wiki_entry_payload_mapping():
    candidate = {
        "entity_name": " Tinh thể zombie ",
        "entity_type": "Vật phẩm",
        "summary": "Tóm tắt ngắn.",
        "content": "Nội dung chi tiết.",
        "aliases": ["Tinh thể", "Zombie Crystal"]
    }
    payload = build_wiki_entry_payload(candidate)
    
    assert payload["title"] == "Tinh thể zombie"
    assert payload["category"] == "Vật phẩm"
    assert payload["slug"] == "tinh-the-zombie"
    assert payload["summary"] == "Tóm tắt ngắn."
    assert payload["content"] == "Nội dung chi tiết."
    assert payload["tags"] == ["Tinh thể", "Zombie Crystal"]
    assert payload["is_main_character"] is False
    assert payload["sort_order"] == 999

def test_build_wiki_entry_payload_category_normalization():
    # item -> Vật phẩm
    c1 = {"entity_name": "Rìu sắt", "entity_type": "item"}
    p1 = build_wiki_entry_payload(c1)
    assert p1["category"] == "Vật phẩm"
    
    # character -> Nhân vật
    c2 = {"entity_name": "Hàn Phong", "entity_type": "character"}
    p2 = build_wiki_entry_payload(c2)
    assert p2["category"] == "Nhân vật"
    
    # unknown/invalid -> Fallback (Sinh vật)
    c3 = {"entity_name": "Thực thể lạ", "entity_type": "strange_type"}
    p3 = build_wiki_entry_payload(c3)
    assert p3["category"] == "Sinh vật"

def test_validate_wiki_entry_payload():
    # 1. Valid payload
    valid_payload = {
        "title": "Tinh thể zombie",
        "category": "Vật phẩm",
        "slug": "tinh-the-zombie",
        "summary": "Tóm tắt",
        "content": "Chi tiết"
    }
    v1 = validate_wiki_entry_payload(valid_payload)
    assert v1["valid"] is True
    assert not v1["errors"]
    
    # 2. Missing required fields
    invalid_payload = {
        "title": "",
        "category": "Invalid Category",
        "slug": "   ",
        "summary": None,
        "content": ""
    }
    v2 = validate_wiki_entry_payload(invalid_payload)
    assert v2["valid"] is False
    assert len(v2["errors"]) == 5
    assert any("title" in e for e in v2["errors"])
    assert any("category" in e for e in v2["errors"])
    assert any("slug" in e for e in v2["errors"])
    assert any("summary" in e for e in v2["errors"])
    assert any("content" in e for e in v2["errors"])

def test_detect_existing_wiki_entry_no_duplicates():
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    
    dup_check = detect_existing_wiki_entry(mock_supabase, "Title", "slug")
    assert dup_check["exists"] is False
    assert dup_check["duplicate_title"] is False
    assert dup_check["duplicate_slug"] is False
    assert dup_check["existing_entry"] is None

def test_detect_existing_wiki_entry_duplicate_title():
    mock_supabase = MagicMock()
    
    # Custom side effect for query simulation
    def mock_table(name):
        if name == "wiki_entries":
            mock_tbl = MagicMock()
            def mock_select(fields):
                mock_sel = MagicMock()
                def mock_eq(field, value):
                    mock_exec = MagicMock()
                    if field == "title" and value == "Tinh thể zombie":
                        mock_exec.execute.return_value.data = [{"id": "dup-id-123", "title": "Tinh thể zombie", "slug": "tinh-the-zombie"}]
                    else:
                        mock_exec.execute.return_value.data = []
                    return mock_exec
                mock_sel.eq.side_effect = mock_eq
                return mock_sel
            mock_tbl.select.side_effect = mock_select
            return mock_tbl
        return MagicMock()
        
    mock_supabase.table.side_effect = mock_table
    
    dup_check = detect_existing_wiki_entry(mock_supabase, "Tinh thể zombie", "tinh-the-zombie")
    assert dup_check["exists"] is True
    assert dup_check["duplicate_title"] is True
    assert dup_check["duplicate_slug"] is False
    assert dup_check["existing_entry"]["id"] == "dup-id-123"

def test_detect_existing_wiki_entry_duplicate_slug():
    mock_supabase = MagicMock()
    
    def mock_table(name):
        if name == "wiki_entries":
            mock_tbl = MagicMock()
            def mock_select(fields):
                mock_sel = MagicMock()
                def mock_eq(field, value):
                    mock_exec = MagicMock()
                    if field == "slug" and value == "tinh-the-zombie":
                        mock_exec.execute.return_value.data = [{"id": "dup-slug-123", "title": "Khác Tên Nhưng Trùng Slug", "slug": "tinh-the-zombie"}]
                    else:
                        mock_exec.execute.return_value.data = []
                    return mock_exec
                mock_sel.eq.side_effect = mock_eq
                return mock_sel
            mock_tbl.select.side_effect = mock_select
            return mock_tbl
        return MagicMock()
        
    mock_supabase.table.side_effect = mock_table
    
    dup_check = detect_existing_wiki_entry(mock_supabase, "Khác Tên Nhưng Trùng Slug", "tinh-the-zombie")
    assert dup_check["exists"] is True
    assert dup_check["duplicate_title"] is False
    assert dup_check["duplicate_slug"] is True
    assert dup_check["existing_entry"]["id"] == "dup-slug-123"

def test_build_apply_plan_behavior():
    candidates = [
        # 1. Eligible candidate (requires canon_reviewed: True or human_review_required: False)
        {
            "correction_id": "corr-1",
            "entity_name": "Tinh thể zombie",
            "entity_type": "Vật phẩm",
            "summary": "Tóm tắt",
            "content": "Nội dung",
            "aliases": ["Tinh thể"],
            "status": "ready_for_review",
            "human_review_required": False
        },
        # 2. Ineligible (missing summary/content)
        {
            "correction_id": "corr-2",
            "entity_name": "Zombie đói",
            "entity_type": "Sinh vật",
            "summary": "",
            "content": "",
            "status": "needs_human_fill",
            "human_review_required": False
        }
    ]
    
    plan = build_apply_plan(candidates)
    
    summary = plan["summary"]
    assert summary["total_candidates"] == 2
    assert summary["eligible_count"] == 1
    assert summary["ineligible_count"] == 1
    
    entries = plan["plan_entries"]
    assert entries[0]["correction_id"] == "corr-1"
    assert entries[0]["eligible"] is True
    assert entries[0]["payload"]["title"] == "Tinh thể zombie"
    
    assert entries[1]["correction_id"] == "corr-2"
    assert entries[1]["eligible"] is False
    assert entries[1]["reason"] == "needs_human_fill"
    assert entries[1]["payload"] is None

def test_build_apply_plan_duplicate_detection():
    candidates = [
        {
            "correction_id": "corr-1",
            "entity_name": "Tinh thể zombie",
            "entity_type": "Vật phẩm",
            "summary": "Tóm tắt",
            "content": "Chi tiết",
            "status": "ready_for_review",
            "human_review_required": False
        }
    ]
    
    # Mock duplicate check return exists = True
    mock_supabase = MagicMock()
    mock_select = MagicMock()
    # Mocking that query returns a duplicate entry in title check
    mock_select.execute.return_value.data = [{"id": "dup-id"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value = mock_select
    
    plan = build_apply_plan(candidates, supabase=mock_supabase)
    
    summary = plan["summary"]
    assert summary["total_candidates"] == 1
    assert summary["eligible_count"] == 0
    assert summary["ineligible_count"] == 1
    assert summary["duplicate_count"] == 1
    
    entry = plan["plan_entries"][0]
    assert entry["eligible"] is False
    assert entry["reason"] in ("duplicate_title", "duplicate_slug")

def test_json_serializable():
    candidates = [
        {
            "correction_id": "corr-1",
            "entity_name": "Tinh thể zombie",
            "entity_type": "Vật phẩm",
            "summary": "Tóm tắt",
            "content": "Nội dung",
            "status": "ready_for_review",
            "human_review_required": False
        }
    ]
    plan = build_apply_plan(candidates)
    
    # Try serializing to json to ensure no date objects or non-serializable fields are returned
    dumped = json.dumps(plan)
    loaded = json.loads(dumped)
    assert "timestamp" in loaded
    assert loaded["summary"]["total_candidates"] == 1

def test_dry_run_safety():
    candidates = [
        {
            "correction_id": "corr-1",
            "entity_name": "Tinh thể zombie",
            "entity_type": "Vật phẩm",
            "summary": "Tóm tắt",
            "content": "Nội dung",
            "status": "ready_for_review",
            "human_review_required": False
        }
    ]
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    
    plan = build_apply_plan(candidates, supabase=mock_supabase)
    
    # Ensure insert, update, upsert, delete are NEVER called on wiki_entries
    assert not mock_supabase.table.return_value.insert.called
    assert not mock_supabase.table.return_value.update.called
    assert not mock_supabase.table.return_value.upsert.called
    assert not mock_supabase.table.return_value.delete.called

# New Safety Gate and Human Review Gate tests for Phase 6E

def test_safety_gate_smoke_test_blacklist():
    # 1. Title contains SMOKE TEST
    c1 = {
        "correction_id": "c1",
        "entity_name": "SMOKE TEST - Tinh thể",
        "entity_type": "Vật phẩm",
        "summary": "Tóm tắt sạch",
        "content": "Nội dung sạch",
        "human_review_required": False
    }
    plan = build_apply_plan([c1])
    assert plan["plan_entries"][0]["eligible"] is False
    assert plan["plan_entries"][0]["reason"] == "unsafe_test_or_placeholder_content"

    # 2. Content contains placeholder/TODO
    c2 = {
        "correction_id": "c2",
        "entity_name": "Rìu sắt",
        "entity_type": "Vật phẩm",
        "summary": "TODO: Thêm tóm tắt sau",
        "content": "Chi tiết rìu",
        "human_review_required": False
    }
    plan = build_apply_plan([c2])
    assert plan["plan_entries"][0]["eligible"] is False
    assert plan["plan_entries"][0]["reason"] == "unsafe_test_or_placeholder_content"

    # 3. Summary contains "chỉ dùng để kiểm thử"
    c3 = {
        "correction_id": "c3",
        "entity_name": "Rìu sắt",
        "entity_type": "Vật phẩm",
        "summary": "Rìu sắt cổ xưa",
        "content": "Nội dung này chỉ dùng để kiểm thử hành vi.",
        "human_review_required": False
    }
    plan = build_apply_plan([c3])
    assert plan["plan_entries"][0]["eligible"] is False
    assert plan["plan_entries"][0]["reason"] == "unsafe_test_or_placeholder_content"

def test_human_review_gate_requirements():
    # 1. human_review_required = True, and no canon_reviewed -> blocked
    c1 = {
        "correction_id": "c1",
        "entity_name": "Hàn Phong",
        "entity_type": "Nhân vật",
        "summary": "Tóm tắt sạch",
        "content": "Nội dung sạch",
        "human_review_required": True
    }
    plan = build_apply_plan([c1])
    assert plan["plan_entries"][0]["eligible"] is False
    assert plan["plan_entries"][0]["reason"] == "canon_review_required"

    # 2. human_review_required = True, but canon_reviewed = True -> approved
    c2 = {
        "correction_id": "c2",
        "entity_name": "Hàn Phong",
        "entity_type": "Nhân vật",
        "summary": "Tóm tắt sạch",
        "content": "Nội dung sạch",
        "human_review_required": True,
        "canon_reviewed": True
    }
    plan = build_apply_plan([c2])
    assert plan["plan_entries"][0]["eligible"] is True

    # 3. human_review_required = False -> approved automatically
    c3 = {
        "correction_id": "c3",
        "entity_name": "Hàn Phong",
        "entity_type": "Nhân vật",
        "summary": "Tóm tắt sạch",
        "content": "Nội dung sạch",
        "human_review_required": False
    }
    plan = build_apply_plan([c3])
    assert plan["plan_entries"][0]["eligible"] is True
