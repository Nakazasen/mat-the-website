# API Documentation - Mạt Thế

**Ngày cập nhật:** 2026-03-01
**Base URL:** `http://localhost:8000` / `https://[render-app].onrender.com`

---

## 📚 Chapters

### GET /api/chapters
Lấy danh sách chương có phân trang và tìm kiếm.

**Query Params:**
- `page`: int (mặc định 1)
- `limit`: int (mặc định 50, tối đa 100)
- `sort`: "asc" | "desc"
- `search`: string (tìm theo số chương hoặc tiêu đề)

---

### GET /api/chapters/{chapter_number}
Lấy metadata chi tiết của một chương.

---

### POST /api/chapters/{chapter_number}/view
Analytics: Tăng số lượt xem cho chương. Gọi tự động sau 15-20s đọc.

---

## 💬 Comments

### GET /api/chapters/{chapter_number}/comments
Lấy danh sách bình luận của chương.

**Response:**
```json
[
  {
    "id": 1,
    "user_name": "Operator Đức",
    "content": "Tuyệt vời!",
    "created_at": "2026-03-01T..."
  }
]
```

---

### POST /api/chapters/{chapter_number}/comments
Đăng bình luận mới.

**Body:**
```json
{
  "user_name": "Tên người dùng",
  "content": "Nội dung bình luận"
}
```

---

### GET /api/admin/comments
(Admin) Lấy danh sách toàn bộ bình luận trong hệ thống, hỗ trợ phân trang.

**Query Params:**
- `page`: int (mặc định 1)
- `limit`: int (mặc định 50, tối đa 100)

**Headers:** `Authorization: Bearer {admin_token}`

---

### PUT /api/admin/comments/{id}
(Admin) Sửa nội dung bình luận theo ID.

**Body:**
```json
{
  "content": "Nội dung mới"
}
```

**Headers:** `Authorization: Bearer {admin_token}`

---

### DELETE /api/admin/comments/{id}
(Admin) Xóa bình luận theo ID.

**Headers:** `Authorization: Bearer {admin_token}`

---

## 📊 Analytics (Admin)

### GET /api/admin/analytics/top-chapters
Lấy danh sách 5 chương có lượt xem cao nhất.

**Headers:** `Authorization: Bearer {admin_token}`

---

## ⚙️ Novel Settings

### GET /api/novel
Lấy thông tin cấu hình truyện (Tên, Tác giả, Ảnh bìa, Thể loại).

---

## ❤️ Like System

### POST /api/chapters/{chapter_number}/like
Thả tim cho một chương truyện.

**Response (200):**
```json
{
  "status": "ok",
  "likes_count": 42
}
```

---

## 📚 Wiki / Bách Khoa

### GET /api/wiki
Lấy danh sách bách khoa.

**Query Parameters:**
- `category`: Lọc theo loại (Nhân vật, Sinh vật...)
- `search`: Tìm kiếm theo tiêu đề

### GET /api/wiki/{slug}
Chi tiết một mục bách khoa.

### POST /api/wiki (Admin)
Tạo bài viết mới.

### PUT /api/wiki/{id} (Admin)
Cập nhật bài viết.

### DELETE /api/wiki/{id} (Admin)
Xóa bài viết.

---

## 🗺️ Interactive Map

### GET /api/map-locations
Lấy danh sách tất cả các điểm ghim trên bản đồ.

### POST /api/admin/map-locations
(Admin) Tạo điểm ghim mới. Gửi `lat`, `lng`, `type`, `name`.

### PUT /api/admin/map-locations/{id}
(Admin) Cập nhật thông tin điểm ghim.

### DELETE /api/admin/map-locations/{id}
(Admin) Xóa điểm ghim.

---

## 👤 Personnel & RBAC

### GET /api/admin/users
(SuperAdmin) Lấy danh sách hồ sơ nhân sự.

### POST /api/admin/invite
(SuperAdmin) Tạo tài khoản mới cho Editor/Admin. Yêu cầu Service Role Key.

---

## 🏠 Homepage Settings

### GET /api/homepage
Lấy cấu hình nội dung trang chủ.

### PUT /api/admin/homepage
(Admin) Cập nhật cấu hình trang chủ.
