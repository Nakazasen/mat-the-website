-- ============================================================
-- Migration: Add review fields to rag_feedback table
-- Purpose: Support recording review notes and review timestamps directly on feedback rows
-- ============================================================

ALTER TABLE rag_feedback 
    ADD COLUMN IF NOT EXISTS reviewer_note TEXT,
    ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMPTZ;
