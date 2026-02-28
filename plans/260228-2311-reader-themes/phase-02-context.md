# Phase 02: Xây Dựng Theme Context & Logic

## Objective
Quản lý trạng thái Theme một cách đồng nhất trên toàn bộ ứng dụng (hoặc trang đọc).

## Requirements
- Tạo một React Context để lưu giữ giá trị theme hiện tại.
- Cung cấp hàm `setTheme` để chuyển đổi qua lại.

## Implementation Steps
1. [ ] Tạo file `src/context/ThemeContext.tsx`.
2. [ ] Viết Logic để cập nhật thuộc tính `data-theme` hoặc class lên thẻ `body` hoặc thẻ bao ngoài nội dung truyện.

## Test Criteria
- [ ] State của Theme thay đổi chính xác khi gọi hàm.
- [ ] Giao diện phản ứng ngay lập tức với thay đổi state.
