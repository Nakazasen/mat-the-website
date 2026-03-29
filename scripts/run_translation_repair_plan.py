from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import backend.main as main  # noqa: E402


DEFAULT_RETRANSLATE_LIST = REPO_ROOT / "reports" / "chapters_retranslate_first.txt"
DEFAULT_REFINE_LIST = REPO_ROOT / "reports" / "chapters_refine_first.txt"
DEFAULT_CHECKPOINT = REPO_ROOT / "reports" / "translation_repair_checkpoint.json"
DEFAULT_LOG = REPO_ROOT / "reports" / "translation_repair_run.log"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export compact repair lists and execute retranslate/refine operations from a grouped chapter report."
    )
    parser.add_argument("--input", type=str, required=True, help="Grouped report JSON path.")
    parser.add_argument("--retranslate-list", type=str, default=str(DEFAULT_RETRANSLATE_LIST), help="Output txt path for retranslate list.")
    parser.add_argument("--refine-list", type=str, default=str(DEFAULT_REFINE_LIST), help="Output txt path for refine list.")
    parser.add_argument("--checkpoint", type=str, default=str(DEFAULT_CHECKPOINT), help="Checkpoint JSON path.")
    parser.add_argument("--log", type=str, default=str(DEFAULT_LOG), help="Execution log path.")
    parser.add_argument("--mode", choices=("all", "retranslate", "refine"), default="all", help="Which repair actions to run.")
    parser.add_argument("--limit-chapters", type=int, default=0, help="Run only first N grouped chapters that need work.")
    parser.add_argument("--sleep-seconds", type=float, default=2.0, help="Delay between chapter operations.")
    parser.add_argument("--retry-count", type=int, default=3, help="Retries per chapter step.")
    parser.add_argument("--reset-checkpoint", action="store_true", help="Delete checkpoint before run.")
    return parser.parse_args()


def load_grouped_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_compact_list(path: Path, rows: list[dict[str, Any]], field_name: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"{row['chapter_number']}: {','.join(row[field_name])}"
        for row in rows
        if row.get(field_name)
    ]
    path.write_text("\n".join(lines).strip() + ("\n" if lines else ""), encoding="utf-8")


def load_checkpoint(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"chapters": {}, "updated_at": None}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"chapters": {}, "updated_at": None}


def save_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_path.replace(path)


def append_log(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def normalize_grouped_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    return list(report.get("chapters") or [])


def truncate_detail(detail: Any, max_length: int = 600) -> str:
    text = str(detail or "").strip()
    if len(text) <= max_length:
        return text
    return f"{text[:max_length].rstrip()}..."


async def run_with_retries(coro_factory, retry_count: int, sleep_seconds: float):
    last_error: Exception | None = None
    for attempt in range(1, retry_count + 1):
        try:
            return await coro_factory()
        except Exception as exc:
            last_error = exc
            if attempt >= retry_count:
                break
            await asyncio.sleep(max(5.0, sleep_seconds * attempt))
    if last_error is not None:
        raise last_error
    raise RuntimeError("Unknown retry failure")


async def execute_retranslate(chapter_row: dict[str, Any], content_text: str, locales: list[str], retry_count: int, sleep_seconds: float) -> dict[str, Any]:
    async def do_work():
        return await main.upsert_chapter_translations(
            chapter_row=chapter_row,
            title=chapter_row["title"],
            content=content_text,
            locales=locales,
            translation_mode="quality",
        )

    return await run_with_retries(do_work, retry_count=retry_count, sleep_seconds=sleep_seconds)


async def execute_refine(chapter_row: dict[str, Any], content_text: str, locales: list[str], retry_count: int, sleep_seconds: float) -> dict[str, Any]:
    async def do_work():
        return await main.improve_chapter_translations(
            chapter_row=chapter_row,
            title=chapter_row["title"],
            content=content_text,
            locales=locales,
        )

    return await run_with_retries(do_work, retry_count=retry_count, sleep_seconds=sleep_seconds)


def build_pending_locales(checkpoint_entry: dict[str, Any], step_name: str, planned_locales: list[str]) -> list[str]:
    if not planned_locales:
        return []
    completed_locales = set((checkpoint_entry.get(step_name) or {}).get("completed_locales") or [])
    return [locale for locale in planned_locales if locale not in completed_locales]


async def run_plan(args: argparse.Namespace) -> dict[str, Any]:
    report_path = Path(args.input)
    grouped_report = load_grouped_report(report_path)
    grouped_rows = normalize_grouped_rows(grouped_report)
    if args.limit_chapters > 0:
        grouped_rows = grouped_rows[: args.limit_chapters]

    retranslate_list_path = Path(args.retranslate_list)
    refine_list_path = Path(args.refine_list)
    write_compact_list(retranslate_list_path, grouped_rows, "retranslate_locales")
    write_compact_list(refine_list_path, grouped_rows, "refine_locales")

    checkpoint_path = Path(args.checkpoint)
    log_path = Path(args.log)
    if args.reset_checkpoint and checkpoint_path.exists():
        checkpoint_path.unlink()

    checkpoint = load_checkpoint(checkpoint_path)
    summary = {
        "source_report": str(report_path),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "processed_chapters": 0,
        "retranslate_completed": 0,
        "retranslate_failed": 0,
        "refine_completed": 0,
        "refine_failed": 0,
        "skipped_chapters": 0,
    }

    for grouped_row in grouped_rows:
        chapter_number = int(grouped_row["chapter_number"])
        chapter_key = str(chapter_number)
        checkpoint_entry = checkpoint.setdefault("chapters", {}).setdefault(chapter_key, {})
        retranslate_locales = list(grouped_row.get("retranslate_locales") or [])
        refine_locales = list(grouped_row.get("refine_locales") or [])

        if args.mode == "retranslate":
            refine_locales = []
        elif args.mode == "refine":
            retranslate_locales = []

        pending_retranslate = build_pending_locales(checkpoint_entry, "retranslate", retranslate_locales)
        pending_refine = build_pending_locales(checkpoint_entry, "refine", refine_locales)

        if not pending_retranslate and not pending_refine:
            summary["skipped_chapters"] += 1
            continue

        summary["processed_chapters"] += 1
        log_context = {"chapter_number": chapter_number}
        print(f"\n=== Chapter {chapter_number} ===")
        print(f"Retranslate: {pending_retranslate or '-'} | Refine: {pending_refine or '-'}")

        chapter_resp = main.supabase.table("chapters").select("*").eq("chapter_number", chapter_number).single().execute()
        chapter_row = chapter_resp.data
        if not chapter_row:
            detail = f"Chapter {chapter_number} not found"
            append_log(log_path, {"event": "chapter_missing", "detail": detail, **log_context})
            checkpoint_entry["last_error"] = detail
            checkpoint["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_checkpoint(checkpoint_path, checkpoint)
            continue

        try:
            content_text = main.fetch_r2_content(chapter_row["content_url"])
        except Exception as exc:
            detail = truncate_detail(exc)
            append_log(log_path, {"event": "source_fetch_failed", "detail": detail, **log_context})
            checkpoint_entry["last_error"] = detail
            checkpoint["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_checkpoint(checkpoint_path, checkpoint)
            await asyncio.sleep(args.sleep_seconds)
            continue

        if pending_retranslate:
            try:
                result = await execute_retranslate(
                    chapter_row=chapter_row,
                    content_text=content_text,
                    locales=pending_retranslate,
                    retry_count=args.retry_count,
                    sleep_seconds=args.sleep_seconds,
                )
                completed_locales = sorted(set(result.get("translated_locales") or []))
                failed_locales = sorted(
                    {
                        str(item.get("locale") or "")
                        for item in (result.get("failed_translations") or [])
                        if item.get("locale")
                    }
                )
                checkpoint_entry["retranslate"] = {
                    "completed_locales": sorted(
                        set((checkpoint_entry.get("retranslate") or {}).get("completed_locales") or []).union(completed_locales)
                    ),
                    "failed_locales": failed_locales,
                    "last_result": result,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                if failed_locales:
                    summary["retranslate_failed"] += 1
                else:
                    summary["retranslate_completed"] += 1
                append_log(
                    log_path,
                    {
                        "event": "retranslate_done",
                        "chapter_number": chapter_number,
                        "completed_locales": completed_locales,
                        "failed_translations": result.get("failed_translations") or [],
                    },
                )
            except Exception as exc:
                detail = truncate_detail(traceback.format_exc() or exc)
                checkpoint_entry["retranslate"] = {
                    "completed_locales": list((checkpoint_entry.get("retranslate") or {}).get("completed_locales") or []),
                    "failed_locales": pending_retranslate,
                    "last_error": detail,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                summary["retranslate_failed"] += 1
                append_log(log_path, {"event": "retranslate_exception", "detail": detail, **log_context})

            checkpoint["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_checkpoint(checkpoint_path, checkpoint)
            await asyncio.sleep(args.sleep_seconds)

        if pending_refine:
            try:
                result = await execute_refine(
                    chapter_row=chapter_row,
                    content_text=content_text,
                    locales=pending_refine,
                    retry_count=args.retry_count,
                    sleep_seconds=args.sleep_seconds,
                )
                completed_locales = sorted(set(result.get("translated_locales") or []))
                failed_locales = sorted(
                    {
                        str(item.get("locale") or "")
                        for item in (result.get("failed_translations") or [])
                        if item.get("locale")
                    }
                )
                checkpoint_entry["refine"] = {
                    "completed_locales": sorted(
                        set((checkpoint_entry.get("refine") or {}).get("completed_locales") or []).union(completed_locales)
                    ),
                    "failed_locales": failed_locales,
                    "last_result": result,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                if failed_locales:
                    summary["refine_failed"] += 1
                else:
                    summary["refine_completed"] += 1
                append_log(
                    log_path,
                    {
                        "event": "refine_done",
                        "chapter_number": chapter_number,
                        "completed_locales": completed_locales,
                        "failed_translations": result.get("failed_translations") or [],
                    },
                )
            except Exception as exc:
                detail = truncate_detail(traceback.format_exc() or exc)
                checkpoint_entry["refine"] = {
                    "completed_locales": list((checkpoint_entry.get("refine") or {}).get("completed_locales") or []),
                    "failed_locales": pending_refine,
                    "last_error": detail,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                summary["refine_failed"] += 1
                append_log(log_path, {"event": "refine_exception", "detail": detail, **log_context})

            checkpoint["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_checkpoint(checkpoint_path, checkpoint)
            await asyncio.sleep(args.sleep_seconds)

    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    checkpoint["updated_at"] = summary["finished_at"]
    save_checkpoint(checkpoint_path, checkpoint)
    return summary


def main_entry() -> int:
    load_dotenv(REPO_ROOT / ".env", override=False)
    load_dotenv(BACKEND_DIR / ".env", override=True)
    load_dotenv(override=True)
    args = parse_args()
    started_at = time.time()
    summary = asyncio.run(run_plan(args))
    elapsed = round(time.time() - started_at, 1)
    print("")
    print("Run summary:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Elapsed seconds: {elapsed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main_entry())
