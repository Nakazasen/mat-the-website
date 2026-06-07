#!/usr/bin/env python3
"""
CLI script to query approved corrections and build wiki candidates.
Outputs candidate JSON to a local file. Does not edit the wiki_entries table.
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

from rag.wiki_candidate_builder import (
    build_wiki_candidate_from_correction,
    summarize_wiki_candidates
)

def main():
    parser = argparse.ArgumentParser(description="Build wiki candidates from approved RAG corrections.")
    parser.add_argument("--status", default="approved", help="Filter by correction status (default: approved)")
    parser.add_argument("--correction-type", default="entity_profile", help="Filter by correction type (default: entity_profile)")
    parser.add_argument("--limit", type=int, default=100, help="Max corrections to fetch (default: 100)")
    parser.add_argument("--output", default="backend/rag/generated_wiki_candidates.json", help="Output JSON path")
    parser.add_argument("--json", action="store_true", help="Print summary or list in raw JSON format")
    
    # Dry run options
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", default=True, help="Dry run mode (default: True)")
    parser.add_argument("--no-dry-run", dest="dry_run", action="store_false", help="Disable dry run mode (forces local file writing)")
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_abs = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_abs), exist_ok=True)
    
    if not supabase:
        print("Error: Supabase client is not initialized. Check your environment variables.")
        sys.exit(1)
        
    # Query database
    try:
        query = supabase.table("rag_corrections").select("*").eq("status", args.status)
        if args.correction_type:
            query = query.eq("correction_type", args.correction_type)
        res = query.order("created_at", desc=True).limit(args.limit).execute()
        rows = res.data or []
    except Exception as e:
        print(f"Database query failed: {e}")
        sys.exit(1)
        
    candidates = []
    for row in rows:
        candidate = build_wiki_candidate_from_correction(row)
        candidates.append(candidate)
        
    summary = summarize_wiki_candidates(candidates)
    
    # Write to local file
    try:
        with open(output_abs, "w", encoding="utf-8") as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to write output JSON file: {e}")
        sys.exit(1)
        
    # Format stdout output
    if args.json:
        # Print results as JSON
        output_data = {
            "summary": summary,
            "candidates": candidates
        }
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
    else:
        print("==================================================")
        print("WIKI CANDIDATES GENERATION COMPLETED (DRY-RUN)")
        print(f"Status: {args.status}")
        print(f"Correction Type: {args.correction_type}")
        print(f"Output Path: {args.output}")
        print("--------------------------------------------------")
        print(f"Total processed:       {summary['total']}")
        print(f"Ready for review:      {summary['ready_for_review']}")
        print(f"Needs human fill:      {summary['needs_human_fill']}")
        print(f"Invalid:               {summary['invalid']}")
        print("==================================================")
        print("Note: No changes were written to the wiki_entries table.")

if __name__ == "__main__":
    main()
