"""
Effective Patch Engine Module
Processes community feedback and generates knowledge patches to refine Oracle retrieval.
"""

import re
from typing import List, Dict, Any

NOISY_KEYWORDS = [
    "lan man", 
    "không liên quan", 
    "lôi thêm", 
    "trả lời dài", 
    "sai trọng tâm", 
    "không phải nhân vật này"
]

def group_feedback_by_target(rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        pid = row.get("provisional_id")
        if not pid:
            continue
        pid = str(pid).strip()
        if pid not in groups:
            groups[pid] = []
        groups[pid].append(row)
    return groups

def detect_noisy_related_feedback(group: List[Dict[str, Any]]) -> bool:
    for row in group:
        comment = (row.get("user_comment") or "").strip().lower()
        if any(kw in comment for kw in NOISY_KEYWORDS):
            return True
    return False

def detect_wrong_info_feedback(group: List[Dict[str, Any]]) -> tuple[int, int]:
    info_count = 0
    evidence_count = 0
    for row in group:
        fb_type = (row.get("feedback_type") or "").strip().lower()
        if fb_type == "wrong_info":
            info_count += 1
        elif fb_type == "wrong_evidence":
            evidence_count += 1
    return info_count, evidence_count

def detect_duplicate_feedback(group: List[Dict[str, Any]]) -> int:
    dup_count = 0
    for row in group:
        fb_type = (row.get("feedback_type") or "").strip().lower()
        if fb_type == "duplicate":
            dup_count += 1
    return dup_count

def extract_target_entity_from_feedback(comment: str, record_name: str) -> tuple[str, str]:
    # Try pattern: "câu hỏi <Name> là ai" or "câu hỏi <Name> là gì"
    m = re.search(r"câu\s+hỏi\s+([A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸY\s\w]+?)\s+là\s+(ai|gì)", comment, re.IGNORECASE)
    if m:
        name = m.group(1).strip()
        name = re.sub(r"[?.,;:!]", "", name).strip()
        q_type = m.group(2).strip().lower()
        return name, f"{name} là {q_type}?"

    # Try pattern: "không liên quan đến <Name>"
    m2 = re.search(r"không\s+liên\s+quan\s+đến\s+([A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸY\s\w]+)", comment, re.IGNORECASE)
    if m2:
        name = m2.group(1).strip()
        name = re.sub(r"[?.,;:!]", "", name).strip()
        return name, f"{name} là ai?"

    # Fallback: extract the main proper nouns from record_name
    words = record_name.split()
    cap_words = []
    for w in words:
        if w and w[0].isupper():
            clean_w = re.sub(r"[^\w\sÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸY]", "", w)
            if clean_w:
                cap_words.append(clean_w)
    
    if len(cap_words) >= 2:
        extracted = " ".join(cap_words)
        return extracted, f"{extracted} là ai?"
        
    return record_name, f"{record_name} là ai?"

def build_patch_payloads(
    feedback_rows: List[Dict[str, Any]],
    provisional_records: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    patches = []
    groups = group_feedback_by_target(feedback_rows)
    identity_suppressions = {}

    for pid, group in groups.items():
        record = provisional_records.get(pid)
        if not record:
            continue
            
        record_name = record.get("name", "")
        
        info_cnt, ev_cnt = detect_wrong_info_feedback(group)
        dup_cnt = detect_duplicate_feedback(group)
        
        fb_ids = [row.get("id") for row in group if row.get("id")]
        
        # Rule A & B: wrong info or wrong evidence
        if info_cnt >= 5 or ev_cnt >= 5:
            patches.append({
                "target_type": "provisional_record",
                "target_id": pid,
                "target_name": record_name,
                "patch_type": "hide_record",
                "effective_status": "active",
                "oracle_policy": "block",
                "feedback_ids": fb_ids,
                "confidence": 1.0,
                "reason": f"Accumulated {info_cnt} wrong_info and {ev_cnt} wrong_evidence feedback flags.",
                "created_by": "community_rag_policy_engine"
            })
        elif info_cnt >= 3 or ev_cnt >= 3:
            patches.append({
                "target_type": "provisional_record",
                "target_id": pid,
                "target_name": record_name,
                "patch_type": "deprioritize_record",
                "effective_status": "active",
                "oracle_policy": "deprioritize",
                "feedback_ids": fb_ids,
                "confidence": 0.8,
                "reason": f"Accumulated {info_cnt} wrong_info and {ev_cnt} wrong_evidence feedback flags.",
                "created_by": "community_rag_policy_engine"
            })

        # Rule D: Duplicate feedback
        if dup_cnt >= 3:
            patches.append({
                "target_type": "provisional_record",
                "target_id": pid,
                "target_name": record_name,
                "patch_type": "warn_record",
                "effective_status": "active",
                "oracle_policy": "warn",
                "feedback_ids": fb_ids,
                "confidence": 0.7,
                "reason": f"Accumulated {dup_cnt} duplicate feedback flags.",
                "created_by": "community_rag_policy_engine"
            })

        # Rule E: Multiple suggested corrections for effective_summary
        corrections = [row.get("suggested_correction", "").strip() for row in group if row.get("suggested_correction")]
        corrections = [c for c in corrections if len(c) >= 10]
        if len(corrections) >= 2:
            from collections import Counter
            counts = Counter(corrections)
            most_common, freq = counts.most_common(1)[0]
            if freq >= 2:
                patches.append({
                    "target_type": "provisional_record",
                    "target_id": pid,
                    "target_name": record_name,
                    "patch_type": "effective_summary",
                    "effective_status": "active",
                    "oracle_policy": "allow",
                    "effective_summary": most_common,
                    "feedback_ids": fb_ids,
                    "confidence": 0.9,
                    "reason": f"Accumulated {freq} identical suggested corrections.",
                    "created_by": "community_rag_policy_engine"
                })

        # Collect noisy feedback for Rule C
        for row in group:
            comment = (row.get("user_comment") or "").strip().lower()
            if any(kw in comment for kw in NOISY_KEYWORDS):
                target_name, query_pattern = extract_target_entity_from_feedback(row.get("user_comment", ""), record_name)
                norm_qp = query_pattern.strip().lower()
                if norm_qp not in identity_suppressions:
                    identity_suppressions[norm_qp] = {
                        "target_name": target_name,
                        "query_pattern": query_pattern,
                        "suppress_record_ids": set(),
                        "feedback_ids": set()
                    }
                identity_suppressions[norm_qp]["suppress_record_ids"].add(pid)
                if row.get("id"):
                    identity_suppressions[norm_qp]["feedback_ids"].add(row.get("id"))

    # Build patches for identity suppressions (Rule C)
    for norm_qp, info in identity_suppressions.items():
        patches.append({
            "target_type": "query",
            "target_name": info["target_name"],
            "query_pattern": info["query_pattern"],
            "patch_type": "suppress_related_for_identity_query",
            "effective_status": "active",
            "oracle_policy": "allow",
            "suppress_record_ids": list(info["suppress_record_ids"]),
            "feedback_ids": list(info["feedback_ids"]),
            "confidence": 0.9,
            "reason": f"Community feedback flagged these records as noisy/unrelated to query '{info['query_pattern']}'.",
            "created_by": "community_rag_policy_engine"
        })

    return patches


def patch_dedupe_key(payload: Dict[str, Any]) -> str:
    """
    Generates a unique deduplication key for a patch payload.
    Normalizes keys: target_type, target_id, target_name, query_pattern, patch_type.
    """
    tt = str(payload.get("target_type") or "").strip().lower()
    tid = str(payload.get("target_id") or "").strip().lower()
    tn = str(payload.get("target_name") or "").strip().lower()
    qp = str(payload.get("query_pattern") or "").strip().lower()
    pt = str(payload.get("patch_type") or "").strip().lower()

    # Normalize whitespace
    tn_norm = " ".join(tn.split())
    qp_norm = " ".join(qp.split())

    return f"{tt}:{tid}:{tn_norm}:{qp_norm}:{pt}"
