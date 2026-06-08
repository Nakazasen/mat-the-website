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
from backend.rag.exact_concept_backfill import build_backfill_candidate

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

def fetch_evidence_chunks(seed: str) -> list:
    """Queries story_chunks for evidence using semantic expansion if needed."""
    # Map seed to search phrases
    search_phrases = [seed]
    if seed == "Tinh thể zombie":
        search_phrases = ["tinh thạch ma dược", "tinh thạch exp", "tinh thạch thây ma", "tinh thể thây ma", "tinh hạch thây ma"]
    elif seed == "Zombie Cấp 3":
        search_phrases = ["thây ma cấp 3", "thây ma cấp ba", "thây ma level 3", "tang thi cấp 3"]
    elif seed == "Căn cứ Hi Vọng":
        search_phrases = ["trấn Hi Vọng", "căn cứ Hi Vọng", "Hi Vọng trại"]

    or_parts = []
    for sp in search_phrases:
        unaccented_sp = strip_accents(sp)
        or_parts.append(f"content_plain.ilike.%{sp}%")
        if unaccented_sp != sp:
            or_parts.append(f"content_plain.ilike.%{unaccented_sp}%")

    evidence_chunks = []
    try:
        or_filter = ",".join(or_parts)
        res = supabase.table("story_chunks").select("chapter_number,chapter_title,chunk_index,content_plain,content_hash").or_(or_filter).execute()
        raw_chunks = res.data or []
        
        seen_hashes = set()
        for rc in raw_chunks:
            content = rc.get("content_plain") or ""
            norm_content = normalize_vietnamese_text(content)
            h = rc.get("content_hash")
            if h in seen_hashes:
                continue

            matched = False
            matched_phrase = ""
            for sp in search_phrases:
                norm_sp = normalize_vietnamese_text(sp)
                if norm_sp in norm_content:
                    matched = True
                    matched_phrase = sp
                    break
            
            if matched:
                seen_hashes.add(h)
                sentences = [s.strip() for s in re.split(r'[.!?。！？]\s+', content) if s.strip()]
                context_sentence = ""
                norm_matched_phrase = normalize_vietnamese_text(matched_phrase)
                for s in sentences:
                    if norm_matched_phrase in normalize_vietnamese_text(s):
                        context_sentence = s
                        break
                if not context_sentence:
                    idx = norm_content.find(norm_matched_phrase)
                    start = max(0, idx - 100)
                    end = min(len(content), idx + len(matched_phrase) + 100)
                    context_sentence = content[start:end]
                
                preview = context_sentence[:200]
                if len(context_sentence) > 200:
                    preview += "..."

                evidence_chunks.append({
                    "chapter_number": rc.get("chapter_number"),
                    "chapter_title": rc.get("chapter_title"),
                    "chunk_index": rc.get("chunk_index"),
                    "content_hash": h,
                    "preview": preview
                })
    except Exception as e:
        print_safe(f"Error fetching evidence for '{seed}': {e}")
        
    return evidence_chunks

def main():
    parser = argparse.ArgumentParser(description="Build exact concept backfills.")
    parser.add_argument("--audit", type=str, default="backend/rag/generated_missing_exact_concepts_audit.json", help="Path to audit JSON.")
    parser.add_argument("--output-candidates", type=str, default="backend/rag/generated_exact_concept_backfills.json", help="Path to candidates output.")
    parser.add_argument("--output-report", type=str, default="backend/rag/generated_exact_concept_backfill_report.json", help="Path to report output.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON output.")
    args = parser.parse_args()

    audit_path = os.path.abspath(args.audit)
    out_candidates_path = os.path.abspath(args.output_candidates)
    out_report_path = os.path.abspath(args.output_report)

    if not os.path.exists(audit_path):
        print_safe(f"Audit file not found at {audit_path}")
        sys.exit(1)

    with open(audit_path, "r", encoding="utf-8") as f:
        audit_results = json.load(f)

    candidates = []
    report_items = []

    for item in audit_results:
        seed = item["seed"]
        exact_match = item["exact_match"]
        proposed_cat = item["proposed_category"]

        # Only backfill if missing exact match
        if exact_match is not None:
            print_safe(f"Seed '{seed}' already has exact match. Skipping.")
            report_items.append({
                "seed": seed,
                "status": "already_exists",
                "record_id": exact_match["id"],
                "evidence_count": len(item.get("evidence", []))
            })
            continue

        print_safe(f"Building backfill candidate for missing seed: '{seed}'...")
        evidence = fetch_evidence_chunks(seed)
        
        if len(evidence) > 0:
            candidate = build_backfill_candidate(seed, proposed_cat, evidence)
            candidates.append(candidate)
            print_safe(f"Created candidate: ID={candidate['id']}, Name='{candidate['name']}', Type='{candidate['type']}', Evidence={len(evidence)}")
            report_items.append({
                "seed": seed,
                "status": "created_candidate",
                "record_id": candidate["id"],
                "evidence_count": len(evidence)
            })
        else:
            print_safe(f"Warning: No evidence found for missing seed '{seed}'. Skipping.")
            report_items.append({
                "seed": seed,
                "status": "missing_no_evidence",
                "record_id": None,
                "evidence_count": 0
            })

    # Save candidates
    os.makedirs(os.path.dirname(out_candidates_path), exist_ok=True)
    with open(out_candidates_path, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)

    # Save report
    with open(out_report_path, "w", encoding="utf-8") as f:
        json.dump(report_items, f, ensure_ascii=False, indent=2)

    print_safe(f"Successfully generated {len(candidates)} candidates.")
    print_safe(f"Saved candidates to {out_candidates_path}")
    print_safe(f"Saved report to {out_report_path}")

    if args.json:
        summary = {
            "candidates_created": len(candidates),
            "skipped_already_exists": sum(1 for x in report_items if x["status"] == "already_exists"),
            "skipped_no_evidence": sum(1 for x in report_items if x["status"] == "missing_no_evidence")
        }
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
