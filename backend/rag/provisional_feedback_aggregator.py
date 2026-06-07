"""
Provisional Feedback Aggregator Module
Aggregates community feedback, calculates dispute scores, and decises oracle policy.
"""

from typing import List, Dict, Any

ALLOWED_FEEDBACK_TYPES = {
    "wrong_info",
    "wrong_type",
    "wrong_evidence",
    "duplicate",
    "spoiler",
    "missing_info",
    "other"
}

DISPUTE_WEIGHTS = {
    "wrong_info": 1.5,
    "wrong_evidence": 1.5,
    "wrong_type": 1.2,
    "spoiler": 1.0,
    "duplicate": 1.0,
    "missing_info": 0.5,
    "other": 0.3
}

def normalize_feedback_type(value: Any) -> str:
    if not isinstance(value, str):
        return "other"
    val = value.strip().lower()
    if val in ALLOWED_FEEDBACK_TYPES:
        return val
    return "other"

def group_feedback_by_provisional_id(rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        pid = row.get("provisional_id")
        if not pid or not isinstance(pid, str):
            continue
        pid = pid.strip()
        if pid not in groups:
            groups[pid] = []
        groups[pid].append(row)
    return groups

def count_unique_user_agents(rows: List[Dict[str, Any]]) -> int:
    agents = set()
    for row in rows:
        ua = row.get("user_agent")
        if ua and isinstance(ua, str) and ua.strip():
            agents.add(ua.strip().lower())
    return len(agents)

def calculate_dispute_score(group: List[Dict[str, Any]]) -> tuple[float, Dict[str, int]]:
    counts = {t: 0 for t in ALLOWED_FEEDBACK_TYPES}
    score = 0.0
    for row in group:
        fb_type = normalize_feedback_type(row.get("feedback_type"))
        counts[fb_type] += 1
        score += DISPUTE_WEIGHTS.get(fb_type, 0.3)
    return round(score, 2), counts

def decide_effective_status(summary: Dict[str, Any]) -> tuple[str, str]:
    total_feedback = summary.get("total_feedback", 0)
    dispute_score = summary.get("dispute_score", 0.0)
    unique_user_agent_count = summary.get("unique_user_agent_count", 0)
    wrong_info_count = summary.get("wrong_info_count", 0)
    wrong_evidence_count = summary.get("wrong_evidence_count", 0)
    duplicate_count = summary.get("duplicate_count", 0)

    # 1. Block policy (high error count)
    if wrong_info_count >= 5 or wrong_evidence_count >= 5:
        return "hidden_from_oracle", "block"
        
    # 2. Deprioritize policy (many reports from multiple users)
    if total_feedback >= 5 and unique_user_agent_count >= 3:
        return "needs_review", "deprioritize"
        
    # 3. Warn policy (substantial disputes)
    if total_feedback >= 3 and dispute_score >= 3.0:
        return "disputed", "warn"
        
    # 4. Duplicate suspected (many duplicate flags)
    if duplicate_count >= 3:
        return "duplicate_suspected", "warn"
        
    # 5. Trusted / Default
    return "trusted", "allow"

def build_feedback_summary_payload(group: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not group:
        return {}
        
    pid = group[0].get("provisional_id", "").strip()
    record_name = group[0].get("record_name")
    if record_name and isinstance(record_name, str):
        record_name = record_name.strip()
    else:
        record_name = None

    # Calculate dispute score and counts
    score, counts = calculate_dispute_score(group)
    ua_count = count_unique_user_agents(group)
    total = len(group)

    # Gather top comments (up to 5 recent comments)
    sorted_group = sorted(
        group, 
        key=lambda x: x.get("created_at") or "", 
        reverse=True
    )
    top_comments = []
    for item in sorted_group[:5]:
        comment = item.get("user_comment", "").strip()
        corr = item.get("suggested_correction")
        created = item.get("created_at")
        if comment:
            top_comments.append({
                "user_comment": comment,
                "suggested_correction": corr.strip() if (corr and isinstance(corr, str)) else None,
                "created_at": created
            })

    summary_draft = {
        "provisional_id": pid,
        "record_name": record_name,
        "total_feedback": total,
        "wrong_info_count": counts.get("wrong_info", 0),
        "wrong_type_count": counts.get("wrong_type", 0),
        "wrong_evidence_count": counts.get("wrong_evidence", 0),
        "duplicate_count": counts.get("duplicate", 0),
        "spoiler_count": counts.get("spoiler", 0),
        "missing_info_count": counts.get("missing_info", 0),
        "other_count": counts.get("other", 0),
        "unique_user_agent_count": ua_count,
        "dispute_score": score,
        "top_comments": top_comments
    }

    effective_status, oracle_policy = decide_effective_status(summary_draft)
    summary_draft["effective_status"] = effective_status
    summary_draft["oracle_policy"] = oracle_policy

    return summary_draft

def summarize_feedback(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    groups = group_feedback_by_provisional_id(rows)
    summaries = []
    for pid, group in groups.items():
        summary = build_feedback_summary_payload(group)
        if summary:
            summaries.append(summary)
    return summaries
