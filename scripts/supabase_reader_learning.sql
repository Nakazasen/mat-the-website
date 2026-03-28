-- ============================================================
-- Reader Learning Schema
-- MVP foundation for English / Japanese / Chinese learning tools
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE FUNCTION set_reader_learning_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE IF NOT EXISTS reader_lookup_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    locale TEXT NOT NULL,
    normalized_term TEXT NOT NULL,
    context_hash TEXT NOT NULL,
    payload_json JSONB NOT NULL,
    source TEXT NOT NULL DEFAULT 'ai',
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (locale, normalized_term, context_hash)
);

CREATE TABLE IF NOT EXISTS reader_saved_vocab (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    locale TEXT NOT NULL,
    term TEXT NOT NULL,
    normalized_term TEXT NOT NULL,
    reading TEXT,
    meaning_vi TEXT,
    pos TEXT,
    notes TEXT,
    context_sentence TEXT,
    chapter_id BIGINT REFERENCES chapters(id) ON DELETE SET NULL,
    source TEXT NOT NULL DEFAULT 'lookup',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reader_saved_sentences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    locale TEXT NOT NULL,
    sentence_text TEXT NOT NULL,
    meaning_vi TEXT,
    note TEXT,
    chapter_id BIGINT REFERENCES chapters(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reader_vocab_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    saved_vocab_id UUID NOT NULL UNIQUE REFERENCES reader_saved_vocab(id) ON DELETE CASCADE,
    ease NUMERIC NOT NULL DEFAULT 2.5,
    interval_days INTEGER NOT NULL DEFAULT 0,
    next_review_at TIMESTAMPTZ,
    last_reviewed_at TIMESTAMPTZ,
    review_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reader_lookup_cache_lookup
    ON reader_lookup_cache (locale, normalized_term, context_hash);

CREATE INDEX IF NOT EXISTS idx_reader_saved_vocab_user_locale
    ON reader_saved_vocab (user_id, locale, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_reader_saved_sentences_user_locale
    ON reader_saved_sentences (user_id, locale, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_reader_vocab_reviews_next_review
    ON reader_vocab_reviews (next_review_at);

DROP TRIGGER IF EXISTS trg_reader_lookup_cache_updated_at ON reader_lookup_cache;
CREATE TRIGGER trg_reader_lookup_cache_updated_at
BEFORE UPDATE ON reader_lookup_cache
FOR EACH ROW
EXECUTE FUNCTION set_reader_learning_updated_at();

DROP TRIGGER IF EXISTS trg_reader_saved_vocab_updated_at ON reader_saved_vocab;
CREATE TRIGGER trg_reader_saved_vocab_updated_at
BEFORE UPDATE ON reader_saved_vocab
FOR EACH ROW
EXECUTE FUNCTION set_reader_learning_updated_at();

DROP TRIGGER IF EXISTS trg_reader_vocab_reviews_updated_at ON reader_vocab_reviews;
CREATE TRIGGER trg_reader_vocab_reviews_updated_at
BEFORE UPDATE ON reader_vocab_reviews
FOR EACH ROW
EXECUTE FUNCTION set_reader_learning_updated_at();

ALTER TABLE reader_lookup_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE reader_saved_vocab ENABLE ROW LEVEL SECURITY;
ALTER TABLE reader_saved_sentences ENABLE ROW LEVEL SECURITY;
ALTER TABLE reader_vocab_reviews ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public can read reader lookup cache" ON reader_lookup_cache;
CREATE POLICY "Public can read reader lookup cache"
    ON reader_lookup_cache
    FOR SELECT
    USING (TRUE);

DROP POLICY IF EXISTS "Users can manage own saved vocab" ON reader_saved_vocab;
CREATE POLICY "Users can manage own saved vocab"
    ON reader_saved_vocab
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage own saved sentences" ON reader_saved_sentences;
CREATE POLICY "Users can manage own saved sentences"
    ON reader_saved_sentences
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage own vocab reviews" ON reader_vocab_reviews;
CREATE POLICY "Users can manage own vocab reviews"
    ON reader_vocab_reviews
    FOR ALL
    USING (
        EXISTS (
            SELECT 1
            FROM reader_saved_vocab
            WHERE reader_saved_vocab.id = reader_vocab_reviews.saved_vocab_id
              AND reader_saved_vocab.user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1
            FROM reader_saved_vocab
            WHERE reader_saved_vocab.id = reader_vocab_reviews.saved_vocab_id
              AND reader_saved_vocab.user_id = auth.uid()
        )
    );
