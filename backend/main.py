"""
FastAPI Backend - Mạt Thế Sinh Hoá Nguy Cơ
Cung cấp API metadata chương. Nội dung chương được fetch từ Cloudflare R2.
"""

import io
import os
import re
import unicodedata
# Force re-deploy to Vercel (Trigger)
from typing import Optional
from urllib.parse import quote
import boto3
from botocore.client import Config
import httpx
from fastapi import FastAPI, HTTPException, Query, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, PlainTextResponse
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

# === CLOUDFLARE R2 CLIENT ===
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
# Support both R2_ENDPOINT_URL (old) and R2_ENDPOINT (new on Render)
R2_ENDPOINT = os.getenv("R2_ENDPOINT_URL") or os.getenv("R2_ENDPOINT")
R2_BUCKET = os.getenv("R2_BUCKET_NAME", "mat-the")
# Support both R2_PUBLIC_URL and R2_PUBLIC_BASE_URL
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL") or os.getenv("R2_PUBLIC_BASE_URL") or ""

r2_client = None
if R2_ACCESS_KEY and R2_SECRET_KEY and R2_ENDPOINT:
    r2_client = boto3.client(
        's3',
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='auto',
    )


def slugify(text: str) -> str:
    """Convert Vietnamese text to ASCII slug for use as R2 object key."""
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')


async def verify_admin(authorization: Optional[str]) -> dict:
    """Verify the Supabase Bearer JWT token from the request header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Thiếu token xác thực")
    token = authorization.replace("Bearer ", "")
    try:
        response = supabase.auth.get_user(token)
        if not response.user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ")
        return {"user": response.user}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token hết hạn hoặc không hợp lệ")

# === FASTAPI APP ===
app = FastAPI(
    title="Mạt Thế API",
    description="API backend cho website đọc truyện Mạt Thế - Sinh Hoá Nguy Cơ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,  # disable redoc để giảm memory trên Render free tier
)

# === CUSTOM LOGGING & CORS MIDDLEWARE (TRULY NUCLEAR OPTION) ===
@app.middleware("http")
async def add_cors_and_logging(request, call_next):
    # Log incoming request
    print(f"DEBUG: Request {request.method} {request.url}")
    
    # Handle preflight (OPTIONS) requests manually
    if request.method == "OPTIONS":
        from fastapi.responses import Response
        response = Response(content=None, status_code=204)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response

    # Process request
    try:
        response = await call_next(request)
    except Exception as e:
        import traceback
        error_msg = f"CRASH in {request.method} {request.url}: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(traceback.format_exc())
        
        # Create a JSON error response manually to ensure headers are added
        from fastapi.responses import JSONResponse
        response = JSONResponse(
            status_code=500,
            content={"detail": f"Server Error: {str(e)}", "error": str(e)}
        )

    # Add CORS headers to ALL responses (even errors)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response

# === DATA MODELS ===
class Chapter(BaseModel):
    id: int
    chapter_number: int
    title: str
    content_url: str  # Cloudflare R2 public URL
    created_at: str
    word_count: Optional[int] = None
    view_count: int = 0

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
    search: Optional[str] = Query(None, description="Tìm kiếm theo tiêu đề hoặc số chương"),
):
    """
    Lấy danh sách chương có phân trang.
    
    - **page**: Trang hiện tại (bắt đầu từ 1)
    - **limit**: Số chương mỗi trang (tối đa 100)
    - **sort**: Sắp xếp theo thứ tự chương (asc/desc)
    """
    try:
        offset = (page - 1) * limit

        # Build base query
        query = supabase.table("chapters").select("id, chapter_number, title, content_url, created_at, word_count", count="exact")
        
        # Apply search if provided
        if search:
            if search.isdigit():
                query = query.eq("chapter_number", int(search))
            else:
                query = query.ilike("title", f"%{search}%")

        # Fetch page
        ascending = sort == "asc"
        resp = (
            query.order("chapter_number", desc=not ascending)
            .range(offset, offset + limit - 1)
            .execute()
        )

        total = resp.count or 0

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


# ============================================================
# ADMIN ROUTES (JWT Protected)
# ============================================================

class AdminChapterCreate(BaseModel):
    chapter_number: int
    title: str
    content: str  # Raw text content of the chapter


class AdminChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


@app.post("/api/admin/chapters", summary="[Admin] Thêm chương mới")
async def admin_create_chapter(
    body: AdminChapterCreate,
    authorization: Optional[str] = Header(None),
):
    """Thêm chương mới: Upload nội dung lên R2, lưu metadata vào Supabase."""
    await verify_admin(authorization)

    if not r2_client:
        raise HTTPException(status_code=500, detail="R2 chưa được cấu hình trên server")

    # Check chapter number uniqueness
    existing = supabase.table("chapters").select("id").eq("chapter_number", body.chapter_number).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail=f"Chương {body.chapter_number} đã tồn tại")

    # Upload content to R2
    slug = slugify(f"chuong-{body.chapter_number}-{body.title}")
    object_key = f"chapters/{body.chapter_number:04d}-{slug}.txt"
    content_bytes = body.content.encode("utf-8")

    r2_client.put_object(
        Bucket=R2_BUCKET,
        Key=object_key,
        Body=content_bytes,
        ContentType="text/plain; charset=utf-8",
    )

    content_url = f"{R2_PUBLIC_URL}/{object_key}"
    word_count = len(body.content.split())

    # Insert metadata into Supabase
    result = supabase.table("chapters").insert({
        "chapter_number": body.chapter_number,
        "title": body.title,
        "content_url": content_url,
        "word_count": word_count,
    }).execute()

    return {"message": "Thêm chương thành công", "chapter": result.data[0]}


@app.put("/api/admin/chapters/{chapter_number}", summary="[Admin] Sửa chương")
async def admin_update_chapter(
    chapter_number: int,
    body: AdminChapterUpdate,
    authorization: Optional[str] = Header(None),
):
    """Sửa tiêu đề và/hoặc nội dung chương."""
    await verify_admin(authorization)

    # Fetch existing chapter
    existing = supabase.table("chapters").select("*").eq("chapter_number", chapter_number).single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail=f"Chương {chapter_number} không tìm thấy")

    chapter = existing.data
    update_data = {}

    # Update content on R2 if provided
    if body.content is not None:
        if not r2_client:
            raise HTTPException(status_code=500, detail="R2 chưa được cấu hình trên server")

        # Derive key from content_url
        content_url = chapter["content_url"]
        object_key = content_url.replace(f"{R2_PUBLIC_URL}/", "")

        r2_client.put_object(
            Bucket=R2_BUCKET,
            Key=object_key,
            Body=body.content.encode("utf-8"),
            ContentType="text/plain; charset=utf-8",
        )
        update_data["word_count"] = len(body.content.split())

    if body.title is not None:
        update_data["title"] = body.title

    if update_data:
        result = supabase.table("chapters").update(update_data).eq("chapter_number", chapter_number).execute()
        return {"message": "Cập nhật thành công", "chapter": result.data[0]}

    return {"message": "Không có gì thay đổi"}


class NovelSettings(BaseModel):
    title: str
    author: str
    description: str
    cover_url: str
    status: str
    genres: list[str]


@app.get("/api/novel", response_model=NovelSettings)
async def get_novel_settings():
    """Lấy thông tin chung của truyện (Tên, tác giả, mô tả...)"""
    try:
        resp = supabase.table("novel_settings").select("*").eq("id", 1).single().execute()
        
        if not resp.data:
            return NovelSettings(
                title="Mạt Thế - Sinh Hoá Nguy Cơ",
                author="Hàn Nhược Tuyết",
                description="Truyện lấy bối cảnh tận thế đột nhiên phủ xuống, thây ma lan tràn, quái vật dị biến nổi lên khắp nơi, loài người bị đẩy vào một trò chơi tàn khốc kinh hoàng nhưng cũng ẩn chứa cơ hội lớn lao...\n\nNhân vật chính là một nhân viên văn phòng hết sức bình thường, bước từng bước tiến lên để tìm ra nguyên nhân của đại tai biến.\nTạo dựng thế lực, ngăn cản biển thây ma, tấn công ổ quái vật, phục hồi trật tự, chiến tranh với các thế lực khác...",
                cover_url="/hero-bg.png",
                status="Đang cập nhật",
                genres=["Mạt Thế", "Zombie", "Hành Động", "Huyền Hạo", "Hành Động"]
            )
        
        # Filter out fields not in the model to avoid Pydantic errors
        model_fields = NovelSettings.__fields__.keys()
        clean_data = {k: v for k, v in resp.data.items() if k in model_fields}
        return NovelSettings(**clean_data)
    except Exception as e:
        print(f"DEBUG: get_novel_settings error: {str(e)}")
        # Fallback dữ liệu mặc định nếu lỗi DB (tránh sập trang chủ)
        return NovelSettings(
            title="Mạt Thế - Sinh Hoá Nguy Cơ",
            author="Hàn Nhược Tuyết",
            description="Truyện lấy bối cảnh tận thế đột nhiên phủ xuống, thây ma lan tràn, quái vật dị biến nổi lên khắp nơi, loài người bị đẩy vào một trò chơi tàn khốc kinh hoàng nhưng cũng ẩn chứa cơ hội lớn lao...\n\nNhân vật chính là một nhân viên văn phòng hết sức bình thường, bước từng bước tiến lên để tìm ra nguyên nhân của đại tai biến.\nTạo dựng thế lực, ngăn cản biển thây ma, tấn công ổ quái vật, phục hồi trật tự, chiến tranh với các thế lực khác...",
            cover_url="/hero-bg.png",
            status="Đang cập nhật",
            genres=["Mạt Thế", "Zombie", "Hành Động", "Huyền Hạo", "Hành Động"]
        )


@app.put("/api/admin/novel", summary="[Admin] Cập nhật thông tin truyện")
async def admin_update_novel(
    body: NovelSettings,
    authorization: Optional[str] = Header(None),
):
    """Cập nhật thông tin chung của truyện."""
    await verify_admin(authorization)
    
    # Upsert vào dòng ID=1
    data = body.dict()
    data["id"] = 1
    
    result = supabase.table("novel_settings").upsert(data).execute()
    
    # Defensive check: if result.data is empty, use the input data as fallback
    novel_data = result.data[0] if result.data and len(result.data) > 0 else data
    
    return {"message": "Cập nhật thông tin thành công", "novel": novel_data}


@app.get("/api/admin/chapters/{chapter_number}/content", summary="[Admin] Lấy nội dung chương từ R2")
async def admin_get_chapter_content(
    chapter_number: int,
    authorization: Optional[str] = Header(None),
):
    """Lấy nội dung text thô của chương từ R2 (Proxy qua Backend để tránh CORS)."""
    await verify_admin(authorization)

    # Fetch metadata to get content_url
    resp = (
        supabase.table("chapters")
        .select("content_url")
        .eq("chapter_number", chapter_number)
        .single()
        .execute()
    )

    if not resp.data or not resp.data.get("content_url"):
        raise HTTPException(status_code=404, detail="Không tìm thấy nội dung chương")

    if not r2_client:
        missing = []
        if not R2_ACCESS_KEY: missing.append("R2_ACCESS_KEY_ID")
        if not R2_SECRET_KEY: missing.append("R2_SECRET_ACCESS_KEY")
        if not R2_ENDPOINT: missing.append("R2_ENDPOINT_URL")
        detail = f"R2 chưa được cấu hình. Thiếu biến: {', '.join(missing)}"
        raise HTTPException(status_code=500, detail=detail)

    # Extract object key from URL (more robustly)
    content_url = resp.data["content_url"]
    # Handle possible http/https mismatch or trailing slashes
    import re
    clean_url = re.sub(r'^https?://', '', content_url)
    clean_base = re.sub(r'^https?://', '', R2_PUBLIC_URL)
    object_key = clean_url.replace(clean_base, "").lstrip("/")

    try:
        r2_resp = r2_client.get_object(Bucket=R2_BUCKET, Key=object_key)
        content = r2_resp["Body"].read().decode("utf-8")
        return PlainTextResponse(content)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Lỗi khi đọc từ R2: {str(e)}")


# === DELETE chapter route was at the end ===
@app.delete("/api/admin/chapters/{chapter_number}", summary="[Admin] Xóa chương")
async def admin_delete_chapter(
    chapter_number: int,
    authorization: Optional[str] = Header(None),
):
    """Xóa chương: Xóa file trên R2 và xóa metadata trong Supabase."""
    await verify_admin(authorization)

    # Fetch existing chapter
    existing = supabase.table("chapters").select("*").eq("chapter_number", chapter_number).single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail=f"Chương {chapter_number} không tìm thấy")

    chapter = existing.data

    # Delete from R2
    if r2_client and chapter.get("content_url"):
        object_key = chapter["content_url"].replace(f"{R2_PUBLIC_URL}/", "")
        try:
            r2_client.delete_object(Bucket=R2_BUCKET, Key=object_key)
        except Exception:
            pass  # Continue even if R2 delete fails

    # Delete from Supabase
    supabase.table("chapters").delete().eq("chapter_number", chapter_number).execute()

    return {"message": f"Đã xóa chương {chapter_number}"}


# === ANALYTICS ROUTES ===

@app.post("/api/chapters/{chapter_number}/view", summary="Tăng lượt đọc chương")
async def increment_view(chapter_number: int):
    """
    Tăng số lượt đọc cho một chương.
    Sử dụng RPC trên Supabase để đảm bảo tính nguyên tử (atomic increment).
    """
    try:
        # Gọi RPC function đã được tạo trong Supabase
        # Function: increment_chapter_view(chapter_num int)
        supabase.rpc("increment_chapter_view", {"chapter_num": chapter_number}).execute()
        return {"status": "success"}
    except Exception as e:
        # Fallback: Nếu RPC chưa được cài đặt, thực hiện update thủ công (không atomic nhưng vẫn chạy được)
        try:
            resp = supabase.table("chapters").select("view_count").eq("chapter_number", chapter_number).single().execute()
            if resp.data:
                current_views = resp.data.get("view_count", 0)
                supabase.table("chapters").update({"view_count": current_views + 1}).eq("chapter_number", chapter_number).execute()
                return {"status": "success", "note": "manual_update"}
        except:
            pass
        return {"status": "error", "detail": str(e)}


@app.get("/api/admin/analytics/top-chapters", summary="[Admin] Top chương đọc nhiều nhất")
async def admin_get_top_chapters(
    limit: int = Query(10, ge=1, le=50),
    authorization: Optional[str] = Header(None),
):
    """Lấy danh sách các chương có lượt đọc cao nhất."""
    await verify_admin(authorization)
    
    try:
        resp = (
            supabase.table("chapters")
            .select("chapter_number, title, view_count")
            .order("view_count", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
