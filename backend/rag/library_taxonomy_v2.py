# library_taxonomy_v2.py
import re
from typing import Dict, List, Any

# Taxonomy V2 Categories and Vietnamese Labels
TAXONOMY_V2_LABELS = {
    "character": "Nhân vật",
    "zombie_species": "Loài zombie",
    "mutated_creature": "Sinh vật biến dị",
    "location_base": "Căn cứ / Địa điểm",
    "organization_faction": "Tổ chức / Thế lực",
    "weapon": "Vũ khí",
    "item": "Vật phẩm",
    "crystal_core": "Tinh thạch / Tinh thể",
    "ability_skill": "Dị năng / Kỹ năng",
    "skill_book": "Sách kỹ năng",
    "event": "Sự kiện",
    "relationship": "Quan hệ",
    "chapter_summary": "Tóm tắt chương"
}

# Whitelisted lowercase keywords that prevent rejection of lowercase terms
WHITELIST_KEYWORDS = {
    "zombie", "tinh thể", "tinh thạch", "dị năng", "kỹ năng", "đội", "thẻ", "sách", "súng",
    "dao", "kiếm", "căn cứ", "hạch", "thức tỉnh", "biến dị", "quái vật", "xác sống", "biến thể"
}

# Common Vietnamese action verbs to reject as action/verb clauses
ACTION_VERBS = {
    "giết", "cứu", "tiến vào", "tấn công", "phát hiện", "thăng cấp", "chạy", "nhảy", "ăn", "uống",
    "nói", "hỏi", "đi", "đứng", "nằm", "ngồi", "thấy", "nghe", "biết", "nghĩ", "muốn", "cần",
    "nhận được", "tiêu diệt", "bắt đầu", "kết thúc", "xuất hiện", "tìm thấy", "nhặt được", "sử dụng",
    "chém", "bắn", "đâm", "né", "tránh", "đưa", "đảo", "đem", "đành", "đánh", "định", "ở", "ôm"
}

# Blacklisted noise words or phrases
NOISE_BLACKLIST = {
    "ác độc", "ác ý", "âm ẩm", "đây đã", "đang", "vừa", "hắn", "nàng", "những kẻ",
    "của họ", "chúng ta", "tôi", "ta", "ngươi", "nó", "chúng", "bọn họ", "kẻ khác",
    "mọi người", "ai đó", "cái gì", "nơi này", "nơi đó", "lúc này", "lúc đó", "sau đó",
    "trước đó", "bên trong", "bên ngoài", "phía trước", "phía sau", "ở đó", "ở đây"
}

# Adjectives and function words to detect adjective-only terms
COMMON_ADJECTIVES = {
    "ác độc", "ác ý", "âm ẩm", "tàn ác", "mạnh mẽ", "yếu ớt", "độc ác", "hung dữ", "hung hãn", "hung tợn",
    "lạnh lùng", "tối tăm", "hoang vắng", "đổ nát", "xấu xa", "tốt bụng", "thông minh", "nhanh nhẹn", "chậm chạp",
    "lớn", "nhỏ", "nhiều", "ít", "đẹp", "xấu", "cao", "thấp", "dài", "ngắn", "nhanh", "chậm", "tàn nhẫn"
}

# Pronouns and grammar particles
GRAMMAR_WORDS = {
    "đã", "đang", "sẽ", "vừa", "đây", "đó", "kia", "này", "hắn", "nàng", "tôi", "tao", "mày", "tớ", "cậu",
    "anh", "em", "ông", "bà", "nó", "họ", "chúng", "ta", "chúng ta", "chúng tôi", "chúng tớ",
    "các", "những", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười", "nhiều", "vài",
    "đây đã", "đến", "từ", "ở", "vào", "ra", "lên", "xuống", "trong", "ngoài", "trên", "dưới", "trước", "sau"
}

ALL_NON_NOUNS = ACTION_VERBS.union(COMMON_ADJECTIVES).union(GRAMMAR_WORDS)

def is_rejected_v2(name: str) -> bool:
    """Returns True if the term should be rejected as noise/adjective-only/too short/too long."""
    if not name:
        return True
    
    name_clean = name.strip()
    name_lower = name_clean.lower()
    
    # 1. Length bounds
    if len(name_clean) < 2:
        return True
        
    words = name_clean.split()
    if len(words) > 12:
        return True
        
    # 2. Junk character filtering
    junk_symbols = set("@#$%^&*_+=<>|\\~`[]{}")
    if any(char in junk_symbols for char in name_clean):
        return True
        
    # 3. Blacklist matches
    if name_lower in NOISE_BLACKLIST:
        return True
        
    # 4. Case-checking for proper nouns vs lowercase noise
    has_capitalized = any(w[0].isupper() for w in words if w and w[0].isalpha())
    if not has_capitalized:
        # Lowercase terms must contain a whitelist keyword (e.g. "zombie", "tinh thể")
        if not any(kw in name_lower for kw in WHITELIST_KEYWORDS):
            return True
            
    # 5. Adjective-only/Verb-only checking
    # If all words in the term belong to our list of non-nouns
    if all(w.lower() in ALL_NON_NOUNS for w in words):
        return True
        
    # Check if first word is a lowercase action verb (unless whitelisted)
    if words[0].lower() in ACTION_VERBS and not any(kw in name_lower for kw in WHITELIST_KEYWORDS):
        return True
        
    return False

def classify_term_v2(name: str, context: str = "") -> str:
    """Classifies a term into one of the 13 Taxonomy V2 categories based on regex and keywords."""
    n_lower = name.lower().strip()
    c_lower = context.lower().strip()
    
    # 1. Skill Book (e.g., "Sách kỹ năng Băng Độc", "Quyển sách", starts/ends with "sách")
    if "sách kỹ năng" in n_lower or "quyển sách" in n_lower:
        return "skill_book"
    if n_lower.startswith("sách ") or n_lower.endswith(" sách"):
        return "skill_book"
        
    # 2. Zombie Species (e.g., "Zombie Cấp 3", "Xác sống", "Biến thể", "Quái vật")
    if "zombie cấp" in n_lower or "xác sống" in n_lower or "biến thể" in n_lower or "quái vật" in n_lower:
        return "zombie_species"
        
    # 3. Crystal Core (e.g., "Tinh thể zombie", "Tinh thạch khai phá", "Tinh thạch nguyện ước", "Hạch tinh thể")
    if "tinh thạch" in n_lower or "tinh thể" in n_lower or "hạch" in n_lower or "nguyện ước" in n_lower or "khai phá" in n_lower:
        return "crystal_core"
        
    # 4. Weapon (e.g., "Súng Diệt Quỷ", "Kiếm", "Dao", "Đao", "Vũ khí")
    weapon_kws = ["súng", "dao", "kiếm", "pháo", "đao", "vũ khí"]
    if any(n_lower.startswith(kw) or f" {kw} " in f" {n_lower} " or n_lower.endswith(kw) for kw in weapon_kws):
        return "weapon"
        
    # 5. Ability/Skill (e.g., "Băng Độc", "Dị năng", "Kỹ năng", "Năng lực")
    ability_kws = ["dị năng", "kỹ năng", "năng lực", "thức tỉnh", "băng độc", "chiêu thức", "băng giáp"]
    if any(kw in n_lower for kw in ability_kws) or n_lower == "băng độc":
        return "ability_skill"
        
    # 6. Organization/Faction (e.g., "Đại Thiên Thần", "Quân đội", "Căn cứ")
    # Đại Thiên Thần is explicitly an organization_faction
    if "đại thiên thần" in n_lower:
        return "organization_faction"
    faction_kws = ["quân đội", "công ty", "bang", "hội", "tổ chức", "băng nhóm", "phòng quản lý"]
    if any(kw in n_lower for kw in faction_kws) or n_lower == "đội" or n_lower.startswith("đội săn") or n_lower.startswith("đội tuần"):
        return "organization_faction"
        
    # 7. Location/Base (e.g., "Căn cứ Hi Vọng", "Thành phố", "Khu")
    loc_kws = ["căn cứ", "thành phố", "khu", "trạm", "bệnh viện", "trường", "kho", "căng tin", "tòa nhà", "nhà kho", "tầng hầm", "phòng điều hành"]
    if any(kw in n_lower for kw in loc_kws):
        return "location_base"
        
    # 8. Mutated Creature
    if "biến dị" in n_lower or "dị dạng" in n_lower:
        return "mutated_creature"
        
    # 9. Item
    item_kws = ["vật phẩm", "trang bị", "dịch thể", "hộp thực phẩm", "thẻ triệu hồi", "thẻ giao dịch", "thẻ bài"]
    if any(kw in n_lower for kw in item_kws) or n_lower == "thẻ" or n_lower.startswith("thẻ "):
        return "item"
        
    # 10. Relationship
    if " và " in n_lower:
        return "relationship"
        
    # 11. Event
    if any(ev in n_lower for ev in ["xuất hiện", "giết", "cứu", "nhận được", "tiến vào", "tấn công", "phát hiện", "thăng cấp"]):
        return "event"
        
    # 12. Character
    # Proper nouns that don't match any keywords above are characters by default
    words = name.split()
    has_capitalized = any(w[0].isupper() for w in words if w and w[0].isalpha())
    if has_capitalized:
        return "character"
        
    return "character" # Default fallback
