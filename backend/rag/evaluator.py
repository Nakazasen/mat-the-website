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
    
    # 1. Identity intent validation
    is_identity = is_identity_question(question)
    if intent == "identity":
        if not is_identity:
            fail_reasons.append(f"Intent is identity but is_identity_question returned False.")
        
        # Try to retrieve entity profile from wiki
        if supabase:
            entity_res = await get_entity_context_for_oracle(supabase, question, chapter_progress)
            if entity_res and entity_res.get("context_text"):
                sources_observed.append("entity_context")
                sources_observed.append("wiki_entries")
    
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
    
    return {
        "id": case_id,
        "intent": intent,
        "passed": passed,
        "chunks_used": chunks_used,
        "retrieved_chapters": retrieved_chapters,
        "expected_chapters": expected_chapters,
        "sources_observed": sources_observed,
        "fail_reasons": fail_reasons
    }

async def evaluate_all_cases(cases: List[Dict[str, Any]], supabase: Any = None) -> Dict[str, Any]:
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
        
    return {
        "total": total,
        "passed": passed_count,
        "failed": failed_count,
        "pass_rate": pass_rate,
        "by_intent": by_intent,
        "failures": failures
    }
