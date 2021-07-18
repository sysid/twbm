# twbm: Bookmarks via Commandline (CLI)

Inspired by https://github.com/jarun/buku.

Why not just use it directly?

- I am looking for better full-text search.
- I use tags extensively and want them to be checked during bookmark input for consistency.
- I struggle a bit with buku's user interface, getting the format right, remember the flags, ...
- I wanted some additional functionality, e.g. alphabetical ordering of `deep` results...
- I do not need tools like bukuserver, after all it's about the command line.

If you are happy using [buku](https://github.com/jarun/buku), by all means stick with it. It is a great piece of OSS.

However, there is no risk in trying [twbm](https://github.com/sysid/twbm). twbm is 100% buku compatible.   
If you do not like it you can go back without loosing your bookmark database.

Why not contribute to buku? Because I do not agree with all design decisions (see also
Architecture).

To harness `twbm`'s power, you need to use correct FTS search syntax (see: https://www.sqlite.org/fts5.html chapter 3). 

If you find a bug, please open an issue.

## Usage
There are two complementary commands:
1. **twbm**: CLI tool with FTS for bookmark management
2. **twbuku**: plain buku with small enhancements and usage of an enhanced database

This allows to use the battle-tested buku interface where applicable and benefit from additional features 
while using one enhanced bookmark database.

Getting help: `twbm --help`

### Examples
```bash
# FTS examples (https://www.sqlite.org/fts5.htm)
twbm search 'security "single-page"'
twbm search '"https://securit" *'
twbm search '^security'
twbm search 'postgres OR sqlite'
twbm search 'security NOT keycloak'

# FTS combined with tag filtering
twbm search -t tag1,tag2 -n notag1 <searchquery>

# Search -> select interactively -> pipe bookmark id downstream for processing
twbm search xxxxx | twbm update -t x
```
Taglists must not have blanks and have comma separator.

Selection of multiple bookmarks for opening in browser is possible, of course:
![Multi selection](multi-select.png)

After selecting you are straight back at the bash prompt.

## Installation
```bash
pipx twbm
```
The database schema needs to be upgraded:  
- To upgrade your existing buku db: `twbm-upgrade-db.sh buku.db twbm.db`.  
- To downgrade your existing twbm db: `twbm-downgrade-db.sh twbm.db buku.db`.  

Your existing bookmark database (`buku.db`) is not changed by the upgrade! Instead, a new database
with advanced features will be created.

Going back to `buku` is easy: Take the FTS database (`twbm.db`) and create a buku database
with reduced features (`buku.db`). Again, existing databases are not affected.

Tested configuration:  
- sqlite 3.28.0 (requires update on macOS)
- macOS 10.15.7

## Configuration
Configure the location of your sqlite database:
```bash
# aliases which I use
alias b="twbuku --db $HOME/bm.db -n 1000 --deep"  # using patched original buku

alias bb="TWBM_DB_URL=sqlite:////$HOME/bm.db twbm search"  # using extended CLI tool
alias bbb="TWBM_DB_URL=sqlite:////$HOME/bm.db twbm"
```

## Architecture
**twbm** uses certain `buku` functions in the background, but is generally rebuilt on top of: 
-  [Typer](https://typer.tiangolo.com/)  
-  [Pydantic](https://pydantic-docs.helpmanual.io/)  
-  [SQLite FTS5](https://www.sqlite.org/fts5.html)  
-  [aiosql](https://nackjicholson.github.io/aiosql/)  
-  [SQLAlchemy](https://www.sqlalchemy.org/)  
-  [alembic](https://alembic.sqlalchemy.org/en/latest/index.html)  
  
This should make it easy to extend and add functionality in an object-oriented manner.


# Development
## patch buku
- download `buku` and compare with `buku.py`
- update `buku.py`: `# tw: add title tagging` (customization: search for `# tw`)
- GOTCHA: Exclude `buku.py` from `black`
```bash
rm buku
wget https://raw.githubusercontent.com/jarun/buku/master/buku .
diff buku.py buku
```

## Local installation from sources
- install twbm with pipx for local development: `pipx install ~/dev/py/twbm`, via `make install`
- uninstall: `pipx uninstall twbm`  # GOTCHA: NOT THE PATH !!!!

## Testing
`make test`

## Roadmap
- tbd