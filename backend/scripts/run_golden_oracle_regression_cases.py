import sys
import os
import json
import urllib.request
import argparse
import ssl
from datetime import datetime, timezone

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

    args = parser.parse_args()
    base_url = args.base_url.rstrip('/')

    # Path to regression cases
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    cases_path = os.path.join(repo_root, "rag", "golden_oracle_regression_cases.json")
    report_path = os.path.join(repo_root, "rag", "generated_golden_oracle_regression_report.json")

    if not os.path.exists(cases_path):
        print(f"Error: Cases file not found at {cases_path}", file=sys.stderr)
        sys.exit(1)

    with open(cases_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    results = []
    passed_count = 0
    failed_count = 0

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

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

        passed = True
        reason = "All validation checks passed."
        answer = ""
        source = "unknown"

        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
                if resp.status != 200:
                    passed = False
                    reason = f"HTTP request failed with status: {resp.status}"
                else:
                    res_body = json.loads(resp.read().decode("utf-8"))
                    answer = res_body.get("answer", "")
                    source = res_body.get("source", "")

                    # 1. must_not_contain
                    for term in must_not_contain:
                        if term.lower() in answer.lower():
                            passed = False
                            reason = f"Answer contains forbidden term: '{term}'"
                            break

                    # 2. semantic_forbidden_patterns
                    if passed:
                        for pattern in semantic_forbidden_patterns:
                            if pattern.lower() in answer.lower():
                                passed = False
                                reason = f"Answer contains semantic forbidden pattern: '{pattern}'"
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
                        else:
                            if semantic_required_any_terms:
                                has_any = any(term.lower() in answer.lower() for term in semantic_required_any_terms)
                                if not has_any:
                                    passed = False
                                    reason = f"Answer is not abstain and does not contain any semantic_required_any_terms: {semantic_required_any_terms}"
        except Exception as e:
            passed = False
            reason = f"HTTP request triggered exception: {e}"

        if passed:
            passed_count += 1
        else:
            failed_count += 1

        results.append({
            "case_id": case_id,
            "question": question,
            "passed": passed,
            "reason": reason,
            "answer": answer,
            "source": source
        })

    report = {
        "summary": {
            "total": len(results),
            "passed": passed_count,
            "failed": failed_count,
            "run_at": datetime.now(timezone.utc).isoformat(),
            "base_url": base_url
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
        print("======================================")
        for r in results:
            status_str = "PASS" if r["passed"] else "FAIL"
            print(f"[{status_str}] Case: {r['case_id']}")
            print(f"  Reason: {r['reason']}")

    if len(results) == 0:
        if not args.json:
            print("Error: No active regression cases found.", file=sys.stderr)
        sys.exit(1)

    if failed_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    run_regression()
