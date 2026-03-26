-- ============================================================
-- Supabase migration: chapter translation execution status
-- Run after supabase_i18n_schema.sql
-- ============================================================

begin;

alter table public.chapter_translations
  add column if not exists last_error text;

alter table public.chapter_translations
  add column if not exists attempt_count integer not null default 0;

update public.chapter_translations
set attempt_count = 1
where coalesce(attempt_count, 0) = 0
  and translation_status = 'published';

create index if not exists idx_chapter_translations_status
  on public.chapter_translations (translation_status, locale);

commit;

select
  chapter_id,
  locale,
  translation_status,
  attempt_count,
  left(coalesce(last_error, ''), 160) as last_error_preview
from public.chapter_translations
order by chapter_id desc, locale asc
limit 50;
