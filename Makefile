.PHONY: init
init:
	poetry install -n

.PHONY: formatting
formatting:
	poetry run isort --settings-path pyproject.toml ./
	poetry run black --config pyproject.toml ./

.PHONY: check-formatting
check-formatting:
	poetry run isort --settings-path pyproject.toml --check-only ./
	poetry run black --config pyproject.toml --check ./

.PHONY: tests
tests:
	poetry run pytest | tee pytest-coverage.txt
