# test_provisional_library_v2.py
import pytest
from backend.rag.provisional_library_v2 import (
    extract_candidate_terms_v2,
    build_provisional_record_v2,
    merge_duplicate_records_v2,
    normalize_name
)

# Mock story chunks for testing extraction pipeline
MOCK_CHUNKS = [
    {
        "chapter_number": 1,
        "chapter_title": "Ngày Tận Thế Bắt Đầu",
        "chunk_index": 0,
        "content_plain": "Nhân vật chính Hàn Phong đang đi qua Căn cứ Hi Vọng. Gió lạnh rít gào qua các tòa nhà đổ nát. Anh vung đao kết liễu một con Zombie Cấp 3 hung tợn.",
        "content_hash": "mock_hash_1"
    },
    {
        "chapter_number": 2,
        "chapter_title": "Tinh Thạch Khai Phá",
        "chunk_index": 0,
        "content_plain": "Hàn Phong tìm thấy Tinh thạch khai phá và nhặt được Tinh thể zombie bên cạnh thi thể quái vật. Hệ thống báo nhận sách kỹ năng Băng Độc. Dị năng Băng Độc của anh đạt cấp 2.",
        "content_hash": "mock_hash_2"
    },
    {
        "chapter_number": 3,
        "chapter_title": "Đại Thiên Thần Thế Lực",
        "chunk_index": 0,
        "content_plain": "Tại đây Đại Thiên Thần xuất hiện, dùng Súng Diệt Quỷ tiêu diệt zombie. Nhưng hành vi của họ có vẻ ác độc và ác ý.",
        "content_hash": "mock_hash_3"
    }
]

def test_extract_candidate_terms_v2():
    candidates = extract_candidate_terms_v2(MOCK_CHUNKS)
    
    # Assert we have extracted candidates
    assert len(candidates) > 0
    
    # Collect names
    names = {c["name"] for c in candidates}
    types = {c["type"] for c in candidates}
    
    # Check that whitelisted proper nouns and keywords are present
    assert "Hàn Phong" in names
    assert "Zombie Cấp 3" in names
    assert "Tinh thể zombie" in names
    assert "Tinh thạch khai phá" in names
    assert "Sách kỹ năng Băng Độc" in names
    assert "Băng Độc" in names
    assert "Đại Thiên Thần" in names
    assert "Căn cứ Hi Vọng" in names
    assert "Súng Diệt Quỷ" in names
    
    # Check classification matching V2 taxonomy
    assert "character" in types
    assert "zombie_species" in types
    assert "crystal_core" in types
    assert "skill_book" in types
    assert "ability_skill" in types
    assert "organization_faction" in types
    assert "location_base" in types
    assert "weapon" in types
    
    # Ensure noise words are NOT extracted
    assert "ác độc" not in names
    assert "ác ý" not in names
    assert "âm ẩm" not in names
    assert "đây đã" not in names

def test_build_and_merge_v2():
    candidates = extract_candidate_terms_v2(MOCK_CHUNKS)
    provisional_records = [
        build_provisional_record_v2(c, [c["evidence"]]) for c in candidates
    ]
    
    assert len(provisional_records) > 0
    
    # Verify properties
    rec = provisional_records[0]
    assert "id" in rec
    assert "name" in rec
    assert "type" in rec
    assert "summary" in rec
    assert "evidence" in rec
    assert "confidence" in rec
    assert "quality_score" in rec
    assert "quality_class" in rec
    assert "discard_reasons" in rec
    
    merged = merge_duplicate_records_v2(provisional_records)
    assert len(merged) <= len(provisional_records)
    
    # Ensure no database writes or LLM/embedding calls are done
    for r in merged:
        assert "embedding" not in r or r["embedding"] is None
        assert r["source"] == "story_chunks_auto_extract_v2"
