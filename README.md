# twbm

Fork of https://github.com/jarun/buku.

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
install buku with pipx

```bash
rm buku
wget https://raw.githubusercontent.com/jarun/buku/master/buku ~/dev/py/bookmark/bookmark
patch it: `# tw: add title tagging`
```

set `main.py:DBFILE` for testing

