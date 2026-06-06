"""
RAG Correction Review Module
Provides validation, verification, payload building, and reporting functionality
for RAG correction drafts before database insertions.
"""

from typing import Any, Dict, List, Optional

VALID_CORRECTION_TYPES = {"wiki_update", "entity_profile", "eval_case", "retrieval_rule", "other"}

def validate_correction_draft(draft: Dict[str, Any]) -> Dict[str, Any]:
    """Validates a single correction draft, returning errors, warnings, and eligibility status."""
    errors = []
    warnings = []

    # 1. Validate feedback_id
    fb_id = draft.get("feedback_id")
    if not fb_id:
        errors.append("Missing required field 'feedback_id'.")
    elif not isinstance(fb_id, str) or not fb_id.strip():
        errors.append("Field 'feedback_id' must be a non-empty string.")

    # 2. Validate correction_type
    corr_type = draft.get("correction_type")
    if not corr_type:
        errors.append("Missing required field 'correction_type'.")
    elif corr_type not in VALID_CORRECTION_TYPES:
        errors.append(f"Invalid 'correction_type': '{corr_type}'. Must be one of {sorted(list(VALID_CORRECTION_TYPES))}.")

    # 3. Validate status
    status = draft.get("status")
    if status != "draft":
        errors.append(f"Invalid 'status': '{status}'. Correction drafts must have status 'draft'.")

    # 4. Validate proposed_content
    proposed = draft.get("proposed_content")
    if proposed is None or (isinstance(proposed, str) and not proposed.strip()):
        errors.append("Field 'proposed_content' cannot be empty.")
    elif isinstance(proposed, str) and proposed.strip() == "needs_review":
        warnings.append("Field 'proposed_content' is 'needs_review' and requires human input.")

    # 5. Validate evidence
    evidence = draft.get("evidence")
    if evidence is not None and not isinstance(evidence, list):
        errors.append("Field 'evidence' must be a list of citations.")

    valid = len(errors) == 0
    eligible_insert = valid

    return {
        "valid": valid,
        "eligible_insert": eligible_insert,
        "errors": errors,
        "warnings": warnings,
        "draft": draft
    }

def validate_correction_drafts(drafts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Applies validation to a list of correction drafts, returning a list of validation reports."""
    reports = []
    for d in drafts:
        reports.append(validate_correction_draft(d))
    return reports

def build_rag_correction_payload(draft: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Formats draft fields to align with the schema of the database's 'rag_corrections' table."""
    report = validate_correction_draft(draft)
    if not report["valid"]:
        return None

    d = report["draft"]
    return {
        "feedback_id": d.get("feedback_id"),
        "entity_name": d.get("entity_name"),
        "correction_type": d.get("correction_type"),
        "proposed_content": d.get("proposed_content"),
        "evidence": d.get("evidence") or [],
        "status": "draft",
        "reviewer_note": d.get("reviewer_note") or "Generated from accepted/resolved feedback; human review required."
    }

def summarize_correction_review(drafts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregates review validation reports into high-level statistics."""
    reports = validate_correction_drafts(drafts)

    total = len(drafts)
    valid_count = 0
    invalid_count = 0
    eligible_insert_count = 0
    warning_count = 0
    eval_cases_detected = 0

    for r in reports:
        if r["valid"]:
            valid_count += 1
        else:
            invalid_count += 1

        if r["eligible_insert"]:
            eligible_insert_count += 1

        if r["warnings"]:
            warning_count += 1

        if r["draft"].get("correction_type") == "eval_case":
            eval_cases_detected += 1

    return {
        "total": total,
        "valid": valid_count,
        "invalid": invalid_count,
        "eligible_insert": eligible_insert_count,
        "warnings": warning_count,
        "eval_cases_detected": eval_cases_detected,
        "reports": reports
    }
