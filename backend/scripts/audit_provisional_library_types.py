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
    parser = argparse.ArgumentParser(description="Audit distinct types/categories in provisional_library.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON output to stdout.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_provisional_library_type_audit.json", help="Path to save JSON audit report.")
    args = parser.parse_args()

    if not supabase:
        print_safe("Error: Supabase client not initialized.")
        sys.exit(1)

    print_safe("Fetching all provisional library records from database...")
    all_rows = []
    batch_size = 1000
    start = 0
    while True:
        try:
            res = supabase.table("provisional_library").select("id, name, type, source, quality_class").range(start, start + batch_size - 1).execute()
            data = res.data or []
            all_rows.extend(data)
            if len(data) < batch_size:
                break
            start += batch_size
        except Exception as e:
            print_safe(f"Error fetching batch starting at {start}: {e}")
            sys.exit(1)

    print_safe(f"Total records retrieved: {len(all_rows)}")

    from backend.rag.provisional_library_type_normalizer import build_type_normalization_plan, is_v2_type

    # Analyze types
    type_counts = Counter()
    source_counts = Counter()
    quality_counts = Counter()
    type_examples = defaultdict(list)
    
    for row in all_rows:
        t = row.get("type") or "None"
        type_counts[t] += 1
        source_counts[row.get("source") or "None"] += 1
        quality_counts[row.get("quality_class") or "None"] += 1
        
        # Collect up to 5 examples per type
        if len(type_examples[t]) < 5:
            type_examples[t].append(row.get("name"))

    legacy_or_unknown = []
    for t in type_counts.keys():
        if not is_v2_type(t):
            legacy_or_unknown.append(t)

    plan = build_type_normalization_plan(all_rows)
    needs_norm_count = sum(1 for p in plan if p["needs_normalization"])
    
    rows_needing_norm = [p for p in plan if p["needs_normalization"]]

    report = {
        "summary": {
            "total_records": len(all_rows),
            "records_needing_normalization": needs_norm_count,
            "legacy_types_count": len(legacy_or_unknown),
            "distinct_types_count": len(type_counts)
        },
        "legacy_or_unknown_types": legacy_or_unknown,
        "type_counts": dict(type_counts),
        "source_counts": dict(source_counts),
        "quality_class_counts": dict(quality_counts),
        "type_examples": dict(type_examples),
        "needs_normalization_sample": rows_needing_norm[:50],
        "all_needs_normalization": rows_needing_norm
    }

    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print_safe(f"Audit report saved to: {output_path}")
    print_safe(f"Summary: total={len(all_rows)}, legacy_types={legacy_or_unknown}, needs_normalization={needs_norm_count}")

    if args.json:
        print(json.dumps(report["summary"], indent=2))

if __name__ == "__main__":
    main()
