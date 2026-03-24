from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from supabase import Client

try:
    from rate_limit import InMemoryCooldownLimiter, get_client_ip
    from security_utils import sanitize_plaintext
except ModuleNotFoundError:
    from backend.rate_limit import InMemoryCooldownLimiter, get_client_ip
    from backend.security_utils import sanitize_plaintext


VIEW_COOLDOWN_SECONDS = 15
LIKE_COOLDOWN_SECONDS = 10
COMMENT_COOLDOWN_SECONDS = 20


class CommentCreate(BaseModel):
    user_name: str
    content: str


def create_engagement_router(supabase: Client) -> APIRouter:
    router = APIRouter()
    limiter = InMemoryCooldownLimiter()

    @router.post("/api/chapters/{chapter_number}/view", summary="Tăng lượt đọc chương")
    async def increment_view(chapter_number: int, request: Request):
        client_ip = get_client_ip(request)
        key = f"view:{client_ip}:{chapter_number}"
        allowed, retry_after = limiter.allow(key, VIEW_COOLDOWN_SECONDS)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Bạn thao tác quá nhanh, vui lòng thử lại sau.",
                headers={"Retry-After": str(retry_after)},
            )

        try:
            supabase.rpc("increment_chapter_view", {"chapter_num": chapter_number}).execute()
            return {"status": "success"}
        except Exception as e:
            try:
                for _ in range(5):
                    resp = (
                        supabase.table("chapters")
                        .select("id, view_count")
                        .eq("chapter_number", chapter_number)
                        .single()
                        .execute()
                    )
                    if not resp.data:
                        break
                    chapter_id = resp.data["id"]
                    current_views = resp.data.get("view_count") or 0
                    updated = (
                        supabase.table("chapters")
                        .update({"view_count": current_views + 1})
                        .eq("id", chapter_id)
                        .eq("view_count", current_views)
                        .execute()
                    )
                    if updated.data:
                        return {"status": "success", "note": "manual_update"}
            except Exception:
                pass
            return {"status": "error", "detail": str(e)}

    @router.post("/api/chapters/{chapter_number}/comments", summary="Gửi bình luận mới")
    async def create_comment(chapter_number: int, body: CommentCreate, request: Request):
        client_ip = get_client_ip(request)
        key = f"comment:{client_ip}:{chapter_number}"
        allowed, retry_after = limiter.allow(key, COMMENT_COOLDOWN_SECONDS)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Bạn bình luận quá nhanh, vui lòng thử lại sau.",
                headers={"Retry-After": str(retry_after)},
            )

        try:
            safe_name = sanitize_plaintext(body.user_name) or "ẩn danh"
            safe_content = sanitize_plaintext(body.content) or ""
            if len(safe_content) < 1 or len(safe_content) > 2000:
                raise HTTPException(status_code=400, detail="Nội dung bình luận không hợp lệ")
            data = {
                "chapter_number": chapter_number,
                "user_name": safe_name,
                "content": safe_content,
            }
            result = supabase.table("comments").insert(data).execute()
            return {"status": "success", "comment": result.data[0]}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/api/chapters/{chapter_number}/comments", summary="Lấy danh sách bình luận")
    async def get_comments(chapter_number: int, limit: int = 50):
        try:
            resp = (
                supabase.table("comments")
                .select("*")
                .eq("chapter_number", chapter_number)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            comments = resp.data or []
            for comment in comments:
                comment["user_name"] = sanitize_plaintext(comment.get("user_name")) or "ẩn danh"
                comment["content"] = sanitize_plaintext(comment.get("content")) or ""
            return comments
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/api/chapters/{chapter_number}/like", summary="Thả tim chương")
    async def like_chapter(chapter_number: int, request: Request):
        client_ip = get_client_ip(request)
        key = f"like:{client_ip}:{chapter_number}"
        allowed, retry_after = limiter.allow(key, LIKE_COOLDOWN_SECONDS)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Bạn thao tác quá nhanh, vui lòng thử lại sau.",
                headers={"Retry-After": str(retry_after)},
            )

        try:
            for _ in range(5):
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
                updated = (
                    supabase.table("chapters")
                    .update({"likes_count": current_likes + 1})
                    .eq("id", chapter_id)
                    .eq("likes_count", current_likes)
                    .execute()
                )
                if updated.data:
                    return {"status": "ok", "likes_count": current_likes + 1}

            raise HTTPException(status_code=409, detail="Xung đột lượt thích, vui lòng thử lại")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
