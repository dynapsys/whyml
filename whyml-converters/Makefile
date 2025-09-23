# WhyML Converters - Makefile
# Multi-format code generation package for WhyML ecosystem

.DEFAULT_GOAL := help

# Variables
PACKAGE_NAME := whyml-converters
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
	@echo "$(BLUE)WhyML Converters Package - Available Commands$(NC)"
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

test-html: ## Test HTML converter specifically
	@echo "$(BLUE)Running HTML converter tests...$(NC)"
	$(PYTEST) tests/test_html_converter.py -v

test-react: ## Test React converter specifically
	@echo "$(BLUE)Running React converter tests...$(NC)"
	$(PYTEST) tests/test_react_converter.py -v

test-vue: ## Test Vue converter specifically
	@echo "$(BLUE)Running Vue converter tests...$(NC)"
	$(PYTEST) tests/test_vue_converter.py -v

test-php: ## Test PHP converter specifically
	@echo "$(BLUE)Running PHP converter tests...$(NC)"
	$(PYTEST) tests/test_php_converter.py -v

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
	flake8 whyml_converters/ tests/
	black --check whyml_converters/ tests/

format: ## Format code
	@echo "$(BLUE)Formatting code for $(PACKAGE_NAME)...$(NC)"
	black whyml_converters/ tests/
	isort whyml_converters/ tests/

type-check: ## Run type checking
	@echo "$(BLUE)Running type checking for $(PACKAGE_NAME)...$(NC)"
	mypy whyml_converters/

## Converter Testing
demo-html: ## Generate demo HTML output
	@echo "$(BLUE)Generating demo HTML output...$(NC)"
	$(PYTHON) -c "from whyml_converters import HTMLConverter; print('HTML converter demo ready')"

demo-react: ## Generate demo React output
	@echo "$(BLUE)Generating demo React output...$(NC)"
	$(PYTHON) -c "from whyml_converters import ReactConverter; print('React converter demo ready')"

demo-vue: ## Generate demo Vue output
	@echo "$(BLUE)Generating demo Vue output...$(NC)"
	$(PYTHON) -c "from whyml_converters import VueConverter; print('Vue converter demo ready')"

demo-php: ## Generate demo PHP output
	@echo "$(BLUE)Generating demo PHP output...$(NC)"
	$(PYTHON) -c "from whyml_converters import PHPConverter; print('PHP converter demo ready')"

## Full workflow
all: clean install test build ## Clean, install, test, and build

.PHONY: help install install-deps clean test test-coverage test-watch test-html test-react test-vue test-php build publish-test publish version-bump lint format type-check demo-html demo-react demo-vue demo-php all
