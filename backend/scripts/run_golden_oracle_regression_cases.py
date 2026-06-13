import sys
import os
import json
import urllib.request
import argparse
import ssl
import time
from datetime import datetime, timezone

# Add repository root to sys.path to ensure absolute imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)


def _get_supabase_client():
    try:
        from backend.main import supabase
        if supabase is not None:
            return supabase
    except Exception:
        pass
    try:
        from main import supabase
        if supabase is not None:
            return supabase
    except Exception:
        pass

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY/SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
    from supabase import create_client
    return create_client(url, key)


def run_regression():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
    parser = argparse.ArgumentParser(description="Run Golden Oracle Regression cases.")
    parser.add_argument("--base-url", required=True, help="Base URL of the target backend service.")
    parser.add_argument("--json", action="store_true", help="Print summary output in JSON format.")
    parser.add_argument("--write-report", action="store_true", help="Save the detailed execution report to backend/rag.")
    parser.add_argument("--source", default="json", choices=["json", "db"], help="Where to load test cases from (json or db).")
    parser.add_argument("--write-db-run", action="store_true", help="Write execution results into oracle_golden_regression_runs DB table.")

    # New options for transport hardening
    parser.add_argument("--request-timeout", type=int, default=60, help="HTTP request timeout in seconds.")
    parser.add_argument("--infra-retries", type=int, default=3, help="Number of infrastructure retries.")
    parser.add_argument("--infra-backoff-seconds", type=int, default=5, help="Backoff seconds between retries.")

    # New options for Phase 11E-4
    parser.add_argument("--rollback-mode", default="off", choices=["off", "verified-canary"], help="Rollback mode for database sources.")
    parser.add_argument("--report-path", default=None, help="Custom path to save the regression report.")

    args = parser.parse_args()
    base_url = args.base_url.rstrip('/')

    # Path to regression cases
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    cases_path = os.path.join(repo_root, "rag", "golden_oracle_regression_cases.json")
    if args.report_path:
        report_path = args.report_path
    else:
        report_path = os.path.join(repo_root, "rag", "generated_golden_oracle_regression_report.json")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Try to query health first to read git_commit
    prod_git_commit = None
    try:
        health_req = urllib.request.Request(f"{base_url}/api/health", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(health_req, context=ctx, timeout=10) as resp:
            if resp.status == 200:
                h_data = json.loads(resp.read().decode("utf-8"))
                prod_git_commit = h_data.get("git_commit")
    except Exception:
        pass

    cases = []
    load_error = None
    if args.source == "db":
        try:
            supabase = _get_supabase_client()
            res = supabase.table("oracle_golden_regression_cases").select("*").eq("status", "active").execute()
            if not res.data:
                cases = []
            else:
                cases = []
                for db_case in res.data:
                    c = dict(db_case)
                    c["id"] = db_case["case_key"]
                    cases.append(c)
        except Exception as e:
            load_error = f"Error loading cases from Supabase database: {e}"
    else:
        if not os.path.exists(cases_path):
            load_error = f"Error: Cases file not found at {cases_path}"
        else:
            try:
                with open(cases_path, "r", encoding="utf-8") as f:
                    cases = json.load(f)
            except Exception as e:
                load_error = f"Error parsing JSON from cases file: {e}"

    results = []
    passed_count = 0
    failed_count = 0
    semantic_failed = 0
    infra_failed = 0
    configuration_failed = 0
    retry_recovered = 0
    total_attempts = 0

    # Initialize rollback summary fields
    case_disabled_count = 0
    candidate_rolled_back_count = 0
    rollback_case_keys = []
    rollback_candidate_keys = []
    rollback_skipped_reasons = {}

    # Handle configuration loading error
    if load_error:
        configuration_failed = 1
        report = {
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "semantic_failed": 0,
                "infra_failed": 0,
                "configuration_failed": 1,
                "retry_recovered": 0,
                "total_attempts": 0,
                "run_at": datetime.now(timezone.utc).isoformat(),
                "base_url": base_url,
                "failure_class": "configuration_failure",
                "load_error": load_error
            },
            "results": []
        }
        if args.write_report:
            try:
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

        # Step summary write on load error
        summary_env = os.getenv("GITHUB_STEP_SUMMARY")
        if summary_env:
            try:
                with open(summary_env, "a", encoding="utf-8") as sf:
                    sf.write("### Golden Oracle Regression Gate Report\n")
                    sf.write(f"❌ **FAILED**: Configuration Error\n")
                    sf.write(f"- **Details**: {load_error}\n")
                    sf.write(f"- **Overall Class**: `CONFIGURATION_FAILURE`\n")
            except Exception:
                pass

        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print(f"Error: {load_error}", file=sys.stderr)
        sys.exit(3)

    for case in cases:
        case_id = case.get("id")
        question = case.get("question")
        chapter_progress = case.get("chapter_progress", 1)
        must_not_contain = case.get("must_not_contain") or []
        semantic_forbidden_patterns = case.get("semantic_forbidden_patterns") or []
        semantic_required_any_terms = case.get("semantic_required_any_terms") or []
        acceptable_abstain = case.get("acceptable_abstain", False)
        expected_abstain_text = case.get("expected_abstain_text", "")
        status = case.get("status", "active")

        if status != "active":
            continue

        url = f"{base_url}/oracle/ask"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        body = {
            "question": question,
            "chapter_progress": chapter_progress
        }

        # Case-level states
        passed = True
        reason = "All validation checks passed."
        answer = ""
        source = "unknown"
        failure_class = "none"

        attempts_run = 0
        http_statuses = []
        attempt_latencies_ms = []
        last_exception_type = None
        last_exception_message = None

        for attempt in range(1, args.infra_retries + 1 + 1):
            attempts_run = attempt
            t0 = time.time()
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")

            passed = True
            reason = "All validation checks passed."
            answer = ""
            source = "unknown"
            status_code = None
            exception_type = None
            exception_msg = None

            try:
                with urllib.request.urlopen(req, context=ctx, timeout=args.request_timeout) as resp:
                    status_code = resp.status
                    http_statuses.append(status_code)
                    latency = int((time.time() - t0) * 1000)
                    attempt_latencies_ms.append(latency)

                    if status_code != 200:
                        passed = False
                        reason = f"HTTP request failed with status: {status_code}"
                    else:
                        res_body = json.loads(resp.read().decode("utf-8"))
                        answer = res_body.get("answer", "")
                        source = res_body.get("source", "")

                        # 1. must_not_contain
                        for term in must_not_contain:
                            if term.lower() in answer.lower():
                                passed = False
                                reason = f"Answer contains forbidden term: '{term}'"
                                failure_class = "semantic_failure"
                                break

                        # 2. semantic_forbidden_patterns
                        if passed:
                            for pattern in semantic_forbidden_patterns:
                                if pattern.lower() in answer.lower():
                                    passed = False
                                    reason = f"Answer contains semantic forbidden pattern: '{pattern}'"
                                    failure_class = "semantic_failure"
                                    break

                        # 3. Check abstain vs semantic_required_any_terms
                        if passed:
                            is_abstain = False
                            if expected_abstain_text:
                                clean_ans = "".join(answer.lower().split())
                                clean_exp = "".join(expected_abstain_text.lower().split())
                                if clean_exp in clean_ans or clean_ans in clean_exp:
                                    is_abstain = True

                            if is_abstain:
                                if not acceptable_abstain:
                                    passed = False
                                    reason = "Answer is an abstain response, but abstain is not acceptable for this case."
                                    failure_class = "semantic_failure"
                            else:
                                if semantic_required_any_terms:
                                    has_any = any(term.lower() in answer.lower() for term in semantic_required_any_terms)
                                    if not has_any:
                                        passed = False
                                        reason = f"Answer is not abstain and does not contain any semantic_required_any_terms: {semantic_required_any_terms}"
                                        failure_class = "semantic_failure"
            except Exception as e:
                latency = int((time.time() - t0) * 1000)
                attempt_latencies_ms.append(latency)
                passed = False
                reason = f"HTTP request triggered exception: {e}"

                if hasattr(e, "code"):
                    status_code = e.code
                    http_statuses.append(status_code)
                else:
                    http_statuses.append("Error")

                exception_type = type(e).__name__
                exception_msg = str(e)
                last_exception_type = exception_type
                last_exception_message = exception_msg

            # Handle retries for infrastructure issues
            if not passed:
                is_infra_error = False

                # Check for network issues or timeout exceptions
                if exception_type is not None:
                    if "timeout" in exception_type.lower() or "timeout" in exception_msg.lower() or "timed out" in exception_msg.lower():
                        is_infra_error = True
                    elif "connection" in exception_msg.lower() or "refused" in exception_msg.lower() or "reset" in exception_msg.lower() or "dns" in exception_msg.lower() or "urlerror" in exception_type.lower():
                        is_infra_error = True

                # Check for specific HTTP statuses
                if status_code in [429, 502, 503, 504]:
                    is_infra_error = True

                if is_infra_error:
                    failure_class = "infra_failure"
                    if attempt < args.infra_retries + 1:
                        # Print retry message if not json mode
                        if not args.json:
                            print(f"[Attempt {attempt} Fail - Infra Error] {reason}. Retrying in {args.infra_backoff_seconds}s...")
                        time.sleep(args.infra_backoff_seconds)
                        continue
                    else:
                        break
                else:
                    # Semantic error or other HTTP error (e.g. 400, 404, 500)
                    if failure_class == "none":
                        if status_code == 500:
                            failure_class = "infra_failure"
                        else:
                            failure_class = "semantic_failure"  # Default non-infra HTTP failure class to semantic

                    # For system_canary, allow up to 2 attempts to confirm semantic failure
                    if case.get("source") == "system_canary" and failure_class == "semantic_failure" and attempt < 2:
                        if not args.json:
                            print(f"[Attempt {attempt} Fail - Semantic check] {reason}. Retrying to confirm...")
                        time.sleep(2)
                        continue
                    break
            else:
                failure_class = "none"
                if attempt > 1:
                    retry_recovered += 1
                break

        total_attempts += attempts_run

        if passed:
            passed_count += 1
        else:
            failed_count += 1
            if failure_class == "semantic_failure":
                semantic_failed += 1
            elif failure_class == "infra_failure":
                infra_failed += 1
            elif failure_class == "configuration_failure":
                configuration_failed += 1

        results.append({
            "case_id": case_id,
            "question": question,
            "passed": passed,
            "reason": reason,
            "answer": answer,
            "source": source,
            # new fields
            "failure_class": failure_class,
            "attempts": attempts_run,
            "request_timeout_seconds": args.request_timeout,
            "http_statuses": http_statuses,
            "attempt_latencies_ms": attempt_latencies_ms,
            "last_exception_type": last_exception_type,
            "last_exception_message": last_exception_message,
            "production_git_commit": prod_git_commit,
            "workflow_sha": os.getenv("GITHUB_SHA")
        })

    if len(results) == 0:
        configuration_failed = 1
        overall_class = "configuration_failure"
    elif semantic_failed > 0:
        overall_class = "semantic_failure"
    elif infra_failed > 0:
        overall_class = "infra_failure"
    else:
        overall_class = "none"
    # Isolate auto-rollback logic for database sources (semantic failures of autonomous system canary only)
    rollback_eligible = False
    if args.source == "db" and failed_count > 0:
        print("\n=== POST-PROMOTION FAILURE DETECTED: EVALUATING AUTOMATIC ROLLBACK ===")
        try:
            supabase = _get_supabase_client()

            for r in results:
                if not r["passed"]:
                    case_key = r["case_id"]

                    # Find actual case object
                    actual_case = next((c for c in cases if c.get("id") == case_key), {})
                    source_from_case = actual_case.get("source")

                    eligible = False
                    skip_reason = ""

                    if r.get("failure_class") != "semantic_failure":
                        skip_reason = f"Failure class is {r.get('failure_class')}, not semantic_failure"
                    elif source_from_case != "system_canary":
                        skip_reason = f"Case source is {source_from_case}, not system_canary"
                    else:
                        # Fetch candidate
                        cand_res = supabase.table("oracle_golden_regression_candidates").select("*").eq("candidate_key", case_key).execute()
                        if cand_res.data:
                            candidate = cand_res.data[0]
                            evidence = candidate.get("evidence") or {}
                            trust_verification = evidence.get("trust_verification") or {}

                            trust_verified = trust_verification.get("trust_verified") or (candidate.get("trust_level") == "system")
                            source_verified = trust_verification.get("source_verified") or (candidate.get("source") == "system_canary")
                            method = trust_verification.get("trust_verification_method")
                            promotion_status = candidate.get("promotion_status")

                            if promotion_status != "auto_promoted":
                                skip_reason = f"Candidate status is {promotion_status}, not auto_promoted"
                            elif not trust_verified:
                                skip_reason = "Candidate trust_verified is false"
                            elif not source_verified:
                                skip_reason = "Candidate source_verified is false"
                            elif method != "internal_backend_canary":
                                skip_reason = f"Candidate verification method is {method}, not internal_backend_canary"
                            else:
                                eligible = True
                        else:
                            skip_reason = f"No linked candidate found for case_key {case_key}"

                    if eligible:
                        rollback_eligible = True
                        if args.rollback_mode == "verified-canary":
                            print(f"Rolling back case: {case_key}")
                            # Disable case in registry (do NOT delete)
                            supabase.table("oracle_golden_regression_cases").update({"status": "disabled"}).eq("case_key", case_key).execute()
                            case_disabled_count += 1
                            rollback_case_keys.append(case_key)

                            # Update candidate status to canary_rolled_back
                            supabase.table("oracle_golden_regression_candidates").update({
                                "promotion_status": "canary_rolled_back",
                                "promotion_reason": f"Rollback: Regression failed. Reason: {r['reason']}"
                            }).eq("candidate_key", case_key).execute()
                            candidate_rolled_back_count += 1
                            rollback_candidate_keys.append(case_key)
                        else:
                            print(f"Eligible for rollback but skipped because rollback-mode is off: {case_key}")
                            rollback_skipped_reasons[case_key] = "Rollback mode is off"
                    else:
                        print(f"Skipping rollback for case: {case_key}. Reason: {skip_reason}")
                        rollback_skipped_reasons[case_key] = skip_reason

            # Prove remaining active cases pass by querying them and running verification (only if rollback performed)
            if case_disabled_count > 0:
                res_remaining = supabase.table("oracle_golden_regression_cases").select("*").eq("status", "active").execute()
                remaining_cases = res_remaining.data or []
                print(f"Remaining active cases to verify: {len(remaining_cases)}")

                remaining_passed = True
                for rc in remaining_cases:
                    rc_url = f"{base_url}/oracle/ask"
                    rc_body = {
                        "question": rc.get("question"),
                        "chapter_progress": rc.get("chapter_progress", 1)
                    }
                    rc_req = urllib.request.Request(rc_url, data=json.dumps(rc_body).encode("utf-8"), headers=headers, method="POST")
                    try:
                        with urllib.request.urlopen(rc_req, context=ctx, timeout=20) as rc_resp:
                            if rc_resp.status != 200:
                                remaining_passed = False
                            else:
                                rc_res_body = json.loads(rc_resp.read().decode("utf-8"))
                                rc_answer = rc_res_body.get("answer", "")
                                for term in rc.get("must_not_contain") or []:
                                    if term.lower() in rc_answer.lower():
                                        remaining_passed = False
                                for pattern in rc.get("semantic_forbidden_patterns") or []:
                                    if pattern.lower() in rc_answer.lower():
                                        remaining_passed = False
                    except Exception:
                        remaining_passed = False

                print(f"Re-check of remaining active cases passed: {remaining_passed}")
        except Exception as rollback_err:
            print(f"Error during automatic rollback: {rollback_err}", file=sys.stderr)

    report = {
        "summary": {
            "total": len(results),
            "passed": passed_count,
            "failed": failed_count,
            "semantic_failed": semantic_failed,
            "infra_failed": infra_failed,
            "configuration_failed": configuration_failed,
            "retry_recovered": retry_recovered,
            "total_attempts": total_attempts,
            "run_at": datetime.now(timezone.utc).isoformat(),
            "base_url": base_url,
            "failure_class": overall_class,
            "case_disabled_count": case_disabled_count,
            "candidate_rolled_back_count": candidate_rolled_back_count,
            "rollback_case_keys": rollback_case_keys,
            "rollback_candidate_keys": rollback_candidate_keys,
            "rollback_skipped_reasons": rollback_skipped_reasons,
            "rollback_performed": case_disabled_count > 0,
            "rollback_mode": args.rollback_mode,
            "rollback_eligible": rollback_eligible,
            "source": args.source,
            "production_git_commit": prod_git_commit,
            "workflow_sha": os.getenv("GITHUB_SHA")
        },
        "results": results
    }

    if args.write_report:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("=== GOLDEN REGRESSION TEST SUMMARY ===")
        print(f"Base URL: {base_url}")
        print(f"Total Cases: {report['summary']['total']}")
        print(f"Passed:      {report['summary']['passed']}")
        print(f"Failed:      {report['summary']['failed']}")
        print(f"Overall Class: {overall_class.upper()}")
        print("======================================")
        for r in results:
            status_str = "PASS" if r["passed"] else "FAIL"
            print(f"[{status_str}] Case: {r['case_id']} (Class: {r['failure_class']})")
            print(f"  Reason: {r['reason']}")

    # Write runs to database if requested
    if args.write_db_run and len(results) > 0:
        try:
            supabase = _get_supabase_client()

            workflow_run_id = os.getenv("GITHUB_RUN_ID")
            run_payloads = []
            for r in results:
                status_code = 200
                if r["http_statuses"]:
                    # Get last valid status or fallback
                    last_status = r["http_statuses"][-1]
                    if isinstance(last_status, int):
                        status_code = last_status
                    else:
                        status_code = 500

                run_payloads.append({
                    "case_key": r["case_id"],
                    "base_url": base_url,
                    "passed": r["passed"],
                    "reason": r["reason"],
                    "answer_excerpt": r["answer"][:500] if r["answer"] else None,
                    "source": r["source"],
                    "response_status": status_code,
                    "git_commit": prod_git_commit or os.getenv("GITHUB_SHA"),
                    "workflow_run_id": workflow_run_id
                })
            if run_payloads:
                supabase.table("oracle_golden_regression_runs").insert(run_payloads).execute()
        except Exception as e:
            print(f"Warning: Failed to write run results to database: {e}", file=sys.stderr)

    # Write to GitHub Step Summary
    summary_env = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_env:
        try:
            with open(summary_env, "a", encoding="utf-8") as sf:
                sf.write("### Golden Oracle Regression Gate Report\n")
                if overall_class == "none":
                    sf.write("✅ **ALL CASES PASSED**\n")
                elif overall_class == "semantic_failure":
                    sf.write("❌ **FAILED**: ORACLE SEMANTIC REGRESSION DETECTED\n")
                elif overall_class == "infra_failure":
                    sf.write("⚠️ **FAILED**: INFRASTRUCTURE FAILURE (TEST SUITE WARM-UP/RETRIES EXHAUSTED)\n")
                else:
                    sf.write("❌ **FAILED**: CONFIGURATION ERROR\n")

                sf.write(f"- **Production Commit**: `{prod_git_commit or 'unknown'}`\n")
                sf.write(f"- **Total Cases**: {report['summary']['total']}\n")
                sf.write(f"- **Passed**: {report['summary']['passed']}\n")
                sf.write(f"- **Failed**: {report['summary']['failed']}\n")
                sf.write(f"- **Semantic Failures**: {report['summary']['semantic_failed']}\n")
                sf.write(f"- **Infra Failures**: {report['summary']['infra_failed']}\n")
                sf.write(f"- **Retries Recovered**: {report['summary']['retry_recovered']}\n")
                sf.write(f"- **Overall Failure Class**: `{overall_class.upper()}`\n\n")

                sf.write("| Case ID | Status | Class | Attempts | Reason | Source |\n")
                sf.write("|---|---|---|---|---|---|\n")
                for r in results:
                    status_str = "✅ PASS" if r["passed"] else "❌ FAIL"
                    sf.write(f"| `{r['case_id']}` | {status_str} | `{r['failure_class']}` | {r['attempts']} | {r['reason']} | `{r['source']}` |\n")
        except Exception as se:
            print(f"Warning: Failed to write to GITHUB_STEP_SUMMARY: {se}", file=sys.stderr)

    # Post-promotion rollback re-check printout or details if any rollback occurred
    if args.source == "db" and failed_count > 0 and case_disabled_count > 0:
        print("Rollback performed successfully. Classification: FAIL_PHASE_11E3_CANARY_AUTO_ROLLED_BACK")

    if len(results) == 0:
        sys.exit(3)

    if overall_class == "semantic_failure":
        sys.exit(1)
    elif overall_class == "infra_failure":
        sys.exit(2)
    elif overall_class == "configuration_failure":
        sys.exit(3)
    else:
        sys.exit(0)


if __name__ == "__main__":
    run_regression()
