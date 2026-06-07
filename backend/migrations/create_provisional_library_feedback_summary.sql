-- ============================================================
-- Migration: Create provisional_library_feedback_summary table
-- Purpose: Aggregate community feedback scores and determine active oracle policies
-- ============================================================

CREATE TABLE IF NOT EXISTS provisional_library_feedback_summary (
  provisional_id TEXT PRIMARY KEY,
  record_name TEXT,
  total_feedback INTEGER NOT NULL DEFAULT 0,
  wrong_info_count INTEGER NOT NULL DEFAULT 0,
  wrong_type_count INTEGER NOT NULL DEFAULT 0,
  wrong_evidence_count INTEGER NOT NULL DEFAULT 0,
  duplicate_count INTEGER NOT NULL DEFAULT 0,
  spoiler_count INTEGER NOT NULL DEFAULT 0,
  missing_info_count INTEGER NOT NULL DEFAULT 0,
  other_count INTEGER NOT NULL DEFAULT 0,
  unique_user_agent_count INTEGER NOT NULL DEFAULT 0,
  dispute_score DOUBLE PRECISION NOT NULL DEFAULT 0,
  effective_status TEXT NOT NULL DEFAULT 'trusted',
  oracle_policy TEXT NOT NULL DEFAULT 'allow',
  top_comments JSONB NOT NULL DEFAULT '[]'::jsonb,
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pl_feedback_summary_status
ON provisional_library_feedback_summary(effective_status);

CREATE INDEX IF NOT EXISTS idx_pl_feedback_summary_dispute_score
ON provisional_library_feedback_summary(dispute_score DESC);

ALTER TABLE provisional_library_feedback_summary ENABLE ROW LEVEL SECURITY;

CREATE POLICY "pl_feedback_summary_public_read" ON provisional_library_feedback_summary
  FOR SELECT TO public USING (true);

CREATE POLICY "pl_feedback_summary_service_manage" ON provisional_library_feedback_summary
  FOR ALL TO service_role USING (true) WITH CHECK (true);
