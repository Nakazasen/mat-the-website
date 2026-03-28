create table if not exists public.user_chapter_reads (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.profiles(id) on delete cascade,
    chapter_id bigint not null references public.chapters(id) on delete cascade,
    locale text,
    created_at timestamptz not null default now(),
    unique (user_id, chapter_id)
);

create table if not exists public.user_chapter_likes (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.profiles(id) on delete cascade,
    chapter_id bigint not null references public.chapters(id) on delete cascade,
    locale text,
    created_at timestamptz not null default now(),
    unique (user_id, chapter_id)
);

create index if not exists idx_user_chapter_reads_user_created_at
    on public.user_chapter_reads (user_id, created_at desc);

create index if not exists idx_user_chapter_likes_user_created_at
    on public.user_chapter_likes (user_id, created_at desc);

alter table public.user_chapter_reads enable row level security;
alter table public.user_chapter_likes enable row level security;

drop policy if exists "Users can read own chapter reads" on public.user_chapter_reads;
create policy "Users can read own chapter reads"
    on public.user_chapter_reads
    for select
    to authenticated
    using (auth.uid() = user_id);

drop policy if exists "Users can insert own chapter reads" on public.user_chapter_reads;
create policy "Users can insert own chapter reads"
    on public.user_chapter_reads
    for insert
    to authenticated
    with check (auth.uid() = user_id);

drop policy if exists "Users can read own chapter likes" on public.user_chapter_likes;
create policy "Users can read own chapter likes"
    on public.user_chapter_likes
    for select
    to authenticated
    using (auth.uid() = user_id);

drop policy if exists "Users can insert own chapter likes" on public.user_chapter_likes;
create policy "Users can insert own chapter likes"
    on public.user_chapter_likes
    for insert
    to authenticated
    with check (auth.uid() = user_id);
