#!/usr/bin/env python3
"""
CLI script to dry-run applying wiki candidates to wiki_entries table.
Compiles payloads, performs schema validation, detects duplicates in database, and outputs a plan.
Does NOT modify the database under any circumstances.
"""

import argparse
import json
import os
import sys

# Configure path imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Load dotenv pointing directly to backend/.env
from dotenv import load_dotenv
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(backend_dir, ".env"))

try:
    from main import supabase
except ImportError:
    try:
        from backend.main import supabase
    except ImportError:
        supabase = None

from rag.wiki_apply_dry_run import build_apply_plan

def main():
    parser = argparse.ArgumentParser(description="Dry-run apply wiki candidates to wiki_entries.")
    parser.add_argument("--input", default="backend/rag/generated_wiki_candidates.json", help="Input candidates JSON path")
    parser.add_argument("--output", default="backend/rag/generated_wiki_apply_plan.json", help="Output plan JSON path")
    parser.add_argument("--check-db", dest="check_db", action="store_true", help="Check database for duplicate titles/slugs")
    parser.add_argument("--no-check-db", dest="check_db", action="store_false", help="Skip database duplicate check")
    parser.set_defaults(check_db=True)
    parser.add_argument("--json", action="store_true", help="Print raw plan in JSON format (ASCII-escaped)")
    
    args = parser.parse_args()
    
    input_abs = os.path.abspath(args.input)
    output_abs = os.path.abspath(args.output)
    
    # 1. Read input candidates
    if not os.path.exists(input_abs):
        print(f"Error: Input file '{args.input}' does not exist.")
        sys.exit(1)
        
    try:
        with open(input_abs, "r", encoding="utf-8") as f:
            candidates = json.load(f)
        if not isinstance(candidates, list):
            print("Error: Input file must contain a JSON list of candidates.")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to read input JSON: {e}")
        sys.exit(1)
        
    # 2. Determine if database connection is available
    db_conn = None
    if args.check_db:
        if not supabase:
            print("Warning: Supabase client not initialized. Database checks will be skipped.")
        else:
            db_conn = supabase
            
    # 3. Build plan
    plan = build_apply_plan(candidates, supabase=db_conn)
    
    # 4. Save plan to output path
    os.makedirs(os.path.dirname(output_abs), exist_ok=True)
    try:
        with open(output_abs, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to write output plan JSON file: {e}")
        sys.exit(1)
        
    # 5. Output summary
    summary = plan["summary"]
    
    if args.json:
        # Use ensure_ascii=True to avoid CP932 encoding errors on Windows stdout
        print(json.dumps(plan, ensure_ascii=True, indent=2))
    else:
        print("==================================================")
        print("WIKI APPLY DRY-RUN PLAN GENERATION COMPLETED")
        print(f"Input Path:  {args.input}")
        print(f"Output Path: {args.output}")
        print(f"Check DB:    {args.check_db and db_conn is not None}")
        print("--------------------------------------------------")
        print(f"Total candidates processed: {summary['total_candidates']}")
        print(f"Eligible for import:        {summary['eligible_count']}")
        print(f"Ineligible/skipped:         {summary['ineligible_count']}")
        print(f"Duplicate entries found:    {summary['duplicate_count']}")
        print("==================================================")
        print("Note: DRY-RUN mode active. No data was written to wiki_entries.")

if __name__ == "__main__":
    main()
