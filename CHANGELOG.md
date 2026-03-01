# Changelog

All notable changes to this project will be documented in this file.

## [2026-03-01] - Part 2

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

---
*Last updated: 2026-03-01 17:30:00*
