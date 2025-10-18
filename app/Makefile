.PHONY: help install run run-dev run-prod check clean build dist

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install project dependencies
	uv sync

run:  ## Run the chicken coop door application (development mode)
	LOG_LEVEL=DEBUG uv run chicken-door2

run-dev:  ## Run in development mode with debug logging
	LOG_LEVEL=DEBUG uv run chicken-door2

run-prod:  ## Run in production mode (INFO logging)
	LOG_LEVEL=INFO uv run chicken-door2

build:  ## Build the project (prepare for distribution)
	@echo "Building chicken-coop-app..."
	uv sync
	@echo "✓ Build complete"

dist:  ## Create distribution package
	@echo "Creating distribution package..."
	uv build
	@echo "✓ Distribution created in dist/"

check:  ## Basic validation checks
	@echo "Checking Python version..."
	@python --version | grep -q "Python 3.1[3-9]" && echo "✓ Python version OK" || (echo "✗ Python 3.13+ required" && exit 1)
	@echo "Checking uv installation..."
	@which uv > /dev/null && echo "✓ uv installed" || (echo "✗ uv not found" && exit 1)
	@echo "Checking dependencies..."
	@uv pip list > /dev/null && echo "✓ Dependencies installed" || (echo "✗ Run 'make install' first" && exit 1)

clean:  ## Clean temporary files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf dist/ build/ 2>/dev/null || true

.DEFAULT_GOAL := help
