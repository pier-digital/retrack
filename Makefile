.PHONY: init
init:
	poetry install -n

.PHONY: formatting
formatting:
	poetry run ruff format .

.PHONY: check-formatting
check-formatting:
	poetry run ruff check .

.PHONY: linting
linting: formatting check-formatting

.PHONY: tests
tests:
	poetry run pytest | tee pytest-coverage.txt
