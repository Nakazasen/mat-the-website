from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env", override=False)

import backend.main as app_main  # noqa: E402


SUSPICIOUS_TOKENS = [
    "Ã¡",
    "Ã¢",
    "Ã£",
    "Ã¨",
    "Ã©",
    "Ãª",
    "Ã¬",
    "Ã­",
    "Ã²",
    "Ã³",
    "Ã´",
    "Ãµ",
    "Ã¹",
    "Ãº",
    "Ã½",
    "Äƒ",
    "Ä‘",
    "Äƒ",
    "Æ°",
    "Æ¡",
    "Æ¯",
    "á»",
    "áº",
    "â€",
    "â€™",
    "â€œ",
    "â€�",
    "â€“",
    "â€”",
    "â€¦",
    "ï»¿",
    "\ufffd",
]

SUSPICIOUS_REGEXES = [
    re.compile(r"Ã[a-zA-Z0-9]"),
    re.compile(r"Ä[\x80-\xBFa-zA-Z0-9]"),
    re.compile(r"Æ[\x80-\xBFa-zA-Z0-9]"),
    re.compile(r"á[»º¼½][0-9A-Za-z]"),
    re.compile(r"â€[™œ”" + "\x93\x94\x99" + r"]"),
]

VIETNAMESE_HINTS = set("ăâđêôơưĂÂĐÊÔƠƯáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ")


@dataclass
class Finding:
    issue_type: str
    dataset: str
    record_id: str
    locale: str
    field: str
    suspicious_score: int
    sample: str
    strategy: str
    extra: dict[str, Any]


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "")


def suspicious_score(text: Optional[str]) -> int:
    if not text:
        return 0
    score = 0
    for token in SUSPICIOUS_TOKENS:
        score += text.count(token)
    for regex in SUSPICIOUS_REGEXES:
        score += len(regex.findall(text)) * 2
    return score


def first_suspicious_excerpt(text: Optional[str], width: int = 120) -> str:
    if not text:
        return ""
    cleaned = strip_html(text).replace("\r", " ").replace("\n", " ")
    for token in SUSPICIOUS_TOKENS:
        idx = cleaned.find(token)
        if idx >= 0:
            start = max(0, idx - width // 2)
            end = min(len(cleaned), idx + width // 2)
            return cleaned[start:end].strip()
    return cleaned[:width].strip()


def vietnamese_char_score(text: str) -> int:
    return sum(1 for ch in text if ch in VIETNAMESE_HINTS)


def cjk_char_score(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def japanese_char_score(text: str) -> int:
    return sum(
        1
        for ch in text
        if ("\u3040" <= ch <= "\u309f") or ("\u30a0" <= ch <= "\u30ff")
    )


def locale_mismatch_score(text: Optional[str], locale: str) -> int:
    if not text or locale == "vi":
        return 0
    cleaned = strip_html(text)
    vi_score = vietnamese_char_score(cleaned)
    cjk_score = cjk_char_score(cleaned)
    ja_score = japanese_char_score(cleaned)
    if locale == "en":
        return vi_score if vi_score >= 3 else 0
    if locale == "zh-CN":
        if vi_score >= 3 and cjk_score < 10:
            return vi_score + 5
        return 0
    if locale == "ja":
        if vi_score >= 3 and (ja_score + cjk_score) < 10:
            return vi_score + 5
        return 0
    return 0


def try_decode_roundtrip(text: str, source_encoding: str) -> Optional[str]:
    try:
        return text.encode(source_encoding).decode("utf-8")
    except Exception:
        return None


def choose_best_repair(text: str) -> Optional[str]:
    if not text:
        return None

    original_score = suspicious_score(text)
    candidates = []
    for encoding in ("latin1", "cp1252"):
        repaired = try_decode_roundtrip(text, encoding)
        if not repaired or repaired == text:
            continue
        candidates.append(repaired)

    best_text = None
    best_tuple = None
    for repaired in candidates:
        repaired_score = suspicious_score(repaired)
        ranking = (
            repaired_score,
            -vietnamese_char_score(repaired),
            len(repaired),
        )
        if best_tuple is None or ranking < best_tuple:
            best_tuple = ranking
            best_text = repaired

    if best_text is None:
        return None
    if suspicious_score(best_text) >= original_score:
        return None
    return best_text


def looks_dirty(text: Optional[str]) -> bool:
    return suspicious_score(text) > 0


def paged_select(
    table: str,
    select_fields: str,
    *,
    page_size: int = 500,
    filters: Optional[Iterable[tuple[str, str, Any]]] = None,
) -> list[dict]:
    rows: list[dict] = []
    offset = 0
    while True:
        query = app_main.supabase.table(table).select(select_fields)
        for column, op, value in filters or []:
            query = getattr(query, op)(column, value)
        result = query.range(offset, offset + page_size - 1).execute()
        batch = result.data or []
        rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
    return rows


def add_findings(
    findings: list[Finding],
    *,
    issue_type: str,
    dataset: str,
    record_id: str,
    locale: str,
    field_map: dict[str, Optional[str]],
    strategy: str,
    extra: Optional[dict[str, Any]] = None,
) -> None:
    for field, raw_text in field_map.items():
        score = suspicious_score(raw_text)
        if score <= 0:
            continue
        findings.append(
            Finding(
                issue_type=issue_type,
                dataset=dataset,
                record_id=record_id,
                locale=locale,
                field=field,
                suspicious_score=score,
                sample=first_suspicious_excerpt(raw_text),
                strategy=strategy,
                extra=extra or {},
            )
        )


def scan_homepage(findings: list[Finding]) -> None:
    base_rows = paged_select(
        "homepage_settings",
        "id, warning_title, warning_subtitle, warning_headline, warning_description, features_title, features_json",
    )
    for row in base_rows:
        features = row.get("features_json") or []
        features_text = json.dumps(features, ensure_ascii=False)
        add_findings(
            findings,
            issue_type="mojibake",
            dataset="homepage_settings",
            record_id=str(row["id"]),
            locale="vi",
            field_map={
                "warning_title": row.get("warning_title"),
                "warning_subtitle": row.get("warning_subtitle"),
                "warning_headline": row.get("warning_headline"),
                "warning_description": row.get("warning_description"),
                "features_title": row.get("features_title"),
                "features_json": features_text,
            },
            strategy="repair_base_text",
        )

    translated_rows = paged_select(
        "homepage_settings_translations",
        "id, homepage_settings_id, locale, warning_title, warning_subtitle, warning_headline, warning_description, features_title, features_json",
    )
    for row in translated_rows:
        add_findings(
            findings,
            issue_type="mojibake",
            dataset="homepage_settings_translations",
            record_id=str(row["id"]),
            locale=row.get("locale") or "",
            field_map={
                "warning_title": row.get("warning_title"),
                "warning_subtitle": row.get("warning_subtitle"),
                "warning_headline": row.get("warning_headline"),
                "warning_description": row.get("warning_description"),
                "features_title": row.get("features_title"),
                "features_json": json.dumps(row.get("features_json") or [], ensure_ascii=False),
            },
            strategy="retranslate_translation",
            extra={"homepage_settings_id": row.get("homepage_settings_id")},
        )
        mismatch_score = 0
        mismatch_score += locale_mismatch_score(row.get("warning_title"), row.get("locale") or "")
        mismatch_score += locale_mismatch_score(row.get("warning_description"), row.get("locale") or "")
        mismatch_score += locale_mismatch_score(json.dumps(row.get("features_json") or [], ensure_ascii=False), row.get("locale") or "")
        if mismatch_score > 0:
            findings.append(
                Finding(
                    issue_type="locale_mismatch",
                    dataset="homepage_settings_translations",
                    record_id=str(row["id"]),
                    locale=row.get("locale") or "",
                    field="payload",
                    suspicious_score=mismatch_score,
                    sample=first_suspicious_excerpt(
                        " ".join(
                            str(part or "")
                            for part in [
                                row.get("warning_title"),
                                row.get("warning_description"),
                                json.dumps(row.get("features_json") or [], ensure_ascii=False),
                            ]
                        )
                    ),
                    strategy="retranslate_translation",
                    extra={"homepage_settings_id": row.get("homepage_settings_id")},
                )
            )


def scan_wiki(findings: list[Finding]) -> None:
    base_rows = paged_select("wiki_entries", "id, slug, title, summary, content")
    for row in base_rows:
        add_findings(
            findings,
            issue_type="mojibake",
            dataset="wiki_entries",
            record_id=str(row["id"]),
            locale="vi",
            field_map={
                "title": row.get("title"),
                "summary": row.get("summary"),
                "content": row.get("content"),
            },
            strategy="repair_base_text",
            extra={"slug": row.get("slug")},
        )

    translated_rows = paged_select("wiki_entry_translations", "id, wiki_entry_id, locale, title, summary, content")
    for row in translated_rows:
        add_findings(
            findings,
            issue_type="mojibake",
            dataset="wiki_entry_translations",
            record_id=str(row["id"]),
            locale=row.get("locale") or "",
            field_map={
                "title": row.get("title"),
                "summary": row.get("summary"),
                "content": row.get("content"),
            },
            strategy="retranslate_translation",
            extra={"wiki_entry_id": row.get("wiki_entry_id")},
        )
        mismatch_score = 0
        mismatch_score += locale_mismatch_score(row.get("title"), row.get("locale") or "")
        mismatch_score += locale_mismatch_score(row.get("summary"), row.get("locale") or "")
        mismatch_score += locale_mismatch_score(row.get("content"), row.get("locale") or "")
        if mismatch_score > 0:
            findings.append(
                Finding(
                    issue_type="locale_mismatch",
                    dataset="wiki_entry_translations",
                    record_id=str(row["id"]),
                    locale=row.get("locale") or "",
                    field="payload",
                    suspicious_score=mismatch_score,
                    sample=first_suspicious_excerpt(" ".join(str(row.get(field) or "") for field in ("title", "summary", "content"))),
                    strategy="retranslate_translation",
                    extra={"wiki_entry_id": row.get("wiki_entry_id")},
                )
            )


def scan_guides(findings: list[Finding]) -> None:
    guide_rows = paged_select("guide_pages", "id, slug, scope, title, content")
    for row in guide_rows:
        slug = str(row.get("slug") or "")
        locale = "vi"
        strategy = "repair_base_text"
        if "__" in slug:
            _, locale = slug.rsplit("__", 1)
            strategy = "retranslate_translation"
        add_findings(
            findings,
            issue_type="mojibake",
            dataset="guide_pages",
            record_id=str(row["id"]),
            locale=locale,
            field_map={
                "title": row.get("title"),
                "content": row.get("content"),
            },
            strategy=strategy,
            extra={"slug": slug, "scope": row.get("scope")},
        )
        if locale != "vi":
            mismatch_score = locale_mismatch_score(row.get("title"), locale) + locale_mismatch_score(row.get("content"), locale)
            if mismatch_score > 0:
                findings.append(
                    Finding(
                        issue_type="locale_mismatch",
                        dataset="guide_pages",
                        record_id=str(row["id"]),
                        locale=locale,
                        field="payload",
                        suspicious_score=mismatch_score,
                        sample=first_suspicious_excerpt(f"{row.get('title') or ''} {row.get('content') or ''}"),
                        strategy="retranslate_translation",
                        extra={"slug": slug, "scope": row.get("scope")},
                    )
                )


def scan_chapter_translations(findings: list[Finding]) -> None:
    rows = paged_select(
        "chapter_translations",
        "id, chapter_id, locale, title, content, summary, translation_status, last_error",
    )
    for row in rows:
        add_findings(
            findings,
            issue_type="mojibake",
            dataset="chapter_translations",
            record_id=str(row["id"]),
            locale=row.get("locale") or "",
            field_map={
                "title": row.get("title"),
                "summary": row.get("summary"),
                "content": row.get("content"),
                "last_error": row.get("last_error"),
            },
            strategy="retranslate_translation",
            extra={
                "chapter_id": row.get("chapter_id"),
                "translation_status": row.get("translation_status"),
            },
        )
        mismatch_score = 0
        mismatch_score += locale_mismatch_score(row.get("title"), row.get("locale") or "")
        mismatch_score += locale_mismatch_score(row.get("summary"), row.get("locale") or "")
        mismatch_score += locale_mismatch_score(row.get("content"), row.get("locale") or "")
        if mismatch_score > 0:
            findings.append(
                Finding(
                    issue_type="locale_mismatch",
                    dataset="chapter_translations",
                    record_id=str(row["id"]),
                    locale=row.get("locale") or "",
                    field="payload",
                    suspicious_score=mismatch_score,
                    sample=first_suspicious_excerpt(" ".join(str(row.get(field) or "") for field in ("title", "summary", "content"))),
                    strategy="retranslate_translation",
                    extra={
                        "chapter_id": row.get("chapter_id"),
                        "translation_status": row.get("translation_status"),
                    },
                )
            )


def scan_all() -> list[Finding]:
    findings: list[Finding] = []
    scan_homepage(findings)
    scan_wiki(findings)
    scan_guides(findings)
    scan_chapter_translations(findings)
    return findings


def summarize_findings(findings: list[Finding]) -> dict[str, Any]:
    by_dataset: dict[str, int] = {}
    by_locale: dict[str, int] = {}
    for item in findings:
        by_dataset[item.dataset] = by_dataset.get(item.dataset, 0) + 1
        by_locale[item.locale] = by_locale.get(item.locale, 0) + 1
    return {
        "total_findings": len(findings),
        "datasets": by_dataset,
        "locales": by_locale,
    }


def write_report(findings: list[Finding], output_path: Optional[Path]) -> Path:
    output_dir = REPO_ROOT / "reports"
    output_dir.mkdir(exist_ok=True)
    if output_path is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_path = output_dir / f"mojibake_scan_{stamp}.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summarize_findings(findings),
        "findings": [asdict(item) for item in findings],
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def group_findings_for_action(findings: list[Finding]) -> dict[tuple[str, str], list[Finding]]:
    grouped: dict[tuple[str, str], list[Finding]] = {}
    for item in findings:
        grouped.setdefault((item.dataset, item.record_id), []).append(item)
    return grouped


def repair_base_wiki(row_id: str) -> bool:
    result = app_main.supabase.table("wiki_entries").select("id, title, summary, content").eq("id", row_id).limit(1).execute()
    if not result.data:
        return False
    row = result.data[0]
    update_data = {}
    for field in ("title", "summary", "content"):
        repaired = choose_best_repair(row.get(field) or "")
        if repaired:
            update_data[field] = repaired
    if not update_data:
        return False
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    app_main.supabase.table("wiki_entries").update(update_data).eq("id", row_id).execute()
    return True


def repair_base_guide(row_id: str) -> bool:
    result = app_main.supabase.table("guide_pages").select("id, title, content, slug").eq("id", row_id).limit(1).execute()
    if not result.data:
        return False
    row = result.data[0]
    if "__" in str(row.get("slug") or ""):
        return False
    update_data = {}
    for field in ("title", "content"):
        repaired = choose_best_repair(row.get(field) or "")
        if repaired:
            update_data[field] = repaired
    if not update_data:
        return False
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    app_main.supabase.table("guide_pages").update(update_data).eq("id", row_id).execute()
    return True


def repair_base_homepage(row_id: str) -> bool:
    result = (
        app_main.supabase.table("homepage_settings")
        .select("id, warning_title, warning_subtitle, warning_headline, warning_description, features_title, features_json")
        .eq("id", row_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        return False
    row = result.data[0]
    update_data = {}
    for field in ("warning_title", "warning_subtitle", "warning_headline", "warning_description", "features_title"):
        repaired = choose_best_repair(row.get(field) or "")
        if repaired:
            update_data[field] = repaired
    features = row.get("features_json") or []
    repaired_features = []
    changed_features = False
    for item in features:
        if not isinstance(item, dict):
            repaired_features.append(item)
            continue
        new_item = dict(item)
        for key in ("title", "desc", "icon"):
            if isinstance(item.get(key), str):
                repaired = choose_best_repair(item[key])
                if repaired:
                    new_item[key] = repaired
                    changed_features = True
        repaired_features.append(new_item)
    if changed_features:
        update_data["features_json"] = repaired_features
    if not update_data:
        return False
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    app_main.supabase.table("homepage_settings").update(update_data).eq("id", row_id).execute()
    return True


async def retranslate_chapter_translation(chapter_id: Any, locale: str) -> bool:
    result = app_main.supabase.table("chapters").select("id, chapter_number, title, content_url").eq("id", chapter_id).limit(1).execute()
    if not result.data:
        return False
    row = result.data[0]
    content = app_main.fetch_r2_content(row.get("content_url") or "")
    await app_main.upsert_chapter_translations(row, row.get("title") or "", content, [locale])
    return True


async def retranslate_wiki_translation(entry_id: Any, locale: str) -> bool:
    result = app_main.supabase.table("wiki_entries").select("*").eq("id", entry_id).limit(1).execute()
    if not result.data:
        return False
    row = dict(result.data[0])
    row["summary"] = app_main.sanitize_html(row.get("summary")) if row.get("summary") is not None else None
    row["content"] = app_main.sanitize_html(row.get("content")) if row.get("content") is not None else None
    await app_main.upsert_wiki_translations(row, [locale])
    return True


async def retranslate_homepage_translation(homepage_settings_id: Any, locale: str) -> bool:
    result = app_main.supabase.table("homepage_settings").select("*").eq("id", homepage_settings_id).limit(1).execute()
    if not result.data:
        return False
    payload = app_main.prepare_homepage_settings_payload(result.data[0])
    await app_main.upsert_homepage_translations(payload, [locale])
    return True


async def retranslate_guide_translation(slug: str, scope: str, locale: str) -> bool:
    result = app_main.supabase.table("guide_pages").select("*").eq("slug", slug).limit(1).execute()
    if not result.data:
        return False
    base_row = dict(result.data[0])
    payload = {
        "title": app_main.sanitize_plaintext(str(base_row.get("title") or "").strip()),
        "content": app_main.sanitize_html(base_row.get("content")) if base_row.get("content") is not None else "",
    }
    await app_main.upsert_guide_translations(slug, scope, payload, [locale])
    return True


async def apply_fix(findings: list[Finding]) -> dict[str, Any]:
    grouped = group_findings_for_action(findings)
    results = {"repaired": [], "retranslated": [], "failed": []}
    for (dataset, record_id), items in grouped.items():
        locale = items[0].locale
        extra = items[0].extra
        try:
            handled = False
            if dataset == "wiki_entries":
                handled = repair_base_wiki(record_id)
                if handled:
                    results["repaired"].append({"dataset": dataset, "record_id": record_id})
            elif dataset == "guide_pages" and locale == "vi":
                handled = repair_base_guide(record_id)
                if handled:
                    results["repaired"].append({"dataset": dataset, "record_id": record_id})
            elif dataset == "homepage_settings":
                handled = repair_base_homepage(record_id)
                if handled:
                    results["repaired"].append({"dataset": dataset, "record_id": record_id})
            elif dataset == "chapter_translations":
                handled = await retranslate_chapter_translation(extra["chapter_id"], locale)
            elif dataset == "wiki_entry_translations":
                handled = await retranslate_wiki_translation(extra["wiki_entry_id"], locale)
            elif dataset == "homepage_settings_translations":
                handled = await retranslate_homepage_translation(extra["homepage_settings_id"], locale)
            elif dataset == "guide_pages":
                base_slug = str(extra["slug"]).split("__", 1)[0]
                handled = await retranslate_guide_translation(base_slug, extra.get("scope") or "public", locale)

            if handled and dataset not in {"wiki_entries", "guide_pages", "homepage_settings"}:
                results["retranslated"].append({"dataset": dataset, "record_id": record_id, "locale": locale})
            elif not handled:
                results["failed"].append({"dataset": dataset, "record_id": record_id, "locale": locale, "detail": "No change applied"})
        except Exception as exc:
            results["failed"].append({"dataset": dataset, "record_id": record_id, "locale": locale, "detail": str(exc)})
    return results


def filter_findings(
    findings: list[Finding],
    *,
    datasets: Optional[set[str]] = None,
    locales: Optional[set[str]] = None,
) -> list[Finding]:
    filtered = []
    for item in findings:
        if datasets and item.dataset not in datasets:
            continue
        if locales and item.locale not in locales:
            continue
        filtered.append(item)
    return filtered


def parse_csv_set(raw: Optional[str]) -> Optional[set[str]]:
    if not raw:
        return None
    return {item.strip() for item in raw.split(",") if item.strip()}


async def main() -> int:
    parser = argparse.ArgumentParser(description="Scan and optionally fix mojibake in production content tables.")
    parser.add_argument("--apply", action="store_true", help="Apply safe fixes and selective retranslation for findings.")
    parser.add_argument("--report", type=Path, help="Write report JSON to this path.")
    parser.add_argument("--datasets", help="Comma-separated dataset filter.")
    parser.add_argument("--locales", help="Comma-separated locale filter.")
    args = parser.parse_args()

    findings = scan_all()
    findings = filter_findings(
        findings,
        datasets=parse_csv_set(args.datasets),
        locales=parse_csv_set(args.locales),
    )
    report_path = write_report(findings, args.report)

    print(json.dumps({"report": str(report_path), "summary": summarize_findings(findings)}, ensure_ascii=False, indent=2))

    if not args.apply:
        return 0

    results = await apply_fix(findings)
    print(json.dumps({"apply_results": results}, ensure_ascii=False, indent=2))
    return 0 if not results["failed"] else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
