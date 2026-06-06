import os
import sys
import asyncio
import argparse
import json

# Ensure correct path resolution
backend_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
parent_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website"
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

try:
    from main import supabase
except ImportError:
    from backend.main import supabase

from backend.rag.eval_cases import EVAL_CASES
from backend.rag.evaluator import evaluate_all_cases
from backend.rag.entity_drafts import build_missing_entity_drafts

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

async def main_async(args):
    # 1. Run evaluator to identify missing entities
    print_safe("Running evaluator to identify missing entity/wiki profiles...")
    eval_result = await evaluate_all_cases(EVAL_CASES, supabase)
    
    missing_entities = []
    for r in eval_result.get("results", []):
        if r.get("missing_entity_context") and r.get("entity_name"):
            missing_entities.append(r["entity_name"])
            
    # Dedup
    deduped = []
    for ent in missing_entities:
        if ent not in deduped:
            deduped.append(ent)
            
    if not deduped:
        print_safe("No missing entities found. Exiting.")
        sys.exit(0)
        
    print_safe(f"Found {len(deduped)} missing entities in evaluator.")
    
    if args.limit_entities:
        deduped = deduped[:args.limit_entities]
        print_safe(f"Limiting to first {args.limit_entities} entities.")
        
    # 2. Build drafts
    print_safe(f"Generating drafts for {len(deduped)} entities with chapter-cap {args.chapter_cap}...")
    drafts = build_missing_entity_drafts(deduped, chapter_cap=args.chapter_cap, supabase=supabase)
    
    # 3. Write output file
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(drafts, f, indent=2, ensure_ascii=False)
        
    print_safe(f"Successfully generated drafts saved to: {output_path}")
    
    has_ev = sum(1 for d in drafts if d.get("evidence"))
    no_ev = len(drafts) - has_ev
    print_safe(f"Stat: {has_ev} drafts with evidence, {no_ev} drafts without evidence.")

def main():
    parser = argparse.ArgumentParser(description="Generate reviewable entity drafts for missing wiki profiles.")
    parser.add_argument("--chapter-cap", type=int, default=10, help="Maximum chapter number to retrieve evidence from.")
    parser.add_argument("--limit-entities", type=int, default=None, help="Limit the number of missing entities to process.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_entity_drafts.json", help="Path to output JSON file.")
    parser.add_argument("--from-evaluator-missing", action="store_true", help="Obtain missing entities list from evaluator run.")
    
    args = parser.parse_args()
    asyncio.run(main_async(args))

if __name__ == "__main__":
    main()
