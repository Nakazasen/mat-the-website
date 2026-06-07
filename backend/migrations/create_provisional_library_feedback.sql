-- ============================================================
-- Migration: Create provisional_library_feedback table
-- Purpose: Store public reader feedback/corrections for auto-extracted records
-- ============================================================

CREATE TABLE IF NOT EXISTS provisional_library_feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provisional_id TEXT NOT NULL,
  record_name TEXT,
  feedback_type TEXT NOT NULL,
  user_comment TEXT NOT NULL,
  suggested_correction TEXT,
  page_url TEXT,
  user_agent TEXT,
  status TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_provisional_library_feedback_provisional_id
ON provisional_library_feedback(provisional_id);

CREATE INDEX IF NOT EXISTS idx_provisional_library_feedback_status
ON provisional_library_feedback(status);

ALTER TABLE provisional_library_feedback ENABLE ROW LEVEL SECURITY;

-- Allow service_role full management
CREATE POLICY "provisional_library_feedback_service_manage" ON provisional_library_feedback
    FOR ALL TO service_role USING (true) WITH CHECK (true);
