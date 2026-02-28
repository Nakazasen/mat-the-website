-- ============================================================
-- SUPABASE DATABASE SCHEMA
-- Mạt Thế - Sinh Hoá Nguy Cơ
-- ============================================================
-- Chạy script này trong Supabase SQL Editor
-- (Dashboard → SQL Editor → New Query → Paste → Run)
-- ============================================================

-- Bảng chapters: chỉ lưu metadata, KHÔNG lưu nội dung văn bản
CREATE TABLE IF NOT EXISTS chapters (
  id              BIGSERIAL PRIMARY KEY,
  chapter_number  INTEGER NOT NULL UNIQUE,   -- Số chương (1, 2, 3...)
  title           TEXT NOT NULL,             -- Tiêu đề chương
  content_url     TEXT NOT NULL,             -- URL file .json trên Cloudflare R2
  word_count      INTEGER,                   -- Số từ (ước tính)
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Index để query nhanh theo số chương
CREATE INDEX IF NOT EXISTS idx_chapters_number ON chapters(chapter_number);

-- ============================================================
-- ROW LEVEL SECURITY (Public read-only)
-- ============================================================
ALTER TABLE chapters ENABLE ROW LEVEL SECURITY;

-- Cho phép tất cả mọi người đọc (anon key)
CREATE POLICY "Allow public read" ON chapters
  FOR SELECT
  TO anon
  USING (true);

-- Chỉ service role được insert/update (dùng trong upload_data.py)
-- Khi dùng script upload, hãy dùng SUPABASE_SERVICE_KEY thay vì anon key
CREATE POLICY "Allow service insert/update" ON chapters
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ============================================================
-- SAMPLE DATA (để test giao diện khi chưa upload truyện)
-- ============================================================
INSERT INTO chapters (chapter_number, title, content_url, word_count) VALUES
  (1, 'Ngày Tận Thế Bắt Đầu', 'https://pub-xxx.r2.dev/chapters/chuong-00001.json', 3200),
  (2, 'Lây Lan', 'https://pub-xxx.r2.dev/chapters/chuong-00002.json', 2800),
  (3, 'Sinh Tồn', 'https://pub-xxx.r2.dev/chapters/chuong-00003.json', 3100)
ON CONFLICT (chapter_number) DO NOTHING;
