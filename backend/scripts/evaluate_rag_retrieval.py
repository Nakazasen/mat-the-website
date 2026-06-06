import os
import sys
import asyncio
import argparse
import json

# Ensure correct path resolution
backend_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
parent_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website"
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

try:
    from main import supabase
except ImportError:
    from backend.main import supabase

from backend.rag.evaluator import evaluate_all_cases, load_eval_cases

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

async def run_evaluation(args):
    # Filter cases
    cases = load_eval_cases(args.case_source)
    if args.intent:
        cases = [c for c in cases if c.get("intent") == args.intent]

    if args.limit:
        cases = cases[:args.limit]

    if not cases:
        print_safe("Warning: No evaluation cases matched the filters.")
        sys.exit(0)

    # Run evaluator
    result = await evaluate_all_cases(cases, supabase, case_source=args.case_source)

    if args.json:
        # Output as JSON
        output_str = json.dumps(result, indent=2, ensure_ascii=False)
        print_safe(output_str)
    else:
        # Output as user-friendly text format
        print_safe("=" * 60)
        print_safe("           RAG RETRIEVAL PIPELINE EVALUATION")
        print_safe("=" * 60)
        print_safe(f"Case Source          : {result['case_source']}")
        print_safe(f"Total cases evaluated : {result['total']}")
        print_safe(f"Passed cases         : {result['passed']}")
        print_safe(f"Failed cases         : {result['failed']}")
        print_safe(f"Overall Pass Rate    : {result['pass_rate']:.2%}")

        if "feedback_cases_count" in result:
            print_safe(f"Feedback cases count : {result['feedback_cases_count']}")

        if result.get("duplicate_ids"):
            print_safe(f"Duplicate Case IDs   : {', '.join(result['duplicate_ids'])}")

        print_safe("-" * 60)
        print_safe("PASS RATE BY INTENT:")
        for intent, stats in result["by_intent"].items():
            print_safe(f"  - {intent:<15}: {stats['passed']}/{stats['total']} ({stats['pass_rate']:.2%})")

        if result["failures"]:
            print_safe("-" * 60)
            print_safe("DETAILED FAILURES:")
            for fail in result["failures"]:
                print_safe(f"  [Case ID: {fail['id']}] Q: '{fail['question']}'")
                for reason in fail["fail_reasons"]:
                    print_safe(f"    - {reason}")

        if args.report_missing_entities:
            missing_entities = []
            for r in result.get("results", []):
                if r.get("missing_entity_context") and r.get("entity_name"):
                    missing_entities.append(r["entity_name"])
            deduped = []
            for ent in missing_entities:
                if ent not in deduped:
                    deduped.append(ent)
            print_safe("-" * 60)
            print_safe("Missing entity/wiki profiles:")
            for ent in deduped:
                print_safe(f"- {ent}")

        print_safe("=" * 60)

    # Failure Report Generation
    if args.failure_report:
        from backend.rag.eval_failure_analysis import analyze_evaluation_failures
        analysis = analyze_evaluation_failures(result)

        # Write report to file
        os.makedirs(os.path.dirname(os.path.abspath(args.failure_report_output)), exist_ok=True)
        try:
            with open(args.failure_report_output, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            if not args.json:
                print_safe("-" * 60)
                print_safe(f"FAILURE ANALYSIS REPORT EXPORTED TO: {args.failure_report_output}")
                print_safe("-" * 60)
                print_safe(f"Total Failure Cases  : {analysis['total_failures']}")
                print_safe(f"Feedback Failures    : {analysis['feedback_failures']}")
                print_safe("\nFAILURES BY REASON:")
                for reason, count in analysis["by_reason"].items():
                    if count > 0:
                        print_safe(f"  - {reason:<40}: {count}")
                print_safe("\nFAILURES BY INTENT:")
                for intent, count in analysis["by_intent"].items():
                    print_safe(f"  - {intent:<15}: {count}")
                if analysis["top_missing_entities"]:
                    print_safe("\nTOP MISSING ENTITIES:")
                    for ent_info in analysis["top_missing_entities"]:
                        print_safe(f"  - {ent_info['entity']}: {ent_info['count']} failures")
                if analysis["recommended_next_actions"]:
                    print_safe("\nRECOMMENDED NEXT ACTIONS:")
                    for action in analysis["recommended_next_actions"]:
                        print_safe(f"  * {action}")
                print_safe("=" * 60)
        except Exception as e:
            print_safe(f"Error writing failure report: {e}")

    # Exit code based on fail-under
    if result["pass_rate"] < args.fail_under:
        print_safe(f"Evaluation FAILED: Pass rate {result['pass_rate']:.2%} is below threshold {args.fail_under:.2%}")
        sys.exit(1)
    else:
        print_safe("Evaluation PASSED successfully!")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Evaluate RAG retrieval and anti-spoiler pipeline quality.")
    parser.add_argument("--case-source", type=str, choices=["base", "feedback", "all"], default="base", help="Select evaluation case source: base, feedback, or all.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of cases to evaluate.")
    parser.add_argument("--intent", type=str, default=None, help="Filter cases by intent.")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format.")
    parser.add_argument("--fail-under", type=float, default=0.7, help="Minimum acceptable overall pass rate (default: 0.7).")
    parser.add_argument("--report-missing-entities", action="store_true", help="Report missing entity wiki profiles for identity cases.")
    parser.add_argument("--failure-report", action="store_true", help="Perform structured failure analysis on failed evaluation cases.")
    parser.add_argument("--failure-report-output", type=str, default="backend/rag/generated_eval_failure_report.json", help="File path to write the JSON failure analysis report.")

    args = parser.parse_args()

    # Run async loop
    asyncio.run(run_evaluation(args))

if __name__ == "__main__":
    main()
