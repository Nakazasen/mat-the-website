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

from backend.rag.provisional_library_quality import rank_records, build_quality_report

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def main():
    parser = argparse.ArgumentParser(description="Rank provisional library quality.")
    parser.add_argument("--input", type=str, default="backend/rag/generated_provisional_library.json", help="Input JSON library path.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_provisional_library_ranked.json", help="Output ranked JSON library path.")
    parser.add_argument("--report", type=str, default="backend/rag/generated_provisional_library_quality_report.json", help="Output quality report JSON path.")
    parser.add_argument("--json", action="store_true", help="Format console summary as JSON.")
    
    args = parser.parse_args()
    
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print_safe(f"Input file does not exist: {input_path}")
        sys.exit(1)
        
    print_safe(f"Loading provisional library from: {input_path}")
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            library = json.load(f)
    except Exception as e:
        print_safe(f"Error reading input JSON: {e}")
        sys.exit(1)
        
    # Gather all records to flatten list
    all_records = []
    # Save the type mapping to reconstruct groups
    record_group_mapping = {}
    
    for key, records in library.items():
        if not isinstance(records, list):
            continue
        for r in records:
            all_records.append(r)
            r_id = r.get("id")
            if r_id:
                record_group_mapping[r_id] = key
                
    print_safe(f"Flattened {len(all_records)} records from {len(library)} groups.")
    
    # Run ranking and quality classification
    print_safe("Ranking records and running quality gates...")
    ranked_flat_records = rank_records(all_records)
    
    # Reconstruct the original groups
    ranked_library = {k: [] for k in library.keys()}
    for r in ranked_flat_records:
        r_id = r.get("id")
        orig_key = record_group_mapping.get(r_id)
        if orig_key and orig_key in ranked_library:
            ranked_library[orig_key].append(r)
        else:
            t_type = r.get("type")
            if t_type == "entity" and "entities" in ranked_library:
                ranked_library["entities"].append(r)
            elif t_type == "item" and "items" in ranked_library:
                ranked_library["items"].append(r)
            elif t_type == "ability" and "abilities" in ranked_library:
                ranked_library["abilities"].append(r)
            elif t_type == "location" and "locations" in ranked_library:
                ranked_library["locations"].append(r)
            elif t_type == "faction" and "factions" in ranked_library:
                ranked_library["factions"].append(r)
            elif t_type == "event" and "events" in ranked_library:
                ranked_library["events"].append(r)
            elif t_type == "relationship" and "relationships" in ranked_library:
                ranked_library["relationships"].append(r)
            elif t_type == "chapter_summary" and "chapter_summaries" in ranked_library:
                ranked_library["chapter_summaries"].append(r)
            else:
                if "entities" in ranked_library:
                    ranked_library["entities"].append(r)
                    
    # Generate report
    print_safe("Building quality report...")
    report = build_quality_report(ranked_flat_records)
    
    # Output report
    if args.json:
        print_safe("-" * 60)
        print_safe("QUALITY REPORT:")
        print_safe(json.dumps(report, indent=2, ensure_ascii=False))
        print_safe("-" * 60)
    else:
        print_safe("-" * 60)
        print_safe("QUALITY REPORT SUMMARY:")
        print_safe(f"Total processed: {report['total']}")
        print_safe(f"High confidence: {report['high_confidence']}")
        print_safe(f"Medium confidence: {report['medium_confidence']}")
        print_safe(f"Weak evidence: {report['weak_evidence']}")
        print_safe(f"Discarded candidates: {report['discard_candidate']}")
        print_safe("-" * 60)
        
    # Save ranked library
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(ranked_library, f, indent=2, ensure_ascii=False)
        print_safe(f"Ranked provisional library saved to: {output_path}")
    except Exception as e:
        print_safe(f"Error saving ranked library: {e}")
        sys.exit(1)
        
    # Save report
    report_path = os.path.abspath(args.report)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print_safe(f"Quality report saved to: {report_path}")
    except Exception as e:
        print_safe(f"Error saving report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
