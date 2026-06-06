"""
RAG Evaluation Case Registry Verification Module
Provides schema validation, source marking, and duplicate ID detection
for evaluation cases derived from user feedback.
"""

from typing import Any, Dict, List, Set

REQUIRED_FIELDS = {
    "id": str,
    "question": str,
    "chapter_progress": int,
    "intent": str,
    "expected_sources": list,
    "must_include": list,
    "must_not_include": list,
    "expected_chapters": list,
    "should_abstain": bool,
    "notes": str,
}

VALID_STATUSES = {"draft", "approved_for_eval"}

def validate_feedback_eval_case(case: Dict[str, Any]) -> Dict[str, Any]:
    """Validates schema, required fields, source markers, and status of a feedback-derived eval case."""
    errors = []
    warnings = []

    # 1. Validate ID prefix
    case_id = case.get("id")
    if not case_id:
        errors.append("Missing required field 'id'.")
    elif not isinstance(case_id, str) or not case_id.startswith("feedback_"):
        errors.append(f"Invalid 'id': '{case_id}'. Feedback-derived evaluation case IDs must start with 'feedback_'.")

    # 2. Required fields type check
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in case:
            errors.append(f"Missing required field '{field}'.")
        else:
            val = case[field]
            if not isinstance(val, expected_type):
                errors.append(f"Field '{field}' must be of type {expected_type.__name__}, got {type(val).__name__}.")

    # 3. Source check
    source = case.get("source")
    if not source:
        errors.append("Missing required field 'source'.")
    elif source != "generated_from_feedback":
        errors.append(f"Invalid 'source': '{source}'. Must be 'generated_from_feedback'.")

    # 4. Status check
    status = case.get("status")
    if not status:
        errors.append("Missing required field 'status'.")
    elif status not in VALID_STATUSES:
        errors.append(f"Invalid 'status': '{status}'. Must be one of {sorted(list(VALID_STATUSES))}.")

    # 5. Abstain notes check
    if case.get("should_abstain") is True:
        notes = case.get("notes", "")
        if not notes or len(str(notes).strip()) < 10:
            errors.append("Case has 'should_abstain' set to True, but lacks detailed explanatory notes (min 10 characters).")

    valid = len(errors) == 0
    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "case": case
    }

def validate_feedback_eval_cases(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Applies validation to a list of feedback eval cases."""
    return [validate_feedback_eval_case(c) for c in cases]

def detect_duplicate_eval_case_ids(base_cases: List[Dict[str, Any]], feedback_cases: List[Dict[str, Any]]) -> List[str]:
    """Detects duplicate IDs within feedback cases, and duplicates between base cases and feedback cases."""
    duplicates = set()
    seen_ids: Set[str] = set()

    # 1. Collect all base case IDs
    base_ids = {c.get("id") for c in base_cases if c.get("id")}

    # 2. Check within feedback cases
    for case in feedback_cases:
        cid = case.get("id")
        if not cid:
            continue

        # Check against base case IDs
        if cid in base_ids:
            duplicates.add(cid)

        # Check duplicate within feedback list
        if cid in seen_ids:
            duplicates.add(cid)
        else:
            seen_ids.add(cid)

    return sorted(list(duplicates))

def build_eval_registry_summary(base_cases: List[Dict[str, Any]], feedback_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compiles validation results and duplicate checks into a registry summary."""
    reports = validate_feedback_eval_cases(feedback_cases)
    duplicates = detect_duplicate_eval_case_ids(base_cases, feedback_cases)

    valid_count = sum(1 for r in reports if r["valid"])
    invalid_count = sum(1 for r in reports if not r["valid"])
    warnings_count = sum(1 for r in reports if r["warnings"])

    return {
        "base_cases_count": len(base_cases),
        "feedback_cases_count": len(feedback_cases),
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "warnings_count": warnings_count,
        "duplicate_ids": duplicates,
        "reports": reports
    }
