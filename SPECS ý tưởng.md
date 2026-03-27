# 🚀 SPECS: COMMAND CENTER v3.0 (BOLD & CREATIVE)

Tầm nhìn: Biến "Đọc truyện" thành một "Chiến dịch sinh tồn kỹ thuật số". Website không chỉ hiển thị chữ, nó phản ứng với hành trình của người đọc.

---

## 🏗️ KIẾN TRÚC TÍNH NĂNG (SMART PROPOSAL)

### 1. 🤖 AI Intelligence Core (Trợ lý Sinh Tồn)
- **Vibe:** Một "linh hồn" trong máy móc (có thể là AI 'Hệ Thống' trong truyện).
- **Tính năng:**
    - Chatbot hỗ trợ giải đáp về thế giới, nhân vật, cấp độ sức mạnh.
    - **Cơ chế Logic:** AI sẽ chỉ trả lời những gì đã xảy ra tính đến chương người dùng đang đọc. (Tránh leak nội dung - Spoilers).
- **Công nghệ:** Tích hợp OpenAI/Gemini API với dữ liệu từ [Wiki](file:///c:/ProgramData/Sandbox/Web_matthesinhhoanguyco/mat-the-website/frontend/src/lib/api.ts#122-136) của website làm Context.

### 2. ⏳ Living Chronicle (Biên niên sử động)
- **Vibe:** "Dòng thời gian đang được viết lại".
- **Tính năng:** Một trục thời gian (Timeline) tự động mở khóa các sự kiện chính.
- **Sáng tạo:** Hiệu ứng "Dữ liệu bị nhiễu" (Glitch/Corrupted) cho các sự kiện ở tương lai (chương chưa đọc). Khi đọc xong, hiệu ứng nhiễu biến mất, hiện ra sự thật.

### 3. 📻 Radio Distress Signals (Tín hiệu Radio)
- **Vibe:** Âm thanh của sự tuyệt vọng và hy vọng.
- **Tính năng:** 
    - Khi đọc đến những chương cao trào, HUD sẽ nhấp nháy icon "Radio Signal Detected".
    - Nhấp vào sẽ hiển thị một đoạn hội thoại "nghe lén" được từ các phe phái khác, cung cấp thông tin bên lề không có trong chính văn.

### 4. 🖨️ Terminal Data Recovery (Minigame bẻ khóa)
- **Vibe:** "Bạn là hacker đang khôi phục dữ liệu thế giới cũ".
- **Tính năng:** Để đọc được các "Hồ sơ tuyệt mật" về nguồn gốc virus trong Wiki, người dùng phải giải các mật mã đơn giản (ví dụ: tên một người đã chết ở chương 10).

---

## 📊 LUỒNG HOẠT ĐỘNG (FLOW)

1. **User vào trang đọc** -> HUD khởi động (Animation).
2. **User cuộn trang** -> Hệ thống quét Keyword -> Trigger hiệu ứng Danger/Radio.
3. **User hoàn thành chương** -> Gửi Signal về Backend -> Cập nhật `ReadProgress`.
4. **User vào Dashboard** -> Thấy tài nguyên căn cứ tăng/giảm dựa trên diễn biến truyện vừa đọc.

---

## 🛠️ TECH STACK ĐỀ XUẤT
- **UI:** Next.js 15 + Tailwind CSS (Cyberpunk/Military theme).
- **Animations:** Framer Motion (Glitch, Pulse, Scanning).
- **Data Visual:** D3.js (cho Map và Graph quan hệ).
- **Backend:** FastAPI + Supabase (Metadata & Real-time updates).

---

## 🗓️ PHÂN CHIA GIAI ĐOẠN (PHASES)

### Phase 1: The HUD Foundation (Quick Wins)
- Triển khai lớp phủ HUD mờ.
- Logic quét keyword và hiển thị Danger Level.
- Tooltip "Quick Scan" nhân vật.

### Phase 2: Base HQ Dashboard (The Heart)
- Trang Dashboard hiển thị tài nguyên phe phái chính.
- Logic đồng bộ chỉ số phe phái với số chương đã đọc.

### Phase 3: AI & Interactive Lore (The Soul)
- Tích hợp AI Chatbot (The System).
- Hệ thống Radio Signals và Timeline động.

---

## ⚠️ CÂU HỎI QUAN TRỌNG (DEEP INTERVIEW)

1. **Độ khó (Complexity):** Anh muốn hệ thống tự động hoàn toàn (AI quét text) hay em sẽ tạo một file JSON metadata cho từng chương để control (chính xác hơn nhưng tốn công nhập liệu)?
2. **Tương tác:** Anh muốn người dùng chỉ "Xem" (Look-only) hay có thể "Chọn" (Impact) - ví dụ: chọn phe phái để HUD thay đổi màu sắc?
3. **Ưu tiên:** Trong 4 tính năng trên, anh muốn em bắt đầu build cái nào đầu tiên để "ăn mừng" sự sáng tạo này?
