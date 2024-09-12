APP_DIRS := consvc_shepherd contile openidc schema
COV_FAIL_UNDER := 95
INSTALL_STAMP := .install.stamp
POETRY := $(shell command -v poetry 2> /dev/null)
VER :=
MIGRATE ?= true

# This will be run if no target is provided
.DEFAULT_GOAL := help

.PHONY: help install isort isort-fix black black-fix flake8 bandit pydocstyle mypy lint lint-fix format local-migration-check local-migrate  test doc-install-deps doc doc-preview dev local-test makemigrations-empty migrate makemigrations remove-migration debug ruff

help: ##  show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% 0-9a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

install: $(INSTALL_STAMP)  ##  Install dependencies with poetry
$(INSTALL_STAMP): pyproject.toml poetry.lock
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) install
	touch $(INSTALL_STAMP)

isort: $(INSTALL_STAMP)  ##  Run isort in --check-only mode
	@echo "Running isort..."
	$(POETRY) run isort --check-only $(APP_DIRS) --profile black

isort-fix: $(INSTALL_STAMP)  ##  Run isort to fix imports
	@echo "Running isort..."
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

lint: $(INSTALL_STAMP) isort black flake8 bandit pydocstyle mypy ##  Run various linters

lint-fix: $(INSTALL_STAMP) isort-fix black-fix flake8 bandit pydocstyle mypy ##  Run various linters and fix errors to pass CircleCi checks

format: install  ##  Sort imports and reformat code
	$(POETRY) run isort $(APP_DIRS) --profile black
	$(POETRY) run black $(APP_DIRS)


local-migration-check: install
	$(POETRY) run python manage.py makemigrations --check --dry-run --noinput

local-migrate: install
	$(POETRY) run python manage.py makemigrations
	$(POETRY) run python manage.py migrate

test: local-migration-check
	env DJANGO_SETTINGS_MODULE=consvc_shepherd.settings $(POETRY) run pytest --cov --cov-report=term-missing --cov-fail-under=$(COV_FAIL_UNDER)

doc-install-deps:  ##  Install the dependencies for doc generation
	cargo install mdbook && cargo install mdbook-mermaid

doc: ##  Generate docs via mdBook
	mdbook-mermaid install && mdbook clean && mdbook build

doc-preview: doc  ##  Preview Merino docs via the default browser
	mdbook serve --open

dev: $(INSTALL_STAMP)  ##  Run shepherd locally and reload automatically
	docker compose up

local-test: $(INSTALL_STAMP)  ##  local test
	docker compose -f docker-compose.test.yml up --abort-on-container-exit

makemigrations-empty: ##  Create an empty migrations file for manual migrations
	docker exec -it consvc-shepherd-app-1 python manage.py makemigrations --empty consvc_shepherd

migrate: ##  Run migrate on the docker container
	docker exec -it consvc-shepherd-app-1 python manage.py migrate


makemigrations: ##  Run makemigrations on the docker container set MIGRATE=false prevent automatic migration.
	@echo "Making migrations..."
	docker exec -it consvc-shepherd-app-1 python manage.py makemigrations
	@if [ "$(MIGRATE)" = "true"]; then \
		echo "Applying migration..."; \
		docker exec -it consvc-shepherd-app-1 python manage.py migrate; \
	fi

ruff: install ##  **Experimental** Run ruff linter. To fix and format files.
	$(POETRY) run ruff check --select I --fix
	$(POETRY) run ruff format

debug: ##  Connect to docker container with docker debug.
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
		if [ "$(MIGRATE)" = "true"]; then \
			docker exec -it consvc-shepherd-app-1 python manage.py makemigrations; \
			docker exec -it consvc-shepherd-app-1 python manage.py migrate; \
		fi; \
	fi