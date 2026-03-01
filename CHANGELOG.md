# Changelog

All notable changes to this project will be documented in this file.

## [2026-03-01]

### Fixed
- **Backend**: Resolved `SyntaxError: unterminated string literal` on line 407 in `main.py`.
- **UI**: Fixed missing Author name on the home page. Added "Tác giả" field to the Quick Stats section.
- **Deployment**: Forced Vercel to re-deploy by pushing a trigger commit.

### Changed
- **Backend**: Updated hardcoded fallback author name to "Hàn Nhược Tuyết".
- **Backend**: Reduced `novel_settings` cache revalidation time to 60 seconds.

---
*Last updated: 2026-03-01 15:55:00*
