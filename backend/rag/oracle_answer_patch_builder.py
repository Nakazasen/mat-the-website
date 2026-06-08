from typing import List, Dict, Any
from backend.rag.oracle_feedback_classifier import classify_oracle_feedback

def normalize_query_pattern(question: str) -> str:
    """Normalizes question string for matching."""
    if not question:
        return ""
    # Lowercase, trim, collapse spaces, remove trailing punctuation
    import re
    val = question.strip().lower()
    val = re.sub(r"\s+", " ", val)
    val = re.sub(r"[?.\s]+$", "", val)
    return val

def build_oracle_patches(feedbacks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Groups classified feedbacks and builds candidate oracle answer patches.
    """
    # 1. Classify all feedbacks
    classified_feedbacks = []
    for row in feedbacks:
        # Only process feedbacks related to RAG (where question exists)
        if not row.get("question"):
            continue
            
        cls_res = classify_oracle_feedback(
            question=row.get("question"),
            answer=row.get("answer"),
            user_feedback=row.get("user_comment"),
            source=row.get("source"),
            chapter_progress=row.get("chapter_progress")
        )
        
        # Skip unknown classification if confidence is too low
        if cls_res["issue_type"] == "unknown":
            continue
            
        classified_feedbacks.append({
            "feedback_row": row,
            "classification": cls_res
        })

    # 2. Group by normalized query pattern + issue type
    groups = {}
    for item in classified_feedbacks:
        fb = item["feedback_row"]
        cls = item["classification"]
        
        q_norm = normalize_query_pattern(fb.get("question", ""))
        issue_type = cls["issue_type"]
        
        group_key = (q_norm, issue_type)
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(item)

    # 3. Compile patches from groups
    patches = []
    for (q_norm, issue_type), items in groups.items():
        first_item = items[0]
        cls = first_item["classification"]
        fb = first_item["feedback_row"]
        
        target_entity = cls["target_entity_or_intent"]
        suggested_policy = cls["suggested_policy_type"]
        
        confidence = sum(i["classification"]["confidence"] for i in items) / len(items)
        feedback_ids = [i["feedback_row"].get("id") for i in items if i["feedback_row"].get("id")]
        reasons = [i["feedback_row"].get("user_comment") for i in items if i["feedback_row"].get("user_comment")]
        
        # Determine status
        # If confidence is high and doesn't modify canon (which none of our patches do), auto-apply.
        # Otherwise, mark for needs_review
        status = "active"
        if confidence < 0.8:
            status = "needs_review"

        # Build policy json payload
        policy_payload = {}
        if suggested_policy == "prefer_chapter_summary_intent":
            policy_payload = {"prefer_chapter_summary": True, "suppress_entities": True}
        elif suggested_policy == "enrich_identity_answer_from_story_chunks":
            policy_payload = {"enrich_from_story_chunks": True, "target_entity": target_entity}
        elif suggested_policy == "suppress_irrelevant_entity_expansion":
            policy_payload = {"suppress_unrelated_entities": True, "target_entity": target_entity}
        elif suggested_policy == "force_exact_entity_lookup":
            policy_payload = {"force_exact": True, "target_entity": target_entity}
        elif suggested_policy == "clear_stale_cache":
            policy_payload = {"clear_cache": True, "target_entity": target_entity}
        elif suggested_policy == "answer_format_policy":
            policy_payload = {"add_warning_banner": True, "format_style": "default"}

        reason_str = f"Aggregated from {len(items)} feedbacks. Comments: {'; '.join(reasons[:3])}"

        patches.append({
            "issue_type": issue_type,
            "query_pattern": q_norm,
            "target_entity": target_entity if target_entity else None,
            "target_intent": "chapter_summary" if issue_type == "intent_misclassification" else None,
            "patch_type": suggested_policy,
            "policy": policy_payload,
            "effective_status": status,
            "confidence": round(confidence, 2),
            "source_feedback_ids": feedback_ids,
            "reason": reason_str
        })

    return patches
