create table if not exists chapter_translations (
    id uuid primary key default gen_random_uuid(),
    chapter_id bigint not null references chapters(id) on delete cascade,
    locale text not null,
    title text not null,
    content text not null,
    summary text,
    translation_status text not null default 'draft',
    translation_source text not null default 'ai',
    translated_at timestamptz,
    sentence_alignment jsonb,
    content_hash text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (chapter_id, locale)
);

create table if not exists novel_settings_translations (
    id uuid primary key default gen_random_uuid(),
    novel_settings_id bigint not null,
    locale text not null,
    title text not null,
    description text,
    seo_title text,
    seo_description text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (novel_settings_id, locale)
);

create table if not exists wiki_entry_translations (
    id uuid primary key default gen_random_uuid(),
    wiki_entry_id uuid not null references wiki_entries(id) on delete cascade,
    locale text not null,
    title text not null,
    summary text,
    content text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (wiki_entry_id, locale)
);

create table if not exists homepage_settings_translations (
    id uuid primary key default gen_random_uuid(),
    homepage_settings_id bigint not null,
    locale text not null,
    warning_title text,
    warning_subtitle text,
    warning_headline text,
    warning_description text,
    features_title text,
    features_json jsonb not null default '[]'::jsonb,
    translation_status text not null default 'draft',
    translation_source text not null default 'ai',
    translated_at timestamptz,
    content_hash text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (homepage_settings_id, locale)
);

create table if not exists tts_audio_cache (
    id uuid primary key default gen_random_uuid(),
    entity_type text not null,
    entity_id bigint not null,
    locale text not null,
    voice text not null,
    provider text not null,
    content_hash text not null,
    audio_url text not null,
    duration_sec numeric,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (entity_type, entity_id, locale, voice, content_hash)
);

create index if not exists idx_chapter_translations_chapter_locale
    on chapter_translations (chapter_id, locale);

create index if not exists idx_wiki_entry_translations_entry_locale
    on wiki_entry_translations (wiki_entry_id, locale);

create index if not exists idx_homepage_settings_translations_lookup
    on homepage_settings_translations (homepage_settings_id, locale);

create index if not exists idx_tts_audio_cache_lookup
    on tts_audio_cache (entity_type, entity_id, locale, voice, content_hash);
