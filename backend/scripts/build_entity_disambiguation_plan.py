#!/usr/bin/env python3
import os
import sys
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from backend.database import supabase
except ImportError:
    supabase = None

def print_safe(text):
    """Safely print text to stdout."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def main():
    parser = argparse.ArgumentParser(description="Build entity disambiguation plan.")
    parser.add_argument("--json", action="store_true", help="Print plan summary JSON to stdout.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_entity_disambiguation_plan.json", help="Path to save JSON plan.")
    args = parser.parse_args()

    if not supabase:
        print_safe("Error: Supabase client not initialized.")
        sys.exit(1)

    print_safe("Fetching records from database...")
    all_rows = []
    batch_size = 1000
    start = 0
    while True:
        try:
            res = supabase.table("provisional_library").select("id, name, type, source, quality_class, confidence, evidence").range(start, start + batch_size - 1).execute()
            data = res.data or []
            all_rows.extend(data)
            if len(data) < batch_size:
                break
            start += batch_size
        except Exception as e:
            print_safe(f"Error fetching batch starting at {start}: {e}")
            sys.exit(1)

    from backend.rag.entity_disambiguation import build_entity_disambiguation_plan

    plan = build_entity_disambiguation_plan(all_rows)

    # Categories
    to_update_type = []
    to_mark_manual_review = []
    to_mark_noise_candidate = []
    no_change = []
    rejected_dangerous_mapping = []

    # Counts
    summary_counts = Counter()
    examples_by_action = defaultdict(list)

    for item in plan:
        act = item["action"]
        name = item["name"]
        old_t = item["old_type"]
        new_t = item["new_type"]
        
        summary_counts[act] += 1
        
        # Categorize
        if act == "update_type":
            to_update_type.append(item)
        elif act == "manual_review":
            to_mark_manual_review.append(item)
        elif act == "noise_candidate":
            to_mark_noise_candidate.append(item)
        elif act == "no_change":
            no_change.append(item)
        else:
            rejected_dangerous_mapping.append(item)

        if len(examples_by_action[act]) < 15:
            examples_by_action[act].append(name)

    # Compile plan report
    plan_report = {
        "summary": dict(summary_counts),
        "examples_by_action": dict(examples_by_action),
        "to_update_type": to_update_type,
        "to_mark_manual_review": to_mark_manual_review,
        "to_mark_noise_candidate": to_mark_noise_candidate,
        "no_change_count": len(no_change),
        "rejected_dangerous_mapping": rejected_dangerous_mapping
    }

    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(plan_report, f, indent=2, ensure_ascii=False)

    print_safe(f"Disambiguation plan saved to: {output_path}")
    print_safe(f"Summary counts: {dict(summary_counts)}")

    if args.json:
        print(json.dumps(dict(summary_counts), indent=2))

if __name__ == "__main__":
    main()
