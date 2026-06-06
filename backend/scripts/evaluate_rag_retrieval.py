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

from backend.rag.eval_cases import EVAL_CASES
from backend.rag.evaluator import evaluate_all_cases

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

async def run_evaluation(args):
    # Filter cases
    cases = EVAL_CASES
    if args.intent:
        cases = [c for c in cases if c.get("intent") == args.intent]
        
    if args.limit:
        cases = cases[:args.limit]
        
    if not cases:
        print_safe("Warning: No evaluation cases matched the filters.")
        sys.exit(0)
        
    # Run evaluator
    result = await evaluate_all_cases(cases, supabase)
    
    if args.json:
        # Output as JSON
        output_str = json.dumps(result, indent=2, ensure_ascii=False)
        print_safe(output_str)
    else:
        # Output as user-friendly text format
        print_safe("=" * 60)
        print_safe("           RAG RETRIEVAL PIPELINE EVALUATION")
        print_safe("=" * 60)
        print_safe(f"Total cases evaluated : {result['total']}")
        print_safe(f"Passed cases         : {result['passed']}")
        print_safe(f"Failed cases         : {result['failed']}")
        print_safe(f"Overall Pass Rate    : {result['pass_rate']:.2%}")
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
        print_safe("=" * 60)
        
    # Exit code based on fail-under
    if result["pass_rate"] < args.fail_under:
        print_safe(f"Evaluation FAILED: Pass rate {result['pass_rate']:.2%} is below threshold {args.fail_under:.2%}")
        sys.exit(1)
    else:
        print_safe("Evaluation PASSED successfully!")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Evaluate RAG retrieval and anti-spoiler pipeline quality.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of cases to evaluate.")
    parser.add_argument("--intent", type=str, default=None, help="Filter cases by intent.")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format.")
    parser.add_argument("--fail-under", type=float, default=0.7, help="Minimum acceptable overall pass rate (default: 0.7).")
    
    args = parser.parse_args()
    
    # Run async loop
    asyncio.run(run_evaluation(args))

if __name__ == "__main__":
    main()
