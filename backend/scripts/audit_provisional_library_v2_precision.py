#!/usr/bin/env python3
import os
import sys
import json
import re
import argparse
from typing import Dict, List, Any

# Ensure correct path resolution
backend_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
parent_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website"
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

# Import ACTION_VERBS, NOISE_BLACKLIST from library_taxonomy_v2
try:
    from backend.rag.library_taxonomy_v2 import ACTION_VERBS, NOISE_BLACKLIST, COMMON_ADJECTIVES, GRAMMAR_WORDS
except ImportError:
    ACTION_VERBS = set()
    NOISE_BLACKLIST = set()
    COMMON_ADJECTIVES = set()
    GRAMMAR_WORDS = set()

GENERIC_NOUNS = {
    "hệ thống", "tang thi", "zombie", "tinh thể", "tinh thạch", "trường học", "bệnh viện", "căn cứ",
    "vũ khí", "súng", "dao", "kiếm", "dị năng", "kỹ năng", "thẻ", "sách", "người", "nhân vật", "con", "cái"
}

def print_safe(text):
    """Safely print text to stdout."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def calculate_suspicious_features(name: str) -> Dict[str, bool]:
    name_clean = name.strip()
    name_lower = name_clean.lower()
    words = name_clean.split()
    
    if not words:
        return {}
        
    first_word_lower = words[0].lower()
    
    starts_with_verb = first_word_lower in ACTION_VERBS
    contains_sentence_punctuation = bool(re.search(r'[,.!?;:"]', name_clean))
    too_many_words = len(words) > 4
    
    lowercase_words = [w for w in words if w.islower()]
    lowercase_phrase = (len(lowercase_words) / len(words)) > 0.5 if words else False
    
    pronoun_fragment = any(pron in name_lower.split() for pron in {"hắn", "nàng", "tôi", "nó", "những kẻ", "chúng ta", "bọn họ", "ta", "ngươi", "chúng", "họ"})
    
    generic_noun = first_word_lower in GENERIC_NOUNS
    
    # Action phrase: contains name + action verb (e.g. "Hàn Phong ăn", "Ngô Soái chạy")
    action_phrase = any(w in name_lower for w in ACTION_VERBS) and not starts_with_verb
    
    # Description phrase: contains adjectives
    description_phrase = any(adj in name_lower for adj in COMMON_ADJECTIVES)
    
    return {
        "starts_with_verb": starts_with_verb,
        "contains_sentence_punctuation": contains_sentence_punctuation,
        "too_many_words": too_many_words,
        "lowercase_phrase": lowercase_phrase,
        "pronoun_fragment": pronoun_fragment,
        "generic_noun": generic_noun,
        "action_phrase": action_phrase,
        "description_phrase": description_phrase
    }

def main():
    parser = argparse.ArgumentParser(description="Audit precision of provisional library V2 concepts.")
    parser.add_argument("--input", type=str, default="backend/rag/generated_provisional_library_v2.json", help="Input V2 library json.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_provisional_library_v2_precision_audit.json", help="Output precision audit json.")
    parser.add_argument("--json", action="store_true", help="Print JSON summary to stdout.")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print_safe(f"Input file not found: {input_path}")
        sys.exit(1)
        
    with open(input_path, "r", encoding="utf-8") as f:
        library = json.load(f)
        
    print_safe(f"Auditing library from: {input_path}")
    
    by_category = {}
    by_quality = {}
    by_evidence_bucket = {
        "1": 0,
        "2": 0,
        "3-5": 0,
        "6-10": 0,
        "10+": 0
    }
    
    examples_risky = {
        "character": [],
        "ability_skill": [],
        "event": [],
        "relationship": []
    }
    
    feature_counts = {
        "starts_with_verb": 0,
        "contains_sentence_punctuation": 0,
        "too_many_words": 0,
        "lowercase_phrase": 0,
        "pronoun_fragment": 0,
        "generic_noun": 0,
        "action_phrase": 0,
        "description_phrase": 0
    }
    
    suspicious_examples = []
    
    for cat, records in library.items():
        if cat == "chapter_summary":
            continue
            
        by_category[cat] = len(records)
        
        for r in records:
            name = r.get("name", "")
            q_class = r.get("quality_class", "unknown")
            evidence = r.get("evidence", [])
            ev_count = len(evidence)
            
            by_quality[q_class] = by_quality.get(q_class, 0) + 1
            
            if ev_count == 1:
                by_evidence_bucket["1"] += 1
            elif ev_count == 2:
                by_evidence_bucket["2"] += 1
            elif 3 <= ev_count <= 5:
                by_evidence_bucket["3-5"] += 1
            elif 6 <= ev_count <= 10:
                by_evidence_bucket["6-10"] += 1
            else:
                by_evidence_bucket["10+"] += 1
                
            if cat in examples_risky:
                if len(examples_risky[cat]) < 100:
                    examples_risky[cat].append(name)
                    
            # Suspicious feature flags
            features = calculate_suspicious_features(name)
            for feat, val in features.items():
                if val:
                    feature_counts[feat] += 1
                    
            # Calculate a suspicious score
            score = sum(3 if val and feat in ["starts_with_verb", "lowercase_phrase"] else (2 if val else 0) for feat, val in features.items())
            if score >= 3 and len(suspicious_examples) < 100:
                suspicious_examples.append({
                    "name": name,
                    "category": cat,
                    "score": score,
                    "features": [feat for feat, val in features.items() if val]
                })
                
    report = {
        "by_category": by_category,
        "by_quality": by_quality,
        "by_evidence_bucket": by_evidence_bucket,
        "feature_counts": feature_counts,
        "suspicious_examples": suspicious_examples,
        "top_examples_risky": examples_risky
    }
    
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print_safe(f"V2 Precision Audit report saved to: {output_path}")
    
    if args.json:
        summary = {
            "by_category": by_category,
            "feature_counts": feature_counts,
            "suspicious_examples_count": len(suspicious_examples)
        }
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
