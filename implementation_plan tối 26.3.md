# 🛡️ KẾ HOẠCH TRIỂN KHAI: COMMAND CENTER v1.0

**Mục tiêu:** Biến website đọc truyện thành "Trạm Chỉ Huy Tình Báo" - một trải nghiệm nhập vai hoàn toàn cho người đọc.

---

## Phase 1: The System HUD (Reader Overlay)

**Mục tiêu:** Tạo lớp phủ HUD lên trang đọc truyện, bao gồm Danger Level, MC Status, và Quick Scan.

### Frontend

#### [NEW] SystemHUD.tsx
`c:\ProgramData\Sandbox\Web_matthesinhhoanguyco\mat-the-website\frontend\src\components\SystemHUD.tsx`
- Component HUD cố định hai bên màn hình (Framer Motion animation: scanline, pulse).
- Props: `chapterNumber`, `dangerLevel` (0-3), `characterStatus` (Normal/Injured/Mutated).
- Hiển thị: Thanh nhịp tim (SVG path animation), thanh trạng thái màu sắc động.

#### [NEW] CharacterTooltip.tsx
`c:\ProgramData\Sandbox\Web_matthesinhhoanguyco\mat-the-website\frontend\src\components\CharacterTooltip.tsx`
- Tooltip "Quick Scan" hiện ra khi hover tên nhân vật.
- Fetch dữ liệu từ `/api/wiki/character?name=...` (lazy, on-demand).

#### [NEW] useChapterMeta.ts
`c:\ProgramData\Sandbox\Web_matthesinhhoanguyco\mat-the-website\frontend\src\hooks\useChapterMeta.ts`
- Custom hook: nhận `chapterNumber`, trả về `{ dangerLevel, characterStatus, keywords }`.
- Logic: scan nội dung chương tìm từ khóa chiến đấu trong client side.

#### [MODIFY] ReadingClient.tsx
[c:\ProgramData\Sandbox\Web_matthesinhhoanguyco\mat-the-website\frontend\src\components\ReadingClient.tsx](file:///c:/ProgramData/Sandbox/Web_matthesinhhoanguyco/mat-the-website/frontend/src/components/ReadingClient.tsx)
- Import và mount `<SystemHUD />` bên cạnh `contentRef`.
- Bọc tên nhân vật trong nội dung bằng `<CharacterTooltip>` sau khi sanitize HTML.

#### [MODIFY] globals.css
[c:\ProgramData\Sandbox\Web_matthesinhhoanguyco\mat-the-website\frontend\src\app\globals.css](file:///c:/ProgramData/Sandbox/Web_matthesinhhoanguyco/mat-the-website/frontend/src/app/globals.css)
- Thêm CSS vars cho chủ đề "The System" (màu glitch-green, amber, border-glow...).
- Animation keyframes: `@keyframes scanline`, `@keyframes heartbeat-pulse`.

---

## Phase 2: Base HQ Dashboard

**Mục tiêu:** Trang Dashboard hiển thị tài nguyên, dân số, và sức mạnh của phe phái chính theo từng chương.

### Backend

#### [NEW] routes/hq_dashboard.py
`c:\ProgramData\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend\routes\hq_dashboard.py`
- `GET /hq/status?chapter={n}` → trả về `{ food_days, crystal_count, warriors, researchers, wall_level }`.
- Logic: đọc từ bảng `hq_snapshots` trong Supabase, lấy snapshot gần nhất với chapter ≤ n.

#### [MODIFY] main.py
[c:\ProgramData\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend\main.py](file:///c:/ProgramData/Sandbox/Web_matthesinhhoanguyco/mat-the-website/backend/main.py)
- Đăng ký router `hq_dashboard` vào FastAPI app.

### Database (Supabase)

#### [NEW] supabase_hq_schema.sql
`c:\ProgramData\Sandbox\Web_matthesinhhoanguyco\mat-the-website\scripts\supabase_hq_schema.sql`
- Tạo bảng `hq_snapshots (id, chapter_id, food_days INT, crystal_count INT, warriors INT, researchers INT, wall_level INT)`.

### Frontend

#### [NEW] app/(reader)/headquarters/page.tsx
`c:\ProgramData\Sandbox\Web_matthesinhhoanguyco\mat-the-website\frontend\src\app\(reader)\headquarters\page.tsx`
- Trang Dashboard: fetch `/hq/status` theo chapter người dùng đang đọc.
- Hiển thị: Progress bars cho tài nguyên, số liệu dân số, Danger Zone map-mini.

---

## Phase 3: AI Intelligence Core (Backend Proxy + Cache)

**Mục tiêu:** Tích hợp Gemini AI an toàn và tiết kiệm thông qua Backend Proxy + caching thông minh.

### Backend

#### [NEW] routes/ai_oracle.py
`c:\ProgramData\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend\routes\ai_oracle.py`
- `POST /oracle/ask` → nhận `{ question, chapter_progress }`.
- **Tầng 1 (Cache):** Hash câu hỏi + chapter → tra trong bảng `oracle_cache` Supabase.
- **Tầng 2 (Local):** Tìm kiếm keyword trong Wiki DB. Nếu đủ thông tin → trả về ngay.
- **Tầng 3 (Gemini):** Gọi `google-generativeai` với System Prompt giới hạn theo `chapter_progress`. Lưu kết quả vào cache.
- API Key đọc từ `os.environ["GEMINI_API_KEY"]` — **không bao giờ expose ra Frontend**.
- Rate limiting: 10 requests/user/day (theo IP + user session).

#### [NEW] routes/wiki_search.py
`c:\ProgramData\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend\routes\wiki_search.py`
- `GET /wiki/character?name=...&chapter={n}` → tìm nhân vật trong Wiki, lọc theo chapter.
- Phục vụ tính năng Quick Scan của HUD.

#### [MODIFY] main.py
- Đăng ký các router mới: `ai_oracle`, `wiki_search`.

### Database (Supabase)

#### [NEW] supabase_oracle_cache.sql
- Tạo bảng `oracle_cache (id, question_hash TEXT UNIQUE, chapter_cap INT, response TEXT, created_at TIMESTAMPTZ)`.
- Index trên `question_hash` để lookup O(1).

### Frontend

#### [NEW] OraclePanel.tsx
`c:\ProgramData\Sandbox\Web_matthesinhhoanguyco\mat-the-website\frontend\src\components\OraclePanel.tsx`
- Chat widget phong cách terminal (font JetBrains Mono).
- Gửi câu hỏi đến `/oracle/ask`, hiển thị loading "SCANNING DATABASE...", hiện kết quả với hiệu ứng typewriter.
- Khi rate limit bị chạm: "⚡ HỆ THỐNG BỊ NHIỄU SÓNG ĐIỆN TỪ. THỬ LẠI SAU 30 GIÂY."

---

## 📋 Lộ trình thực hiện

| Phase | Tính năng | Độ phức tạp | Thứ tự |
|-------|-----------|-------------|--------|
| 1 | Reader HUD + Quick Scan | ⭐⭐ | 1 (Làm trước) |
| 2 | Base HQ Dashboard | ⭐⭐⭐ | 2 |
| 3 | AI Oracle + Cache | ⭐⭐⭐⭐ | 3 |

---

## ✅ Kế hoạch Kiểm thử (Verification Plan)

### Phase 1 — Automated Tests
- File test hiện có: [backend/tests/test_rate_limit.py](file:///c:/ProgramData/Sandbox/Web_matthesinhhoanguyco/mat-the-website/backend/tests/test_rate_limit.py), [backend/tests/test_security_utils.py](file:///c:/ProgramData/Sandbox/Web_matthesinhhoanguyco/mat-the-website/backend/tests/test_security_utils.py).
- Kiểm tra HUD component: test tự động bằng cách chạy dev server và xem log.

### Phase 1 — Manual Tests (Thủ công)
1. Chạy `npm run dev` trong `frontend/`.
2. Mở trang đọc bất kỳ (VD: `http://localhost:3000/chapters/1`).
3. **Quan sát:** HUD hiển thị ở bên phải màn hình, có animation nhịp tim.
4. **Quan sát:** Thanh Danger Level tắt để màu xanh (chương bình thường) hoặc đỏ (chương chiến đấu).
5. Di chuột vào một tên nhân vật → Tooltip "Quick Scan" hiện ra.

### Phase 2 — Manual Tests
1. Truy cập `http://localhost:3000/headquarters`.
2. **Quan sát:** Dashboard hiển thị các thanh tài nguyên.
3. Thay đổi chapter parameter → **Quan sát** chỉ số thay đổi tương ứng.

### Phase 3 — Manual Tests + Backend
1. Gọi `POST http://localhost:8000/oracle/ask` với body `{"question": "Trần Phong là ai?", "chapter_progress": 10}` bằng curl/Postman.
2. **Quan sát:** Response trả về JSON hợp lệ, không chứa thông tin về chương > 10.
3. Gọi lần 2 với cùng câu hỏi → **Quan sát:** Response nhanh hơn (từ cache).
4. Gọi 11 lần → **Quan sát:** Response trả về lỗi rate limit.
