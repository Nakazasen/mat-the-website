"""
AI Oracle - The Living System
POST /oracle/ask

3-tier architecture:
  Tier 1: Cache hit -> return immediately (0 API calls)
  Tier 2: Local wiki search -> return if sufficient data is found
  Tier 3: Gemini API -> call with chapter-capped context, then store in cache

Security: API key is never exposed to the frontend.
Rate limit: 50 AI queries per IP per day (local wiki queries are unlimited).
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
DEFAULT_MODEL_CATALOG = [
    "gemini-3.1-flash-lite-preview",
    "gemma-3n-1b-it",
    "gemma-3n-e2b-it",
    "gemma-3-4b-it",
    "gemma-3-12b-it",
    "gemma-3-27b-it",
    "gemini-robotics-er-1.5-preview",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]
DEFAULT_MODEL = DEFAULT_MODEL_CATALOG[0]
MODEL_PRIORITY = {model: index for index, model in enumerate(DEFAULT_MODEL_CATALOG)}
BASE_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)
DAILY_AI_LIMIT = 50

SYSTEM_PROMPT_TEMPLATE = """
Ban la "He Thong" - mot tri tue nhan tao bi an trong cau chuyen "Mat The Sinh Hoa Nguy Co".
Nguoi dung dang doc den Chuong {chapter_cap}.

QUY TAC TUYET DOI:
1. Chi duoc su dung thong tin tu Chuong 1 den Chuong {chapter_cap}.
2. Neu su kien xay ra sau Chuong {chapter_cap}, hay noi chinh xac: "Du lieu chua duoc giai ma."
3. Tra loi bang tieng Viet tu nhien, ngan gon, ro nghia, toi da 150 tu.
4. Khong duoc tra ve tieu de rong kieu "[THONG BAO HE THONG]" neu khong co noi dung giai thich theo sau.
5. Neu cau hoi khong du du kien trong pham vi da doc, hay tra loi ngan gon theo phong cach He Thong va neu ro gioi han du lieu.
6. Khong bia thong tin khong co trong truyen hoac trong wiki context.
7. Neu cau hoi la ve nhan vat, the luc, vat pham hoac su kien, uu tien tra loi bang chi tiet cu the thay vi noi chung chung.
8. Tra loi PHAI day du va hoan chinh. KHONG duoc cat ngang giua cau.

Thong tin ngu canh (wiki):
{wiki_context}
""".strip()

WIKI_EMPTY_CONTEXT = "Khong co du lieu wiki lien quan."
MIN_CACHEABLE_LENGTH = 24
QUESTION_STOPWORDS = {
    "ai", "la", "gi", "nao", "bao", "nhieu", "co", "khong", "cho", "toi",
    "mot", "nhung", "trong", "the", "than", "phe", "xuat", "hien", "tu",
    "chuong", "voi", "ve", "nay", "kia", "roi", "sao", "cac", "nhan", "vat",
}


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


class AdminOracleResetResponse(BaseModel):
    deleted_rows: int
    detail: str


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
    if lowered.startswith("[he thong da khoi dong]") and len(normalized) < 96:
        return True
    if lowered.startswith("ch 816 context") or lowered.startswith("chuong ") or lowered.startswith("chapter "):
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
        # Also extract significant lowercase words (>= 4 chars, not stopwords)
        extra_words = [
            w for w in re.findall(r"[\wA-Za-zÀ-ỹ]{4,}", question)
            if w.lower() not in QUESTION_STOPWORDS and w not in words
        ]
        search_words = (words + extra_words[:2])[:5]
        if not search_words:
            return ""

        context_parts: list[str] = []
        seen_names: set[str] = set()
        for word in search_words:
            result = (
                supabase.table("wiki_entries")
                .select("name, faction, status, description")
                .ilike("name", f"%{word}%")
                .lte("chapter_introduced", chapter_cap)
                .limit(3)
                .execute()
            )
            for row in result.data or []:
                name = row.get('name', '')
                if name in seen_names:
                    continue
                seen_names.add(name)
                desc = row.get('description', '') or ''
                faction = row.get('faction', '') or ''
                status_text = row.get('status', '') or ''
                parts = [f"- {name}"]
                if faction:
                    parts.append(f"(Phe: {faction})")
                if status_text:
                    parts.append(f"[{status_text}]")
                parts.append(f": {desc[:300]}")
                context_parts.append(" ".join(parts))
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
            "maxOutputTokens": 800,
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


async def call_ai_provider(
    question: str,
    chapter_cap: int,
    wiki_context: str,
) -> Optional[str]:
    """Try multi-provider router first, return None if unavailable."""
    try:
        try:
            from main import get_provider_router, resolve_ai_provider_config, AIRequest
        except ImportError:
            from backend.main import get_provider_router, resolve_ai_provider_config, AIRequest

        router = get_provider_router()
        if not router._providers:
            return None

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            chapter_cap=chapter_cap,
            wiki_context=wiki_context,
        )
        request = AIRequest(
            text=question,
            mode="chat",
            system_instruction=system_prompt,
            max_output_tokens=800,
            temperature=0.7,
        )
        config = resolve_ai_provider_config()
        policy = config.get("chat_policy", {"mode": "waterfall"})
        result = await router.route(request, policy=policy)
        if result.status == "success" and result.text:
            return result.text.strip()
        return None
    except Exception:
        return None


def normalize_model_catalog(raw_catalog, fallback_model: str) -> list[str]:
    if isinstance(raw_catalog, list):
        catalog = [f"{item}".strip() for item in raw_catalog if f"{item}".strip()]
    else:
        catalog = []
    if fallback_model and fallback_model not in catalog:
        catalog.insert(0, fallback_model)
    if not catalog:
        catalog = DEFAULT_MODEL_CATALOG.copy()
    else:
        catalog.extend(DEFAULT_MODEL_CATALOG)
    deduped = list(dict.fromkeys(catalog))
    return sorted(deduped, key=lambda item: MODEL_PRIORITY.get(item, len(DEFAULT_MODEL_CATALOG) + 100))


def normalize_api_key_catalog(raw_keys, fallback_key: Optional[str]) -> list[str]:
    keys = []
    if isinstance(raw_keys, list):
        keys.extend(f"{item}".strip() for item in raw_keys if f"{item}".strip())
    if fallback_key and fallback_key.strip():
        keys.insert(0, fallback_key.strip())
    return list(dict.fromkeys([item for item in keys if item]))


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


async def resolve_ai_settings(supabase) -> tuple[str, list[str], list[str]]:
    try:
        settings_resp = (
            supabase.table("novel_settings")
            .select("ai_model_name, ai_model_catalog, ai_api_key, ai_api_keys")
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
                normalize_api_key_catalog(
                    settings_resp.data.get("ai_api_keys"),
                    settings_resp.data.get("ai_api_key"),
                ),
            )
    except Exception:
        pass

    return DEFAULT_MODEL, DEFAULT_MODEL_CATALOG.copy(), normalize_api_key_catalog([], GEMINI_API_KEY)


def probe_table(supabase, table_name: str) -> bool:
    if not supabase:
        return False
    try:
        supabase.table(table_name).select("id").limit(1).execute()
        return True
    except Exception:
        return False


async def build_oracle_health(supabase) -> OracleHealthResponse:
    active_model, model_catalog, api_keys = await resolve_ai_settings(supabase)
    has_api_key = bool(api_keys)
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
    for api_key in api_keys:
        for model_name in model_catalog:
            try:
                await call_gemini(
                    question="Tra loi mot tu: ONLINE",
                    chapter_cap=1,
                    wiki_context="",
                    model_name=model_name,
                    api_key=api_key,
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


@router.get("/admin/health", response_model=OracleHealthResponse)
async def admin_oracle_health(authorization: Optional[str] = Header(None)):
    try:
        from main import supabase, verify_admin
    except ImportError:
        from backend.main import supabase, verify_admin

    user = await verify_admin(authorization)
    if user.get("role") != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can inspect Oracle health.")

    return await build_oracle_health(supabase)


@router.post("/admin/reset-rate-limit", response_model=AdminOracleResetResponse)
async def admin_reset_oracle_rate_limit(authorization: Optional[str] = Header(None)):
    try:
        from main import supabase, verify_admin
    except ImportError:
        from backend.main import supabase, verify_admin

    user = await verify_admin(authorization)
    if user.get("role") != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can reset Oracle rate limits.")

    try:
        existing = supabase.table("oracle_rate_limits").select("id").execute()
        deleted_rows = len(existing.data or [])
        supabase.table("oracle_rate_limits").delete().neq("id", 0).execute()
        return AdminOracleResetResponse(
            deleted_rows=deleted_rows,
            detail="Oracle rate limits have been reset.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to reset Oracle rate limits: {exc}")


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

    # --- Multi-provider route (Phase 4) ---
    answer = await call_ai_provider(question, chapter_cap, wiki_context)
    if answer and not is_garbage_answer(answer):
        await store_cache(supabase, question_hash, chapter_cap, answer, "ai_provider")
        return OracleResponse(answer=answer, source="ai_provider", chapter_cap=chapter_cap)

    # --- Legacy Gemini fallback ---
    _, model_catalog, api_keys = await resolve_ai_settings(supabase)

    last_error: Optional[HTTPException] = None
    for api_key in api_keys:
        for model_name in model_catalog:
            try:
                answer = await call_gemini(
                    question,
                    chapter_cap,
                    wiki_context,
                    model_name=model_name,
                    api_key=api_key,
                )
                if is_garbage_answer(answer):
                    last_error = HTTPException(
                        status_code=502,
                        detail=f"Model {model_name} returned invalid answer",
                    )
                    continue
                break
            except HTTPException as exc:
                last_error = exc
                if not is_model_retryable(exc):
                    raise
                continue
        if answer is not None and not is_garbage_answer(answer):
            break

    if answer is None or is_garbage_answer(answer):
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
    stored_model, _, stored_keys = await resolve_ai_settings(supabase)
    chosen_key = body.api_key.strip() if body.api_key else (stored_keys[0] if stored_keys else "")
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
