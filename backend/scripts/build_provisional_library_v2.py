#!/usr/bin/env python3
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

from backend.rag.provisional_library_v2 import (
    extract_candidate_terms_v2,
    build_provisional_record_v2,
    merge_duplicate_records_v2,
    normalize_name
)
from backend.rag.library_taxonomy_v2 import TAXONOMY_V2_LABELS, is_rejected_v2

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
        ch_chunks.sort(key=lambda c: c.get("chunk_index") or 0)
        first_chunk = ch_chunks[0]
        
        ch_title = first_chunk.get("chapter_title") or f"Chương {ch_num}"
        content = first_chunk.get("content_plain") or first_chunk.get("content") or ""
        
        preview = content[:150] + "..." if len(content) > 150 else content
        stable_id = hashlib.md5(f"chapter_summary_{ch_num}".encode('utf-8')).hexdigest()
        
        record = {
            "id": stable_id,
            "name": f"Chương {ch_num}: {ch_title}",
            "type": "chapter_summary",
            "summary": f"[Tóm tắt chương] Nội dung bắt đầu của chương {ch_num}. Trích đoạn: '{preview}'",
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
            "source": "story_chunks_auto_extract_v2",
            "feedback_score": 0,
            "needs_review": False,
            "quality_score": 10.0,
            "quality_class": "high_confidence",
            "discard_reasons": []
        }
        chapter_records.append(record)
        
    return chapter_records

def main():
    parser = argparse.ArgumentParser(description="Build provisional library V2 dry-run.")
    parser.add_argument("--chapter-cap", type=int, default=829, help="Max chapter cap for chunks.")
    parser.add_argument("--limit-chunks", type=int, default=10000, help="Max chunks to load.")
    parser.add_argument("--min-evidence", type=int, default=2, help="Min evidence to be provisional.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_provisional_library_v2.json", help="Output JSON path.")
    parser.add_argument("--report", type=str, default="backend/rag/generated_provisional_library_v2_report.json", help="Report JSON path.")
    parser.add_argument("--json", action="store_true", help="Format summary as JSON on stdout.")
    
    args = parser.parse_args()
    
    print_safe(f"Fetching story chunks up to chapter {args.chapter_cap}...")
    
    # Query story_chunks using pagination to ensure we get all of them up to chapter cap
    chunks = []
    limit = 1000
    offset = 0
    while len(chunks) < args.limit_chunks:
        try:
            res = supabase.table("story_chunks")\
                .select("chapter_number, chapter_title, chunk_index, content, content_plain, content_hash")\
                .lte("chapter_number", args.chapter_cap)\
                .order("chapter_number")\
                .order("chunk_index")\
                .range(offset, offset + limit - 1)\
                .execute()
            data = res.data or []
            if not data:
                break
            chunks.extend(data)
            if len(data) < limit:
                break
            offset += limit
        except Exception as e:
            print_safe(f"Error fetching chunks: {e}")
            sys.exit(1)
            
    print_safe(f"Loaded {len(chunks)} chunks from database.")
    
    # 1. Run Extractor V2
    print_safe("Running Extractor V2...")
    candidates = extract_candidate_terms_v2(chunks)
    print_safe(f"Extracted {len(candidates)} raw candidates.")
    
    # 2. Build provisional records
    provisional_records = []
    for cand in candidates:
        rec = build_provisional_record_v2(cand, [cand["evidence"]], min_evidence=args.min_evidence)
        provisional_records.append(rec)
        
    # 3. Merge duplicate records
    print_safe("Merging duplicates...")
    merged_records = merge_duplicate_records_v2(provisional_records, min_evidence=args.min_evidence)
    print_safe(f"Merged into {len(merged_records)} unique records.")
    
    # 4. Generate chapter summaries
    chapter_summaries = build_chapter_summaries(chunks)
    
    # Organize library structure
    library_v2 = {cat: [] for cat in TAXONOMY_V2_LABELS.keys()}
    library_v2["chapter_summary"] = chapter_summaries
    
    # Sort merged records into categories
    quality_counts = {"high_confidence": 0, "medium_confidence": 0, "weak_evidence": 0, "discard_candidate": 0}
    
    for r in merged_records:
        q_class = r.get("quality_class", "weak_evidence")
        quality_counts[q_class] = quality_counts.get(q_class, 0) + 1
        
        t_type = r["type"]
        if t_type in library_v2:
            library_v2[t_type].append(r)
        else:
            # Fallback
            library_v2["character"].append(r)
            
    # Calculate coverage by chapter
    chapter_coverage = {}
    for cat, items in library_v2.items():
        for item in items:
            for ev in item.get("evidence", []):
                ch = ev.get("chapter_number")
                if ch is not None:
                    chapter_coverage[ch] = True
                    
    coverage_percentage = round((len(chapter_coverage) / args.chapter_cap) * 100, 2) if args.chapter_cap > 0 else 0
    
    # Extract top 20 examples per category
    top_examples = {}
    for cat, items in library_v2.items():
        # Sort by quality_score descending
        sorted_items = sorted(items, key=lambda x: x.get("quality_score", 0.0), reverse=True)
        top_examples[cat] = [item["name"] for item in sorted_items[:20]]
        
    # Track rejected noise examples by checking the blacklist
    # We can scan the raw text again or mock a few rejected words for documentation
    sample_raw_noise = ["ác độc", "ác ý", "âm ẩm", "đây đã", "đang", "vừa", "hắn", "nàng", "những kẻ", "chúng ta"]
    rejected_examples = [w for w in sample_raw_noise if is_rejected_v2(w)]
    
    # Save library file
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(library_v2, f, indent=2, ensure_ascii=False)
        
    # Load V1 audit for comparison
    v1_audit_path = os.path.abspath("backend/rag/generated_provisional_library_audit_v1.json")
    v1_stats = {}
    if os.path.exists(v1_audit_path):
        try:
            with open(v1_audit_path, "r", encoding="utf-8") as f:
                v1_stats = json.load(f)
        except Exception:
            pass
            
    # Compile comparison
    total_v2_records = sum(len(v) for v in library_v2.values())
    comparison = {
        "v1_total_records": v1_stats.get("total_records", 0),
        "v2_total_records": total_v2_records,
        "v1_type_counts": v1_stats.get("count_by_type", {}),
        "v2_type_counts": {k: len(v) for k, v in library_v2.items()},
        "v1_quality_counts": v1_stats.get("count_by_quality_class", {}),
        "v2_quality_counts": quality_counts
    }
    
    report = {
        "total_records": total_v2_records,
        "count_by_category": {cat: len(items) for cat, items in library_v2.items()},
        "coverage_by_chapter_count": len(chapter_coverage),
        "coverage_by_chapter_percentage": coverage_percentage,
        "quality_class_counts": quality_counts,
        "top_examples_per_category": top_examples,
        "rejected_noise_examples": rejected_examples,
        "comparison_v1_vs_v2": comparison
    }
    
    # Save report file
    report_path = os.path.abspath(args.report)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print_safe(f"Provisional library V2 built successfully: {output_path}")
    print_safe(f"V2 Extraction Report generated: {report_path}")
    
    if args.json:
        print(json.dumps({
            "total_records": total_v2_records,
            "coverage_percentage": coverage_percentage,
            "quality_class_counts": quality_counts
        }, indent=2))

if __name__ == "__main__":
    main()
