import re
from typing import List, Dict, Any, Tuple

VALID_V2_TYPES = {
    "character",
    "zombie_species",
    "mutated_creature",
    "location_base",
    "organization_faction",
    "weapon",
    "item",
    "crystal_core",
    "ability_skill",
    "skill_book",
    "event",
    "relationship",
    "chapter_summary"
}

def is_v2_type(type_str: str) -> bool:
    if not type_str:
        return False
    return type_str.lower().strip() in VALID_V2_TYPES

def detect_false_positive_type(name: str, current_type: str, evidence: List[Dict[str, Any]] = None) -> str:
    if not current_type:
        return "entity"
        
    c_type = current_type.lower().strip()
    name_clean = (name or "").strip()
    name_lower = name_clean.lower()
    
    if c_type == "organization_faction":
        # Reject generic/lowercase grouping phrases that were false positives
        if name_lower in ("đoàn đội", "đoàn ô", "đoàn đội đã", "đội ngũ", "đám đội"):
            return "entity"
            
    if c_type == "character":
        # Check if the name looks like an action or noise rather than a proper character name
        if any(kw in name_lower for kw in (" đang", " đứng", " để", " đầu", " đã", " tấn công", " tiến vào")):
            return "entity"
        # Purely lowercase characters are highly suspicious
        if name_clean and not any(c.isupper() for c in name_clean):
            return "entity"
            
    if c_type == "location_base":
        # Check for clothing or other items classified as locations
        if any(kw in name_lower for kw in ("áo khoác", "bình thuốc", "trang bị", "vật phẩm")):
            return "entity"
            
    return current_type

def classify_entity_candidate(name: str, evidence: List[Dict[str, Any]] = None, current_type: str = "entity") -> Dict[str, Any]:
    name_clean = (name or "").strip()
    name_lower = name_clean.lower()
    
    result = {
        "target_type": current_type,
        "action": "no_change",
        "reason": "already_v2_type" if current_type != "entity" else "uncertain"
    }

    # 1. False positive detection for non-entity types
    if current_type != "entity":
        fp_type = detect_false_positive_type(name_clean, current_type, evidence)
        if fp_type != current_type:
            result["target_type"] = fp_type
            # If it's a false positive organization like "đoàn đội", we want to classify it as noise
            if name_lower in ("đoàn đội", "đoàn ô", "đoàn đội đã", "đội ngũ", "đám đội"):
                result["action"] = "noise_candidate"
                result["reason"] = f"false_positive_noise_phrase: {current_type} -> noise"
            else:
                result["action"] = "update_type"
                result["reason"] = f"false_positive_reverted: {current_type} -> {fp_type}"
        return result

    # 2. Lowercase and generic noise phrase checks
    is_lowercase = False
    if name_clean and not name_clean.isupper():
        if not any(c.isupper() for c in name_clean):
            is_lowercase = True

    noise_keywords = [
        "đã", "đang", "đều", "đưa", "để", "ở", "này", "kia", "ấy", "đó",
        "tôi", "tao", "hắn", "nó", "họ", "chúng", "ta", "mình",
        "định đoạt", "đơn độc", "độc ác", "phập phập", "sau đây", "ý định",
        "đoàn đội", "đoàn ô", "đoàn đội đã", "đội ngũ", "đám đội"
    ]
    
    is_noise = is_lowercase
    if not is_noise:
        words = name_lower.split()
        if any(w in noise_keywords for w in words) or name_lower in noise_keywords:
            is_noise = True
        elif any(f" {kw}" in name_lower or f"{kw} " in name_lower for kw in (" đang", " đứng", " để", " đầu", " đã", " tấn công")):
            is_noise = True

    if is_noise:
        result["target_type"] = "entity"
        result["action"] = "noise_candidate"
        result["reason"] = "lowercase_or_generic_noise_phrase"
        return result

    # 3. Crystal core classification
    if any(kw in name_lower for kw in ("tinh thể", "tinh thạch", "tinh hạch", "nhân hạch")):
        result["target_type"] = "crystal_core"
        result["action"] = "update_type"
        result["reason"] = "crystal_core_keyword"
        return result

    # 4. Zombie species classification
    if any(kw in name_lower for kw in ("zombie", "xác sống", "biến thể", "biến dị")) or ("cấp" in name_lower and any(str(i) in name_lower for i in range(10))):
        result["target_type"] = "zombie_species"
        result["action"] = "update_type"
        result["reason"] = "zombie_or_species_keyword"
        return result

    # 5. Location base classification (excluding organization keywords)
    location_kws = ("căn cứ", "thành phố", "khu vực", "vùng an toàn", "bệnh viện", "nhà kho", "trường học")
    org_kws = ("hội", "bang", "quân đoàn", "tổ chức", "công ty", "đoàn", "đội", "đại thiên thần", "thế lực", "phái")
    if any(kw in name_lower for kw in location_kws) and not any(kw in name_lower for kw in org_kws):
        result["target_type"] = "location_base"
        result["action"] = "update_type"
        result["reason"] = "location_keyword"
        return result

    # 6. Organization faction classification
    if any(kw in name_lower for kw in org_kws):
        result["target_type"] = "organization_faction"
        result["action"] = "update_type"
        result["reason"] = "organization_keyword"
        return result

    # 7. Ability skill classification
    skill_kws = ("kỹ năng", "kỷ năng", "dị năng", "năng lực", "chiêu thức", "pháp quyết", "ấn tâm lực", "băng độc")
    if any(kw in name_lower for kw in skill_kws):
        result["target_type"] = "ability_skill"
        result["action"] = "update_type"
        result["reason"] = "ability_or_skill_keyword"
        return result

    # 8. Title-case without strong keywords -> manual review candidate (never auto-map to character bừa)
    if name_clean and name_clean[0].isupper():
        result["target_type"] = "entity"
        result["action"] = "manual_review"
        result["reason"] = "title_case_without_strong_keywords"
        return result

    return result

def build_entity_disambiguation_plan(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    plan = []
    for r in rows:
        r_id = r.get("id")
        name = r.get("name", "")
        old_type = r.get("type", "entity")
        evidence = r.get("evidence", [])
        
        classification = classify_entity_candidate(name, evidence=evidence, current_type=old_type)
        target_type = classification["target_type"]
        action = classification["action"]
        reason = classification["reason"]
        
        plan.append({
            "id": r_id,
            "name": name,
            "old_type": old_type,
            "new_type": target_type,
            "action": action,
            "reason": reason
        })
    return plan
