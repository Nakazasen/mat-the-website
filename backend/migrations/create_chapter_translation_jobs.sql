-- ============================================================
-- Migration: Create chapter translation resumable job tables
-- Purpose: Persist per-locale, per-chunk translation progress so
--          long chapter translations can resume after failures/restarts.
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS chapter_translation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id BIGINT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    chapter_number INTEGER NOT NULL,
    locale TEXT NOT NULL,
    source_locale TEXT NOT NULL DEFAULT 'vi',
    source_content_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    total_chunks INTEGER NOT NULL DEFAULT 0,
    completed_chunks INTEGER NOT NULL DEFAULT 0,
    failed_chunks INTEGER NOT NULL DEFAULT 0,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chapter_translation_jobs_status_check CHECK (
        status IN ('queued', 'in_progress', 'completed', 'failed', 'cancelled')
    ),
    CONSTRAINT chapter_translation_jobs_locale_check CHECK (locale IN ('en', 'zh-CN', 'ja')),
    CONSTRAINT chapter_translation_jobs_counts_check CHECK (
        total_chunks >= 0 AND completed_chunks >= 0 AND failed_chunks >= 0 AND attempt_count >= 0
    ),
    CONSTRAINT uq_chapter_translation_job_source UNIQUE (chapter_id, locale, source_content_hash)
);

CREATE TABLE IF NOT EXISTS chapter_translation_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES chapter_translation_jobs(id) ON DELETE CASCADE,
    chapter_id BIGINT NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    locale TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    source_text TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    translated_text TEXT,
    translated_title TEXT,
    status TEXT NOT NULL DEFAULT 'queued',
    attempt_count INTEGER NOT NULL DEFAULT 0,
    provider TEXT,
    model TEXT,
    last_error TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chapter_translation_chunks_status_check CHECK (
        status IN ('queued', 'in_progress', 'completed', 'failed')
    ),
    CONSTRAINT chapter_translation_chunks_locale_check CHECK (locale IN ('en', 'zh-CN', 'ja')),
    CONSTRAINT chapter_translation_chunks_index_check CHECK (chunk_index >= 0),
    CONSTRAINT chapter_translation_chunks_attempt_check CHECK (attempt_count >= 0),
    CONSTRAINT uq_chapter_translation_chunk_index UNIQUE (job_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_chapter_translation_jobs_chapter_locale
    ON chapter_translation_jobs(chapter_id, locale);
CREATE INDEX IF NOT EXISTS idx_chapter_translation_jobs_status_updated
    ON chapter_translation_jobs(status, updated_at);
CREATE INDEX IF NOT EXISTS idx_chapter_translation_jobs_source_hash
    ON chapter_translation_jobs(source_content_hash);

CREATE INDEX IF NOT EXISTS idx_chapter_translation_chunks_job_status
    ON chapter_translation_chunks(job_id, status);
CREATE INDEX IF NOT EXISTS idx_chapter_translation_chunks_chapter_locale
    ON chapter_translation_chunks(chapter_id, locale);
CREATE INDEX IF NOT EXISTS idx_chapter_translation_chunks_status_updated
    ON chapter_translation_chunks(status, updated_at);
CREATE INDEX IF NOT EXISTS idx_chapter_translation_chunks_source_hash
    ON chapter_translation_chunks(source_hash);

ALTER TABLE chapter_translation_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE chapter_translation_chunks ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "chapter_translation_jobs_service_manage" ON chapter_translation_jobs;
CREATE POLICY "chapter_translation_jobs_service_manage" ON chapter_translation_jobs
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "chapter_translation_chunks_service_manage" ON chapter_translation_chunks;
CREATE POLICY "chapter_translation_chunks_service_manage" ON chapter_translation_chunks
    FOR ALL TO service_role USING (true) WITH CHECK (true);
