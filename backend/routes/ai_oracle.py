"""
AI Oracle — The Living System
POST /oracle/ask

3-tier architecture:
  Tier 1: Cache hit → return immediately (0 API calls)
  Tier 2: Wiki local search → return if sufficient data found
  Tier 3: Gemini API → call with chapter-capped context, store in cache

Security: API key is NEVER exposed to frontend.
Rate limit: 10 AI queries per IP per day (local wiki queries unlimited).
"""

import os
import hashlib
import re
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/oracle", tags=["ai_oracle"])

# =============================================
# Config
# =============================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_MODEL = "gemini-3.1-flash-lite-preview"
BASE_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DAILY_AI_LIMIT = 10  # Max Gemini calls per IP per day

# Story system prompt — caps knowledge at reader progress
SYSTEM_PROMPT_TEMPLATE = """
Bạn là "Hệ Thống" — một trí tuệ nhân tạo bí ẩn trong câu chuyện "Mạt Thế Sinh Hoá Nguy Cơ".
Người dùng đang đọc đến Chương {chapter_cap}.

QUY TẮC TUYỆT ĐỐI:
1. Chỉ được sử dụng thông tin từ Chương 1 đến Chương {chapter_cap}.
2. Nếu sự kiện xảy ra sau Chương {chapter_cap}, hãy nói: "Dữ liệu chưa được giải mã."
3. Trả lời bằng tiếng Việt, ngắn gọn (dưới 200 chữ), đúng chất "Hệ Thống" — lạnh lùng và chính xác.
4. Không bịa đặt thông tin không có trong truyện.

Thông tin ngữ cảnh (wiki):
{wiki_context}
""".strip()


# =============================================
# Models
# =============================================
class OracleRequest(BaseModel):
    question: str
    chapter_progress: int = 1


class OracleResponse(BaseModel):
    answer: str
    source: str  # "cache" | "local_wiki" | "gemini"
    chapter_cap: int


# =============================================
# Helpers
# =============================================
def hash_question(question: str, chapter_cap: int) -> str:
    """Create a stable hash for cache key."""
    normalized = re.sub(r"\s+", " ", question.lower().strip())
    return hashlib.sha256(f"{normalized}|{chapter_cap}".encode()).hexdigest()[:32]


def get_ip_hash(request: Request) -> str:
    ip = request.client.host if request.client else "unknown"
    return hashlib.md5(ip.encode()).hexdigest()


async def check_cache(supabase, question_hash: str, chapter_cap: int) -> Optional[str]:
    """Returns cached response if found."""
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
            # Increment hit count async (fire and forget)
            supabase.table("oracle_cache").update(
                {"hit_count": result.data[0].get("hit_count", 0) + 1}
            ).eq("question_hash", question_hash).execute()
            return result.data[0]["response"]
    except Exception:
        pass
    return None


async def store_cache(supabase, question_hash: str, chapter_cap: int, response: str, source: str):
    """Store response in cache."""
    try:
        supabase.table("oracle_cache").upsert({
            "question_hash": question_hash,
            "chapter_cap": chapter_cap,
            "response": response,
            "source": source,
            "hit_count": 0,
        }, on_conflict="question_hash,chapter_cap").execute()
    except Exception:
        pass


async def get_wiki_context(supabase, question: str, chapter_cap: int) -> str:
    """Search wiki for relevant context to inject into Gemini prompt."""
    if not supabase:
        return ""
    try:
        # Extract potential entity names (words > 2 chars, capitalized)
        words = [w for w in re.findall(r"[\wÀ-ỹ]{3,}", question) if w[0].isupper()]
        if not words:
            return ""

        context_parts = []
        for word in words[:3]:  # Limit to 3 searches
            result = supabase.table("wiki_entries")\
                .select("name, faction, status, description")\
                .ilike("name", f"%{word}%")\
                .lte("chapter_introduced", chapter_cap)\
                .limit(2)\
                .execute()
            for row in (result.data or []):
                context_parts.append(
                    f"- {row['name']}: {row.get('description', '')[:150]}"
                )
        return "\n".join(context_parts) or "Không có dữ liệu wiki liên quan."
    except Exception:
        return ""


async def check_rate_limit(supabase, ip_hash: str) -> bool:
    """
    Returns True if request is allowed, False if limit exceeded.
    10 AI calls per IP per 24 hours.
    """
    if not supabase:
        return True
    try:
        now = datetime.now(timezone.utc)
        window_start = (now - timedelta(hours=24)).isoformat()

        result = supabase.table("oracle_rate_limits")\
            .select("id, request_count, window_start")\
            .eq("ip_hash", ip_hash)\
            .limit(1)\
            .execute()

        if not result.data:
            # First request — create record
            supabase.table("oracle_rate_limits").insert({
                "ip_hash": ip_hash,
                "request_count": 1,
                "window_start": now.isoformat(),
            }).execute()
            return True

        row = result.data[0]
        row_window = datetime.fromisoformat(row["window_start"].replace("Z", "+00:00"))

        # Reset if > 24h old
        if row_window < now - timedelta(hours=24):
            supabase.table("oracle_rate_limits").update({
                "request_count": 1,
                "window_start": now.isoformat(),
            }).eq("ip_hash", ip_hash).execute()
            return True

        if row["request_count"] >= DAILY_AI_LIMIT:
            return False

        supabase.table("oracle_rate_limits").update({
            "request_count": row["request_count"] + 1,
        }).eq("ip_hash", ip_hash).execute()
        return True

    except Exception:
        return True  # Fail open — don't block users if DB is down


async def call_gemini(question: str, chapter_cap: int, wiki_context: str, model_name: str = DEFAULT_MODEL, api_key: Optional[str] = None) -> str:
    """Call Gemini API and return text response."""
    # Prioritize provided key (from DB) over global env key
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
        resp = await client.post(
            f"{gemini_url}?key={current_key}",
            json=payload,
        )
        if not resp.is_success:
            raise HTTPException(
                status_code=502,
                detail=f"Gemini API error: {resp.status_code}"
            )
        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise HTTPException(status_code=502, detail="Invalid Gemini response format")


# =============================================
# Route
# =============================================
@router.post("/ask", response_model=OracleResponse)
async def ask_oracle(body: OracleRequest, request: Request):
    """
    The System Oracle endpoint.
    Enforces chapter-based spoiler protection and multi-tier caching.
    """
    try:
        from database import supabase
    except ImportError:
        from backend.database import supabase

    question = body.question.strip()
    if len(question) < 5:
        raise HTTPException(status_code=400, detail="Câu hỏi quá ngắn")
    if len(question) > 500:
        raise HTTPException(status_code=400, detail="Câu hỏi quá dài (max 500 ký tự)")

    chapter_cap = max(1, min(body.chapter_progress, 9999))
    question_hash = hash_question(question, chapter_cap)

    # Tier 1: Cache lookup
    cached = await check_cache(supabase, question_hash, chapter_cap)
    if cached:
        return OracleResponse(answer=cached, source="cache", chapter_cap=chapter_cap)

    # Tier 2: Local wiki search (fast, free)
    wiki_context = await get_wiki_context(supabase, question, chapter_cap)
    # If wiki has strong data and question is a simple lookup  
    # (heuristic: < 15 words means it's likely a simple "who is X" query)
    if wiki_context and wiki_context != "Không có dữ liệu wiki liên quan." \
            and len(question.split()) <= 12:
        answer = f"[DỮ LIỆU HỆ THỐNG]\n{wiki_context}"
        await store_cache(supabase, question_hash, chapter_cap, answer, "local_wiki")
        return OracleResponse(answer=answer, source="local_wiki", chapter_cap=chapter_cap)

    # Tier 3: Rate limit check before calling Gemini
    ip_hash = get_ip_hash(request)
    if not await check_rate_limit(supabase, ip_hash):
        raise HTTPException(
            status_code=429,
            detail="HỆ THỐNG ĐANG BỊ NHIỄU SÓNG. Vui lòng thử lại vào ngày mai.",
        )

    # Get model name and potential custom API key from novel settings
    try:
        settings_resp = supabase.table("novel_settings")\
            .select("ai_model_name, ai_api_key")\
            .eq("id", 1).single().execute()
        
        ai_model = DEFAULT_MODEL
        custom_key = None
        
        if settings_resp.data:
            ai_model = settings_resp.data.get("ai_model_name", DEFAULT_MODEL)
            custom_key = settings_resp.data.get("ai_api_key")
            
    except Exception:
        ai_model = DEFAULT_MODEL
        custom_key = None

    # Call Gemini
    answer = await call_gemini(question, chapter_cap, wiki_context, model_name=ai_model, api_key=custom_key)
    await store_cache(supabase, question_hash, chapter_cap, answer, "gemini")
    return OracleResponse(answer=answer, source="gemini", chapter_cap=chapter_cap)
