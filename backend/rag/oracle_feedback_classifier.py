import re
from typing import Dict, List, Any

def extract_entity_name_simple(question: str) -> str:
    """Extract potential entity/character name from an identity question."""
    q = question.strip()
    q = re.sub(r"[?\s]+$", "", q)
    q_lower = q.lower()

    suffixes = [
        " là vật phẩm gì", " la vat pham gi",
        " là thực thể gì", " la thuc the gi",
        " là sinh vật gì", " la sinh vat gi",
        " là nhân vật nào", " la nhan vat nao",
        " là tổ chức gì", " la to chuc gi",
        " là kỹ năng gì", " la ky nang gi",
        " là ai", " la ai",
        " là gì", " la gi"
    ]
    for suffix in suffixes:
        if q_lower.endswith(suffix):
            return q[:-len(suffix)].strip()

    prefixes = [
        "thông tin về ", "thong tin ve ",
        "giới thiệu ", "gioi thieu ",
        "nhân vật ", "nhan vat ",
        "ai là ", "ai la "
    ]
    for prefix in prefixes:
        if q_lower.startswith(prefix):
            return q[len(prefix):].strip()

    return q

def classify_oracle_feedback(
    question: str,
    answer: str,
    user_feedback: str,
    source: str = None,
    chapter_progress: int = None
) -> Dict[str, Any]:
    """
    Classifies RAG feedback into specific RAG issue categories without using LLM/embeddings.
    Heuristics based on keywords and Vietnamese phrases.
    """
    q_val = (question or "").strip()
    ans_val = (answer or "").strip()
    fb_val = (user_feedback or "").strip()
    fb_lower = fb_val.lower()
    q_lower = q_val.lower()
    ans_lower = ans_val.lower()

    # Default output structure
    issue_type = "unknown"
    target_entity_or_intent = ""
    severity = "medium"
    suggested_policy_type = "answer_format_policy"
    evidence_terms = []
    confidence = 0.5

    # 1. intent_misclassification / wrong_chapter_summary
    # E.g. Question about chapter summary but RAG answers with entities,
    # or user explicitly complains about chapter contents vs character/organization info.
    is_chapter_q = any(w in q_lower for w in ["nội dung chương", "tóm tắt chương", "chương này", "diễn biến chương"])
    complained_about_intent = any(w in fb_lower for w in ["linh tinh", "sai ý", "nhầm", "nhân vật", "tổ chức", "tóm tắt"])
    
    if is_chapter_q and (complained_about_intent or "[chưa có mục định danh chính xác]" in ans_lower):
        issue_type = "intent_misclassification"
        target_entity_or_intent = "chapter_summary"
        severity = "high"
        suggested_policy_type = "prefer_chapter_summary_intent"
        evidence_terms = [w for w in ["nội dung chương", "tóm tắt", "linh tinh", "chương"] if w in fb_lower or w in q_lower]
        confidence = 0.95
        
    # 2. answer_quality_too_shallow
    # E.g. "sơ sài", "máy móc", "quá ngắn", "không đủ thông tin"
    elif any(w in fb_lower for w in ["sơ sài", "máy móc", "quá ngắn", "không đủ thông tin", "thiếu chi tiết", "chưa sâu", "sơ lược"]):
        issue_type = "answer_quality_too_shallow"
        target_entity_or_intent = extract_entity_name_simple(q_val)
        severity = "medium"
        suggested_policy_type = "enrich_identity_answer_from_story_chunks"
        evidence_terms = [w for w in ["sơ sài", "máy móc", "quá ngắn", "không đủ thông tin", "sơ lược"] if w in fb_lower]
        confidence = 0.9
        
    # 3. irrelevant_entities
    # E.g. Answer lists entities that are completely unrelated to the target question.
    elif any(w in fb_lower for w in ["không liên quan", "linh tinh", "lan man", "nhầm", "thêm nhân vật khác", "đưa thêm"]):
        issue_type = "irrelevant_entities"
        target_entity_or_intent = extract_entity_name_simple(q_val)
        severity = "medium"
        suggested_policy_type = "suppress_irrelevant_entity_expansion"
        evidence_terms = [w for w in ["không liên quan", "linh tinh", "lan man", "đưa thêm"] if w in fb_lower]
        confidence = 0.85
        
    # 4. missing_exact_entity
    # E.g. "chưa có mục định danh chính xác"
    elif "[chưa có mục định danh chính xác]" in ans_lower or any(w in fb_lower for w in ["chưa định danh", "không tìm thấy", "chưa có mục"]):
        issue_type = "missing_exact_entity"
        target_entity_or_intent = extract_entity_name_simple(q_val)
        severity = "high"
        suggested_policy_type = "force_exact_entity_lookup"
        evidence_terms = ["[chưa có mục định danh chính xác]"]
        confidence = 0.9
        
    # 5. stale_cache
    # E.g. source == cache and user says it is old/stale
    elif (source == "cache" and any(w in fb_lower for w in ["sai", "cũ", "lệch", "không đúng"])) or any(w in fb_lower for w in ["cache", "cập nhật", "stale"]):
        issue_type = "stale_cache"
        target_entity_or_intent = extract_entity_name_simple(q_val)
        severity = "medium"
        suggested_policy_type = "clear_stale_cache"
        evidence_terms = [w for w in ["cũ", "cache", "cập nhật"] if w in fb_lower]
        confidence = 0.9

    # 6. too_mechanical
    # E.g. mechanical structure
    elif any(w in fb_lower for w in ["máy móc", "rập khuôn", "như robot"]):
        issue_type = "too_mechanical"
        target_entity_or_intent = extract_entity_name_simple(q_val)
        severity = "low"
        suggested_policy_type = "answer_format_policy"
        evidence_terms = [w for w in ["máy móc", "rập khuôn"] if w in fb_lower]
        confidence = 0.8

    return {
        "issue_type": issue_type,
        "target_entity_or_intent": target_entity_or_intent,
        "severity": severity,
        "suggested_policy_type": suggested_policy_type,
        "evidence_terms": evidence_terms,
        "confidence": confidence
    }
