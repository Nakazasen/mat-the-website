-- ====================================================
-- AI Oracle Cache: Store AI responses to avoid re-calling
-- the Gemini API for duplicate questions.
-- ====================================================

DROP TABLE IF EXISTS oracle_cache CASCADE;
DROP TABLE IF EXISTS oracle_rate_limits CASCADE;

-- Cache for AI responses (keyed by question hash + chapter cap)
CREATE TABLE oracle_cache (
    id              SERIAL PRIMARY KEY,
    question_hash   TEXT NOT NULL,   -- MD5/SHA256 of normalized question
    chapter_cap     INTEGER NOT NULL, -- Max chapter the response is valid for
    response        TEXT NOT NULL,   -- AI-generated response text
    source          TEXT NOT NULL DEFAULT 'gemini', -- 'gemini' | 'local_wiki'
    hit_count       INTEGER NOT NULL DEFAULT 0,     -- how many times this was served from cache
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ                     -- NULL = never expires
);

-- Unique constraint: same question + same chapter cap = same cache entry
CREATE UNIQUE INDEX idx_oracle_cache_unique ON oracle_cache (question_hash, chapter_cap);
CREATE INDEX idx_oracle_cache_hash ON oracle_cache (question_hash);

-- Rate limit tracking per IP
CREATE TABLE oracle_rate_limits (
    id          SERIAL PRIMARY KEY,
    ip_hash     TEXT NOT NULL,       -- Hashed user IP for privacy
    request_count INTEGER NOT NULL DEFAULT 0,
    window_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- Reset every 24h
    CONSTRAINT uq_ip_hash UNIQUE (ip_hash)
);

CREATE INDEX idx_oracle_rate_limits_ip ON oracle_rate_limits (ip_hash);

-- RLS: Allow public read for cache but not rate limits
ALTER TABLE oracle_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE oracle_rate_limits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role manages oracle_cache"
    ON oracle_cache FOR ALL
    USING (true);

CREATE POLICY "Service role manages oracle_rate_limits"
    ON oracle_rate_limits FOR ALL
    USING (true);

COMMENT ON TABLE oracle_cache IS 'Caches AI Oracle responses to minimize Gemini API calls and costs';
COMMENT ON TABLE oracle_rate_limits IS 'Per-IP daily rate limiting for the AI Oracle feature';
