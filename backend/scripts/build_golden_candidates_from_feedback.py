# build_golden_candidates_from_feedback.py
# Aggregates pending/accepted/resolved feedbacks, calculates trust metrics, and builds regression candidates.

import sys
import os
import json
import argparse
import hashlib
from datetime import datetime, timezone

# Add repository root to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

try:
    from backend.main import supabase
except ImportError:
    from main import supabase

from backend.rag.golden_promotion_policy import (
    determine_trust_level,
    parse_constraints_from_comment,
    TRUST_WEIGHTS,
    SCORE_THRESHOLD
)

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Aggregate rag_feedback into regression candidates.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Default dry-run mode (no DB writes).")
    parser.add_argument("--write", action="store_true", help="Actually write updates to Supabase DB.")
    parser.add_argument("--json", action="store_true", help="Print summary output in JSON format.")

    args = parser.parse_args()
    dry_run = True
    if args.write:
        dry_run = False

    summary = {
        "feedback_rows_read": 0,
        "candidates_built": 0,
        "candidates_observing": 0,
        "candidates_auto_promote_ready": 0,
        "planned_upserts": 0,
        "written_upserts": 0,
        "skipped_ambiguous": 0,
        "errors": []
    }

    # 1. Read feedbacks from DB
    feedbacks = []
    try:
        res = supabase.table("rag_feedback").select("*").in_("status", ["pending", "accepted", "resolved"]).execute()
        if res.data:
            feedbacks = res.data
    except Exception as e:
        summary["errors"].append(f"Failed to fetch feedbacks: {e}")
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    summary["feedback_rows_read"] = len(feedbacks)

    # 2. Group feedbacks by normalized question and chapter progress
    grouped = {}
    for fb in feedbacks:
        question = fb.get("question") or ""
        norm_q = " ".join(question.lower().split())
        if not norm_q:
            summary["skipped_ambiguous"] += 1
            continue

        chapter_progress = fb.get("chapter_progress") or 1
        key = (norm_q, chapter_progress)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(fb)

    # Fetch existing candidates in DB to preserve RLS or existing statuses
    existing_candidates = {}
    try:
        cand_res = supabase.table("oracle_golden_regression_candidates").select("*").execute()
        if cand_res.data:
            existing_candidates = {c["candidate_key"]: c for c in cand_res.data}
    except Exception as e:
        # Ignore error if table doesn't exist yet, will be caught during upserts
        pass

    upsert_payloads = []

    for (norm_q, chapter_progress), group in grouped.items():
        # Representing question from first item
        representative_q = group[0].get("question")
        if len(representative_q) < 5:
            summary["skipped_ambiguous"] += 1
            continue

        # Compute trust metrics
        highest_trust = "anonymous"
        score = 0.0
        feedback_ids = []
        evidence_entries = []

        must_not_contain_set = set()
        semantic_forbidden_set = set()
        semantic_required_set = set()
        expected_abstain_text = ""

        # Predefined mapping for trust priority
        trust_priority = {"anonymous": 0, "reader": 1, "trusted_reader": 2, "system": 3, "author": 4}

        for fb in group:
            fid = fb.get("id")
            feedback_ids.append(fid)
            trust = determine_trust_level(fb)
            if trust_priority[trust] > trust_priority[highest_trust]:
                highest_trust = trust

            score += TRUST_WEIGHTS.get(trust, 0.2)

            evidence_entries.append({
                "feedback_id": fid,
                "user_comment": fb.get("user_comment"),
                "answer": fb.get("answer"),
                "suggested_correction": fb.get("suggested_correction")
            })

            # Parse constraints
            mnc, sfp, srt, eat = parse_constraints_from_comment(fb.get("user_comment"), fb.get("suggested_correction"))
            must_not_contain_set.update(mnc)
            semantic_forbidden_set.update(sfp)
            semantic_required_set.update(srt)
            if eat and len(eat) > len(expected_abstain_text):
                expected_abstain_text = eat

        # Candidate Key
        h = hashlib.md5(norm_q.encode("utf-8")).hexdigest()[:16]
        candidate_key = f"candidate_{h}_{chapter_progress}"

        existing_cand = existing_candidates.get(candidate_key)
        
        # Determine promotion status
        promotion_status = "candidate"
        promotion_reason = "Aggregated from feedback. Pending runtime check."

        # Skip if no constraints specified
        has_any_constraint = (
            must_not_contain_set or 
            semantic_forbidden_set or 
            semantic_required_set or 
            expected_abstain_text
        )
        if not has_any_constraint:
            promotion_status = "observing"
            promotion_reason = "Observing. Missing explicit validation constraints."
            summary["candidates_observing"] += 1
        elif score >= SCORE_THRESHOLD:
            promotion_status = "auto_promote_ready"
            promotion_reason = "Auto-promote ready. Score threshold met. Pending runtime check."
            summary["candidates_auto_promote_ready"] += 1
        else:
            promotion_status = "observing"
            promotion_reason = f"Observing. Score {score:.2f} is below threshold {SCORE_THRESHOLD}."
            summary["candidates_observing"] += 1

        payload = {
            "candidate_key": candidate_key,
            "source": f"{highest_trust}_feedback",
            "trust_level": highest_trust,
            "question": representative_q,
            "chapter_progress": chapter_progress,
            "feedback_ids": feedback_ids,
            "error_signature": group[0].get("feedback_type") or "wrong",
            "intent": "event_plot",
            "must_not_contain": list(must_not_contain_set),
            "semantic_forbidden_patterns": list(semantic_forbidden_set),
            "semantic_required_any_terms": list(semantic_required_set),
            "acceptable_abstain": True,
            "expected_abstain_text": expected_abstain_text,
            "evidence": {"feedbacks": evidence_entries},
            "runtime_repro_passed": False,
            "promotion_score": round(score, 2),
            "promotion_status": promotion_status,
            "promotion_reason": promotion_reason
        }

        # Keep existing custom status if it's already disabled or auto_promoted
        if existing_cand:
            payload["id"] = existing_cand["id"]
            if existing_cand.get("promotion_status") in ["disabled", "auto_promoted", "blocked_conflict"]:
                payload["promotion_status"] = existing_cand["promotion_status"]
                payload["promotion_reason"] = existing_cand.get("promotion_reason")

        upsert_payloads.append(payload)

    summary["candidates_built"] = len(upsert_payloads)
    summary["planned_upserts"] = len(upsert_payloads)

    if not dry_run and upsert_payloads:
        written_count = 0
        for payload in upsert_payloads:
            try:
                supabase.table("oracle_golden_regression_candidates").upsert(payload, on_conflict="candidate_key").execute()
                written_count += 1
            except Exception as e:
                summary["errors"].append(f"Failed to upsert candidate '{payload['candidate_key']}': {e}")
        summary["written_upserts"] = written_count

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print("=== GOLDEN CANDIDATE BUILD SUMMARY ===")
        print(f"Dry Run: {dry_run}")
        print(f"Feedback rows read:            {summary['feedback_rows_read']}")
        print(f"Candidates built:              {summary['candidates_built']}")
        print(f"Candidates observing:          {summary['candidates_observing']}")
        print(f"Candidates auto-promote ready: {summary['candidates_auto_promote_ready']}")
        print(f"Planned upserts:               {summary['planned_upserts']}")
        print(f"Written upserts:               {summary['written_upserts']}")
        print(f"Skipped ambiguous/short:       {summary['skipped_ambiguous']}")
        if summary["errors"]:
            print("Errors encountered:")
            for err in summary["errors"]:
                print(f" - {err}")
        print("=======================================")

if __name__ == "__main__":
    main()
