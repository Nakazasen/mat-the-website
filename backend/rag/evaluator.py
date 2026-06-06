"""
RAG Evaluator Module
Provides retrieval and anti-spoiler evaluation for benchmark cases without calling LLM.
"""

from typing import Any, List, Dict
from backend.routes.ai_oracle import is_identity_question, get_entity_context_for_oracle
from backend.rag.retrieval import search_story_chunks_hybrid_lexical
from backend.rag.context_builder import build_rag_context_block

async def evaluate_case_retrieval(case: Dict[str, Any], supabase: Any = None) -> Dict[str, Any]:
    """
    Evaluates a single benchmark case against the current retrieval and context builder pipeline.
    """
    case_id = case.get("id", "unknown")
    intent = case.get("intent", "unknown")
    question = case.get("question", "")
    chapter_progress = case.get("chapter_progress", 9999)
    expected_sources = case.get("expected_sources", [])
    expected_chapters = case.get("expected_chapters", [])
    should_abstain = case.get("should_abstain", False)

    fail_reasons = []
    sources_observed = []
    retrieved_chapters = []
    chunks_used = 0

    # 1. Identity intent validation & entity name extraction
    is_identity = is_identity_question(question)
    entity_name = None
    missing_entity_context = False
    suggestion = None

    if is_identity or intent == "identity":
        from backend.routes.ai_oracle import extract_entity_name
        entity_name = extract_entity_name(question)

    if intent == "identity":
        if not is_identity:
            fail_reasons.append(f"Intent is identity but is_identity_question returned False.")

        # Try to retrieve entity profile from wiki
        has_profile = False
        if supabase:
            entity_res = await get_entity_context_for_oracle(supabase, question, chapter_progress)
            if entity_res and entity_res.get("context_text"):
                sources_observed.append("entity_context")
                sources_observed.append("wiki_entries")
                has_profile = True

        if not has_profile:
            missing_entity_context = True
            if entity_name:
                suggestion = f"add wiki_entries profile for {entity_name}"

    # 2. General story chunks retrieval
    if supabase and question:
        results = search_story_chunks_hybrid_lexical(
            supabase=supabase,
            query=question,
            chapter_cap=chapter_progress,
            limit=5
        )
        context_data = build_rag_context_block(results, max_chunks=4)
        chunks_used = context_data.get("chunks_used", 0)

        if chunks_used > 0:
            sources_observed.append("story_chunks")

        citations = context_data.get("citations", [])
        for cit in citations:
            ch_num = cit.get("chapter_number")
            if ch_num is not None:
                retrieved_chapters.append(ch_num)

        retrieved_chapters = sorted(list(set(retrieved_chapters)))

        # Check spoiler protection
        for cit in citations:
            ch_num = cit.get("chapter_number")
            if ch_num is not None and ch_num > chapter_progress:
                fail_reasons.append(f"Spoiler detected: chapter {ch_num} > chapter_progress {chapter_progress}")

    # Deduplicate observed sources
    sources_observed = sorted(list(set(sources_observed)))

    # 3. Abstain rules verification
    if should_abstain:
        if chunks_used > 0:
            fail_reasons.append(f"Expected abstain (should_abstain=True) but chunks_used was {chunks_used}.")

    # 4. Expected chapters validation (if shouldn't abstain and expected_chapters is provided)
    if not should_abstain and expected_chapters:
        overlap = set(expected_chapters) & set(retrieved_chapters)
        if not overlap:
            fail_reasons.append(f"No matching expected chapters. Expected {expected_chapters}, got {retrieved_chapters}.")

    # 5. Expected sources validation
    if expected_sources:
        for src in expected_sources:
            if src == "entity_context" or src == "wiki_entries":
                if "entity_context" not in sources_observed and "wiki_entries" not in sources_observed:
                    fail_reasons.append(f"Expected source '{src}' was not retrieved.")
            elif src not in sources_observed:
                fail_reasons.append(f"Expected source '{src}' was not retrieved.")

    passed = len(fail_reasons) == 0

    res = {
        "id": case_id,
        "intent": intent,
        "passed": passed,
        "chunks_used": chunks_used,
        "retrieved_chapters": retrieved_chapters,
        "expected_chapters": expected_chapters,
        "sources_observed": sources_observed,
        "fail_reasons": fail_reasons
    }

    if intent == "identity" or is_identity:
        res["entity_name"] = entity_name
        res["expected_sources"] = expected_sources
        res["missing_entity_context"] = missing_entity_context
        if suggestion:
            res["suggestion"] = suggestion

    return res

def load_eval_cases(case_source: str = "base") -> List[Dict[str, Any]]:
    """
    Loads evaluation cases from registry files based on the specified source.
    """
    # Import base cases
    try:
        from backend.rag.eval_cases import EVAL_CASES
    except ImportError:
        try:
            from rag.eval_cases import EVAL_CASES
        except ImportError:
            EVAL_CASES = []

    # Import feedback cases safely (fall back to [] on any error)
    try:
        from backend.rag.generated_feedback_eval_cases import FEEDBACK_EVAL_CASES
    except Exception:
        try:
            from rag.generated_feedback_eval_cases import FEEDBACK_EVAL_CASES
        except Exception:
            FEEDBACK_EVAL_CASES = []

    # Copy list items to prevent mutation
    base_copied = [dict(c) for c in EVAL_CASES]
    feedback_copied = [dict(c) for c in FEEDBACK_EVAL_CASES]

    if case_source == "base":
        return base_copied
    elif case_source == "feedback":
        return feedback_copied
    elif case_source == "all":
        return base_copied + feedback_copied
    else:
        raise ValueError(f"Invalid case_source: {case_source}. Must be one of 'base', 'feedback', 'all'.")

async def evaluate_all_cases(cases: List[Dict[str, Any]], supabase: Any = None, case_source: str = "base") -> Dict[str, Any]:
    """
    Evaluates all given benchmark cases and aggregates results.
    """
    results = []
    passed_count = 0
    failed_count = 0

    # Intent tracking statistics
    by_intent = {}

    failures = []

    for case in cases:
        res = await evaluate_case_retrieval(case, supabase)
        results.append(res)

        intent = res["intent"]
        if intent not in by_intent:
            by_intent[intent] = {"total": 0, "passed": 0, "pass_rate": 0.0}

        by_intent[intent]["total"] += 1

        if res["passed"]:
            passed_count += 1
            by_intent[intent]["passed"] += 1
        else:
            failed_count += 1
            failures.append({
                "id": res["id"],
                "question": case.get("question", ""),
                "fail_reasons": res["fail_reasons"]
            })

    # Calculate pass rates
    total = len(cases)
    pass_rate = passed_count / total if total > 0 else 0.0

    for intent, stats in by_intent.items():
        stats["pass_rate"] = stats["passed"] / stats["total"] if stats["total"] > 0 else 0.0

    # Count cases generated from feedback
    feedback_cases_count = sum(1 for c in cases if c.get("source") == "generated_from_feedback")

    # Detect duplicate IDs in the current cases list
    seen_ids = set()
    duplicate_ids = set()
    for case in cases:
        cid = case.get("id")
        if cid:
            if cid in seen_ids:
                duplicate_ids.add(cid)
            else:
                seen_ids.add(cid)
    duplicate_ids_list = sorted(list(duplicate_ids))

    summary = {
        "case_source": case_source,
        "total": total,
        "passed": passed_count,
        "failed": failed_count,
        "pass_rate": pass_rate,
        "by_intent": by_intent,
        "failures": failures,
        "results": results,
        "duplicate_ids": duplicate_ids_list
    }

    if case_source in ("feedback", "all"):
        summary["feedback_cases_count"] = feedback_cases_count

    return summary
