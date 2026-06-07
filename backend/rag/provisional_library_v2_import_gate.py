# provisional_library_v2_import_gate.py
import re
from typing import Dict, Any, Tuple

# Imported sets from library_taxonomy_v2
try:
    from backend.rag.library_taxonomy_v2 import ACTION_VERBS, COMMON_ADJECTIVES, NOISE_BLACKLIST, GRAMMAR_WORDS
except ImportError:
    ACTION_VERBS = set()
    COMMON_ADJECTIVES = set()
    NOISE_BLACKLIST = set()
    GRAMMAR_WORDS = set()

PRONOUNS_AND_NOISE = {
    "hắn", "nàng", "tôi", "nó", "chúng", "họ", "chúng ta", "bọn họ", "kẻ khác", "ta", "ngươi",
    "đây đã", "đang định", "đều đang", "hắn đang", "đang ở", "đang được", "đây", "đó", "kia", "này",
    "của họ", "chúng tôi", "chúng tớ", "của hắn", "của nàng", "của tôi", "của ta", "của nó", "của chúng"
}

GENERIC_NOUNS = {
    "hệ thống", "tang thi", "zombie", "tinh thể", "tinh thạch", "trường học", "bệnh viện", "căn cứ",
    "vũ khí", "súng", "dao", "kiếm", "dị năng", "kỹ năng", "thẻ", "sách", "người", "nhân vật", "con", "cái"
}

def check_title_case(name: str) -> bool:
    """Checks if each word in the name starts with a capital letter."""
    words = name.split()
    if not words:
        return False
    # Check if first character of each word is uppercase
    for w in words:
        if w and w[0].isalpha() and not w[0].isupper():
            return False
    return True

def is_importable_v2(record: Dict[str, Any]) -> Tuple[bool, str]:
    """Determines whether a provisional library record is eligible for import.
    
    Returns (True, "") if eligible, or (False, reason) if rejected.
    """
    name = record.get("name", "").strip()
    t_type = record.get("type", "")
    q_class = record.get("quality_class", "")
    evidence = record.get("evidence", [])
    evidence_count = len(evidence)
    
    # 0. Preserve all chapter summaries
    if t_type == "chapter_summary":
        return True, ""
        
    # 1. Global quality checks
    if q_class == "weak_evidence":
        return False, "weak_evidence"
        
    if not name or len(name) < 2:
        return False, "name_too_short"
        
    words = name.split()
    name_lower = name.lower()
    
    # Max length bounds
    if t_type in ["event", "relationship"]:
        if len(words) > 12:
            return False, "name_too_long"
    else:
        if len(words) > 6:
            return False, "name_too_long"
            
    # 2. Check for sentence punctuation
    if bool(re.search(r'[,.!?;:"]', name)):
        return False, "contains_punctuation"
        
    # 3. Check for pronoun/action/noise fragments
    if any(pron in name_lower.split() for pron in PRONOUNS_AND_NOISE):
        return False, "contains_pronoun_noise"
        
    if name_lower in NOISE_BLACKLIST:
        return False, "noise_blacklist_match"
        
    # 4. Check for starts with action verbs (for non-events)
    if t_type != "event" and words[0].lower() in ACTION_VERBS:
        return False, "starts_with_verb"
        
    # 5. Category-specific guards
    
    # CHARACTER
    if t_type == "character":
        # Must be title-cased proper nouns
        if not check_title_case(name):
            return False, "character_not_title_cased"
        if evidence_count < 3:
            return False, "character_insufficient_evidence"
        # First word cannot be generic noun
        if words[0].lower() in GENERIC_NOUNS:
            return False, "character_starts_with_generic_noun"
        # Cannot contain action verbs or adjectives
        if any(w.lower() in ACTION_VERBS for w in words):
            return False, "character_contains_verb"
        if any(w.lower() in COMMON_ADJECTIVES for w in words):
            return False, "character_contains_adjective"
            
    # ABILITY / SKILL
    elif t_type == "ability_skill":
        # Must contain skill keywords
        ability_kws = ["kỹ năng", "dị năng", "năng lực", "thức", "băng", "hỏa", "lôi", "độc", "quang", "tâm linh", "cường hóa", "tốc độ", "phòng ngự"]
        if not any(kw in name_lower for kw in ability_kws):
            return False, "ability_missing_keywords"
        if evidence_count < 2:
            return False, "ability_insufficient_evidence"
        # Reject sentence clauses (verbs/conjunctions/pronouns)
        sentence_indicators = {"tuy", "bởi", "vì", "nhưng", "tuy nhiên", "hẳn", "sẽ", "được", "làm", "để", "cho", "ném", "học", "trùng", "này", "kia"}
        if any(w in name_lower.split() for w in sentence_indicators):
            return False, "ability_looks_like_clause"
        # Reject if contains verbs like sử dụng, đạt, tăng
        action_indicators = {"sử dụng", "đạt", "gia tăng", "tăng cường", "phát huy", "kích hoạt"}
        if any(act in name_lower for act in action_indicators):
            return False, "ability_contains_action"
            
    # CRYSTAL CORE
    elif t_type == "crystal_core":
        crystal_kws = ["tinh thạch", "tinh thể", "hạch"]
        if not any(kw in name_lower for kw in crystal_kws):
            return False, "crystal_missing_keywords"
        if evidence_count < 1:
            return False, "crystal_insufficient_evidence"
            
    # SKILL BOOK
    elif t_type == "skill_book":
        book_kws = ["sách kỹ năng", "sách"]
        if not any(kw in name_lower for kw in book_kws):
            return False, "book_missing_keywords"
        if evidence_count < 1:
            return False, "book_insufficient_evidence"
            
    # ZOMBIE SPECIES / MUTATED CREATURE
    elif t_type in ["zombie_species", "mutated_creature"]:
        creature_kws = ["zombie", "xác sống", "biến thể", "quái vật", "sinh vật", "biến dị"]
        if not any(kw in name_lower for kw in creature_kws):
            return False, "creature_missing_keywords"
        if evidence_count < 1:
            return False, "creature_insufficient_evidence"
            
    # LOCATION BASE
    elif t_type == "location_base":
        loc_kws = ["căn cứ", "thành", "khu", "trạm", "bệnh viện", "trường", "kho", "căng tin", "tòa nhà", "nhà kho", "tầng hầm", "phòng điều hành"]
        is_named_loc = check_title_case(name) and len(words) >= 2
        if not (any(kw in name_lower for kw in loc_kws) or is_named_loc):
            return False, "location_missing_keywords_or_proper_name"
        if evidence_count < 2:
            return False, "location_insufficient_evidence"
            
    # ORGANIZATION FACTION
    elif t_type == "organization_faction":
        faction_kws = ["hội", "bang", "quân", "công ty", "tổ chức", "đội", "đoàn", "căn cứ"]
        is_named_fac = check_title_case(name) and len(words) >= 2
        if not (any(kw in name_lower for kw in faction_kws) or is_named_fac):
            return False, "faction_missing_keywords_or_proper_name"
        if evidence_count < 2:
            return False, "faction_insufficient_evidence"
            
    # WEAPON
    elif t_type == "weapon":
        weapon_kws = ["súng", "dao", "kiếm", "đao", "thương", "pháo", "vũ khí"]
        if not any(kw in name_lower for kw in weapon_kws):
            return False, "weapon_missing_keywords"
        if evidence_count < 1:
            return False, "weapon_insufficient_evidence"
            
    # ITEM
    elif t_type == "item":
        item_kws = ["vật phẩm", "trang bị", "dịch thể", "hộp thực phẩm", "thẻ triệu hồi", "thẻ giao dịch", "thẻ bài"]
        if not any(kw in name_lower for kw in item_kws) and not name_lower.startswith("thẻ"):
            return False, "item_missing_keywords"
        if evidence_count < 1:
            return False, "item_insufficient_evidence"
            
    return True, ""
