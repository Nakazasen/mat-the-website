#!/usr/bin/env python3
import os
import sys
import json
import argparse

# Ensure paths are set
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

from backend.rag.oracle_answer_patch_builder import build_oracle_patches

def print_safe(text: str):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def build_patches_from_db(dry_run: bool = True, output_path: str = None) -> list:
    print_safe("Fetching pending feedbacks from rag_feedback...")
    try:
        res = supabase.table("rag_feedback").select("*").eq("status", "pending").execute()
        feedbacks = res.data or []
    except Exception as e:
        print_safe(f"Error fetching feedbacks: {e}")
        feedbacks = []

    print_safe(f"Fetched {len(feedbacks)} pending feedbacks.")
    patches = build_oracle_patches(feedbacks)
    print_safe(f"Generated {len(patches)} candidate patches.")

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(patches, f, ensure_ascii=False, indent=2)
        print_safe(f"Patch plan saved to: {output_path}")

    return patches

def main():
    parser = argparse.ArgumentParser(description="Build Oracle answer policy patches from pending feedbacks.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Simulate build without saving to DB (default: True).")
    parser.add_argument("--json", action="store_true", help="Print patches output as JSON.")
    args = parser.parse_args()

    plan_path = os.path.join(backend_path, "rag", "generated_oracle_answer_patch_plan.json")
    patches = build_patches_from_db(dry_run=args.dry_run, output_path=plan_path)

    if args.json:
        print_safe(json.dumps(patches, ensure_ascii=False, indent=2))
    else:
        print_safe(f"Completed patch building. dry_run={args.dry_run}")

if __name__ == "__main__":
    main()
