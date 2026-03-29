from __future__ import annotations

import argparse
import csv
import html
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from supabase import create_client


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.main import fetch_r2_content, normalize_locale, supabase as backend_supabase  # noqa: E402
from backend.routes.reader_learning import (  # noqa: E402
    _extract_sentence_alignment_entries,
    _filtered_sentence_count,
    _source_reference_structure_is_reliable,
    _split_text_blocks,
)
from scripts.scan_and_fix_mojibake import suspicious_score  # noqa: E402


DEFAULT_LOCALES = ("en", "zh-CN", "ja")
DEFAULT_STATUS = "published"
DEFAULT_END_CHAPTER = 548
VIETNAMESE_DIACRITICS = set("ăâêôơưđàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵĂÂÊÔƠƯĐÀÁẢÃẠẰẮẲẴẶẦẤẨẪẬÈÉẺẼẸỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌỒỐỔỖỘỜỚỞỠỢÙÚỦŨỤỪỨỬỮỰỲÝỶỸỴ")


@dataclass
class ScanRow:
    chapter_number: int
    chapter_id: int
    locale: str
    action: str
    severity: str
    priority_score: int
    reason_codes: list[str]
    translation_source: str
    translation_status: str
    has_sentence_alignment: bool
    alignment_entry_count: int
    source_sentence_count: int
    translated_sentence_count: int
    sentence_ratio: float
    source_block_count: int
    translated_block_count: int
    block_delta: int
    structure_reliable: bool
    mojibake_score: int
    locale_mismatch_score: int
    sample: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan translated chapters and rank chapter-locale rows that should be refined or retranslated first."
    )
    parser.add_argument("--start-chapter", type=int, default=1, help="Start chapter number (inclusive).")
    parser.add_argument("--end-chapter", type=int, default=DEFAULT_END_CHAPTER, help="End chapter number (inclusive).")
    parser.add_argument("--locales", type=str, default="en,zh-CN,ja", help="Comma-separated locales to scan.")
    parser.add_argument("--status", type=str, default=DEFAULT_STATUS, help="Translation status filter.")
    parser.add_argument("--include-safe", action="store_true", help="Include safe rows in output.")
    parser.add_argument("--top", type=int, default=50, help="Print top N candidates to stdout (0 = print all).")
    parser.add_argument("--output", type=str, default="", help="Optional JSON output path.")
    parser.add_argument("--csv-output", type=str, default="", help="Optional CSV output path.")
    return parser.parse_args()


def parse_locales(raw_locales: str) -> list[str]:
    locales: list[str] = []
    for token in raw_locales.split(","):
        locale = normalize_locale(token.strip())
        if not locale or locale == "vi":
            continue
        if locale not in locales:
            locales.append(locale)
    return locales or list(DEFAULT_LOCALES)


def get_supabase_client():
    load_dotenv(REPO_ROOT / ".env", override=False)
    load_dotenv(BACKEND_DIR / ".env", override=True)
    load_dotenv(override=True)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        return backend_supabase
    try:
        return create_client(url, key)
    except Exception:
        return backend_supabase


def chunked(items: list[Any], size: int) -> list[list[Any]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def fetch_chapters(supabase, start_chapter: int, end_chapter: int) -> list[dict[str, Any]]:
    result = (
        supabase.table("chapters")
        .select("id, chapter_number, content_url")
        .gte("chapter_number", start_chapter)
        .lte("chapter_number", end_chapter)
        .order("chapter_number")
        .execute()
    )
    return list(result.data or [])


def fetch_translations(
    supabase,
    chapter_ids: list[int],
    locales: list[str],
    status: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for id_batch in chunked(chapter_ids, 200):
        query = (
            supabase.table("chapter_translations")
            .select(
                "id, chapter_id, locale, title, summary, content, translation_status, translation_source, sentence_alignment"
            )
            .eq("translation_status", status)
            .in_("chapter_id", id_batch)
        )
        if locales:
            query = query.in_("locale", locales)
        result = query.execute()
        rows.extend(list(result.data or []))
    return rows


def build_sample(text: Optional[str], max_length: int = 120) -> str:
    cleaned = " ".join(str(text or "").replace("\r", " ").replace("\n", " ").split())
    if len(cleaned) <= max_length:
        return cleaned
    return f"{cleaned[:max_length].rstrip()}..."


def strip_html(text: Optional[str]) -> str:
    normalized = re.sub(r"(?i)<br\\s*/?>", "\n", str(text or ""))
    normalized = re.sub(r"<[^>]+>", " ", normalized)
    normalized = html.unescape(normalized)
    return " ".join(normalized.replace("\r", " ").replace("\n", " ").split())


def vietnamese_diacritic_count(text: Optional[str]) -> int:
    return sum(1 for ch in strip_html(text) if ch in VIETNAMESE_DIACRITICS)


def cjk_count(text: Optional[str]) -> int:
    return sum(1 for ch in strip_html(text) if "\u4e00" <= ch <= "\u9fff")


def kana_count(text: Optional[str]) -> int:
    return sum(
        1
        for ch in strip_html(text)
        if ("\u3040" <= ch <= "\u309f") or ("\u30a0" <= ch <= "\u30ff")
    )


def strict_locale_mismatch_score(text: Optional[str], locale: str) -> int:
    cleaned = strip_html(text)
    if not cleaned or locale == "vi":
        return 0

    vi_count = vietnamese_diacritic_count(cleaned)
    cjk_char_count = cjk_count(cleaned)
    kana_char_count = kana_count(cleaned)

    if locale == "en":
        if vi_count >= 8:
            return vi_count
        if cjk_char_count >= 12:
            return cjk_char_count
        return 0

    if locale == "zh-CN":
        if vi_count >= 8 and cjk_char_count < 40:
            return vi_count + 20
        return 0

    if locale == "ja":
        if vi_count >= 8 and (cjk_char_count + kana_char_count) < 40:
            return vi_count + 20
        return 0

    return 0


def round_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 3)


def compute_priority(
    *,
    sentence_ratio: float,
    block_delta: int,
    mojibake: int,
    locale_mismatch: int,
    structure_reliable: bool,
    has_alignment: bool,
    translation_source: str,
) -> tuple[str, str, int, list[str]]:
    reasons: list[str] = []
    priority = 0

    if mojibake > 0:
        reasons.append("mojibake")
        priority += 220 + min(mojibake, 30)
    if locale_mismatch > 0:
        reasons.append("wrong_locale_content")
        priority += 200 + min(locale_mismatch, 30)

    ratio_gap = abs(sentence_ratio - 1.0)
    extreme_structure = sentence_ratio < 0.58 or sentence_ratio > 1.75
    high_structure_drift = sentence_ratio < 0.67 or sentence_ratio > 1.5
    moderate_structure_drift = sentence_ratio < 0.8 or sentence_ratio > 1.3

    if extreme_structure:
        reasons.append("sentence_ratio_extreme")
        priority += 140 + int(ratio_gap * 100)
    elif high_structure_drift:
        reasons.append("sentence_ratio_unreliable")
        priority += 95 + int(ratio_gap * 100)
    elif moderate_structure_drift:
        reasons.append("sentence_ratio_drift")
        priority += 35 + int(ratio_gap * 100)

    if block_delta >= 8:
        reasons.append("block_delta_extreme")
        priority += 70 + (block_delta * 2)
    elif block_delta > 2:
        reasons.append("block_delta_high")
        priority += 30 + (block_delta * 3)

    if not structure_reliable:
        reasons.append("source_reference_unreliable")
        priority += 45

    if not has_alignment:
        reasons.append("missing_alignment")
        priority += 8

    if translation_source == "ai_refine" and priority > 0:
        reasons.append("already_refined_but_still_bad")
        priority += 20

    if "mojibake" in reasons or "wrong_locale_content" in reasons:
        return "retranslate", "critical", priority, reasons
    if extreme_structure or block_delta >= 8:
        return "retranslate", "high", priority, reasons
    if not structure_reliable or block_delta > 2:
        return "refine", "high" if priority >= 120 else "medium", priority, reasons
    if moderate_structure_drift or not has_alignment:
        return "refine", "medium", priority, reasons
    return "safe", "low", priority, reasons


def scan_rows(
    chapters: list[dict[str, Any]],
    translations: list[dict[str, Any]],
) -> tuple[list[ScanRow], dict[str, Any]]:
    chapter_by_id = {int(row["id"]): row for row in chapters}
    source_cache: dict[int, dict[str, Any]] = {}
    scanned_rows: list[ScanRow] = []
    fetch_failures: list[dict[str, Any]] = []

    for row in sorted(
        translations,
        key=lambda item: (
            int(chapter_by_id.get(int(item["chapter_id"]), {}).get("chapter_number") or 0),
            str(item.get("locale") or ""),
        ),
    ):
        chapter_id = int(row["chapter_id"])
        chapter = chapter_by_id.get(chapter_id)
        if not chapter:
            continue

        if chapter_id not in source_cache:
            try:
                source_text = fetch_r2_content(str(chapter.get("content_url") or ""))
                source_cache[chapter_id] = {
                    "source_text": source_text,
                    "source_sentence_count": _filtered_sentence_count(source_text),
                    "source_block_count": len(_split_text_blocks(source_text)),
                }
            except Exception as exc:
                fetch_failures.append(
                    {
                        "chapter_number": int(chapter["chapter_number"]),
                        "chapter_id": chapter_id,
                        "detail": str(exc),
                    }
                )
                source_cache[chapter_id] = {
                    "source_text": "",
                    "source_sentence_count": 0,
                    "source_block_count": 0,
                }

        source_meta = source_cache[chapter_id]
        translated_text = str(row.get("content") or "")
        translated_sentence_count = _filtered_sentence_count(translated_text)
        translated_block_count = len(_split_text_blocks(translated_text))
        source_sentence_count = int(source_meta["source_sentence_count"])
        source_block_count = int(source_meta["source_block_count"])
        sentence_ratio = round_ratio(translated_sentence_count, source_sentence_count)
        block_delta = abs(translated_block_count - source_block_count)
        structure_reliable = _source_reference_structure_is_reliable(
            source_meta["source_text"],
            translated_text,
        )
        alignment_entries = _extract_sentence_alignment_entries(row.get("sentence_alignment"))
        has_alignment = len(alignment_entries) > 0
        joined_payload = " ".join(
            str(row.get(field) or "")
            for field in ("title", "summary", "content")
        )
        mojibake = suspicious_score(joined_payload)
        mismatch = (
            strict_locale_mismatch_score(row.get("title"), str(row.get("locale") or ""))
            + strict_locale_mismatch_score(row.get("summary"), str(row.get("locale") or ""))
            + strict_locale_mismatch_score(row.get("content"), str(row.get("locale") or ""))
        )
        action, severity, priority, reasons = compute_priority(
            sentence_ratio=sentence_ratio,
            block_delta=block_delta,
            mojibake=mojibake,
            locale_mismatch=mismatch,
            structure_reliable=structure_reliable,
            has_alignment=has_alignment,
            translation_source=str(row.get("translation_source") or ""),
        )
        scanned_rows.append(
            ScanRow(
                chapter_number=int(chapter["chapter_number"]),
                chapter_id=chapter_id,
                locale=str(row.get("locale") or ""),
                action=action,
                severity=severity,
                priority_score=priority,
                reason_codes=reasons,
                translation_source=str(row.get("translation_source") or ""),
                translation_status=str(row.get("translation_status") or ""),
                has_sentence_alignment=has_alignment,
                alignment_entry_count=len(alignment_entries),
                source_sentence_count=source_sentence_count,
                translated_sentence_count=translated_sentence_count,
                sentence_ratio=sentence_ratio,
                source_block_count=source_block_count,
                translated_block_count=translated_block_count,
                block_delta=block_delta,
                structure_reliable=structure_reliable,
                mojibake_score=mojibake,
                locale_mismatch_score=mismatch,
                sample=build_sample(translated_text),
            )
        )

    summary = build_summary(scanned_rows, fetch_failures)
    return scanned_rows, summary


def build_summary(rows: list[ScanRow], fetch_failures: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "rows_scanned": len(rows),
        "rows_needing_attention": 0,
        "actions": {},
        "by_locale": {},
        "fetch_failures": len(fetch_failures),
    }

    for row in rows:
        locale_bucket = summary["by_locale"].setdefault(
            row.locale,
            {"scanned": 0, "safe": 0, "refine": 0, "retranslate": 0},
        )
        locale_bucket["scanned"] += 1
        locale_bucket[row.action] = locale_bucket.get(row.action, 0) + 1
        summary["actions"][row.action] = summary["actions"].get(row.action, 0) + 1
        if row.action != "safe":
            summary["rows_needing_attention"] += 1

    summary["fetch_failure_samples"] = fetch_failures[:10]
    return summary


def sort_rows(rows: list[ScanRow]) -> list[ScanRow]:
    action_rank = {"retranslate": 0, "refine": 1, "safe": 2}
    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(
        rows,
        key=lambda row: (
            action_rank.get(row.action, 9),
            severity_rank.get(row.severity, 9),
            -row.priority_score,
            row.chapter_number,
            row.locale,
        ),
    )


def resolve_output_path(raw_path: str, suffix: str) -> Path:
    if raw_path:
        return Path(raw_path)
    output_dir = REPO_ROOT / "reports"
    output_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return output_dir / f"translation_refine_candidates_{stamp}.{suffix}"


def write_json_report(path: Path, *, args: argparse.Namespace, summary: dict[str, Any], rows: list[ScanRow]) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "range": {
            "start_chapter": args.start_chapter,
            "end_chapter": args.end_chapter,
        },
        "locales": parse_locales(args.locales),
        "status": args.status,
        "summary": summary,
        "rows": [asdict(row) for row in rows],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv_report(path: Path, rows: list[ScanRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "chapter_number",
        "chapter_id",
        "locale",
        "action",
        "severity",
        "priority_score",
        "reason_codes",
        "translation_source",
        "translation_status",
        "has_sentence_alignment",
        "alignment_entry_count",
        "source_sentence_count",
        "translated_sentence_count",
        "sentence_ratio",
        "source_block_count",
        "translated_block_count",
        "block_delta",
        "structure_reliable",
        "mojibake_score",
        "locale_mismatch_score",
        "sample",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            payload = asdict(row)
            payload["reason_codes"] = ",".join(row.reason_codes)
            writer.writerow(payload)


def print_top_rows(rows: list[ScanRow], top: int) -> None:
    visible_rows = rows if top <= 0 else rows[:top]
    if not visible_rows:
        print("No chapter-locale rows matched the selected filters.")
        return
    print("")
    print("Top candidates:")
    for row in visible_rows:
        reasons = ",".join(row.reason_codes) if row.reason_codes else "-"
        print(
            f"- chapter={row.chapter_number} locale={row.locale} action={row.action} "
            f"severity={row.severity} score={row.priority_score} "
            f"ratio={row.sentence_ratio} block_delta={row.block_delta} reasons={reasons}"
        )


def main() -> int:
    args = parse_args()
    locales = parse_locales(args.locales)
    supabase = get_supabase_client()

    chapters = fetch_chapters(supabase, args.start_chapter, args.end_chapter)
    if not chapters:
        print("No chapters found in the selected range.")
        return 1

    chapter_ids = [int(row["id"]) for row in chapters]
    translations = fetch_translations(supabase, chapter_ids, locales, args.status)
    if not translations:
        print("No matching chapter translations found.")
        return 0

    print(
        f"Scanning chapters {args.start_chapter}..{args.end_chapter} "
        f"for locales={locales} status={args.status} rows={len(translations)}"
    )
    rows, summary = scan_rows(chapters, translations)
    rows = sort_rows(rows)
    if not args.include_safe:
        rows = [row for row in rows if row.action != "safe"]

    json_path = resolve_output_path(args.output, "json")
    csv_path = resolve_output_path(args.csv_output, "csv")
    write_json_report(json_path, args=args, summary=summary, rows=rows)
    write_csv_report(csv_path, rows)

    print("")
    print("Summary:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"JSON report: {json_path}")
    print(f"CSV report:  {csv_path}")
    print_top_rows(rows, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
