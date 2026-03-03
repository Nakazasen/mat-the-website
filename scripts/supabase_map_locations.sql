-- ============================================================
-- SUPABASE DATABASE SCHEMA: MAP LOCATIONS
-- Mạt Thế - Sinh Hoá Nguy Cơ
-- Phase: 09 Bản Đồ Chiến Sự
-- ============================================================
-- Chạy script này trong Supabase SQL Editor
-- (Dashboard → SQL Editor → New Query → Paste → Run)
-- ============================================================

CREATE TABLE IF NOT EXISTS public.map_locations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    lat FLOAT8 NOT NULL,
    lng FLOAT8 NOT NULL,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================
ALTER TABLE public.map_locations ENABLE ROW LEVEL SECURITY;

-- Cho phép tất cả mọi người đọc các điểm trên bản đồ (hiển thị công khai)
CREATE POLICY "Allow public read on map_locations" 
ON public.map_locations
FOR SELECT
TO public
USING (true);

-- Cho phép Admin (Service Role) toàn quyền quản lý
CREATE POLICY "Allow service role all on map_locations" 
ON public.map_locations
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Cho phép user đã xác thực (có role trên profile) quản lý (dự phòng nếu gọi thẳng từ JS)
-- Nhưng trong hệ thống này, Admin thao tác qua Backend FastAPI => Backend dùng Service Key.
-- Dưới đây ta mở quyền thêm cho safety nếu sau này đổi kiến trúc.
CREATE POLICY "Allow authenticated users to manage locations"
ON public.map_locations
FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);

-- Insert một trạm trung tâm Sài Gòn làm mẫu
INSERT INTO public.map_locations (name, type, description, lat, lng)
VALUES ('Căn Cứ Sài Gòn', 'safe_zone', 'Trụ sở chỉ huy chiến dịch.', 10.762622, 106.660172)
ON CONFLICT DO NOTHING;
