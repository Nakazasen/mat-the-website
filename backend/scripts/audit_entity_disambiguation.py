#!/usr/bin/env python3
import os
import sys
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from backend.database import supabase
except ImportError:
    supabase = None

def print_safe(text):
    """Safely print text to stdout."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def main():
    parser = argparse.ArgumentParser(description="Audit entities and false positive records in provisional_library.")
    parser.add_argument("--json", action="store_true", help="Print summary JSON output to stdout.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_entity_disambiguation_audit.json", help="Path to save JSON audit report.")
    args = parser.parse_args()

    if not supabase:
        print_safe("Error: Supabase client not initialized.")
        sys.exit(1)

    print_safe("Fetching records from database...")
    all_rows = []
    batch_size = 1000
    start = 0
    while True:
        try:
            res = supabase.table("provisional_library").select("id, name, type, source, quality_class, confidence, evidence").range(start, start + batch_size - 1).execute()
            data = res.data or []
            all_rows.extend(data)
            if len(data) < batch_size:
                break
            start += batch_size
        except Exception as e:
            print_safe(f"Error fetching batch starting at {start}: {e}")
            sys.exit(1)

    print_safe(f"Total records retrieved: {len(all_rows)}")

    from backend.rag.entity_disambiguation import classify_entity_candidate, detect_false_positive_type

    entity_records = [r for r in all_rows if r.get("type") == "entity"]
    non_entity_records = [r for r in all_rows if r.get("type") != "entity"]

    # 1. Audit entity patterns
    patterns = {
        "likely_character": [],
        "likely_location": [],
        "likely_organization": [],
        "likely_zombie_species": [],
        "likely_crystal_core": [],
        "likely_ability_skill": [],
        "likely_noise": [],
        "uncertain": []
    }

    # Group entity examples by confidence
    examples_by_confidence = defaultdict(list)

    for row in entity_records:
        name = row.get("name", "")
        evidence = row.get("evidence", [])
        classification = classify_entity_candidate(name, evidence=evidence, current_type="entity")
        
        action = classification["action"]
        target = classification["target_type"]
        
        # Examples by confidence
        conf_label = row.get("quality_class") or "None"
        if len(examples_by_confidence[conf_label]) < 5:
            examples_by_confidence[conf_label].append(name)

        if action == "noise_candidate":
            patterns["likely_noise"].append(name)
        elif action == "update_type":
            if target == "zombie_species":
                patterns["likely_zombie_species"].append(name)
            elif target == "crystal_core":
                patterns["likely_crystal_core"].append(name)
            elif target == "location_base":
                patterns["likely_location"].append(name)
            elif target == "organization_faction":
                patterns["likely_organization"].append(name)
            elif target == "ability_skill":
                patterns["likely_ability_skill"].append(name)
        elif action == "manual_review":
            patterns["likely_character"].append(name)  # proper name/title-case
        else:
            patterns["uncertain"].append(name)

    # 2. Audit suspicious existing records (false positives)
    suspicious_records = {
        "character": [],
        "organization_faction": [],
        "location_base": [],
        "ability_skill": []
    }

    for row in non_entity_records:
        name = row.get("name", "")
        old_type = row.get("type")
        evidence = row.get("evidence", [])
        
        classification = classify_entity_candidate(name, evidence=evidence, current_type=old_type)
        if classification["action"] in ("update_type", "noise_candidate"):
            if old_type in suspicious_records:
                suspicious_records[old_type].append({
                    "id": row.get("id"),
                    "name": name,
                    "old_type": old_type,
                    "suggested_type": classification["target_type"],
                    "suggested_action": classification["action"],
                    "reason": classification["reason"]
                })

    report = {
        "entity_counts": {
            "total_entities": len(entity_records),
            "likely_character": len(patterns["likely_character"]),
            "likely_location": len(patterns["likely_location"]),
            "likely_organization": len(patterns["likely_organization"]),
            "likely_zombie_species": len(patterns["likely_zombie_species"]),
            "likely_crystal_core": len(patterns["likely_crystal_core"]),
            "likely_ability_skill": len(patterns["likely_ability_skill"]),
            "likely_noise": len(patterns["likely_noise"]),
            "uncertain": len(patterns["uncertain"])
        },
        "examples_by_confidence": dict(examples_by_confidence),
        "patterns_samples": {
            "likely_character": patterns["likely_character"][:30],
            "likely_location": patterns["likely_location"][:30],
            "likely_organization": patterns["likely_organization"][:30],
            "likely_zombie_species": patterns["likely_zombie_species"][:30],
            "likely_crystal_core": patterns["likely_crystal_core"][:30],
            "likely_ability_skill": patterns["likely_ability_skill"][:30],
            "likely_noise": patterns["likely_noise"][:30],
            "uncertain": patterns["uncertain"][:30]
        },
        "suspicious_existing_records_counts": {
            "character": len(suspicious_records["character"]),
            "organization_faction": len(suspicious_records["organization_faction"]),
            "location_base": len(suspicious_records["location_base"]),
            "ability_skill": len(suspicious_records["ability_skill"])
        },
        "suspicious_existing_records_details": suspicious_records
    }

    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print_safe(f"Audit report saved to: {output_path}")
    print_safe(f"Summary: total_entities={len(entity_records)}, likely_noise={len(patterns['likely_noise'])}, suspicious_existing={sum(len(v) for v in suspicious_records.values())}")

    if args.json:
        print(json.dumps(report["entity_counts"], indent=2))

if __name__ == "__main__":
    main()
