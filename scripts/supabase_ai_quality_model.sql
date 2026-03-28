alter table public.novel_settings
  add column if not exists ai_quality_model_name text default 'gemini-2.5-flash';

update public.novel_settings
set ai_quality_model_name = 'gemini-2.5-flash'
where ai_quality_model_name is null or length(trim(ai_quality_model_name)) = 0;

alter table public.novel_settings
  alter column ai_quality_model_name set default 'gemini-2.5-flash';
