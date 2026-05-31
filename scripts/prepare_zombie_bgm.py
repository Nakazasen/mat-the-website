import os
import sys
import urllib.request
import subprocess
import uuid
import json
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ENV_PATH = REPO_ROOT / "backend" / ".env"

from dotenv import load_dotenv
load_dotenv(BACKEND_ENV_PATH, override=True)

# Read credentials directly
R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "mat-the-chapters")
R2_PUBLIC_BASE_URL = os.getenv("R2_PUBLIC_BASE_URL", "https://pub-7b84345562bb41c6acf9cda324d194f8.r2.dev")

# Initialize boto3 S3 client
import boto3
r2_client = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
)

TRACKS = [
    {
        "title": "Dark Cello / Ambient Tension",
        "url": "https://pub-7b84345562bb41c6acf9cda324d194f8.r2.dev/bgm/20260331_5b1d8133_bgm_817_optimized_64k.mp3",
        "action": "copy"
    },
    {
        "title": "Gathering Darkness / Cello Horror",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Gathering%20Darkness.mp3",
        "action": "transcode"
    },
    {
        "title": "Unseen Horrors / Creepy Scraping",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Unseen%20Horrors.mp3",
        "action": "transcode"
    },
    {
        "title": "Anxiety / High String Tension",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Anxiety.mp3",
        "action": "transcode"
    },
    {
        "title": "Phantasm / Melancholic Suspense",
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Phantasm.mp3",
        "action": "transcode"
    }
]

def upload_audio_bytes(contents: bytes, safe_name: str) -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8]
    object_key = f"bgm/{date_str}_{unique_id}_{safe_name}.mp3"
    
    r2_client.put_object(
        Bucket=R2_BUCKET_NAME,
        Key=object_key,
        Body=contents,
        ContentType="audio/mpeg"
    )
    return f"{R2_PUBLIC_BASE_URL.rstrip('/')}/{object_key}"

def main_run():
    uploaded_tracks = []
    
    for track in TRACKS:
        title = track["title"]
        url = track["url"]
        action = track["action"]
        
        print(f"\nProcessing: {title}...")
        
        if action == "copy":
            uploaded_tracks.append({
                "title": title,
                "url": url
            })
            print(f"Copied existing optimized track: {url}")
            continue
            
        # Download
        temp_input = Path(f"temp_input_{uuid.uuid4().hex[:6]}.mp3")
        temp_output = Path(f"temp_output_{uuid.uuid4().hex[:6]}.mp3")
        
        try:
            print(f"Downloading from {url}...")
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req) as response:
                temp_input.write_bytes(response.read())
            
            print("Transcoding and trimming to 120s at 64k mono with ffmpeg...")
            # Trim to 120s, convert to 64k mono MP3 for ultra lightweight loop
            command = [
                "ffmpeg",
                "-y",
                "-ss", "0",
                "-i", str(temp_input),
                "-t", "120",
                "-vn",
                "-ac", "1",
                "-c:a", "libmp3lame",
                "-b:a", "64k",
                str(temp_output)
            ]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print("Uploading to R2...")
            safe_name = title.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
            r2_url = upload_audio_bytes(temp_output.read_bytes(), safe_name)
            
            uploaded_tracks.append({
                "title": title,
                "url": r2_url
            })
            print(f"Success! Uploaded URL: {r2_url}")
            
        except Exception as e:
            print(f"Error processing {title}: {e}")
        finally:
            # Clean up temps
            if temp_input.exists():
                try:
                    temp_input.unlink()
                except Exception:
                    pass
            if temp_output.exists():
                try:
                    temp_output.unlink()
                except Exception:
                    pass
                
    print("\n--- PROCESS COMPLETE ---")
    print(json.dumps(uploaded_tracks, indent=2))

if __name__ == "__main__":
    main_run()
