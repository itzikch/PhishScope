.PHONY: install dev format lint test api frontend analyze docker-build docker-up docker-down clean help

# Default target
help:
	@echo "PhishScope - Evidence-Driven Phishing Analysis Agent"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Setup:"
	@echo "  install       Install dependencies using uv"
	@echo "  dev           Install dev dependencies"
	@echo "  playwright    Install Playwright browsers"
	@echo ""
	@echo "Development:"
	@echo "  format        Format code with black"
	@echo "  lint          Run pylint"
	@echo "  test          Run tests with pytest"
	@echo ""
	@echo "Running:"
	@echo "  api           Start FastAPI server (port 8070)"
	@echo "  analyze       Run analysis on a URL (URL=<url>)"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-up     Start Docker containers"
	@echo "  docker-down   Stop Docker containers"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean         Remove build artifacts and caches"

# Setup targets
install:
	uv sync

dev:
	uv sync --group dev

playwright:
	uv run playwright install chromium

# Development targets
format:
	uv run black src/

lint:
	uv run pylint src/phishscope/

test:
	uv run pytest

# Running targets
api:
	uv run phishscope serve --port 8070

analyze:
ifndef URL
	$(error URL is required. Usage: make analyze URL=https://example.com)
endif
	uv run phishscope analyze $(URL)

# Docker targets
docker-build:
	docker build -t phishscope:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Cleanup
clean:
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf src/phishscope/__pycache__
	rm -rf .ruff_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
