-- ============================================================
-- Migration: Harden RAG feedback trust provenance schema
-- Purpose: Add security provenance columns and harden RLS policies to prevent spoofing
-- ============================================================

-- 1. Add provenance columns to rag_feedback if they don't exist
ALTER TABLE rag_feedback 
    ADD COLUMN IF NOT EXISTS trust_verified BOOLEAN DEFAULT false,
    ADD COLUMN IF NOT EXISTS source_verified BOOLEAN DEFAULT false,
    ADD COLUMN IF NOT EXISTS trust_verification_method TEXT,
    ADD COLUMN IF NOT EXISTS trust_verified_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS trust_subject_user_id UUID,
    ADD COLUMN IF NOT EXISTS trust_level TEXT DEFAULT 'anonymous',
    ADD COLUMN IF NOT EXISTS is_author BOOLEAN DEFAULT false,
    ADD COLUMN IF NOT EXISTS is_trusted_reader BOOLEAN DEFAULT false;

-- 2. Drop and replace the anonymous insert policy with a hardened policy
DROP POLICY IF EXISTS "feedback_anonymous_insert" ON rag_feedback;

CREATE POLICY "feedback_anonymous_insert" ON rag_feedback
    FOR INSERT TO public
    WITH CHECK (
        (trust_level IS NULL OR trust_level = 'anonymous') AND
        (trust_verified IS NULL OR trust_verified = false) AND
        (source_verified IS NULL OR source_verified = false) AND
        (is_author IS NULL OR is_author = false) AND
        (is_trusted_reader IS NULL OR is_trusted_reader = false) AND
        (status IS NULL OR status = 'pending')
    );
