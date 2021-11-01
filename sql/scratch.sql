select *
from main.bookmarks
where id = 1001
;

select *
from bookmarks_fts
order by rank
limit 20;


drop table bookmarks_fts;
CREATE VIRTUAL TABLE bookmarks_fts USING fts5
(
    id,
    URL,
    metadata,
    tags,
    "desc",
    flags UNINDEXED,
    last_update_ts UNINDEXED,
    content= 'bookmarks',
    content_rowid= 'id',
    tokenize= "porter unicode61",
);


PRAGMA table_info(bookmarks_fts);

PRAGMA table_info(bookmarks);

-- rebuild index
INSERT INTO bookmarks_fts(bookmarks_fts) VALUES('rebuild');