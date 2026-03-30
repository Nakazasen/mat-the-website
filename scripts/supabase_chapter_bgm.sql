alter table if exists chapters
  add column if not exists bgm_url text,
  add column if not exists bgm_title text;

comment on column chapters.bgm_url is 'Public URL for optional chapter background music track';
comment on column chapters.bgm_title is 'Display title for optional chapter background music track';
