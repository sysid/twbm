/*
 cleanup/prep of bm.db --> test.db
 */
-- delete
select count(*)
from bookmarks
-- where tags not like '%,py,%';
;

select * from sqlite_master where type = 'trigger';
