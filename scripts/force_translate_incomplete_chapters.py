import argparse
import asyncio
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ENV_PATH = REPO_ROOT / "backend" / ".env"
DEFAULT_CHECKPOINT = REPO_ROOT / "reports" / "force_translate_incomplete_checkpoint.json"
DEFAULT_LOG = REPO_ROOT / "reports" / "force_translate_incomplete_log.jsonl"
TARGET_LOCALES = ("en", "zh-CN", "ja")
TRANSLATION_QUERY_CHUNK_SIZE = 200


if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

load_dotenv(BACKEND_ENV_PATH, override=True)

import backend.main as main


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Force translate every chapter locale that is not yet published."
    )
    parser.add_argument("--checkpoint", default=str(DEFAULT_CHECKPOINT))
    parser.add_argument("--log", default=str(DEFAULT_LOG))
    parser.add_argument("--max-chapters", type=int, default=0, help="Optional cap for this run.")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--sleep-seconds", type=float, default=1.5)
    parser.add_argument("--retry-sleep-seconds", type=float, default=8.0)
    parser.add_argument("--reset-checkpoint", action="store_true")
    return parser.parse_args()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_checkpoint(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def append_log(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def query_translation_rows(chapter_ids: list[int]) -> list[dict[str, Any]]:
    if not chapter_ids:
        return []
    rows: list[dict[str, Any]] = []
    for start_index in range(0, len(chapter_ids), TRANSLATION_QUERY_CHUNK_SIZE):
        chunk = chapter_ids[start_index:start_index + TRANSLATION_QUERY_CHUNK_SIZE]
        chunk_rows = (
            main.supabase.table("chapter_translations")
            .select("chapter_id, locale, translation_status, last_error, updated_at")
            .in_("chapter_id", chunk)
            .execute()
            .data
            or []
        )
        rows.extend(chunk_rows)
    return rows


def build_work_items() -> list[dict[str, Any]]:
    chapter_rows = (
        main.supabase.table("chapters")
        .select("id, chapter_number, title, content_url")
        .order("chapter_number")
        .execute()
        .data
        or []
    )
    translation_rows = query_translation_rows([row["id"] for row in chapter_rows])

    translation_map: dict[int, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in translation_rows:
        chapter_id = row.get("chapter_id")
        locale = row.get("locale")
        if chapter_id and locale:
            translation_map[chapter_id][locale] = row

    work_items: list[dict[str, Any]] = []
    for chapter_row in chapter_rows:
        chapter_id = chapter_row["id"]
        needed_locales: list[str] = []
        row_statuses = translation_map.get(chapter_id, {})
        for locale in TARGET_LOCALES:
            status = row_statuses.get(locale, {}).get("translation_status")
            if status != "published":
                needed_locales.append(locale)
        if needed_locales:
            work_items.append(
                {
                    "chapter_id": chapter_id,
                    "chapter_number": chapter_row["chapter_number"],
                    "title": chapter_row["title"],
                    "content_url": chapter_row["content_url"],
                    "needed_locales": needed_locales,
                }
            )
    return work_items


async def process_chapter(
    chapter_row: dict[str, Any],
    needed_locales: list[str],
    max_retries: int,
    retry_sleep_seconds: float,
) -> dict[str, Any]:
    chapter_number = chapter_row["chapter_number"]
    content_text = main.fetch_r2_content(chapter_row["content_url"])
    if not content_text:
        raise RuntimeError(f"Could not fetch content for chapter {chapter_number}")

    remaining = list(dict.fromkeys(needed_locales))
    translated_locales: list[str] = []
    failure_details: list[dict[str, Any]] = []

    for attempt in range(1, max_retries + 1):
        if not remaining:
            break
        try:
            result = await main.upsert_chapter_translations(
                chapter_row=chapter_row,
                title=chapter_row["title"],
                content=content_text,
                locales=remaining,
                translation_mode="bulk",
            )
            success_locales = list(result.get("translated_locales") or [])
            translated_locales.extend(success_locales)

            failed_translations = list(result.get("failed_translations") or [])
            if not failed_translations:
                remaining = [locale for locale in remaining if locale not in success_locales]
                continue

            failure_details = failed_translations
            remaining = [str(item.get("locale")) for item in failed_translations if str(item.get("locale") or "").strip()]
            if attempt < max_retries and remaining:
                await asyncio.sleep(retry_sleep_seconds * attempt)
        except Exception as exc:
            failure_details = [
                {
                    "locale": ",".join(remaining),
                    "detail": str(exc),
                }
            ]
            if attempt >= max_retries:
                break
            await asyncio.sleep(retry_sleep_seconds * attempt)

    refreshed_rows = query_translation_rows([chapter_row["id"]])
    published_locales = sorted(
        row["locale"]
        for row in refreshed_rows
        if row.get("translation_status") == "published" and row.get("locale") in TARGET_LOCALES
    )
    remaining_after = [locale for locale in TARGET_LOCALES if locale not in published_locales]

    return {
        "chapter_number": chapter_number,
        "translated_locales": sorted(set(translated_locales)),
        "published_locales": published_locales,
        "remaining_locales": remaining_after,
        "failures": failure_details,
    }


async def main_async() -> int:
    args = parse_args()
    checkpoint_path = Path(args.checkpoint)
    log_path = Path(args.log)

    if args.reset_checkpoint and checkpoint_path.exists():
        checkpoint_path.unlink()

    checkpoint = load_checkpoint(checkpoint_path)
    completed_numbers = set(int(item) for item in (checkpoint.get("completed_numbers") or []) if int(item) > 0)
    failed_numbers = {
        str(key): value
        for key, value in (checkpoint.get("failed_chapters") or {}).items()
    }

    work_items = build_work_items()
    if args.max_chapters > 0:
        pending_items = [item for item in work_items if item["chapter_number"] not in completed_numbers][: args.max_chapters]
    else:
        pending_items = [item for item in work_items if item["chapter_number"] not in completed_numbers]

    summary = Counter(checkpoint.get("summary") or {})
    print(f"Pending chapters: {len(pending_items)} / {len(work_items)}")
    append_log(
        log_path,
        {
            "event": "run_started",
            "timestamp": now_iso(),
            "pending_count": len(pending_items),
            "work_item_count": len(work_items),
            "completed_checkpoint_count": len(completed_numbers),
        },
    )

    for index, item in enumerate(pending_items, start=1):
        chapter_number = int(item["chapter_number"])
        chapter_row = {
            "id": item["chapter_id"],
            "chapter_number": chapter_number,
            "title": item["title"],
            "content_url": item["content_url"],
        }
        needed_locales = list(item["needed_locales"])
        print(
            f"[{index}/{len(pending_items)}] Chapter {chapter_number} -> need {needed_locales}"
        )
        append_log(
            log_path,
            {
                "event": "chapter_started",
                "timestamp": now_iso(),
                "chapter_number": chapter_number,
                "needed_locales": needed_locales,
            },
        )

        try:
            result = await process_chapter(
                chapter_row=chapter_row,
                needed_locales=needed_locales,
                max_retries=args.max_retries,
                retry_sleep_seconds=args.retry_sleep_seconds,
            )
            if result["remaining_locales"]:
                failed_numbers[str(chapter_number)] = {
                    "remaining_locales": result["remaining_locales"],
                    "failures": result["failures"],
                    "updated_at": now_iso(),
                }
                summary["chapter_partial_or_failed"] += 1
                print(
                    f"  Remaining: {result['remaining_locales']} | failures: {len(result['failures'])}"
                )
                append_log(
                    log_path,
                    {
                        "event": "chapter_incomplete",
                        "timestamp": now_iso(),
                        **result,
                    },
                )
            else:
                failed_numbers.pop(str(chapter_number), None)
                summary["chapter_completed"] += 1
                summary["locale_completed"] += len(result["translated_locales"])
                print(f"  Completed all locales: {result['published_locales']}")
                append_log(
                    log_path,
                    {
                        "event": "chapter_completed",
                        "timestamp": now_iso(),
                        **result,
                    },
                )
                completed_numbers.add(chapter_number)
        except Exception as exc:
            failed_numbers[str(chapter_number)] = {
                "remaining_locales": needed_locales,
                "failures": [{"locale": ",".join(needed_locales), "detail": str(exc)}],
                "updated_at": now_iso(),
            }
            summary["chapter_exception"] += 1
            print(f"  Exception: {exc}")
            append_log(
                log_path,
                {
                    "event": "chapter_exception",
                    "timestamp": now_iso(),
                    "chapter_number": chapter_number,
                    "needed_locales": needed_locales,
                    "detail": str(exc),
                },
            )

        checkpoint_payload = {
            "updated_at": now_iso(),
            "completed_numbers": sorted(completed_numbers),
            "failed_chapters": failed_numbers,
            "summary": dict(summary),
            "pending_count_at_start": len(pending_items),
            "total_work_items_at_start": len(work_items),
        }
        save_checkpoint(checkpoint_path, checkpoint_payload)
        await asyncio.sleep(args.sleep_seconds)

    final_work_items = build_work_items()
    final_payload = {
        "updated_at": now_iso(),
        "completed_numbers": sorted(completed_numbers),
        "failed_chapters": failed_numbers,
        "summary": dict(summary),
        "remaining_work_items": len(final_work_items),
    }
    save_checkpoint(checkpoint_path, final_payload)
    append_log(
        log_path,
        {
            "event": "run_finished",
            "timestamp": now_iso(),
            "remaining_work_items": len(final_work_items),
            "summary": dict(summary),
        },
    )
    print(f"Run finished. Remaining work items: {len(final_work_items)}")
    return 0 if not final_work_items else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main_async()))
