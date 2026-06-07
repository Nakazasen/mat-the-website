-- ============================================================
-- Migration: Create feedback_policy_pipeline_runs table
-- Purpose: Log self-learning pipeline runs and operational health metrics
-- ============================================================

CREATE TABLE IF NOT EXISTS feedback_policy_pipeline_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  started_at TIMESTAMPTZ DEFAULT now(),
  finished_at TIMESTAMPTZ,
  trigger_source TEXT NOT NULL DEFAULT 'unknown',
  dry_run BOOLEAN NOT NULL DEFAULT false,
  clear_cache BOOLEAN NOT NULL DEFAULT false,
  feedback_rows_read INTEGER NOT NULL DEFAULT 0,
  summary_rows_written INTEGER NOT NULL DEFAULT 0,
  patches_written INTEGER NOT NULL DEFAULT 0,
  cache_rows_deleted INTEGER NOT NULL DEFAULT 0,
  ok BOOLEAN NOT NULL DEFAULT false,
  errors JSONB NOT NULL DEFAULT '[]'::jsonb,
  report JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_fpp_runs_started_at
ON feedback_policy_pipeline_runs(started_at DESC);

ALTER TABLE feedback_policy_pipeline_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "feedback_policy_pipeline_runs_service_manage"
ON feedback_policy_pipeline_runs
FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "feedback_policy_pipeline_runs_admin_read"
ON feedback_policy_pipeline_runs
FOR SELECT TO authenticated USING (true);
