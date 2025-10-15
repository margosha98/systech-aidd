.PHONY: install run format lint typecheck test quality

install:
	uv sync

run:
	uv run python -m src.main

format:
	uv run ruff format src/

lint:
	uv run ruff check src/

typecheck:
	uv run mypy src/

test:
	uv run pytest

quality: format lint typecheck test
	@echo ""
	@echo "✅ All quality checks passed!"

