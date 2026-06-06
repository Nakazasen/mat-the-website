-- ============================================================
-- Migration: Create RAG feedback and corrections tables
-- Purpose: Support audit trails and reader corrections for the RAG chatbot
-- ============================================================

-- Step 1: Create rag_feedback table
CREATE TABLE IF NOT EXISTS rag_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    answer TEXT,
    source TEXT,
    citations JSONB DEFAULT '[]'::jsonb,
    chapter_progress INTEGER,
    feedback_type TEXT NOT NULL,
    user_comment TEXT,
    suggested_correction TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT chk_feedback_type CHECK (feedback_type IN ('wrong', 'missing', 'spoiler', 'hallucination', 'other')),
    CONSTRAINT chk_feedback_status CHECK (status IN ('pending', 'reviewed', 'accepted', 'rejected', 'resolved'))
);

-- Step 2: Create rag_corrections table
CREATE TABLE IF NOT EXISTS rag_corrections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback_id UUID REFERENCES rag_feedback(id) ON DELETE SET NULL,
    entity_name TEXT,
    correction_type TEXT NOT NULL,
    proposed_content TEXT,
    evidence JSONB DEFAULT '[]'::jsonb,
    status TEXT NOT NULL DEFAULT 'draft',
    reviewer_note TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT chk_correction_type CHECK (correction_type IN ('wiki_update', 'entity_profile', 'eval_case', 'retrieval_rule', 'other')),
    CONSTRAINT chk_correction_status CHECK (status IN ('draft', 'approved', 'rejected', 'applied'))
);

-- Step 3: Create indexes
CREATE INDEX IF NOT EXISTS idx_rag_feedback_status ON rag_feedback(status);
CREATE INDEX IF NOT EXISTS idx_rag_feedback_created_at ON rag_feedback(created_at);
CREATE INDEX IF NOT EXISTS idx_rag_corrections_status ON rag_corrections(status);
CREATE INDEX IF NOT EXISTS idx_rag_corrections_feedback_id ON rag_corrections(feedback_id);

-- Step 4: Row Level Security (RLS)
ALTER TABLE rag_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_corrections ENABLE ROW LEVEL SECURITY;

-- Allow public to insert feedback (anonymous submission)
CREATE POLICY "feedback_anonymous_insert" ON rag_feedback
    FOR INSERT TO public WITH CHECK (true);

-- Allow service_role to manage all feedback
CREATE POLICY "feedback_service_manage" ON rag_feedback
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Allow service_role to manage all corrections
CREATE POLICY "corrections_service_manage" ON rag_corrections
    FOR ALL TO service_role USING (true) WITH CHECK (true);
