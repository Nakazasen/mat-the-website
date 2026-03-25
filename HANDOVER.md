# HANDOVER (PROJECT HANDOVER)

Du an: Mat the sinh hoa nguy co (mat-the-website)
Cap nhat: 2026-03-26 (Asia/Bangkok)

## Tom tat

- Da di chuyen toan bo cau hinh AI (Gemini model + API key) ra khoi trang doc gia `/headquarters` sang admin dashboard `/admin/novel`.
- Chi tai khoan `superadmin` moi duoc xem va chinh sua AI settings; tai khoan role thap hon khong the update AI fields (frontend + backend).
- Trang `/headquarters` hien chi con dashboard nhap vai (diagnostic read-only), khong con input ky thuat/command code.
- Da sua loi hien thi tieng Viet (mojibake) tren trang Headquarters do text bi ghi sai encoding.
- Da loai bo cac diem hard-code token: tat ca thao tac admin phai dung Supabase session (`session.access_token`).

## Kien truc (nhanh)

- Frontend: Next.js (App Router) + Tailwind, deploy Vercel.
- Backend: FastAPI, deploy Render.
- DB/Auth: Supabase (Postgres + Auth), role doc tu `profiles.role` (editor/superadmin).
- Storage: Cloudflare R2 (chapter content + images).
- AI: Gemini (BYOK) - key va model luu DB, backend goi Gemini; frontend khong bao gio nhan key.

## Thay doi chinh (2026-03-25 -> 2026-03-26)

### Frontend (Next.js)

- Di chuyen UI AI settings sang Admin Novel:
  - `frontend/src/app/admin/(dashboard)/novel/page.tsx`
  - Chi render va gui `ai_model_name`/`ai_api_key` khi `userRole === 'superadmin'`.
- Cleanup Headquarters thanh read-only dashboard nhap vai:
  - `frontend/src/app/(reader)/headquarters/page.tsx`
  - Bo toan bo input lien quan AI model/API key/command code.
  - Sua lai chuoi tieng Viet bi "S? Ch? Huy" thanh tieng Viet dung.
- API client:
  - `frontend/src/lib/api.ts`
  - `updateNovelSettings(data, token)` bat buoc truyen token, khong con fallback token hard-code.
- Admin navigation:
  - `frontend/src/app/admin/AdminNav.tsx`
  - Bo fallback base URL hard-code production; uu tien `NEXT_PUBLIC_API_URL`.

### Backend (FastAPI)

- Admin update novel settings:
  - `backend/main.py`
  - `PUT /api/admin/novel` chi cho `superadmin` update AI fields (`ai_model_name`, `ai_api_key`).
  - `AdminNovelUpdate` duoc mo rong de ho tro `cover_url` va `donate_qr_url` (khong lam mat du lieu khi admin luu).
- Da hop nhat ve 1 endpoint duy nhat cho `PUT /api/admin/novel` (xoa route trung path).

## Kiem tra nhanh (Runbook)

- Backend:
  - `py -3 -m py_compile backend/main.py`
  - `py -3 -m pytest backend/tests/test_security_utils.py backend/tests/test_rate_limit.py`
- Frontend:
  - `cd frontend; npm run build`
- Manual:
  - Dang nhap editor: khong thay AI settings trong `/admin/novel`; goi update AI fields bi 403.
  - Dang nhap superadmin: thay AI settings, update duoc model va key.
  - `/headquarters`: khong con input ky thuat, tieng Viet hien dung.

## Rủi ro / Debt con lai

- Can them integration test cho role gating `PUT /api/admin/novel` (editor vs superadmin) de tranh regression.
- Rate-limit backend hien la in-memory (scale nhieu instance se khong dong bo).
- Encoding hygiene: tranh ghi file bang tool/co che co the lam mojibake; uu tien patch theo diff (va dam bao UTF-8).
