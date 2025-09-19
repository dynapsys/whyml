# PASVG - Project Artifact SVG Package
# Makefile for development, testing, and publishing

.PHONY: help install install-dev test lint format clean build publish example-test

# Default target
help:
	@echo "PASVG - Project Artifact SVG Package"
	@echo "======================================"
	@echo ""
	@echo "Available targets:"
	@echo "  install      - Install package in development mode"
	@echo "  install-dev  - Install package with development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting (flake8, mypy)"
	@echo "  format       - Format code (black, isort)"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build wheel and source distribution"
	@echo "  publish      - Publish package to PyPI"
	@echo "  example-test - Test package with example SVG files"
	@echo "  validate     - Validate PASVG files"

# Development setup
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Testing
test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=pasvg --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src/pasvg tests/
	mypy src/pasvg

format:
	black src/pasvg tests/
	isort src/pasvg tests/

format-check:
	black --check src/pasvg tests/
	isort --check-only src/pasvg tests/

# Build and publish
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	python -m twine upload dist/*

publish-test: build
	python -m twine upload --repository testpypi dist/*

# Example and validation
example-test:
	@echo "Testing PASVG package with example files..."
	pasvg generate examples/tutorial.md examples/output/
	pasvg extract examples/output/tutorial.pasvg.svg examples/extracted/
	pasvg validate examples/output/tutorial.pasvg.svg
	@echo "✅ Example test completed successfully!"

validate:
	@echo "Validating all PASVG files..."
	find examples/ -name "*.pasvg.svg" -exec pasvg validate {} \;

# Development workflow
dev-setup: install-dev
	@echo "🚀 PASVG development environment ready!"
	@echo "Run 'make example-test' to test the package"

# CI/CD targets
ci-test: install-dev lint test

ci-build: clean build

# Package info
info:
	@echo "Package: pasvg"
	@echo "Version: $(shell python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"
	@echo "Python: $(shell python --version)"
	@echo "Location: $(shell pwd)"
