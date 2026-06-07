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

from backend.rag.provisional_library_quality import is_noise_name

# Standard adjectives or common noise terms that frequently contaminate V1 Proper Noun extraction
NOISE_ADJECTIVES = {
    "ác độc", "ác ý", "âm ẩm", "tàn ác", "mạnh mẽ", "yếu ớt", "độc ác", "tối tăm", "lạnh lùng",
    "hoang tàn", "đổ nát", "hung hãn", "nhanh chóng", "chậm chạp", "bất ngờ", "đột ngột",
    "đây đã", "đang", "vừa", "hắn", "nàng", "những kẻ", "của họ", "chúng ta"
}

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def main():
    parser = argparse.ArgumentParser(description="Audit V1 provisional library quality.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_provisional_library_audit_v1.json", help="Output JSON path.")
    parser.add_argument("--json", action="store_true", help="Format output as JSON on stdout.")
    args = parser.parse_args()

    print_safe("Fetching all provisional library records from database...")
    
    all_records = []
    limit = 1000
    offset = 0
    while True:
        try:
            res = supabase.table("provisional_library")\
                .select("*")\
                .range(offset, offset + limit - 1)\
                .execute()
            data = res.data or []
            if not data:
                break
            all_records.extend(data)
            if len(data) < limit:
                break
            offset += limit
        except Exception as e:
            print_safe(f"Error querying provisional_library table: {e}")
            sys.exit(1)
            
    print_safe(f"Retrieved {len(all_records)} total records.")

    # 1. Count by type
    count_by_type = {}
    # 2. Count by quality_class
    count_by_quality_class = {}
    
    # Track examples by type
    examples_by_type = {}
    
    # Analyze noise
    noise_examples = []
    short_adjective_examples = []
    
    for rec in all_records:
        t_type = rec.get("type", "unknown")
        q_class = rec.get("quality_class", "unknown")
        name = rec.get("name", "")
        
        count_by_type[t_type] = count_by_type.get(t_type, 0) + 1
        count_by_quality_class[q_class] = count_by_quality_class.get(q_class, 0) + 1
        
        # Track top 5 examples per type
        if t_type not in examples_by_type:
            examples_by_type[t_type] = []
        if len(examples_by_type[t_type]) < 5:
            examples_by_type[t_type].append(name)
            
        # Check if it looks like noise
        name_lower = name.lower().strip()
        if is_noise_name(name):
            noise_examples.append(name)
        elif name_lower in NOISE_ADJECTIVES or any(adj in name_lower for adj in NOISE_ADJECTIVES):
            short_adjective_examples.append(name)
            
    report = {
        "total_records": len(all_records),
        "count_by_type": count_by_type,
        "count_by_quality_class": count_by_quality_class,
        "noise_examples_detected": len(noise_examples),
        "noise_examples": noise_examples[:30],
        "short_adjective_examples_detected": len(short_adjective_examples),
        "short_adjective_examples": short_adjective_examples[:30],
        "examples_by_type": examples_by_type
    }
    
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print_safe(f"Provisional library V1 audit report generated and saved to: {output_path}")
    
    if args.json:
        # Print short summary
        summary = {
            "total_records": len(all_records),
            "count_by_type": count_by_type,
            "count_by_quality_class": count_by_quality_class,
            "noise_examples_count": len(noise_examples),
            "short_adjective_examples_count": len(short_adjective_examples)
        }
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
