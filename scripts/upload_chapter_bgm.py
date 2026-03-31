import argparse
import mimetypes
import os
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ENV_PATH = REPO_ROOT / "backend" / ".env"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

load_dotenv(BACKEND_ENV_PATH, override=True)

import backend.main as main


VALID_CONTENT_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/ogg",
    "audio/webm",
    "audio/mp4",
    "audio/x-m4a",
    "audio/aac",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload a local BGM file to R2 and attach it to a chapter.")
    parser.add_argument("--file", required=True, help="Absolute path to the local audio file.")
    parser.add_argument("--chapter", type=int, required=True, help="Chapter number to attach the BGM to.")
    parser.add_argument("--title", default="", help="Optional BGM title to store in the chapter row.")
    parser.add_argument("--start-seconds", type=int, default=0, help="Optional trim start offset in seconds.")
    parser.add_argument("--trim-seconds", type=int, default=0, help="Optional trim duration in seconds.")
    parser.add_argument("--bitrate-kbps", type=int, default=0, help="Optional MP3 re-encode bitrate in kbps, e.g. 64.")
    return parser.parse_args()


def detect_content_type(path: Path) -> str:
    guessed_type, _ = mimetypes.guess_type(path.name)
    normalized = (guessed_type or "audio/mpeg").lower()
    if normalized not in VALID_CONTENT_TYPES:
        extension = path.suffix.lower()
        if extension == ".mp3":
            return "audio/mpeg"
        if extension == ".wav":
            return "audio/wav"
        if extension == ".ogg":
            return "audio/ogg"
        if extension == ".webm":
            return "audio/webm"
        if extension == ".m4a":
            return "audio/x-m4a"
        if extension == ".aac":
            return "audio/aac"
        raise SystemExit(f"Unsupported audio type for file: {path.name}")
    return normalized


def maybe_prepare_audio(path: Path, start_seconds: int, trim_seconds: int, bitrate_kbps: int) -> tuple[Path, bool]:
    should_transcode = bitrate_kbps > 0
    if start_seconds <= 0 and trim_seconds <= 0 and not should_transcode:
        return path, False

    suffix = ".mp3" if should_transcode else (path.suffix or ".mp3")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.close()
    output_path = Path(temp_file.name)

    command = [
        "ffmpeg",
        "-y",
        "-ss",
        str(max(0, start_seconds)),
        "-i",
        str(path),
    ]
    if trim_seconds > 0:
        command.extend(["-t", str(trim_seconds)])
    if should_transcode:
        command.extend(["-vn", "-c:a", "libmp3lame", "-b:a", f"{bitrate_kbps}k"])
    else:
        command.extend(["-c", "copy"])
    command.append(str(output_path))
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path, True


def upload_audio_file(path: Path) -> str:
    if not main.r2_client:
        raise SystemExit("Cloudflare R2 is not configured in backend/.env")
    if not main.R2_PUBLIC_URL:
        raise SystemExit("R2_PUBLIC_URL is missing in backend/.env")

    content_type = detect_content_type(path)
    contents = path.read_bytes()
    if len(contents) > 25 * 1024 * 1024:
        raise SystemExit("Audio file exceeds 25MB limit.")

    date_str = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8]
    safe_name = main.slugify(path.stem) or f"bgm-{unique_id}"
    ext = path.suffix.lower().lstrip(".") or "mp3"
    object_key = f"bgm/{date_str}_{unique_id}_{safe_name}.{ext}"

    main.r2_client.put_object(
        Bucket=main.R2_BUCKET,
        Key=object_key,
        Body=contents,
        ContentType=content_type,
    )
    return f"{main.R2_PUBLIC_URL.rstrip('/')}/{object_key}"


def attach_bgm_to_chapter(chapter_number: int, bgm_url: str, bgm_title: str, file_stem: str) -> dict:
    chapter_resp = (
        main.supabase.table("chapters")
        .select("id, chapter_number, title, bgm_url, bgm_title")
        .eq("chapter_number", chapter_number)
        .single()
        .execute()
    )
    chapter_row = chapter_resp.data
    if not chapter_row:
        raise SystemExit(f"Chapter {chapter_number} not found.")

    if not main.chapters_support_bgm():
        raise SystemExit("Chapters table does not support bgm_url/bgm_title yet. Run scripts/supabase_chapter_bgm.sql first.")

    title_to_save = bgm_title.strip() or chapter_row.get("bgm_title") or file_stem.replace("_", " ").replace("-", " ").strip()
    updated = (
        main.supabase.table("chapters")
        .update({
            "bgm_url": bgm_url,
            "bgm_title": title_to_save,
        })
        .eq("chapter_number", chapter_number)
        .execute()
    )
    return updated.data[0]


if __name__ == "__main__":
    args = parse_args()
    path = Path(args.file).expanduser()
    if not path.exists():
        raise SystemExit(f"Audio file not found: {path}")

    source_path, should_cleanup = maybe_prepare_audio(path, args.start_seconds, args.trim_seconds, args.bitrate_kbps)
    try:
        uploaded_url = upload_audio_file(source_path)
        updated_row = attach_bgm_to_chapter(args.chapter, uploaded_url, args.title, path.stem)
        print(f"Uploaded: {uploaded_url}")
        print(f"Chapter: {updated_row['chapter_number']}")
        print(f"BGM title: {updated_row.get('bgm_title')}")
    finally:
        if should_cleanup:
            try:
                source_path.unlink(missing_ok=True)
            except Exception:
                pass
