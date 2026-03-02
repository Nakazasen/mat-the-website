-- 1. Thêm cột avatar_url vào bảng profiles nếu chưa có
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS avatar_url TEXT;

-- 2. Cập nhật hàm xử lý tạo profile tự động khi có user mới
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email, display_name, avatar_url, role)
  VALUES (
    new.id,
    new.email,
    -- Ưu tiên lấy full_name từ metadata của Google, nếu không thì lấy name
    COALESCE(new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'name'),
    -- Lấy ảnh đại diện từ Google
    new.raw_user_meta_data->>'avatar_url',
    -- Mặc định gán role 'reader' cho người dùng đăng nhập bằng Google/Email thường
    'reader'
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Tạo Trigger để tự động chạy hàm trên khi có dòng mới trong auth.users
-- Drop trigger cũ nếu có để tránh lỗi duplicate
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
