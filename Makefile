.PHONY: init
init:
	poetry install -n

.PHONY: check-formatting
check-formatting:
	poetry run ruff check .

.PHONY: formatting
formatting: check-formatting
	poetry run ruff format .

.PHONY: linting
linting: formatting check-formatting

.PHONY: tests
tests:
	poetry run pytest | tee pytest-coverage.txt
