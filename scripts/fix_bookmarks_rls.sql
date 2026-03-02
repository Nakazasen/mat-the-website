-- =========================================================================
-- BUG FIX: CHAPTERS RLS POLICY
-- DESC: Updates the SELECT policy on chapters to allow 'authenticated' users.
--       Currently restricted to 'anon', which breaks joined queries for
--       logged-in users (like Bookmarks in Profile).
-- =========================================================================

-- 1. Drop the old restrictive policy
DROP POLICY IF EXISTS "Allow public read" ON public.chapters;

-- 2. Create a new inclusive policy
-- Using 'TO public' covers both 'anon' and 'authenticated' roles
CREATE POLICY "Allow public read" ON public.chapters
  FOR SELECT
  TO public
  USING (true);

-- 3. (Optional but recommended) Ensure other metadata tables are also readable by authenticated users
DROP POLICY IF EXISTS "Public read" ON public.novel_settings;
CREATE POLICY "Public read" ON public.novel_settings FOR SELECT TO public USING (true);

DROP POLICY IF EXISTS "Public read" ON public.homepage_settings;
CREATE POLICY "Public read" ON public.homepage_settings FOR SELECT TO public USING (true);
