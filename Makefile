.PHONY: init
init:
	poetry install -n

.PHONY: formatting
formatting:
	poetry run isort --settings-path pyproject.toml ./
	poetry run black --config pyproject.toml ./

.PHONE: check-formatting
check-formatting:
	poetry run isort --settings-path pyproject.toml --check-only ./
	poetry run black --config pyproject.toml --check ./

.PHONY: tests
tests:
	poetry run pytest