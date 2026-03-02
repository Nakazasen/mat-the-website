-- =========================================================================
-- SYSTEM UPGRADE: LEADERBOARD RPC
-- DESC: Safely fetch the top 10 users for the Leaderboard
-- =========================================================================

-- CREATE RPC FUNCTION TO FETCH LEADERBOARD SAFELY
-- This avoids RLS issues and extracts avatar_url / full_name directly from auth.users
CREATE OR REPLACE FUNCTION get_leaderboard()
RETURNS TABLE (
    id UUID,
    full_name TEXT,
    avatar_url TEXT,
    exp INTEGER,
    chapters_read INTEGER
)
SECURITY DEFINER
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id as id,
    COALESCE(
       NULLIF((u.raw_user_meta_data->>'full_name')::TEXT, ''),
       NULLIF(p.display_name, ''),
       SPLIT_PART(u.email, '@', 1),
       'Ẩn Danh'
    ) as full_name,
    (u.raw_user_meta_data->>'avatar_url')::TEXT as avatar_url,
    p.exp,
    p.chapters_read
  FROM public.profiles p
  JOIN auth.users u ON p.id = u.id
  WHERE p.chapters_read > 0
  ORDER BY p.chapters_read DESC, p.exp DESC
  LIMIT 10;
END;
$$ LANGUAGE plpgsql;

-- Grant EXECUTE permission to all users (including anonymous for public Leaderboard)
GRANT EXECUTE ON FUNCTION get_leaderboard() TO anon, authenticated;
