"""
AI Oracle - The Living System
POST /oracle/ask

3-tier architecture:
  Tier 1: Cache hit -> return immediately (0 API calls)
  Tier 2: Local wiki search -> return if sufficient data is found
  Tier 3: Gemini API -> call with chapter-capped context, then store in cache

Security: API key is never exposed to the frontend.
Rate limit: 10 AI queries per IP per day (local wiki queries are unlimited).
"""

import hashlib
import os
import re
from datetime import datetime, timedelta, timezone
from time import perf_counter
from typing import Optional

import httpx
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/oracle", tags=["ai_oracle"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_MODEL = "gemini-3.1-flash-lite-preview"
BASE_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)
DAILY_AI_LIMIT = 10

SYSTEM_PROMPT_TEMPLATE = """
Bạn là "Hệ Thống" - một trí tuệ nhân tạo bí ẩn trong câu chuyện "Mạt Thế Sinh Hóa Nguy Cơ".
Người dùng đang đọc đến Chương {chapter_cap}.

QUY TẮC TUYỆT ĐỐI:
1. Chỉ được sử dụng thông tin từ Chương 1 đến Chương {chapter_cap}.
2. Nếu sự kiện xảy ra sau Chương {chapter_cap}, hãy nói: "Dữ liệu chưa được giải mã."
3. Trả lời bằng tiếng Việt, ngắn gọn (dưới 200 chữ), đúng chất "Hệ Thống" - lạnh lùng và chính xác.
4. Không bịa đặt thông tin không có trong truyện.

Thông tin ngữ cảnh (wiki):
{wiki_context}
""".strip()

WIKI_EMPTY_CONTEXT = "Khong co du lieu wiki lien quan."
MIN_CACHEABLE_LENGTH = 24


class OracleRequest(BaseModel):
    question: str
    chapter_progress: int = 1


class OracleResponse(BaseModel):
    answer: str
    source: str
    chapter_cap: int


class OracleHealthResponse(BaseModel):
    ok: bool
    status: str
    active_model: str
    model_catalog: list[str]
    has_api_key: bool
    rate_limit_configured: bool
    cache_configured: bool
    detail: str
    upstream_status: Optional[int] = None
    upstream_error: Optional[str] = None


class AdminAiPlaygroundRequest(BaseModel):
    models: list[str]
    prompt: str = "Tra loi ngan gon bang tieng Viet: xac nhan model dang hoat dong."
    chapter_progress: int = 1
    api_key: Optional[str] = None


class AdminAiPlaygroundResult(BaseModel):
    model: str
    status: str
    latency_ms: int
    answer_preview: Optional[str] = None
    error: Optional[str] = None
    used_saved_key: bool


class AdminAiPlaygroundResponse(BaseModel):
    prompt: str
    chapter_progress: int
    results: list[AdminAiPlaygroundResult]


def hash_question(question: str, chapter_cap: int) -> str:
    normalized = re.sub(r"\s+", " ", question.lower().strip())
    return hashlib.sha256(f"{normalized}|{chapter_cap}".encode()).hexdigest()[:32]


def get_ip_hash(request: Request) -> str:
    ip = request.client.host if request.client else "unknown"
    return hashlib.md5(ip.encode()).hexdigest()


def normalize_answer_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def is_garbage_answer(text: str) -> bool:
    normalized = normalize_answer_text(text)
    if not normalized:
        return True
    if len(normalized) < MIN_CACHEABLE_LENGTH:
        return True

    lowered = normalized.lower()
    garbage_markers = (
        "[he thong khoi dong]",
        "[thong bao he thong]",
        "[du lieu he thong]",
        "chuong",
        "context:*",
    )
    if lowered in garbage_markers:
        return True
    if lowered.startswith("[he thong khoi dong]") and len(normalized) < 96:
        return True
    if lowered.startswith("[thong bao he thong]") and len(normalized) < 96:
        return True
    return False


async def delete_cache_entry(supabase, question_hash: str, chapter_cap: int):
    try:
        (
            supabase.table("oracle_cache")
            .delete()
            .eq("question_hash", question_hash)
            .eq("chapter_cap", chapter_cap)
            .execute()
        )
    except Exception:
        pass


async def check_cache(supabase, question_hash: str, chapter_cap: int) -> Optional[str]:
    try:
        result = (
            supabase.table("oracle_cache")
            .select("id, response")
            .eq("question_hash", question_hash)
            .eq("chapter_cap", chapter_cap)
            .limit(1)
            .execute()
        )
        if result.data:
            response = result.data[0].get("response", "")
            if is_garbage_answer(response):
                await delete_cache_entry(supabase, question_hash, chapter_cap)
                return None
            supabase.table("oracle_cache").update(
                {"hit_count": result.data[0].get("hit_count", 0) + 1}
            ).eq("question_hash", question_hash).execute()
            return response
    except Exception:
        pass
    return None


async def store_cache(
    supabase,
    question_hash: str,
    chapter_cap: int,
    response: str,
    source: str,
):
    if is_garbage_answer(response):
        return
    try:
        supabase.table("oracle_cache").upsert(
            {
                "question_hash": question_hash,
                "chapter_cap": chapter_cap,
                "response": response,
                "source": source,
                "hit_count": 0,
            },
            on_conflict="question_hash,chapter_cap",
        ).execute()
    except Exception:
        pass


async def get_wiki_context(supabase, question: str, chapter_cap: int) -> str:
    if not supabase:
        return ""
    try:
        words = [w for w in re.findall(r"[\wA-Za-zÀ-ỹ]{3,}", question) if w[0].isupper()]
        if not words:
            return ""

        context_parts: list[str] = []
        for word in words[:3]:
            result = (
                supabase.table("wiki_entries")
                .select("name, faction, status, description")
                .ilike("name", f"%{word}%")
                .lte("chapter_introduced", chapter_cap)
                .limit(2)
                .execute()
            )
            for row in result.data or []:
                context_parts.append(f"- {row['name']}: {row.get('description', '')[:150]}")
        return "\n".join(context_parts) or WIKI_EMPTY_CONTEXT
    except Exception:
        return ""


async def check_rate_limit(supabase, ip_hash: str) -> bool:
    if not supabase:
        return True
    try:
        now = datetime.now(timezone.utc)
        result = (
            supabase.table("oracle_rate_limits")
            .select("id, request_count, window_start")
            .eq("ip_hash", ip_hash)
            .limit(1)
            .execute()
        )

        if not result.data:
            supabase.table("oracle_rate_limits").insert(
                {
                    "ip_hash": ip_hash,
                    "request_count": 1,
                    "window_start": now.isoformat(),
                }
            ).execute()
            return True

        row = result.data[0]
        row_window = datetime.fromisoformat(row["window_start"].replace("Z", "+00:00"))

        if row_window < now - timedelta(hours=24):
            supabase.table("oracle_rate_limits").update(
                {
                    "request_count": 1,
                    "window_start": now.isoformat(),
                }
            ).eq("ip_hash", ip_hash).execute()
            return True

        if row["request_count"] >= DAILY_AI_LIMIT:
            return False

        supabase.table("oracle_rate_limits").update(
            {"request_count": row["request_count"] + 1}
        ).eq("ip_hash", ip_hash).execute()
        return True
    except Exception:
        return True


async def call_gemini(
    question: str,
    chapter_cap: int,
    wiki_context: str,
    model_name: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
) -> str:
    current_key = api_key or GEMINI_API_KEY
    if not current_key:
        raise HTTPException(status_code=503, detail="AI service not configured")

    gemini_url = BASE_GEMINI_URL.format(model=model_name)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        chapter_cap=chapter_cap,
        wiki_context=wiki_context,
    )
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": system_prompt}]},
            {"role": "user", "parts": [{"text": question}]},
        ],
        "generationConfig": {
            "maxOutputTokens": 300,
            "temperature": 0.7,
        },
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(f"{gemini_url}?key={current_key}", json=payload)
        if not resp.is_success:
            detail = f"Gemini API error: {resp.status_code}"
            try:
                error_payload = resp.json()
                message = error_payload.get("error", {}).get("message")
                if message:
                    detail = f"{detail} - {message}"
            except Exception:
                pass
            raise HTTPException(status_code=resp.status_code, detail=detail)

        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise HTTPException(status_code=502, detail="Invalid Gemini response format")


def normalize_model_catalog(raw_catalog, fallback_model: str) -> list[str]:
    if isinstance(raw_catalog, list):
        catalog = [f"{item}".strip() for item in raw_catalog if f"{item}".strip()]
    else:
        catalog = []
    if fallback_model and fallback_model not in catalog:
        catalog.insert(0, fallback_model)
    if not catalog:
        catalog = [fallback_model or DEFAULT_MODEL]
    return list(dict.fromkeys(catalog))


def is_model_retryable(exc: HTTPException) -> bool:
    detail = str(exc.detail).lower()
    return (
        exc.status_code == 429
        or "resource exhausted" in detail
        or "rate limit" in detail
        or "quota" in detail
    )


def classify_upstream_error(exc: HTTPException) -> str:
    detail = str(exc.detail).lower()
    if exc.status_code == 503 and "not configured" in detail:
        return "missing_key"
    if exc.status_code == 429:
        return "rate_limited"
    if "resource exhausted" in detail or "quota" in detail or "rate limit" in detail:
        return "model_exhausted"
    if exc.status_code in (400, 404):
        return "model_unavailable"
    if exc.status_code in (401, 403):
        return "auth_error"
    return "upstream_error"


async def resolve_ai_settings(supabase) -> tuple[str, list[str], Optional[str]]:
    try:
        settings_resp = (
            supabase.table("novel_settings")
            .select("ai_model_name, ai_model_catalog, ai_api_key")
            .eq("id", 1)
            .single()
            .execute()
        )
        if settings_resp.data:
            model_name = settings_resp.data.get("ai_model_name", DEFAULT_MODEL)
            return (
                model_name,
                normalize_model_catalog(
                    settings_resp.data.get("ai_model_catalog"),
                    model_name,
                ),
                settings_resp.data.get("ai_api_key"),
            )
    except Exception:
        pass

    return DEFAULT_MODEL, [DEFAULT_MODEL], None


def probe_table(supabase, table_name: str) -> bool:
    if not supabase:
        return False
    try:
        supabase.table(table_name).select("id").limit(1).execute()
        return True
    except Exception:
        return False


async def build_oracle_health(supabase) -> OracleHealthResponse:
    active_model, model_catalog, custom_key = await resolve_ai_settings(supabase)
    has_api_key = bool((custom_key or GEMINI_API_KEY).strip())
    cache_configured = probe_table(supabase, "oracle_cache")
    rate_limit_configured = probe_table(supabase, "oracle_rate_limits")

    if not has_api_key:
        return OracleHealthResponse(
            ok=False,
            status="missing_key",
            active_model=active_model,
            model_catalog=model_catalog,
            has_api_key=False,
            rate_limit_configured=rate_limit_configured,
            cache_configured=cache_configured,
            detail="Oracle chua co API key hop le.",
        )

    last_error: Optional[HTTPException] = None
    for model_name in model_catalog:
        try:
            await call_gemini(
                question="Tra loi mot tu: ONLINE",
                chapter_cap=1,
                wiki_context="",
                model_name=model_name,
                api_key=custom_key,
            )
            return OracleHealthResponse(
                ok=True,
                status="ok",
                active_model=model_name,
                model_catalog=model_catalog,
                has_api_key=True,
                rate_limit_configured=rate_limit_configured,
                cache_configured=cache_configured,
                detail="Oracle backend san sang xu ly.",
            )
        except HTTPException as exc:
            last_error = exc
            if not is_model_retryable(exc):
                break

    if last_error:
        status = classify_upstream_error(last_error)
        return OracleHealthResponse(
            ok=False,
            status=status,
            active_model=active_model,
            model_catalog=model_catalog,
            has_api_key=True,
            rate_limit_configured=rate_limit_configured,
            cache_configured=cache_configured,
            detail=str(last_error.detail),
            upstream_status=last_error.status_code,
            upstream_error=str(last_error.detail),
        )

    return OracleHealthResponse(
        ok=False,
        status="model_unavailable",
        active_model=active_model,
        model_catalog=model_catalog,
        has_api_key=has_api_key,
        rate_limit_configured=rate_limit_configured,
        cache_configured=cache_configured,
        detail="Khong co model AI kha dung.",
    )


@router.get("/health", response_model=OracleHealthResponse)
async def oracle_health():
    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase

    return await build_oracle_health(supabase)


@router.post("/ask", response_model=OracleResponse)
async def ask_oracle(body: OracleRequest, request: Request):
    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase

    question = body.question.strip()
    if len(question) < 5:
        raise HTTPException(status_code=400, detail="Cau hoi qua ngan")
    if len(question) > 500:
        raise HTTPException(status_code=400, detail="Cau hoi qua dai (max 500 ky tu)")

    chapter_cap = max(1, min(body.chapter_progress, 9999))
    question_hash = hash_question(question, chapter_cap)

    cached = await check_cache(supabase, question_hash, chapter_cap)
    if cached:
        return OracleResponse(answer=cached, source="cache", chapter_cap=chapter_cap)

    wiki_context = await get_wiki_context(supabase, question, chapter_cap)
    if wiki_context and wiki_context != WIKI_EMPTY_CONTEXT and len(question.split()) <= 12:
        answer = f"[DU LIEU HE THONG]\n{wiki_context}"
        await store_cache(supabase, question_hash, chapter_cap, answer, "local_wiki")
        return OracleResponse(answer=answer, source="local_wiki", chapter_cap=chapter_cap)

    ip_hash = get_ip_hash(request)
    if not await check_rate_limit(supabase, ip_hash):
        raise HTTPException(
            status_code=429,
            detail="He thong da dat gioi han truy van trong ngay. Vui long thu lai vao ngay mai.",
        )

    _, model_catalog, custom_key = await resolve_ai_settings(supabase)

    answer = None
    last_error: Optional[HTTPException] = None
    for model_name in model_catalog:
        try:
            answer = await call_gemini(
                question,
                chapter_cap,
                wiki_context,
                model_name=model_name,
                api_key=custom_key,
            )
            break
        except HTTPException as exc:
            last_error = exc
            if not is_model_retryable(exc):
                raise
            continue

    if answer is None:
        if last_error:
            raise last_error
        raise HTTPException(status_code=502, detail="No AI model available")

    await store_cache(supabase, question_hash, chapter_cap, answer, "gemini")
    return OracleResponse(answer=answer, source="gemini", chapter_cap=chapter_cap)


@router.post("/admin/playground", response_model=AdminAiPlaygroundResponse)
async def admin_ai_playground(
    body: AdminAiPlaygroundRequest,
    authorization: Optional[str] = Header(None),
):
    try:
        from main import supabase, verify_admin
    except ImportError:
        from backend.main import supabase, verify_admin

    user = await verify_admin(authorization)
    if user.get("role") != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can use AI playground.")

    models = [model.strip() for model in body.models if model.strip()]
    models = list(dict.fromkeys(models))[:12]
    if not models:
        raise HTTPException(status_code=400, detail="At least one model is required.")

    prompt = body.prompt.strip() or "Tra loi ngan gon bang tieng Viet: xac nhan model dang hoat dong."
    chapter_progress = max(1, min(body.chapter_progress, 9999))
    stored_model, _, stored_key = await resolve_ai_settings(supabase)
    chosen_key = body.api_key.strip() if body.api_key else (stored_key or "")
    used_saved_key = not bool(body.api_key and body.api_key.strip())

    results: list[AdminAiPlaygroundResult] = []
    for model in models:
        start = perf_counter()
        try:
            if not chosen_key:
                raise HTTPException(status_code=503, detail="AI service not configured")

            answer = await call_gemini(
                prompt,
                chapter_progress,
                "",
                model_name=model or stored_model,
                api_key=chosen_key,
            )
            latency_ms = int((perf_counter() - start) * 1000)
            results.append(
                AdminAiPlaygroundResult(
                    model=model,
                    status="success",
                    latency_ms=latency_ms,
                    answer_preview=answer[:240],
                    used_saved_key=used_saved_key,
                )
            )
        except HTTPException as exc:
            latency_ms = int((perf_counter() - start) * 1000)
            status = classify_upstream_error(exc)
            results.append(
                AdminAiPlaygroundResult(
                    model=model,
                    status=status,
                    latency_ms=latency_ms,
                    error=str(exc.detail),
                    used_saved_key=used_saved_key,
                )
            )
        except Exception as exc:
            latency_ms = int((perf_counter() - start) * 1000)
            results.append(
                AdminAiPlaygroundResult(
                    model=model,
                    status="internal_error",
                    latency_ms=latency_ms,
                    error=str(exc),
                    used_saved_key=used_saved_key,
                )
            )

    return AdminAiPlaygroundResponse(
        prompt=prompt,
        chapter_progress=chapter_progress,
        results=results,
    )
