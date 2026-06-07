import pytest
import json
from typing import Dict, Any

from backend.rag.provisional_library import (
    normalize_name,
    classify_term,
    score_confidence,
    extract_candidate_terms,
    build_provisional_record,
    merge_duplicate_records
)

def test_normalize_name():
    # 1. normalize_name behaves stably
    assert normalize_name("  Hàn Phong  ") == "Hàn Phong"
    assert normalize_name('"Lâm Nhã Vy"') == "Lâm Nhã Vy"
    assert normalize_name("- Tinh thể zombie -") == "Tinh thể zombie"
    assert normalize_name(" (Băng thứ) ") == "Băng thứ"
    assert normalize_name("") == ""

def test_classify_term():
    # 2. classify item/faction/location/ability/entity by keyword
    # Ability
    assert classify_term("Băng giáp", "Hàn Phong sử dụng băng giáp bảo vệ bản thân.") == "ability"
    assert classify_term("Dị năng", "Anh ta thức tỉnh dị năng hệ hỏa.") == "ability"
    
    # Item
    assert classify_term("Tinh thể zombie", "Nhận được một viên tinh thể zombie từ quái vật.") == "item"
    assert classify_term("Thẻ triệu hồi", "Hắn có được thẻ triệu hồi ma thú.") == "item"
    
    # Location
    assert classify_term("Căn cứ Giang Nam", "Tiến vào căn cứ Giang Nam trú ẩn.") == "location"
    assert classify_term("Phòng điều hành", "Mọi người tụ tập tại phòng điều hành.") == "location"
    
    # Faction
    assert classify_term("Đại thiên thần", "Họ thuộc tổ chức Đại thiên thần.") == "faction"
    assert classify_term("Bang hội", "Thế lực của bang hội bắt đầu trỗi dậy.") == "faction"
    
    # Relationship
    assert classify_term("Đồng đội", "Họ là những đồng đội kề vai sát cánh.") == "relationship"
    assert classify_term("Hàn Phong và Lâm Nhã Vy", "Hàn Phong là sếp của Lâm Nhã Vy.") == "relationship"
    
    # Event
    assert classify_term("Hàn Phong thăng cấp", "Đột phá thăng cấp thành công.") == "event"
    assert classify_term("Hàn Phong giết zombie", "Con quái vật đã bị tiêu diệt.") == "event"
    
    # Default Entity
    assert classify_term("Hàn Phong", "Hàn Phong bước ra khỏi phòng.") == "entity"

def test_merge_duplicate_records():
    # 3. merge duplicate records
    # Mock provisional records
    r1 = {
        "id": "id1",
        "name": "Hàn Phong",
        "type": "entity",
        "summary": "Thực thể Hàn Phong xuất hiện.",
        "evidence": [
            {
                "chapter_number": 1,
                "chapter_title": "Chương 1",
                "chunk_index": 0,
                "content_hash": "hash1",
                "preview": "Hàn Phong đứng nhìn trời mưa."
            }
        ],
        "confidence": 0.3,
        "status": "provisional",
        "source": "test",
        "feedback_score": 0,
        "needs_review": False
    }
    r2 = {
        "id": "id2",
        "name": "hàn phong", # different casing
        "type": "entity",
        "summary": "Thực thể hàn phong xuất hiện.",
        "evidence": [
            {
                "chapter_number": 2,
                "chapter_title": "Chương 2",
                "chunk_index": 1,
                "content_hash": "hash2",
                "preview": "Mọi người nói về hàn phong."
            },
            {
                "chapter_number": 1,
                "chapter_title": "Chương 1",
                "chunk_index": 0,
                "content_hash": "hash1", # duplicate evidence
                "preview": "Hàn Phong đứng nhìn trời mưa."
            }
        ],
        "confidence": 0.5,
        "status": "provisional",
        "source": "test",
        "feedback_score": 0,
        "needs_review": False
    }
    
    merged = merge_duplicate_records([r1, r2], min_evidence=2)
    assert len(merged) == 1
    m_record = merged[0]
    
    # Check casing matches the first encountered name format
    assert m_record["name"] == "Hàn Phong"
    assert m_record["type"] == "entity"
    # deduplicated evidence (hash1, hash2)
    assert len(m_record["evidence"]) == 2
    assert m_record["evidence"][0]["content_hash"] == "hash1" # sorted by chapter
    assert m_record["evidence"][1]["content_hash"] == "hash2"
    
    # 4. confidence increases with evidence_count
    # starting at 0.1, +0.2 * count = 0.5
    assert m_record["confidence"] == 0.5
    assert m_record["status"] == "provisional"

def test_weak_evidence():
    # 5. weak evidence không được canon
    r = {
        "id": "id1",
        "name": "Đoàn Thanh",
        "type": "entity",
        "summary": "Đoàn Thanh xuất hiện.",
        "evidence": [
            {
                "chapter_number": 1,
                "chapter_title": "Chương 1",
                "chunk_index": 0,
                "content_hash": "hash1",
                "preview": "Đoàn Thanh đi ngang qua."
            }
        ],
        "confidence": 0.3,
        "status": "provisional",
        "source": "test",
        "feedback_score": 0,
        "needs_review": False
    }
    merged = merge_duplicate_records([r], min_evidence=2)
    assert len(merged) == 1
    assert merged[0]["confidence"] == 0.3
    assert merged[0]["status"] == "weak_evidence"

def test_json_serializable_and_schema():
    # 6. output JSON serializable and follows schema
    mock_cand = {
        "name": "Tinh thể zombie",
        "type": "item",
        "context": "Hàn Phong nhặt được tinh thể zombie.",
        "evidence": {
            "chapter_number": 1,
            "chapter_title": "Chương 1",
            "chunk_index": 1,
            "content_hash": "hash123",
            "preview": "Hàn Phong nhặt được tinh thể zombie."
        }
    }
    record = build_provisional_record(mock_cand, [mock_cand["evidence"]])
    
    # Verify schema fields
    required_keys = ["id", "name", "type", "summary", "evidence", "confidence", "status", "source", "feedback_score", "needs_review"]
    for k in required_keys:
        assert k in record
        
    assert record["name"] == "Tinh thể zombie"
    assert record["type"] == "item"
    assert record["status"] == "weak_evidence" # only 1 evidence
    
    # Assert JSON serializable
    serialized = json.dumps(record)
    assert serialized is not None
    deserialized = json.loads(serialized)
    assert deserialized["id"] == record["id"]

def test_strict_constraints():
    # 7. không có write path wiki_entries
    # 8. không gọi LLM
    # We inspect provisional_library.py to ensure it is purely algorithmic/extractive
    import inspect
    import backend.rag.provisional_library as pl
    
    source_code = inspect.getsource(pl)
    
    # Check no supabase write functions are used
    assert "supabase" not in source_code
    assert "insert" not in source_code
    assert "update" not in source_code
    assert "upsert" not in source_code
    assert "delete" not in source_code
    
    # Check no LLM keywords (openai, gemini, anthropic, client.chat.completions, etc.)
    for kw in ["openai", "gemini", "anthropic", "chat.completions", "generate_content"]:
        assert kw not in source_code.lower()
