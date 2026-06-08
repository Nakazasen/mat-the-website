#!/usr/bin/env python3
import os
import sys
import json
import argparse
import datetime
import requests

def print_safe(text):
    """Safely print text to prevent encoding errors on Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

# Lexical scoring functions
def score_ha_huyen_suong(response: str) -> tuple[bool, str]:
    lower_resp = response.lower()
    if "hạ huyền sương" not in lower_resp:
        return False, "Missing 'Hạ Huyền Sương' name"
    if "816" not in lower_resp and "tám trăm mười sáu" not in lower_resp:
        return False, "Missing chapter 816 reference or context"
    if len(response) < 100:
        return False, "Response is too short/shallow"
    return True, ""

def score_chapter_summary(response: str) -> tuple[bool, str]:
    lower_resp = response.lower()
    if "phân loại:" in lower_resp:
        return False, "Contains entity category list markup indicating search fallback"
    if not any(kw in lower_resp for kw in ["tóm tắt", "chương", "nội dung"]):
        return False, "Missing summary keywords ('tóm tắt', 'chương', 'nội dung')"
    if not any(kw in lower_resp for kw in ["hàn phong", "sương", "lẩu", "đun nước", "tắm"]):
        return False, "Missing chapter 820 plot details"
    return True, ""

def score_tinh_the_zombie(response: str) -> tuple[bool, str]:
    lower_resp = response.lower()
    if "tinh thể zombie" not in lower_resp and "tinh thạch" not in lower_resp:
        return False, "Missing 'Tinh thể zombie' or 'tinh thạch' name"
    if not any(kw in lower_resp for kw in ["crystal_core", "chương 9"]):
        return False, "Missing core category or evidence details (crystal_core, chương 9)"
    if "phá tâm linh" in lower_resp:
        return False, "Incorrectly references 'Phá Tâm Linh'"
    return True, ""

def score_bang_doc(response: str) -> tuple[bool, str]:
    lower_resp = response.lower()
    if "băng độc" not in lower_resp:
        return False, "Missing 'Băng Độc' name"
    return True, ""

def score_han_phong(response: str) -> tuple[bool, str]:
    lower_resp = response.lower()
    if "hàn phong" not in lower_resp:
        return False, "Missing 'Hàn Phong' name"
    if not any(kw in lower_resp for kw in ["nhân vật chính", "main", "nam chính", "bất tử", "hệ thống", "trọng sinh", "mạt thế"]):
        return False, "Missing main protagonist context for Hàn Phong"
    return True, ""

def score_doan_doi(response: str) -> tuple[bool, str]:
    lower_resp = response.lower()
    if any(kw in lower_resp for kw in ["là một thế lực", "là thế lực", "là tổ chức"]) and not any(kw in lower_resp for kw in ["từ chung", "từ thông dụng", "discard", "loại bỏ", "nhiễu"]):
        return False, "Treats generic term 'đoàn đội' as a proper noun organization/faction"
    return True, ""

# Query registry
REGRESSION_CASES = [
    {
        "id": "ha_huyen_suong",
        "question": "Hạ Huyền Sương là ai",
        "chapter_progress": 829,
        "scorer": score_ha_huyen_suong
    },
    {
        "id": "chapter_summary",
        "question": "nội dung chương truyện là gì",
        "chapter_progress": 820,
        "scorer": score_chapter_summary
    },
    {
        "id": "tinh_the_zombie",
        "question": "Tinh thể zombie là gì?",
        "chapter_progress": 829,
        "scorer": score_tinh_the_zombie
    },
    {
        "id": "bang_doc",
        "question": "Băng Độc là gì?",
        "chapter_progress": 829,
        "scorer": score_bang_doc
    },
    {
        "id": "han_phong",
        "question": "Hàn Phong là ai?",
        "chapter_progress": 829,
        "scorer": score_han_phong
    },
    {
        "id": "doan_doi",
        "question": "đoàn đội là gì?",
        "chapter_progress": 829,
        "scorer": score_doan_doi
    }
]

def run_regression_pack(base_url: str) -> dict:
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    results = []
    all_passed = True

    print_safe(f"Running regression queries against: {base_url}")
    print_safe("-" * 60)

    for case in REGRESSION_CASES:
        qid = case["id"]
        qtext = case["question"]
        prog = case["chapter_progress"]
        scorer = case["scorer"]

        print_safe(f"Query: '{qtext}' (progress: {prog})...")

        try:
            url = f"{base_url}/oracle/ask"
            resp = requests.post(url, json={"question": qtext, "chapter_progress": prog}, timeout=15)

            if resp.status_code != 200:
                results.append({
                    "id": qid,
                    "question": qtext,
                    "chapter_progress": prog,
                    "status_code": resp.status_code,
                    "passed": False,
                    "failure_reason": f"HTTP error {resp.status_code}",
                    "response": resp.text
                })
                all_passed = False
                print_safe(f"--> FAIL (HTTP status {resp.status_code})")
                continue

            data = resp.json()
            answer_text = data.get("response") or data.get("answer") or ""
            source_tier = data.get("source_tier") or data.get("tier")

            passed, reason = scorer(answer_text)

            results.append({
                "id": qid,
                "question": qtext,
                "chapter_progress": prog,
                "status_code": 200,
                "source_tier": source_tier,
                "passed": passed,
                "failure_reason": reason if not passed else None,
                "response": answer_text
            })

            if passed:
                print_safe(f"--> PASS (Tier: {source_tier})")
            else:
                all_passed = False
                print_safe(f"--> FAIL: {reason}")

        except Exception as e:
            results.append({
                "id": qid,
                "question": qtext,
                "chapter_progress": prog,
                "passed": False,
                "failure_reason": f"Request failed: {str(e)}",
                "response": None
            })
            all_passed = False
            print_safe(f"--> FAIL: Exception {e}")

        print_safe("-" * 60)

    report = {
        "timestamp": started_at,
        "base_url": base_url,
        "all_passed": all_passed,
        "summary": {
            "total": len(REGRESSION_CASES),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"])
        },
        "results": results
    }

    return report

def main():
    parser = argparse.ArgumentParser(description="Oracle RAG Self-Learning UX Regression Pack.")
    parser.add_argument("--base-url", type=str, default="https://mat-the-website.onrender.com", help="Target API base URL.")
    parser.add_argument("--json", action="store_true", help="Print only JSON results report.")
    args = parser.parse_args()

    report = run_regression_pack(args.base_url)

    # Save to file
    report_dir = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend\rag"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "generated_oracle_self_learning_regression_report.json")
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    except Exception as e:
        if not args.json:
            print_safe(f"Warning: could not save report to {report_path}: {e}")

    if args.json:
        print_safe(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_safe("\nREGRESSION PACK RUN SUMMARY:")
        print_safe(f"Timestamp: {report['timestamp']}")
        print_safe(f"Total Test Cases: {report['summary']['total']}")
        print_safe(f"Passed: {report['summary']['passed']}")
        print_safe(f"Failed: {report['summary']['failed']}")
        print_safe(f"Overall Result: {'PASS' if report['all_passed'] else 'FAIL'}")
        print_safe(f"Report saved to: {report_path}")

    if not report["all_passed"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
