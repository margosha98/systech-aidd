.PHONY: install run run-api run-api-dev format lint typecheck test quality
.PHONY: install-frontend run-frontend build-frontend lint-frontend format-frontend
.PHONY: install-all run-all

# Backend commands
install:
	uv sync

run:
	uv run python -m src.main

run-api:
	uv run python -m backend.api

run-api-dev:
	uv run uvicorn backend.api.server:app --reload --port 8000

format:
	uv run ruff format src/ backend/

lint:
	uv run ruff check src/ backend/

typecheck:
	uv run mypy src/ backend/

test:
	uv run pytest

quality: format lint typecheck test
	@echo ""
	@echo "✅ All quality checks passed!"

stop:
    powershell -Command "Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force"

# Frontend commands
install-frontend:
	cd frontend && pnpm install

run-frontend:
	cd frontend && pnpm dev

build-frontend:
	cd frontend && pnpm build

lint-frontend:
	cd frontend && pnpm lint

format-frontend:
	cd frontend && pnpm format

type-check-frontend:
	cd frontend && pnpm type-check

# Full stack commands
install-all: install install-frontend
	@echo ""
	@echo "✅ All dependencies installed!"

run-all:
	@echo "Starting backend API and frontend..."
	@start /B cmd /C "make run-api-dev"
	@timeout /t 3 /nobreak > nul
	@start /B cmd /C "make run-frontend"
	@echo "Backend API: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
