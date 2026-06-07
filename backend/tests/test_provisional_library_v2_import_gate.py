# test_provisional_library_v2_import_gate.py
import pytest
from backend.rag.provisional_library_v2_import_gate import is_importable_v2

def create_mock_record(name: str, t_type: str, quality_class: str = "high_confidence", evidence_count: int = 3) -> dict:
    return {
        "id": f"mock_id_{name}",
        "name": name,
        "type": t_type,
        "quality_class": quality_class,
        "evidence": [{"chapter_number": 1, "preview": "mock context"} for _ in range(evidence_count)],
        "confidence": 0.9,
        "status": "provisional"
    }

def test_import_gate_accepted_cases():
    # 1. Hàn Phong accepted as character
    rec1 = create_mock_record("Hàn Phong", "character", evidence_count=3)
    ok, reason = is_importable_v2(rec1)
    assert ok is True, f"Failed for Hàn Phong: {reason}"
    
    # 2. Zombie Cấp 3 accepted as zombie_species
    rec2 = create_mock_record("Zombie Cấp 3", "zombie_species", evidence_count=1)
    ok, reason = is_importable_v2(rec2)
    assert ok is True, f"Failed for Zombie Cấp 3: {reason}"
    
    # 3. Tinh thạch khai phá accepted as crystal_core
    rec3 = create_mock_record("Tinh thạch khai phá", "crystal_core", evidence_count=1)
    ok, reason = is_importable_v2(rec3)
    assert ok is True, f"Failed for Tinh thạch khai phá: {reason}"
    
    # 4. Tinh thạch nguyện ước accepted as crystal_core
    rec4 = create_mock_record("Tinh thạch nguyện ước", "crystal_core", evidence_count=1)
    ok, reason = is_importable_v2(rec4)
    assert ok is True, f"Failed for Tinh thạch nguyện ước: {reason}"
    
    # 5. Sách kỹ năng Băng Độc accepted as skill_book
    rec5 = create_mock_record("Sách kỹ năng Băng Độc", "skill_book", evidence_count=1)
    ok, reason = is_importable_v2(rec5)
    assert ok is True, f"Failed for Sách kỹ năng Băng Độc: {reason}"
    
    # 6. Băng Độc accepted as ability_skill
    rec6 = create_mock_record("Băng Độc", "ability_skill", evidence_count=2)
    ok, reason = is_importable_v2(rec6)
    assert ok is True, f"Failed for Băng Độc: {reason}"
    
    # 7. Đại Thiên Thần accepted as organization_faction
    rec7 = create_mock_record("Đại Thiên Thần", "organization_faction", evidence_count=2)
    ok, reason = is_importable_v2(rec7)
    assert ok is True, f"Failed for Đại Thiên Thần: {reason}"
    
    # 8. Căn cứ Hi Vọng accepted as location_base
    rec8 = create_mock_record("Căn cứ Hi Vọng", "location_base", evidence_count=2)
    ok, reason = is_importable_v2(rec8)
    assert ok is True, f"Failed for Căn cứ Hi Vọng: {reason}"
    
    # 9. Súng Diệt Quỷ accepted as weapon
    rec9 = create_mock_record("Súng Diệt Quỷ", "weapon", evidence_count=1)
    ok, reason = is_importable_v2(rec9)
    assert ok is True, f"Failed for Súng Diệt Quỷ: {reason}"

def test_import_gate_rejected_cases():
    # 10. ác độc rejected
    rec10 = create_mock_record("ác độc", "character", evidence_count=3)
    ok, reason = is_importable_v2(rec10)
    assert ok is False
    assert reason in ["noise_blacklist_match", "character_contains_adjective"]
    
    # 11. ác ý rejected
    rec11 = create_mock_record("ác ý", "character", evidence_count=3)
    ok, reason = is_importable_v2(rec11)
    assert ok is False
    assert reason in ["noise_blacklist_match", "character_contains_adjective"]
    
    # 12. âm ẩm rejected
    rec12 = create_mock_record("âm ẩm", "character", evidence_count=3)
    ok, reason = is_importable_v2(rec12)
    assert ok is False
    assert reason in ["noise_blacklist_match", "character_contains_adjective"]
    
    # 13. câu có động từ dài (sentence/action clauses) rejected
    rec13 = create_mock_record("Kỹ năng này tuy rằng hắn không có hiểu rõ", "ability_skill", evidence_count=2)
    ok, reason = is_importable_v2(rec13)
    assert ok is False
    assert reason in ["name_too_long", "ability_looks_like_clause"]
    
    # Weak evidence records should be rejected
    rec14 = create_mock_record("Hàn Phong", "character", quality_class="weak_evidence", evidence_count=1)
    ok, reason = is_importable_v2(rec14)
    assert ok is False
    assert reason == "weak_evidence"
    
    # Character with less than 3 evidence should be rejected
    rec15 = create_mock_record("Lâm Gia Hào", "character", evidence_count=2)
    ok, reason = is_importable_v2(rec15)
    assert ok is False
    assert reason == "character_insufficient_evidence"

def test_chapter_summary_always_accepted():
    rec = create_mock_record("Chương 10: Giác ngộ", "chapter_summary", quality_class="weak_evidence", evidence_count=1)
    ok, reason = is_importable_v2(rec)
    assert ok is True
