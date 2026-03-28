-- Reconcile reader profile stats from canonical engagement tables.
-- Use this once to clean historical drift (exp/chapters_read mismatch).
-- Rule:
-- - chapters_read = count(distinct chapter_id) from user_chapter_reads
-- - exp = chapters_read * 10

with read_counts as (
    select
        user_id,
        count(distinct chapter_id)::int as chapters_read
    from public.user_chapter_reads
    group by user_id
)
update public.profiles p
set
    chapters_read = coalesce(rc.chapters_read, 0),
    exp = coalesce(rc.chapters_read, 0) * 10
from read_counts rc
where p.id = rc.user_id;

-- Ensure users with no reads are normalized as well.
update public.profiles p
set
    chapters_read = 0,
    exp = 0
where not exists (
    select 1
    from public.user_chapter_reads r
    where r.user_id = p.id
);
