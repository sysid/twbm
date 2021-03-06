# You can set these variables from the command line, and also from the environment for the first two.
SOURCEDIR     = source
BUILDDIR      = build
TESTDIR       = tests
MAKEFILE_LIST = /tmp/makefile_list.txt
MAKE          = make

VERSION       = $(shell cat twbm/__init__.py | grep __version__ | sed "s/__version__ = //" | sed "s/'//g")

.PHONY: all help clean build test black

# Put it first so that "make" without argument is like "make help".
help:
	@echo "$(MAKE) [all,clean,build,upload,test,black,install,uninstall]"

default: all

all: clean build upload tag
	@echo "--------------------------------------------------------------------------------"
	@echo "-M- building and distributing"
	@echo "--------------------------------------------------------------------------------"

test:
#	./scripts/test
	TWBM_DB_URL=sqlite:///test/tests_data/bm_test.db python -m py.test test -vv


clean:
	@echo "Cleaning up..."
	#git clean -Xdf
	rm -rf ./dist

build:
	@echo "building"
#	git add .
#	git commit
#	git push
	python setup.py sdist

upload:
	@echo "upload"
	twine upload --verbose dist/*

tag:
	@echo "tagging $(VERSION)"
	git tag -a $(VERSION) -m "version $(VERSION)"
	git push --tags

black:
	@echo "Formatting with black"
	#black --check --verbose --exclude="twbm/buku.py" .
	black --verbose --exclude="twbm/buku.py" .

init: clean
	@cp -v $(HOME)/vimwiki/buku/bm.db $(HOME)/dev/py/twbm/sql/bm.db


install: uninstall clean build
	pipx install $(HOME)/dev/py/twbm

uninstall:
	pipx uninstall twbm

.PHONY: bump-minor
bump-minor:  ## bump-minor
	#bumpversion --dry-run --allow-dirty --verbose patch
	#bumpversion --verbose patch
	bumpversion --verbose minor

.PHONY: bump-patch
bump-patch:  ## bump-patch
	#bumpversion --dry-run --allow-dirty --verbose patch
	bumpversion --verbose patch
