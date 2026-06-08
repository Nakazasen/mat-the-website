import re
from typing import List, Dict, Any

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

def normalize_library_type(name: str, current_type: str, source: str = None) -> str:
    if not current_type:
        return "item" # Standard fallback
        
    c_type = current_type.lower().strip()
    name_clean = (name or "").lower().strip()
    
    # 1. Legacy type direct mappings
    if c_type == "ability":
        return "ability_skill"
    if c_type == "faction":
        return "organization_faction"
    if c_type == "location":
        return "location_base"
    if c_type in ("book", "skillbook", "skill_book"):
        return "skill_book"
        
    # 2. Creature mapping
    if c_type == "creature":
        if "zombie" in name_clean or "xác sống" in name_clean:
            return "zombie_species"
        return "mutated_creature"
        
    # 3. Item crystal core mapping
    if c_type == "item":
        if any(kw in name_clean for kw in ("tinh thạch", "tinh thể", "tinh hạch", "nhân hạch")):
            return "crystal_core"
        return "item"
        
    # 4. Entity mappings (audited carefully)
    if c_type == "entity":
        if "zombie" in name_clean or "xác sống" in name_clean:
            return "zombie_species"
        if any(kw in name_clean for kw in ("căn cứ", "vùng an toàn", "khu vực")):
            return "location_base"
        if any(kw in name_clean for kw in ("đoàn", "bang", "phái", "tổ chức", "thế lực", "đại thiên thần", "hội")):
            return "organization_faction"
        if any(kw in name_clean for kw in ("tinh thạch", "tinh thể", "tinh hạch", "nhân hạch")):
            return "crystal_core"
        if any(kw in name_clean for kw in ("kỹ năng", "chiêu thức", "pháp quyết", "kỷ năng")):
            return "ability_skill"
        return "entity"
        
    # If already a valid V2 type, return as is
    if c_type in VALID_V2_TYPES:
        return c_type
        
    # Fallback for unknown categories
    return c_type

def build_type_normalization_plan(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    plan = []
    for r in rows:
        r_id = r.get("id")
        name = r.get("name", "")
        old_type = r.get("type", "")
        
        new_type = normalize_library_type(name, old_type, source=r.get("source"))
        needs_norm = old_type != new_type or not is_v2_type(old_type)
        
        if needs_norm:
            rule = f"{old_type} -> {new_type}"
        else:
            rule = "unchanged"
            
        plan.append({
            "id": r_id,
            "name": name,
            "old_type": old_type,
            "new_type": new_type,
            "needs_normalization": needs_norm,
            "rule_applied": rule
        })
    return plan
