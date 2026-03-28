# Encoding Safety Rules

Những quy tắc này là bắt buộc trong repo này để tránh mojibake và lỗi encoding.

## 1. Quy tắc sửa file

- Không dùng `Set-Content`, `Out-File`, `>` hoặc bất kỳ lệnh bulk-write nào để sửa source hiện có.
- Chỉ dùng `apply_patch` cho sửa source thủ công.
- Không tự ý đổi encoding của file nếu chưa xác minh rõ nhu cầu.
- Không làm "chuẩn hóa hàng loạt" encoding trên nhiều file cùng lúc nếu không thật sự cần.

## 2. Quy tắc an toàn trước khi sửa file Unicode

- Với file lớn hoặc file có tiếng Việt / Nhật / Trung, phải ưu tiên chỉnh tối thiểu.
- Nếu nghi có mojibake, phải so với `git HEAD` trước.
- Nếu lỡ làm file hỏng encoding, phải restore file sạch rồi mới sửa lại bằng patch nhỏ.

## 3. Quy tắc trước khi commit

- Luôn chạy script quét mojibake trước khi commit:

```powershell
py -3 scripts/check_mojibake.py --staged
```

- Repo này có pre-commit hook để chặn commit nếu phát hiện chuỗi nghi mojibake.
- Nếu hook fail, không commit tiếp cho đến khi file nghi lỗi được kiểm tra và sửa xong.

## 4. Dấu hiệu nguy hiểm

Các chuỗi sau thường là dấu hiệu mojibake hoặc encoding drift:

- `�` <!-- mojibake-scan: ignore-line -->
- `蘯` <!-- mojibake-scan: ignore-line -->
- `盻` <!-- mojibake-scan: ignore-line -->
- `笏` <!-- mojibake-scan: ignore-line -->
- `逶` <!-- mojibake-scan: ignore-line -->
- `繝` <!-- mojibake-scan: ignore-line -->
- `陂` <!-- mojibake-scan: ignore-line -->
- các chuỗi halfwidth katakana dày đặc như `ﾃ`, `ﾄ`, `｡`, `ｿ` trong file vốn không nên có <!-- mojibake-scan: ignore-line -->

## 5. Cách xử lý khi phát hiện lỗi

1. Dừng sửa file đó.
2. So với `git diff` và `git show HEAD:<path>`.
3. Khôi phục nội dung sạch.
4. Áp lại thay đổi bằng `apply_patch`.
5. Chạy lại script quét trước khi commit.
