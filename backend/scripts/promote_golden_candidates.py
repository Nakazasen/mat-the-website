# promote_golden_candidates.py
# Verifies candidate failures against the production API and auto-promotes verified ones.

import sys
import os
import json
import urllib.request
import argparse
import ssl
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

def verify_runtime_repro(base_url, question, chapter_progress, must_not_contain, semantic_forbidden_patterns, semantic_required_any_terms, expected_abstain_text, acceptable_abstain, insecure_dev_no_ssl_verify=False):
    """
    Call production API to reproduce the failure.
    Returns: (repro_passed, status_code, answer, source, reason)
    repro_passed = True means the error actually reproduces (meaning the answer violated constraints).
    """
    url = f"{base_url.rstrip('/')}/oracle/ask"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    body = {
        "question": question,
        "chapter_progress": chapter_progress
    }

    ctx = ssl.create_default_context()
    if insecure_dev_no_ssl_verify:
        url_lower = base_url.lower()
        if "mat-the-website.onrender.com" not in url_lower and "matthesinhhoa.vercel.app" not in url_lower:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            status_code = resp.status
            if status_code != 200:
                return False, status_code, "", "unknown", f"HTTP status: {status_code}"

            res_body = json.loads(resp.read().decode("utf-8"))
            answer = res_body.get("answer", "")
            source = res_body.get("source", "")

            # Run checks: if checks fail, it means the error is reproduced!
            error_reproduced = False
            repro_reason = "No error reproduced (answer passed all safety gates)."

            # 1. must_not_contain
            for term in must_not_contain:
                if term.lower() in answer.lower():
                    error_reproduced = True
                    repro_reason = f"Answer contains forbidden term: '{term}'"
                    break

            # 2. semantic_forbidden_patterns
            if not error_reproduced:
                for pattern in semantic_forbidden_patterns:
                    if pattern.lower() in answer.lower():
                        error_reproduced = True
                        repro_reason = f"Answer contains forbidden pattern: '{pattern}'"
                        break

            # 3. Check abstain vs required terms
            if not error_reproduced:
                is_abstain = False
                if expected_abstain_text:
                    clean_ans = "".join(answer.lower().split())
                    clean_exp = "".join(expected_abstain_text.lower().split())
                    if clean_exp in clean_ans or clean_ans in clean_exp:
                        is_abstain = True

                if is_abstain:
                    if not acceptable_abstain:
                        error_reproduced = True
                        repro_reason = "Answer is an abstain response, but abstain is not acceptable."
                else:
                    if semantic_required_any_terms:
                        has_any = any(term.lower() in answer.lower() for term in semantic_required_any_terms)
                        if not has_any:
                            error_reproduced = True
                            repro_reason = f"Answer is not abstain and does not contain required terms: {semantic_required_any_terms}"

            return error_reproduced, status_code, answer, source, repro_reason

    except Exception as e:
        return False, 500, "", "error", f"Network exception: {e}"

def main():
    global supabase
    supabase = _get_supabase_client()
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Autonomously promote golden regression candidates.")
    parser.add_argument("--base-url", default="https://mat-the-website.onrender.com", help="Base URL of production API.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Default dry-run mode (no DB writes).")
    parser.add_argument("--write", action="store_true", help="Actually promote candidates and update DB.")
    parser.add_argument("--json", action="store_true", help="Print summary output in JSON format.")
    parser.add_argument("--insecure-dev-no-ssl-verify", action="store_true", help="Disable SSL certificate verification for local development.")

    args = parser.parse_args()
    dry_run = True
    if args.write:
        dry_run = False

    base_url = args.base_url.rstrip('/')

    if args.insecure_dev_no_ssl_verify:
        url_lower = base_url.lower()
        if "mat-the-website.onrender.com" in url_lower or "matthesinhhoa.vercel.app" in url_lower:
            print("Error: --insecure-dev-no-ssl-verify is strictly forbidden on production domains.", file=sys.stderr)
            sys.exit(1)

    report_path = os.path.join(backend_root, "rag", "generated_feedback_to_golden_promotion_report.json")

    summary = {
        "feedback_rows_read": 0,
        "candidates_built": 0,
        "candidates_observing": 0,
        "candidates_auto_promote_ready": 0,
        "candidates_auto_promoted": 0,
        "candidates_blocked_conflict": 0,
        "candidates_failed_runtime": 0,
        "planned_promotions": 0,
        "written_promotions": 0,
        "skipped_ambiguous": 0,
        "skipped_no_runtime_proof": 0,
        "candidate_source_count": 0,
        "db_candidates_read": 0,
        "synthetic_candidates_added": 0,
        "errors": []
    }

    # Fetch active candidates from DB
    candidates = []
    try:
        cand_res = supabase.table("oracle_golden_regression_candidates").select("*").execute()
        if cand_res.data:
            candidates = cand_res.data
    except Exception as e:
        summary["errors"].append(f"Failed to fetch candidates: {e}")
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Dry-run must reflect actual database records truthfully (no synthetic appends)
    summary["candidate_source_count"] = len(candidates)
    summary["db_candidates_read"] = len(candidates)
    summary["synthetic_candidates_added"] = 0
    summary["candidates_built"] = len(candidates)

    # Fetch existing active golden cases to check for conflicts
    existing_cases = {}
    try:
        cases_res = supabase.table("oracle_golden_regression_cases").select("*").execute()
        if cases_res.data:
            existing_cases = {c["case_key"]: c for c in cases_res.data}
    except Exception as e:
        pass

    promotions_to_write = []
    candidate_updates = []

    for cand in candidates:
        status = cand.get("promotion_status")
        candidate_key = cand.get("candidate_key")

        # Skip already promoted, blocked or disabled candidates
        if status in ["auto_promoted", "disabled", "blocked_conflict"]:
            if status == "auto_promoted":
                summary["candidates_auto_promoted"] += 1
            elif status == "blocked_conflict":
                summary["candidates_blocked_conflict"] += 1
            elif status == "observing":
                summary["candidates_observing"] += 1
            continue

        # Perform runtime repro verification on production URL
        repro_passed, status_code, answer, source, reason = verify_runtime_repro(
            base_url=base_url,
            question=cand.get("question"),
            chapter_progress=cand.get("chapter_progress", 1),
            must_not_contain=cand.get("must_not_contain") or [],
            semantic_forbidden_patterns=cand.get("semantic_forbidden_patterns") or [],
            semantic_required_any_terms=cand.get("semantic_required_any_terms") or [],
            expected_abstain_text=cand.get("expected_abstain_text"),
            acceptable_abstain=cand.get("acceptable_abstain", True),
            insecure_dev_no_ssl_verify=args.insecure_dev_no_ssl_verify
        )

        # Determine distinct validation flags
        runtime_failure_reproduced = repro_passed
        runtime_validation_passed = not repro_passed

        # Gating based on candidate provenance source
        if cand.get("source") == "system_canary":
            promotion_gate_passed = runtime_validation_passed
        else:
            promotion_gate_passed = runtime_failure_reproduced

        cand_update = {
            "id": cand.get("id"),
            "candidate_key": candidate_key,
            "runtime_repro_passed": repro_passed,
            "evidence": {
                **(cand.get("evidence") or {}),
                "runtime_failure_reproduced": runtime_failure_reproduced,
                "runtime_validation_passed": runtime_validation_passed,
                "promotion_gate_passed": promotion_gate_passed,
                "runtime_verification": {
                    "verified_at": datetime.now(timezone.utc).isoformat(),
                    "base_url": base_url,
                    "status_code": status_code,
                    "answer_excerpt": answer[:300] if answer else "",
                    "source": source,
                    "repro_reason": reason
                }
            }
        }

        # Check for conflict
        existing_case = existing_cases.get(candidate_key)
        if existing_case and existing_case.get("status") == "active":
            cand_update["promotion_status"] = "blocked_conflict"
            cand_update["promotion_reason"] = f"Conflict: Active case '{candidate_key}' already exists in registry."
            summary["candidates_blocked_conflict"] += 1
            candidate_updates.append(cand_update)
            continue

        # Promotion logic
        if status_code != 200:
            cand_update["promotion_status"] = "failed_runtime"
            cand_update["promotion_reason"] = f"Runtime check failed with status {status_code}: {reason}."
            summary["candidates_failed_runtime"] += 1
        elif status == "auto_promote_ready":
            if promotion_gate_passed:
                # Promotion gate passed successfully (canary validation passed, or regression repro succeeded)
                cand_update["promotion_status"] = "auto_promoted"
                cand_update["promotion_reason"] = f"Auto-promoted successfully. Gate passed. Reason: {reason}"
                summary["candidates_auto_promoted"] += 1
                summary["planned_promotions"] += 1

                promotions_to_write.append({
                    "case_key": candidate_key,
                    "source": cand.get("source"),
                    "question": cand.get("question"),
                    "chapter_progress": cand.get("chapter_progress"),
                    "intent": cand.get("intent", "event_plot"),
                    "must_not_contain": cand.get("must_not_contain"),
                    "semantic_forbidden_patterns": cand.get("semantic_forbidden_patterns"),
                    "semantic_required_any_terms": cand.get("semantic_required_any_terms"),
                    "acceptable_abstain": cand.get("acceptable_abstain"),
                    "expected_abstain_text": cand.get("expected_abstain_text"),
                    "status": "active",
                    "created_from_feedback_id": cand.get("feedback_ids")[0] if cand.get("feedback_ids") else None
                })
            else:
                # Gate failed
                if cand.get("source") == "system_canary":
                    cand_update["promotion_status"] = "canary_validation_failed"
                    cand_update["promotion_reason"] = f"Canary validation failed: {reason}"
                    summary["candidates_failed_runtime"] += 1
                else:
                    cand_update["promotion_status"] = "observing"
                    cand_update["promotion_reason"] = f"Stale check: production answer passed safety checks. Reason: {reason}."
                    summary["skipped_no_runtime_proof"] += 1
                    summary["candidates_observing"] += 1
        else:
            if promotion_gate_passed:
                cand_update["promotion_status"] = "observing"
                cand_update["promotion_reason"] = f"Observing. Score below threshold. Repro verified: {repro_passed}."
                summary["candidates_observing"] += 1
            else:
                cand_update["promotion_status"] = "observing"
                cand_update["promotion_reason"] = f"Stale check: production answer passed safety checks. Reason: {reason}."
                summary["skipped_no_runtime_proof"] += 1
                summary["candidates_observing"] += 1

        candidate_updates.append(cand_update)

    # Apply database changes if not dry-run
    if not dry_run:
        # 1. Update candidate statuses
        for update in candidate_updates:
            try:
                supabase.table("oracle_golden_regression_candidates").update(update).eq("id", update["id"]).execute()
            except Exception as e:
                summary["errors"].append(f"Failed to update candidate '{update['candidate_key']}': {e}")

        # 2. Write promoted cases to registry
        written_count = 0
        for promo in promotions_to_write:
            try:
                # Check status disabled to avoid overwrite
                existing = existing_cases.get(promo["case_key"])
                if existing and existing.get("status") == "disabled":
                    continue
                supabase.table("oracle_golden_regression_cases").upsert(promo, on_conflict="case_key").execute()
                written_count += 1
            except Exception as e:
                summary["errors"].append(f"Failed to promote case '{promo['case_key']}': {e}")
        summary["written_promotions"] = written_count

    # Save summary report
    try:
        # Read from feedback_rows_read for report
        fb_res = supabase.table("rag_feedback").select("count", count="exact").execute()
        summary["feedback_rows_read"] = fb_res.count or 0
    except Exception:
        pass

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print("=== GOLDEN CANDIDATE PROMOTION SUMMARY ===")
        print(f"Dry Run: {dry_run}")
        print(f"Candidates built/total:        {summary['candidates_built']}")
        print(f"Candidates auto-promoted:      {summary['candidates_auto_promoted']}")
        print(f"Candidates observing:          {summary['candidates_observing']}")
        print(f"Candidates blocked conflict:   {summary['candidates_blocked_conflict']}")
        print(f"Candidates failed runtime:     {summary['candidates_failed_runtime']}")
        print(f"Planned promotions:            {summary['planned_promotions']}")
        print(f"Written promotions:            {summary['written_promotions']}")
        print(f"Skipped no runtime proof:      {summary['skipped_no_runtime_proof']}")
        print(f"Candidate source count:        {summary['candidate_source_count']}")
        print(f"DB candidates read:            {summary['db_candidates_read']}")
        print(f"Synthetic candidates added:    {summary['synthetic_candidates_added']}")
        if summary["errors"]:
            print("Errors encountered:")
            for err in summary["errors"]:
                print(f" - {err}")
        print("==========================================")

if __name__ == "__main__":
    main()
