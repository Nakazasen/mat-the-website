# test_library_taxonomy_v2.py
import pytest
from backend.rag.library_taxonomy_v2 import (
    classify_term_v2,
    is_rejected_v2,
    TAXONOMY_V2_LABELS
)

def test_taxonomy_v2_classification():
    # 1. “Hàn Phong” => character
    assert classify_term_v2("Hàn Phong") == "character"
    
    # 2. “Zombie Cấp 3” => zombie_species
    assert classify_term_v2("Zombie Cấp 3") == "zombie_species"
    
    # 3. “Tinh thể zombie” => crystal_core
    assert classify_term_v2("Tinh thể zombie") == "crystal_core"
    
    # 4. “Tinh thạch khai phá” => crystal_core
    assert classify_term_v2("Tinh thạch khai phá") == "crystal_core"
    
    # 5. “Tinh thạch nguyện ước” => crystal_core
    assert classify_term_v2("Tinh thạch nguyện ước") == "crystal_core"
    
    # 6. “Sách kỹ năng Băng Độc” => skill_book
    assert classify_term_v2("Sách kỹ năng Băng Độc") == "skill_book"
    
    # 7. “Băng Độc” => ability_skill
    assert classify_term_v2("Băng Độc") == "ability_skill"
    
    # 8. “Đại Thiên Thần” => organization_faction
    assert classify_term_v2("Đại Thiên Thần") == "organization_faction"
    
    # 9. “Căn cứ Hi Vọng” => location_base
    assert classify_term_v2("Căn cứ Hi Vọng") == "location_base"
    
    # 10. “Súng Diệt Quỷ” => weapon
    assert classify_term_v2("Súng Diệt Quỷ") == "weapon"

def test_taxonomy_v2_rejection():
    # 11. “ác độc”, “ác ý”, “âm ẩm” => rejected/noise
    assert is_rejected_v2("ác độc") is True
    assert is_rejected_v2("ác ý") is True
    assert is_rejected_v2("âm ẩm") is True
    
    # Other noise terms
    assert is_rejected_v2("đây đã") is True
    assert is_rejected_v2("đang") is True
    assert is_rejected_v2("vừa") is True
    assert is_rejected_v2("hắn") is True
    assert is_rejected_v2("nàng") is True
    assert is_rejected_v2("những kẻ") is True
    assert is_rejected_v2("a") is True  # Too short
    
    # Valid terms should NOT be rejected
    assert is_rejected_v2("Hàn Phong") is False
    assert is_rejected_v2("Zombie Cấp 3") is False
    assert is_rejected_v2("Tinh thể zombie") is False
    assert is_rejected_v2("Căn cứ Hi Vọng") is False
    assert is_rejected_v2("Sách kỹ năng Băng Độc") is False
    assert is_rejected_v2("Băng Độc") is False

def test_taxonomy_v2_labels():
    assert "character" in TAXONOMY_V2_LABELS
    assert TAXONOMY_V2_LABELS["character"] == "Nhân vật"
    assert TAXONOMY_V2_LABELS["zombie_species"] == "Loài zombie"
