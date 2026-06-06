import argparse
import json
import os
import sys
from typing import Any, Dict, List

# Add parent directory and backend directory to path
sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from dotenv import load_dotenv

# Try importing from backend, or local path
try:
    from backend.rag.feedback_corrections import (
        build_correction_draft_from_feedback,
        build_eval_case_from_feedback,
    )
except ImportError:
    from rag.feedback_corrections import (
        build_correction_draft_from_feedback,
        build_eval_case_from_feedback,
    )

def main():
    parser = argparse.ArgumentParser(description="Generate RAG correction drafts and eval cases from admin-reviewed feedback.")
    parser.add_argument("--status", choices=["accepted", "resolved"], help="Filter feedback by status (accepted or resolved). If not specified, fetches both.")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of feedback items to process (default: 50).")
    parser.add_argument("--output", default="backend/rag/generated_feedback_corrections.json", help="Path to write the output JSON (default: backend/rag/generated_feedback_corrections.json).")
    parser.add_argument("--write-corrections", action="store_true", help="Insert generated correction drafts into the rag_corrections table in database.")
    parser.add_argument("--json", action="store_true", help="Print output to stdout in JSON format.")

    args = parser.parse_args()

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
        # Check if environment keys are defined
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url and key:
            try:
                from supabase import create_client
                supabase = create_client(url, key)
            except Exception as e:
                print(f"Error initializing Supabase client: {e}", file=sys.stderr)

    if not supabase:
        print("Error: Supabase client could not be initialized. Please configure backend/.env or system environment variables.", file=sys.stderr)
        sys.exit(1)

    try:
        # Build query
        query = supabase.table("rag_feedback").select("*")
        if args.status:
            query = query.eq("status", args.status)
        else:
            query = query.in_("status", ["accepted", "resolved"])

        res = query.order("created_at", desc=True).limit(args.limit).execute()
        feedbacks = res.data or []
    except Exception as e:
        print(f"Error querying database for feedback: {e}", file=sys.stderr)
        sys.exit(1)

    corrections = []
    eval_cases = []

    for fb in feedbacks:
        # 1. Create correction draft
        corr = build_correction_draft_from_feedback(fb)
        corrections.append(corr)

        # 2. Create eval case
        ev = build_eval_case_from_feedback(fb)
        if ev:
            eval_cases.append(ev)

    output_data = {
        "corrections": corrections,
        "eval_cases": eval_cases
    }

    # Ensure parent directory of output exists
    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error writing output file {args.output}: {e}", file=sys.stderr)
        sys.exit(1)

    # Write to database if requested
    inserted_count = 0
    if args.write_corrections and corrections:
        try:
            for corr in corrections:
                # Check if correction for this feedback already exists
                existing = supabase.table("rag_corrections").select("id").eq("feedback_id", corr["feedback_id"]).execute()
                if not existing.data:
                    supabase.table("rag_corrections").insert(corr).execute()
                    inserted_count += 1
        except Exception as e:
            print(f"Error inserting corrections to DB: {e}", file=sys.stderr)
            sys.exit(1)

    summary = {
        "feedbacks_processed": len(feedbacks),
        "corrections_generated": len(corrections),
        "eval_cases_generated": len(eval_cases),
        "corrections_written_to_db": inserted_count,
        "output_path": args.output
    }

    if args.json:
        # Print output to stdout
        print(json.dumps({**summary, "data": output_data}, ensure_ascii=False, indent=2))
    else:
        print(f"Processing complete.")
        print(f" - Feedbacks processed: {len(feedbacks)}")
        print(f" - Correction drafts generated: {len(corrections)}")
        print(f" - Eval cases generated: {len(eval_cases)}")
        print(f" - Correction drafts written to database: {inserted_count}")
        print(f" - Output saved to: {args.output}")

if __name__ == "__main__":
    main()
