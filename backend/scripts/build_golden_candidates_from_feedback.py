# build_golden_candidates_from_feedback.py
# Aggregates pending/accepted/resolved feedbacks, calculates trust metrics, and builds regression candidates.

import sys
import os
import json
import argparse
import hashlib
from datetime import datetime, timezone

# Add repository root and backend root to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(os.path.dirname(script_dir))
backend_root = os.path.dirname(script_dir)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

supabase = None

def _get_supabase_client():
    global supabase
    if supabase is not None:
        return supabase
    try:
        from backend.main import supabase as main_supabase
        if main_supabase is not None:
            supabase = main_supabase
            return supabase
    except Exception:
        pass
    try:
        from main import supabase as main_supabase
        if main_supabase is not None:
            supabase = main_supabase
            return supabase
    except Exception:
        pass

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY/SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
    from supabase import create_client
    supabase = create_client(url, key)
    return supabase

from backend.rag.golden_promotion_policy import (
    determine_trust_level,
    parse_constraints_from_comment,
    TRUST_WEIGHTS,
    SCORE_THRESHOLD
)

def main():
    global supabase
    supabase = _get_supabase_client()
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
        "spoofed_trust_tags_detected": 0,
        "untrusted_author_claims": 0,
        "untrusted_system_claims": 0,
        "untrusted_trusted_reader_claims": 0,
        "unverified_elevated_metadata_claims": 0,
        "rejected_privileged_payload_fields": 0,
        "verified_author_feedback_count": 0,
        "verified_system_feedback_count": 0,
        "verified_trusted_reader_count": 0,
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

            # Audit server-side metadata provenance vs claims
            trust_verified = fb.get("trust_verified") is True or fb.get("trust_verified") == "true"
            source_verified = fb.get("source_verified") is True or fb.get("source_verified") == "true"
            method = fb.get("trust_verification_method")

            # Detect unverified elevated metadata claims
            has_author_metadata_claim = (
                fb.get("source") == "author_feedback" or
                fb.get("trust_level") == "author" or
                fb.get("is_author") is True or
                fb.get("is_author") == "true"
            )
            has_system_metadata_claim = (
                fb.get("source") == "system_detected_failure" or
                fb.get("trust_level") == "system"
            )
            has_trusted_metadata_claim = (
                fb.get("trust_level") == "trusted_reader" or
                fb.get("is_trusted_reader") is True or
                fb.get("is_trusted_reader") == "true"
            )

            is_elevated_metadata_claim = (
                has_author_metadata_claim or
                has_system_metadata_claim or
                has_trusted_metadata_claim
            )

            unverified_claim = False
            if is_elevated_metadata_claim:
                if not trust_verified and not source_verified:
                    unverified_claim = True
                    summary["unverified_elevated_metadata_claims"] += 1
                    # Treat direct privileged fields set without verification as rejected
                    summary["rejected_privileged_payload_fields"] += 1
                elif method == "none" or not method:
                    unverified_claim = True
                    summary["unverified_elevated_metadata_claims"] += 1
                    summary["rejected_privileged_payload_fields"] += 1

            # Count verified feedback types
            if trust == "author":
                summary["verified_author_feedback_count"] += 1
            elif trust == "system":
                summary["verified_system_feedback_count"] += 1
            elif trust == "trusted_reader":
                summary["verified_trusted_reader_count"] += 1

            # Detect spoofed roles in comment text
            comment = fb.get("user_comment") or ""
            claimed_roles = []
            if "[AUTHOR]" in comment:
                claimed_roles.append("author")
            if "[SYSTEM]" in comment:
                claimed_roles.append("system")
            if "[TRUSTED]" in comment:
                claimed_roles.append("trusted_reader")
            if "[READER]" in comment:
                claimed_roles.append("reader")

            is_spoofed = False
            verified = True
            for role in claimed_roles:
                if role == "author" and trust != "author":
                    summary["untrusted_author_claims"] += 1
                    is_spoofed = True
                    verified = False
                elif role == "system" and trust != "system":
                    summary["untrusted_system_claims"] += 1
                    is_spoofed = True
                    verified = False
                elif role == "trusted_reader" and trust not in ["author", "system", "trusted_reader"]:
                    summary["untrusted_trusted_reader_claims"] += 1
                    is_spoofed = True
                    verified = False
                elif role == "reader" and trust not in ["author", "system", "trusted_reader", "reader"]:
                    is_spoofed = True
                    verified = False

            if is_spoofed:
                summary["spoofed_trust_tags_detected"] += 1

            evidence_entries.append({
                "feedback_id": fid,
                "user_comment": fb.get("user_comment"),
                "answer": fb.get("answer"),
                "suggested_correction": fb.get("suggested_correction"),
                "untrusted_claimed_role_hint": claimed_roles,
                "verified": verified,
                "unverified_elevated_metadata_claim": unverified_claim
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
        print(f"Spoofed trust tags detected:   {summary['spoofed_trust_tags_detected']}")
        print(f"Untrusted author claims:       {summary['untrusted_author_claims']}")
        print(f"Untrusted system claims:       {summary['untrusted_system_claims']}")
        print(f"Untrusted trusted reader claims: {summary['untrusted_trusted_reader_claims']}")
        print(f"Unverified metadata claims:    {summary['unverified_elevated_metadata_claims']}")
        print(f"Rejected privileged payloads:  {summary['rejected_privileged_payload_fields']}")
        print(f"Verified author feedbacks:     {summary['verified_author_feedback_count']}")
        print(f"Verified system feedbacks:     {summary['verified_system_feedback_count']}")
        print(f"Verified trusted reader fbs:   {summary['verified_trusted_reader_count']}")
        if summary["errors"]:
            print("Errors encountered:")
            for err in summary["errors"]:
                print(f" - {err}")
        print("=======================================")

if __name__ == "__main__":
    main()
