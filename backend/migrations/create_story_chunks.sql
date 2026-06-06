-- ============================================================
-- Migration: Create story_chunks table
-- Purpose: Store chunked text of story chapters for RAG
-- ============================================================

-- Step 1: Enable pgvector extension if available
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Create story_chunks table
CREATE TABLE IF NOT EXISTS story_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id BIGINT REFERENCES chapters(id) ON DELETE SET NULL,
    chapter_number INTEGER NOT NULL,
    chapter_title TEXT,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_plain TEXT NOT NULL,
    token_count INTEGER NOT NULL DEFAULT 0,
    char_count INTEGER NOT NULL DEFAULT 0,
    content_hash TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding vector(1536), -- TODO: Adjust dimensions if embedding provider changes (e.g. 1536 for OpenAI/standard, 768 for Gemini)
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Step 3: Create constraints & indexes
ALTER TABLE story_chunks 
    ADD CONSTRAINT uq_chapter_chunk_hash UNIQUE (chapter_number, chunk_index, content_hash);

CREATE INDEX IF NOT EXISTS idx_story_chunks_chapter_number ON story_chunks(chapter_number);
CREATE INDEX IF NOT EXISTS idx_story_chunks_content_hash ON story_chunks(content_hash);
CREATE INDEX IF NOT EXISTS idx_story_chunks_metadata ON story_chunks USING gin(metadata);

-- Full-text search index (using simple configuration for multi-language and Vietnamese safety)
CREATE INDEX IF NOT EXISTS idx_story_chunks_content_plain_fts ON story_chunks USING gin(to_tsvector('simple', content_plain));

-- Step 4: Row Level Security (RLS)
ALTER TABLE story_chunks ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "story_chunks_public_read" ON story_chunks
    FOR SELECT TO public USING (true);

-- Allow service_role full management
CREATE POLICY "story_chunks_service_manage" ON story_chunks
    FOR ALL TO service_role USING (true) WITH CHECK (true);
