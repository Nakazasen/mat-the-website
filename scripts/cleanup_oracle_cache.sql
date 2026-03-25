-- Xoa cac ban ghi cache Oracle bi hong / qua ngan / chi chua thong bao he thong
delete from public.oracle_cache
where response is null
   or length(trim(response)) < 24
   or lower(trim(response)) in (
        '[he thong khoi dong]',
        '[thong bao he thong]',
        '[du lieu he thong]',
        'chuong',
        'context:*'
   )
   or lower(trim(response)) like '[he thong khoi dong]%'
   or lower(trim(response)) like '[thong bao he thong]%'
   or lower(trim(response)) like '%context:*%';

-- Kiem tra nhanh cache con lai
select id, chapter_cap, source, left(response, 160) as preview, hit_count
from public.oracle_cache
order by id desc
limit 50;
