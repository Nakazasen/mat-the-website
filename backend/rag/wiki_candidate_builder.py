"""
Wiki Candidate Builder Module
Provides functionality to parse, build, validate, and summarize wiki candidates
derived from approved RAG corrections.
"""

import json
from typing import Any, Dict, List

# Allowed canonical categories in wiki_entries
VALID_WIKI_CATEGORIES = ["Nhân vật", "Sinh vật", "Thế lực", "Vật phẩm", "Địa điểm"]

def map_entity_type_to_wiki_category(entity_type: str) -> str:
    """Maps a proposed entity_type to a canonical wiki_entries category."""
    if not entity_type:
        return "Sinh vật"  # Default fallback
        
    et_strip = str(entity_type).strip()
    
    # Direct case-insensitive match check with canonical categories
    for cat in VALID_WIKI_CATEGORIES:
        if cat.lower() == et_strip.lower():
            return cat
            
    # English lowercase key mapping
    mapping = {
        "character": "Nhân vật",
        "item": "Vật phẩm",
        "faction": "Thế lực",
        "location": "Địa điểm",
        "concept": "Sinh vật",
        "unknown": "Sinh vật"
    }
    return mapping.get(et_strip.lower(), "Sinh vật")

def parse_entity_profile_proposed_content(proposed_content: str) -> dict:
    """Safely parses proposed_content from corrections, handling JSON or raw strings."""
    if not proposed_content:
        return {}
    if isinstance(proposed_content, dict):
        return proposed_content
    try:
        data = json.loads(proposed_content)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, TypeError):
        pass
    return {"summary": "", "content": str(proposed_content)}

def build_wiki_candidate_from_correction(correction: dict) -> dict:
    """Transforms a raw correction dict from rag_corrections table into a wiki candidate payload."""
    if not correction:
        correction = {}
        
    correction_id = str(correction.get("id") or "")
    entity_name = correction.get("entity_name") or ""
    proposed_content_raw = correction.get("proposed_content") or ""
    
    parsed_content = parse_entity_profile_proposed_content(proposed_content_raw)
    
    # Map entity_type to category
    raw_type = parsed_content.get("entity_type") or correction.get("correction_type") or "unknown"
    entity_type = map_entity_type_to_wiki_category(raw_type)
    
    summary = str(parsed_content.get("summary") or "").strip()
    content = str(parsed_content.get("content") or "").strip()
    
    aliases = parsed_content.get("aliases")
    if not isinstance(aliases, list):
        aliases = []
        
    evidence = correction.get("evidence")
    
    # Status determination rules
    if not entity_name:
        status = "invalid"
    elif not isinstance(evidence, list):
        status = "invalid"
        evidence = []
    elif not summary or not content:
        status = "needs_human_fill"
    else:
        status = "ready_for_review"
        
    res = {
        "correction_id": correction_id,
        "entity_name": entity_name,
        "entity_type": entity_type,
        "summary": summary,
        "content": content,
        "aliases": aliases,
        "evidence": evidence,
        "source": "rag_corrections",
        "status": status,
        "human_review_required": True,
        "notes": "Generated from approved rag_corrections; not applied to wiki_entries."
    }
    if "canon_reviewed" in parsed_content:
        res["canon_reviewed"] = parsed_content["canon_reviewed"]
    if "canon_reviewed_at" in parsed_content:
        res["canon_reviewed_at"] = parsed_content["canon_reviewed_at"]

    return res

def validate_wiki_candidate(candidate: dict) -> dict:
    """Validates schema fields of a wiki candidate payload."""
    errors = []
    
    if not candidate:
        errors.append("Candidate is empty or None.")
        return {
            "valid": False,
            "status": "invalid",
            "errors": errors
        }
        
    entity_name = candidate.get("entity_name")
    if not entity_name or not isinstance(entity_name, str) or not entity_name.strip():
        errors.append("Field 'entity_name' is required and must be a non-empty string.")
        
    evidence = candidate.get("evidence")
    if evidence is None:
        errors.append("Field 'evidence' is required.")
    elif not isinstance(evidence, list):
        errors.append("Field 'evidence' must be a list.")
        
    status = candidate.get("status")
    allowed_statuses = {"ready_for_review", "needs_human_fill", "invalid"}
    if status not in allowed_statuses:
        errors.append(f"Field 'status' must be one of {allowed_statuses}.")
        
    valid = len(errors) == 0
    return {
        "valid": valid,
        "status": status if status in allowed_statuses else "invalid",
        "errors": errors
    }

def summarize_wiki_candidates(candidates: list[dict]) -> dict:
    """Aggregates a list of wiki candidates into status counts."""
    total = len(candidates)
    ready = sum(1 for c in candidates if c.get("status") == "ready_for_review")
    needs_fill = sum(1 for c in candidates if c.get("status") == "needs_human_fill")
    invalid = sum(1 for c in candidates if c.get("status") == "invalid")
    
    return {
        "total": total,
        "ready_for_review": ready,
        "needs_human_fill": needs_fill,
        "invalid": invalid
    }
