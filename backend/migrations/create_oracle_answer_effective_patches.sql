-- ============================================================
-- Migration: Create oracle answer feedback tables
-- Purpose: Store self-learned patches and feedback summaries for RAG Oracle
-- ============================================================

CREATE TABLE IF NOT EXISTS oracle_answer_feedback_summary (
  query_pattern TEXT PRIMARY KEY,
  total_feedback INTEGER NOT NULL DEFAULT 0,
  shallow_count INTEGER NOT NULL DEFAULT 0,
  misclassification_count INTEGER NOT NULL DEFAULT 0,
  irrelevant_count INTEGER NOT NULL DEFAULT 0,
  missing_entity_count INTEGER NOT NULL DEFAULT 0,
  stale_cache_count INTEGER NOT NULL DEFAULT 0,
  wrong_summary_count INTEGER NOT NULL DEFAULT 0,
  too_mechanical_count INTEGER NOT NULL DEFAULT 0,
  unknown_count INTEGER NOT NULL DEFAULT 0,
  top_comments JSONB NOT NULL DEFAULT '[]'::jsonb,
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS oracle_answer_effective_patches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  issue_type TEXT NOT NULL,
  query_pattern TEXT NOT NULL,
  target_entity TEXT,
  target_intent TEXT,
  patch_type TEXT NOT NULL,
  policy JSONB NOT NULL DEFAULT '{}'::jsonb,
  effective_status TEXT NOT NULL DEFAULT 'active',
  confidence NUMERIC NOT NULL DEFAULT 0,
  source_feedback_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  reason TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_oracle_patches_query_pattern ON oracle_answer_effective_patches(query_pattern);
CREATE INDEX IF NOT EXISTS idx_oracle_patches_issue_type ON oracle_answer_effective_patches(issue_type);
CREATE INDEX IF NOT EXISTS idx_oracle_patches_status ON oracle_answer_effective_patches(effective_status);

-- Enable Row Level Security (RLS)
ALTER TABLE oracle_answer_feedback_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE oracle_answer_effective_patches ENABLE ROW LEVEL SECURITY;

-- Allow public read
CREATE POLICY "oracle_feedback_summary_public_read" ON oracle_answer_feedback_summary
  FOR SELECT TO public USING (true);

CREATE POLICY "oracle_effective_patches_public_read" ON oracle_answer_effective_patches
  FOR SELECT TO public USING (true);

-- Allow service role full management
CREATE POLICY "oracle_feedback_summary_service_manage" ON oracle_answer_feedback_summary
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "oracle_effective_patches_service_manage" ON oracle_answer_effective_patches
  FOR ALL TO service_role USING (true) WITH CHECK (true);
