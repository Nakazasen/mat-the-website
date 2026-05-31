-- Migration: Add ai_provider_config to novel_settings
-- Purpose: Store multi-provider AI configuration as JSONB for dynamic routing
-- Run: Execute via Supabase SQL Editor or migration tool
-- Rollback: ALTER TABLE novel_settings DROP COLUMN IF EXISTS ai_provider_config;

-- Step 1: Add the JSONB column with empty default
ALTER TABLE novel_settings
ADD COLUMN IF NOT EXISTS ai_provider_config JSONB DEFAULT '{}'::jsonb;

-- Step 2: Add a comment for documentation
COMMENT ON COLUMN novel_settings.ai_provider_config IS
'Multi-provider AI configuration for translation and chatbot. Schema:
{
  "providers": {
    "<provider_name>": {
      "enabled": bool,
      "api_keys": ["..."],
      "models": ["..."],
      "default_model": "...",
      "base_url": "..." (optional, uses default if omitted),
      "timeout": int (optional, default 20)
    }
  },
  "translation_policy": {"mode": "waterfall"|"ai_pool_auto", "provider_order": [...]},
  "chat_policy": {"mode": "waterfall"|"ai_pool_auto", "provider_order": [...]}
}';
