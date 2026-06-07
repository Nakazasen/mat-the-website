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
from typing import Optional, Any, Literal

import httpx
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

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

DAILY_AI_LIMIT = 50

SYSTEM_PROMPT_TEMPLATE = """
Bạn là "Hệ Thống" - một trí tuệ nhân tạo bí ẩn, tối cao đang hỗ trợ người dùng sinh tồn trong thế giới tận thế của tác phẩm "Mạt Thế Sinh Hóa Nguy Cơ".
Người dùng hiện đang đọc đến Chương {chapter_cap}. Bạn có quyền truy cập vào dữ liệu của chương này và thông tin wiki được cung cấp dưới đây.

QUY TẮC TUYỆT ĐỐI KHÔNG ĐƯỢC VI PHẠM:
1. Chỉ được phép sử dụng thông tin từ Chương 1 đến Chương {chapter_cap} (dựa trên thông tin ngữ cảnh wiki và nội dung chương hiện tại được cung cấp bên dưới).
2. Nếu câu hỏi liên quan đến bất kỳ sự kiện, nhân vật hay chi tiết nào xuất hiện sau Chương {chapter_cap}, hoặc nằm ngoài dữ liệu được cung cấp dưới đây, bạn PHẢI trả lời chính xác câu sau: "Dữ liệu chưa được giải mã." (không được thêm thắt, không bịa đặt, không giải thích gì thêm).
3. Câu trả lời phải sử dụng tiếng Việt có dấu hoàn chỉnh, tự nhiên, mang phong thái lạnh lùng, huyền bí nhưng chuyên nghiệp của "Hệ Thống" tối cao.
4. Độ dài câu trả lời ngắn gọn, cô đọng, tối đa 150 từ. Trả lời đầy đủ, trọn vẹn ý, tuyệt đối không được cắt ngang giữa câu hoặc bỏ dở câu.
5. Tuyệt đối KHÔNG ĐƯỢC BỊA ĐẶT thông tin không có trong truyện hoặc không có trong dữ liệu wiki/ngữ cảnh được cung cấp. Nếu không chắc chắn, hãy trả lời: "Dữ liệu chưa được giải mã."
6. Không sử dụng tiêu đề rỗng như "[THÔNG BÁO HỆ THỐNG]" nếu không có nội dung giải thích chi tiết đi kèm.

Dữ liệu Wiki (Nhân vật, Thế lực, Vật phẩm, Địa điểm):
{wiki_context}

Nội dung Chương {chapter_cap} hiện tại:
{chapter_context}
""".strip()

WIKI_EMPTY_CONTEXT = "Không có dữ liệu wiki liên quan."
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


class OracleRagPreviewRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    chapter_progress: int = Field(..., ge=1)
    limit: int = Field(5, ge=1, le=10)
    max_chunks: int = Field(4, ge=1, le=6)


class OracleRagPreviewResponse(BaseModel):
    ok: bool
    rag_used: bool
    chunks_used: int
    citations: list[dict]
    context_preview: str
    source: str = "story_chunks_hybrid_context"


class OracleRagAnswerPreviewRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    chapter_progress: int = Field(..., ge=1)
    limit: int = Field(5, ge=1, le=10)
    max_chunks: int = Field(4, ge=1, le=6)


class OracleRagAnswerPreviewResponse(BaseModel):
    ok: bool
    rag_used: bool
    chunks_used: int
    answer: str
    citations: list[dict]
    source: str = "rag_answer_preview"


def is_identity_question(question: str) -> bool:
    """Detects whether a question is an identity/entity identification query."""
    q = question.lower().strip()
    q = re.sub(r"[?\s]+$", "", q)
    
    suffixes = (
        " là ai", " la ai",
        " là gì", " la gi",
        " là vật phẩm gì", " la vat pham gi",
        " là thực thể gì", " la thuc the gi",
        " là sinh vật gì", " la sinh vat gi",
        " là tổ chức gì", " la to chuc gi",
        " là kỹ năng gì", " la ky nang gi",
        " là nhân vật nào", " la nhan vat nao"
    )
    if q.endswith(suffixes):
        return True
        
    prefixes = (
        "ai là ", "ai la ",
        "giới thiệu ", "gioi thieu ",
        "thông tin về ", "thong tin ve ",
        "nhân vật ", "nhan vat "
    )
    if q.startswith(prefixes):
        return True
        
    return False


def extract_entity_name(question: str) -> str:
    """Extracts potential entity/character name from an identity question."""
    q = question.strip()
    q = re.sub(r"[?\s]+$", "", q)
    q_lower = q.lower()
    
    suffixes = [
        " là vật phẩm gì", " la vat pham gi",
        " là thực thể gì", " la thuc the gi",
        " là sinh vật gì", " la sinh vat gi",
        " là nhân vật nào", " la nhan vat nao",
        " là tổ chức gì", " la to chuc gi",
        " là kỹ năng gì", " la ky nang gi",
        " là ai", " la ai",
        " là gì", " la gi"
    ]
    for suffix in suffixes:
        if q_lower.endswith(suffix):
            return q[:-len(suffix)].strip()
            
    prefixes = [
        "thông tin về ", "thong tin ve ",
        "giới thiệu ", "gioi thieu ",
        "nhân vật ", "nhan vat ",
        "ai là ", "ai la "
    ]
    for prefix in prefixes:
        if q_lower.startswith(prefix):
            return q[len(prefix):].strip()
            
    return q


async def get_entity_context_for_oracle(supabase, question: str, chapter_cap: int | None = None) -> dict | None:
    """Retrieves identity information from wiki_entries table based on question's main entity name."""
    if not supabase:
        return None
    entity_name = extract_entity_name(question)
    if not entity_name or len(entity_name) < 2:
        return None
        
    try:
        result = (
            supabase.table("wiki_entries")
            .select("title, category, summary, content")
            .ilike("title", f"%{entity_name}%")
            .limit(1)
            .execute()
        )
        if result.data:
            row = result.data[0]
            title = row.get("title", "")
            category = row.get("category", "") or ""
            summary = row.get("summary", "") or ""
            content = row.get("content", "") or ""
            
            desc = summary if summary else content
            desc = desc.strip()
            
            context_text = f"- {title}"
            if category:
                context_text += f" (Phân loại: {category})"
            context_text += f": {desc}"
            
            citation = {
                "title": title,
                "category": category,
                "source": "wiki_entries"
            }
            
            return {
                "context_text": context_text,
                "citations": [citation],
                "source": "entity_profile"
            }
    except Exception as e:
        print(f"Warning: get_entity_context_for_oracle failed: {e}")
    return None


def build_rag_answer_prompt(
    question: str,
    entity_context: str,
    story_context: str,
    chapter_cap: int | None
) -> str:
    """Builds the prompt instructing the AI to answer strictly based on RAG contexts (Entity profile & Story evidence)."""
    cap = chapter_cap if chapter_cap is not None else 9999
    
    entity_section = f"--- [ENTITY_CONTEXT (ƯU TIÊN HÀNG ĐẦU BẰT BUỘC)] ---\n{entity_context}" if entity_context else "--- [ENTITY_CONTEXT] ---\nKhông có thông tin hồ sơ định danh trực tiếp."
    story_section = f"--- [STORY_EVIDENCE (BẰNG CHỨNG HỖ TRỢ)] ---\n{story_context}" if story_context else "--- [STORY_EVIDENCE] ---\nKhông có trích đoạn truyện hỗ trợ."
    
    return f"""
Bạn là "Hệ Thống" - một trí tuệ nhân tạo tối cao hỗ trợ người dùng trong thế giới tận thế của "Mạt Thế Sinh Hóa Nguy Cơ".
Người dùng hiện đang đọc đến Chương {cap}. Bạn PHẢI tuân thủ các quy tắc sau:

QUY TẮC ĐẶC BIỆT CHO RAG ANSWER:
1. CHỈ được trả lời câu hỏi dựa trên khối dữ liệu ngữ cảnh được cung cấp dưới đây gồm ENTITY_CONTEXT (thông tin hồ sơ wiki chính thức) và STORY_EVIDENCE (bằng chứng từ các chương truyện).
2. ƯU TIÊN HÀNG ĐẦU thông tin định danh từ ENTITY_CONTEXT để trả lời các câu hỏi định danh (Ví dụ: "... là ai", "... là gì").
3. Tuyệt đối KHÔNG BỊA ĐẶT, không được sử dụng kiến thức bên ngoài hoặc thông tin không có trong khối ngữ cảnh được cung cấp.
4. Nếu thông tin trong cả hai ngữ cảnh không đủ để trả lời câu hỏi một cách chắc chắn, bạn bắt buộc phải trả lời: "Dữ liệu hiện có chưa đủ để kết luận." (không thêm thắt, không giải thích).
5. Không spoil thông tin xuất hiện sau Chương {cap}.
6. Câu trả lời mang phong thái lạnh lùng, ngắn gọn, súc tích (dưới 150 từ). Nếu đó là câu hỏi định danh và có hồ sơ, hãy nêu bật vai trò cốt lõi của đối tượng (ví dụ: "nhân vật chính").
7. Hãy định dạng câu trả lời theo cấu trúc sau:

Câu trả lời:
[Nội dung câu trả lời của bạn]

Nguồn:
[Liệt kê các nguồn dưới dạng: - Wiki: [Tên thực thể] hoặc - Chương X - Tiêu đề chương | chunk Y (như được ghi trong tiêu đề của chunk ngữ cảnh)]

Ngữ cảnh RAG:
{entity_section}

{story_section}

Câu hỏi của người dùng: {question}
""".strip()


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


# TODO: Upgrade this basic keyword-matching retrieval to a more advanced RAG system in future phases.
# E.g., implement dense vector embeddings with pgvector or hybrid dense-sparse search to retrieve context.
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
        seen_titles: set[str] = set()
        for word in search_words:
            result = (
                supabase.table("wiki_entries")
                .select("title, category, summary, content")
                .ilike("title", f"%{word}%")
                .limit(3)
                .execute()
            )
            for row in result.data or []:
                title = row.get('title', '')
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                summary = row.get('summary', '') or ''
                content = row.get('content', '') or ''
                category = row.get('category', '') or ''
                desc = summary if summary else content
                parts = [f"- {title}"]
                if category:
                    parts.append(f"(Phân loại: {category})")
                parts.append(f": {desc[:400]}")
                context_parts.append(" ".join(parts))
        return "\n".join(context_parts) or WIKI_EMPTY_CONTEXT
    except Exception:
        return ""


async def get_chapter_context(supabase, chapter_cap: int) -> str:
    if not supabase:
        return ""
    try:
        result = (
            supabase.table("chapters")
            .select("title, content_url")
            .eq("chapter_number", chapter_cap)
            .limit(1)
            .execute()
        )
        if not result.data:
            return f"(Không có dữ liệu Chương {chapter_cap})"

        row = result.data[0]
        title = row.get("title", "")
        content_url = row.get("content_url")
        if not content_url:
            return f"Chương {chapter_cap}: {title}\n(Nội dung chưa được tải)"

        try:
            from main import fetch_r2_content
        except ImportError:
            from backend.main import fetch_r2_content

        import asyncio
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, fetch_r2_content, content_url)

        if content:
            snippet = content[:12000]
            return f"Nội dung Chương {chapter_cap}: {title}\n{snippet}"
        return f"Chương {chapter_cap}: {title}\n(Nội dung trống)"
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



def is_oracle_rag_enabled() -> bool:
    """Checks if the RAG context enhancement is enabled for the Oracle ask endpoint."""
    val = os.getenv("ORACLE_RAG_ENABLED", "").lower().strip()
    return val in ("1", "true", "yes", "on")

def get_rag_context_for_oracle(
    question: str,
    chapter_cap: int | None,
    limit: int = 5
) -> dict | None:
    """
    Retrieves the RAG context block for the oracle query if RAG is enabled.
    Returns the context data dictionary containing 'context_text' and 'citations', or None.
    """
    if not is_oracle_rag_enabled():
        return None
    if not question or not question.strip():
        return None

    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase

    if not supabase:
        return None

    try:
        from backend.rag.retrieval import search_story_chunks_hybrid_lexical
        from backend.rag.context_builder import build_rag_context_block

        results = search_story_chunks_hybrid_lexical(
            supabase=supabase,
            query=question,
            chapter_cap=chapter_cap,
            limit=limit
        )
        if not results:
            return None

        context_data = build_rag_context_block(results, max_chunks=limit)
        if context_data.get("chunks_used", 0) == 0:
            return None

        return context_data
    except Exception as e:
        # Catch all exceptions to prevent crash, fallback to old Oracle logic
        print(f"Warning: RAG retrieval failed: {e}")
        return None

async def call_ai_provider_result(
    question: str,
    chapter_cap: int,
    wiki_context: str,
    chapter_context: str = "",
    rag_context: str = "",
) -> Any:
    """Route question through the multi-provider router, returning the AIResult."""
    try:
        from main import get_provider_router, resolve_ai_provider_config, AIRequest
    except ImportError:
        from backend.main import get_provider_router, resolve_ai_provider_config, AIRequest

    router = get_provider_router()
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        chapter_cap=chapter_cap,
        wiki_context=wiki_context,
        chapter_context=chapter_context,
    )
    if rag_context:
        system_prompt += f"\n\n[RAG_CONTEXT_STORY_CHUNKS]\n{rag_context}"

    request = AIRequest(
        text=question,
        mode="chat",
        system_instruction=system_prompt,
        max_output_tokens=800,
        temperature=0.7,
    )
    config = resolve_ai_provider_config()
    policy = config.get("chat_policy", {"mode": "waterfall"})
    return await router.route(request, policy=policy)



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
    cache_configured = probe_table(supabase, "oracle_cache")
    rate_limit_configured = probe_table(supabase, "oracle_rate_limits")

    try:
        from main import get_provider_router, resolve_ai_provider_config
    except ImportError:
        from backend.main import get_provider_router, resolve_ai_provider_config

    router = get_provider_router()
    enabled_providers = [p for p in router._providers.values() if p.is_available()]

    if not enabled_providers:
        return OracleHealthResponse(
            ok=False,
            status="missing_key",
            active_model="N/A",
            model_catalog=[],
            has_api_key=False,
            rate_limit_configured=rate_limit_configured,
            cache_configured=cache_configured,
            detail="Oracle chưa cấu hình hoặc không có nhà cung cấp AI Multi-provider nào khả dụng (vui lòng cấu hình API keys trong novel_settings).",
        )

    # Let's run a test query to verify if the router works
    try:
        result = await call_ai_provider_result(
            question="Tra loi dung mot tu viet hoa duy nhat: ONLINE",
            chapter_cap=1,
            wiki_context="",
        )
        if result.status == "success" and result.text:
            return OracleHealthResponse(
                ok=True,
                status="ok",
                active_model=result.model or "Multi-Provider",
                model_catalog=[p.name for p in enabled_providers],
                has_api_key=True,
                rate_limit_configured=rate_limit_configured,
                cache_configured=cache_configured,
                detail="Oracle backend sẵn sàng xử lý qua bộ định tuyến Multi-provider.",
            )
        else:
            err_msg = result.error_message or "Router returned empty response"
            return OracleHealthResponse(
                ok=False,
                status="upstream_error",
                active_model="Multi-Provider Router",
                model_catalog=[p.name for p in enabled_providers],
                has_api_key=True,
                rate_limit_configured=rate_limit_configured,
                cache_configured=cache_configured,
                detail=f"Lỗi kết nối bộ định tuyến AI Multi-provider: {err_msg}",
                upstream_status=502,
                upstream_error=err_msg,
            )
    except Exception as exc:
        return OracleHealthResponse(
            ok=False,
            status="upstream_error",
            active_model="Multi-Provider Router",
            model_catalog=[p.name for p in enabled_providers],
            has_api_key=True,
            rate_limit_configured=rate_limit_configured,
            cache_configured=cache_configured,
            detail=f"Lỗi kết nối bộ định tuyến AI Multi-provider: {exc}",
            upstream_status=502,
            upstream_error=str(exc),
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


async def test_multi_provider_model(
    model_name: str,
    prompt: str,
    custom_api_key: Optional[str] = None
) -> str:
    try:
        from main import get_provider_router
    except ImportError:
        from backend.main import get_provider_router
    from ai_providers.openai_compatible import OpenAICompatibleProvider
    from ai_providers.profiles import ProviderProfile
    from ai_providers.base import AIRequest, ProviderCandidate

    router = get_provider_router()

    # 1. Find which provider owns this model
    target_provider = None
    for provider in router._providers.values():
        if model_name in provider.model_pool:
            target_provider = provider
            break

    if not target_provider:
        if router._providers:
            target_provider = list(router._providers.values())[0]
        else:
            raise HTTPException(status_code=404, detail=f"Model {model_name} không được cấu hình trong bất kỳ nhà cung cấp AI nào.")

    request = AIRequest(text=prompt, mode="chat", max_output_tokens=800, temperature=0.7)

    if custom_api_key:
        # Build dynamic provider profile to test the custom key
        temp_profile = ProviderProfile(
            name=target_provider.name,
            display_name=target_provider.display_name,
            provider_type="openai_compatible",
            enabled=True,
            base_url=target_provider.base_url,
            api_key_pool=[custom_api_key],
            model_pool=[model_name],
            timeout=target_provider.timeout,
            default_model=model_name
        ).normalized()
        temp_provider = OpenAICompatibleProvider(profile=temp_profile)
        candidates = temp_provider.iter_candidates()
        if not candidates:
            raise HTTPException(status_code=500, detail="Không tạo được candidate hợp lệ cho API key.")
        result = await temp_provider.call(request, candidates[0])
    else:
        # Iterate over provider candidates to find matching model
        candidates = target_provider.iter_candidates()
        matching_candidate = None
        for cand in candidates:
            if cand.model == model_name:
                matching_candidate = cand
                break
        if not matching_candidate:
            if candidates:
                matching_candidate = ProviderCandidate(
                    provider_name=candidates[0].provider_name,
                    model=model_name,
                    key_index=candidates[0].key_index,
                    key_id=candidates[0].key_id
                )
            else:
                raise HTTPException(status_code=500, detail=f"Không có API keys khả dụng cho nhà cung cấp {target_provider.name}.")
        result = await target_provider.call(request, matching_candidate)

    if result.status == "success" and result.text:
        return result.text
    else:
        raise HTTPException(status_code=502, detail=result.error_message or f"Model {model_name} trả về lỗi từ API.")


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
    chapter_context = await get_chapter_context(supabase, chapter_cap)

    if wiki_context and wiki_context != WIKI_EMPTY_CONTEXT and len(question.split()) <= 12:
        answer = f"[DỮ LIỆU HỆ THỐNG]\n{wiki_context}"
        await store_cache(supabase, question_hash, chapter_cap, answer, "local_wiki")
        return OracleResponse(answer=answer, source="local_wiki", chapter_cap=chapter_cap)

    ip_hash = get_ip_hash(request)
    if not await check_rate_limit(supabase, ip_hash):
        raise HTTPException(
            status_code=429,
            detail="He thong da dat gioi han truy van trong ngay. Vui long thu lai vao ngay mai.",
        )

    # --- Multi-provider route (Phase 4) ---
    rag_data = get_rag_context_for_oracle(question, chapter_cap)
    rag_context = rag_data.get("context_text", "") if rag_data else ""

    result = await call_ai_provider_result(question, chapter_cap, wiki_context, chapter_context, rag_context)
    if result.status == "success" and result.text:
        answer = result.text.strip()
        if answer and not is_garbage_answer(answer):
            await store_cache(supabase, question_hash, chapter_cap, answer, "ai_provider")
            return OracleResponse(answer=answer, source="ai_provider", chapter_cap=chapter_cap)

    # Collect router failure details
    router_error_details = []
    if result.attempts:
        for a in result.attempts:
            if a.get('status') == 'failed':
                router_error_details.append(f"{a.get('provider')} ({a.get('model')}): {a.get('reason')} - {a.get('message')}")

    # No fallback to Gemini! Direct exception raised.
    err_msg = "Không thể lấy câu trả lời từ Hệ Thống: Tất cả các nhà cung cấp AI Multi-provider đều báo lỗi hoặc hết hạn ngạch."
    if router_error_details:
        err_msg += f" Chi tiết lỗi: {'; '.join(router_error_details[:3])}"
    raise HTTPException(status_code=503, detail=err_msg)


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
    chosen_key = body.api_key.strip() if body.api_key else ""
    used_saved_key = not bool(body.api_key and body.api_key.strip())
    results: list[AdminAiPlaygroundResult] = []

    for model in models:
        start = perf_counter()
        try:
            answer = await test_multi_provider_model(
                model_name=model,
                prompt=prompt,
                custom_api_key=chosen_key if chosen_key else None
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


@router.post("/rag-preview", response_model=OracleRagPreviewResponse)
async def oracle_rag_preview(
    body: OracleRagPreviewRequest,
    x_oracle_rag_preview_token: Optional[str] = Header(None, alias="X-Oracle-Rag-Preview-Token")
):
    token_env = os.getenv("ORACLE_RAG_PREVIEW_TOKEN")
    if not token_env or not token_env.strip():
        raise HTTPException(
            status_code=403,
            detail="Forbidden: RAG preview token not configured on server."
        )

    if not x_oracle_rag_preview_token or x_oracle_rag_preview_token.strip() != token_env.strip():
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Invalid RAG preview token."
        )

    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase

    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Service Unavailable: Supabase client not initialized."
        )

    try:
        from backend.rag.retrieval import search_story_chunks_hybrid_lexical
        from backend.rag.context_builder import build_rag_context_block

        results = search_story_chunks_hybrid_lexical(
            supabase=supabase,
            query=body.question,
            chapter_cap=body.chapter_progress,
            limit=body.limit
        )

        context_data = build_rag_context_block(results, max_chunks=body.max_chunks)
        chunks_used = context_data.get("chunks_used", 0)

        return OracleRagPreviewResponse(
            ok=True,
            rag_used=chunks_used > 0,
            chunks_used=chunks_used,
            citations=context_data.get("citations", []),
            context_preview=context_data.get("context_text", ""),
            source="story_chunks_hybrid_context"
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service Unavailable: RAG retrieval failed: {str(e)}"
        )


@router.post("/rag-answer-preview", response_model=OracleRagAnswerPreviewResponse)
async def oracle_rag_answer_preview(
    body: OracleRagAnswerPreviewRequest,
    x_oracle_rag_preview_token: Optional[str] = Header(None, alias="X-Oracle-Rag-Preview-Token")
):
    token_env = os.getenv("ORACLE_RAG_PREVIEW_TOKEN")
    if not token_env or not token_env.strip():
        raise HTTPException(
            status_code=403,
            detail="Forbidden: RAG preview token not configured on server."
        )

    if not x_oracle_rag_preview_token or x_oracle_rag_preview_token.strip() != token_env.strip():
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Invalid RAG preview token."
        )

    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase

    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Service Unavailable: Supabase client not initialized."
        )

    try:
        from backend.rag.retrieval import search_story_chunks_hybrid_lexical
        from backend.rag.context_builder import build_rag_context_block

        is_identity = is_identity_question(body.question)
        entity_context_text = ""
        entity_citations = []
        entity_source = None

        if is_identity:
            entity_res = await get_entity_context_for_oracle(supabase, body.question, body.chapter_progress)
            if entity_res:
                entity_context_text = entity_res["context_text"]
                entity_citations = entity_res["citations"]
                entity_source = entity_res["source"]

        results = search_story_chunks_hybrid_lexical(
            supabase=supabase,
            query=body.question,
            chapter_cap=body.chapter_progress,
            limit=body.limit
        )

        context_data = build_rag_context_block(results, max_chunks=body.max_chunks)
        story_context_text = context_data.get("context_text", "")
        story_citations = context_data.get("citations", [])
        chunks_used = context_data.get("chunks_used", 0)

        has_context = bool(entity_context_text.strip()) or (chunks_used > 0)

        if not has_context:
            return OracleRagAnswerPreviewResponse(
                ok=True,
                rag_used=False,
                chunks_used=0,
                answer="Dữ liệu hiện có chưa đủ để kết luận.",
                citations=[],
                source="rag_answer_preview"
            )

        all_citations = []
        if entity_citations:
            all_citations.extend(entity_citations)
        if story_citations:
            all_citations.extend(story_citations)

        if is_identity:
            if entity_context_text:
                resp_source = "entity_profile_rag_answer_preview"
            else:
                resp_source = "fallback_story_chunks_rag_answer_preview"
        else:
            resp_source = "story_chunks_rag_answer_preview"

        try:
            from main import get_provider_router, resolve_ai_provider_config, AIRequest
        except ImportError:
            from backend.main import get_provider_router, resolve_ai_provider_config, AIRequest

        system_instruction = build_rag_answer_prompt(
            question=body.question,
            entity_context=entity_context_text,
            story_context=story_context_text,
            chapter_cap=body.chapter_progress
        )

        request = AIRequest(
            text=body.question,
            mode="chat",
            system_instruction=system_instruction,
            max_output_tokens=800,
            temperature=0.3,
        )

        router = get_provider_router()
        config = resolve_ai_provider_config()
        policy = config.get("chat_policy", {"mode": "waterfall"})

        result = await router.route(request, policy=policy)

        if result.status == "success" and result.text:
            return OracleRagAnswerPreviewResponse(
                ok=True,
                rag_used=True,
                chunks_used=chunks_used,
                answer=result.text.strip(),
                citations=all_citations,
                source=resp_source
            )

        err_msg = result.error_message or "Router returned empty response"
        raise HTTPException(
            status_code=502,
            detail=f"Bad Gateway: Multi-provider router error: {err_msg}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service Unavailable: RAG answer generation failed: {str(e)}"
        )


class OracleFeedbackRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    answer: Optional[str] = Field(None, max_length=8000)
    source: Optional[str] = Field(None, max_length=100)
    citations: list = Field(default_factory=list)
    chapter_progress: Optional[int] = Field(None, ge=1)
    feedback_type: Literal["wrong", "missing", "spoiler", "hallucination", "other"]
    user_comment: Optional[str] = Field(None, max_length=2000)
    suggested_correction: Optional[str] = Field(None, max_length=4000)


class OracleFeedbackResponse(BaseModel):
    ok: bool
    feedback_id: str
    status: str = "pending"


@router.post("/feedback", response_model=OracleFeedbackResponse)
async def create_oracle_feedback(body: OracleFeedbackRequest):
    if not isinstance(body.citations, list):
        raise HTTPException(status_code=400, detail="Citations must be a list")

    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase

    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )

    feedback_data = {
        "question": body.question,
        "answer": body.answer,
        "source": body.source,
        "citations": body.citations,
        "chapter_progress": body.chapter_progress,
        "feedback_type": body.feedback_type,
        "user_comment": body.user_comment,
        "suggested_correction": body.suggested_correction,
        "status": "pending"
    }

    try:
        res = supabase.table("rag_feedback").insert(feedback_data).execute()
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to record feedback")
        feedback_id = res.data[0]["id"]
        return OracleFeedbackResponse(ok=True, feedback_id=str(feedback_id), status="pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/feedback/pending")
async def get_pending_feedback(
    x_oracle_feedback_admin_token: Optional[str] = Header(None, alias="X-Oracle-Feedback-Admin-Token"),
    limit: int = 50
):
    admin_token = os.getenv("ORACLE_FEEDBACK_ADMIN_TOKEN")
    if not admin_token:
        raise HTTPException(status_code=403, detail="Admin token not configured")

    if not x_oracle_feedback_admin_token or x_oracle_feedback_admin_token != admin_token:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid admin token")

    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase

    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )

    try:
        res = (
            supabase.table("rag_feedback")
            .select("*")
            .eq("status", "pending")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


class FeedbackReviewRequest(BaseModel):
    status: Literal["reviewed", "accepted", "rejected", "resolved"]
    reviewer_note: Optional[str] = Field(None, max_length=2000)


class FeedbackReviewResponse(BaseModel):
    ok: bool
    feedback_id: str
    status: str


@router.patch("/feedback/{feedback_id}", response_model=FeedbackReviewResponse)
async def review_oracle_feedback(
    feedback_id: str,
    body: FeedbackReviewRequest,
    x_oracle_feedback_admin_token: Optional[str] = Header(None, alias="X-Oracle-Feedback-Admin-Token")
):
    admin_token = os.getenv("ORACLE_FEEDBACK_ADMIN_TOKEN")
    if not admin_token:
        raise HTTPException(status_code=403, detail="Admin token not configured")

    if not x_oracle_feedback_admin_token or x_oracle_feedback_admin_token != admin_token:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid admin token")

    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase

    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )

    try:
        # Check if feedback exists
        existing = supabase.table("rag_feedback").select("id").eq("id", feedback_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Feedback not found")

        update_data = {
            "status": body.status,
            "reviewer_note": body.reviewer_note,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        res = supabase.table("rag_feedback").update(update_data).eq("id", feedback_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Feedback not found or update failed")

        return FeedbackReviewResponse(
            ok=True,
            feedback_id=str(res.data[0]["id"]),
            status=res.data[0]["status"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


class CorrectionReviewRequest(BaseModel):
    status: Literal["reviewed", "accepted", "rejected", "resolved", "needs_more_info"]
    reviewer_note: Optional[str] = Field(None, max_length=2000)
    proposed_content: Optional[str] = Field(None)


class CorrectionReviewResponse(BaseModel):
    ok: bool
    correction_id: str
    status: str


@router.get("/corrections/pending")
async def get_pending_corrections(
    x_oracle_feedback_admin_token: Optional[str] = Header(None, alias="X-Oracle-Feedback-Admin-Token"),
    status: str = "draft",
    correction_type: Optional[str] = None,
    limit: int = 50
):
    admin_token = os.getenv("ORACLE_FEEDBACK_ADMIN_TOKEN")
    if not admin_token:
        raise HTTPException(status_code=403, detail="Admin token not configured")

    if not x_oracle_feedback_admin_token or x_oracle_feedback_admin_token != admin_token:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid admin token")

    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase

    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )

    try:
        q = supabase.table("rag_corrections").select("*").eq("status", status)
        if correction_type:
            q = q.eq("correction_type", correction_type)
        res = q.order("created_at", desc=True).limit(limit).execute()
        return res.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.patch("/corrections/{correction_id}", response_model=CorrectionReviewResponse)
async def review_oracle_correction(
    correction_id: str,
    body: CorrectionReviewRequest,
    x_oracle_feedback_admin_token: Optional[str] = Header(None, alias="X-Oracle-Feedback-Admin-Token")
):
    admin_token = os.getenv("ORACLE_FEEDBACK_ADMIN_TOKEN")
    if not admin_token:
        raise HTTPException(status_code=403, detail="Admin token not configured")

    if not x_oracle_feedback_admin_token or x_oracle_feedback_admin_token != admin_token:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid admin token")

    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase

    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )

    status_map = {
        "reviewed": "approved",
        "accepted": "approved",
        "rejected": "rejected",
        "resolved": "applied",
        "needs_more_info": "draft"
    }
    db_status = status_map.get(body.status)
    if not db_status:
        raise HTTPException(status_code=400, detail=f"Invalid status transition: {body.status}")

    try:
        # Check if correction exists and get its type
        existing = supabase.table("rag_corrections").select("id, correction_type").eq("id", correction_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Correction not found")

        corr_type = existing.data[0].get("correction_type")

        update_data = {
            "status": db_status,
            "reviewer_note": body.reviewer_note,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        if body.proposed_content is not None:
            if corr_type != "entity_profile":
                raise HTTPException(status_code=400, detail="Only entity_profile corrections can have their proposed content updated")
            try:
                import json
                parsed = json.loads(body.proposed_content)
                if not isinstance(parsed, dict):
                    raise HTTPException(status_code=400, detail="proposed_content must be a JSON object")
            except (json.JSONDecodeError, TypeError):
                raise HTTPException(status_code=400, detail="proposed_content must be a valid JSON string")

            update_data["proposed_content"] = body.proposed_content

        res = supabase.table("rag_corrections").update(update_data).eq("id", correction_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Correction not found or update failed")

        return CorrectionReviewResponse(
            ok=True,
            correction_id=str(res.data[0]["id"]),
            status=res.data[0]["status"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

