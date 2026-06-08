#!/usr/bin/env python3
import os
import sys
import json
import argparse
from pathlib import Path

# Add repo root to sys.path
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
    parser = argparse.ArgumentParser(description="Manually clear oracle_cache rows for specific concepts.")
    parser.add_argument("--terms", nargs="+", required=True, help="List of concept terms or names to clear cache for.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry-run mode (default). Does not delete.")
    parser.add_argument("--write", action="store_true", help="Perform actual deletion. Overrides default dry-run.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON output to stdout.")
    
    args = parser.parse_args()

    # If --write is specified, dry-run is False
    dry_run = not args.write

    if not supabase:
        print_safe("Error: Supabase client not initialized.")
        sys.exit(1)

    if not args.terms:
        print_safe("Error: No terms specified.")
        sys.exit(1)

    from backend.rag.oracle_cache_invalidation import clear_oracle_cache_for_terms, build_cache_invalidation_terms
    
    # Standardize/deduplicate terms
    clean_terms = build_cache_invalidation_terms(args.terms)
    
    if not clean_terms:
        print_safe("Error: Terms list resolved to empty after normalization.")
        sys.exit(1)

    if not args.json:
        print_safe(f"Processing cache invalidation for terms: {clean_terms}")
        print_safe(f"Mode: {'WRITE (actual deletion)' if not dry_run else 'DRY-RUN (read-only)'}")

    cache_report = clear_oracle_cache_for_terms(
        supabase,
        terms=clean_terms,
        dry_run=dry_run
    )

    if args.json:
        print(json.dumps(cache_report, indent=2))
    else:
        print_safe(f"Cache invalidation finished.")
        print_safe(f"Matched rows: {cache_report['matched_rows']}")
        print_safe(f"Deleted rows: {cache_report['deleted_rows']}")
        if cache_report.get("skipped_reason"):
            print_safe(f"Warning/Error: {cache_report['skipped_reason']}")

if __name__ == "__main__":
    main()
