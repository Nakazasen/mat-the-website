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

## 📊 Analytics (Admin)

### GET /api/admin/analytics/top-chapters
Lấy danh sách 5 chương có lượt xem cao nhất.

**Headers:** `Authorization: Bearer {admin_token}`

---

## ⚙️ Novel Settings

### GET /api/novel
Lấy thông tin cấu hình truyện (Tên, Tác giả, Ảnh bìa, Thể loại).
