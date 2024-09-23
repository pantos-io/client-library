PYTHON_FILES := pantos/client tests

.PHONY: check-version
check-version:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION is not set"; \
		exit 1; \
	fi
	@VERSION_FROM_POETRY=$$(poetry version | awk '{print $$2}') ; \
	if test "$$VERSION_FROM_POETRY" != "$(VERSION)"; then \
		echo "Version mismatch: expected $(VERSION), got $$VERSION_FROM_POETRY" ; \
		exit 1 ; \
	else \
		echo "Version check passed" ; \
	fi

.PHONY: build
build:
	poetry build

.PHONY: code
code: check format lint sort bandit test

.PHONY: check
check:
	poetry run mypy ${PYTHON_FILES}

.PHONY: format
format:
	poetry run yapf --in-place --recursive $(PYTHON_FILES)

.PHONY: format-check
format-check:
	poetry run yapf --diff --recursive $(PYTHON_FILES)

.PHONY: lint
lint:
	poetry run flake8 $(PYTHON_FILES)

.PHONY: sort
sort:
	poetry run isort --force-single-line-imports $(PYTHON_FILES)

.PHONY: sort-check
sort-check:
	poetry run isort --force-single-line-imports $(PYTHON_FILES) --check-only

.PHONY: bandit
bandit:
	poetry run bandit -r $(PYTHON_FILES) --quiet --configfile=.bandit

.PHONY: bandit-check
bandit-check:
	poetry run bandit -r $(PYTHON_FILES) --configfile=.bandit

.PHONY: test
test:
	poetry run python3 -m pytest tests

.PHONY: coverage
coverage:
	poetry run python3 -m pytest --cov-report term-missing --cov=pantos tests

.PHONY: local-common
local-common:
ifndef DEV_PANTOS_COMMON
	$(error Please define DEV_PANTOS_COMMON variable)
endif
	$(eval CURRENT_COMMON := $(shell echo .venv/lib/python3.*/site-packages/pantos/common))
	@if [ -d "$(CURRENT_COMMON)" ]; then \
		rm -rf "$(CURRENT_COMMON)"; \
		ln -s "$(DEV_PANTOS_COMMON)" "$(CURRENT_COMMON)"; \
	else \
		echo "Directory $(CURRENT_COMMON) does not exist"; \
	fi

.PHONY: clean
clean:
	rm -r -f dist/
