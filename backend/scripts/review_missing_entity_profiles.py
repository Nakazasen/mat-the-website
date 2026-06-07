import argparse
import json
import os
import sys
from typing import Any, Dict, List

# Ensure parent directory and backend directory are in python path
backend_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
parent_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website"
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

from dotenv import load_dotenv

try:
    from backend.rag.entity_profile_review import (
        summarize_entity_profile_review,
        build_entity_profile_correction_payload,
    )
except ImportError:
    from rag.entity_profile_review import (
        summarize_entity_profile_review,
        build_entity_profile_correction_payload,
    )

def print_safe(text, to_stderr=False):
    """Safely print text on Windows consoles to prevent encoding errors."""
    file = sys.stderr if to_stderr else sys.stdout
    try:
        print(text, file=file)
    except UnicodeEncodeError:
        try:
            print(text.encode('ascii', errors='backslashreplace').decode('ascii'), file=file)
        except Exception:
            print(text.encode('utf-8', errors='ignore'), file=file)

def main():
    parser = argparse.ArgumentParser(description="Review and validate missing entity profile drafts.")
    parser.add_argument("--input", default="backend/rag/generated_missing_entity_profiles.json", help="Path to input JSON file containing profile drafts (default: backend/rag/generated_missing_entity_profiles.json).")
    parser.add_argument("--json", action="store_true", help="Print output to stdout in formatted JSON.")
    parser.add_argument("--write-corrections", action="store_true", help="Write valid profile drafts to database with status 'draft'.")
    parser.add_argument("--fail-on-invalid", action="store_true", help="Exit with code 1 if any invalid draft is found.")

    args = parser.parse_args()

    # 1. Read input JSON
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print_safe(f"Error: Input file '{args.input}' not found.", to_stderr=True)
        sys.exit(1)

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            drafts = json.load(f)
    except Exception as e:
        print_safe(f"Error reading or parsing input file '{args.input}': {e}", to_stderr=True)
        sys.exit(1)

    if not isinstance(drafts, list):
        print_safe("Error: Input file must contain a list of profile drafts.", to_stderr=True)
        sys.exit(1)

    # 2. Run validation review
    summary = summarize_entity_profile_review(drafts)

    # 3. Handle fail-on-invalid
    if args.fail_on_invalid and summary["invalid"] > 0:
        print_safe(f"Validation failed: Found {summary['invalid']} invalid profile drafts.", to_stderr=True)
        for r in summary["reports"]:
            if not r["valid"]:
                name = r["draft"].get("entity_name") or "unknown"
                print_safe(f"  - Draft {name}: {', '.join(r['errors'])}", to_stderr=True)
        sys.exit(1)

    # 4. Handle DB write
    inserted_count = 0
    failure_count = 0

    if args.write_corrections and summary["eligible_insert"] > 0:
        # Load env files
        load_dotenv("backend/.env", override=True)
        load_dotenv(override=True)

        # Initialize Supabase client
        supabase = None
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
                    print_safe(f"Error initializing Supabase client: {e}", to_stderr=True)

        if not supabase:
            print_safe("Error: Supabase client could not be initialized. Cannot write to DB.", to_stderr=True)
            sys.exit(1)

        # Write valid drafts
        for report in summary["reports"]:
            if report["eligible_insert"]:
                payload = build_entity_profile_correction_payload(report["draft"])
                if payload:
                    try:
                        # Check duplicate by entity_name and correction_type
                        existing = (
                            supabase.table("rag_corrections")
                            .select("id")
                            .eq("entity_name", payload["entity_name"])
                            .eq("correction_type", "entity_profile")
                            .execute()
                        )
                        if not existing.data:
                            supabase.table("rag_corrections").insert(payload).execute()
                            inserted_count += 1
                    except Exception as e:
                        name = payload.get("entity_name") or "unknown"
                        print_safe(f"Error inserting correction for {name}: {e}", to_stderr=True)
                        failure_count += 1

    # 5. Output results
    run_summary = {
        "total": summary["total"],
        "valid": summary["valid"],
        "invalid": summary["invalid"],
        "eligible_insert": summary["eligible_insert"],
        "needs_review": summary["needs_review"],
        "with_evidence": summary["with_evidence"],
        "warnings": summary["warnings"],
        "database_writes": {
            "requested": args.write_corrections,
            "inserted": inserted_count,
            "failed": failure_count
        }
    }

    if args.json:
        # Print JSON report
        print_safe(json.dumps(run_summary, ensure_ascii=False, indent=2))
    else:
        print_safe("Missing entity profiles review completed.")
        print_safe(f" - Total drafts: {run_summary['total']}")
        print_safe(f" - Valid drafts: {run_summary['valid']}")
        print_safe(f" - Invalid drafts: {run_summary['invalid']}")
        print_safe(f" - Eligible for DB insert: {run_summary['eligible_insert']}")
        print_safe(f" - Drafts with evidence: {run_summary['with_evidence']}")
        print_safe(f" - Drafts needing review (no evidence): {run_summary['needs_review']}")
        print_safe(f" - Warnings triggered: {run_summary['warnings']}")
        if args.write_corrections:
            print_safe(f" - DB inserts succeeded: {inserted_count}")
            print_safe(f" - DB inserts failed: {failure_count}")
        else:
            print_safe(" - Local check dry-run (no database writes performed).")

if __name__ == "__main__":
    main()
