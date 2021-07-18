# You can set these variables from the command line, and also from the environment for the first two.
SOURCEDIR     = source
BUILDDIR      = build
TESTDIR       = tests
MAKE          = make

VERSION       = $(shell cat twbm/__init__.py | grep __version__ | sed "s/__version__ = //" | sed "s/'//g")

.DEFAULT_GOAL := help

# Put it first so that "make" without argument is like "make help".
#help:
#	@echo "$(MAKE) [all,clean,build,upload,test,black,install,uninstall]"
#default: all

.PHONY: all
all: clean build upload tag
	@echo "--------------------------------------------------------------------------------"
	@echo "-M- building and distributing"
	@echo "--------------------------------------------------------------------------------"

.PHONY: test
test:  ## run tests
#	./scripts/test
	TWBM_DB_URL=sqlite:///test/tests_data/bm_test.db python -m py.test test -vv

.PHONY: test-shell
test-shell:  ## run tests
	./scripts/test-pipe.sh

.PHONY: clean
clean:  ## remove ./dist
	@echo "Cleaning up..."
	#git clean -Xdf
	rm -rf ./dist

.PHONY: build
build:  ## build
	@echo "building"
#	git add .
#	git commit
#	git push
	python setup.py sdist

.PHONY: upload
upload:  ## upload to PyPi
	@echo "upload"
	twine upload --verbose dist/*

.PHONY: tag
tag:  ## tag with VERSION
	@echo "tagging $(VERSION)"
	git tag -a $(VERSION) -m "version $(VERSION)"
	git push --tags

.PHONY: format
format:  ## format with black
	@echo "Formatting with black"
	#black --check --verbose --exclude="twbm/buku.py" .
	black --verbose --exclude="twbm/buku.py" .

.PHONY: init
init-db:  ## copy prod db to sql/bm.db and clean
	@cp -v $(HOME)/vimwiki/buku/bm.db $(HOME)/dev/py/twbm/sql/bm.db


.PHONY: install
install: uninstall clean build  ## pipx install
	pipx install $(HOME)/dev/py/twbm

.PHONY: uninstall
uninstall:  ## pipx uninstall
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

.PHONY: help
help: ## Show help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-20s %s\n" "task" "help" ; \
	printf "%-20s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-20s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done
