import os
from typing import Any, Dict, List

def analyze_evaluation_failures(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes RAG evaluator failures, groups them by reason, intent, identifies top missing entities,
    and provides action recommendations.
    """
    results_list = results.get("results", [])
    duplicate_ids = results.get("duplicate_ids", [])
    
    total_failures = 0
    feedback_failures = 0
    
    by_reason = {
        "missing_entity_context": 0,
        "expected_chapter_not_retrieved": 0,
        "no_chunks_retrieved": 0,
        "anti_spoiler_violation": 0,
        "no_data_should_abstain_but_retrieved": 0,
        "source_mismatch": 0,
        "intent_detection_mismatch": 0,
        "duplicate_id": 0,
        "unknown": 0
    }
    
    by_intent = {}
    missing_entities_map = {}
    
    # Process duplicate IDs first
    if duplicate_ids:
        by_reason["duplicate_id"] += len(duplicate_ids)
        
    for res in results_list:
        if res.get("passed", False):
            continue
            
        total_failures += 1
        
        # Check if feedback failure
        case_id = res.get("id", "")
        # A case is feedback-derived if it has 'source' == 'generated_from_feedback' or its ID starts with 'feedback_'
        is_feedback = res.get("source") == "generated_from_feedback" or str(case_id).startswith("feedback_")
        if is_feedback:
            feedback_failures += 1
            
        # Group by intent
        intent = res.get("intent", "unknown")
        by_intent[intent] = by_intent.get(intent, 0) + 1
        
        fail_reasons = res.get("fail_reasons", [])
        chunks_used = res.get("chunks_used", 0)
        
        # Track categories mapped in this case to avoid double counting
        reasons_found = set()
        
        # Check if no chunks retrieved when data is expected
        has_abstain_fail = any("Expected abstain" in r for r in fail_reasons)
        if chunks_used == 0 and not has_abstain_fail:
            reasons_found.add("no_chunks_retrieved")
            
        # Check if missing entity profile
        has_missing_entity = False
        if res.get("missing_entity_context", False):
            reasons_found.add("missing_entity_context")
            has_missing_entity = True
        
        for reason in fail_reasons:
            if "Spoiler detected" in reason:
                reasons_found.add("anti_spoiler_violation")
            elif "Intent is identity but" in reason or "is_identity_question" in reason:
                reasons_found.add("intent_detection_mismatch")
            elif "Expected abstain" in reason or "should_abstain=True" in reason or "weak_match_should_abstain" in reason or "no_data_should_abstain_but_retrieved" in reason:
                reasons_found.add("no_data_should_abstain_but_retrieved")
            elif "No matching expected chapters" in reason:
                reasons_found.add("expected_chapter_not_retrieved")
            elif "Expected source 'entity_context'" in reason or "Expected source 'wiki_entries'" in reason:
                reasons_found.add("missing_entity_context")
                has_missing_entity = True
            elif "Expected source" in reason:
                reasons_found.add("source_mismatch")
            elif "weak_match_retrieved" in reason:
                reasons_found.add("no_chunks_retrieved")
                
        if has_missing_entity:
            ent_name = res.get("entity_name")
            if ent_name:
                missing_entities_map[ent_name] = missing_entities_map.get(ent_name, 0) + 1
                
        # If no categories matched but we have fail reasons
        if not reasons_found and fail_reasons:
            reasons_found.add("unknown")
            
        # Increment by_reason counts
        for r in reasons_found:
            if r in by_reason:
                by_reason[r] += 1
                
    # Sort top missing entities by count descending
    top_missing_entities = [
        {"entity": name, "count": count}
        for name, count in sorted(missing_entities_map.items(), key=lambda x: x[1], reverse=True)
    ]
    
    # Generate recommendations
    recommended_next_actions = []
    if by_reason.get("missing_entity_context", 0) > 0:
        recommended_next_actions.append("Add missing entity profiles to wiki_entries table.")
    if by_reason.get("expected_chapter_not_retrieved", 0) > 0 or by_reason.get("no_chunks_retrieved", 0) > 0:
        recommended_next_actions.append("Improve hybrid lexical retrieval logic and check chunk indexing.")
    if by_reason.get("anti_spoiler_violation", 0) > 0:
        recommended_next_actions.append("Debug spoiler protection logic in search_story_chunks_hybrid_lexical.")
    if by_reason.get("no_data_should_abstain_but_retrieved", 0) > 0:
        recommended_next_actions.append("Refine abstain threshold and search matching rules.")
    if by_reason.get("duplicate_id", 0) > 0:
        recommended_next_actions.append("Resolve duplicate evaluation case IDs.")
        
    return {
        "total_failures": total_failures,
        "by_reason": by_reason,
        "by_intent": by_intent,
        "feedback_failures": feedback_failures,
        "top_missing_entities": top_missing_entities,
        "recommended_next_actions": recommended_next_actions
    }
