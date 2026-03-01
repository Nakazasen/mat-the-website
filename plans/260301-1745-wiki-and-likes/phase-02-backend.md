# Phase 02: Backend API (Wiki + Like)
Status: ⬜ Pending
Dependencies: Phase 01

## Objective
Thêm các endpoint API vào `backend/main.py`.

## API Endpoints cần tạo

### Wiki CRUD
- `GET  /api/wiki?category=&search=`  → Lấy danh sách entries
- `GET  /api/wiki/{slug}`              → Lấy chi tiết 1 entry
- `POST /api/wiki` (Admin)             → Tạo entry mới
- `PUT  /api/wiki/{id}` (Admin)        → Sửa entry
- `DELETE /api/wiki/{id}` (Admin)      → Xóa entry

### Like System
- `POST /api/chapters/{number}/like`   → Thêm 1 like vào chương

## Files to Modify
- `backend/main.py` - Thêm các routes mới

## Implementation Steps
1. [ ] Tạo Pydantic model `WikiEntry`
2. [ ] Implement `GET /api/wiki`
3. [ ] Implement `GET /api/wiki/{slug}`
4. [ ] Implement `POST /api/wiki` (yêu cầu admin auth)
5. [ ] Implement `PUT /api/wiki/{id}` (yêu cầu admin auth)
6. [ ] Implement `DELETE /api/wiki/{id}` (yêu cầu admin auth)
7. [ ] Implement `POST /api/chapters/{number}/like`

## Test Criteria
- [ ] GET /api/wiki trả về list (empty ok)
- [ ] POST /api/wiki tạo được entry
- [ ] POST like tăng được likes_count

---
Next Phase: phase-03-admin-ui.md
