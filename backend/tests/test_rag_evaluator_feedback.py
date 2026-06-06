import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Path resolution
sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.rag.evaluator import load_eval_cases, evaluate_all_cases

def test_load_eval_cases_base():
    """Verify that load_eval_cases('base') returns base cases."""
    cases = load_eval_cases("base")
    assert len(cases) > 0
    # Every base case shouldn't have source == "generated_from_feedback"
    for c in cases:
        assert c.get("source") != "generated_from_feedback"

def test_load_eval_cases_feedback():
    """Verify that load_eval_cases('feedback') returns feedback-derived cases."""
    cases = load_eval_cases("feedback")
    assert len(cases) >= 1
    for c in cases:
        assert c.get("source") == "generated_from_feedback"
        assert c.get("id").startswith("feedback_")

def test_load_eval_cases_all():
    """Verify that load_eval_cases('all') returns combination of both."""
    base_cases = load_eval_cases("base")
    feedback_cases = load_eval_cases("feedback")
    all_cases = load_eval_cases("all")
    assert len(all_cases) == len(base_cases) + len(feedback_cases)

def test_no_duplicate_ids_between_base_and_feedback():
    """Verify there are no duplicate IDs between base and feedback cases."""
    base_cases = load_eval_cases("base")
    feedback_cases = load_eval_cases("feedback")
    base_ids = {c["id"] for c in base_cases if "id" in c}
    feedback_ids = {c["id"] for c in feedback_cases if "id" in c}
    
    duplicates = base_ids.intersection(feedback_ids)
    assert len(duplicates) == 0, f"Found duplicate IDs: {duplicates}"

def test_feedback_cases_keep_source_marker():
    """Verify that feedback cases in registry maintain source='generated_from_feedback'."""
    feedback_cases = load_eval_cases("feedback")
    for c in feedback_cases:
        assert c.get("source") == "generated_from_feedback"

def test_load_eval_cases_missing_feedback_fallback():
    """Verify that load_eval_cases does not crash and falls back to [] if feedback registry raises exception."""
    # We patch sys.modules so that attempting to import backend.rag.generated_feedback_eval_cases raises ImportError
    with patch.dict("sys.modules", {
        "backend.rag.generated_feedback_eval_cases": None,
        "rag.generated_feedback_eval_cases": None
    }):
        cases = load_eval_cases("feedback")
        assert cases == []

def test_cli_parser_accepts_case_source():
    """Verify that CLI parser accepts --case-source and passes it to run_evaluation."""
    from backend.scripts.evaluate_rag_retrieval import main as cli_main
    with patch("sys.argv", ["evaluate_rag_retrieval.py", "--case-source", "all", "--limit", "1"]), \
         patch("backend.scripts.evaluate_rag_retrieval.run_evaluation") as mock_run:
        cli_main()
        assert mock_run.called
        args = mock_run.call_args[0][0]
        assert args.case_source == "all"

@pytest.mark.asyncio
async def test_evaluator_summary_has_case_source():
    """Verify evaluator summary returns case_source, feedback_cases_count, and duplicate_ids."""
    cases = [
        {
            "id": "feedback_test",
            "intent": "event",
            "question": "test question",
            "chapter_progress": 1,
            "expected_sources": [],
            "must_include": [],
            "must_not_include": [],
            "expected_chapters": [],
            "should_abstain": False,
            "notes": "",
            "source": "generated_from_feedback"
        }
    ]
    with patch("backend.rag.evaluator.evaluate_case_retrieval", return_value={"id": "feedback_test", "intent": "event", "passed": True, "fail_reasons": []}):
        summary = await evaluate_all_cases(cases, supabase=None, case_source="feedback")
        assert summary["case_source"] == "feedback"
        assert summary["feedback_cases_count"] == 1
        assert summary["duplicate_ids"] == []
