# Phase 04: Frontend - Trang /wiki cho Độc giả
Status: ⬜ Pending
Dependencies: Phase 03

## Objective
Xây dựng trang `/wiki` đẹp, chuẩn "Vũ trụ Mạt Thế" cho độc giả tra cứu.

## Layout chính

```
/wiki
├── Header: "CẨM NANG MẠT THẾ" (theo phong cách Biohazard)
├── Sidebar (trái): Lọc theo Category
│   ├── Tất cả
│   ├── 👤 Nhân vật
│   ├── 🧟 Sinh vật
│   ├── ⚔️ Thế lực
│   ├── 🗡️ Vật phẩm
│   └── 📍 Địa điểm
└── Grid bài viết (phải): Card của từng entry
    └── Click vào → /wiki/{slug}
```

## /wiki/{slug} (Trang chi tiết)
- Ảnh minh họa (banner)
- Tiêu đề + Category badge
- Tags dạng chip
- Nội dung đầy đủ (render markdown)
- Liên quan: các entry cùng category

## Files to Create
- `frontend/src/app/(reader)/wiki/page.tsx` → [NEW] Trang danh sách
- `frontend/src/app/(reader)/wiki/[slug]/page.tsx` → [NEW] Trang chi tiết

## Implementation Steps
1. [ ] Tạo trang `/wiki` với sidebar lọc category
2. [ ] Tạo component WikiCard cho danh sách
3. [ ] Tạo trang `/wiki/{slug}` chi tiết
4. [ ] Thêm link Wiki vào Header navigation
5. [ ] SEO: Tạo metadata động cho mỗi entry

## Test Criteria
- [ ] Trang /wiki load được danh sách entries
- [ ] Sidebar lọc theo Category hoạt động
- [ ] Click vào 1 entry → /wiki/slug hiển thị đầy đủ

---
Next Phase: phase-05-likes.md
