# Changelog

All notable changes to this project will be documented in this file.

## [2026-03-01] - Phase 2: Wiki & Thả Tim
### Added
- **Cẩm Nang Mạt Thế (Wiki):** Hệ thống tra cứu Nhân vật, Sinh vật, Thế lực.
  - Backend: Endpoints CRUD đầy đủ + Model `wiki_entries`.
  - Admin: Tab quản lý wiki, form thêm mới/sửa với slug tự động.
  - Reader: Trang `/wiki` với sidebar lọc theo Category.
- **Hệ thống Thả Tim ❤️:** Độc giả có thể like từng chương.
  - Backend: Endpoint `/like` tăng count trong database.
  - Frontend: Component `LikeButton` với hiệu ứng animation và ghi nhớ qua `localStorage`.
- **Database:** Bảng `wiki_entries` mới và cột `likes_count` cho bảng `chapters`.

## [2026-03-01] - Part 3: Interaction & Features
### Added
- **Analytics System**: Tracked chapter views and metadata. Added "Top Chapters" dashboard for Admin.
- **Interaction Features**:
    - **Comment System**: Users can now post and view comments on each chapter (Anonymous by default).
    - **Sharing**: Integrated Facebook and Zalo social sharing buttons.
- **Reader Enhancements**:
    - **Reading History**: Added "Tiếp tục đọc" button on the homepage using `localStorage`.
    - **Typography**: Added Font Family setting (Sans-serif vs. Serif/Bookish).
    - **Search**: Enhanced search bar to support title-based lookups and result indicators.

### Fixed
- **Connectivity**: Resolved "Invalid API key" crash by updating `backend/.env` with a valid Supabase Anon key.
- **Backend**: Fixed `total_pages` undefined error in `main.py` which caused 404/500 errors on the frontend.
- **Lints**: Resolved multiple TypeScript/ESLint warnings in `ChaptersPage`.
- **UI**: Corrected main character name from "Hàn Nhược Tuyết" to **Hàn Phong** in the Footer description.

### Changed
- **Reader**: Moved Search Bar to the top and added quick jump buttons for better UX.

## [2026-03-01] - Part 4: Management & World Building
### Added
- **Ngoại Truyện (Side Stories):** Phân loại chương truyện thành Mạch chính và Ngoại truyện.
  - Backend: Thêm cột `is_side_story` và logic lọc API.
  - Admin: Checkbox ghim chương là Ngoại truyện.
  - Reader: Giao diện Tab tách biệt giữa truyện chính và hồ sơ phụ.
- **Trang chủ Linh hoạt (Dynamic Homepage):** Quản lý nội dung Welcome, Warning và Features từ Admin.
  - Database: Bảng `homepage_settings`.
- **Hệ thống Nhân sự (RBAC):** Quản lý Editor và SuperAdmin.
  - Bảo mật: Tích hợp Supabase Auth JWT và phân quyền bảng `profiles`.
  - Admin: Dashboard tuyển dụng, mời thành viên và phân vai trò.
- **Bản đồ Chiến sự (Interactive Map):** 🗺️
  - Công nghệ: `react-leaflet` + CartoDB Dark Matter.
  - Admin: Cắm gờ ghim địa điểm trực tiếp trên bản đồ, lấy tọa độ tự động.
  - Reader: Bản đồ full-screen, Popup thông tin khu vực Safe/Danger.

### Fixed
- **Deployment**: Sửa lỗi thiếu dependency `python-multipart` và lỗi `NameError: List` trong Backend.
- **Security**: Cập nhật `verify_admin` để hỗ trợ xác thực JWT thực tế từ Supabase thay vì chỉ dùng static token.
- **Auth**: Khắc phục lỗi "User not allowed" khi tạo tài khoản bằng cách yêu cầu sử dụng Service Role Key.

---
*Last updated: 2026-03-02 01:00:00*
