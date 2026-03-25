"""
FastAPI Backend - M蘯｡t Th蘯ｿ Sinh Hoﾃ｡ Nguy Cﾆ｡
Cung c蘯･p API metadata chﾆｰﾆ｡ng. N盻冓 dung chﾆｰﾆ｡ng ﾄ柁ｰ盻｣c fetch t盻ｫ Cloudflare R2.
"""

import io
import os
import re
import unicodedata
# Force re-deploy to Vercel and Render (Trigger: 2026-03-25 23:02)
from typing import Optional, List
from urllib.parse import quote
import boto3
from botocore.client import Config
import httpx
from fastapi import FastAPI, HTTPException, Query, Header, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, PlainTextResponse
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
import sys
# Ensure the current directory is in sys.path to handle different execution contexts (Local vs Render)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from security_utils import sanitize_html, sanitize_plaintext, extract_bearer_token
except ImportError:
    try:
        from backend.security_utils import sanitize_html, sanitize_plaintext, extract_bearer_token
    except ImportError:
        # Fallback for some environments
        sys.path.append(os.path.join(current_dir, ".."))
        from backend.security_utils import sanitize_html, sanitize_plaintext, extract_bearer_token

# Import routers with robust path handling
try:
    from routes.engagement import create_engagement_router
    from routes.hq_dashboard import router as hq_router
    from routes.ai_oracle import router as oracle_router
    from routes.wiki_search import router as wiki_router
except ImportError:
    from backend.routes.engagement import create_engagement_router
    from backend.routes.hq_dashboard import router as hq_router
    from backend.routes.ai_oracle import router as oracle_router
    from backend.routes.wiki_search import router as wiki_router


load_dotenv(override=True)

# === SUPABASE CLIENT ===
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL vﾃ SUPABASE_KEY ph蘯｣i ﾄ柁ｰ盻｣c c蘯･u hﾃｬnh trong file .env")

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


# === ADMIN AUTH ===
async def verify_admin(authorization: Optional[str]) -> dict:
    """
    Xﾃ｡c th盻ｱc token Admin t盻ｫ Header Authorization (Bearer <token>).
    """
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Thi蘯ｿu token xﾃ｡c th盻ｱc. Hﾃ｣y ﾄ惰ハg nh蘯ｭp l蘯｡i."
        )

    try:
        # Verify Supabase JWT only
        user_resp = supabase.auth.get_user(token)
        if not user_resp or not user_resp.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token khﾃｴng h盻｣p l盻・ho蘯ｷc ﾄ妥｣ h蘯ｿt h蘯｡n."
            )
        
        # Truy v蘯･n profile ﾄ黛ｻ・l蘯･y role (editor/superadmin)
        profile_resp = supabase.table("profiles").select("role").eq("id", user_resp.user.id).execute()
        
        user_role = "editor" # M蘯ｷc ﾄ黛ｻ杵h
        if profile_resp.data:
            user_role = profile_resp.data[0].get("role", "editor").lower()
            
        return {
            "id": user_resp.user.id,
            "email": user_resp.user.email,
            "role": user_role
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Auth Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token khﾃｴng h盻｣p l盻・ho蘯ｷc ﾄ妥｣ h蘯ｿt h蘯｡n."
        )


# === FASTAPI APP ===
app = FastAPI(
    title="M蘯｡t Th蘯ｿ API",
    description="API backend cho website ﾄ黛ｻ皇 truy盻㌻ M蘯｡t Th蘯ｿ - Sinh Hoﾃ｡ Nguy Cﾆ｡",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,  # disable redoc ﾄ黛ｻ・gi蘯｣m memory trﾃｪn Render free tier
)

# === CORS MIDDLEWARE ===
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=ALLOWED_ORIGINS != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(create_engagement_router(supabase))
app.include_router(hq_router)
app.include_router(oracle_router)
app.include_router(wiki_router)


@app.middleware("http")
async def log_requests(request, call_next):
    # Log incoming request for better debugging on Render/Vercel
    print(f"DEBUG: {request.method} {request.url}")
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        import traceback
        print(f"ERROR: Crash in {request.method} {request.url}: {str(e)}")
        print(traceback.format_exc())
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )

# === DATA MODELS ===
class Chapter(BaseModel):
    id: int
    chapter_number: int
    title: str
    content_url: str  # Cloudflare R2 public URL
    created_at: str
    word_count: Optional[int] = None
    view_count: int = 0
    is_side_story: bool = False

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
    page: int = Query(1, ge=1, description="S盻・trang"),
    limit: int = Query(50, ge=1, le=100, description="S盻・chﾆｰﾆ｡ng m盻擁 trang"),
    sort: str = Query("asc", pattern="^(asc|desc)$", description="Th盻ｩ t盻ｱ s蘯ｯp x蘯ｿp: asc ho蘯ｷc desc"),
    search: Optional[str] = Query(None, description="Tﾃｬm ki蘯ｿm theo tiﾃｪu ﾄ黛ｻ・ho蘯ｷc s盻・chﾆｰﾆ｡ng"),
    is_side_story: Optional[bool] = Query(None, description="L盻皇 ngo蘯｡i truy盻㌻ (true) ho蘯ｷc m蘯｡ch chﾃｭnh (false)"),
):
    """
    L蘯･y danh sﾃ｡ch chﾆｰﾆ｡ng cﾃｳ phﾃ｢n trang.
    
    - **page**: Trang hi盻㌻ t蘯｡i (b蘯ｯt ﾄ黛ｺｧu t盻ｫ 1)
    - **limit**: S盻・chﾆｰﾆ｡ng m盻擁 trang (t盻訴 ﾄ疎 100)
    - **sort**: S蘯ｯp x蘯ｿp theo th盻ｩ t盻ｱ chﾆｰﾆ｡ng (asc/desc)
    """
    try:
        offset = (page - 1) * limit

        # Build base query
        query = supabase.table("chapters").select("id, chapter_number, title, content_url, created_at, word_count, is_side_story", count="exact")
        
        # Apply filters
        if is_side_story is not None:
            query = query.eq("is_side_story", is_side_story)

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
        total_pages = (total + limit - 1) // limit if limit > 0 else 1

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
    L蘯･y thﾃｴng tin metadata c盻ｧa m盻冲 chﾆｰﾆ｡ng bao g盻杜 URL file R2 ch盻ｩa n盻冓 dung.
    Frontend s蘯ｽ dﾃｹng content_url nﾃy ﾄ黛ｻ・fetch n盻冓 dung th蘯ｳng t盻ｫ Cloudflare CDN.
    
    - **chapter_number**: S盻・chﾆｰﾆ｡ng th盻ｱc t蘯ｿ trong truy盻㌻
    """
    try:
        resp = (
            supabase.table("chapters")
            .select("id, chapter_number, title, content_url, created_at, word_count, is_side_story")
            .eq("chapter_number", chapter_number)
            .single()
            .execute()
        )

        if not resp.data:
            raise HTTPException(status_code=404, detail=f"Chﾆｰﾆ｡ng {chapter_number} khﾃｴng tﾃｬm th蘯･y")

        return Chapter(**resp.data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# === TTS PROXY ===
@app.get("/api/tts", summary="Google Translate TTS Proxy")
async def tts_proxy(
    text: str = Query(..., max_length=200, description="Vﾄハ b蘯｣n c蘯ｧn ﾄ黛ｻ皇 (t盻訴 ﾄ疎 200 kﾃｽ t盻ｱ)"),
    lang: str = Query("vi", description="Ngﾃｴn ng盻ｯ (vi, en, ...)"),
    speed: float = Query(1.0, ge=0.5, le=2.0, description="T盻祖 ﾄ黛ｻ・ﾄ黛ｻ皇"),
):
    """
    Proxy Google Translate TTS ﾄ黛ｻ・trﾃ｡nh b盻・ch蘯ｷn khi g盻絞 tr盻ｱc ti蘯ｿp t盻ｫ browser.
    Tr蘯｣ v盻・audio MP3 stream.
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
                detail=f"Google TTS tr蘯｣ v盻・{resp.status_code}"
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
    is_side_story: bool = False


class AdminChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_side_story: Optional[bool] = None


@app.post("/api/admin/chapters", summary="[Admin] Thﾃｪm chﾆｰﾆ｡ng m盻嬖")
async def admin_create_chapter(
    body: AdminChapterCreate,
    authorization: Optional[str] = Header(None),
):
    """Thﾃｪm chﾆｰﾆ｡ng m盻嬖: Upload n盻冓 dung lﾃｪn R2, lﾆｰu metadata vﾃo Supabase."""
    await verify_admin(authorization)

    if not r2_client:
        raise HTTPException(status_code=500, detail="R2 chﾆｰa ﾄ柁ｰ盻｣c c蘯･u hﾃｬnh trﾃｪn server")

    # Check chapter number uniqueness
    existing = supabase.table("chapters").select("id").eq("chapter_number", body.chapter_number).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail=f"Chﾆｰﾆ｡ng {body.chapter_number} ﾄ妥｣ t盻渡 t蘯｡i")

    sanitized_content = sanitize_html(body.content) or ""

    # Upload content to R2
    slug = slugify(f"chuong-{body.chapter_number}-{body.title}")
    object_key = f"chapters/{body.chapter_number:04d}-{slug}.txt"
    content_bytes = sanitized_content.encode("utf-8")

    r2_client.put_object(
        Bucket=R2_BUCKET,
        Key=object_key,
        Body=content_bytes,
        ContentType="text/plain; charset=utf-8",
    )

    content_url = f"{R2_PUBLIC_URL}/{object_key}"
    word_count = len(sanitized_content.split())

    # Insert metadata into Supabase
    result = supabase.table("chapters").insert({
        "chapter_number": body.chapter_number,
        "title": body.title,
        "content_url": content_url,
        "word_count": word_count,
        "is_side_story": body.is_side_story,
    }).execute()

    return {"message": "Thﾃｪm chﾆｰﾆ｡ng thﾃnh cﾃｴng", "chapter": result.data[0]}


@app.put("/api/admin/chapters/{chapter_number}", summary="[Admin] S盻ｭa chﾆｰﾆ｡ng")
async def admin_update_chapter(
    chapter_number: int,
    body: AdminChapterUpdate,
    authorization: Optional[str] = Header(None),
):
    """S盻ｭa tiﾃｪu ﾄ黛ｻ・vﾃ/ho蘯ｷc n盻冓 dung chﾆｰﾆ｡ng."""
    await verify_admin(authorization)

    # Fetch existing chapter
    existing = supabase.table("chapters").select("*").eq("chapter_number", chapter_number).single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail=f"Chﾆｰﾆ｡ng {chapter_number} khﾃｴng tﾃｬm th蘯･y")

    chapter = existing.data
    update_data = {}

    # Update content on R2 if provided
    if body.content is not None:
        if not r2_client:
            raise HTTPException(status_code=500, detail="R2 chﾆｰa ﾄ柁ｰ盻｣c c蘯･u hﾃｬnh trﾃｪn server")
        sanitized_content = sanitize_html(body.content) or ""

        # Derive key from content_url
        content_url = chapter["content_url"]
        object_key = content_url.replace(f"{R2_PUBLIC_URL}/", "")

        r2_client.put_object(
            Bucket=R2_BUCKET,
            Key=object_key,
            Body=sanitized_content.encode("utf-8"),
            ContentType="text/plain; charset=utf-8",
        )
        update_data["word_count"] = len(sanitized_content.split())

    if body.title is not None:
        update_data["title"] = body.title

    if body.is_side_story is not None:
        update_data["is_side_story"] = body.is_side_story

    if update_data:
        result = supabase.table("chapters").update(update_data).eq("chapter_number", chapter_number).execute()
        return {"message": "C蘯ｭp nh蘯ｭt thﾃnh cﾃｴng", "chapter": result.data[0]}

    return {"message": "Khﾃｴng cﾃｳ gﾃｬ thay ﾄ黛ｻ品"}


class NovelSettings(BaseModel):
    title: str
    author: str
    description: str
    cover_url: str
    status: str
    genres: list[str]
    donate_qr_url: str = ""
    total_chapters: int = 0
    max_chapter: int = 0
    total_views: int = 0
    total_likes: int = 0
    ai_model_name: str = "gemini-3.1-flash-lite-preview"
    has_ai_key: bool = False  # Frontend diagnostic


class AdminNovelUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    genres: Optional[list[str]] = None
    ai_model_name: Optional[str] = None
    ai_api_key: Optional[str] = None


@app.get("/api/novel", response_model=NovelSettings)
async def get_novel_settings():
    """L蘯･y thﾃｴng tin chung c盻ｧa truy盻㌻ (Tﾃｪn, tﾃ｡c gi蘯｣, mﾃｴ t蘯｣...)"""
    try:
        # 1. Fetch current stats (Total chapters, Max chapter, and aggregated View/Like counts)
        # We fetch all at once to minimize Supabase calls
        stats_resp = supabase.table("chapters").select("chapter_number, view_count, likes_count", count="exact").order("chapter_number", desc=True).execute()
        
        total_chapters = stats_resp.count or 0
        max_chapter = stats_resp.data[0]["chapter_number"] if stats_resp.data else 0
        total_views = sum(row.get("view_count", 0) for row in stats_resp.data) if stats_resp.data else 0
        total_likes = sum(row.get("likes_count", 0) for row in stats_resp.data) if stats_resp.data else 0

        # 2. Fetch novel settings
        resp = supabase.table("novel_settings").select("*").eq("id", 1).single().execute()
        
        default_settings = {
            "title": "M蘯｡t Th蘯ｿ - Sinh Hoﾃ｡ Nguy Cﾆ｡",
            "author": "Hﾃn Nhﾆｰ盻｣c Tuy蘯ｿt",
            "description": "Truy盻㌻ l蘯･y b盻訴 c蘯｣nh t蘯ｭn th蘯ｿ ﾄ黛ｻ冲 nhiﾃｪn ph盻ｧ xu盻創g, thﾃ｢y ma lan trﾃn, quﾃ｡i v蘯ｭt d盻・bi蘯ｿn n盻品 lﾃｪn kh蘯ｯp nﾆ｡i, loﾃi ngﾆｰ盻拱 b盻・ﾄ黛ｺｩy vﾃo m盻冲 trﾃｲ chﾆ｡i tﾃn kh盻祖 kinh hoﾃng nhﾆｰng cﾅｩng 蘯ｩn ch盻ｩa cﾆ｡ h盻冓 l盻嬾 lao...",
            "cover_url": "https://pub-28de8065099f4ffea76bd6dc28a9bcf3.r2.dev/matthe-hero.jpg",
            "status": "ﾄ紳ng c蘯ｭp nh蘯ｭt",
            "genres": ["M蘯｡t Th蘯ｿ", "Sinh T盻渡", "H盻・Th盻創g", "D盻・Nﾄハg"],
            "donate_qr_url": "",
            "total_chapters": total_chapters,
            "max_chapter": max_chapter,
            "total_views": total_views,
            "total_likes": total_likes
        }

        if not resp.data:
            return NovelSettings(**default_settings)
        
        # Merge data
        model_fields = NovelSettings.__fields__.keys()
        final_data = {k: v for k, v in resp.data.items() if k in model_fields}
        final_data["description"] = sanitize_html(final_data.get("description")) or ""
        final_data["total_chapters"] = total_chapters
        final_data["max_chapter"] = max_chapter
        final_data["total_views"] = total_views
        final_data["total_likes"] = total_likes
        final_data["ai_model_name"] = resp.data.get("ai_model_name", "gemini-3.1-flash-lite-preview")
        
        # Security: Never return the actual API key to the frontend
        db_key = resp.data.get("ai_api_key")
        final_data["has_ai_key"] = bool(db_key and len(db_key) > 5)
        if "ai_api_key" in final_data:
            del final_data["ai_api_key"]
        
        return NovelSettings(**final_data)
    except Exception as e:
        print(f"DEBUG: get_novel_settings error: {str(e)}")
        # Fallback d盻ｯ li盻㎡ m蘯ｷc ﾄ黛ｻ杵h n蘯ｿu l盻擁 DB (trﾃ｡nh s蘯ｭp trang ch盻ｧ)
        return NovelSettings(
            title="M蘯｡t Th蘯ｿ - Sinh Hoﾃ｡ Nguy Cﾆ｡",
            author="Hﾃn Nhﾆｰ盻｣c Tuy蘯ｿt",
            description="L盻擁 t蘯｣i d盻ｯ li盻㎡. Hﾃ｣y th盻ｭ l蘯｡i sau.",
            cover_url="/hero-bg.png",
            status="ﾄ紳ng c蘯ｭp nh蘯ｭt",
            genres=["M蘯｡t Th蘯ｿ"],
            total_chapters=0,
            max_chapter=0,
            total_views=0,
            total_likes=0,
            ai_model_name="gemini-1.5-flash"
        )


@app.put("/api/admin/novel", summary="[Admin] Cập nhật thông tin truyện & cấu hình hệ thống")
async def admin_update_novel(
    body: AdminNovelUpdate,
    authorization: Optional[str] = Header(None),
):
    """Cập nhật các thông tin chung của truyện và cấu hình AI."""
    await verify_admin(authorization)
    
    data = body.model_dump(exclude_none=True)
    if not data:
        return {"message": "Không có gì thay đổi"}
    
    # Update novel settings (ID 1)
    result = supabase.table("novel_settings").upsert({**data, "id": 1}).execute()
    return {"message": "Cập nhật thành công", "data": result.data[0]}


class HomepageSettings(BaseModel):
    warning_title: Optional[str] = None
    warning_subtitle: Optional[str] = None
    warning_headline: Optional[str] = None
    warning_description: Optional[str] = None
    features_title: Optional[str] = None
    features_json: Optional[list] = None


class Profile(BaseModel):
    id: str
    email: str
    role: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: str


class AccountInvite(BaseModel):
    email: str
    password: str
    display_name: str
    role: str = "editor"


@app.get("/api/admin/users", response_model=List[Profile], summary="[Admin] Danh sﾃ｡ch nhﾃ｢n s盻ｱ")
async def admin_get_users(authorization: Optional[str] = Header(None)):
    """L蘯･y danh sﾃ｡ch t蘯･t c蘯｣ nhﾃ｢n s盻ｱ (Profiles). Ch盻・dﾃnh cho SuperAdmin."""
    user = await verify_admin(authorization)
    
    # Ch盻・SuperAdmin m盻嬖 ﾄ柁ｰ盻｣c xem danh sﾃ｡ch nhﾃ｢n s盻ｱ
    if user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Ch盻・SuperAdmin m盻嬖 cﾃｳ quy盻］ xem danh sﾃ｡ch nhﾃ｢n s盻ｱ")
    
    resp = supabase.table("profiles").select("*").order("created_at", desc=True).execute()
    return resp.data


@app.post("/api/admin/invite", summary="[Admin] T蘯｡o tﾃi kho蘯｣n nhﾃ｢n s盻ｱ m盻嬖")
async def admin_invite_user(
    body: AccountInvite,
    authorization: Optional[str] = Header(None)
):
    """T蘯｡o tﾃi kho蘯｣n Auth vﾃ Profile m盻嬖 cho nhﾃ｢n viﾃｪn. Ch盻・dﾃnh cho SuperAdmin."""
    user = await verify_admin(authorization)
    
    # Ki盻ノ tra quy盻］ SuperAdmin
    if user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Ch盻・SuperAdmin m盻嬖 cﾃｳ quy盻］ t蘯｡o nhﾃ｢n s盻ｱ m盻嬖")
    
    # 1. T蘯｡o user trong h盻・th盻創g Auth c盻ｧa Supabase b蘯ｱng Service Role
    try:
        # auth.admin.create_user c蘯ｧn service_role key
        auth_resp = supabase.auth.admin.create_user({
            "email": body.email,
            "password": body.password,
            "email_confirm": True,
            "user_metadata": {"full_name": body.display_name}
        })
        
        if not auth_resp or not auth_resp.user:
            raise Exception("Supabase khﾃｴng tr蘯｣ v盻・thﾃｴng tin user m盻嬖.")

        # 2. Update role trong b蘯｣ng profiles
        if body.role != "editor":
            supabase.table("profiles").update({"role": body.role}).eq("id", auth_resp.user.id).execute()
            
        return {"message": "ﾄ静｣ t蘯｡o tﾃi kho蘯｣n thﾃnh cﾃｴng", "user_id": auth_resp.user.id}
    except Exception as e:
        error_msg = str(e)
        if "User not allowed" in error_msg:
            detail = "L盻擁: Backend chﾆｰa ﾄ柁ｰ盻｣c c蘯･p quy盻］ Admin (Service Role Key). Hﾃ｣y ki盻ノ tra SUPABASE_KEY."
        else:
            detail = f"L盻擁 t蘯｡o tﾃi kho蘯｣n: {error_msg}"
        raise HTTPException(status_code=500, detail=detail)


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    role: Optional[str] = None

@app.get("/api/user/role", summary="L蘯･y quy盻］ (Role) c盻ｧa ngﾆｰ盻拱 dﾃｹng hi盻㌻ t蘯｡i")
async def get_current_user_role(authorization: Optional[str] = Header(None)):
    """Ki盻ノ tra quy盻］ c盻ｧa ngﾆｰ盻拱 dﾃｹng (editor hay superadmin)."""
    user = await verify_admin(authorization)
    return {"role": user["role"]}

@app.put("/api/admin/personnel/{user_id}", summary="[Admin] C蘯ｭp nh蘯ｭt nhﾃ｢n s盻ｱ")
async def admin_update_user(
    user_id: str,
    body: ProfileUpdate,
    authorization: Optional[str] = Header(None)
):
    """C蘯ｭp nh蘯ｭt profile nhﾃ｢n s盻ｱ (tﾃｪn, vai trﾃｲ, email, m蘯ｭt kh蘯ｩu). Ch盻・dﾃnh cho SuperAdmin."""
    user = await verify_admin(authorization)

    if user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Ch盻・SuperAdmin m盻嬖 cﾃｳ quy盻］ ch盻穎h s盻ｭa nhﾃ｢n s盻ｱ")

    try:
        from datetime import datetime, timezone
        # Update profile table
        profile_data = {}
        if body.display_name is not None:
            profile_data["display_name"] = body.display_name
        if body.role is not None:
            profile_data["role"] = body.role
        if body.email is not None:
            profile_data["email"] = body.email

        if profile_data:
            profile_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            supabase.table("profiles").update(profile_data).eq("id", user_id).execute()

        # Update Auth fields (email, password)
        auth_updates = {}
        if body.email:
            auth_updates["email"] = body.email
        if body.password:
            if len(body.password) < 6:
                raise HTTPException(status_code=400, detail="M蘯ｭt kh蘯ｩu ph蘯｣i cﾃｳ t盻訴 thi盻ブ 6 kﾃｽ t盻ｱ")
            auth_updates["password"] = body.password

        if auth_updates:
            supabase.auth.admin.update_user_by_id(user_id, auth_updates)

        return {"message": "ﾄ静｣ c蘯ｭp nh蘯ｭt thﾃｴng tin nhﾃ｢n s盻ｱ thﾃnh cﾃｴng"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"L盻擁 c蘯ｭp nh蘯ｭt: {str(e)}")


@app.delete("/api/admin/users/{user_id}", summary="[Admin] Xoﾃ｡ nhﾃ｢n s盻ｱ")
async def admin_delete_user(
    user_id: str,
    authorization: Optional[str] = Header(None)
):
    """Xoﾃ｡ tﾃi kho蘯｣n nhﾃ｢n s盻ｱ. Ch盻・dﾃnh cho SuperAdmin."""
    user = await verify_admin(authorization)
    
    # Ki盻ノ tra quy盻］ SuperAdmin
    if user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Ch盻・SuperAdmin m盻嬖 cﾃｳ quy盻］ xoﾃ｡ nhﾃ｢n s盻ｱ")
    
    try:
        # Xoﾃ｡ trong Auth (b蘯｣ng profiles s蘯ｽ t盻ｱ ﾄ黛ｻ冢g xoﾃ｡ do CASCADE)
        supabase.auth.admin.delete_user(user_id)
        return {"message": "ﾄ静｣ xoﾃ｡ nhﾃ｢n s盻ｱ thﾃnh cﾃｴng"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"L盻擁 khi xoﾃ｡ nhﾃ｢n s盻ｱ: {str(e)}")


# ============================================================
# MAP LOCATIONS API (Phase 09)
# ============================================================

class MapLocation(BaseModel):
    id: str
    name: str
    type: str  # safe_zone, danger_zone, neutral, outpost, ruins
    description: Optional[str] = None
    lat: float
    lng: float
    image_url: Optional[str] = None
    created_at: str


class AdminMapLocationIn(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    lat: float
    lng: float
    image_url: Optional[str] = None


@app.get("/api/map-locations", response_model=List[MapLocation], summary="Lấy danh sách điểm bản đồ")
async def get_map_locations():
    """L蘯･y t蘯･t c蘯｣ cﾃ｡c ﾄ訴盻ノ ﾄ妥｡nh d蘯･u trﾃｪn b蘯｣n ﾄ黛ｻ・(Cﾃｴng khai)."""
    resp = supabase.table("map_locations").select("*").order("created_at", desc=True).execute()
    rows = resp.data or []
    for row in rows:
        row["description"] = sanitize_html(row.get("description")) if row.get("description") is not None else None
    return rows


@app.post("/api/admin/map-locations", response_model=MapLocation, summary="[Admin] T蘯｡o ﾄ訴盻ノ b蘯｣n ﾄ黛ｻ・m盻嬖")
async def admin_create_map_location(
    body: AdminMapLocationIn,
    authorization: Optional[str] = Header(None)
):
    """T蘯｡o ﾄ訴盻ノ ﾄ妥｡nh d蘯･u m盻嬖 trﾃｪn b蘯｣n ﾄ黛ｻ・ Ch盻・dﾃnh cho Admin."""
    await verify_admin(authorization)

    payload = body.dict()
    payload["description"] = sanitize_html(payload.get("description")) if payload.get("description") is not None else None

    resp = supabase.table("map_locations").insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Không thể tạo điểm bản đồ")
    return resp.data[0]


@app.put("/api/admin/map-locations/{location_id}", response_model=MapLocation, summary="[Admin] Cập nhật điểm bản đồ")
async def admin_update_map_location(
    location_id: str,
    body: AdminMapLocationIn,
    authorization: Optional[str] = Header(None)
):
    """C蘯ｭp nh蘯ｭt thﾃｴng tin ﾄ訴盻ノ ﾄ妥｡nh d蘯･u. Ch盻・dﾃnh cho Admin."""
    await verify_admin(authorization)

    payload = body.dict()
    payload["description"] = sanitize_html(payload.get("description")) if payload.get("description") is not None else None

    resp = supabase.table("map_locations").update(payload).eq("id", location_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Khﾃｴng tﾃｬm th蘯･y ﾄ訴盻ノ b蘯｣n ﾄ黛ｻ・ﾄ黛ｻ・c蘯ｭp nh蘯ｭt")
    return resp.data[0]


@app.delete("/api/admin/map-locations/{location_id}", summary="[Admin] Xóa điểm bản đồ")
async def admin_delete_map_location(
    location_id: str,
    authorization: Optional[str] = Header(None)
):
    """Xoﾃ｡ ﾄ訴盻ノ ﾄ妥｡nh d蘯･u kh盻淑 b蘯｣n ﾄ黛ｻ・ Ch盻・dﾃnh cho Admin."""
    await verify_admin(authorization)
    
    supabase.table("map_locations").delete().eq("id", location_id).execute()
    return {"message": "ﾄ静｣ xoﾃ｡ ﾄ訴盻ノ b蘯｣n ﾄ黛ｻ・thﾃnh cﾃｴng"}


@app.get("/api/homepage", response_model=HomepageSettings)
async def get_homepage_settings():
    """L蘯･y c蘯･u hﾃｬnh n盻冓 dung hi盻ハ th盻・trﾃｪn trang ch盻ｧ."""
    try:
        resp = supabase.table("homepage_settings").select("*").eq("id", 1).single().execute()
        if not resp.data:
            return HomepageSettings(
                warning_title="C蘯｢NH Bﾃ＾ KHU V盻ｰC C蘯､M",
                warning_subtitle="BIOSAFETY LEVEL 4 ﾂｷ RESTRICTED ACCESS",
                warning_headline="TR蘯ｬN ﾄ雪ｻ晦 SINH T盻ｬ",
                warning_description="Nﾄノ 20XX. Virus Z-79 bﾃｹng phﾃ｡t t盻ｫ m盻冲 phﾃｲng thﾃｭ nghi盻㍊ bﾃｭ m蘯ｭt...",
                features_title="ﾄ蝕盻・ N盻祢 B蘯ｬT",
                features_json=[]
            )
        cleaned = dict(resp.data)
        cleaned["warning_description"] = sanitize_html(cleaned.get("warning_description")) or ""
        return HomepageSettings(**cleaned)
    except Exception:
        # Fallback if table doesn't exist yet
        return HomepageSettings(
            warning_title="C蘯｢NH Bﾃ＾ KHU V盻ｰC C蘯､M",
            warning_subtitle="BIOSAFETY LEVEL 4 ﾂｷ RESTRICTED ACCESS",
            warning_headline="TR蘯ｬN ﾄ雪ｻ晦 SINH T盻ｬ",
            warning_description="Nﾄノ 20XX. Virus Z-79 bﾃｹng phﾃ｡t t盻ｫ m盻冲 phﾃｲng thﾃｭ nghi盻㍊ bﾃｭ m蘯ｭt...",
            features_title="ﾄ蝕盻・ N盻祢 B蘯ｬT",
            features_json=[]
        )


@app.put("/api/admin/homepage", summary="[Admin] C蘯ｭp nh蘯ｭt c蘯･u hﾃｬnh trang ch盻ｧ")
async def admin_update_homepage(
    body: HomepageSettings,
    authorization: Optional[str] = Header(None),
):
    """C蘯ｭp nh蘯ｭt cﾃ｡c ﾄ双蘯｡n text vﾃ c蘯･u hﾃｬnh trﾃｪn trang ch盻ｧ."""
    await verify_admin(authorization)
    
    data = body.model_dump(exclude_none=True)
    data["warning_description"] = sanitize_html(data.get("warning_description")) or ""
    data["id"] = 1
    data["updated_at"] = "now()"
    
    result = supabase.table("homepage_settings").upsert(data).execute()
    return {"message": "C蘯ｭp nh蘯ｭt trang ch盻ｧ thﾃnh cﾃｴng", "settings": result.data[0] if result.data else data}


@app.put("/api/admin/novel", summary="[Admin] C蘯ｭp nh蘯ｭt thﾃｴng tin truy盻㌻")
async def admin_update_novel(
    body: NovelSettings,
    authorization: Optional[str] = Header(None),
):
    """C蘯ｭp nh蘯ｭt thﾃｴng tin chung c盻ｧa truy盻㌻."""
    await verify_admin(authorization)
    
    # Upsert vﾃo dﾃｲng ID=1
    data = body.dict()
    data["description"] = sanitize_html(data.get("description")) or ""
    data["id"] = 1
    
    result = supabase.table("novel_settings").upsert(data).execute()
    
    # Defensive check: if result.data is empty, use the input data as fallback
    novel_data = result.data[0] if result.data and len(result.data) > 0 else data
    
    return {"message": "C蘯ｭp nh蘯ｭt thﾃｴng tin thﾃnh cﾃｴng", "novel": novel_data}


@app.get("/api/admin/chapters/{chapter_number}/content", summary="[Admin] L蘯･y n盻冓 dung chﾆｰﾆ｡ng t盻ｫ R2")
async def admin_get_chapter_content(
    chapter_number: int,
    authorization: Optional[str] = Header(None),
):
    """L蘯･y n盻冓 dung text thﾃｴ c盻ｧa chﾆｰﾆ｡ng t盻ｫ R2 (Proxy qua Backend ﾄ黛ｻ・trﾃ｡nh CORS)."""
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
        raise HTTPException(status_code=404, detail="Khﾃｴng tﾃｬm th蘯･y n盻冓 dung chﾆｰﾆ｡ng")

    if not r2_client:
        missing = []
        if not R2_ACCESS_KEY: missing.append("R2_ACCESS_KEY_ID")
        if not R2_SECRET_KEY: missing.append("R2_SECRET_ACCESS_KEY")
        if not R2_ENDPOINT: missing.append("R2_ENDPOINT_URL")
        detail = f"R2 chﾆｰa ﾄ柁ｰ盻｣c c蘯･u hﾃｬnh. Thi蘯ｿu bi蘯ｿn: {', '.join(missing)}"
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
        raise HTTPException(status_code=502, detail=f"L盻擁 khi ﾄ黛ｻ皇 t盻ｫ R2: {str(e)}")


# === DELETE chapter route was at the end ===
@app.delete("/api/admin/chapters/{chapter_number}", summary="[Admin] Xﾃｳa chﾆｰﾆ｡ng")
async def admin_delete_chapter(
    chapter_number: int,
    authorization: Optional[str] = Header(None),
):
    """Xﾃｳa chﾆｰﾆ｡ng: Xﾃｳa file trﾃｪn R2 vﾃ xﾃｳa metadata trong Supabase."""
    await verify_admin(authorization)

    # Fetch existing chapter
    existing = supabase.table("chapters").select("*").eq("chapter_number", chapter_number).single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail=f"Chﾆｰﾆ｡ng {chapter_number} khﾃｴng tﾃｬm th蘯･y")

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

    return {"message": f"ﾄ静｣ xﾃｳa chﾆｰﾆ｡ng {chapter_number}"}


# === ANALYTICS ROUTES ===

@app.get("/api/admin/analytics/top-chapters", summary="[Admin] Top chﾆｰﾆ｡ng ﾄ黛ｻ皇 nhi盻「 nh蘯･t")
async def admin_get_top_chapters(
    limit: int = Query(10, ge=1, le=50),
    authorization: Optional[str] = Header(None),
):
    """L蘯･y danh sﾃ｡ch cﾃ｡c chﾆｰﾆ｡ng cﾃｳ lﾆｰ盻｣t ﾄ黛ｻ皇 cao nh蘯･t."""
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


@app.get("/api/admin/analytics/top-liked", summary="[Admin] Top chﾆｰﾆ｡ng ﾄ柁ｰ盻｣c yﾃｪu thﾃｭch nh蘯･t")
async def admin_get_top_liked(
    limit: int = Query(10, ge=1, le=50),
    authorization: Optional[str] = Header(None),
):
    """L蘯･y danh sﾃ｡ch cﾃ｡c chﾆｰﾆ｡ng cﾃｳ lﾆｰ盻｣t th蘯｣ tim cao nh蘯･t."""
    await verify_admin(authorization)

    try:
        resp = (
            supabase.table("chapters")
            .select("chapter_number, title, likes_count")
            .order("likes_count", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === COMMENT ROUTES ===

class Comment(BaseModel):
    id: str
    chapter_number: int
    user_name: str
    content: str
    created_at: str


class AdminCommentUpdate(BaseModel):
    content: str


@app.get("/api/admin/comments", summary="[Admin] L蘯･y danh sﾃ｡ch t蘯･t c蘯｣ bﾃｬnh lu蘯ｭn")
async def admin_get_comments(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    authorization: Optional[str] = Header(None)
):
    """L蘯･y danh sﾃ｡ch bﾃｬnh lu蘯ｭn trﾃｪn toﾃn h盻・th盻創g, cﾃｳ phﾃ｢n trang."""
    await verify_admin(authorization)
    try:
        offset = (page - 1) * limit
        resp = (
            supabase.table("comments")
            .select("*", count="exact")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        total = resp.count or 0
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        comments = resp.data or []
        for comment in comments:
            comment["user_name"] = sanitize_plaintext(comment.get("user_name")) or "ẩn danh"
            comment["content"] = sanitize_plaintext(comment.get("content")) or ""
        return {
            "comments": comments,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/admin/comments/{comment_id}", summary="[Admin] S盻ｭa bﾃｬnh lu蘯ｭn")
async def admin_update_comment(
    comment_id: str,
    body: AdminCommentUpdate,
    authorization: Optional[str] = Header(None)
):
    """S盻ｭa n盻冓 dung bﾃｬnh lu蘯ｭn c盻ｧa ﾄ黛ｻ冂 gi蘯｣."""
    await verify_admin(authorization)
    try:
        resp = supabase.table("comments").update({"content": sanitize_plaintext(body.content) or ""}).eq("id", comment_id).execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="Khﾃｴng tﾃｬm th蘯･y bﾃｬnh lu蘯ｭn")
        return resp.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/admin/comments/{comment_id}", summary="[Admin] Xﾃｳa bﾃｬnh lu蘯ｭn")
async def admin_delete_comment(
    comment_id: str,
    authorization: Optional[str] = Header(None)
):
    """Xﾃｳa m盻冲 bﾃｬnh lu蘯ｭn kh盻淑 h盻・th盻創g."""
    await verify_admin(authorization)
    try:
        supabase.table("comments").delete().eq("id", comment_id).execute()
        return {"status": "success", "message": "ﾄ静｣ xﾃｳa bﾃｬnh lu蘯ｭn"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# IMAGE UPLOAD (CLOUDFLARE R2)
# ============================================================

@app.post("/api/upload/image", summary="Upload 蘯｣nh lﾃｪn Cloudflare R2 (Admin)")
async def upload_image(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """Upload 蘯｣nh ph盻･c v盻･ cho Editor/Wiki. Yﾃｪu c蘯ｧu quy盻］ Admin."""
    await verify_admin(authorization)
    
    if not r2_client:
        raise HTTPException(status_code=500, detail="C蘯･u hﾃｬnh Cloudflare R2 chﾆｰa hoﾃn ch盻穎h")
        
    try:
        import uuid
        from datetime import datetime
        
        # Validate file type
        valid_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in valid_types:
            raise HTTPException(status_code=400, detail="Ch盻・h盻・tr盻｣ file 蘯｣nh (JPG, PNG, GIF, WEBP)")
            
        # Generate unique filename
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'png'
        date_str = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"uploads/{date_str}_{unique_id}.{ext}"
        
        # Read file
        contents = await file.read()
        
        # Upload to R2 (Wrapped in threadpool to avoid blocking event loop)
        from fastapi.concurrency import run_in_threadpool
        
        await run_in_threadpool(
            r2_client.put_object,
            Bucket=R2_BUCKET,
            Key=filename,
            Body=contents,
            ContentType=file.content_type
        )
        
        # Return URL
        # ﾄ雪ｺ｣m b蘯｣o R2_PUBLIC_URL khﾃｴng k蘯ｿt thﾃｺc b蘯ｱng /
        base_url = R2_PUBLIC_URL.rstrip('/')
        public_url = f"{base_url}/{filename}"
        return {"url": public_url}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# FACTION HIERARCHY (Cﾃ｢y T盻・Ch盻ｩc Th蘯ｿ L盻ｱc)
# ============================================================

class FactionMemberIn(BaseModel):
    character_id: Optional[str] = None
    parent_id: Optional[str] = None
    role_title: str = ""
    division: Optional[str] = None
    rank_level: int = 0
    sort_order: int = 0


class FactionMemberOut(BaseModel):
    id: str
    faction_id: str
    character_id: Optional[str] = None
    parent_id: Optional[str] = None
    role_title: str
    division: Optional[str] = None
    rank_level: int
    sort_order: int
    created_at: str
    # Joined character info
    character_name: Optional[str] = None
    character_slug: Optional[str] = None
    character_image: Optional[str] = None


@app.get("/api/wiki/{slug}/hierarchy", summary="L蘯･y cﾃ｢y t盻・ch盻ｩc c盻ｧa th蘯ｿ l盻ｱc (public)")
async def get_faction_hierarchy(slug: str):
    """L蘯･y toﾃn b盻・cﾃ｢y phﾃ｢n c蘯･p c盻ｧa 1 th蘯ｿ l盻ｱc theo slug."""
    try:
        # 1. Get the faction wiki entry
        faction_resp = (
            supabase.table("wiki_entries")
            .select("id, title, category")
            .eq("slug", slug)
            .single()
            .execute()
        )
        if not faction_resp.data:
            raise HTTPException(status_code=404, detail="Khﾃｴng tﾃｬm th蘯･y th蘯ｿ l盻ｱc")
        if faction_resp.data.get("category") != "Th蘯ｿ l盻ｱc":
            raise HTTPException(status_code=400, detail="Entry nﾃy khﾃｴng ph蘯｣i Th蘯ｿ l盻ｱc")

        faction_id = faction_resp.data["id"]

        # 2. Get all members of this faction
        members_resp = (
            supabase.table("faction_members")
            .select("*")
            .eq("faction_id", faction_id)
            .order("rank_level")
            .order("sort_order")
            .execute()
        )

        members = members_resp.data or []

        # 3. Collect unique character IDs to batch-fetch their info
        char_ids = list(set(m["character_id"] for m in members if m.get("character_id")))
        char_map = {}
        if char_ids:
            chars_resp = (
                supabase.table("wiki_entries")
                .select("id, title, slug, image_url")
                .in_("id", char_ids)
                .execute()
            )
            for c in (chars_resp.data or []):
                char_map[c["id"]] = c

        # 4. Enrich members with character info
        result = []
        for m in members:
            char = char_map.get(m.get("character_id"), {})
            result.append({
                **m,
                "character_name": char.get("title"),
                "character_slug": char.get("slug"),
                "character_image": char.get("image_url"),
            })

        return {
            "faction_id": faction_id,
            "faction_title": faction_resp.data["title"],
            "members": result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/wiki/{faction_id}/members", summary="[Admin] Thﾃｪm thﾃnh viﾃｪn vﾃo cﾃ｢y th蘯ｿ l盻ｱc")
async def admin_add_faction_member(
    faction_id: str,
    body: FactionMemberIn,
    authorization: Optional[str] = Header(None),
):
    """Thﾃｪm m盻冲 node m盻嬖 vﾃo cﾃ｢y t盻・ch盻ｩc. Yﾃｪu c蘯ｧu quy盻］ Admin."""
    await verify_admin(authorization)
    try:
        data = body.model_dump(exclude_none=True)
        data["faction_id"] = faction_id
        result = supabase.table("faction_members").insert(data).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Khﾃｴng th盻・thﾃｪm thﾃnh viﾃｪn")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/admin/wiki/members/{member_id}", summary="[Admin] S盻ｭa thﾃnh viﾃｪn trong cﾃ｢y th蘯ｿ l盻ｱc")
async def admin_update_faction_member(
    member_id: str,
    body: FactionMemberIn,
    authorization: Optional[str] = Header(None),
):
    """C蘯ｭp nh蘯ｭt thﾃｴng tin node trong cﾃ｢y t盻・ch盻ｩc."""
    await verify_admin(authorization)
    try:
        data = body.model_dump(exclude_none=True)
        result = supabase.table("faction_members").update(data).eq("id", member_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Khﾃｴng tﾃｬm th蘯･y thﾃnh viﾃｪn")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/admin/wiki/members/{member_id}", summary="[Admin] Xﾃｳa thﾃnh viﾃｪn kh盻淑 cﾃ｢y th蘯ｿ l盻ｱc")
async def admin_delete_faction_member(
    member_id: str,
    authorization: Optional[str] = Header(None),
):
    """Xﾃｳa node kh盻淑 cﾃ｢y. Children s蘯ｽ ﾄ柁ｰ盻｣c detach (parent_id = null)."""
    await verify_admin(authorization)
    try:
        # Detach children first (set their parent to null)
        supabase.table("faction_members").update({"parent_id": None}).eq("parent_id", member_id).execute()
        # Delete the member
        supabase.table("faction_members").delete().eq("id", member_id).execute()
        return {"status": "deleted", "id": member_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# WIKI - Bﾃ，H KHOA TOﾃN THﾆｯ
# ============================================================

VALID_WIKI_CATEGORIES = ["Nhﾃ｢n v蘯ｭt", "Sinh v蘯ｭt", "Th蘯ｿ l盻ｱc", "V蘯ｭt ph蘯ｩm", "ﾄ雪ｻ蟻 ﾄ訴盻ノ"]


class WikiEntryOut(BaseModel):
    id: str
    title: str
    category: str
    slug: str
    summary: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[list[str]] = None
    sort_order: int = 0
    is_main_character: bool = False
    created_at: str
    updated_at: str


class WikiEntryIn(BaseModel):
    title: str
    category: str
    slug: str
    summary: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[list[str]] = None
    sort_order: Optional[int] = None
    is_main_character: Optional[bool] = None


@app.get("/api/wiki", summary="L蘯･y danh sﾃ｡ch Wiki")
async def get_wiki_entries(
    category: Optional[str] = Query(None, description="L盻皇 theo category"),
    search: Optional[str] = Query(None, description="Tim kiem theo tieu de"),
    page: int = Query(1, ge=1, description="S盻・trang"),
    limit: int = Query(50, ge=1, le=200, description="S盻・lﾆｰ盻｣ng m盻擁 trang"),
):
    """L蘯･y danh sﾃ｡ch t蘯･t c蘯｣ wiki entries, cﾃｳ th盻・l盻皇 theo category ho蘯ｷc tﾃｬm ki蘯ｿm."""
    try:
        offset = (page - 1) * limit
        query = supabase.table("wiki_entries").select("*", count="exact")
        if category:
            query = query.eq("category", category)
        if search:
            query = query.ilike("title", f"%{search}%")
        
        resp = (
            query.order("is_main_character", desc=True)
            .order("sort_order", desc=False, nullsfirst=False)
            .order("category")
            .order("title")
            .range(offset, offset + limit - 1)
            .execute()
        )
        
        total = resp.count or 0
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        
        entries = resp.data or []
        for entry in entries:
            entry["summary"] = sanitize_html(entry.get("summary")) if entry.get("summary") is not None else None
            entry["content"] = sanitize_html(entry.get("content")) if entry.get("content") is not None else None

        return {
            "entries": entries,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wiki/{slug}", summary="L蘯･y chi ti蘯ｿt Wiki entry")
async def get_wiki_entry(slug: str):
    """L蘯･y m盻冲 wiki entry theo slug."""
    try:
        resp = (
            supabase.table("wiki_entries")
            .select("*")
            .eq("slug", slug)
            .single()
            .execute()
        )
        if not resp.data:
            raise HTTPException(status_code=404, detail="Khﾃｴng tﾃｬm th蘯･y entry")
        data = dict(resp.data)
        data["summary"] = sanitize_html(data.get("summary")) if data.get("summary") is not None else None
        data["content"] = sanitize_html(data.get("content")) if data.get("content") is not None else None
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/wiki", summary="T蘯｡o Wiki entry m盻嬖 (Admin)")
async def create_wiki_entry(
    body: WikiEntryIn,
    authorization: Optional[str] = Header(None),
):
    """T蘯｡o wiki entry m盻嬖. Yﾃｪu c蘯ｧu quy盻］ Admin."""
    await verify_admin(authorization)
    try:
        if body.category not in VALID_WIKI_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Category khﾃｴng h盻｣p l盻・ Ch盻肱 trong: {VALID_WIKI_CATEGORIES}")
        data = body.model_dump(exclude_none=True)
        data["summary"] = sanitize_html(data.get("summary")) if data.get("summary") is not None else None
        data["content"] = sanitize_html(data.get("content")) if data.get("content") is not None else None
        result = supabase.table("wiki_entries").insert(data).execute()
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/wiki/{entry_id}", summary="S盻ｭa Wiki entry (Admin)")
async def update_wiki_entry(
    entry_id: str,
    body: WikiEntryIn,
    authorization: Optional[str] = Header(None),
):
    """C蘯ｭp nh蘯ｭt wiki entry theo id. Yﾃｪu c蘯ｧu quy盻］ Admin."""
    await verify_admin(authorization)
    try:
        from datetime import datetime, timezone
        data = body.model_dump(exclude_none=True)
        data["summary"] = sanitize_html(data.get("summary")) if data.get("summary") is not None else None
        data["content"] = sanitize_html(data.get("content")) if data.get("content") is not None else None
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = supabase.table("wiki_entries").update(data).eq("id", entry_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Entry khﾃｴng t盻渡 t蘯｡i")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/wiki/{entry_id}", summary="Xﾃｳa Wiki entry (Admin)")
async def delete_wiki_entry(
    entry_id: str,
    authorization: Optional[str] = Header(None),
):
    """Xﾃｳa wiki entry theo id. Yﾃｪu c蘯ｧu quy盻］ Admin."""
    await verify_admin(authorization)
    try:
        supabase.table("wiki_entries").delete().eq("id", entry_id).execute()
        return {"status": "deleted", "id": entry_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
#   GUIDE PAGES (Hﾆｰ盻嬾g d蘯ｫn s盻ｭ d盻･ng & SOP n盻冓 b盻・
# ============================================================

class GuidePageUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


@app.get("/api/guide/{slug}", summary="L蘯･y trang hﾆｰ盻嬾g d蘯ｫn public")
async def get_public_guide(slug: str):
    """L蘯･y n盻冓 dung trang hﾆｰ盻嬾g d蘯ｫn cﾃｳ scope = 'public'."""
    try:
        result = supabase.table("guide_pages").select("*").eq("slug", slug).eq("scope", "public").execute()
        if not result.data:
            return {"slug": slug, "title": "", "content": "", "scope": "public"}
        data = dict(result.data[0])
        data["content"] = sanitize_html(data.get("content")) or ""
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/guide/{slug}", summary="L蘯･y trang hﾆｰ盻嬾g d蘯ｫn (Admin)")
async def get_admin_guide(
    slug: str,
    authorization: Optional[str] = Header(None),
):
    """L蘯･y n盻冓 dung b蘯･t k盻ｳ trang nﾃo (k盻・c蘯｣ internal). Yﾃｪu c蘯ｧu Admin."""
    await verify_admin(authorization)
    try:
        result = supabase.table("guide_pages").select("*").eq("slug", slug).execute()
        if not result.data:
            return {"slug": slug, "title": "", "content": "", "scope": "internal"}
        data = dict(result.data[0])
        data["content"] = sanitize_html(data.get("content")) or ""
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/admin/guide/{slug}", summary="C蘯ｭp nh蘯ｭt trang hﾆｰ盻嬾g d蘯ｫn (Admin)")
async def update_guide(
    slug: str,
    body: GuidePageUpdate,
    authorization: Optional[str] = Header(None),
):
    """C蘯ｭp nh蘯ｭt ho蘯ｷc t蘯｡o m盻嬖 trang hﾆｰ盻嬾g d蘯ｫn. Yﾃｪu c蘯ｧu Admin."""
    await verify_admin(authorization)
    try:
        from datetime import datetime, timezone
        # Determine scope from slug
        scope = "internal" if slug == "admin-sop" else "public"

        existing = supabase.table("guide_pages").select("id").eq("slug", slug).execute()

        data = body.model_dump(exclude_none=True)
        if "content" in data:
            data["content"] = sanitize_html(data.get("content")) or ""
        data["updated_at"] = datetime.now(timezone.utc).isoformat()

        if existing.data:
            result = supabase.table("guide_pages").update(data).eq("slug", slug).execute()
        else:
            data["slug"] = slug
            data["scope"] = scope
            if "title" not in data:
                data["title"] = "Hướng dẫn" if scope == "public" else "SOP Nội bộ"
            if "content" not in data:
                data["content"] = ""
            result = supabase.table("guide_pages").insert(data).execute()

        return result.data[0] if result.data else {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
