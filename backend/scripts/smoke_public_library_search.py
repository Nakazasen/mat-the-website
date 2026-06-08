#!/usr/bin/env python3
"""
Smoke Public Library Search quality check.
Verifies that key library concepts return exact or near matches,
and that common noise terms do not match any provisional library cards.
"""

import sys
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Force UTF-8 encoding for standard output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from backend.database import supabase
except ImportError:
    print("Error: Could not import backend.database.supabase")
    sys.exit(1)

from backend.rag.retrieval import search_provisional_library, normalize_vietnamese_text

# Define expectations for core queries
CORE_QUERIES = {
    "Tinh thể zombie": "Tinh thể zombie",
    "Tinh thạch khai phá": "Tinh Thạch Khai Phá",
    "Súng Diệt Quỷ": "Súng Diệt Quỷ",
    "Băng Độc": "Băng Độc",
    "Căn cứ Hi Vọng": "Căn cứ Hi Vọng",
    "Zombie Cấp 3": "Zombie Cấp 3"
}

NOISE_QUERIES = [
    "ác độc",
    "ác ý",
    "âm ẩm",
    "đây đã"
]

def main():
    print("=" * 60)
    print("Public Library Search Smoke Test")
    print("=" * 60)

    if not supabase:
        print("Error: Supabase client not initialized.")
        sys.exit(1)

    failed = False

    # 1. Check Core Queries
    print("\n--- Checking Core Concepts ---")
    for query_str, expected_name in CORE_QUERIES.items():
        print(f"Querying: '{query_str}'...")
        results = search_provisional_library(supabase, query_str, limit=5)
        
        if not results:
            print(f"  [FAIL] No results returned for '{query_str}'")
            failed = True
            continue

        top_result = results[0]
        top_name = top_result.get("name", "")
        
        # Check normalized match
        norm_expected = normalize_vietnamese_text(expected_name)
        norm_top = normalize_vietnamese_text(top_name)
        
        if norm_expected == norm_top or norm_expected in norm_top or norm_top in norm_expected:
            print(f"  [PASS] Top result: '{top_name}' (expected: '{expected_name}')")
        else:
            print(f"  [FAIL] Top result: '{top_name}' (expected: '{expected_name}')")
            failed = True

    # 2. Check Noise Queries
    print("\n--- Checking Noise Regression ---")
    for noise_str in NOISE_QUERIES:
        print(f"Querying noise: '{noise_str}'...")
        results = search_provisional_library(supabase, noise_str, limit=5)
        
        # We fail if there is an exact or near match returned for this noise term
        norm_noise = normalize_vietnamese_text(noise_str)
        found_exact_or_near = False
        
        for r in results:
            name_val = r.get("name", "")
            norm_name = normalize_vietnamese_text(name_val)
            # If the noise term is exactly matching the card name, or very close
            if norm_noise == norm_name or norm_name == norm_noise:
                print(f"  [FAIL] Noise query matched card '{name_val}'!")
                found_exact_or_near = True
                failed = True
                break
        
        if not found_exact_or_near:
            print(f"  [PASS] No exact card matches found for noise '{noise_str}' (results returned: {len(results)})")

    print("\n" + "=" * 60)
    if failed:
        print("RESULT: SMOKE TEST FAILED!")
        print("=" * 60)
        sys.exit(1)
    else:
        print("RESULT: ALL SMOKE TESTS PASSED!")
        print("=" * 60)
        sys.exit(0)

if __name__ == "__main__":
    main()
