"""
FastAPI Backend - M蘯｡t Th蘯ｿ Sinh Hoﾃ｡ Nguy Cﾆ｡
Cung c蘯･p API metadata chﾆｰﾆ｡ng. N盻冓 dung chﾆｰﾆ｡ng ﾄ柁ｰ盻｣c fetch t盻ｫ Cloudflare R2.
"""

import io
import hashlib
import json
import os
import re
import unicodedata
from datetime import datetime, timezone
# Force re-deploy to Vercel and Render (Trigger: 2026-03-25 23:14)
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
# Add both current and parent directory to sys.path for maximum compatibility
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Consolidated imports with intelligent fallback
try:
    # Try importing as top-level modules first (when running from within backend/)
    from security_utils import sanitize_html, sanitize_plaintext, extract_bearer_token
    from routes.engagement import create_engagement_router
    from routes.hq_dashboard import router as hq_router
    from routes.ai_oracle import router as oracle_router
    from routes.wiki_search import router as wiki_router
except (ImportError, ModuleNotFoundError):
    # Fallback to absolute imports (when running from project root)
    from backend.security_utils import sanitize_html, sanitize_plaintext, extract_bearer_token
    from backend.routes.engagement import create_engagement_router
    from backend.routes.hq_dashboard import router as hq_router
    from backend.routes.ai_oracle import router as oracle_router
    from backend.routes.wiki_search import router as wiki_router


load_dotenv(override=True)

# === SUPABASE CLIENT ===
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be configured in .env")

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


SUPPORTED_LOCALES = ("vi", "en", "zh-CN", "ja")
DEFAULT_LOCALE = "vi"
TRANSLATION_GLOSSARY_PATH = os.path.join(current_dir, "translation_glossary.json")
DEFAULT_TRANSLATION_MODELS = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemma-3-27b-it",
    "gemma-3-12b-it",
    "gemma-3-4b-it",
    "gemma-3n-e2b-it",
    "gemma-3n-1b-it",
    "gemini-robotics-er-1.5-preview",
]
TRANSLATION_MODEL_FALLBACK = DEFAULT_TRANSLATION_MODELS[0]


def normalize_locale(value: Optional[str]) -> str:
    if not value:
        return DEFAULT_LOCALE
    if value in SUPPORTED_LOCALES:
        return value
    lowered = value.lower()
    if lowered.startswith("vi"):
        return "vi"
    if lowered.startswith("en"):
        return "en"
    if lowered.startswith("zh"):
        return "zh-CN"
    if lowered.startswith("ja"):
        return "ja"
    return DEFAULT_LOCALE


def safe_select(table_name: str, select_fields: str = "*"):
    try:
        return supabase.table(table_name).select(select_fields)
    except Exception:
        return None


def build_content_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def load_translation_glossary() -> list[dict]:
    try:
        with open(TRANSLATION_GLOSSARY_PATH, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
            if isinstance(payload, list):
                return payload
    except Exception:
        pass
    return []


def build_glossary_prompt() -> str:
    glossary = load_translation_glossary()
    if not glossary:
        return "Khong co glossary bo sung."

    lines = []
    for item in glossary:
        source = item.get("source", "").strip()
        if not source:
            continue
        translations = item.get("translations", {})
        if not isinstance(translations, dict):
            continue
        mapped = ", ".join(f"{k}={v}" for k, v in translations.items() if v)
        if mapped:
            lines.append(f"- {source}: {mapped}")
    return "\n".join(lines) if lines else "Khong co glossary bo sung."


def extract_r2_object_key(content_url: str) -> Optional[str]:
    if not content_url or not R2_PUBLIC_URL:
        return None
    clean_url = re.sub(r'^https?://', '', content_url)
    clean_base = re.sub(r'^https?://', '', R2_PUBLIC_URL)
    return clean_url.replace(clean_base, "").lstrip("/")


def fetch_r2_content(content_url: str) -> str:
    object_key = extract_r2_object_key(content_url)
    if object_key and r2_client:
        response = r2_client.get_object(Bucket=R2_BUCKET, Key=object_key)
        return response["Body"].read().decode("utf-8")

    response = httpx.get(content_url, timeout=20.0)
    response.raise_for_status()
    return response.text


def resolve_chapter_translation(chapter_id: int, locale: str):
    locale = normalize_locale(locale)
    if locale == DEFAULT_LOCALE:
        return None
    try:
        result = (
            supabase.table("chapter_translations")
            .select("*")
            .eq("chapter_id", chapter_id)
            .eq("locale", locale)
            .eq("translation_status", "published")
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
    except Exception:
        return None
    return None


def resolve_novel_translation(locale: str):
    locale = normalize_locale(locale)
    if locale == DEFAULT_LOCALE:
        return None
    try:
        result = (
            supabase.table("novel_settings_translations")
            .select("*")
            .eq("novel_settings_id", 1)
            .eq("locale", locale)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
    except Exception:
        return None
    return None


def normalize_model_catalog(raw_catalog, fallback_model: str) -> list[str]:
    if isinstance(raw_catalog, list):
        catalog = [f"{item}".strip() for item in raw_catalog if f"{item}".strip()]
    else:
        catalog = []
    if fallback_model and fallback_model not in catalog:
        catalog.insert(0, fallback_model)
    if not catalog:
        catalog = DEFAULT_TRANSLATION_MODELS.copy()
    else:
        catalog.extend(DEFAULT_TRANSLATION_MODELS)
    return list(dict.fromkeys(catalog))


def normalize_api_key_catalog(raw_keys, fallback_key: str) -> list[str]:
    keys = []
    if isinstance(raw_keys, list):
        keys.extend(f"{item}".strip() for item in raw_keys if f"{item}".strip())
    if fallback_key and fallback_key.strip():
        keys.insert(0, fallback_key.strip())
    return list(dict.fromkeys([item for item in keys if item]))


def is_translation_retryable(exc: HTTPException) -> bool:
    detail = str(exc.detail).lower()
    return (
        exc.status_code == 429
        or "resource exhausted" in detail
        or "rate limit" in detail
        or "quota" in detail
        or exc.status_code in (400, 404, 401, 403)
    )


def resolve_homepage_translation(locale: str):
    locale = normalize_locale(locale)
    if locale == DEFAULT_LOCALE:
        return None
    try:
        result = (
            supabase.table("homepage_settings_translations")
            .select("*")
            .eq("homepage_settings_id", 1)
            .eq("locale", locale)
            .eq("translation_status", "published")
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
    except Exception:
        return None
    return None


def resolve_wiki_translation(entry_id: str, locale: str):
    locale = normalize_locale(locale)
    if locale == DEFAULT_LOCALE:
        return None
    try:
        result = (
            supabase.table("wiki_entry_translations")
            .select("*")
            .eq("wiki_entry_id", entry_id)
            .eq("locale", locale)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
    except Exception:
        return None
    return None


def apply_wiki_translation(entry: dict, locale: str) -> dict:
    translation = resolve_wiki_translation(entry.get("id"), locale)
    resolved_locale = DEFAULT_LOCALE
    is_fallback = False
    if translation:
        if translation.get("title"):
            entry["title"] = translation["title"]
        if translation.get("summary"):
            entry["summary"] = translation["summary"]
        if translation.get("content"):
            entry["content"] = translation["content"]
        resolved_locale = normalize_locale(locale)
    elif normalize_locale(locale) != DEFAULT_LOCALE:
        is_fallback = True

    entry["requested_locale"] = normalize_locale(locale)
    entry["resolved_locale"] = resolved_locale
    entry["is_fallback"] = is_fallback
    return entry


def sanitize_homepage_features(features) -> list[dict]:
    cleaned = []
    if not isinstance(features, list):
        return cleaned

    for item in features:
        if not isinstance(item, dict):
            continue
        cleaned.append(
            {
                "icon": str(item.get("icon") or "").strip(),
                "title": sanitize_plaintext(str(item.get("title") or "")),
                "desc": sanitize_plaintext(str(item.get("desc") or "")),
            }
        )
    return cleaned


def prepare_homepage_settings_payload(payload: Optional[dict]) -> dict:
    raw = dict(payload or {})
    return {
        "warning_title": sanitize_plaintext(raw.get("warning_title")) if raw.get("warning_title") is not None else None,
        "warning_subtitle": sanitize_plaintext(raw.get("warning_subtitle")) if raw.get("warning_subtitle") is not None else None,
        "warning_headline": sanitize_plaintext(raw.get("warning_headline")) if raw.get("warning_headline") is not None else None,
        "warning_description": sanitize_html(raw.get("warning_description")) if raw.get("warning_description") is not None else "",
        "features_title": sanitize_plaintext(raw.get("features_title")) if raw.get("features_title") is not None else None,
        "features_json": sanitize_homepage_features(raw.get("features_json")),
    }


def apply_homepage_translation(payload: dict, locale: str) -> dict:
    requested_locale = normalize_locale(locale)
    resolved_locale = DEFAULT_LOCALE
    is_fallback = False

    translation = resolve_homepage_translation(requested_locale)
    if translation:
        for key in (
            "warning_title",
            "warning_subtitle",
            "warning_headline",
            "warning_description",
            "features_title",
            "features_json",
        ):
            if translation.get(key) is not None:
                payload[key] = translation.get(key)
        payload = prepare_homepage_settings_payload(payload)
        resolved_locale = requested_locale
    elif requested_locale != DEFAULT_LOCALE:
        is_fallback = True

    payload["requested_locale"] = requested_locale
    payload["resolved_locale"] = resolved_locale
    payload["is_fallback"] = is_fallback
    return payload


async def resolve_ai_settings_for_translation() -> tuple[str, list[str], list[str]]:
    try:
        settings = (
            supabase.table("novel_settings")
            .select("ai_model_name, ai_model_catalog, ai_api_key, ai_api_keys")
            .eq("id", 1)
            .single()
            .execute()
        )
        if settings.data:
            model_name = settings.data.get("ai_model_name") or TRANSLATION_MODEL_FALLBACK
            api_key = settings.data.get("ai_api_key") or os.getenv("GEMINI_API_KEY", "")
            return (
                model_name,
                normalize_model_catalog(settings.data.get("ai_model_catalog"), model_name),
                normalize_api_key_catalog(settings.data.get("ai_api_keys"), api_key),
            )
    except Exception:
        pass
    fallback_key = os.getenv("GEMINI_API_KEY", "")
    return (
        TRANSLATION_MODEL_FALLBACK,
        DEFAULT_TRANSLATION_MODELS.copy(),
        normalize_api_key_catalog([], fallback_key),
    )


async def translate_text_with_ai(source_text: str, source_locale: str, target_locale: str, context_label: str) -> str:
    _active_model, model_catalog, api_keys = await resolve_ai_settings_for_translation()
    if not api_keys:
        raise HTTPException(status_code=503, detail="AI translation is not configured")

    glossary_prompt = build_glossary_prompt()
    prompt = f"""
Ban la bien dich vien chuyen nghiep cho tieu thuyet sinh ton hau tan the.
Hay dich noi dung sau tu {source_locale} sang {target_locale}.

YEU CAU:
1. Giu nguyen ten rieng theo glossary neu co.
2. Khong duoc rut gon, khong them giai thich, khong them markdown.
3. Giu nguyen ngat doan va thu tu noi dung.
4. Neu gap ky hieu hoac ten ky nang, uu tien nhat quan hon viet dep.
5. Chi tra ve ban dich sau cung.

CONTEXT: {context_label}

GLOSSARY:
{glossary_prompt}

SOURCE:
{source_text}
""".strip()

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.3},
    }

    last_error: Optional[HTTPException] = None
    async with httpx.AsyncClient(timeout=60.0) as client:
        for api_key in api_keys:
            for model_name in model_catalog:
                gemini_url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{model_name}:generateContent?key={api_key}"
                )
                response = await client.post(gemini_url, json=payload)
                if response.is_success:
                    data = response.json()
                    try:
                        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    except Exception as exc:
                        raise HTTPException(status_code=502, detail=f"Invalid translation response: {exc}")

                last_error = HTTPException(
                    status_code=response.status_code,
                    detail=f"Translation API error: {response.text}",
                )
                if not is_translation_retryable(last_error):
                    raise last_error

    if last_error:
        raise last_error
    raise HTTPException(status_code=502, detail="No translation model available")


async def upsert_chapter_translation(chapter_row: dict, title: str, content: str, locale: str):
    if normalize_locale(locale) == DEFAULT_LOCALE:
        return None

    translated_title = await translate_text_with_ai(title, DEFAULT_LOCALE, locale, f"chapter-title-{chapter_row['chapter_number']}")
    translated_content = await translate_text_with_ai(content, DEFAULT_LOCALE, locale, f"chapter-content-{chapter_row['chapter_number']}")
    payload = {
        "chapter_id": chapter_row["id"],
        "locale": locale,
        "title": translated_title,
        "content": translated_content,
        "summary": translated_content[:280],
        "translation_status": "published",
        "translation_source": "ai",
        "translated_at": datetime.now(timezone.utc).isoformat(),
        "content_hash": build_content_hash(content),
    }
    try:
        return supabase.table("chapter_translations").upsert(payload, on_conflict="chapter_id,locale").execute()
    except Exception:
        return None


async def upsert_homepage_translation(settings_payload: dict, locale: str):
    locale = normalize_locale(locale)
    if locale == DEFAULT_LOCALE:
        return None

    base_payload = prepare_homepage_settings_payload(settings_payload)
    translated_features = []
    for index, feature in enumerate(base_payload.get("features_json") or []):
        translated_features.append(
            {
                "icon": feature.get("icon", ""),
                "title": await translate_text_with_ai(feature.get("title", ""), DEFAULT_LOCALE, locale, f"homepage-feature-title-{index}")
                if feature.get("title")
                else "",
                "desc": await translate_text_with_ai(feature.get("desc", ""), DEFAULT_LOCALE, locale, f"homepage-feature-desc-{index}")
                if feature.get("desc")
                else "",
            }
        )

    source_hash = build_content_hash(json.dumps(base_payload, ensure_ascii=False, sort_keys=True))
    payload = {
        "homepage_settings_id": 1,
        "locale": locale,
        "warning_title": await translate_text_with_ai(base_payload.get("warning_title", ""), DEFAULT_LOCALE, locale, "homepage-warning-title")
        if base_payload.get("warning_title")
        else "",
        "warning_subtitle": await translate_text_with_ai(base_payload.get("warning_subtitle", ""), DEFAULT_LOCALE, locale, "homepage-warning-subtitle")
        if base_payload.get("warning_subtitle")
        else "",
        "warning_headline": await translate_text_with_ai(base_payload.get("warning_headline", ""), DEFAULT_LOCALE, locale, "homepage-warning-headline")
        if base_payload.get("warning_headline")
        else "",
        "warning_description": await translate_text_with_ai(base_payload.get("warning_description", ""), DEFAULT_LOCALE, locale, "homepage-warning-description")
        if base_payload.get("warning_description")
        else "",
        "features_title": await translate_text_with_ai(base_payload.get("features_title", ""), DEFAULT_LOCALE, locale, "homepage-features-title")
        if base_payload.get("features_title")
        else "",
        "features_json": translated_features,
        "translation_status": "published",
        "translation_source": "ai",
        "translated_at": datetime.now(timezone.utc).isoformat(),
        "content_hash": source_hash,
    }

    try:
        return (
            supabase.table("homepage_settings_translations")
            .upsert(payload, on_conflict="homepage_settings_id,locale")
            .execute()
        )
    except Exception:
        return None


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
    requested_locale: str = DEFAULT_LOCALE
    resolved_locale: str = DEFAULT_LOCALE
    is_fallback: bool = False
    translated_title: Optional[str] = None
    translated_content: Optional[str] = None

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
    locale: str = Query(DEFAULT_LOCALE, description="Requested locale"),
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

        requested_locale = normalize_locale(locale)
        chapters = []
        for row in resp.data:
            chapter_payload = dict(row)
            translation = resolve_chapter_translation(chapter_payload["id"], requested_locale)
            chapter_payload["requested_locale"] = requested_locale
            chapter_payload["resolved_locale"] = requested_locale if translation else DEFAULT_LOCALE
            chapter_payload["is_fallback"] = requested_locale != DEFAULT_LOCALE and translation is None
            if translation:
                chapter_payload["title"] = translation.get("title") or chapter_payload["title"]
                chapter_payload["translated_title"] = translation.get("title")
            chapters.append(Chapter(**chapter_payload))
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
async def get_chapter(
    chapter_number: int,
    locale: str = Query(DEFAULT_LOCALE, description="Requested locale"),
):
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

        requested_locale = normalize_locale(locale)
        chapter_payload = dict(resp.data)
        chapter_payload["requested_locale"] = requested_locale
        chapter_payload["resolved_locale"] = DEFAULT_LOCALE
        chapter_payload["translated_title"] = chapter_payload["title"]

        translation = resolve_chapter_translation(chapter_payload["id"], requested_locale)
        if translation:
            chapter_payload["translated_title"] = translation.get("title") or chapter_payload["title"]
            chapter_payload["translated_content"] = translation.get("content")
            chapter_payload["title"] = chapter_payload["translated_title"]
            chapter_payload["resolved_locale"] = requested_locale
            chapter_payload["is_fallback"] = False
        else:
            try:
                chapter_payload["translated_content"] = fetch_r2_content(chapter_payload["content_url"])
            except Exception:
                chapter_payload["translated_content"] = None
            chapter_payload["is_fallback"] = requested_locale != DEFAULT_LOCALE

        return Chapter(**chapter_payload)

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


class ChapterTtsRequest(BaseModel):
    chapter_id: int
    locale: str = DEFAULT_LOCALE
    voice: Optional[str] = None


@app.post("/api/tts/chapter", summary="Prepare chapter TTS metadata")
async def prepare_chapter_tts(body: ChapterTtsRequest):
    locale = normalize_locale(body.locale)
    chapter_resp = (
        supabase.table("chapters")
        .select("id, chapter_number, title, content_url")
        .eq("id", body.chapter_id)
        .single()
        .execute()
    )
    if not chapter_resp.data:
        raise HTTPException(status_code=404, detail="Chapter not found")

    chapter_row = chapter_resp.data
    translation = resolve_chapter_translation(chapter_row["id"], locale)
    resolved_locale = locale if translation else DEFAULT_LOCALE
    content_text = translation.get("content") if translation else fetch_r2_content(chapter_row["content_url"])
    content_hash = build_content_hash(content_text)
    audio_url = f"/api/tts?lang={resolved_locale}&text={quote((content_text or '')[:200])}"
    cached = False

    try:
        existing = (
            supabase.table("tts_audio_cache")
            .select("audio_url")
            .eq("entity_type", "chapter")
            .eq("entity_id", body.chapter_id)
            .eq("locale", resolved_locale)
            .eq("voice", body.voice or "default")
            .eq("content_hash", content_hash)
            .limit(1)
            .execute()
        )
        if existing.data:
            cached = True
            audio_url = existing.data[0].get("audio_url") or audio_url
        else:
            supabase.table("tts_audio_cache").upsert(
                {
                    "entity_type": "chapter",
                    "entity_id": body.chapter_id,
                    "locale": resolved_locale,
                    "voice": body.voice or "default",
                    "provider": "google-translate-tts",
                    "content_hash": content_hash,
                    "audio_url": audio_url,
                },
                on_conflict="entity_type,entity_id,locale,voice,content_hash",
            ).execute()
    except Exception:
        pass

    return {
        "chapter_id": body.chapter_id,
        "requested_locale": locale,
        "resolved_locale": resolved_locale,
        "cached": cached,
        "audio_url": audio_url,
        "content_hash": content_hash,
    }


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
    user = await verify_admin(authorization)

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


@app.post("/api/admin/chapters/{chapter_number}/translate", summary="[Admin] Translate chapter to EN/ZH-CN/JA")
async def admin_translate_chapter(
    chapter_number: int,
    authorization: Optional[str] = Header(None),
):
    await verify_admin(authorization)

    chapter_resp = (
        supabase.table("chapters")
        .select("*")
        .eq("chapter_number", chapter_number)
        .single()
        .execute()
    )
    if not chapter_resp.data:
        raise HTTPException(status_code=404, detail="Chapter not found")

    chapter_row = chapter_resp.data
    content_text = fetch_r2_content(chapter_row["content_url"])
    translated_locales = []
    failed_translations = []
    for locale_code in ("en", "zh-CN", "ja"):
        await upsert_chapter_translation(chapter_row, chapter_row["title"], content_text, locale_code)
        translated_locales.append(locale_code)

    return {
        "message": "Chapter translated",
        "chapter_number": chapter_number,
        "translated_locales": translated_locales,
        "failed_translations": failed_translations,
    }


class AdminBatchTranslateRequest(BaseModel):
    start_chapter: int = 1
    end_chapter: int
    only_missing: bool = True


@app.post("/api/admin/chapters/translate-batch", summary="[Admin] Batch translate chapters to EN/ZH-CN/JA")
async def admin_translate_chapters_batch(
    body: AdminBatchTranslateRequest,
    authorization: Optional[str] = Header(None),
):
    await verify_admin(authorization)

    start_chapter = max(1, body.start_chapter)
    end_chapter = max(start_chapter, body.end_chapter)

    chapters_resp = (
        supabase.table("chapters")
        .select("*")
        .gte("chapter_number", start_chapter)
        .lte("chapter_number", end_chapter)
        .order("chapter_number")
        .execute()
    )
    chapter_rows = chapters_resp.data or []
    if not chapter_rows:
        raise HTTPException(status_code=404, detail="No chapters found in selected range")

    translation_map: dict[int, set[str]] = {}
    if body.only_missing:
        translation_resp = (
            supabase.table("chapter_translations")
            .select("chapter_id, locale, translation_status")
            .eq("translation_status", "published")
            .in_("chapter_id", [row["id"] for row in chapter_rows])
            .execute()
        )
        for row in (translation_resp.data or []):
            translation_map.setdefault(row["chapter_id"], set()).add(row["locale"])

    translated_chapters = []
    skipped_chapters = []
    failed_chapters = []

    for chapter_row in chapter_rows:
        needed_locales = ["en", "zh-CN", "ja"]
        if body.only_missing:
            existing_locales = translation_map.get(chapter_row["id"], set())
            needed_locales = [locale_code for locale_code in needed_locales if locale_code not in existing_locales]
            if not needed_locales:
                skipped_chapters.append(chapter_row["chapter_number"])
                continue

        try:
            content_text = fetch_r2_content(chapter_row["content_url"])
            completed_locales = []
            for locale_code in needed_locales:
                await upsert_chapter_translation(chapter_row, chapter_row["title"], content_text, locale_code)
                completed_locales.append(locale_code)
            translated_chapters.append(
                {
                    "chapter_number": chapter_row["chapter_number"],
                    "translated_locales": completed_locales,
                }
            )
        except HTTPException as exc:
            failed_chapters.append(
                {
                    "chapter_number": chapter_row["chapter_number"],
                    "status_code": exc.status_code,
                    "detail": str(exc.detail),
                }
            )
        except Exception as exc:
            failed_chapters.append(
                {
                    "chapter_number": chapter_row["chapter_number"],
                    "status_code": 500,
                    "detail": str(exc),
                }
            )

    return {
        "message": "Batch chapter translation completed",
        "range": {"start_chapter": start_chapter, "end_chapter": end_chapter},
        "only_missing": body.only_missing,
        "translated_count": len(translated_chapters),
        "skipped_count": len(skipped_chapters),
        "failed_count": len(failed_chapters),
        "translated_chapters": translated_chapters,
        "skipped_chapters": skipped_chapters,
        "failed_chapters": failed_chapters,
    }


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
    ai_model_name: str = TRANSLATION_MODEL_FALLBACK
    ai_model_catalog: list[str] = DEFAULT_TRANSLATION_MODELS.copy()
    ai_api_keys_count: int = 0
    has_ai_key: bool = False  # Frontend diagnostic
    requested_locale: str = DEFAULT_LOCALE
    resolved_locale: str = DEFAULT_LOCALE
    is_fallback: bool = False


class AdminNovelUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    status: Optional[str] = None
    genres: Optional[list[str]] = None
    donate_qr_url: Optional[str] = None
    ai_model_name: Optional[str] = None
    ai_model_catalog: Optional[list[str]] = None
    ai_api_key: Optional[str] = None
    ai_api_keys: Optional[list[str]] = None


@app.get("/api/novel", response_model=NovelSettings)
async def get_novel_settings(locale: str = Query(DEFAULT_LOCALE, description="Requested locale")):
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
            "total_likes": total_likes,
            "ai_model_catalog": DEFAULT_TRANSLATION_MODELS.copy(),
            "ai_api_keys_count": 0,
        }

        requested_locale = normalize_locale(locale)

        if not resp.data:
            default_settings["requested_locale"] = requested_locale
            default_settings["resolved_locale"] = DEFAULT_LOCALE
            default_settings["is_fallback"] = requested_locale != DEFAULT_LOCALE
            return NovelSettings(**default_settings)
        
        # Merge data
        model_fields = NovelSettings.__fields__.keys()
        final_data = {k: v for k, v in resp.data.items() if k in model_fields}
        final_data["description"] = sanitize_html(final_data.get("description")) or ""
        final_data["total_chapters"] = total_chapters
        final_data["max_chapter"] = max_chapter
        final_data["total_views"] = total_views
        final_data["total_likes"] = total_likes
        final_data["ai_model_name"] = resp.data.get("ai_model_name", TRANSLATION_MODEL_FALLBACK)
        final_data["ai_model_catalog"] = normalize_model_catalog(resp.data.get("ai_model_catalog"), final_data["ai_model_name"])
        key_catalog = normalize_api_key_catalog(resp.data.get("ai_api_keys"), resp.data.get("ai_api_key") or "")
        final_data["ai_api_keys_count"] = len(key_catalog)
        final_data["requested_locale"] = requested_locale
        final_data["resolved_locale"] = DEFAULT_LOCALE
        final_data["is_fallback"] = False

        translation = resolve_novel_translation(requested_locale)
        if translation:
            if translation.get("title"):
                final_data["title"] = translation["title"]
            if translation.get("description"):
                final_data["description"] = translation["description"]
            final_data["resolved_locale"] = requested_locale
        elif requested_locale != DEFAULT_LOCALE:
            final_data["is_fallback"] = True
        
        # Security: Never return the actual API key to the frontend
        db_key = resp.data.get("ai_api_key")
        final_data["has_ai_key"] = bool(key_catalog or (db_key and len(db_key) > 5))
        if "ai_api_key" in final_data:
            del final_data["ai_api_key"]
        if "ai_api_keys" in final_data:
            del final_data["ai_api_keys"]
        
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
            ai_model_name=TRANSLATION_MODEL_FALLBACK,
            ai_model_catalog=DEFAULT_TRANSLATION_MODELS.copy(),
            ai_api_keys_count=0,
            requested_locale=normalize_locale(locale),
            resolved_locale=DEFAULT_LOCALE,
            is_fallback=normalize_locale(locale) != DEFAULT_LOCALE,
        )


@app.put("/api/admin/novel", summary="[Admin] Cập nhật thông tin truyện & cấu hình hệ thống")
async def admin_update_novel(
    body: AdminNovelUpdate,
    authorization: Optional[str] = Header(None),
):
    """Cập nhật các thông tin chung của truyện và cấu hình AI."""
    user = await verify_admin(authorization)
    
    data = body.model_dump(exclude_none=True)
    if not data:
        return {"message": "Không có gì thay đổi"}
    
    if "description" in data:
        data["description"] = sanitize_html(data.get("description")) or ""

    ai_fields = {"ai_model_name", "ai_model_catalog", "ai_api_key", "ai_api_keys"}
    if any(field in data for field in ai_fields) and user.get("role") != "superadmin":
        raise HTTPException(
            status_code=403,
            detail="Only superadmin can update AI model or API key.",
        )

    if "ai_model_catalog" in data:
        data["ai_model_catalog"] = normalize_model_catalog(
            data.get("ai_model_catalog"),
            data.get("ai_model_name") or TRANSLATION_MODEL_FALLBACK,
        )

    if "ai_api_keys" in data:
        normalized_keys = normalize_api_key_catalog(data.get("ai_api_keys"), data.get("ai_api_key") or "")
        data["ai_api_keys"] = normalized_keys
        if normalized_keys:
            data["ai_api_key"] = normalized_keys[0]

    # Update novel settings (ID 1)
    # Do not return raw API keys to the admin frontend.
    result = supabase.table("novel_settings").upsert({**data, "id": 1}).execute()
    saved_row = result.data[0] if result.data else {"id": 1, **data}
    key_catalog = normalize_api_key_catalog(saved_row.get("ai_api_keys"), saved_row.get("ai_api_key") or "")
    return {
        "message": "C蘯ｭp nh蘯ｭt thﾃnh cﾃｴng",
        "data": {
            "id": saved_row.get("id", 1),
            "title": saved_row.get("title"),
            "author": saved_row.get("author"),
            "status": saved_row.get("status"),
            "ai_model_name": saved_row.get("ai_model_name", TRANSLATION_MODEL_FALLBACK),
            "ai_model_catalog": normalize_model_catalog(
                saved_row.get("ai_model_catalog"),
                saved_row.get("ai_model_name") or TRANSLATION_MODEL_FALLBACK,
            ),
            "has_ai_key": bool(key_catalog),
            "ai_api_keys_count": len(key_catalog),
        },
    }
class HomepageSettings(BaseModel):
    warning_title: Optional[str] = None
    warning_subtitle: Optional[str] = None
    warning_headline: Optional[str] = None
    warning_description: Optional[str] = None
    features_title: Optional[str] = None
    features_json: Optional[list] = None
    requested_locale: str = DEFAULT_LOCALE
    resolved_locale: str = DEFAULT_LOCALE
    is_fallback: bool = False


class HomepageAutoSaveResponse(BaseModel):
    message: str
    settings: dict
    auto_translated_locales: list[str] = []
    failed_translations: list[dict] = []


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


def build_default_homepage_settings() -> dict:
    return {
        "warning_title": "CẢNH BÁO KHU VỰC CẤM",
        "warning_subtitle": "BIOSAFETY LEVEL 4 • RESTRICTED ACCESS",
        "warning_headline": "TRẬN ĐỊA SINH TỬ",
        "warning_description": "Năm 20XX. Virus Z-79 bùng phát từ một phòng thí nghiệm bí mật...",
        "features_title": "ĐIỂM NỔI BẬT",
        "features_json": [],
    }


@app.get("/api/homepage", response_model=HomepageSettings)
async def get_homepage_settings_i18n(locale: str = Query(DEFAULT_LOCALE, description="Requested locale")):
    """Lấy cấu hình nội dung hiển thị trên trang chủ theo locale."""
    base_payload = build_default_homepage_settings()
    try:
        resp = supabase.table("homepage_settings").select("*").eq("id", 1).single().execute()
        if resp.data:
            base_payload = prepare_homepage_settings_payload(resp.data)
        else:
            base_payload = prepare_homepage_settings_payload(base_payload)
    except Exception:
        base_payload = prepare_homepage_settings_payload(base_payload)

    translated_payload = apply_homepage_translation(base_payload, locale)
    return HomepageSettings(**translated_payload)


@app.put("/api/admin/homepage", summary="[Admin] Cập nhật cấu hình trang chủ")
async def admin_update_homepage_i18n(
    body: HomepageSettings,
    authorization: Optional[str] = Header(None),
    locale: str = Query(DEFAULT_LOCALE, description="Locale to update"),
):
    """Cập nhật nội dung CMS của trang chủ theo locale."""
    await verify_admin(authorization)

    target_locale = normalize_locale(locale)
    payload = prepare_homepage_settings_payload(body.model_dump(exclude_none=True))
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()

    if target_locale == DEFAULT_LOCALE:
        payload["id"] = 1
        result = supabase.table("homepage_settings").upsert(payload).execute()
        return {"message": "Cập nhật trang chủ thành công", "settings": result.data[0] if result.data else payload}

    payload.update(
        {
            "homepage_settings_id": 1,
            "locale": target_locale,
            "translation_status": "published",
            "translation_source": "human",
            "translated_at": datetime.now(timezone.utc).isoformat(),
            "content_hash": build_content_hash(json.dumps(payload, ensure_ascii=False, sort_keys=True)),
        }
    )
    result = (
        supabase.table("homepage_settings_translations")
        .upsert(payload, on_conflict="homepage_settings_id,locale")
        .execute()
    )
    return {"message": "Cập nhật bản dịch trang chủ thành công", "settings": result.data[0] if result.data else payload}


@app.post("/api/admin/homepage/translate", summary="[Admin] Dịch AI cấu hình trang chủ")
async def admin_translate_homepage_i18n(
    authorization: Optional[str] = Header(None),
    locale: Optional[str] = Query(None, description="Specific locale to translate"),
):
    """Dịch AI cho các field CMS của trang chủ từ tiếng Việt sang các locale còn lại."""
    await verify_admin(authorization)

    try:
        resp = supabase.table("homepage_settings").select("*").eq("id", 1).single().execute()
        base_payload = prepare_homepage_settings_payload(resp.data if resp.data else build_default_homepage_settings())
    except Exception:
        base_payload = prepare_homepage_settings_payload(build_default_homepage_settings())

    if locale:
        target_locales = [normalize_locale(locale)]
    else:
        target_locales = [item for item in SUPPORTED_LOCALES if item != DEFAULT_LOCALE]

    target_locales = [item for item in target_locales if item != DEFAULT_LOCALE]
    translated_locales = []
    for target_locale in target_locales:
        try:
            await upsert_homepage_translation(base_payload, target_locale)
            translated_locales.append(target_locale)
        except HTTPException as exc:
            failed_translations.append(
                {
                    "locale": target_locale,
                    "status_code": exc.status_code,
                    "detail": str(exc.detail),
                }
            )
        except Exception as exc:
            failed_translations.append(
                {
                    "locale": target_locale,
                    "status_code": 500,
                    "detail": str(exc),
                }
            )

    return {
        "message": "Đã dịch cấu hình trang chủ",
        "translated_locales": translated_locales,
    }


@app.put("/api/admin/homepage/auto-save", response_model=HomepageAutoSaveResponse, summary="[Admin] Luu trang chu va tu dong dich AI")
async def admin_auto_save_homepage_i18n(
    body: HomepageSettings,
    authorization: Optional[str] = Header(None),
    locale: str = Query(DEFAULT_LOCALE, description="Locale to update"),
):
    """Luu CMS trang chu. Neu locale la vi thi tu dong dich sang en, zh-CN va ja."""
    await verify_admin(authorization)

    target_locale = normalize_locale(locale)
    payload = prepare_homepage_settings_payload(body.model_dump(exclude_none=True))
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()

    if target_locale == DEFAULT_LOCALE:
        payload["id"] = 1
        result = supabase.table("homepage_settings").upsert(payload).execute()
        translated_locales = []
        failed_translations = []
        for auto_locale in (item for item in SUPPORTED_LOCALES if item != DEFAULT_LOCALE):
            try:
                await upsert_homepage_translation(payload, auto_locale)
                translated_locales.append(auto_locale)
            except HTTPException as exc:
                failed_translations.append(
                    {
                        "locale": auto_locale,
                        "status_code": exc.status_code,
                        "detail": str(exc.detail),
                    }
                )
            except Exception as exc:
                failed_translations.append(
                    {
                        "locale": auto_locale,
                        "status_code": 500,
                        "detail": str(exc),
                    }
                )

        message = "Da luu trang chu va tu dong dich"
        if failed_translations and translated_locales:
            message = "Da luu trang chu va dich mot phan"
        elif failed_translations and not translated_locales:
            message = "Da luu trang chu, nhung auto-dich tam thoi that bai"

        return {
            "message": message,
            "settings": result.data[0] if result.data else payload,
            "auto_translated_locales": translated_locales,
            "failed_translations": failed_translations,
        }

    payload.update(
        {
            "homepage_settings_id": 1,
            "locale": target_locale,
            "translation_status": "published",
            "translation_source": "human",
            "translated_at": datetime.now(timezone.utc).isoformat(),
            "content_hash": build_content_hash(json.dumps(payload, ensure_ascii=False, sort_keys=True)),
        }
    )
    result = (
        supabase.table("homepage_settings_translations")
        .upsert(payload, on_conflict="homepage_settings_id,locale")
        .execute()
    )
    return {
        "message": "Da luu ban dich trang chu",
        "settings": result.data[0] if result.data else payload,
        "auto_translated_locales": [],
        "failed_translations": [],
    }


@app.get("/api/_legacy/homepage", response_model=HomepageSettings)
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


@app.put("/api/_legacy/admin/homepage", summary="[Legacy] Cập nhật cấu hình trang chủ")
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
async def get_wiki_entry(slug: str, locale: str = Query(DEFAULT_LOCALE, description="Requested locale")):
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
        apply_wiki_translation(data, normalize_locale(locale))
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
