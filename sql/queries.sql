-- name: get_all
select *
from bookmarks;

-- name: create_db#
CREATE TABLE IF NOT EXISTS "main"."bookmarks" (
    "id" INTEGER PRIMARY KEY,
    "URL" TEXT NOT NULL UNIQUE,
    "metadata" text default '',
    "tags" text default ',',
    "desc" text default '',
    "flags" integer default '',
    "last_update_ts" DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER [UpdateLastTime]
    AFTER
    UPDATE
    ON bookmarks
    FOR EACH ROW
    WHEN NEW.last_update_ts <= OLD.last_update_ts
BEGIN
    update bookmarks set last_update_ts=CURRENT_TIMESTAMP where id=OLD.id;
END;

/*
 For tracking the database version, I use the built in user-version variable that sqlite provides
 (sqlite does nothing with this variable, you are free to use it however you please).
 It starts at 0, and you can get/set this variable with the following sqlite statements:
 */
-- name: get_user_version
PRAGMA user_version;

-- PRAGMA user_version = 1;
