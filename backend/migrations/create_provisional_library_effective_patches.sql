-- ============================================================
-- Migration: Create provisional_library_effective_patches table
-- Purpose: Store knowledge patches generated from community feedback
-- ============================================================

CREATE TABLE IF NOT EXISTS provisional_library_effective_patches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  target_type TEXT NOT NULL,
  target_id TEXT,
  target_name TEXT,
  query_pattern TEXT,
  patch_type TEXT NOT NULL,
  effective_status TEXT NOT NULL DEFAULT 'active',
  oracle_policy TEXT NOT NULL DEFAULT 'allow',
  effective_summary TEXT,
  effective_content TEXT,
  effective_type TEXT,
  suppress_record_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  suppress_name_patterns JSONB NOT NULL DEFAULT '[]'::jsonb,
  boost_record_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
  feedback_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  confidence DOUBLE PRECISION NOT NULL DEFAULT 0,
  reason TEXT,
  created_by TEXT NOT NULL DEFAULT 'community_rag_policy_engine',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pl_effective_patches_target
ON provisional_library_effective_patches(target_type, target_id);

CREATE INDEX IF NOT EXISTS idx_pl_effective_patches_query
ON provisional_library_effective_patches(query_pattern);

CREATE INDEX IF NOT EXISTS idx_pl_effective_patches_policy
ON provisional_library_effective_patches(oracle_policy);

ALTER TABLE provisional_library_effective_patches ENABLE ROW LEVEL SECURITY;

CREATE POLICY "pl_effective_patches_public_read" ON provisional_library_effective_patches
  FOR SELECT TO public USING (true);

CREATE POLICY "pl_effective_patches_service_manage" ON provisional_library_effective_patches
  FOR ALL TO service_role USING (true) WITH CHECK (true);
