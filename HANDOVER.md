# BIÊN BẢN BÀN GIAO DỰ ÁN (PROJECT HANDOVER)

**Dự án**: Mạt thế sinh hóa nguy cơ (mat-the-website)
**Ngày cập nhật**: 2026-03-25
**Trình trạng**: Đang hiện đại hóa (AI & Security Upgrades)

---

## 1. TÓM TẮT NGỮ CẢNH (CONTEXT)

Đây là một website đọc truyện kết hợp yếu tố Game (RPG/System) mang chủ đề "Mạt thế sinh hóa nguy cơ". Người đọc không chỉ đọc truyện mà còn theo dõi các chỉ số sinh tồn (Survival Stats) thông qua một giao diện HUD sống động.

**Mục tiêu gần đây**:

- Hiện đại hóa hệ thống AI (sử dụng Gemini 3.1 Standards).
- Bảo mật hệ thống AI (BYOK - Bring Your Own Key).
- Củng cố giao diện Headquarters (Sở chỉ huy) cho Commander.

---

## 2. KIẾN TRÚC & CÔNG NGHỆ (ARCHITECTURE)

- **Backend**: FastAPI (Python) + Supabase (Database/Auth).
- **Frontend**: Next.js (App Router) + Tailwind CSS.
- **AI Core**: `ai_oracle.py` hỗ trợ Gemini 3.1. Phối hợp với `hq_snapshots` để phân tích bối cảnh chương truyện.
- **Lưu trữ**: Cloudflare R2 (Ảnh và nội dung chương truyện).

---

## 3. CÁC VIỆC ĐÃ HOÀN THÀNH (DONE)

1.  **Hệ thống HUD Reader**:
    - `ReadingClient.tsx` & `SystemHUD.tsx`: Hiển thị chỉ số sinh tồn, mức độ nguy hiểm, tiến trình chương truyện.
    - **Fix Font**: Đã sửa lỗi encoding (Mojibake) tiếng Việt trong giao diện đọc.
2.  **Cấu hình AI linh hoạt (BYOK)**:
    - Đã thêm cột `ai_api_key` và `ai_model_name` vào bảng `novel` trong Supabase.
    - Backend `ai_oracle.py` tự động lấy Key từ DB nếu có, nếu không sẽ dùng `GEMINI_API_KEY` trong env.
    - Các model mặc định: `gemini-3.1-flash-lite-preview` (2026 standards).
3.  **Deployment (Render)**:
    - Đã xử lý lỗi `ModuleNotFoundError` khi deploy lên Render bằng cách sử dụng **Lazy Imports** trong `main.py`.
4.  **Bảo mật Headquarters (HQ)**:
    - Đã tạo giao diện khóa "Technical Command" bằng `ADMIN_TOKEN` (Command Code).

---

## 4. VIỆC CẦN THỰC HIỆN TIẾP (PENDING/TODO)

Đây là phần CRITICAL mà Agent tiếp theo cần thực hiện:

### ⚡ Chuyển các cài đặt kỹ thuật về Admin Dashboard

- **Vấn đề**: Các cài đặt AI Model và API Key hiện đang nằm ở trang `/headquarters` (vốn dành cho người đọc/người chơi). Điều này không đúng về mặt kiến trúc.
- **Giải pháp**:
    1.  Di chuyển UI cài đặt AI (`ai_model_name`, `ai_api_key`) sang trang **`admin/novel/page.tsx`**.
    2.  Chỉ hiển thị và cho phép chỉnh sửa nếu `userRole === 'superadmin'`.
    3.  Làm sạch trang `Headquarters` (`src/app/(reader)/headquarters/page.tsx`): Gỡ bỏ các input field và logic khóa bằng `ADMIN_TOKEN`, chỉ giữ lại các thông tin diagnostic (read-only) để tăng tính nhập vai.

### 🔍 Lưu ý về File quan trọng:

- `backend/main.py`: Chứa các lazy import cho router.
- `backend/routes/ai_oracle.py`: Logic AI và lấy Key từ DB.
- `frontend/src/app/admin/(dashboard)/novel/page.tsx`: Nơi cần được bổ sung cài đặt AI.
- `frontend/src/app/(reader)/headquarters/page.tsx`: Cần được dọn dẹp (Cleanup).
- `frontend/src/lib/api.ts`: API client để gọi backend (hàm `updateNovelSettings`).

---

## 5. THAM SỐ HỆ THỐNG

- `ADMIN_TOKEN` (trong backend `.env`): Dùng để xác thực các request PUT/POST của admin thay cho Supabase Auth trong một số trường hợp tùy chỉnh.
- `SUPABASE_URL` / `SUPABASE_KEY`: Thông tin kết nối DB.

---

## 6. CHI TIẾT CÁC THAY ĐỔI TRONG PHIÊN (SESSION CHANGES)

Dành cho Agent tiếp theo thực hiện **Audit Code**:

### 🔹 Backend (FastAPI)

- **`main.py`**: Refactor toàn bộ các router import sang dạng hàm (`_get_supabase()`) để tránh lỗi tuần hoàn (circular import) và lỗi `ModuleNotFoundError` khi deploy lên Render.
- **`routes/ai_oracle.py`**:
    - Cập nhật hàm `get_ai_oracle` để đọc `ai_api_key` và `ai_model_name` từ Supabase.
    - Logic fallback: Nếu DB trống thì dùng biến môi trường.
- **`routes/novel.py`**:
    - Thêm endpoint `PUT /api/admin/novel` để admin cập nhật cấu hình.
    - Hàm `get_novel_settings` giờ sẽ ẩn trường `ai_api_key` (chỉ trả về `has_ai_key: true` để frontend biết).

### 🔹 Frontend (Next.js)

- **`lib/api.ts`**:
    - Cập nhật `NovelSettings` interface.
    - Hardening: Bỏ mặc định `adminToken` để ép UI phải truyền token chính xác.
- **`components/ReadingClient.tsx`**:
    - Khôi phục toàn diện font chữ tiếng Việt cho các nút điều hướng (Mojibake fix).
- **`app/(reader)/headquarters/page.tsx`**:
    - Implement hệ thống "Mã lệnh" (Command Code) để xác thực người dùng trước khi hiện nút Lưu (Hiện đang ở giai đoạn proof-of-concept, cần chuyển sang Admin Dashboard thực thụ).
- **`components/SystemHUD.tsx`**:
    - Tích hợp chỉ số sinh tồn và mức độ nguy hiểm dựa trên bối cảnh chương truyện.

---

**LƯU Ý QUAN TRỌNG**: Agent tiếp theo cần ưu tiên việc **Audit logic Auth/Role** trong `admin` dashboard vì hiện tại một số logic đang được demo trực tiếp bằng `ADMIN_TOKEN` thay vì dùng phiên Supabase chuẩn.
