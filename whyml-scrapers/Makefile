# WhyML Scrapers - Makefile
# Web scraping and analysis package for WhyML ecosystem

.DEFAULT_GOAL := help

# Variables
PACKAGE_NAME := whyml-scrapers
PYTHON := python3
PIP := pip3
PYTEST := pytest
COVERAGE := coverage

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m

## Help
help: ## Show this help message
	@echo "$(BLUE)WhyML Scrapers Package - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

## Development
install: ## Install package in development mode
	@echo "$(BLUE)Installing $(PACKAGE_NAME) in development mode...$(NC)"
	$(PIP) install -e .

install-deps: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install -e .[dev]

clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

## Testing
test: ## Run tests
	@echo "$(BLUE)Running tests for $(PACKAGE_NAME)...$(NC)"
	$(PYTEST) tests/ -v

test-coverage: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage for $(PACKAGE_NAME)...$(NC)"
	$(COVERAGE) run -m pytest tests/ -v
	$(COVERAGE) report -m
	$(COVERAGE) html

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	$(PYTEST) tests/ -v --tb=short -f

test-scraper: ## Test URL scraper specifically
	@echo "$(BLUE)Running URL scraper tests...$(NC)"
	$(PYTEST) tests/test_url_scraper.py -v

test-analyzer: ## Test webpage analyzer specifically
	@echo "$(BLUE)Running webpage analyzer tests...$(NC)"
	$(PYTEST) tests/test_webpage_analyzer.py -v

test-extractor: ## Test content extractor specifically
	@echo "$(BLUE)Running content extractor tests...$(NC)"
	$(PYTEST) tests/test_content_extractor.py -v

## Build & Publish
build: ## Build package
	@echo "$(BLUE)Building $(PACKAGE_NAME)...$(NC)"
	$(PYTHON) -m build

publish-test: ## Publish to test PyPI
	@echo "$(BLUE)Publishing $(PACKAGE_NAME) to test PyPI...$(NC)"
	$(PYTHON) -m twine upload --repository testpypi dist/*

publish: ## Publish to PyPI
	@echo "$(BLUE)Publishing $(PACKAGE_NAME) to PyPI...$(NC)"
	$(PYTHON) -m twine upload dist/*

version-bump: ## Bump version (requires bumpversion)
	@echo "$(BLUE)Bumping version for $(PACKAGE_NAME)...$(NC)"
	bumpversion patch

## Quality
lint: ## Run linting
	@echo "$(BLUE)Running linting for $(PACKAGE_NAME)...$(NC)"
	flake8 whyml_scrapers/ tests/
	black --check whyml_scrapers/ tests/

format: ## Format code
	@echo "$(BLUE)Formatting code for $(PACKAGE_NAME)...$(NC)"
	black whyml_scrapers/ tests/
	isort whyml_scrapers/ tests/

type-check: ## Run type checking
	@echo "$(BLUE)Running type checking for $(PACKAGE_NAME)...$(NC)"
	mypy whyml_scrapers/

## Scraping Demos
demo-scrape: ## Demo scraping functionality
	@echo "$(BLUE)Running scraping demo...$(NC)"
	$(PYTHON) -c "from whyml_scrapers import URLScraper; print('URL scraper demo ready')"

demo-analyze: ## Demo webpage analysis
	@echo "$(BLUE)Running webpage analysis demo...$(NC)"
	$(PYTHON) -c "from whyml_scrapers import WebpageAnalyzer; print('Webpage analyzer demo ready')"

test-live: ## Test scraping with live websites (careful!)
	@echo "$(YELLOW)Testing with live websites - use responsibly!$(NC)"
	$(PYTEST) tests/ -v -k "live" --tb=short

## Full workflow
all: clean install test build ## Clean, install, test, and build

.PHONY: help install install-deps clean test test-coverage test-watch test-scraper test-analyzer test-extractor build publish-test publish version-bump lint format type-check demo-scrape demo-analyze test-live all
