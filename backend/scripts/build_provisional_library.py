import os
import sys
import json
import argparse
import hashlib
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

from backend.rag.provisional_library import (
    extract_candidate_terms,
    build_provisional_record,
    merge_duplicate_records,
    normalize_name
)

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def build_chapter_summaries(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generates provisional chapter summaries by grouping chunks by chapter."""
    chapter_map = {}
    for chunk in chunks:
        ch_num = chunk.get("chapter_number")
        if ch_num is None:
            continue
        if ch_num not in chapter_map:
            chapter_map[ch_num] = []
        chapter_map[ch_num].append(chunk)
        
    chapter_records = []
    for ch_num, ch_chunks in sorted(chapter_map.items()):
        # Sort chunks by index to get the first chunk
        ch_chunks.sort(key=lambda c: c.get("chunk_index") or 0)
        first_chunk = ch_chunks[0]
        
        ch_title = first_chunk.get("chapter_title") or f"Chương {ch_num}"
        content = first_chunk.get("content_plain") or first_chunk.get("content") or ""
        
        # Take first 150 characters as preview/summary
        preview = content[:150] + "..." if len(content) > 150 else content
        
        stable_id = hashlib.md5(f"chapter_summary_{ch_num}".encode('utf-8')).hexdigest()
        
        record = {
            "id": stable_id,
            "name": f"Chương {ch_num}: {ch_title}",
            "type": "chapter_summary",
            "summary": f"Nội dung bắt đầu của chương {ch_num}. Trích đoạn: '{preview}'",
            "evidence": [
                {
                    "chapter_number": ch_num,
                    "chapter_title": ch_title,
                    "chunk_index": first_chunk.get("chunk_index"),
                    "content_hash": first_chunk.get("content_hash"),
                    "preview": preview
                }
            ],
            "confidence": 1.0,
            "status": "provisional",
            "source": "story_chunks_auto_extract",
            "feedback_score": 0,
            "needs_review": False
        }
        chapter_records.append(record)
        
    return chapter_records

def main():
    parser = argparse.ArgumentParser(description="Automatically build provisional library from story chunks.")
    parser.add_argument("--chapter-cap", type=int, default=829, help="Max chapter number limit for evidence.")
    parser.add_argument("--limit-chunks", type=int, default=10000, help="Maximum number of chunks to fetch.")
    parser.add_argument("--min-evidence", type=int, default=2, help="Minimum evidence count to not be marked as weak_evidence.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_provisional_library.json", help="Output path for JSON library.")
    parser.add_argument("--json", action="store_true", help="Format output as JSON.")
    
    args = parser.parse_args()
    
    print_safe(f"Fetching story chunks up to chapter {args.chapter_cap}...")
    try:
        res = supabase.table("story_chunks")\
            .select("chapter_number, chapter_title, chunk_index, content, content_plain, content_hash")\
            .lte("chapter_number", args.chapter_cap)\
            .order("chapter_number")\
            .order("chunk_index")\
            .limit(args.limit_chunks)\
            .execute()
        chunks = res.data or []
        print_safe(f"Successfully retrieved {len(chunks)} chunks.")
    except Exception as e:
        print_safe(f"Error fetching chunks from DB: {e}")
        sys.exit(1)
        
    if not chunks:
        print_safe("No chunks found in database.")
        sys.exit(1)
        
    # 1. Extract terms candidate records
    print_safe("Running candidate terms extraction from chunks...")
    candidates = extract_candidate_terms(chunks)
    print_safe(f"Extracted {len(candidates)} raw candidates.")
    
    # 2. Build provisional records
    provisional_records = []
    for cand in candidates:
        rec = build_provisional_record(cand, [cand["evidence"]])
        provisional_records.append(rec)
        
    # 3. Merge duplicate records and check min evidence
    print_safe("Merging duplicate records and filtering evidence...")
    merged_records = merge_duplicate_records(provisional_records, min_evidence=args.min_evidence)
    print_safe(f"Synthesized {len(merged_records)} merged term records.")
    
    # 4. Generate chapter summaries
    print_safe("Generating chapter summaries...")
    chapter_summaries = build_chapter_summaries(chunks)
    print_safe(f"Generated {len(chapter_summaries)} chapter summaries.")
    
    # 5. Group records into 8 groups
    library = {
        "entities": [],
        "items": [],
        "abilities": [],
        "locations": [],
        "factions": [],
        "events": [],
        "relationships": [],
        "chapter_summaries": chapter_summaries
    }
    
    weak_evidence_count = 0
    
    for r in merged_records:
        if r["status"] == "weak_evidence":
            weak_evidence_count += 1
            
        t_type = r["type"]
        if t_type in ["entity", "character", "creature"]:
            library["entities"].append(r)
        elif t_type == "item":
            library["items"].append(r)
        elif t_type == "ability":
            library["abilities"].append(r)
        elif t_type == "location":
            library["locations"].append(r)
        elif t_type == "faction":
            library["factions"].append(r)
        elif t_type == "event":
            library["events"].append(r)
        elif t_type == "relationship":
            library["relationships"].append(r)
            
    total_records = sum(len(v) for v in library.values())
    
    # Compile CLI output summary
    cli_summary = {
        "total_records": total_records,
        "by_type": {k: len(v) for k, v in library.items()},
        "weak_evidence": weak_evidence_count,
        "output": args.output
    }
    
    print_safe("-" * 60)
    print_safe("PROVISIONAL LIBRARY SUMMARY:")
    print_safe(json.dumps(cli_summary, indent=2))
    print_safe("-" * 60)
    
    # Save output
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(library, f, indent=2, ensure_ascii=False)
        print_safe(f"Provisional library successfully saved to: {output_path}")
    except Exception as e:
        print_safe(f"Error saving provisional library to file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
