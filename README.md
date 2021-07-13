# twbm

Fork of https://github.com/jarun/buku.

## Configuration
```bash
TWBM_DB_URL=sqlite:////$HOME/vimwiki/buku/bm.db bb search
```

## Reason
I do not need bukuserver.
I need to have some additional functionality in buku, e.g. alphabetical ordering, ...


## Personal Notes
Collection of bookmark handling utilities.

### Loading buku DB:
use original interface, but parse additional hashtags in title. This allows to populated tags in Buku from title
hashtags.
`scripts/load_db.sh`

### Howto patch buku
install twbm with pipx for local development: `pipx install ~/dev/py/twbm`
uninstall: `pipx uninstall twbm`  # GOTCHA: NOT THE PATH !!!!

```bash
rm buku
wget https://raw.githubusercontent.com/jarun/buku/master/buku .

# Update buku.py
patch it: `# tw: add title tagging`
```

set `main.py:DBFILE` for testing

