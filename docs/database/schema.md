# Database Schema - Mạt Thế

**Provider:** Supabase (PostgreSQL)
**Last Updated:** 2026-03-02

---

## 📖 Bảng: `chapters`
Lưu trữ thông tin metadata của các chương truyện.

| Cột | Kiểu dữ liệu | Mô tả |
|-----|--------------|-------|
| id | UUID/INT | Primary Key |
| chapter_number | INT | Số chương (để link với tệp .txt trên R2) |
| title | TEXT | Tiêu đề chương |
| view_count | INT | Lượt xem (mặc định 0) |
| likes_count | INT | Lượt thả tim (mặc định 0) |
| is_side_story | BOOLEAN | true nếu là ngoại truyện, false nếu là mạch chính |
| created_at | TIMESTAMPTZ | Thời gian tạo |

---

## ⚙️ Bảng: `novel_settings`
Cấu hình thông tin chung của bộ truyện (Chỉ 1 dòng).

| Cột | Kiểu dữ liệu | Mô tả |
|-----|--------------|-------|
| id | INT | Primary Key |
| title | TEXT | Tiêu đề truyện |
| author | TEXT | Tác giả |
| description | TEXT | Mô tả / Giới thiệu |
| cover_url | TEXT | Link ảnh bìa (R2) |
| status | TEXT | Trạng thái (Đang cập nhật, Hoàn thành...) |
| genres | JSONB | Danh sách thể loại |

---

## 💬 Bảng: `comments`
Lưu trữ bình luận của độc giả.

| Cột | Kiểu dữ liệu | Mô tả |
|-----|--------------|-------|
| id | UUID | Primary Key |
| chapter_number | INT | Link tới chương truyện |
| user_name | TEXT | Tên người dùng (mặc định "Người sống sót") |
| content | TEXT | Nội dung bình luận |
| created_at | TIMESTAMPTZ | Thời gian tạo |

---

## 📚 Bảng: `wiki_entries`
Lưu trữ các mục bách khoa toàn thư.

| Cột | Kiểu dữ liệu | Mô tả |
|-----|--------------|-------|
| id | UUID | Primary Key |
| slug | TEXT | URL-friendly name (unique) |
| title | TEXT | Tên mục bách khoa |
| content | TEXT | Nội dung chi tiết (HTML từ Tiptap) |
| category | TEXT | Phân loại (Nhân vật, Sinh vật...) |
| image_url | TEXT | Link ảnh minh họa |

---

## 🏠 Bảng: `homepage_settings`
Quản lý nội dung động trên trang chủ.

| Cột | Kiểu dữ liệu | Mô tả |
|-----|--------------|-------|
| id | INT | Primary Key (thường là 1) |
| warning_title | TEXT | Tiêu đề vùng cảnh báo |
| warning_subtitle | TEXT | Phụ đề cảnh báo |
| warning_headline | TEXT | Nội dung nhấn mạnh |
| warning_description | TEXT | Mô tả chi tiết cảnh báo |
| features_title | TEXT | Tiêu đề phần tính năng |
| features_json | JSONB | Danh sách features (icon, title, desc) |

---

## 👤 Bảng: `profiles`
Quản lý thông tin và phân quyền nhân sự.

| Cột | Kiểu dữ liệu | Mô tả |
|-----|--------------|-------|
| id | UUID | Link tới `auth.users` của Supabase |
| email | TEXT | Email nhân sự |
| role | TEXT | Vai trò: `superadmin` hoặc `editor` |
| display_name | TEXT | Tên hiển thị |

---

## 🗺️ Bảng: `map_locations`
Lưu trữ các điểm ghim trên bản đồ chiến sự.

| Cột | Kiểu dữ liệu | Mô tả |
|-----|--------------|-------|
| id | UUID | Primary Key |
| name | TEXT | Tên địa điểm |
| type | TEXT | Loại: `safe_zone`, `danger_zone`, `ruins`, etc. |
| description | TEXT | Mô tả khu vực |
| lat | FLOAT8 | Vĩ độ |
| lng | FLOAT8 | Kinh độ |
| ---

## 🌳 Bảng: `faction_members`
Lưu trữ sơ đồ tổ chức/gia phả của các thế lực.

| Cột | Kiểu dữ liệu | Mô tả |
|-----|--------------|-------|
| id | UUID | Primary Key |
| faction_id | UUID | Link tới `wiki_entries` (của thế lực đó) |
| character_id | UUID | (Optional) Link tới `wiki_entries` (nhân vật) |
| parent_id | UUID | (Self-reference) ID của cấp trên trực tiếp |
| role_title | TEXT | Chức danh (VD: Đoàn trưởng, Đại đội trưởng...) |
| division | TEXT | Khối/Bộ phận (VD: Quân đội, Dân sự) |
| rank_level | INT | Cấp bậc (0=Đỉnh, 1, 2...) để định dạng hiển thị |
| sort_order | INT | Thứ tự sắp xếp ngang hàng |
| created_at | TIMESTAMPTZ | Thời gian tạo |

