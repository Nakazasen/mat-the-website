# Phase 05: Frontend - Nút Thả Tim ❤️
Status: ✅ Done
Dependencies: Phase 02

## Objective
Thêm nút ❤️ (Thả tim) ở cuối mỗi trang đọc chương. Không bắt đăng nhập.

## Logic hoạt động
1. Người đọc bấm ❤️
2. Frontend check `localStorage` → nếu chưa bấm chương này
3. Gọi `POST /api/chapters/{number}/like`
4. Lưu vào `localStorage["liked_chapter_X"] = true`
5. Nút đổi màu đỏ rực + hiệu ứng pulse
6. Nếu bấm lại → Hiện tooltip "Anh đã thả tim rồi!" (không trừ tim)

## Files to Modify
- `frontend/src/components/ReadingClient.tsx` → Thêm component LikeButton
- `frontend/src/lib/api.ts` → Thêm hàm `likeChapter()`

## Implementation Steps
1. [x] Tạo hàm `likeChapter()` trong api.ts
2. [x] Tạo component `LikeButton` (client component)
3. [x] Tích hợp vào ReadingClient.tsx (đặt ngay trên khu vực bình luận)
4. [x] Thêm hiệu ứng animation khi bấm tim

## Test Criteria
- [ ] Nút tim hiển thị ở cuối chương
- [ ] Bấm lần 1 → Nút đổi màu đỏ
- [ ] Bấm lần 2 → Có tooltip "đã thả tim"
- [ ] Reload trang → Nút vẫn đỏ (nhớ từ localStorage)
- [ ] Check Supabase → likes_count của chương tăng 1

---
Next Phase: phase-06-testing.md
