# Phase 06: Testing & Cleanup
Status: ⬜ Pending
Dependencies: Phase 04, Phase 05

## Checklist cuối cùng

### Wiki
- [ ] Thêm entry "Zombie Cấp 1" qua Admin
- [ ] Thêm entry "Hàn Phong" (Nhân vật chính)
- [ ] Kiểm tra trang /wiki load đúng
- [ ] Kiểm tra filter category
- [ ] Kiểm tra trang /wiki/slug

### Like System
- [ ] Bấm tim trên Chương 1 → Số tăng trong DB
- [ ] Refresh trang → Nút vẫn đỏ (localStorage)
- [ ] Dùng thiết bị khác bấm → Số tăng độc lập

### Push lên GitHub
- [ ] git add . && git commit -m "feat: add Wiki system and Like button"
- [ ] git push origin main
- [ ] Chờ Vercel tự deploy

### Cleanup
- [ ] Xóa console.log debug (nếu có)
- [ ] Update CHANGELOG.md
- [ ] Update /save-brain
