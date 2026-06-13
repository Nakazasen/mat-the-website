# create_verified_golden_canary.py
# Creates and registers a verified system canary candidate after production pre-validation.

import sys
import os
import json
import argparse
import urllib.request
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

try:
    from backend.main import supabase
except ImportError:
    from main import supabase

# Import provenance logic
try:
    from backend.rag.feedback_trust_provenance import get_canary_provenance
except ImportError:
    from rag.feedback_trust_provenance import get_canary_provenance


def run_pre_validation(base_url, question, chapter_progress, mnc, sfp, srt, eat, acceptable_abstain):
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
    # For production validation we always use SSL verify
    
    attempts = []
    all_passed = True
    failure_reason = ""

    for i in range(3):
        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
                status_code = resp.status
                if status_code != 200:
                    all_passed = False
                    failure_reason = f"HTTP status code {status_code} on attempt {i+1}"
                    attempts.append({
                        "attempt": i+1,
                        "status_code": status_code,
                        "passed": False,
                        "reason": failure_reason
                    })
                    break

                res_body = json.loads(resp.read().decode("utf-8"))
                answer = res_body.get("answer", "")
                source = res_body.get("source", "")

                # Check safety constraints
                passed = True
                reason = "Pre-validation passed."

                # 1. must_not_contain
                for term in mnc:
                    if term.lower() in answer.lower():
                        passed = False
                        reason = f"Answer contains must_not_contain term: '{term}'"
                        break

                # 2. semantic_forbidden_patterns
                if passed:
                    for pattern in sfp:
                        if pattern.lower() in answer.lower():
                            passed = False
                            reason = f"Answer contains forbidden pattern: '{pattern}'"
                            break

                # 3. Required terms or abstain
                if passed:
                    is_abstain = False
                    if eat:
                        clean_ans = "".join(answer.lower().split())
                        clean_exp = "".join(eat.lower().split())
                        if clean_exp in clean_ans or clean_ans in clean_exp:
                            is_abstain = True

                    if is_abstain:
                        if not acceptable_abstain:
                            passed = False
                            reason = "Answer is an abstain response, but abstain is not acceptable."
                    else:
                        if srt:
                            has_any = any(term.lower() in answer.lower() for term in srt)
                            if not has_any:
                                passed = False
                                reason = f"Answer does not contain any required terms: {srt}"

                attempts.append({
                    "attempt": i+1,
                    "status_code": status_code,
                    "answer_excerpt": answer[:300] if answer else "",
                    "source": source,
                    "passed": passed,
                    "reason": reason
                })

                if not passed:
                    all_passed = False
                    failure_reason = reason
                    break
        except Exception as e:
            all_passed = False
            failure_reason = f"Exception on attempt {i+1}: {e}"
            attempts.append({
                "attempt": i+1,
                "status_code": 500,
                "passed": False,
                "reason": failure_reason
            })
            break

    return all_passed, failure_reason, attempts


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Create a verified system canary candidate.")
    parser.add_argument("--base-url", default="https://mat-the-website.onrender.com", help="Base URL of production API.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Default dry-run mode (no DB writes).")
    parser.add_argument("--write", action="store_true", help="Write changes to the database.")
    parser.add_argument("--json", action="store_true", help="Print summary output in JSON format.")

    args = parser.parse_args()
    dry_run = True
    if args.write:
        dry_run = False

    base_url = args.base_url.rstrip('/')

    canary_key = "canary_verified_le_giang_campaign"
    question = "Hãy kể lại diễn biến của chiến dịch Lệ Giang."
    chapter_progress = 829
    intent = "event_plot"
    mnc = ["[DỮ LIỆU HỆ THỐNG]", "Tổ chức trấn Hi Vọng", "Zombie Cấp 3", "Chu Vấn", "Quân Lệnh Như Sơn"]
    sfp = ["sông Lệ Giang", "cầu Lệ Giang", "bờ sông Lệ Giang", "tài nguyên thuỷ sản", "kho vũ khí"]
    srt = ["chiến dịch", "thanh tẩy", "nhiệm vụ", "huy động", "Thể Thôn Phệ Lệ Giang"]
    eat = "Chưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang."
    acceptable_abstain = True

    summary = {
        "planned_candidates": 1,
        "written_candidates": 0,
        "production_validation_passed": False,
        "validation_attempts": 0,
        "errors": [],
        "classification": None
    }

    # Run pre-validation
    val_passed, val_reason, attempts = run_pre_validation(
        base_url, question, chapter_progress, mnc, sfp, srt, eat, acceptable_abstain
    )
    summary["validation_attempts"] = len(attempts)
    summary["production_validation_passed"] = val_passed

    prov = get_canary_provenance()

    if val_passed:
        promotion_status = "auto_promote_ready"
        promotion_reason = "verified internal canary passed production validation"
    else:
        promotion_status = "canary_validation_failed"
        promotion_reason = f"Pre-validation failed: {val_reason}"
        summary["errors"].append(promotion_reason)
        summary["classification"] = "FAIL_PHASE_11E3_CANARY_PREVALIDATION_FAILED"

    payload = {
        "candidate_key": canary_key,
        "source": prov["source"],
        "trust_level": prov["trust_level"],
        "question": question,
        "chapter_progress": chapter_progress,
        "intent": intent,
        "must_not_contain": mnc,
        "semantic_forbidden_patterns": sfp,
        "semantic_required_any_terms": srt,
        "acceptable_abstain": acceptable_abstain,
        "expected_abstain_text": eat,
        "promotion_status": promotion_status,
        "promotion_score": 1.0,
        "runtime_repro_passed": False,
        "promotion_reason": promotion_reason,
        "evidence": {
            "trust_verification": {
                "verified_at": prov["trust_verified_at"],
                "trust_verification_method": prov["trust_verification_method"]
            },
            "pre_validation": {
                "base_url": base_url,
                "verified_at": datetime.now(timezone.utc).isoformat(),
                "attempts": attempts
            }
        }
    }

    if not dry_run:
        try:
            # Check if exists
            existing = supabase.table("oracle_golden_regression_candidates").select("*").eq("candidate_key", canary_key).execute()
            if existing.data:
                # Update existing
                supabase.table("oracle_golden_regression_candidates").update(payload).eq("candidate_key", canary_key).execute()
            else:
                # Insert new
                supabase.table("oracle_golden_regression_candidates").insert(payload).execute()
            summary["written_candidates"] = 1
        except Exception as e:
            summary["errors"].append(f"Database write failed: {e}")
            if not summary["classification"]:
                summary["classification"] = "FAIL_PHASE_11E3_CANARY_PREVALIDATION_FAILED"

    if summary["classification"] is None:
        if not val_passed:
            summary["classification"] = "FAIL_PHASE_11E3_CANARY_PREVALIDATION_FAILED"

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print("=== CREATE VERIFIED GOLDEN CANARY SUMMARY ===")
        print(f"Planned Candidates: {summary['planned_candidates']}")
        print(f"Written Candidates: {summary['written_candidates']}")
        print(f"Validation Passed:  {summary['production_validation_passed']}")
        print(f"Validation Attempts: {summary['validation_attempts']}")
        print(f"Classification:     {summary['classification']}")
        if summary["errors"]:
            print("Errors/Warnings:")
            for err in summary["errors"]:
                print(f" - {err}")
        print("=============================================")

    if not val_passed:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
