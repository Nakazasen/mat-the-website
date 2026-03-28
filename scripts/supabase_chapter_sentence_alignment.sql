alter table public.chapter_translations
  add column if not exists sentence_alignment jsonb;

comment on column public.chapter_translations.sentence_alignment is
  'Rule-based sentence alignment map from translated sentence to Vietnamese source excerpt.';
