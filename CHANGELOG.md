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
## [2026-03-02] - Part 5: Full Content Rendering & UX
### Added
- **Rich Karaoke Engine**: New logic to support visual highlighting (Karaoke) on HTML-rich chapters while preserving images and formatting.
- **Comprehensive HTML Audit**: Enabled rich text rendering across Home, Map, and Wiki sections.
- **Admin Panel Improvements**: 
    - Fixed image upload by adding `ADMIN_TOKEN` fallbacks and relative API paths.
    - Verified image upload functionality across all admin tabs (Chapters, Wiki, Map, etc.).

### Fixed
- **Reader Contrast**: Resolved "faded text" issue in light and sepia themes by improving CSS variable inheritance.
- **Bookmarks**: 
    - Fixed prominence of the bookmark button.
    - Resolved "Chapter deleted" bug in profiles by identifying RLS policy requirements.
- **TTS**: Made the Text-to-Speech engine HTML-aware to prevent reading raw tags.

---
## [2026-03-03] - Part 6: Mobile UX & Dashboard Reliability
### Fixed
- **Mobile Contrast**: Optimized Home Page Hero section to maintain high contrast regardless of active reader theme (Light, Sepia, or Dark).
- **Admin Dashboard**: Resolved data loading failure in "Top 5 Most Read" and "Top 5 Most Liked" sections by removing invalid database queries.
- **Header Visibility**: Increased brightness of navigation links and secondary descriptions to improve readability on smaller screens.

### Changed
- **Styling**: Introduced `.rich-text-home` and fixed-color button utilities for better design consistency on fixed-background sections.
- **Workflow**: Integrated AWF 4.0.2 for improved project memory and status tracking.

## [2026-03-07] - Part 7: Stability & Rendering Critical Fixes
### Fixed
- **React Error #137 (Void Elements)**: Resolved a critical client-side crash in `karaoke.tsx` by separating void elements (like `<br>`, `<hr>`, `<img>`) to prevent them from receiving children.
- **Hydration Mismatch**: Fixed persistent "Application error: a client-side exception has occurred" by:
    - Adding `isMounted` hooks to `ReadingClient.tsx` to defer rich rendering until client-mount.
    - Adding `suppressHydrationWarning` to avoid theme-related attribute mismatches.
    - Ensuring `ThemeContext.tsx` only accesses `document` on the client side.
- **Performance & OOM**: Replaced `Math.random()` React keys with deterministic path-based keys in the Karaoke engine to prevent re-render loops and memory exhaustion on long chapters.
- **Build Reliability**: Converted dynamic `require()` calls to static ES imports in `AudioPlayer.tsx` to ensure correct bundling in production.

### Changed
- **Karaoke Engine**: Optimized recursive rendering to use fixed keys, significantly reducing CPU usage during audio playback.

---
## [2026-03-13] - Part 8: Wiki Optimization & Immediate Updates
### Added
- **Wiki Image Guidelines**: Created comprehensive documentation for image ratios (21:9/16:9) and resolutions to ensure high-quality display in both list and detail views.
- **Instant Wiki Updates**: Optimized the reader experience by disabling cache on Wiki entry fetching, allowing editorial changes to reflect immediately.

### Fixed
- **Wiki Detail Cache**: Resolved the 5-minute delay issue where new images or content edits wouldn't show up in the detail view because of Next.js ISR/Data Cache.

### Changed
- **Frontend API**: Updated `getWikiEntry` in `lib/api.ts` to use `cache: "no-store"`.
- **Deployment Trigger**: Added a timestamp-based trigger in `backend/main.py` to ensure Render redeploys in sync with Vercel for backend-dependent changes.

---
## [2026-03-14] - Part 9: Content Editor Enhancements & Build Stability
### Added
- **Clean Text Feature ✨:** Added a button to the Rich Text Editor to automatically remove redundant empty paragraphs and extra line breaks.
  - Useful for cleaning up content pasted from Google Docs or Microsoft Word.
  - Integrated into the Editor Toolbar with a yellow sparkle icon.
  - Supports Undo/Redo operations.

### Fixed
- **Build Stability (JSX Syntax):** Resolved a critical Vercel deployment failure caused by an unclosed `<button>` tag in `EditorToolbar.tsx`.
- **Editor Linting:** Fixed Tiptap `setContent` options type error to align with the latest API.

---
*Last updated: 2026-03-14 08:00:00*
