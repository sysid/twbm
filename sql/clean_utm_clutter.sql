/*
 Fixing URLs with utm_medium clutter
 */
-- Find URLs
select *
from main.bookmarks
where URL like '%utm_source%'
  and not URL like 'https://www.youtube.com/watch%'
;

-- Calculate replacements
select URL,
       ltrim(
               URL,
               '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*()_+-=`~[]\/{}|;:,.<>'
           ) as todelete,
       replace(
               URL,
               ltrim(URL,
                     '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*()_+-=`~[]\/{}|;:,.<>'),
               ''
           ) as result
from main.bookmarks
where URL like '%utm_source%'
  and not URL like 'https://www.youtube.com/watch%'
;

-- Update, but ignore unique constraint violations
Update or ignore bookmarks
set URL = replace(
        URL,
        ltrim(URL, '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*()_+-=`~[]\/{}|;:,.<>'),
        ''
    )
where URL like '%utm_source%'
  and not URL like 'https://www.youtube.com/watch%'
;

-- Check skipped conflicts
select *
from main.bookmarks
where URL like '%utm_source%'
  and not URL like 'https://www.youtube.com/watch%'
;

