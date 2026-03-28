-- Manual alias map for character quick scan.
-- Purpose:
-- 1) Handle romanization/name variants that are far from wiki title.
-- 2) Improve match reliability across vi/en/zh-CN/ja.
--
-- Run in Supabase SQL editor (production first, then other envs if needed).
create extension if not exists unaccent;

create table if not exists public.wiki_character_aliases (
    id bigserial primary key,
    wiki_entry_id uuid not null references public.wiki_entries(id) on delete cascade,
    locale text not null default 'any',
    alias text not null,
    normalized_alias text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create unique index if not exists wiki_character_aliases_unique_idx
    on public.wiki_character_aliases (wiki_entry_id, locale, normalized_alias);

create index if not exists wiki_character_aliases_locale_idx
    on public.wiki_character_aliases (locale);

create index if not exists wiki_character_aliases_normalized_alias_idx
    on public.wiki_character_aliases (normalized_alias);

-- Enable RLS + read policy for public reader.
alter table public.wiki_character_aliases enable row level security;

drop policy if exists "Public can read wiki character aliases" on public.wiki_character_aliases;
create policy "Public can read wiki character aliases"
    on public.wiki_character_aliases
    for select
    using (true);

-- Maintain updated_at on row updates.
do $$
begin
    if exists (
        select 1
        from pg_proc p
        join pg_namespace n on n.oid = p.pronamespace
        where p.proname = 'update_updated_at_column'
          and n.nspname = 'public'
    ) then
        execute 'drop trigger if exists trg_wiki_character_aliases_updated_at on public.wiki_character_aliases';
        execute 'create trigger trg_wiki_character_aliases_updated_at
                 before update on public.wiki_character_aliases
                 for each row
                 execute function public.update_updated_at_column()';
    end if;
end $$;

-- Backfill baseline aliases from current wiki entries + tags.
-- locale='any' means usable across all reader locales.
insert into public.wiki_character_aliases (wiki_entry_id, locale, alias, normalized_alias)
select
    e.id,
    'any',
    e.title,
    lower(regexp_replace(unaccent(coalesce(e.title, '')), '[^[:alnum:][:space:]]', '', 'g'))
from public.wiki_entries e
where e.category = 'Nhân vật'
  and coalesce(trim(e.title), '') <> ''
on conflict (wiki_entry_id, locale, normalized_alias) do nothing;

insert into public.wiki_character_aliases (wiki_entry_id, locale, alias, normalized_alias)
select
    e.id,
    'any',
    t.tag_value,
    lower(regexp_replace(unaccent(coalesce(t.tag_value, '')), '[^[:alnum:][:space:]]', '', 'g'))
from public.wiki_entries e
cross join lateral unnest(coalesce(e.tags, array[]::text[])) as t(tag_value)
where e.category = 'Nhân vật'
  and coalesce(trim(t.tag_value), '') <> ''
on conflict (wiki_entry_id, locale, normalized_alias) do nothing;

-- Optional: add manual aliases (examples)
-- insert into public.wiki_character_aliases (wiki_entry_id, locale, alias, normalized_alias)
-- values
--   ('<wiki_entry_uuid>', 'en', 'Fang Xiang', 'fang xiang'),
--   ('<wiki_entry_uuid>', 'ja', 'ハン・フォン', 'ハン フォン'),
--   ('<wiki_entry_uuid>', 'zh-CN', '韩枫', '韩枫')
-- on conflict (wiki_entry_id, locale, normalized_alias) do nothing;
