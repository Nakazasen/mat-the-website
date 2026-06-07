# Public Oracle Chatbot Verification & Availability Record

**Ngày ghi nhận:** 2026-06-07 (Asia/Bangkok)
**Trạng thái kiểm thử:** PASS
**Classification:** `PASS_PUBLIC_ORACLE_CHATBOT_AVAILABLE_FOR_ANONYMOUS_USERS`

---

## 1. Kết quả Health Check (Health Verification)
Hệ thống dịch vụ trên production (Render) hoạt động bình thường:
* **GET `/api/health`**: Phản hồi `200 OK`
  ```json
  {"status":"ok","service":"mat-the-api"}
  ```
* **GET `/oracle/health`**: Phản hồi `200 OK`
  ```json
  {"ok":true,"status":"ok","active_model":"deepseek-v4-flash",...}
  ```

---

## 2. Kết quả Public Ask API (Public Chatbot Verification)
Kiểm thử endpoint công khai gửi câu hỏi tới AI Oracle chatbot:
* **POST `/oracle/ask`**: Trả về `200 OK` mà không yêu cầu Header xác thực hay phiên đăng nhập admin.
* **Cấu trúc phản hồi:**
  ```json
  {
    "answer": "[DỮ LIỆU HỆ THỐNG]\n- Công Tôn Trường Thanh (Phân loại: Nhân vật) : \n- Hàn Phong (Phân loại: Nhân vật) : <QUÂN ĐỘI>Đoàn Trưởng",
    "source": "cache",
    "chapter_progress": 1
  }
  ```
* **Nguồn câu trả lời:** Nguồn (`source`) hợp lệ (`cache` / `local_wiki` / `ai_provider`), phản hồi được định dạng và lọc thông tin an toàn.

---

## 3. Hoạt động trên Frontend (Reader UX)
* Độc giả vãng lai (ẩn danh) khi đọc truyện hoàn toàn có thể mở và sử dụng **OraclePanel** trên giao diện đọc chương.
* Có thể đặt câu hỏi trực tiếp mà không gặp bất kỳ rào cản xác thực nào.

---

## 4. Kết quả Báo lỗi Công khai (Public Feedback Button)
* Sau khi nhận câu trả lời, độc giả có thể click nút báo lỗi câu trả lời ("Báo lỗi câu trả lời") để gửi ý kiến phản hồi về hệ thống.
* **POST `/api/oracle/feedback`**: Gửi phản hồi thành công và lưu trữ ở trạng thái `pending` trong database mà không cần token xác thực của admin.
* Phản hồi kiểm thử đã được giải quyết trực tiếp trong DB (`status` đặt thành `resolved`).

---

## 5. Xác minh bảo vệ quyền quản trị (Admin Route Protection)
Đảm bảo các đường dẫn API và trang quản trị hoàn toàn được đóng kín với độc giả ẩn danh:
* **Vercel API Proxy Endpoints** (Yêu cầu phiên đăng nhập):
  * `GET /api/oracle/corrections/pending` -> `401 Unauthorized`
  * `GET /api/oracle/feedback/pending` -> `401 Unauthorized`
  * `GET /api/oracle/wiki-candidates` -> `401 Unauthorized`
* **FastAPI Direct Endpoints** (Yêu cầu `X-Oracle-Feedback-Admin-Token`):
  * `GET /oracle/corrections/pending` -> `403 Forbidden` (`Forbidden: Invalid admin token`)
  * `GET /oracle/feedback/pending` -> `403 Forbidden` (`Forbidden: Invalid admin token`)

---

## 6. Trạng thái cấu hình RAG hiện tại (Current RAG Status)
* **ORACLE_RAG_ENABLED:** `OFF` (Tắt trên cả Vercel và Render).
* **Chi tiết:** Tính năng RAG đầy đủ (Dense vector & Hybrid RAG với các chunk văn bản truyện) chưa được kích hoạt công khai cho người dùng cuối. Hệ thống chatbot hiện đang sử dụng cơ chế định danh thực thể cục bộ kết hợp với bộ đệm (cache) và mô hình AI Multi-provider chuẩn.

---

## 7. Kết luận
Độc giả bình thường khi vào web hoàn toàn có thể sử dụng chatbot công khai một cách trơn tru, bảo mật và an toàn. Các định tuyến quản trị được bảo mật nghiêm ngặt.
