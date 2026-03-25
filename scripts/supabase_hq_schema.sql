-- ====================================================
-- Base HQ Dashboard: Schema for Supabase
-- Stores faction resource snapshots per chapter
-- ====================================================

-- Drop if re-running
DROP TABLE IF EXISTS hq_snapshots CASCADE;

-- Create the snapshots table
CREATE TABLE hq_snapshots (
    id          SERIAL PRIMARY KEY,
    chapter_id  INTEGER NOT NULL,         -- Which chapter this snapshot is from
    faction     TEXT NOT NULL DEFAULT 'main', -- Faction key (e.g. 'main', 'shadow', 'government')

    -- Resource metrics
    food_days   INTEGER NOT NULL DEFAULT 0,  -- Days of food supply remaining
    crystal_count INTEGER NOT NULL DEFAULT 0, -- Ti Tinh Hach (energy crystals) count
    water_unit  INTEGER NOT NULL DEFAULT 0,  -- Water supply (liters)

    -- Personnel
    warriors    INTEGER NOT NULL DEFAULT 0,  -- Combat-capable members
    researchers INTEGER NOT NULL DEFAULT 0,  -- Scientists / medics
    civilians   INTEGER NOT NULL DEFAULT 0,  -- Non-combat population

    -- Infrastructure
    wall_level  SMALLINT NOT NULL DEFAULT 1, -- Defensive wall level (1-5)
    territory_km2 SMALLINT NOT NULL DEFAULT 0, -- Controlled area (km²)
    morale      SMALLINT NOT NULL DEFAULT 80, -- Morale percentage 0-100

    -- Timestamps
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast chapter-based lookup
CREATE INDEX idx_hq_snapshots_chapter ON hq_snapshots (chapter_id, faction);

-- Row-Level Security (public read, admin write)
ALTER TABLE hq_snapshots ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public can read hq_snapshots"
    ON hq_snapshots FOR SELECT
    USING (true);

-- ====================================================
-- Seed data: Pre-populate base snapshots at key chapters
-- (Admin updates these manually as story progresses)
-- ====================================================

INSERT INTO hq_snapshots (chapter_id, faction, food_days, crystal_count, water_unit, warriors, researchers, civilians, wall_level, territory_km2, morale)
VALUES
    -- Early game (Chương 1-50): Struggling survivor base
    (1,   'main', 7,   0,    200,  3,  0,  8,  1, 0,  60),
    (10,  'main', 14,  5,    500,  8,  1,  15, 1, 1,  65),
    (30,  'main', 30,  20,   1200, 18, 2,  40, 2, 3,  72),
    (50,  'main', 45,  80,   3000, 35, 5,  90, 2, 8,  75),

    -- Mid game (Chương 100-300): Growing faction
    (100, 'main', 60,  250,  8000, 80, 12, 200, 3, 20, 80),
    (200, 'main', 90,  800,  20000, 200, 30, 500, 3, 50, 82),
    (300, 'main', 120, 2000, 50000, 450, 60, 1200, 4, 100, 85),

    -- Late game (Chương 500-816): Major power
    (500, 'main', 180, 8000, 120000, 1200, 150, 4000, 5, 300, 88),
    (700, 'main', 240, 25000, 300000, 3000, 400, 12000, 5, 800, 90),
    (816, 'main', 365, 80000, 800000, 8000, 1200, 40000, 5, 2500, 95);

COMMENT ON TABLE hq_snapshots IS 'Resource snapshots for faction base HQ, keyed by chapter milestone';
