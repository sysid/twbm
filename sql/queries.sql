-- name: get_all
select *
from bookmarks;

/*
 For tracking the database version, I use the built in user-version variable that sqlite provides
 (sqlite does nothing with this variable, you are free to use it however you please).
 It starts at 0, and you can get/set this variable with the following sqlite statements:
 */
-- name: get_user_version
PRAGMA user_version;

-- PRAGMA user_version = 1;
