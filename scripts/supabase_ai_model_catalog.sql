-- ============================================================
-- Supabase migration: AI model catalog for rotation/fallback
-- Run once in Supabase SQL Editor
-- ============================================================

begin;

alter table public.novel_settings
  add column if not exists ai_model_name text default 'gemini-3.1-flash-lite-preview';

alter table public.novel_settings
  add column if not exists ai_model_catalog jsonb default '["gemini-3.1-flash-lite-preview"]'::jsonb;

alter table public.novel_settings
  add column if not exists ai_api_key text;

update public.novel_settings
set ai_model_name = coalesce(nullif(trim(ai_model_name), ''), 'gemini-3.1-flash-lite-preview')
where ai_model_name is null or trim(ai_model_name) = '';

update public.novel_settings
set ai_model_catalog = jsonb_build_array(ai_model_name)
where ai_model_catalog is null
   or jsonb_typeof(ai_model_catalog) <> 'array'
   or jsonb_array_length(ai_model_catalog) = 0;

alter table public.novel_settings
  alter column ai_model_name set default 'gemini-3.1-flash-lite-preview';

alter table public.novel_settings
  alter column ai_model_catalog set default '["gemini-3.1-flash-lite-preview"]'::jsonb;

commit;

-- Verify current AI config
select
  id,
  ai_model_name,
  ai_model_catalog,
  case
    when ai_api_key is null or length(trim(ai_api_key)) = 0 then false
    else true
  end as has_ai_key
from public.novel_settings
order by id;
