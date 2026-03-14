-- ============================================================
-- Migration: Create faction_members table
-- Purpose: Hierarchical org chart for "Thế lực" wiki entries
-- ============================================================

CREATE TABLE IF NOT EXISTS faction_members (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    faction_id UUID NOT NULL REFERENCES wiki_entries(id) ON DELETE CASCADE,
    character_id UUID REFERENCES wiki_entries(id) ON DELETE SET NULL,
    parent_id UUID REFERENCES faction_members(id) ON DELETE SET NULL,
    role_title TEXT NOT NULL DEFAULT '',
    division TEXT,
    rank_level INT NOT NULL DEFAULT 0,
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_faction_members_faction ON faction_members(faction_id);
CREATE INDEX IF NOT EXISTS idx_faction_members_parent ON faction_members(parent_id);
CREATE INDEX IF NOT EXISTS idx_faction_members_character ON faction_members(character_id);

-- RLS (Row Level Security)
ALTER TABLE faction_members ENABLE ROW LEVEL SECURITY;

-- Public read access
CREATE POLICY "faction_members_public_read" ON faction_members
    FOR SELECT USING (true);

-- Admin full access (via service role key, bypasses RLS)
