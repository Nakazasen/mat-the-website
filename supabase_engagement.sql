-- =========================================================================
-- SYSTEM UPGRADE: READER ENGAGEMENT
-- DESC: Adds required tables & functions for History, Bookmarks & EXP
-- =========================================================================

-- 1. ADD EXP AND CHAPTERS_READ TO PROFILES
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS exp INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS chapters_read INTEGER DEFAULT 0;

-- 2. CREATE BOOKMARKS TABLE
CREATE TABLE IF NOT EXISTS public.bookmarks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    novel_id UUID REFERENCES public.novels(id) ON DELETE CASCADE, -- In case we want to bookmark the whole novel
    chapter_id UUID REFERENCES public.chapters(id) ON DELETE CASCADE, -- In case we want to bookmark a specific chapter
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    -- Ensure a user can't bookmark the exact same chapter/novel multiple times
    UNIQUE(user_id, novel_id, chapter_id)
);

-- Enable RLS for bookmarks
ALTER TABLE public.bookmarks ENABLE ROW LEVEL SECURITY;

-- BOOKMARKS POLICIES
-- Users can view their own bookmarks
CREATE POLICY "Users can view own bookmarks"
ON public.bookmarks FOR SELECT
USING (auth.uid() = user_id);

-- Users can insert their own bookmarks
CREATE POLICY "Users can insert own bookmarks"
ON public.bookmarks FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Users can delete their own bookmarks
CREATE POLICY "Users can delete own bookmarks"
ON public.bookmarks FOR DELETE
USING (auth.uid() = user_id);


-- 3. CREATE RPC FUNCTION TO SAFELY INCREMENT EXP AND CHAPTERS_READ
-- This allows the frontend to call a Supabase function to increase stats
-- without granting full UPDATE access to the profiles table.
CREATE OR REPLACE FUNCTION increment_reader_stats(user_id_param UUID, new_chapters_count INTEGER, new_exp_amount INTEGER)
RETURNS void AS $$
BEGIN
  UPDATE public.profiles
  SET 
    chapters_read = GREATEST(chapters_read, new_chapters_count),
    exp = exp + new_exp_amount
  WHERE id = user_id_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant EXECUTE permission to authenticated users
GRANT EXECUTE ON FUNCTION increment_reader_stats(UUID, INTEGER, INTEGER) TO authenticated;
