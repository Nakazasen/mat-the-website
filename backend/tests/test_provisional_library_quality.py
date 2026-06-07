import pytest
import json
from typing import Dict, Any

from backend.rag.provisional_library_quality import (
    is_noise_name,
    has_valid_name,
    score_record_quality,
    classify_quality,
    rank_records,
    build_quality_report
)

def test_is_noise_name():
    # Invalid/noise names
    assert is_noise_name("") == True
    assert is_noise_name("A") == True # Too short
    assert is_noise_name("Đây là một cái tên cực kỳ dài dài dài dài dài dài dài dài dài dài dài dài dài") == True # Too long (>12 words)
    assert is_noise_name("Hàn Phong@123") == True # Contains junk character
    assert is_noise_name("giết zombie") == True # Action verb start
    assert is_noise_name("chạy trốn khỏi căn cứ") == True # Clause
    
    # Valid names
    assert is_noise_name("Hàn Phong") == False
    assert is_noise_name("Tinh thể zombie") == False
    assert is_noise_name("Căn cứ Giang Nam") == False

def test_classify_quality():
    # 1. high confidence record được phân loại đúng (evidence >= 3, confidence >= 0.7)
    high_rec = {
        "name": "Hàn Phong",
        "type": "entity",
        "summary": "Nhân vật chính của câu chuyện.",
        "evidence": [{"ch": 1}, {"ch": 2}, {"ch": 3}],
        "confidence": 0.7,
        "discard_reasons": []
    }
    assert classify_quality(high_rec) == "high_confidence"
    
    # 2. medium confidence record được phân loại đúng (evidence >= 2, confidence >= 0.5)
    med_rec = {
        "name": "Lâm Nhã Vy",
        "type": "entity",
        "summary": "Đồng đội của Hàn Phong.",
        "evidence": [{"ch": 1}, {"ch": 2}],
        "confidence": 0.5,
        "discard_reasons": []
    }
    assert classify_quality(med_rec) == "medium_confidence"
    
    # 3. one evidence -> weak_evidence
    weak_rec = {
        "name": "Phương Tường",
        "type": "entity",
        "summary": "Giám đốc cũ của Hàn Phong.",
        "evidence": [{"ch": 1}],
        "confidence": 0.3,
        "discard_reasons": []
    }
    assert classify_quality(weak_rec) == "weak_evidence"
    
    # 4. invalid/noise name -> discard_candidate
    noise_rec = {
        "name": "chạy trốn khỏi căn cứ",
        "type": "entity",
        "summary": "Mô tả chạy trốn.",
        "evidence": [{"ch": 1}, {"ch": 2}, {"ch": 3}],
        "confidence": 0.7,
        "discard_reasons": ["noise_name"]
    }
    assert classify_quality(noise_rec) == "discard_candidate"

def test_duplicate_deduplication():
    # 5. duplicate normalized name giữ record mạnh nhất.
    r1 = {
        "id": "id1",
        "name": "Hàn Phong",
        "type": "entity",
        "summary": "Nhân vật Hàn Phong.",
        "evidence": [{"ch": 1}, {"ch": 2}, {"ch": 3}],
        "confidence": 0.7,
        "source": "test"
    }
    r2 = {
        "id": "id2",
        "name": "hàn phong", # duplicate normalized
        "type": "entity",
        "summary": "Thực thể hàn phong.",
        "evidence": [{"ch": 1}],
        "confidence": 0.3,
        "source": "test"
    }
    
    ranked = rank_records([r1, r2])
    assert len(ranked) == 2
    
    # r1 should be kept (not weaker duplicate), r2 should be marked weaker duplicate and discarded
    r1_ranked = next(r for r in ranked if r["id"] == "id1")
    r2_ranked = next(r for r in ranked if r["id"] == "id2")
    
    assert r1_ranked["quality_class"] == "high_confidence"
    assert r2_ranked["quality_class"] == "discard_candidate"
    assert "duplicate_weaker" in r2_ranked["discard_reasons"]

def test_report_json_serializable():
    # 6. report JSON serializable
    r1 = {
        "id": "id1",
        "name": "Hàn Phong",
        "type": "entity",
        "summary": "Nhân vật chính.",
        "evidence": [{"ch": 1}, {"ch": 2}, {"ch": 3}],
        "confidence": 0.7
    }
    r2 = {
        "id": "id2",
        "name": "giết zombie",
        "type": "entity",
        "summary": "Hành động giết zombie.",
        "evidence": [{"ch": 1}],
        "confidence": 0.3
    }
    
    ranked = rank_records([r1, r2])
    report = build_quality_report(ranked)
    
    serialized = json.dumps(report)
    assert serialized is not None
    deserialized = json.loads(serialized)
    assert deserialized["total"] == 2
    assert deserialized["high_confidence"] == 1
    assert deserialized["discard_candidate"] == 1

def test_strict_constraints():
    # 7. không có write path wiki_entries
    # 8. không gọi LLM
    import inspect
    import backend.rag.provisional_library_quality as plq
    
    source_code = inspect.getsource(plq)
    
    # Check no supabase write functions are used
    assert "supabase" not in source_code
    assert "insert" not in source_code
    assert "update" not in source_code
    assert "upsert" not in source_code
    assert "delete" not in source_code
    
    # Check no LLM keywords
    for kw in ["openai", "gemini", "anthropic", "chat.completions", "generate_content"]:
        assert kw not in source_code.lower()
