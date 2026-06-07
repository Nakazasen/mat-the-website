#!/usr/bin/env python3
import os
import sys
import json
import argparse
from typing import Dict, List, Any

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

from backend.rag.provisional_library_v2_import_gate import is_importable_v2

def print_safe(text):
    """Safely print text to stdout."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def build_db_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    """Prepares the database payload matching the provisional_library table columns."""
    name = record.get("name", "")
    evidence = record.get("evidence", [])
    
    chapters = set()
    for ev in evidence:
        ch_num = ev.get("chapter_number")
        if ch_num is not None:
            try:
                chapters.add(int(ch_num))
            except (ValueError, TypeError):
                pass
    chapter_list = sorted(list(chapters))
    
    first_ch = chapter_list[0] if chapter_list else None
    last_ch = chapter_list[-1] if chapter_list else None
    
    return {
        "id": record.get("id"),
        "name": name,
        "normalized_name": name, # V2 uses name directly or case-normalized
        "type": record.get("type"),
        "summary": record.get("summary"),
        "evidence": evidence,
        "confidence": float(record.get("confidence", 0.0)),
        "quality_class": record.get("quality_class"),
        "status": record.get("status", "provisional"),
        "source": record.get("source", "story_chunks_auto_extract_v2"),
        "feedback_score": int(record.get("feedback_score", 0)),
        "needs_review": bool(record.get("needs_review", False)),
        "chapter_numbers": chapter_list,
        "first_chapter": first_ch,
        "last_chapter": last_ch
    }

def main():
    parser = argparse.ArgumentParser(description="Build V2 provisional library import candidates.")
    parser.add_argument("--input", type=str, default="backend/rag/generated_provisional_library_v2.json", help="Input V2 library path.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_provisional_library_v2_import_candidates.json", help="Output candidate JSON path.")
    parser.add_argument("--report", type=str, default="backend/rag/generated_provisional_library_v2_import_candidate_report.json", help="Output report JSON path.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON to stdout.")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print_safe(f"Input file not found: {input_path}")
        sys.exit(1)
        
    with open(input_path, "r", encoding="utf-8") as f:
        library = json.load(f)
        
    print_safe(f"Filtering provisional library V2 candidates from: {input_path}")
    
    total_records = 0
    accepted_records = []
    rejected_records_details = []
    
    accepted_by_category = {}
    rejected_by_reason = {}
    
    accepted_examples_by_category = {}
    rejected_examples_by_reason = {}
    
    for cat, records in library.items():
        total_records += len(records)
        
        for r in records:
            importable, reason = is_importable_v2(r)
            if importable:
                db_record = build_db_payload(r)
                accepted_records.append(db_record)
                
                accepted_by_category[cat] = accepted_by_category.get(cat, 0) + 1
                if cat not in accepted_examples_by_category:
                    accepted_examples_by_category[cat] = []
                if len(accepted_examples_by_category[cat]) < 10:
                    accepted_examples_by_category[cat].append(r["name"])
            else:
                rejected_records_details.append({
                    "name": r.get("name", ""),
                    "category": cat,
                    "reason": reason
                })
                rejected_by_reason[reason] = rejected_by_reason.get(reason, 0) + 1
                
                if reason not in rejected_examples_by_reason:
                    rejected_examples_by_reason[reason] = []
                if len(rejected_examples_by_reason[reason]) < 10:
                    rejected_examples_by_reason[reason].append(r["name"])
                    
    # Save candidates
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(accepted_records, f, indent=2, ensure_ascii=False)
        
    # Compile report
    report = {
        "V1_current_production_count": 1264,
        "V2_dry_run_total_records": total_records,
        "V2_import_candidate_count": len(accepted_records),
        "accepted_count": len(accepted_records),
        "rejected_count": len(rejected_records_details),
        "accepted_by_category": accepted_by_category,
        "rejected_by_reason": rejected_by_reason,
        "accepted_examples_by_category": accepted_examples_by_category,
        "rejected_examples_by_reason": rejected_examples_by_reason
    }
    
    report_path = os.path.abspath(args.report)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print_safe(f"Import candidates successfully written to: {output_path}")
    print_safe(f"Import candidate report saved to: {report_path}")
    
    if args.json:
        summary = {
            "v2_dry_run_total_records": total_records,
            "v2_import_candidate_count": len(accepted_records),
            "rejected_count": len(rejected_records_details)
        }
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
