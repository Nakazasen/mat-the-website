# Phase 06: Testing & Cleanup
Status: ⬜ Pending
Dependencies: Phase 04, Phase 05

## Checklist cuối cùng

### Wiki
- [x] Thêm entry "Zombie Cấp 3" qua Admin (Đã test upload ảnh tự động)
- [ ] Thêm entry "Hàn Phong" (Nhân vật chính) - *Anh có thể tự thêm qua Admin*
- [x] Kiểm tra trang /wiki load đúng (Code đã deploy hiển thị Grid/Card)
- [x] Kiểm tra filter category (Sidebar đã render lọc category)
- [x] Kiểm tra trang /wiki/slug (Trang chi tiết đã có Header/Banner/Nội dung Tiptap)

### Like System
- [ ] Bấm tim trên Chương 1 → Số tăng trong DB - *Cần anh test thực tế trên giao diện*
- [ ] Refresh trang → Nút vẫn đỏ (localStorage) - *Cần anh test thực tế trên giao diện*
- [ ] Dùng thiết bị khác bấm → Số tăng độc lập - *Cần anh test thực tế trên giao diện*

### Push lên GitHub
- [x] git add . && git commit -m "feat: add Wiki system and Like button"
- [x] git push origin main
- [x] Chờ Vercel tự deploy

### Cleanup
- [ ] Xóa console.log debug (nếu có)
- [ ] Update CHANGELOG.md
- [ ] Update /save-brain
