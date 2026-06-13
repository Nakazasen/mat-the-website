import os
import json
import pytest

BENCHMARK_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "evals",
    "chapter_bot_quality_cases_v1.json"
)

def test_benchmark_loader():
    assert os.path.exists(BENCHMARK_PATH), f"Benchmark file not found at {BENCHMARK_PATH}"

    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    assert isinstance(cases, list), "Benchmark must be a list of cases"
    assert len(cases) == 50, f"Expected exactly 50 cases, found {len(cases)}"

    categories = {
        "chapter_summary": 0,
        "character_question": 0,
        "event_causality_question": 0,
        "location_world_question": 0,
        "unavailable_out_of_scope": 0,
        "adversarial_ambiguous": 0
    }

    required_keys = {
        "case_id",
        "category",
        "question",
        "chapter_progress",
        "explicit_target_chapter",
        "allowed_chapter_range",
        "expected_chunk_refs",
        "required_facts",
        "optional_facts",
        "forbidden_facts",
        "important_event_clusters",
        "acceptable_abstain",
        "human_reference_answer"
    }

    for index, case in enumerate(cases):
        # Verify keys
        for key in required_keys:
            assert key in case, f"Case at index {index} (ID: {case.get('case_id')}) is missing required key '{key}'"

        cat = case.get("category")
        assert cat in categories, f"Invalid category '{cat}' at index {index} (ID: {case.get('case_id')})"
        categories[cat] += 1

    # Verify counts
    assert categories["chapter_summary"] == 15, f"Expected 15 chapter_summary cases, found {categories['chapter_summary']}"
    assert categories["character_question"] == 10, f"Expected 10 character_question cases, found {categories['character_question']}"
    assert categories["event_causality_question"] == 10, f"Expected 10 event_causality_question cases, found {categories['event_causality_question']}"
    assert categories["location_world_question"] == 5, f"Expected 5 location_world_question cases, found {categories['location_world_question']}"
    assert categories["unavailable_out_of_scope"] == 5, f"Expected 5 unavailable_out_of_scope cases, found {categories['unavailable_out_of_scope']}"
    assert categories["adversarial_ambiguous"] == 5, f"Expected 5 adversarial_ambiguous cases, found {categories['adversarial_ambiguous']}"

    print("\nBenchmark loader validation checks all PASSED!")
