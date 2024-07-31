APP_DIRS := consvc_shepherd contile openidc schema
COV_FAIL_UNDER := 95
INSTALL_STAMP := .install.stamp
POETRY := $(shell command -v poetry 2> /dev/null)

# This will be run if no target is provided
.DEFAULT_GOAL := help

.PHONY: install
install: $(INSTALL_STAMP)  ##  Install dependencies with poetry
$(INSTALL_STAMP): pyproject.toml poetry.lock
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) install
	touch $(INSTALL_STAMP)

.PHONY: isort
isort: $(INSTALL_STAMP)  ##  Run isort
	$(POETRY) run isort --check-only $(APP_DIRS) --profile black

.PHONY: black
black: $(INSTALL_STAMP)  ##  Run black
	$(POETRY) run black --quiet --diff --check $(APP_DIRS)

.PHONY: flake8
flake8: $(INSTALL_STAMP)  ##  Run flake8
	$(POETRY) run flake8 $(APP_DIRS) --max-line-length=120

.PHONY: bandit
bandit: $(INSTALL_STAMP)  ##  Run bandit
	$(POETRY) run bandit --quiet -r $(APP_DIRS) -c "pyproject.toml"

.PHONY: pydocstyle
pydocstyle: $(INSTALL_STAMP)  ##  Run pydocstyle
	$(POETRY) run pydocstyle $(APP_DIRS) --explain --config="pyproject.toml"

.PHONY: mypy
mypy: $(INSTALL_STAMP)  ##  Run mypy
	$(POETRY) run mypy $(APP_DIRS) --config-file="pyproject.toml"

.PHONY: lint
lint: $(INSTALL_STAMP) isort black flake8 bandit pydocstyle mypy ##  Run various linters

.PHONY: format
format: install  ##  Sort imports and reformat code
	$(POETRY) run isort $(APP_DIRS) --profile black
	$(POETRY) run black $(APP_DIRS)

.PHONY: migration-check
migration-check: install
	$(POETRY) run python manage.py makemigrations --check --dry-run --noinput

.PHONY: migrate
migrate: install
	$(POETRY) run python manage.py makemigrations
	$(POETRY) run python manage.py migrate

.PHONY: test
test: migration-check
	env DJANGO_SETTINGS_MODULE=consvc_shepherd.settings $(POETRY) run pytest --cov --cov-report=term-missing --cov-fail-under=$(COV_FAIL_UNDER)

.PHONY: doc-install-deps
doc-install-deps:  ## Install the dependencies for doc generation
	cargo install mdbook && cargo install mdbook-mermaid

.PHONY: doc
doc: ##  Generate docs via mdBook
	mdbook-mermaid install && mdbook clean && mdbook build  

.PHONY: doc-preview
doc-preview: doc  ##  Preview Merino docs via the default browser
	mdbook serve --open

.PHONY: dev
dev: $(INSTALL_STAMP)  ##  Run shepherd locally and reload automatically
	docker-compose up

.PHONY: local-test
local-test: $(INSTALL_STAMP)
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit
