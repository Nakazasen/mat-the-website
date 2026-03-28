from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
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

from backend.main import (  # noqa: E402
    build_chapter_sentence_alignment,
    fetch_r2_content,
    normalize_locale,
    supabase as backend_supabase,
)


DEFAULT_LOCALES = ("en", "zh-CN", "ja")
DEFAULT_STATUS = "published"
DEFAULT_CHECKPOINT_FILE = Path(__file__).with_name("backfill_sentence_alignment_checkpoint.json")


@dataclass
class Counters:
    chapters_seen: int = 0
    chapters_processed: int = 0
    rows_seen: int = 0
    rows_updated: int = 0
    rows_skipped_existing: int = 0
    rows_skipped_empty: int = 0
    rows_failed: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Backfill sentence_alignment for existing chapter translations "
            "without calling AI."
        )
    )
    parser.add_argument("--start-chapter", type=int, default=1, help="Start chapter number (inclusive).")
    parser.add_argument("--end-chapter", type=int, default=10**9, help="End chapter number (inclusive).")
    parser.add_argument("--locales", type=str, default="en,zh-CN,ja", help="Comma-separated locales.")
    parser.add_argument("--status", type=str, default=DEFAULT_STATUS, help="Translation status filter.")
    parser.add_argument("--force", action="store_true", help="Rebuild even when sentence_alignment already exists.")
    parser.add_argument("--dry-run", action="store_true", help="Compute only, do not write to DB.")
    parser.add_argument("--sleep-ms", type=int, default=0, help="Sleep between row updates.")
    parser.add_argument("--limit-chapters", type=int, default=0, help="Process only N chapters (0 = no limit).")
    parser.add_argument(
        "--checkpoint-file",
        type=str,
        default=str(DEFAULT_CHECKPOINT_FILE),
        help="Checkpoint file path.",
    )
    parser.add_argument("--no-checkpoint", action="store_true", help="Ignore and do not write checkpoint.")
    parser.add_argument("--reset-checkpoint", action="store_true", help="Delete checkpoint before run.")
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


def load_checkpoint(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_path.replace(path)


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


def fetch_chapter_translations(
    supabase,
    chapter_id: int,
    locales: list[str],
    status: str,
) -> list[dict[str, Any]]:
    query = (
        supabase.table("chapter_translations")
        .select("id, locale, content, sentence_alignment, translation_status")
        .eq("chapter_id", chapter_id)
        .eq("translation_status", status)
    )
    if locales:
        query = query.in_("locale", locales)
    result = query.execute()
    return list(result.data or [])


def should_skip_row(row: dict[str, Any], force: bool) -> tuple[bool, str]:
    if not row.get("content"):
        return True, "empty_content"
    if not force and row.get("sentence_alignment"):
        return True, "has_alignment"
    return False, ""


def backfill(args: argparse.Namespace) -> int:
    locales = parse_locales(args.locales)
    checkpoint_path = Path(args.checkpoint_file)
    if args.reset_checkpoint and checkpoint_path.exists():
        checkpoint_path.unlink()

    checkpoint_enabled = (not args.no_checkpoint) and (not args.dry_run)
    checkpoint = load_checkpoint(checkpoint_path) if checkpoint_enabled else {}
    resume_after = int(checkpoint.get("last_chapter_number") or 0)
    if resume_after and resume_after >= args.start_chapter:
        start_chapter = resume_after + 1
    else:
        start_chapter = args.start_chapter

    supabase = get_supabase_client()
    chapters = fetch_chapters(supabase, start_chapter, args.end_chapter)
    counters = Counters()

    if not chapters:
        print("No chapters found for the selected range.")
        return 0

    print(
        f"Backfill start: chapters={len(chapters)}, locales={locales}, "
        f"status={args.status}, force={args.force}, dry_run={args.dry_run}"
    )
    if checkpoint_enabled and resume_after:
        print(f"Resume from checkpoint: chapter_number>{resume_after}")

    processed_chapters = 0
    for chapter in chapters:
        if args.limit_chapters > 0 and processed_chapters >= args.limit_chapters:
            break
        chapter_number = int(chapter["chapter_number"])
        chapter_id = int(chapter["id"])
        content_url = str(chapter.get("content_url") or "").strip()
        counters.chapters_seen += 1

        translations = fetch_chapter_translations(supabase, chapter_id, locales, args.status)
        if not translations:
            if checkpoint_enabled:
                save_checkpoint(
                    checkpoint_path,
                    {
                        "last_chapter_number": chapter_number,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "rows_updated": counters.rows_updated,
                        "rows_failed": counters.rows_failed,
                    },
                )
            continue

        source_content: Optional[str] = None
        chapter_had_work = False
        for row in translations:
            counters.rows_seen += 1
            skip, reason = should_skip_row(row, force=args.force)
            if skip:
                if reason == "has_alignment":
                    counters.rows_skipped_existing += 1
                else:
                    counters.rows_skipped_empty += 1
                continue

            if not content_url:
                counters.rows_failed += 1
                print(f"[fail] chapter {chapter_number} locale={row.get('locale')} missing content_url")
                continue

            if source_content is None:
                try:
                    source_content = fetch_r2_content(content_url)
                except Exception as exc:
                    counters.rows_failed += 1
                    print(f"[fail] chapter {chapter_number} fetch source failed: {exc}")
                    break

            try:
                alignment = build_chapter_sentence_alignment(
                    source_text=source_content or "",
                    translated_text=str(row.get("content") or ""),
                )
                if not args.dry_run:
                    (
                        supabase.table("chapter_translations")
                        .update({"sentence_alignment": alignment})
                        .eq("id", row["id"])
                        .execute()
                    )
                counters.rows_updated += 1
                chapter_had_work = True
            except Exception as exc:
                counters.rows_failed += 1
                print(
                    f"[fail] chapter {chapter_number} locale={row.get('locale')} "
                    f"alignment build/update failed: {exc}"
                )

            if args.sleep_ms > 0:
                time.sleep(args.sleep_ms / 1000.0)

        if chapter_had_work:
            counters.chapters_processed += 1
        processed_chapters += 1

        if checkpoint_enabled:
            save_checkpoint(
                checkpoint_path,
                {
                    "last_chapter_number": chapter_number,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "rows_updated": counters.rows_updated,
                    "rows_failed": counters.rows_failed,
                },
            )

        print(
            f"[chapter {chapter_number}] seen_rows={counters.rows_seen} "
            f"updated={counters.rows_updated} skipped_existing={counters.rows_skipped_existing} "
            f"skipped_empty={counters.rows_skipped_empty} failed={counters.rows_failed}"
        )

    print("Backfill done.")
    print(
        f"chapters_seen={counters.chapters_seen}, chapters_processed={counters.chapters_processed}, "
        f"rows_seen={counters.rows_seen}, rows_updated={counters.rows_updated}, "
        f"rows_skipped_existing={counters.rows_skipped_existing}, "
        f"rows_skipped_empty={counters.rows_skipped_empty}, rows_failed={counters.rows_failed}"
    )
    return 0 if counters.rows_failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(backfill(parse_args()))
