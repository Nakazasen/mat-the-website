import os
import json
import pytest

BENCHMARK_V1_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "evals",
    "chapter_bot_quality_cases_v1.json"
)

BENCHMARK_V2_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "evals",
    "chapter_bot_quality_cases_v2_pro_reviewed.json"
)

def validate_benchmark(path, is_v2=False):
    assert os.path.exists(path), f"Benchmark file not found at {path}"

    with open(path, "r", encoding="utf-8") as f:
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

    if is_v2:
        required_keys.update({"gold_version", "gold_review_status", "invalidated_v1_facts", "soft_scoring_facts", "gold_evidence_refs"})

    case_ids = set()

    for index, case in enumerate(cases):
        # Verify keys
        for key in required_keys:
            assert key in case, f"Case at index {index} (ID: {case.get('case_id')}) is missing required key '{key}'"

        cat = case.get("category")
        assert cat in categories, f"Invalid category '{cat}' at index {index} (ID: {case.get('case_id')})"
        categories[cat] += 1
        case_ids.add(case["case_id"])

    # Verify counts
    assert categories["chapter_summary"] == 15, f"Expected 15 chapter_summary cases, found {categories['chapter_summary']}"
    assert categories["character_question"] == 10, f"Expected 10 character_question cases, found {categories['character_question']}"
    assert categories["event_causality_question"] == 10, f"Expected 10 event_causality_question cases, found {categories['event_causality_question']}"
    assert categories["location_world_question"] == 5, f"Expected 5 location_world_question cases, found {categories['location_world_question']}"
    assert categories["unavailable_out_of_scope"] == 5, f"Expected 5 unavailable_out_of_scope cases, found {categories['unavailable_out_of_scope']}"
    assert categories["adversarial_ambiguous"] == 5, f"Expected 5 adversarial_ambiguous cases, found {categories['adversarial_ambiguous']}"

    assert len(case_ids) == 50, "Duplicate case IDs found"
    return case_ids

def test_benchmark_loader_v1():
    validate_benchmark(BENCHMARK_V1_PATH, is_v2=False)

def test_benchmark_loader_v2():
    ids_v1 = validate_benchmark(BENCHMARK_V1_PATH, is_v2=False)
    ids_v2 = validate_benchmark(BENCHMARK_V2_PATH, is_v2=True)
    assert ids_v1 == ids_v2, "Case IDs changed between V1 and V2"
