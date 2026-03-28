#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".env",
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".css",
    ".scss",
    ".html",
    ".sql",
    ".sh",
    ".ps1",
}

IGNORED_PATHS = {
    Path(".brain/rules.md"),
    Path("frontend/hex_dicts.txt"),
    Path("scripts/check_mojibake.py"),
    Path("scripts/scan_and_fix_mojibake.py"),
    Path("status.txt"),
}

IGNORE_TOKEN = "mojibake-scan: ignore-line"
HALFWIDTH_KATAKANA_RE = re.compile("[\uff61-\uff9f]{3,}")

SUSPICIOUS_FRAGMENTS = (
    "\ufffd",
    "\u862f",  # 蘯
    "\u76fb",  # 盻
    "\u7b0f",  # 笏
    "\u9036",  # 逶
    "\u7e5d",  # 繝
    "\u9642",  # 陂
    "\u5193",  # 冓
    "\u5b16",  # 嬖
    "\u8700",  # 蜀
    "\u8b2b",  # 謫
    "\u9082",  # 邂
    "\u8373",  # 荳
    "\u8b4c",  # 譌
    "\u8b5b",  # 譛
    "\u96b1",  # 隱
)


def run_git(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def staged_files() -> list[Path]:
    return [Path(path) for path in run_git("diff", "--cached", "--name-only", "--diff-filter=ACMR")]


def tracked_files() -> list[Path]:
    return [Path(path) for path in run_git("ls-files")]


def normalize_repo_path(path: Path) -> Path:
    return Path(path.as_posix())


def is_text_candidate(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    if normalize_repo_path(path) in IGNORED_PATHS:
        return False
    if path.name in {".DS_Store"}:
        return False
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    if path.name.startswith(".env"):
        return True
    return False


def find_suspicious_lines(path: Path) -> list[tuple[int, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [(0, "File is not valid UTF-8.")]

    hits: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if IGNORE_TOKEN in line:
            continue
        if any(fragment in line for fragment in SUSPICIOUS_FRAGMENTS) or HALFWIDTH_KATAKANA_RE.search(line):
            hits.append((line_number, line.strip()))
    return hits


def safe_console_text(value: str) -> str:
    encoding = sys.stdout.encoding or "utf-8"
    return value.encode(encoding, errors="backslashreplace").decode(encoding, errors="strict")


def collect_paths(args: argparse.Namespace) -> list[Path]:
    if args.staged:
        return staged_files()
    if args.paths:
        return [Path(path) for path in args.paths]
    return tracked_files()


def main() -> int:
    parser = argparse.ArgumentParser(description="Quick mojibake scan for staged or tracked text files.")
    parser.add_argument("--staged", action="store_true", help="Scan staged files only.")
    parser.add_argument("paths", nargs="*", help="Optional file paths to scan.")
    args = parser.parse_args()

    paths = [path for path in collect_paths(args) if is_text_candidate(path)]
    if not paths:
        print("No candidate text files to scan.")
        return 0

    findings: list[tuple[Path, list[tuple[int, str]]]] = []
    for path in paths:
        hits = find_suspicious_lines(path)
        if hits:
            findings.append((path, hits))

    if not findings:
        print("No suspicious mojibake markers found.")
        return 0

    print("Suspicious mojibake markers detected:\n")
    for path, hits in findings:
        print(f"- {path}")
        for line_number, line in hits[:10]:
            prefix = f"  L{line_number}" if line_number > 0 else "  !"
            print(f"{prefix}: {safe_console_text(line[:200])}")
        if len(hits) > 10:
            print(f"  ... {len(hits) - 10} more suspicious lines")
        print()

    print("Commit blocked. Review and fix the files above before committing.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
