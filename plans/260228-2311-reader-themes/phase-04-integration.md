# Phase 04: Tích Hợp Vào ReadingClient

## Objective
Áp dụng theme đã chọn vào nội dung truyện thực tế.

## Requirements
- Sử dụng màu từ CSS Variables đã định nghĩa ở Phase 01.
- Đảm bảo các nút điều hướng (Trước/Sau) vẫn hiển thị rõ ràng trên mọi nền.

## Implementation Steps
1. [ ] Bọc `ReadingClient` trong `ThemeProvider`.
2. [ ] Thay thế các class Fix cứng màu sắc bằng các class Tailwind sử dụng CSS Variables.

## Test Criteria
- [ ] Nội dung truyện đổi màu đồng bộ khi chọn theme.
- [ ] Không có hiện tượng chữ bị chìm vào nền (ví dụ: chữ đen trên nền đen).
