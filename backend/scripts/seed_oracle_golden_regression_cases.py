import sys
import os
import json
import argparse
from datetime import datetime, timezone

# Add repository root to sys.path to ensure absolute imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Seed Oracle Golden cases from JSON to Supabase DB.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Default dry-run mode (no DB writes).")
    parser.add_argument("--write", action="store_true", help="Actually write updates/upserts to Supabase DB.")
    parser.add_argument("--json", action="store_true", help="Print summary output in JSON format.")

    args = parser.parse_args()
    dry_run = True
    if args.write:
        dry_run = False

    # Path to JSON cases
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    json_path = os.path.join(repo_root, "rag", "golden_oracle_regression_cases.json")

    summary = {
        "read_from_json": 0,
        "existing_db_cases": 0,
        "planned_upserts": 0,
        "written_upserts": 0,
        "skipped_disabled": 0,
        "errors": []
    }

    if not os.path.exists(json_path):
        summary["errors"].append(f"JSON file not found at: {json_path}")
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"Error: {summary['errors'][0]}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            json_cases = json.load(f)
    except Exception as e:
        summary["errors"].append(f"Failed to read JSON: {e}")
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"Error: {summary['errors'][0]}", file=sys.stderr)
        sys.exit(1)

    summary["read_from_json"] = len(json_cases)

    # Initialize Supabase client
    try:
        try:
            from backend.main import supabase
        except ImportError:
            from main import supabase
    except Exception as e:
        summary["errors"].append(f"Failed to initialize Supabase client: {e}")
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"Error: {summary['errors'][0]}", file=sys.stderr)
        sys.exit(1)

    # Fetch existing cases in DB
    existing_db = {}
    try:
        res = supabase.table("oracle_golden_regression_cases").select("*").execute()
        if res.data:
            existing_db = {item["case_key"]: item for item in res.data}
    except Exception as e:
        # Capture database query error (e.g. table may not exist yet)
        summary["errors"].append(f"Database query error (table may not exist): {e}")

    summary["existing_db_cases"] = len(existing_db)

    upsert_payloads = []

    for case in json_cases:
        case_key = case.get("id") or case.get("case_key")
        if not case_key:
            continue

        existing_case = existing_db.get(case_key)

        # Check status: preserve 'disabled' status if already set in DB
        status_to_write = case.get("status", "active")
        if existing_case and existing_case.get("status") == "disabled":
            summary["skipped_disabled"] += 1
            status_to_write = "disabled"

        payload = {
            "case_key": case_key,
            "source": case.get("source", "manual_regression"),
            "question": case.get("question"),
            "chapter_progress": case.get("chapter_progress", 1),
            "intent": case.get("intent", "event_plot"),
            "must_not_contain": case.get("must_not_contain", []),
            "semantic_forbidden_patterns": case.get("semantic_forbidden_patterns", []),
            "semantic_required_any_terms": case.get("semantic_required_any_terms", []),
            "acceptable_abstain": case.get("acceptable_abstain", False),
            "expected_abstain_text": case.get("expected_abstain_text", ""),
            "status": status_to_write,
            "created_from_feedback_id": case.get("created_from_feedback_id")
        }

        if existing_case:
            payload["id"] = existing_case["id"]

        upsert_payloads.append(payload)

    summary["planned_upserts"] = len(upsert_payloads)

    if not dry_run and upsert_payloads:
        written_count = 0
        for payload in upsert_payloads:
            try:
                # Upsert by case_key
                supabase.table("oracle_golden_regression_cases").upsert(payload, on_conflict="case_key").execute()
                written_count += 1
            except Exception as e:
                summary["errors"].append(f"Failed to upsert case '{payload['case_key']}': {e}")
        summary["written_upserts"] = written_count

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print("=== ORACLE GOLDEN REGRESSION SEED SUMMARY ===")
        print(f"Dry Run: {dry_run}")
        print(f"Read from JSON:    {summary['read_from_json']}")
        print(f"Existing DB cases: {summary['existing_db_cases']}")
        print(f"Planned upserts:   {summary['planned_upserts']}")
        print(f"Written upserts:   {summary['written_upserts']}")
        print(f"Skipped disabled:  {summary['skipped_disabled']}")
        if summary["errors"]:
            print("Errors encountered:")
            for err in summary["errors"]:
                print(f" - {err}")
        print("=============================================")

if __name__ == "__main__":
    main()
