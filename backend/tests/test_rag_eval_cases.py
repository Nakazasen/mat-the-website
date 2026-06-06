import pytest

def test_rag_eval_cases_loadable():
    """Verify that the evaluation cases module can be imported and contains a valid list."""
    from backend.rag.eval_cases import EVAL_CASES
    assert isinstance(EVAL_CASES, list)
    assert len(EVAL_CASES) >= 80


def test_rag_eval_cases_required_fields():
    """Verify that every evaluation case contains all required schema fields with correct types."""
    from backend.rag.eval_cases import EVAL_CASES
    
    required_fields = {
        "id": str,
        "question": str,
        "chapter_progress": int,
        "intent": str,
        "expected_sources": list,
        "must_include": list,
        "must_not_include": list,
        "expected_chapters": list,
        "should_abstain": bool,
        "notes": str
    }
    
    for idx, case in enumerate(EVAL_CASES):
        case_id = case.get("id", f"index_{idx}")
        
        # Check presence of all required fields
        for field, field_type in required_fields.items():
            assert field in case, f"Case {case_id} is missing required field: '{field}'"
            assert isinstance(case[field], field_type), f"Case {case_id} field '{field}' must be of type {field_type.__name__}"


def test_rag_eval_cases_intent_coverage():
    """Verify that all 8 required intents are present in the benchmark suite."""
    from backend.rag.eval_cases import EVAL_CASES
    
    expected_intents = {
        "identity",
        "event",
        "summary",
        "relationship",
        "ability",
        "location",
        "no_data",
        "anti_spoiler"
    }
    
    found_intents = set()
    for case in EVAL_CASES:
        found_intents.add(case["intent"])
        
    missing_intents = expected_intents - found_intents
    assert not missing_intents, f"Benchmark suite is missing intents: {missing_intents}"


def test_rag_eval_cases_intent_counts():
    """Verify the distribution and minimum case requirements for each intent."""
    from backend.rag.eval_cases import EVAL_CASES
    
    counts = {}
    for case in EVAL_CASES:
        intent = case["intent"]
        counts[intent] = counts.get(intent, 0) + 1
        
    # Minimum requirements check
    assert counts.get("identity", 0) >= 15, f"Expected >= 15 identity cases, found {counts.get('identity', 0)}"
    assert counts.get("event", 0) >= 15, f"Expected >= 15 event cases, found {counts.get('event', 0)}"
    assert counts.get("summary", 0) >= 10, f"Expected >= 10 summary cases, found {counts.get('summary', 0)}"
    assert counts.get("relationship", 0) >= 10, f"Expected >= 10 relationship cases, found {counts.get('relationship', 0)}"
    assert counts.get("ability", 0) >= 10, f"Expected >= 10 ability cases, found {counts.get('ability', 0)}"
    assert counts.get("location", 0) >= 10, f"Expected >= 10 location cases, found {counts.get('location', 0)}"
    assert counts.get("no_data", 0) >= 10, f"Expected >= 10 no-data cases, found {counts.get('no_data', 0)}"
    assert counts.get("anti_spoiler", 0) >= 10, f"Expected >= 10 anti-spoiler cases, found {counts.get('anti_spoiler', 0)}"


def test_rag_eval_cases_anti_spoiler_rules():
    """Verify that all anti-spoiler cases have valid chapter_progress constraint."""
    from backend.rag.eval_cases import EVAL_CASES
    
    for case in EVAL_CASES:
        if case["intent"] == "anti_spoiler":
            assert case["chapter_progress"] >= 1, f"Anti-spoiler case {case['id']} must have a valid chapter_progress constraint."


def test_rag_eval_cases_no_data_rules():
    """Verify that all no-data cases require abstaining from answering."""
    from backend.rag.eval_cases import EVAL_CASES
    
    for case in EVAL_CASES:
        if case["intent"] == "no_data":
            assert case["should_abstain"] is True, f"No-data case {case['id']} must have should_abstain set to True."


def test_rag_eval_cases_identity_source_rules():
    """Verify that identity questions specify entity_context or wiki_entries as expected sources."""
    from backend.rag.eval_cases import EVAL_CASES
    
    for case in EVAL_CASES:
        if case["intent"] == "identity":
            sources = case["expected_sources"]
            assert "entity_context" in sources or "wiki_entries" in sources, \
                f"Identity case {case['id']} expected_sources must include 'entity_context' or 'wiki_entries'."
