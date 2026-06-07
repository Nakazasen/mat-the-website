-- ============================================================
-- Migration: Create provisional_library table
-- Purpose: Store provisional library concepts/entities for auto-enrichment
-- ============================================================

CREATE TABLE IF NOT EXISTS provisional_library (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  normalized_name TEXT NOT NULL,
  type TEXT NOT NULL,
  summary TEXT,
  evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
  confidence DOUBLE PRECISION NOT NULL DEFAULT 0,
  quality_class TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'provisional',
  source TEXT NOT NULL DEFAULT 'story_chunks_auto_extract',
  feedback_score INTEGER NOT NULL DEFAULT 0,
  needs_review BOOLEAN NOT NULL DEFAULT false,
  chapter_numbers INTEGER[] DEFAULT '{}',
  first_chapter INTEGER,
  last_chapter INTEGER,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_provisional_library_name ON provisional_library(name);
CREATE INDEX IF NOT EXISTS idx_provisional_library_normalized_name ON provisional_library(normalized_name);
CREATE INDEX IF NOT EXISTS idx_provisional_library_type ON provisional_library(type);
CREATE INDEX IF NOT EXISTS idx_provisional_library_quality_class ON provisional_library(quality_class);
CREATE INDEX IF NOT EXISTS idx_provisional_library_confidence ON provisional_library(confidence DESC);

ALTER TABLE provisional_library ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "provisional_library_public_read" ON provisional_library
    FOR SELECT TO public USING (true);

-- Allow service_role full management
CREATE POLICY "provisional_library_service_manage" ON provisional_library
    FOR ALL TO service_role USING (true) WITH CHECK (true);
