.DEFAULT_GOAL := help

# You can set these variables from the command line, and also from the environment
SOURCEDIR     = twbm
TESTDIR       = test
MAKE          = make
VERSION       = $(shell cat VERSION)

app_root = $(PROJ_DIR)
app_root ?= .
pkg_src =  $(app_root)/twbm
tests_src = $(app_root)/test

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z0-9_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("\033[36m%-20s\033[0m %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: all
all: clean build upload tag  ## Build and upload
	@echo "--------------------------------------------------------------------------------"
	@echo "-M- building and distributing"
	@echo "--------------------------------------------------------------------------------"

.PHONY: coverage
coverage:  ## Run tests with coverage
	python -m coverage erase
	#python -m coverage run --include=$(pkg_src)/* --omit="$(pkg_src)/text.py" -m pytest -ra
	TWBM_DB_URL=sqlite:///test/tests_data/bm_test.db python -m coverage run --include=$(pkg_src)/* -m pytest -ra
	#python -m coverage report -m
	python -m coverage html
	python -m coverage report -m
	python -m coverage xml
	open htmlcov/index.html  # work on macOS

.PHONY: test
test:  ## run tests
	#TWBM_DB_URL=sqlite:///test/tests_data/bm_test.db python -m py.test test -vv
	TWBM_DB_URL=sqlite:///test/tests_data/bm_test.db python -m pytest -ra --junitxml=report.xml --cov-config=setup.cfg --cov-report=xml --cov-report term --cov=$(pkg_src) -vv test/

.PHONY: test-shell
test-shell:  ## run tests
	./scripts/test-pipe.sh

.PHONY: build
build: clean  format isort  ## format and build
	@echo "building"
	python -m build

.PHONY: upload
upload:  ## upload to PyPi
	@echo "upload"
	twine upload --verbose dist/*

.PHONY: tag
tag:  ## tag with VERSION
	@echo "tagging $(VERSION)"
	git tag -a $(VERSION) -m "version $(VERSION)"
	git push --tags

.PHONY: clean
clean: clean-build clean-pyc  ## remove all build, test, coverage and Python artifacts

.PHONY: clean-build
clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg-info' -exec rm -fr {} +
	find . \( -path ./env -o -path ./venv -o -path ./.env -o -path ./.venv \) -prune -o -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: style
style: isort format  ## perform code style format (black, isort)

.PHONY: format
format:  ## perform black formatting
	black --verbose --exclude="twbm/buku.py" $(pkg_src) test

.PHONY: isort
isort:  ## apply import sort ordering
	isort . --profile black

.PHONY: lint
lint: flake8 mypy ## lint code with all static code checks

.PHONY: flake8
flake8:  ## check style with flake8
	@flake8 $(pkg_src)

.PHONY: mypy
mypy:  ## check type hint annotations
	# keep config in setup.cfg for integration with PyCharm
	mypy --config-file setup.cfg $(pkg_src)

.PHONY: tox
tox:   ## Run tox
	tox

.PHONY: init
init-db:  ## copy prod db to sql/bm.db and clean
	@cp -v $(HOME)/vimwiki/buku/bm.db $(HOME)/dev/py/twbm/sql/bm.db

.PHONY: install
install: clean build uninstall ## pipx install
	pipx install $(HOME)/dev/py/twbm

.PHONY: uninstall
uninstall:  ## pipx uninstall
	-pipx uninstall twbm

.PHONY: bump-major
bump-major:  ## bump-major
	bumpversion --commit --verbose major

.PHONY: bump-minor
bump-minor:  ## bump-minor
	bumpversion --commit --verbose minor

.PHONY: bump-patch
bump-patch:  ## bump-patch
	bumpversion --commit --verbose patch

.PHONY: mypy
mypy:  ## mypy
	mypy --config-file setup.cfg $(SOURCEDIR)

.PHONY: flake8
flake8:  ## flake8
	flake8 $(SOURCEDIR)

.PHONY: complexity
complexity:  ## measure complexity KPIs
	radon cc --show-complexity --min C --exclude '**/buku*' $(SOURCEDIR)

.PHONY: pyroma
pyroma:  ## measure package best practice compliance
	pyroma --min 9 .

quality: mypy flake8 pyroma  ## total quality check

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
