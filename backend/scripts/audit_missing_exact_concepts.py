#!/usr/bin/env python3
import os
import sys
import json
import argparse
import re
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.database import supabase
from backend.rag.library_taxonomy_v2 import classify_term_v2
from backend.rag.retrieval import normalize_vietnamese_text

def print_safe(text):
    """Safely print text to stdout."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def strip_accents(text: str) -> str:
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))

def main():
    parser = argparse.ArgumentParser(description="Audit missing exact concepts in provisional library.")
    parser.add_argument("--seeds", type=str, default="backend/rag/important_concept_seeds.json", help="Path to seeds JSON file.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_missing_exact_concepts_audit.json", help="Path to output JSON file.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON output to stdout.")
    args = parser.parse_args()

    seeds_path = os.path.abspath(args.seeds)
    output_path = os.path.abspath(args.output)

    if not os.path.exists(seeds_path):
        print_safe(f"Seeds file not found at {seeds_path}")
        sys.exit(1)

    with open(seeds_path, "r", encoding="utf-8") as f:
        seeds = json.load(f)

    print_safe(f"Loaded {len(seeds)} seed concepts to audit.")

    # 1. Fetch all provisional_library records using pagination
    print_safe("Fetching all provisional_library records from database...")
    all_records = []
    offset = 0
    limit = 1000
    while True:
        try:
            res = supabase.table("provisional_library").select("id, name, normalized_name, type, quality_class, confidence").range(offset, offset + limit - 1).execute()
            data = res.data or []
            all_records.extend(data)
            if len(data) < limit:
                break
            offset += limit
        except Exception as e:
            print_safe(f"Error fetching records from provisional_library: {e}")
            sys.exit(1)

    print_safe(f"Fetched {len(all_records)} records from provisional_library.")

    # 2. Audit seeds
    audit_results = []

    for seed in seeds:
        print_safe(f"Auditing seed: '{seed}'...")
        norm_seed = normalize_vietnamese_text(seed)
        
        exact_match = None
        near_matches = []

        for record in all_records:
            rec_name = record.get("name") or ""
            rec_norm = record.get("normalized_name") or rec_name
            
            norm_rec_name = normalize_vietnamese_text(rec_name)
            norm_rec_norm = normalize_vietnamese_text(rec_norm)

            if norm_seed == norm_rec_name or norm_seed == norm_rec_norm:
                exact_match = {
                    "id": record.get("id"),
                    "name": rec_name,
                    "normalized_name": rec_norm,
                    "type": record.get("type"),
                    "quality_class": record.get("quality_class"),
                    "confidence": record.get("confidence")
                }
            elif (norm_seed in norm_rec_name or norm_rec_name in norm_seed or
                  norm_seed in norm_rec_norm or norm_rec_norm in norm_seed):
                near_matches.append({
                    "id": record.get("id"),
                    "name": rec_name,
                    "normalized_name": rec_norm,
                    "type": record.get("type"),
                    "quality_class": record.get("quality_class"),
                    "confidence": record.get("confidence")
                })

        # 3. Search story_chunks for evidence
        seed_accented = seed.strip()
        seed_unaccented = strip_accents(seed_accented)

        evidence_chunks = []
        try:
            # Query story_chunks
            or_filter = f"content_plain.ilike.%{seed_accented}%,content_plain.ilike.%{seed_unaccented}%"
            res = supabase.table("story_chunks").select("chapter_number,chapter_title,chunk_index,content_plain,content_hash").or_(or_filter).execute()
            raw_chunks = res.data or []
            
            # Post-filter in python to ensure exact match of normalized text
            for rc in raw_chunks:
                content = rc.get("content_plain") or ""
                norm_content = normalize_vietnamese_text(content)
                if norm_seed in norm_content:
                    # Find context sentence containing seed
                    sentences = [s.strip() for s in re.split(r'[.!?。！？]\s+', content) if s.strip()]
                    context_sentence = ""
                    for s in sentences:
                        if norm_seed in normalize_vietnamese_text(s):
                            context_sentence = s
                            break
                    if not context_sentence:
                        # Fallback: slice around the match
                        idx = norm_content.find(norm_seed)
                        start = max(0, idx - 100)
                        end = min(len(content), idx + len(seed) + 100)
                        context_sentence = content[start:end]
                    
                    preview = context_sentence[:200]
                    if len(context_sentence) > 200:
                        preview += "..."

                    evidence_chunks.append({
                        "chapter_number": rc.get("chapter_number"),
                        "chapter_title": rc.get("chapter_title"),
                        "chunk_index": rc.get("chunk_index"),
                        "content_hash": rc.get("content_hash"),
                        "preview": preview
                    })
        except Exception as e:
            print_safe(f"Error querying story_chunks for '{seed}': {e}")

        # Propose category/type
        first_preview = evidence_chunks[0]["preview"] if evidence_chunks else ""
        proposed_cat = classify_term_v2(seed, first_preview)

        # Sort evidence chunks by chapter and index
        evidence_chunks.sort(key=lambda x: (x.get("chapter_number") or 9999, x.get("chunk_index") or 0))
        chapter_numbers = sorted(list(set(x["chapter_number"] for x in evidence_chunks if x.get("chapter_number") is not None)))

        audit_results.append({
            "seed": seed,
            "exact_match": exact_match,
            "near_matches": near_matches,
            "has_evidence": len(evidence_chunks) > 0,
            "proposed_category": proposed_cat,
            "evidence": evidence_chunks,
            "chapter_numbers": chapter_numbers
        })

    # Save to output file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, ensure_ascii=False, indent=2)

    print_safe(f"Audit completed. Saved results to {output_path}")

    # Print summary JSON if requested
    if args.json:
        summary = {
            "total_audited": len(audit_results),
            "missing_exact": sum(1 for r in audit_results if r["exact_match"] is None),
            "with_evidence": sum(1 for r in audit_results if r["has_evidence"])
        }
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
