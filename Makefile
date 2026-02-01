.PHONY: all
all: check

.PHONY: check
check:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy .
	uv run pytest

.PHONY: format
format:
	uv run ruff check . --fix
	uv run ruff format .

.PHONY: format-and-check
format-and-check:
	$(MAKE) format
	$(MAKE) check
