"""
FastAPI Backend - Mạt Thế Sinh Hoá Nguy Cơ
Cung cấp API metadata chương. Nội dung chương được fetch từ Cloudflare R2.
"""

import io
import os
from typing import Optional
from urllib.parse import quote
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# === SUPABASE CLIENT ===
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL và SUPABASE_KEY phải được cấu hình trong file .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === FASTAPI APP ===
app = FastAPI(
    title="Mạt Thế API",
    description="API backend cho website đọc truyện Mạt Thế - Sinh Hoá Nguy Cơ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,  # disable redoc để giảm memory trên Render free tier
)

# === CORS MIDDLEWARE ===
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [o.strip() for o in allowed_origins_raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# === DATA MODELS ===
class Chapter(BaseModel):
    id: int
    chapter_number: int
    title: str
    content_url: str  # Cloudflare R2 public URL
    created_at: str
    word_count: Optional[int] = None

class ChaptersResponse(BaseModel):
    chapters: list[Chapter]
    total: int
    page: int
    limit: int
    total_pages: int
    max_chapter: int

# ============================================================
# ROUTES
# ============================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint cho Render monitoring"""
    return {"status": "ok", "service": "mat-the-api"}


@app.get("/api/chapters", response_model=ChaptersResponse)
async def get_chapters(
    page: int = Query(1, ge=1, description="Số trang"),
    limit: int = Query(50, ge=1, le=100, description="Số chương mỗi trang"),
    sort: str = Query("asc", pattern="^(asc|desc)$", description="Thứ tự sắp xếp: asc hoặc desc"),
):
    """
    Lấy danh sách chương có phân trang.
    
    - **page**: Trang hiện tại (bắt đầu từ 1)
    - **limit**: Số chương mỗi trang (tối đa 100)
    - **sort**: Sắp xếp theo thứ tự chương (asc/desc)
    """
    try:
        offset = (page - 1) * limit

        # Count total
        count_resp = supabase.table("chapters").select("id", count="exact").execute()
        total = count_resp.count or 0
        total_pages = (total + limit - 1) // limit if total > 0 else 1

        # Fetch page
        ascending = sort == "asc"
        resp = (
            supabase.table("chapters")
            .select("id, chapter_number, title, content_url, created_at, word_count")
            .order("chapter_number", desc=not ascending)
            .range(offset, offset + limit - 1)
            .execute()
        )

        # Fetch max chapter number for realistic pagination bounding
        max_chapter_resp = (
            supabase.table("chapters")
            .select("chapter_number")
            .order("chapter_number", desc=True)
            .limit(1)
            .execute()
        )
        max_chapter = max_chapter_resp.data[0]["chapter_number"] if max_chapter_resp.data else total

        chapters = [Chapter(**row) for row in resp.data]

        return ChaptersResponse(
            chapters=chapters,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            max_chapter=max_chapter,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/chapters/{chapter_number}", response_model=Chapter)
async def get_chapter(chapter_number: int):
    """
    Lấy thông tin metadata của một chương bao gồm URL file R2 chứa nội dung.
    Frontend sẽ dùng content_url này để fetch nội dung thẳng từ Cloudflare CDN.
    
    - **chapter_number**: Số chương thực tế trong truyện
    """
    try:
        resp = (
            supabase.table("chapters")
            .select("id, chapter_number, title, content_url, created_at, word_count")
            .eq("chapter_number", chapter_number)
            .single()
            .execute()
        )

        if not resp.data:
            raise HTTPException(status_code=404, detail=f"Chương {chapter_number} không tìm thấy")

        return Chapter(**resp.data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# === TTS PROXY ===
@app.get("/api/tts", summary="Google Translate TTS Proxy")
async def tts_proxy(
    text: str = Query(..., max_length=200, description="Văn bản cần đọc (tối đa 200 ký tự)"),
    lang: str = Query("vi", description="Ngôn ngữ (vi, en, ...)"),
    speed: float = Query(1.0, ge=0.5, le=2.0, description="Tốc độ đọc"),
):
    """
    Proxy Google Translate TTS để tránh bị chặn khi gọi trực tiếp từ browser.
    Trả về audio MP3 stream.
    """
    url = (
        f"https://translate.google.com/translate_tts"
        f"?ie=UTF-8&client=tw-ob&tl={lang}&ttsspeed={speed}"
        f"&q={quote(text)}"
    )
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://translate.google.com/",
        "Accept": "audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,*/*;q=0.5",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers, follow_redirects=True)

        if resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Google TTS trả về {resp.status_code}"
            )

        return StreamingResponse(
            io.BytesIO(resp.content),
            media_type="audio/mpeg",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*",
            },
        )

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Google TTS timeout")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
