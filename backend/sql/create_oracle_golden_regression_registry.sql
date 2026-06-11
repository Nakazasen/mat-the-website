-- create_oracle_golden_regression_registry.sql
-- Migration file for Oracle Golden Cases & Registry

-- Enable uuid-ossp if gen_random_uuid is used (or gen_random_uuid is built-in in postgres 13+)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table 1: oracle_golden_regression_cases
CREATE TABLE IF NOT EXISTS oracle_golden_regression_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_key TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    question TEXT NOT NULL,
    chapter_progress INTEGER,
    intent TEXT,
    must_not_contain JSONB DEFAULT '[]'::jsonb,
    semantic_forbidden_patterns JSONB DEFAULT '[]'::jsonb,
    semantic_required_any_terms JSONB DEFAULT '[]'::jsonb,
    acceptable_abstain BOOLEAN DEFAULT false,
    expected_abstain_text TEXT,
    status TEXT DEFAULT 'active',
    created_from_feedback_id UUID,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Table 2: oracle_golden_regression_runs
CREATE TABLE IF NOT EXISTS oracle_golden_regression_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_key TEXT NOT NULL,
    base_url TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    reason TEXT,
    answer_excerpt TEXT,
    source TEXT,
    response_status INTEGER,
    run_at TIMESTAMPTZ DEFAULT now(),
    git_commit TEXT,
    workflow_run_id TEXT
);

-- Enable RLS
ALTER TABLE oracle_golden_regression_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE oracle_golden_regression_runs ENABLE ROW LEVEL SECURITY;

-- Allow service_role to manage all cases
CREATE POLICY "Allow service_role full access to cases"
    ON oracle_golden_regression_cases
    FOR ALL TO service_role
    USING (true) WITH CHECK (true);

-- Allow service_role to manage all runs
CREATE POLICY "Allow service_role full access to runs"
    ON oracle_golden_regression_runs
    FOR ALL TO service_role
    USING (true) WITH CHECK (true);
