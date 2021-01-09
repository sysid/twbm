import json
import logging
import os

import sqlite3
import sys
from itertools import chain
from typing import Optional, Tuple

_log = logging.getLogger(__name__)
LOGGER = logging.getLogger(__name__)
LOGDBG = LOGGER.debug
LOGERR = LOGGER.error

DELIM = ','  # Delimiter used to store tags in DB
BookmarkVar = Tuple[int, str, Optional[str], str, str, int]


class BukuDb:
    def __init__(self, dbfile: Optional[str] = None, colorize: Optional[bool] = True) -> None:
        self.conn, self.cur = BukuDb.initdb(dbfile)

    @staticmethod
    def get_default_dbdir():
        return '../'

    @staticmethod
    def initdb(dbfile: Optional[str] = None) -> Tuple[
        sqlite3.Connection, sqlite3.Cursor]:

        if not dbfile:
            dbpath = BukuDb.get_default_dbdir()
            filename = 'bm.db'
            dbfile = os.path.join(dbpath, filename)
        else:
            dbfile = os.path.abspath(dbfile)
            dbpath, filename = os.path.split(dbfile)

        try:
            if not os.path.exists(dbpath):
                os.makedirs(dbpath)
        except Exception as e:
            LOGERR(e)
            os._exit(1)

        db_exists = os.path.exists(dbfile)
        enc_exists = os.path.exists(dbfile + '.enc')

        try:
            # Create a connection
            conn = sqlite3.connect(dbfile, check_same_thread=False)
            # conn.create_function('REGEXP', 2, regexp)
            cur = conn.cursor()

            # Create table if it doesn't exist
            # flags: designed to be extended in future using bitwise masks
            # Masks:
            #     0b00000001: set title immutable
            cur.execute('CREATE TABLE if not exists bookmarks ('
                        'id integer PRIMARY KEY, '
                        'URL text NOT NULL UNIQUE, '
                        'metadata text default \'\', '
                        'tags text default \',\', '
                        'desc text default \'\', '
                        'flags integer default 0)')
            conn.commit()
            _log.info(f"database created: {dbfile}")
        except Exception as e:
            LOGERR('initdb(): %s', e)
            sys.exit(1)

        return conn, cur

    def get_rec_all(self):
        self.cur.execute('SELECT * FROM bookmarks')
        return self.cur.fetchall()

    def get_rec_by_id(self, index: int) -> Optional[BookmarkVar]:
        """Get a bookmark from database by its ID. """

        self.cur.execute('SELECT * FROM bookmarks WHERE id = ? LIMIT 1', (index,))
        resultset = self.cur.fetchall()
        return resultset[0] if resultset else None

    def get_rec_id(self, url) -> int:
        """Check if URL already exists in DB. """
        self.cur.execute('SELECT id FROM bookmarks WHERE URL = ? LIMIT 1', (url,))
        resultset = self.cur.fetchall()
        return resultset[0][0] if resultset else -1

    def get_max_id(self) -> int:
        """Fetch the ID of the last record. """
        self.cur.execute('SELECT MAX(id) from bookmarks')
        resultset = self.cur.fetchall()
        return -1 if resultset[0][0] is None else resultset[0][0]

    def add_rec(
            self,
            url: str,
            title_in: Optional[str] = None,
            tags_in: Optional[str] = None,
            desc: Optional[str] = None,
            immutable: Optional[int] = 0,
            delay_commit: Optional[bool] = False,  # tw: not using
            fetch: Optional[bool] = True) -> int:  # tw: not using
        """Add a new bookmark.
        Returns
        -------
        int
            DB index of new bookmark on success, -1 on failure.
        """

        # Return error for empty URL
        if not url or url == '':
            LOGERR('Invalid URL')
            return -1

        # Ensure that the URL does not exist in DB already
        id = self.get_rec_id(url)
        if id != -1:
            LOGERR('URL [%s] already exists at index %d', url, id)
            return -1

        ptitle = pdesc = ptags = ''
        LOGDBG('ptags: [%s]', ptags)

        if title_in is not None:
            ptitle = title_in

        # Fix up tags, if broken
        tags_in = delim_wrap(tags_in)

        # Process description
        if desc is None:
            desc = '' if pdesc is None else pdesc

        try:
            flagset = 0
            if immutable == 1:
                flagset |= immutable

            qry = 'INSERT INTO bookmarks(URL, metadata, tags, desc, flags) VALUES (?, ?, ?, ?, ?)'
            self.cur.execute(qry, (url, ptitle, tags_in, desc, flagset))
            self.conn.commit()
            _log.info(f"Created: {self.cur.lastrowid}")
            return self.cur.lastrowid
        except Exception as e:
            LOGERR('add_rec(): %s', e)
            return -1

    def list_using_id(self, ids=[]) -> list:
        """List entries in the DB using the specified id list. """
        q0 = 'SELECT * FROM bookmarks'
        if ids:
            q0 += ' WHERE id in ('
            for idx in ids:
                if '-' in idx:
                    val = idx.split('-')
                    if val[0]:
                        part_ids = list(map(int, val))
                        part_ids[1] += 1
                        part_ids = list(range(*part_ids))
                    else:
                        end = int(val[1])
                        qtemp = 'SELECT id FROM bookmarks ORDER BY id DESC limit {0}'.format(end)
                        self.cur.execute(qtemp, [])
                        part_ids = list(chain.from_iterable(self.cur.fetchall()))
                    q0 += ','.join(list(map(str, part_ids)))
                else:
                    q0 += idx + ','
            q0 = q0.rstrip(',')
            q0 += ')'

        try:
            self.cur.execute(q0, [])
        except sqlite3.OperationalError as e:
            LOGERR(e)
            return None
        return self.cur.fetchall()

    def cleardb(self) -> bool:
        """Drops the bookmark table if it exists. """
        raise NotImplementedError

    def get_tag_all(self) -> Tuple:
        """Get list of tags in DB.

        Returns
        -------
        tuple
            (list of unique tags sorted alphabetically,
             dictionary of {tag: usage_count}).
        """

        tags = []
        unique_tags = []
        dic = {}
        qry = 'SELECT DISTINCT tags, COUNT(tags) FROM bookmarks GROUP BY tags'
        for row in self.cur.execute(qry):
            tagset = row[0].strip(DELIM).split(DELIM)
            for tag in tagset:
                if tag not in tags:
                    dic[tag] = row[1]
                    tags += (tag,)
                else:
                    dic[tag] += row[1]

        if not tags:
            return tags, dic

        if tags[0] == '':
            unique_tags = sorted(tags[1:])
        else:
            unique_tags = sorted(tags)

        return unique_tags, dic

    @staticmethod
    def get_tagstr_from_taglist(id_list, taglist):
        """Get a string of delimiter-separated (and enclosed) string
        of tags from a dictionary of tags by matching ids.

        The inputs are the outputs from BukuDb.get_tag_all().

        Parameters
        ----------
        id_list : list
            List of ids.
        taglist : list
            List of tags.
        Returns
        -------
        str
            Delimiter separated and enclosed list of tags.
        """

        tags = DELIM

        for id in id_list:
            if is_int(id) and int(id) > 0:
                tags += taglist[int(id) - 1] + DELIM
            elif '-' in id:
                vals = [int(x) for x in id.split('-')]
                if vals[0] > vals[-1]:
                    vals[0], vals[-1] = vals[-1], vals[0]

                for _id in range(vals[0], vals[-1] + 1):
                    tags += taglist[_id - 1] + DELIM

        return tags

    def traverse_bm_folder(self, sublist, unique_tag, folder_name, add_parent_folder_as_tag) -> Tuple:
        """Traverse bookmark folders recursively and find bookmarks.

        Parameters
        ----------
        sublist : list
            List of child entries in bookmark folder.
        unique_tag : str
            Timestamp tag in YYYYMonDD format.
        folder_name : str
            Name of the parent folder.
        add_parent_folder_as_tag : bool
            True if bookmark parent folders should be added as tags else False.

        Returns
        -------
        tuple
            Bookmark record data.
        """

        for item in sublist:
            if item['type'] == 'folder':
                next_folder_name = folder_name + ',' + item['name']
                for i in self.traverse_bm_folder(
                        item['children'],
                        unique_tag,
                        next_folder_name,
                        add_parent_folder_as_tag):
                    yield i
            elif item['type'] == 'url':
                try:
                    if is_nongeneric_url(item['url']):
                        continue
                except KeyError:
                    continue

                tags = ''
                if add_parent_folder_as_tag:
                    tags += folder_name
                if unique_tag:
                    tags += DELIM + unique_tag
                # tw: add title tagging
                if ' #' in item['name']:
                    hashtags = [x.strip() for x in item['name'].split('#')[1:]]
                    tags += DELIM + DELIM.join(hashtags)
                yield item['url'], item['name'], parse_tags([tags]), None, 0, True, False

    def load_chrome_database(self, path, unique_tag, add_parent_folder_as_tag):
        """Open Chrome Bookmarks JSON file and import data.

        Parameters
        ----------
        path : str
            Path to Google Chrome bookmarks file.
        unique_tag : str
            Timestamp tag in YYYYMonDD format.
        add_parent_folder_as_tag : bool
            True if bookmark parent folders should be added as tags else False.
        """

        with open(path, 'r', encoding="utf8") as datafile:
            data = json.load(datafile)

        roots = data['roots']
        for entry in roots:
            # Needed to skip 'sync_transaction_version' key from roots
            if isinstance(roots[entry], str):
                continue
            for item in self.traverse_bm_folder(
                    roots[entry]['children'],
                    unique_tag,
                    roots[entry]['name'],
                    add_parent_folder_as_tag):
                self.add_rec(*item)

    def auto_import_from_browser(self):
        """Import bookmarks from a browser default database file.

        Supports Firefox and Google Chrome.

        Returns
        -------
        bool
            True on success, False on failure.
        """

        ff_bm_db_path = None
        gc_bm_db_path = None

        if sys.platform.startswith(('linux', 'freebsd', 'openbsd')):
            gc_bm_db_path = '~/.config/google-chrome/Default/Bookmarks'
            cb_bm_db_path = '~/.config/chromium/Default/Bookmarks'

        elif sys.platform == 'darwin':
            gc_bm_db_path = '~/Library/Application Support/Google/Chrome/Default/Bookmarks'
            cb_bm_db_path = '~/Library/Application Support/Chromium/Default/Bookmarks'

        else:
            LOGERR('buku does not support {} yet'.format(sys.platform))
            self.close_quit(1)

        newtag = None

        try:
            bookmarks_database = os.path.expanduser(gc_bm_db_path)
            if not os.path.exists(bookmarks_database):
                raise FileNotFoundError
            self.load_chrome_database(bookmarks_database, newtag, add_parent_folder_as_tag=True)
        except Exception as e:
            LOGERR(e)
            print('Could not import bookmarks from google-chrome')

        self.conn.commit()

    def close(self):
        """Close a DB connection."""

        if self.conn is not None:
            try:
                self.cur.close()
                self.conn.close()
            except Exception:
                # ignore errors here, we're closing down
                pass

    def close_quit(self, exitval=0):
        """Close a DB connection and exit.

        Parameters
        ----------
        exitval : int, optional
            Program exit value.
        """

        if self.conn is not None:
            try:
                self.cur.close()
                self.conn.close()
            except Exception:
                # ignore errors here, we're closing down
                pass
        sys.exit(exitval)


def delim_wrap(token) -> str:
    """Returns token string wrapped in delimiters. """

    if token is None or token.strip() == '':
        return DELIM

    if token[0] != DELIM:
        token = DELIM + token

    if token[-1] != DELIM:
        token = token + DELIM

    return token


def is_int(string) -> bool:
    """Check if a string is a digit. """
    try:
        int(string)
        return True
    except Exception:
        return False


def is_nongeneric_url(url) -> bool:
    """Returns True for URLs which are non-http and non-generic. """
    ignored_prefix = [
        'about:',
        'apt:',
        'chrome://',
        'file://',
        'place:',
    ]
    for prefix in ignored_prefix:
        if url.startswith(prefix):
            return True
    return False


def parse_tags(keywords=[]):
    """Format and get tag string from tokens.

    Parameters
    ----------
    keywords : list, optional
        List of tags to parse. Default is empty list.

    Returns
    -------
    str
        Comma-delimited string of tags.
    DELIM : str
        If no keywords, returns the delimiter.
    None
        If keywords is None.
    """

    if keywords is None:
        return None

    if not keywords or len(keywords) < 1 or not keywords[0]:
        return DELIM

    tags = DELIM

    # Cleanse and get the tags
    tagstr = ' '.join(keywords)
    marker = tagstr.find(DELIM)

    while marker >= 0:
        token = tagstr[0:marker]
        tagstr = tagstr[marker + 1:]
        marker = tagstr.find(DELIM)
        token = token.strip()
        if token == '':
            continue

        tags += token + DELIM

    tagstr = tagstr.strip()
    if tagstr != '':
        tags += tagstr + DELIM

    LOGDBG('keywords: %s', keywords)
    LOGDBG('parsed tags: [%s]', tags)

    if tags == DELIM:
        return tags

    # original tags in lower case
    orig_tags = tags.lower().strip(DELIM).split(DELIM)

    # Create list of unique tags and sort
    unique_tags = sorted(set(orig_tags))

    # Wrap with delimiter
    return delim_wrap(DELIM.join(unique_tags))


if __name__ == '__main__':
    log_fmt = r'%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s'
    logging.basicConfig(format=log_fmt, level=logging.DEBUG)

    # conn = sqlite3.connect('../bookmarks.db')
