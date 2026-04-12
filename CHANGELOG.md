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
## [2026-03-14] - Part 10: Faction Hierarchy & Performance
### Added
- **Sơ đồ Tổ chức (Faction Hierarchy):** 🌳
  - Backend: Table `faction_members` với cơ chế `parent_id` cho phép cây nhân sự vô hạn cấp.
  - Admin: Component `FactionHierarchyEditor` trực quan, cho phép kéo thả/gán nhân vật và chức danh.
  - Reader: Component `FactionOrgChart` tự động hiển thị theo tầng (Tiers) dựa trên `rank_level` hoặc theo sơ đồ cây.
  - Phân loại màu sắc: Rank 0 (Vàng), Rank 1 (Xanh lá), Rank 2 (Xanh lơ - Cyan).
- **Tối ưu Upload Ảnh (Image Compression):** ⚡
  - Tích hợp `browser-image-compression` để nén ảnh ngay tại trình duyệt.
  - Tự động nén file 7MB-10MB xuống ~1.5MB trước khi upload, tăng tốc độ 5-10 lần.
  - Fix lỗi trùng tên ảnh bằng cách sử dụng UUID cho mỗi file upload lên R2.

### Fixed
- **Admin UX:** 
  - Vô hiệu hóa nút Lưu khi đang upload ảnh để tránh mất dữ liệu.
  - Thêm spinner loading cho nút Upload.
  - Sửa lỗi hiển thị dàn hàng ngang của sơ đồ tổ chức khi chưa gán cha-con.

*Last updated: 2026-03-14 18:30:00*

---
## [2026-03-15] - Part 11: Wiki Pagination & Reader Customization
### Added
- **Wiki Pagination:** 📖
  - Backend: Updated `/api/wiki` with `page` and `limit` parameters using Supabase `.range()`. Returns total item count and metadata.
  - Reader: Implemented "Previous/Next" navigation and dynamic URL-based state (`?page=X`).
  - Admin: Integrated pagination into the management list to handle 50+ entries.
- **Wiki Reader Settings:** ⚙️
  - Added a customization panel to the Wiki section (Index & Detail views).
  - Users can now adjust Theme (Dark, Light, Sepia, etc.), Font Size, and Font Family on the Wiki, matching the reading experience of chapters.
- **Admin Enhancements:**
  - Added "Sort Order" (Thứ tự sắp xếp) and "Is Main" (Nổi bật/Chính) toggles to the Wiki entry form.

### Fixed
- **Entry Visibility:** Resolved the issue where entries (like "Hồ Du") would disappear when pushed past the first 50 items.
- **Backend Sorting:** Fixed a fatal typo `nulls_first` -> `nullsfirst` in the Python Supabase client that caused 500 errors.
- **Deployment Compatibility:** Added a backward-compatibility layer in the frontend to handle both old (array) and new (paginated object) API response formats during deployment transitions.

### Changed
- **API Client:** Updated `getWikiEntries` in `lib/api.ts` to support paginated response types.
- **Character Picker:** Updated `FactionHierarchyEditor` to fetch up to 1000 characters to ensure full list availability for hierarchy building.

---
## [2026-03-28] - Part 12: Admin UX & HUD Localization
### Added
- **SystemHUD Localization:** 🌐
  - Hỗ trợ đa ngôn ngữ (VI, EN, ZH, JA) cho toàn bộ nhãn trong HUD.
  - Tích hợp hook `useLocale` và hệ thống từ điển `dictionaries.ts`.
  - Tự động cập nhật trạng thái (Normal, Injured, Mutated, Critical) theo ngôn ngữ.
- **Admin Chapters Responsive:** 📱
  - Refactor giao diện quản lý chương sang dạng card-view trên mobile.
  - Đảm bảo các nút "Dịch", "Sửa", "Xóa" luôn hiển thị và dễ thao tác trên màn hình nhỏ.

### Fixed
- **I18n Dictionaries:** Export `dictionaries` object trong `dictionaries.ts` để hỗ trợ các script validation bên ngoài.
- **Hydration Mismatch:** Xử lý dynamic labels để tránh lỗi đồng bộ khi trình duyệt tự động dịch trang.

### Changed
- **Deployment Policy:** Thiết lập quy trình tự động push GitHub và rebuild Vercel/Render sau mỗi thay đổi quan trọng.

*Last updated: 2026-03-28 06:45:00*

---
## [2026-04-08] - Part 13: Header Navigation State Sync

### Fixed

- **Navigation Resets:** Resolved a critical UX issue where the "Đọc tiếp" (Continue Reading) button in the Header would sometimes loop, refresh the same page, or reset progress to Chapter 1.
- **Hydration / State Synchronization:**
  - Implemented a robust custom event listener (`chapter-read-updated`) to sync `localStorage` changes to the Header in real-time.
  - Fixed hydration mismatches by ensuring dynamic UI elements only render after client-side mounting.

### UI Logic

- The Header button now dynamically toggles between **"Đọc ngay"** (Read Now - Blood Red) for new users and **"Đọc tiếp"** (Continue Reading - Toxic Green) for returning readers.
- Added logic to hide the dynamic navigation button when the user is already viewing a chapter to streamline the interface and prevent navigation loops.

*Last updated: 2026-04-08 01:20:00*
