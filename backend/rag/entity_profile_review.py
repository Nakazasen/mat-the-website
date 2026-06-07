"""
RAG Entity Profile Review Module
Provides validation, payload building, and reporting functionality
for missing entity profile drafts.
"""

import json
from typing import Any, Dict, List, Optional

VALID_ENTITY_TYPES = {"character", "item", "faction", "location", "concept", "unknown"}

def validate_entity_profile_draft(draft: Dict[str, Any]) -> Dict[str, Any]:
    """Validates a single missing entity profile draft, checking schema and safety."""
    errors = []
    warnings = []
    
    if not draft:
        errors.append("Draft is empty or None.")
        return {
            "valid": False,
            "eligible_insert": False,
            "errors": errors,
            "warnings": warnings,
            "draft": draft
        }
        
    # 1. Validate entity_name
    entity_name = draft.get("entity_name")
    if not entity_name:
        errors.append("Missing or empty field 'entity_name'.")
    elif not isinstance(entity_name, str) or not entity_name.strip():
        errors.append("Field 'entity_name' must be a non-empty string.")
        
    # 2. Validate entity_type
    entity_type = draft.get("entity_type")
    if not entity_type:
        errors.append("Missing or empty field 'entity_type'.")
    elif entity_type not in VALID_ENTITY_TYPES:
        errors.append(f"Invalid 'entity_type': '{entity_type}'. Must be one of {sorted(list(VALID_ENTITY_TYPES))}.")
        
    # 3. Validate status
    status = draft.get("status")
    if status not in {"draft", "needs_review"}:
        errors.append(f"Invalid 'status': '{status}'. Must be 'draft' or 'needs_review'.")
        
    # 4. Validate human_review_required
    human_review_required = draft.get("human_review_required")
    if human_review_required is not True:
        errors.append("Field 'human_review_required' must be True.")
        
    # 5. Validate evidence
    evidence = draft.get("evidence")
    if not isinstance(evidence, list):
        errors.append("Field 'evidence' must be a list.")
    else:
        # If status=draft, evidence cannot be empty
        if status == "draft" and len(evidence) == 0:
            errors.append("Field 'evidence' cannot be empty when status is 'draft'.")
        # If status=needs_review, evidence can be empty but has warning
        if status == "needs_review" and len(evidence) == 0:
            warnings.append("Status is 'needs_review' and evidence is empty.")
            
    valid = len(errors) == 0
    # eligible_insert logic: Không eligible nếu thiếu entity_name hoặc entity_type sai.
    has_name = bool(entity_name and isinstance(entity_name, str) and entity_name.strip())
    has_valid_type = bool(entity_type in VALID_ENTITY_TYPES)
    eligible_insert = has_name and has_valid_type
    
    return {
        "valid": valid,
        "eligible_insert": eligible_insert,
        "errors": errors,
        "warnings": warnings,
        "draft": draft
    }

def validate_entity_profile_drafts(drafts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validates a list of entity profile drafts, returning a dictionary of reports."""
    reports = [validate_entity_profile_draft(d) for d in drafts]
    return {
        "reports": reports,
        "valid_count": sum(1 for r in reports if r["valid"]),
        "invalid_count": sum(1 for r in reports if not r["valid"]),
        "eligible_insert_count": sum(1 for r in reports if r["eligible_insert"]),
    }

def build_entity_profile_correction_payload(draft: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Formats valid drafts to align with the database's 'rag_corrections' table schema."""
    report = validate_entity_profile_draft(draft)
    if not report["eligible_insert"]:
        return None
        
    d = report["draft"]
    proposed_content = json.dumps(d, ensure_ascii=False)
    
    return {
        "feedback_id": None,
        "entity_name": d.get("entity_name"),
        "correction_type": "entity_profile",
        "proposed_content": proposed_content,
        "evidence": d.get("evidence") or [],
        "status": "draft",
        "reviewer_note": "Generated from missing entity failure analysis; human review required."
    }

def summarize_entity_profile_review(drafts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregates review validation reports into statistics."""
    report_dict = validate_entity_profile_drafts(drafts)
    reports = report_dict["reports"]
    
    total = len(drafts)
    valid_count = report_dict["valid_count"]
    invalid_count = report_dict["invalid_count"]
    eligible_insert_count = report_dict["eligible_insert_count"]
    
    needs_review_count = 0
    with_evidence_count = 0
    warning_count = 0
    
    for r in reports:
        d = r["draft"]
        if d:
            if d.get("status") == "needs_review":
                needs_review_count += 1
            if isinstance(d.get("evidence"), list) and len(d["evidence"]) > 0:
                with_evidence_count += 1
        if r["warnings"]:
            warning_count += len(r["warnings"])
            
    return {
        "total": total,
        "valid": valid_count,
        "invalid": invalid_count,
        "eligible_insert": eligible_insert_count,
        "needs_review": needs_review_count,
        "with_evidence": with_evidence_count,
        "warnings": warning_count,
        "reports": reports
    }
