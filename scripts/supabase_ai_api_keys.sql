-- ============================================================
-- Supabase migration: AI API key catalog for rotation
-- Run once after supabase_ai_model_catalog.sql
-- ============================================================

begin;

alter table public.novel_settings
  add column if not exists ai_api_keys jsonb default '[]'::jsonb;

update public.novel_settings
set ai_api_keys = case
    when ai_api_key is null or length(trim(ai_api_key)) = 0 then '[]'::jsonb
    else jsonb_build_array(trim(ai_api_key))
  end
where ai_api_keys is null
   or jsonb_typeof(ai_api_keys) <> 'array';

alter table public.novel_settings
  alter column ai_api_keys set default '[]'::jsonb;

commit;

-- Verify current AI key catalog
select
  id,
  ai_model_name,
  ai_model_catalog,
  ai_api_keys,
  jsonb_array_length(coalesce(ai_api_keys, '[]'::jsonb)) as ai_api_keys_count
from public.novel_settings
order by id;
