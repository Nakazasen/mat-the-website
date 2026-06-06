import argparse
import json
import os
import sys
from typing import Any, Dict, List

# Add parent directory and backend directory to path
sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from dotenv import load_dotenv

# Try importing from backend or local
try:
    from backend.rag.correction_review import (
        summarize_correction_review,
        build_rag_correction_payload,
    )
except ImportError:
    from rag.correction_review import (
        summarize_correction_review,
        build_rag_correction_payload,
    )

def main():
    parser = argparse.ArgumentParser(description="Review and validate RAG correction drafts.")
    parser.add_argument("--input", default="backend/rag/generated_feedback_corrections.json", help="Path to input JSON file containing correction drafts (default: backend/rag/generated_feedback_corrections.json).")
    parser.add_argument("--json", action="store_true", help="Print output to stdout in formatted JSON.")
    parser.add_argument("--write-corrections", action="store_true", help="Write valid correction drafts to database with status 'draft'.")
    parser.add_argument("--fail-on-invalid", action="store_true", help="Exit with code 1 if any invalid draft is found.")

    args = parser.parse_args()

    # 1. Read input JSON
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading or parsing input file '{args.input}': {e}", file=sys.stderr)
        sys.exit(1)

    corrections = data.get("corrections")
    if corrections is None:
        # Check if root is a list or contains it directly
        if isinstance(data, list):
            corrections = data
        else:
            corrections = []

    # 2. Run validation review
    summary = summarize_correction_review(corrections)

    # 3. Handle fail-on-invalid
    if args.fail_on_invalid and summary["invalid"] > 0:
        print(f"Validation failed: Found {summary['invalid']} invalid correction drafts.", file=sys.stderr)
        # print details
        for r in summary["reports"]:
            if not r["valid"]:
                print(f"  - Draft {r['draft'].get('feedback_id') or 'unknown'}: {', '.join(r['errors'])}", file=sys.stderr)
        sys.exit(1)

    # 4. Handle DB write
    inserted_count = 0
    failure_count = 0

    if args.write_corrections and summary["eligible_insert"] > 0:
        # Load env files
        load_dotenv("backend/.env", override=True)
        load_dotenv(override=True)

        # Initialize Supabase client
        try:
            from main import supabase
        except ImportError:
            try:
                from backend.main import supabase
            except ImportError:
                supabase = None

        if not supabase:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if url and key:
                try:
                    from supabase import create_client
                    supabase = create_client(url, key)
                except Exception as e:
                    print(f"Error initializing Supabase client: {e}", file=sys.stderr)

        if not supabase:
            print("Error: Supabase client could not be initialized. Cannot write to DB.", file=sys.stderr)
            sys.exit(1)

        # Write valid drafts
        for report in summary["reports"]:
            if report["eligible_insert"]:
                payload = build_rag_correction_payload(report["draft"])
                if payload:
                    try:
                        # Check duplicate
                        existing = supabase.table("rag_corrections").select("id").eq("feedback_id", payload["feedback_id"]).execute()
                        if not existing.data:
                            supabase.table("rag_corrections").insert(payload).execute()
                            inserted_count += 1
                    except Exception as e:
                        print(f"Error inserting correction for {payload['feedback_id']}: {e}", file=sys.stderr)
                        failure_count += 1

    # 5. Output results
    run_summary = {
        "total": summary["total"],
        "valid": summary["valid"],
        "invalid": summary["invalid"],
        "eligible_insert": summary["eligible_insert"],
        "warnings": summary["warnings"],
        "eval_cases_detected": summary["eval_cases_detected"],
        "database_writes": {
            "requested": args.write_corrections,
            "inserted": inserted_count,
            "failed": failure_count
        }
    }

    if args.json:
        # Print JSON report
        print(json.dumps(run_summary, ensure_ascii=False, indent=2))
    else:
        print("Correction drafts review completed.")
        print(f" - Total drafts: {run_summary['total']}")
        print(f" - Valid drafts: {run_summary['valid']}")
        print(f" - Invalid drafts: {run_summary['invalid']}")
        print(f" - Warnings triggered: {run_summary['warnings']}")
        print(f" - Eval cases detected: {run_summary['eval_cases_detected']}")
        if args.write_corrections:
            print(f" - DB inserts succeeded: {inserted_count}")
            print(f" - DB inserts failed: {failure_count}")
        else:
            print(" - Local check dry-run (no database writes performed).")

if __name__ == "__main__":
    main()
