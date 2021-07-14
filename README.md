# twbm: Bookmarks via Commandline

Inspired by https://github.com/jarun/buku. Uses it partly under the hood. So why not just use it directly?

I need better full-text search.
I use tags extensively and want them to be checked for consistency.
I struggle with the user interface, getting the format right remember the flags, ...
I wanted some additional functionality, e.g. alphabetical ordering.
I do not need bukuserver, after all it's about the command line.

If you are happy using buku, by all means stick with it. It is a great piece of OSS.

There is no risk in trying twbm. twbm is 100% buku compatible. 
If you do not like it you can go back with your bookmark collection any time without loosing anything.

## Usage Examples
### Bulk update using bash piping
```bash
echo 1 2 | python ./twbm/twb.py update -t x
```

## Configuration
```bash
TWBM_DB_URL=sqlite:////$HOME/vimwiki/buku/bm.db bb search

# alias
alias b='twbm --db <pathto>/bm.db -n 1000 --deep'  # using patched buku
alias bb='TWBM_DB_URL=sqlite://///<pathto>/bm.db bb search'  # using extended buku
```

### Loading buku DB:
use original interface, but parse additional hashtags in title. This allows to populated tags in Buku from title
hashtags.
`scripts/load_db.sh`

# Development
## Howto patch buku
- download `buku` and compare with `buku.py`
- update `buku.py`: `# tw: add title tagging` (customization: search for `# tw`)
- GOTCHA: Exclude `buku.py` from `black`
```bash
rm buku
wget https://raw.githubusercontent.com/jarun/buku/master/buku .
```

## Local installation
- install twbm with pipx for local development: `pipx install ~/dev/py/twbm`
- uninstall: `pipx uninstall twbm`  # GOTCHA: NOT THE PATH !!!!

set `main.py:DBFILE` for testing

