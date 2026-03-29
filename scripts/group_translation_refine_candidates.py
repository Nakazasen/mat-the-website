from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

ACTION_RANK = {"retranslate": 0, "refine": 1, "safe": 2}
SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Group translation refine scan rows by chapter_number for batch admin operations."
    )
    parser.add_argument("--input", type=str, required=True, help="Path to scan JSON report.")
    parser.add_argument("--output", type=str, default="", help="Optional grouped JSON output path.")
    parser.add_argument("--csv-output", type=str, default="", help="Optional grouped CSV output path.")
    parser.add_argument("--top", type=int, default=50, help="Print top N grouped chapters.")
    return parser.parse_args()


def resolve_output_path(raw_path: str, suffix: str) -> Path:
    if raw_path:
        return Path(raw_path)
    output_dir = REPO_ROOT / "reports"
    output_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return output_dir / f"grouped_translation_refine_candidates_{stamp}.{suffix}"


def load_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def group_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[int, dict[str, Any]] = {}

    for row in rows:
        chapter_number = int(row["chapter_number"])
        target = grouped.setdefault(
            chapter_number,
            {
                "chapter_number": chapter_number,
                "retranslate_locales": [],
                "refine_locales": [],
                "highest_action": "safe",
                "highest_severity": "low",
                "max_priority_score": 0,
                "locale_actions": {},
                "locale_reasons": {},
            },
        )

        locale = str(row["locale"])
        action = str(row["action"])
        severity = str(row["severity"])
        priority = int(row["priority_score"])
        reasons = list(row.get("reason_codes") or [])

        if action == "retranslate":
            target["retranslate_locales"].append(locale)
        elif action == "refine":
            target["refine_locales"].append(locale)

        target["locale_actions"][locale] = action
        target["locale_reasons"][locale] = reasons
        target["max_priority_score"] = max(target["max_priority_score"], priority)

        current_action = target["highest_action"]
        current_severity = target["highest_severity"]
        if ACTION_RANK.get(action, 9) < ACTION_RANK.get(current_action, 9):
            target["highest_action"] = action
        if SEVERITY_RANK.get(severity, 9) < SEVERITY_RANK.get(current_severity, 9):
            target["highest_severity"] = severity

    result = list(grouped.values())
    for row in result:
        row["retranslate_locales"] = sorted(set(row["retranslate_locales"]))
        row["refine_locales"] = sorted(set(row["refine_locales"]))

    return sorted(
        result,
        key=lambda item: (
            ACTION_RANK.get(item["highest_action"], 9),
            SEVERITY_RANK.get(item["highest_severity"], 9),
            -int(item["max_priority_score"]),
            int(item["chapter_number"]),
        ),
    )


def build_summary(grouped_rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "chapters_needing_attention": len(grouped_rows),
        "highest_action_counts": {},
        "retranslate_locale_totals": {},
        "refine_locale_totals": {},
    }
    for row in grouped_rows:
        highest_action = str(row["highest_action"])
        summary["highest_action_counts"][highest_action] = summary["highest_action_counts"].get(highest_action, 0) + 1
        for locale in row["retranslate_locales"]:
            summary["retranslate_locale_totals"][locale] = summary["retranslate_locale_totals"].get(locale, 0) + 1
        for locale in row["refine_locales"]:
            summary["refine_locale_totals"][locale] = summary["refine_locale_totals"].get(locale, 0) + 1
    return summary


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "chapter_number",
        "highest_action",
        "highest_severity",
        "max_priority_score",
        "retranslate_locales",
        "refine_locales",
        "locale_actions",
        "locale_reasons",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            payload = dict(row)
            payload["retranslate_locales"] = ",".join(row["retranslate_locales"])
            payload["refine_locales"] = ",".join(row["refine_locales"])
            payload["locale_actions"] = json.dumps(row["locale_actions"], ensure_ascii=False)
            payload["locale_reasons"] = json.dumps(row["locale_reasons"], ensure_ascii=False)
            writer.writerow(payload)


def print_top(rows: list[dict[str, Any]], top: int) -> None:
    visible = rows if top <= 0 else rows[:top]
    if not visible:
        print("No grouped chapters need attention.")
        return

    print("")
    print("Top grouped chapters:")
    for row in visible:
        print(
            f"- chapter={row['chapter_number']} highest_action={row['highest_action']} "
            f"severity={row['highest_severity']} score={row['max_priority_score']} "
            f"retranslate={','.join(row['retranslate_locales']) or '-'} "
            f"refine={','.join(row['refine_locales']) or '-'}"
        )


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    report = load_report(input_path)
    grouped_rows = group_rows(list(report.get("rows") or []))
    summary = build_summary(grouped_rows)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_report": str(input_path),
        "source_summary": report.get("summary") or {},
        "summary": summary,
        "chapters": grouped_rows,
    }

    json_path = resolve_output_path(args.output, "json")
    csv_path = resolve_output_path(args.csv_output, "csv")
    write_json(json_path, payload)
    write_csv(csv_path, grouped_rows)

    print("Summary:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"JSON report: {json_path}")
    print(f"CSV report:  {csv_path}")
    print_top(grouped_rows, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
