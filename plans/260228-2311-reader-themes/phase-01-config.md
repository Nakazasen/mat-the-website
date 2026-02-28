# Phase 01: Cấu Hình CSS Variables & Tailwind

## Objective
Thiết lập bộ biến màu sắc làm nền tảng cho việc chuyển đổi giao diện (Theme).

## Requirements
- Định nghĩa các biến CSS cho Nền (Background) và Chữ (Text) trong `globals.css`.
- Hỗ trợ 3 bộ màu: Toxic Dark (Mặc định), Light (Sáng), Sepia (Vàng nhạt).

## Implementation Steps
1. [ ] Cập nhật `src/app/globals.css` với các biến mới (ví dụ: `--reader-bg`, `--reader-text`).
2. [ ] Cập nhật `tailwind.config.ts` để sử dụng các biến CSS này dưới dạng các thẻ màu tùy chỉnh.

## Test Criteria
- [ ] Các biến CSS được nạp thành công vào trình duyệt.
- [ ] Có thể thay đổi màu toàn trang bằng cách thay đổi giá trị biến thủ công trong DevTools.
