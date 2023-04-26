APP_DIRS := consvc_shepherd contile
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

.PHONY: lint
lint: install  ##  Run various linters
	$(POETRY) run isort --check-only $(APP_DIRS) --profile black
	$(POETRY) run black --quiet --diff --check $(APP_DIRS)
	$(POETRY) run flake8 $(APP_DIRS) --ignore=E203,E302,E501,E701
	$(POETRY) run bandit --quiet -r $(APP_DIRS)

.PHONY: format
format: install  ##  Sort imports and reformat code
	$(POETRY) run isort $(APP_DIRS) --profile black
	$(POETRY) run black $(APP_DIRS)

.PHONY: migration-check
check: install
	$(POETRY) run python manage.py makemigrations --check --dry-run --noinput

.PHONY: test
test: migration-check
	env DJANGO_SETTINGS_MODULE=consvc_shepherd.settings $(POETRY) run pytest --cov --cov-report=term-missing --cov-fail-under=$(COV_FAIL_UNDER)

