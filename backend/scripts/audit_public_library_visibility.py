#!/usr/bin/env python3
import os
import sys
import json
import argparse
import urllib.request
import urllib.parse
from pathlib import Path
from collections import Counter

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
    parser = argparse.ArgumentParser(description="Audit visibility of discard/needs_review records in the public library.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON output to stdout.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_public_library_visibility_audit.json", help="Path to save JSON audit report.")
    args = parser.parse_args()

    if not supabase:
        print_safe("Error: Supabase client not initialized.")
        sys.exit(1)

    print_safe("Fetching all database records for statistics...")
    all_rows = []
    batch_size = 1000
    start = 0
    while True:
        try:
            res = supabase.table("provisional_library").select("id, name, type, status, needs_review, quality_class").range(start, start + batch_size - 1).execute()
            data = res.data or []
            all_rows.extend(data)
            if len(data) < batch_size:
                break
            start += batch_size
        except Exception as e:
            print_safe(f"Error fetching batch starting at {start}: {e}")
            sys.exit(1)

    # 1. Database level counts
    status_counts = Counter(r.get("status", "None") for r in all_rows)
    needs_review_counts = Counter(r.get("needs_review") for r in all_rows)

    # 2. Simulate the public API filter on database rows:
    # - quality_class in high_confidence, medium_confidence
    # - status != discard
    # - needs_review != true
    simulated_public_rows = []
    for r in all_rows:
        qc = r.get("quality_class")
        status = r.get("status")
        nr = r.get("needs_review")
        if qc in ("high_confidence", "medium_confidence") and status != "discard" and not nr:
            simulated_public_rows.append(r)

    # Verify if any discard or needs_review got through the filter
    discard_in_simulated = [r["name"] for r in simulated_public_rows if r.get("status") == "discard"]
    needs_review_in_simulated = [r["name"] for r in simulated_public_rows if r.get("needs_review") is True]

    # 3. Hit the live Vercel API and query for test concepts
    vercel_api_url = "https://matthesinhhoa.vercel.app/api/public/provisional-library"
    test_concepts = [
        "đoàn đội",
        "đoàn ô",
        "Hàn Phong đứng",
        "Châu Lam đang",
        "Áo Khoác Phòng Hộ",
        "Áo Khoác Tận Thế"
    ]

    vercel_results = {}
    print_safe("Querying live Vercel API for regression concepts...")
    for concept in test_concepts:
        encoded = urllib.parse.quote(concept)
        url = f"{vercel_api_url}?search={encoded}&page=1&page_size=5"
        try:
            req = urllib.request.urlopen(url)
            res_json = json.loads(req.read().decode("utf-8"))
            items = res_json.get("items", [])
            
            # Check if our target concept is found in any returned name (case-insensitive exact)
            found = False
            top_match = None
            if items:
                top_match = items[0].get("name")
                for item in items:
                    if item.get("name", "").lower().strip() == concept.lower().strip():
                        found = True
            
            vercel_results[concept] = {
                "returned_in_api": found,
                "api_results_count": len(items),
                "top_result_returned": top_match
            }
        except Exception as e:
            vercel_results[concept] = {
                "error": str(e)
            }

    report = {
        "db_statistics": {
            "total_records": len(all_rows),
            "status_distribution": dict(status_counts),
            "needs_review_distribution": dict(needs_review_counts)
        },
        "simulated_public_api": {
            "total_visible_records": len(simulated_public_rows),
            "discard_records_leaked_count": len(discard_in_simulated),
            "discard_records_leaked_examples": discard_in_simulated[:10],
            "needs_review_records_leaked_count": len(needs_review_in_simulated),
            "needs_review_records_leaked_examples": needs_review_in_simulated[:10]
        },
        "live_vercel_api_check": vercel_results
    }

    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print_safe(f"Visibility audit report saved to: {output_path}")
    if args.json:
        print(json.dumps(report["db_statistics"], indent=2))

if __name__ == "__main__":
    main()
