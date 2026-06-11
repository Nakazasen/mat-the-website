-- create_oracle_golden_regression_candidates.sql
-- Migration file for Oracle Golden Regression Candidates

CREATE TABLE IF NOT EXISTS oracle_golden_regression_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_key TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    trust_level TEXT NOT NULL,
    question TEXT NOT NULL,
    chapter_progress INTEGER,
    feedback_ids JSONB DEFAULT '[]'::jsonb,
    error_signature TEXT,
    intent TEXT,
    must_not_contain JSONB DEFAULT '[]'::jsonb,
    semantic_forbidden_patterns JSONB DEFAULT '[]'::jsonb,
    semantic_required_any_terms JSONB DEFAULT '[]'::jsonb,
    acceptable_abstain BOOLEAN DEFAULT true,
    expected_abstain_text TEXT,
    evidence JSONB DEFAULT '{}'::jsonb,
    runtime_repro_passed BOOLEAN DEFAULT false,
    promotion_score NUMERIC DEFAULT 0,
    promotion_status TEXT DEFAULT 'candidate',
    promotion_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE oracle_golden_regression_candidates ENABLE ROW LEVEL SECURITY;

-- Drop policy if exists to prevent duplicate creation errors
DROP POLICY IF EXISTS "Allow service_role full access to candidates" ON oracle_golden_regression_candidates;

-- Allow service_role to manage all candidates
CREATE POLICY "Allow service_role full access to candidates"
    ON oracle_golden_regression_candidates
    FOR ALL TO service_role
    USING (true) WITH CHECK (true);

