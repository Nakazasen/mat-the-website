# Phase 03: Admin UI - Quản lý Wiki
Status: ⬜ Pending
Dependencies: Phase 02

## Objective
Thêm tab "📚 Wiki" trong trang Admin, cho phép anh Thêm / Sửa / Xóa bài viết wiki và upload ảnh lên R2.

## UI Components cần tạo

### Tab Danh sách Wiki
- Bảng hiển thị tất cả entries (Title, Category, Ngày tạo)
- Filter theo Category
- Nút "Thêm mới" và nút Sửa/Xóa trên từng dòng

### Form Thêm/Sửa Wiki Entry
- Input: Tiêu đề (Title)
- Dropdown: Category (Nhân vật | Sinh vật | Thế lực | Vật phẩm | Địa điểm)
- Input: Tags (nhập tự do, phân cách bằng dấu phẩy)
- Textarea: Tóm tắt ngắn (Summary)
- Textarea: Nội dung đầy đủ (Content - markdown)
- Upload ảnh: Upload lên R2, tự điền Image URL

## Files to Create/Modify
- `frontend/src/app/admin/(dashboard)/wiki/page.tsx` → [NEW] Tab danh sách wiki
- `frontend/src/app/admin/(dashboard)/wiki/new/page.tsx` → [NEW] Form thêm mới
- `frontend/src/app/admin/(dashboard)/wiki/[id]/page.tsx` → [NEW] Form sửa
- `frontend/src/lib/api.ts` → Thêm các hàm gọi wiki API

## Implementation Steps
1. [ ] Tạo route admin wiki list page
2. [ ] Tạo form Thêm mới / Sửa entry
3. [ ] Tích hợp upload ảnh lên R2
4. [ ] Kết nối form với API endpoint
5. [ ] Thêm nút Xóa với confirm dialog

## Test Criteria (Tiêu chí "test con Zombie")
- [ ] Anh điền form một entry Zombie Cấp 1 với ảnh
- [ ] Bấm "Lưu" → Entry xuất hiện trong danh sách
- [ ] Bấm "Sửa" → Đổi tên → Lưu lại thành công
- [ ] Bấm "Xóa" → Entry biến mất

---
Next Phase: phase-04-frontend-wiki.md
