import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Add parent directory and backend directory to path
sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend.rag.eval_case_registry import (
        validate_feedback_eval_case,
        validate_feedback_eval_cases,
        detect_duplicate_eval_case_ids,
        build_eval_registry_summary
    )
except ImportError:
    from rag.eval_case_registry import (
        validate_feedback_eval_case,
        validate_feedback_eval_cases,
        detect_duplicate_eval_case_ids,
        build_eval_registry_summary
    )

# 1. Test feedback eval case hợp lệ pass
def test_valid_feedback_eval_case():
    case = {
        "id": "feedback_uuid123",
        "question": "Hàn Phong là ai?",
        "chapter_progress": 10,
        "intent": "identity",
        "expected_sources": ["entity_context"],
        "must_include": ["Hàn Phong"],
        "must_not_include": [],
        "expected_chapters": [1],
        "should_abstain": False,
        "notes": "Testing notes here.",
        "source": "generated_from_feedback",
        "status": "draft"
    }
    report = validate_feedback_eval_case(case)
    assert report["valid"] is True
    assert len(report["errors"]) == 0

# 2. Test thiếu required field fail
def test_missing_required_field():
    case = {
        "id": "feedback_uuid123",
        "question": "Hàn Phong là ai?",
        # missing chapter_progress
        "intent": "identity",
        "expected_sources": [],
        "must_include": [],
        "must_not_include": [],
        "expected_chapters": [],
        "should_abstain": False,
        "notes": "Notes",
        "source": "generated_from_feedback",
        "status": "draft"
    }
    report = validate_feedback_eval_case(case)
    assert report["valid"] is False
    assert any("chapter_progress" in err for err in report["errors"])

# 3. Test duplicate id với base EVAL_CASES bị phát hiện
def test_duplicate_id_detection():
    base_cases = [
        {"id": "ident-01", "question": "Q1"},
        {"id": "ident-02", "question": "Q2"}
    ]
    feedback_cases = [
        # Duplicate with base case
        {"id": "ident-01", "question": "Q3"},
        # Duplicate within feedback cases
        {"id": "feedback_dup", "question": "Q4"},
        {"id": "feedback_dup", "question": "Q5"},
        # Unique case
        {"id": "feedback_unique", "question": "Q6"}
    ]
    duplicates = detect_duplicate_eval_case_ids(base_cases, feedback_cases)
    assert "ident-01" in duplicates
    assert "feedback_dup" in duplicates
    assert "feedback_unique" not in duplicates
    assert len(duplicates) == 2

# 4. Test source không phải generated_from_feedback bị fail
def test_invalid_source():
    case = {
        "id": "feedback_uuid123",
        "question": "Q",
        "chapter_progress": 1,
        "intent": "event",
        "expected_sources": [],
        "must_include": [],
        "must_not_include": [],
        "expected_chapters": [],
        "should_abstain": False,
        "notes": "Notes here",
        "source": "wrong_source",
        "status": "draft"
    }
    report = validate_feedback_eval_case(case)
    assert report["valid"] is False
    assert any("source" in err for err in report["errors"])

# 5. Test status invalid bị fail
def test_invalid_status():
    case = {
        "id": "feedback_uuid123",
        "question": "Q",
        "chapter_progress": 1,
        "intent": "event",
        "expected_sources": [],
        "must_include": [],
        "must_not_include": [],
        "expected_chapters": [],
        "should_abstain": False,
        "notes": "Notes here",
        "source": "generated_from_feedback",
        "status": "applied" # Invalid status
    }
    report = validate_feedback_eval_case(case)
    assert report["valid"] is False
    assert any("status" in err for err in report["errors"])

# 6. Test generated registry summary đếm đúng base_count, feedback_count, duplicates
def test_registry_summary():
    base_cases = [
        {"id": "ident-01"},
        {"id": "ident-02"}
    ]
    feedback_cases = [
        # Valid
        {
            "id": "feedback_1",
            "question": "Q",
            "chapter_progress": 1,
            "intent": "event",
            "expected_sources": [],
            "must_include": [],
            "must_not_include": [],
            "expected_chapters": [],
            "should_abstain": False,
            "notes": "Notes here",
            "source": "generated_from_feedback",
            "status": "draft"
        },
        # Invalid (missing intent)
        {
            "id": "feedback_2",
            "question": "Q",
            "chapter_progress": 1,
            "expected_sources": [],
            "must_include": [],
            "must_not_include": [],
            "expected_chapters": [],
            "should_abstain": False,
            "notes": "Notes here",
            "source": "generated_from_feedback",
            "status": "draft"
        }
    ]
    summary = build_eval_registry_summary(base_cases, feedback_cases)
    assert summary["base_cases_count"] == 2
    assert summary["feedback_cases_count"] == 2
    assert summary["valid_count"] == 1
    assert summary["invalid_count"] == 1

# 7. Test script không sửa eval_cases.py chính
@patch("sys.argv", ["review_feedback_eval_cases.py", "--input", "backend/rag/generated_feedback_corrections.json", "--output", "backend/rag/generated_feedback_eval_cases.py", "--json"])
def test_script_does_not_modify_base_cases():
    try:
        from backend.scripts.review_feedback_eval_cases import main as script_main
    except ImportError:
        from scripts.review_feedback_eval_cases import script_main

    eval_cases_path = "backend/rag/eval_cases.py"

    # Store original stat of eval_cases.py
    orig_mtime = os.path.getmtime(eval_cases_path)

    with patch("sys.stdout") as mock_stdout:
        script_main()

    # Check that mtime is not changed (meaning script didn't touch/modify the file)
    assert os.path.getmtime(eval_cases_path) == orig_mtime

# 8. Test generated_feedback_eval_cases.py import được nếu output được tạo
def test_import_generated_eval_cases():
    output_path = "backend/rag/generated_feedback_eval_cases.py"
    if os.path.exists(output_path):
        try:
            # Add backend to path and import dynamically
            if "backend" not in sys.path:
                sys.path.append(os.path.join(os.getcwd(), 'backend'))

            # Import dynamically
            import importlib
            # Try backend.rag.generated_feedback_eval_cases or rag.generated_feedback_eval_cases
            try:
                mod = importlib.import_module("backend.rag.generated_feedback_eval_cases")
            except ImportError:
                mod = importlib.import_module("rag.generated_feedback_eval_cases")

            assert hasattr(mod, "FEEDBACK_EVAL_CASES")
            assert isinstance(mod.FEEDBACK_EVAL_CASES, list)
        except Exception as e:
            pytest.fail(f"Failed to import generated feedback eval cases module: {e}")
