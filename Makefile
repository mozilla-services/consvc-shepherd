APP_DIRS := consvc_shepherd contile openidc schema
COV_FAIL_UNDER := 95
INSTALL_STAMP := .install.stamp
POETRY := $(shell command -v poetry 2> /dev/null)
NPM := $(shell command -v npm 2> /dev/null)
VER :=
MIGRATE ?= true

# This will be run if no target is provided
.DEFAULT_GOAL := help

.PHONY: help install isort isort-fix black black-fix flake8 bandit pydocstyle mypy lint lint-fix eslint eslint-fix format local-migration-check local-migrate test test-django test-react doc-install-deps doc doc-preview dev local-test local-test-django local-test-react makemigrations-empty migrate makemigrations remove-migration debug ruff

help: ##  show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% 0-9a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

install: $(INSTALL_STAMP)  ##  Install dependencies with poetry and npm
$(INSTALL_STAMP): pyproject.toml poetry.lock
	# Python dependencies
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) install
	# Node dependencies
	@if [ -z $(NPM) ]; then echo "Npm could not be found. See npm install instructions for your platform"; exit 2; fi
	cd ad-ops-dashboard && $(NPM) install
	touch $(INSTALL_STAMP)

isort: $(INSTALL_STAMP)  ##  Run isort in --check-only mode
	@echo "Running isort..."
	$(POETRY) run isort --check-only $(APP_DIRS) --profile black

isort-fix: $(INSTALL_STAMP)  ##  Run isort to fix imports
	@echo "Running isort with autofix..."
	$(POETRY) run isort  $(APP_DIRS) --profile black

black: $(INSTALL_STAMP)  ##  Run black
	@echo "Running black..."
	$(POETRY) run black --quiet --diff --check --color $(APP_DIRS)

black-fix: $(INSTALL_STAMP)  ##  Format code with Black
	@echo "Running black with autofix..."
	$(POETRY) run black --quiet $(APP_DIRS)

flake8: $(INSTALL_STAMP)  ##  Run flake8
	@echo "Running flake8..."
	$(POETRY) run flake8 $(APP_DIRS) --max-line-length=120

bandit: $(INSTALL_STAMP)  ##  Run bandit
	@echo "Running bandit..."
	$(POETRY) run bandit --quiet -r $(APP_DIRS) -c "pyproject.toml"

pydocstyle: $(INSTALL_STAMP)  ##  Run pydocstyle
	@echo "Running pydocstyle..."
	$(POETRY) run pydocstyle $(APP_DIRS) --explain --config="pyproject.toml"

mypy: $(INSTALL_STAMP)  ##  Run mypy
	@echo "Running mypy..."
	$(POETRY) run mypy $(APP_DIRS) --config-file="pyproject.toml"

eslint: $(INSTALL_STAMP)  ##  Run eslint
	@echo "Running eslint ..."
	cd ad-ops-dashboard && npm run lint

eslint-fix: $(INSTALL_STAMP)  ##  Format code with eslint
	@echo "Running eslint with autofix..."
	cd ad-ops-dashboard && npm run lint:fix

# Temporarily disable eslint while we fix the current issues in the ad-ops-dashboard
lint: $(INSTALL_STAMP) isort black flake8 bandit pydocstyle mypy eslint ##  Run various linters

lint-fix: $(INSTALL_STAMP) isort-fix black-fix flake8 bandit pydocstyle mypy eslint-fix ##  Run various linters and fix errors to pass CircleCi checks

format: install  ##  Sort imports and reformat code
	$(POETRY) run isort $(APP_DIRS) --profile black
	$(POETRY) run black $(APP_DIRS)

local-migration-check: install # Check if any DB migrations need to be run
	$(POETRY) run python manage.py makemigrations --check --dry-run --noinput

local-migrate: install # Create DB migrations from models and apply them in one command
	$(POETRY) run python manage.py makemigrations
	$(POETRY) run python manage.py migrate

test-django: local-migration-check # Run the tests for the shepherd Django app in CI
	env DJANGO_SETTINGS_MODULE=consvc_shepherd.settings $(POETRY) run pytest --cov --cov-report=term-missing --cov-fail-under=$(COV_FAIL_UNDER)

test-react: # Run the tests for the ad-ops-dashboard React app in CI
	cd ad-ops-dashboard && npm run test:ci

test: test-django test-react  ##  Run all tests in CI

doc-install-deps:  ##  Install the dependencies for doc generation
	cargo install mdbook && cargo install mdbook-mermaid

doc: ##  Generate docs via mdBook
	mdbook-mermaid install && mdbook clean && mdbook build

doc-preview: doc  ##  Preview Merino docs via the default browser
	mdbook serve --open

dev: $(INSTALL_STAMP)  ## Run shepherd locally and show human readable timestamps.
	docker compose up -d && docker-compose logs -f -t

local-test-django: $(INSTALL_STAMP) # Run shepherd Django app tests locally
	docker compose -f docker-compose.test-django.yml up --abort-on-container-exit

local-test-react: # Run ad-ops-ad-ops-dashboard React app tests locally
	docker compose -f docker-compose.test-react.yml up --abort-on-container-exit

local-test: local-test-django local-test-react   ##  Run all tests when developing locally

makemigrations-empty: ##  Create an empty migrations file for manual migrations
	docker exec -it consvc-shepherd-app-1 python manage.py makemigrations --empty consvc_shepherd

migrate: ##  Run migrate on the docker container
	docker exec -it consvc-shepherd-app-1 python manage.py migrate

makemigrations: ##  Run makemigrations on the docker container set MIGRATE=false prevent automatic migration.
	@echo "Making migrations..."
	docker exec -it consvc-shepherd-app-1 python manage.py makemigrations
	@if [ "$(MIGRATE)" = "true" ]; then \
		echo "Applying migration..."; \
		docker exec -it consvc-shepherd-app-1 python manage.py migrate; \
	fi

ruff: install ##  **Experimental** Run ruff linter. To fix and format files.
	@echo "Running Mypy..."
	$(POETRY) run mypy $(APP_DIRS) --config-file="pyproject.toml"
	@echo "Running Ruff..."
	$(POETRY) run ruff check
	$(POETRY) run ruff format

debug: ##  Connect to the shepherd container with docker debug.
	docker debug consvc-shepherd-app-1

remove-migration: install  ##  Run command to undo migrations add VER= to set the migration number e.g. 0002
	@if [ -z "$(VER)" ]; then \
		echo "You must provide a migration version using VER=<version>"; \
	else \
		docker exec -it consvc-shepherd-app-1 python manage.py migrate consvc_shepherd ${VER}; \
	fi

remove-migration-fix: install  ##  Run command to undo migrations, delete the corresponding files, recreate migrations and perform the migration. Add VER= to set the migration number e.g. 0002

	@if [ -z "$(VER)" ]; then \
		echo "You must provide a migration version using VER=<version>"; \
	else \
		echo "Undoing migrations for version $(VER)..."; \
		docker exec -it consvc-shepherd-app-1 python manage.py migrate consvc_shepherd $(VER); \
		echo "Removing migration files greater than version $(VER)..."; \
		for file in consvc_shepherd/migrations/????_*.py; do \
			base_filename="$${file##*/}"; \
			migration_number="$${base_filename%%_*}"; \
			if [ "$${migration_number}" -gt "$(VER)" ]; then \
				echo "Removing $${file}"; \
				rm -f "$${file}"; \
			fi; \
		done; \
		echo "Migration files removed."; \
		echo "Generating New Migration file."; \
		if [ "$(MIGRATE)" = "true" ]; then \
			docker exec -it consvc-shepherd-app-1 python manage.py makemigrations; \
			docker exec -it consvc-shepherd-app-1 python manage.py migrate; \
		fi; \
	fi
