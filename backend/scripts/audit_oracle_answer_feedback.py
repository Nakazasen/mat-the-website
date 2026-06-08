#!/usr/bin/env python3
import os
import sys
import json
import argparse
from collections import Counter

# Add backend and root to sys.path
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

# Helper to print safely in Windows CMD/PowerShell
def print_safe(text: str):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def audit_feedbacks(json_output_path: str = None) -> dict:
    print_safe("Fetching rag_feedback rows from Supabase...")
    try:
        res = supabase.table("rag_feedback").select("*").execute()
        rows = res.data or []
    except Exception as e:
        print_safe(f"Error fetching feedbacks: {e}")
        rows = []

    total_feedback = len(rows)
    status_counts = Counter(row.get("status", "unknown") for row in rows)
    source_counts = Counter(row.get("source", "unknown") for row in rows)

    # Keywords to extract
    keywords = ["sơ sài", "máy móc", "linh tinh", "tóm tắt", "lan man", "không liên quan", "chương", "nhân vật"]
    comment_texts = [row.get("user_comment", "") for row in rows if row.get("user_comment")]
    
    keyword_freq = {}
    for kw in keywords:
        count = sum(1 for text in comment_texts if kw in text.lower())
        if count > 0:
            keyword_freq[kw] = count

    # Categorize samples using simple heuristics (aligned with classifier rules)
    examples = []
    for row in rows:
        comment = (row.get("user_comment") or "").lower()
        question = (row.get("question") or "").lower()
        answer = (row.get("answer") or "").lower()
        
        guess = "unknown"
        if any(w in comment for w in ["sơ sài", "máy móc", "quá ngắn", "không đủ thông tin"]):
            guess = "answer_quality_too_shallow"
        elif any(w in question for w in ["nội dung chương", "tóm tắt chương", "chương này"]) and any(w in comment for w in ["linh tinh", "nhân vật", "tổ chức"]):
            guess = "intent_misclassification"
        elif any(w in comment for w in ["không liên quan", "linh tinh", "lan man"]):
            guess = "irrelevant_entities"
        elif "[chưa có mục định danh chính xác]" in answer:
            guess = "missing_exact_entity"
        elif "cache" in comment or "cũ" in comment:
            guess = "stale_cache"

        examples.append({
            "id": row.get("id"),
            "question": row.get("question"),
            "answer": row.get("answer")[:200] if row.get("answer") else "",
            "user_comment": row.get("user_comment"),
            "feedback_type": row.get("feedback_type"),
            "status": row.get("status"),
            "issue_type_guess": guess
        })

    report = {
        "total_feedback": total_feedback,
        "status_counts": dict(status_counts),
        "source_counts": dict(source_counts),
        "common_complaint_keywords": keyword_freq,
        "examples": examples
    }

    if json_output_path:
        os.makedirs(os.path.dirname(json_output_path), exist_ok=True)
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print_safe(f"Audit report saved to: {json_output_path}")

    return report

def main():
    parser = argparse.ArgumentParser(description="Audit Oracle answer feedbacks.")
    parser.add_argument("--json", action="store_true", help="Print output as JSON.")
    args = parser.parse_args()

    output_path = os.path.join(backend_path, "rag", "generated_oracle_answer_feedback_audit.json")
    report = audit_feedbacks(output_path)

    if args.json:
        print_safe(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_safe("-" * 60)
        print_safe("ORACLE FEEDBACK AUDIT RESULTS:")
        print_safe(f"Total Feedback: {report['total_feedback']}")
        print_safe(f"Status Counts: {report['status_counts']}")
        print_safe(f"Source Counts: {report['source_counts']}")
        print_safe(f"Keywords: {report['common_complaint_keywords']}")
        print_safe("-" * 60)

if __name__ == "__main__":
    main()
