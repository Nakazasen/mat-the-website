-- Migration: Create new_chapter_staging table
-- For staging incoming story growth chapters before primary DB ingestion

CREATE TABLE IF NOT EXISTS new_chapter_staging (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_number INTEGER NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_label TEXT DEFAULT 'admin_input',
    source_url TEXT NULL,
    validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'valid', 'invalid')),
    validation_errors JSONB DEFAULT '[]'::jsonb,
    ingest_status TEXT DEFAULT 'staged' CHECK (ingest_status IN ('staged', 'ingested', 'rejected')),
    submitted_by TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indices for fast staging lookups
CREATE INDEX IF NOT EXISTS idx_new_chapter_staging_chapter_number ON new_chapter_staging(chapter_number);
CREATE INDEX IF NOT EXISTS idx_new_chapter_staging_validation_status ON new_chapter_staging(validation_status);
CREATE INDEX IF NOT EXISTS idx_new_chapter_staging_ingest_status ON new_chapter_staging(ingest_status);

-- Enable RLS
ALTER TABLE new_chapter_staging ENABLE ROW LEVEL SECURITY;

-- Policy: Authenticated users (admin) can select, insert, update
CREATE POLICY "staging_admin_manage" ON new_chapter_staging
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);
