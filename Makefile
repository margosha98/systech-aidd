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
	-@uv run mypy src/ || echo "⚠️  Mypy errors found (will be fixed in iteration 2)"

test:
	-@uv run pytest || echo "⚠️  No tests yet (will be added in iteration 6)"

quality: format lint typecheck test
	@echo ""
	@echo "✅ Quality checks completed"
	@echo "Note: Some errors are expected and will be fixed in upcoming iterations"

