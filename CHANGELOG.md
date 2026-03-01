# Changelog

All notable changes to this project will be documented in this file.

## [2026-03-01]

### Fixed
- **Backend**: Resolved `SyntaxError: unterminated string literal` on line 407 in `main.py`.
- **UI**: Fixed missing Author name on the home page. Added "Tác giả" field to the Quick Stats section.
- **Metadata**: Updated SEO description and keywords in `layout.tsx` to reflect author **Hàn Nhược Tuyết**.
- **DevOps**: Resolved terminal character encoding issue (Japanese output) and PowerShell command syntax.

### Changed
- **Backend**: Updated hardcoded fallback author name to "Hàn Nhược Tuyết".
- **Backend**: Reduced `novel_settings` cache revalidation time to 60 seconds.
- **UI**: Incremented Footer version to `v2.2` to force deployment detection.

### Notes
- **Vercel**: Reached free tier daily deployment limit (100/day). Latest commit `4ad2527` is on GitHub but will deploy once limit resets.

---
*Last updated: 2026-03-01 15:55:00*
