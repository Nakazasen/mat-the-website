"""
FastAPI Backend - Mạt Thế Sinh Hoá Nguy Cơ
Cung cấp API metadata chương. Nội dung chương được fetch từ Cloudflare R2.
"""

import io
import os
import re
import unicodedata
# Force re-deploy to Vercel (Trigger)
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

load_dotenv(override=True)

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


# === ADMIN AUTH (Simple token-based) ===
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "mat-the-admin-2026")


async def verify_admin(authorization: Optional[str]) -> dict:
    """
    Xác thực token Admin từ Header Authorization (Bearer <token>).
    Hỗ trợ cả static ADMIN_TOKEN và Supabase JWT thực tế.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Thiếu token xác thực. Hãy đăng nhập lại."
        )
    
    token = authorization.replace("Bearer ", "").strip()
    
    # 1. Kiểm tra static token (Bypass cho dev hoặc token cứng)
    if token == ADMIN_TOKEN:
        return {"id": "static-admin", "role": "superadmin", "email": "admin@static"}
    
    # 2. Kiểm tra JWT của Supabase
    try:
        # supabase-py Auth client sẽ tự verify JWT
        user_resp = supabase.auth.get_user(token)
        if not user_resp or not user_resp.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token không hợp lệ hoặc đã hết hạn."
            )
        
        # Truy vấn profile để lấy role (editor/superadmin)
        profile_resp = supabase.table("profiles").select("role").eq("id", user_resp.user.id).execute()
        
        user_role = "editor" # Mặc định
        if profile_resp.data:
            user_role = profile_resp.data[0].get("role", "editor")
            
        return {
            "id": user_resp.user.id,
            "email": user_resp.user.email,
            "role": user_role
        }
    except Exception as e:
        print(f"Auth Error: {str(e)}")
        # Trả về chi tiết lỗi để dễ debug
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Token không hợp lệ: {str(e)}"
        )


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
    page: int = Query(1, ge=1, description="Số trang"),
    limit: int = Query(50, ge=1, le=100, description="Số chương mỗi trang"),
    sort: str = Query("asc", pattern="^(asc|desc)$", description="Thứ tự sắp xếp: asc hoặc desc"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tiêu đề hoặc số chương"),
    is_side_story: Optional[bool] = Query(None, description="Lọc ngoại truyện (true) hoặc mạch chính (false)"),
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
    Lấy thông tin metadata của một chương bao gồm URL file R2 chứa nội dung.
    Frontend sẽ dùng content_url này để fetch nội dung thẳng từ Cloudflare CDN.
    
    - **chapter_number**: Số chương thực tế trong truyện
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
    is_side_story: bool = False


class AdminChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_side_story: Optional[bool] = None


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
        "is_side_story": body.is_side_story,
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

    if body.is_side_story is not None:
        update_data["is_side_story"] = body.is_side_story

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
    created_at: str


class AccountInvite(BaseModel):
    email: str
    password: str
    display_name: str
    role: str = "editor"


@app.get("/api/admin/users", response_model=List[Profile], summary="[Admin] Danh sách nhân sự")
async def admin_get_users(authorization: Optional[str] = Header(None)):
    """Lấy danh sách tất cả nhân sự (Profiles). Chỉ dành cho SuperAdmin."""
    user = await verify_admin(authorization)
    
    # Chỉ SuperAdmin mới được xem danh sách nhân sự
    if user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Chỉ SuperAdmin mới có quyền xem danh sách nhân sự")
    
    resp = supabase.table("profiles").select("*").order("created_at", desc=True).execute()
    return resp.data


@app.post("/api/admin/invite", summary="[Admin] Tạo tài khoản nhân sự mới")
async def admin_invite_user(
    body: AccountInvite,
    authorization: Optional[str] = Header(None)
):
    """Tạo tài khoản Auth và Profile mới cho nhân viên. Chỉ dành cho SuperAdmin."""
    user = await verify_admin(authorization)
    
    # Kiểm tra quyền SuperAdmin
    if user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Chỉ SuperAdmin mới có quyền tạo nhân sự mới")
    
    # 1. Tạo user trong hệ thống Auth của Supabase bằng Service Role
    try:
        # auth.admin.create_user cần service_role key
        auth_resp = supabase.auth.admin.create_user({
            "email": body.email,
            "password": body.password,
            "email_confirm": True,
            "user_metadata": {"full_name": body.display_name}
        })
        
        if not auth_resp or not auth_resp.user:
            raise Exception("Supabase không trả về thông tin user mới.")

        # 2. Update role trong bảng profiles
        if body.role != "editor":
            supabase.table("profiles").update({"role": body.role}).eq("id", auth_resp.user.id).execute()
            
        return {"message": "Đã tạo tài khoản thành công", "user_id": auth_resp.user.id}
    except Exception as e:
        error_msg = str(e)
        if "User not allowed" in error_msg:
            detail = "Lỗi: Backend chưa được cấp quyền Admin (Service Role Key). Hãy kiểm tra SUPABASE_KEY."
        else:
            detail = f"Lỗi tạo tài khoản: {error_msg}"
        raise HTTPException(status_code=500, detail=detail)


@app.delete("/api/admin/users/{user_id}", summary="[Admin] Xoá nhân sự")
async def admin_delete_user(
    user_id: str,
    authorization: Optional[str] = Header(None)
):
    """Xoá tài khoản nhân sự. Chỉ dành cho SuperAdmin."""
    user = await verify_admin(authorization)
    
    # Kiểm tra quyền SuperAdmin
    if user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Chỉ SuperAdmin mới có quyền xoá nhân sự")
    
    try:
        # Xoá trong Auth (bảng profiles sẽ tự động xoá do CASCADE)
        supabase.auth.admin.delete_user(user_id)
        return {"message": "Đã xoá nhân sự thành công"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xoá nhân sự: {str(e)}")


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
    """Lấy tất cả các điểm đánh dấu trên bản đồ (Công khai)."""
    resp = supabase.table("map_locations").select("*").order("created_at", desc=True).execute()
    return resp.data


@app.post("/api/admin/map-locations", response_model=MapLocation, summary="[Admin] Tạo điểm bản đồ mới")
async def admin_create_map_location(
    body: AdminMapLocationIn,
    authorization: Optional[str] = Header(None)
):
    """Tạo điểm đánh dấu mới trên bản đồ. Chỉ dành cho Admin."""
    await verify_admin(authorization)
    
    resp = supabase.table("map_locations").insert(body.dict()).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Không thể tạo điểm bản đồ")
    return resp.data[0]


@app.put("/api/admin/map-locations/{location_id}", response_model=MapLocation, summary="[Admin] Cập nhật điểm bản đồ")
async def admin_update_map_location(
    location_id: str,
    body: AdminMapLocationIn,
    authorization: Optional[str] = Header(None)
):
    """Cập nhật thông tin điểm đánh dấu. Chỉ dành cho Admin."""
    await verify_admin(authorization)
    
    resp = supabase.table("map_locations").update(body.dict()).eq("id", location_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Không tìm thấy điểm bản đồ để cập nhật")
    return resp.data[0]


@app.delete("/api/admin/map-locations/{location_id}", summary="[Admin] Xoá điểm bản đồ")
async def admin_delete_map_location(
    location_id: str,
    authorization: Optional[str] = Header(None)
):
    """Xoá điểm đánh dấu khỏi bản đồ. Chỉ dành cho Admin."""
    await verify_admin(authorization)
    
    supabase.table("map_locations").delete().eq("id", location_id).execute()
    return {"message": "Đã xoá điểm bản đồ thành công"}


@app.get("/api/homepage", response_model=HomepageSettings)
async def get_homepage_settings():
    """Lấy cấu hình nội dung hiển thị trên trang chủ."""
    try:
        resp = supabase.table("homepage_settings").select("*").eq("id", 1).single().execute()
        if not resp.data:
            return HomepageSettings(
                warning_title="CẢNH BÁO KHU VỰC CẤM",
                warning_subtitle="BIOSAFETY LEVEL 4 · RESTRICTED ACCESS",
                warning_headline="TRẬN ĐỊA SINH TỬ",
                warning_description="Năm 20XX. Virus Z-79 bùng phát từ một phòng thí nghiệm bí mật...",
                features_title="ĐIỂM NỔI BẬT",
                features_json=[
                    {"icon": "🧟", "title": "Zombie & Dị Biến", "desc": "Nhiều loại zombie với khả năng đặc biệt..."},
                    {"icon": "⚔️", "title": "Chiến Thuật & Sinh Tồn", "desc": "Xây dựng căn cứ, thu thập tài nguyên..."},
                    {"icon": "🔬", "title": "Khoa Học Viễn Tưởng", "desc": "Nghiên cứu virus, nâng cấp cơ thể..."},
                    {"icon": "❤️", "title": "Tình Cảm & Con Người", "desc": "Tình đồng đội, tình yêu..."}
                ]
            )
        return HomepageSettings(**resp.data)
    except Exception:
        # Fallback if table doesn't exist yet
        return HomepageSettings(
            warning_title="CẢNH BÁO KHU VỰC CẤM",
            warning_subtitle="BIOSAFETY LEVEL 4 · RESTRICTED ACCESS",
            warning_headline="TRẬN ĐỊA SINH TỬ",
            warning_description="Năm 20XX. Virus Z-79 bùng phát từ một phòng thí nghiệm bí mật...",
            features_title="ĐIỂM NỔI BẬT",
            features_json=[
                {"icon": "🧟", "title": "Zombie & Dị Biến", "desc": "Nhiều loại zombie với khả năng đặc biệt..."},
                {"icon": "⚔️", "title": "Chiến Thuật & Sinh Tồn", "desc": "Xây dựng căn cứ, thu thập tài nguyên..."},
                {"icon": "🔬", "title": "Khoa Học Viễn Tưởng", "desc": "Nghiên cứu virus, nâng cấp cơ thể..."},
                {"icon": "❤️", "title": "Tình Cảm & Con Người", "desc": "Tình đồng đội, tình yêu..."}
            ]
        )


@app.put("/api/admin/homepage", summary="[Admin] Cập nhật cấu hình trang chủ")
async def admin_update_homepage(
    body: HomepageSettings,
    authorization: Optional[str] = Header(None),
):
    """Cập nhật các đoạn text và cấu hình trên trang chủ."""
    await verify_admin(authorization)
    
    data = body.model_dump(exclude_none=True)
    data["id"] = 1
    data["updated_at"] = "now()"
    
    result = supabase.table("homepage_settings").upsert(data).execute()
    return {"message": "Cập nhật trang chủ thành công", "settings": result.data[0] if result.data else data}


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


# === COMMENT ROUTES ===

class CommentCreate(BaseModel):
    user_name: str
    content: str


class Comment(BaseModel):
    id: str
    chapter_number: int
    user_name: str
    content: str
    created_at: str


@app.post("/api/chapters/{chapter_number}/comments", summary="Gửi bình luận mới")
async def create_comment(chapter_number: int, body: CommentCreate):
    """Gửi một bình luận ẩn danh cho chương."""
    try:
        data = {
            "chapter_number": chapter_number,
            "user_name": body.user_name or "Ẩn danh",
            "content": body.content
        }
        result = supabase.table("comments").insert(data).execute()
        return {"status": "success", "comment": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chapters/{chapter_number}/comments", summary="Lấy danh sách bình luận")
async def get_comments(chapter_number: int, limit: int = 50):
    """Lấy danh sách bình luận của một chương, chương mới nhất lên đầu."""
    try:
        resp = (
            supabase.table("comments")
            .select("*")
            .eq("chapter_number", chapter_number)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# LIKE SYSTEM
# ============================================================

@app.post("/api/chapters/{chapter_number}/like", summary="Thả tim cho chương")
async def like_chapter(chapter_number: int):
    """Tăng likes_count của chương lên 1."""
    try:
        # Fetch current like count
        resp = (
            supabase.table("chapters")
            .select("id, likes_count")
            .eq("chapter_number", chapter_number)
            .single()
            .execute()
        )
        if not resp.data:
            raise HTTPException(status_code=404, detail="Chương không tồn tại")

        current_likes = resp.data.get("likes_count") or 0
        chapter_id = resp.data["id"]

        # Increment
        supabase.table("chapters").update(
            {"likes_count": current_likes + 1}
        ).eq("id", chapter_id).execute()

        return {"status": "ok", "likes_count": current_likes + 1}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# IMAGE UPLOAD (CLOUDFLARE R2)
# ============================================================

@app.post("/api/upload/image", summary="Upload ảnh lên Cloudflare R2 (Admin)")
async def upload_image(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """Upload ảnh phục vụ cho Editor/Wiki. Yêu cầu quyền Admin."""
    await verify_admin(authorization)
    
    if not r2_client:
        raise HTTPException(status_code=500, detail="Cấu hình Cloudflare R2 chưa hoàn chỉnh")
        
    try:
        import uuid
        from datetime import datetime
        
        # Validate file type
        valid_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in valid_types:
            raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file ảnh (JPG, PNG, GIF, WEBP)")
            
        # Generate unique filename
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'png'
        date_str = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"uploads/{date_str}_{unique_id}.{ext}"
        
        # Read file
        contents = await file.read()
        
        # Upload to R2
        r2_client.put_object(
            Bucket=R2_BUCKET,
            Key=filename,
            Body=contents,
            ContentType=file.content_type
        )
        
        # Return URL
        # Đảm bảo R2_PUBLIC_URL không kết thúc bằng /
        base_url = R2_PUBLIC_URL.rstrip('/')
        public_url = f"{base_url}/{filename}"
        return {"url": public_url}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# WIKI - BÁCH KHOA TOÀN THƯ
# ============================================================

VALID_WIKI_CATEGORIES = ["Nhân vật", "Sinh vật", "Thế lực", "Vật phẩm", "Địa điểm"]


class WikiEntryOut(BaseModel):
    id: str
    title: str
    category: str
    slug: str
    summary: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[list[str]] = None
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


@app.get("/api/wiki", summary="Lấy danh sách Wiki")
async def get_wiki_entries(
    category: Optional[str] = Query(None, description="Lọc theo category"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tiêu đề"),
    limit: int = Query(50, ge=1, le=200),
):
    """Lấy danh sách tất cả wiki entries, có thể lọc theo category hoặc tìm kiếm."""
    try:
        query = supabase.table("wiki_entries").select("*")
        if category:
            query = query.eq("category", category)
        if search:
            query = query.ilike("title", f"%{search}%")
        resp = query.order("category").order("title").limit(limit).execute()
        return resp.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wiki/{slug}", summary="Lấy chi tiết Wiki entry")
async def get_wiki_entry(slug: str):
    """Lấy một wiki entry theo slug."""
    try:
        resp = (
            supabase.table("wiki_entries")
            .select("*")
            .eq("slug", slug)
            .single()
            .execute()
        )
        if not resp.data:
            raise HTTPException(status_code=404, detail="Không tìm thấy entry")
        return resp.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/wiki", summary="Tạo Wiki entry mới (Admin)")
async def create_wiki_entry(
    body: WikiEntryIn,
    authorization: Optional[str] = Header(None),
):
    """Tạo wiki entry mới. Yêu cầu quyền Admin."""
    await verify_admin(authorization)
    try:
        if body.category not in VALID_WIKI_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Category không hợp lệ. Chọn trong: {VALID_WIKI_CATEGORIES}")
        data = body.model_dump(exclude_none=True)
        result = supabase.table("wiki_entries").insert(data).execute()
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/wiki/{entry_id}", summary="Sửa Wiki entry (Admin)")
async def update_wiki_entry(
    entry_id: str,
    body: WikiEntryIn,
    authorization: Optional[str] = Header(None),
):
    """Cập nhật wiki entry theo id. Yêu cầu quyền Admin."""
    await verify_admin(authorization)
    try:
        from datetime import datetime, timezone
        data = body.model_dump(exclude_none=True)
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = supabase.table("wiki_entries").update(data).eq("id", entry_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Entry không tồn tại")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/wiki/{entry_id}", summary="Xóa Wiki entry (Admin)")
async def delete_wiki_entry(
    entry_id: str,
    authorization: Optional[str] = Header(None),
):
    """Xóa wiki entry theo id. Yêu cầu quyền Admin."""
    await verify_admin(authorization)
    try:
        supabase.table("wiki_entries").delete().eq("id", entry_id).execute()
        return {"status": "deleted", "id": entry_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
#   GUIDE PAGES (Hướng dẫn sử dụng & SOP nội bộ)
# ============================================================

class GuidePageUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


@app.get("/api/guide/{slug}", summary="Lấy trang hướng dẫn public")
async def get_public_guide(slug: str):
    """Lấy nội dung trang hướng dẫn có scope = 'public'."""
    try:
        result = supabase.table("guide_pages").select("*").eq("slug", slug).eq("scope", "public").execute()
        if not result.data:
            return {"slug": slug, "title": "", "content": "", "scope": "public"}
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/guide/{slug}", summary="Lấy trang hướng dẫn (Admin)")
async def get_admin_guide(
    slug: str,
    authorization: Optional[str] = Header(None),
):
    """Lấy nội dung bất kỳ trang nào (kể cả internal). Yêu cầu Admin."""
    await verify_admin(authorization)
    try:
        result = supabase.table("guide_pages").select("*").eq("slug", slug).execute()
        if not result.data:
            return {"slug": slug, "title": "", "content": "", "scope": "internal"}
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/admin/guide/{slug}", summary="Cập nhật trang hướng dẫn (Admin)")
async def update_guide(
    slug: str,
    body: GuidePageUpdate,
    authorization: Optional[str] = Header(None),
):
    """Cập nhật hoặc tạo mới trang hướng dẫn. Yêu cầu Admin."""
    await verify_admin(authorization)
    try:
        from datetime import datetime, timezone
        # Determine scope from slug
        scope = "internal" if slug == "admin-sop" else "public"

        existing = supabase.table("guide_pages").select("id").eq("slug", slug).execute()

        data = body.model_dump(exclude_none=True)
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
