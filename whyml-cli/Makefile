# WhyML CLI - Makefile
# Command-line interface package for WhyML ecosystem

.DEFAULT_GOAL := help

# Variables
PACKAGE_NAME := whyml-cli
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
	@echo "$(BLUE)WhyML CLI Package - Available Commands$(NC)"
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

test-cli: ## Test CLI functionality specifically
	@echo "$(BLUE)Running CLI tests...$(NC)"
	$(PYTEST) tests/test_cli.py -v

test-commands: ## Test CLI commands specifically
	@echo "$(BLUE)Running CLI command tests...$(NC)"
	$(PYTEST) tests/test_commands.py -v

test-integration: ## Run integration tests
	@echo "$(BLUE)Running CLI integration tests...$(NC)"
	$(PYTEST) tests/ -v -k "integration"

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
	flake8 whyml_cli/ tests/
	black --check whyml_cli/ tests/

format: ## Format code
	@echo "$(BLUE)Formatting code for $(PACKAGE_NAME)...$(NC)"
	black whyml_cli/ tests/
	isort whyml_cli/ tests/

type-check: ## Run type checking
	@echo "$(BLUE)Running type checking for $(PACKAGE_NAME)...$(NC)"
	mypy whyml_cli/

## CLI Testing
demo-scrape: ## Demo CLI scraping command
	@echo "$(BLUE)Testing CLI scrape command...$(NC)"
	$(PYTHON) -m whyml_cli.cli scrape --help

demo-convert: ## Demo CLI convert command
	@echo "$(BLUE)Testing CLI convert command...$(NC)"
	$(PYTHON) -m whyml_cli.cli convert --help

demo-validate: ## Demo CLI validate command
	@echo "$(BLUE)Testing CLI validate command...$(NC)"
	$(PYTHON) -m whyml_cli.cli validate --help

test-cli-live: ## Test CLI with sample data (requires data folder)
	@echo "$(BLUE)Testing CLI with sample data...$(NC)"
	@if [ -f "../data/manifest.yaml" ]; then \
		$(PYTHON) -m whyml_cli.cli validate ../data/manifest.yaml; \
	else \
		echo "$(YELLOW)Sample data not found. Run from main project directory.$(NC)"; \
	fi

## Full workflow
all: clean install test build ## Clean, install, test, and build

.PHONY: help install install-deps clean test test-coverage test-watch test-cli test-commands test-integration build publish-test publish version-bump lint format type-check demo-scrape demo-convert demo-validate test-cli-live all
