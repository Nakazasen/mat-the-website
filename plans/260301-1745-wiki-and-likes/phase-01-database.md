# Phase 01: Database Setup
Status: ⬜ Pending
Dependencies: Không có

## Objective
Tạo bảng `wiki_entries` mới và thêm cột `likes_count` vào bảng `chapters` đã có.

## SQL cần chạy trên Supabase SQL Editor

### 1. Tạo bảng Wiki

```sql
-- Tạo bảng wiki_entries
CREATE TABLE IF NOT EXISTS public.wiki_entries (
  id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title        TEXT NOT NULL,
  category     TEXT NOT NULL CHECK (category IN ('Nhân vật', 'Sinh vật', 'Thế lực', 'Vật phẩm', 'Địa điểm')),
  slug         TEXT UNIQUE NOT NULL,
  summary      TEXT,
  content      TEXT,
  image_url    TEXT,
  tags         TEXT[],
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  updated_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Cho phép mọi người xem wiki (public)
ALTER TABLE public.wiki_entries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public can view wiki" ON public.wiki_entries FOR SELECT USING (true);
```

### 2. Thêm cột likes_count vào chapters

```sql
ALTER TABLE public.chapters ADD COLUMN IF NOT EXISTS likes_count INT DEFAULT 0;
```

## Implementation Steps
1. [ ] Chạy SQL tạo bảng wiki_entries
2. [ ] Chạy SQL thêm cột likes_count
3. [ ] Verify bảng đã tạo thành công

## Test Criteria
- [ ] Bảng `wiki_entries` tồn tại trong Supabase
- [ ] Cột `likes_count` xuất hiện trong bảng `chapters`
- [ ] INSERT thử 1 wiki entry thành công

---
Next Phase: phase-02-backend.md
