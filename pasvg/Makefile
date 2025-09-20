# PASVG - Project Artifact SVG Package
# Makefile for development, testing, and publishing

.PHONY: help install install-dev test lint format format-check bump-major bump-minor bump-patch clean build publish publish-test example-test validate

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
	@echo "  bump-major   - Bump major version (x.0.0)"
	@echo "  bump-minor   - Bump minor version (x.y.0)"
	@echo "  bump-patch   - Bump patch version (x.y.z)"
	@echo "  example-test - Test package with example SVG files"
	@echo "  validate     - Validate PASVG files"

# Development setup
install:
	@echo "🚀 Setting up development environment..."
	@if [ -d "venv" ]; then \
		echo "♻️  Removing existing virtual environment..."; \
		rm -rf venv; \
	fi
	@echo "🛠️  Creating new virtual environment..."
	python3 -m venv venv
	@echo "🔄 Upgrading pip..."
	venv/bin/pip install --upgrade pip
	@echo "📦 Installing package in development mode..."
	venv/bin/pip install -e .
	@echo "✅ Development environment ready!"
	@echo "   Run 'source venv/bin/activate' to activate the virtual environment"
	@echo "🧪 Verifying installation..."
	@if venv/bin/python -c "import pasvg" &>/dev/null; then \
		echo "✅ PASVG package is properly installed"; \
	else \
		echo "❌ PASVG package could not be imported"; \
		echo "💡 Try running: source venv/bin/activate && pip install -e ."; \
		exit 1; \
	fi

install-dev: install
	@echo "📦 Installing development dependencies..."
	venv/bin/pip install -e ".[dev]"
	@echo "✅ Development dependencies installed!"

# Testing
test:
	PYTHONPATH=src pytest tests/ -v

test-coverage:
	PYTHONPATH=src pytest tests/ --cov=pasvg --cov-report=html --cov-report=term

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
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Version management
bump-major:
	@echo "📈 Bumping major version (x.0.0)..."
	python3 scripts/version_bumper.py major

bump-minor:
	@echo "📈 Bumping minor version (x.y.0)..."
	python3 scripts/version_bumper.py minor

bump-patch:
	@echo "📈 Bumping patch version (x.y.z)..."
	python3 scripts/version_bumper.py patch

bump-version:
	@echo "📈 Bumping patch version automatically..."
	python3 scripts/version_bumper.py patch

build: clean bump-version
	@echo "🔧 Installing build tools..."
	pip install --upgrade build
	@echo "🏗️  Building package..."
	python -m build

publish: build
	@echo "📤 Publishing to PyPI..."
	pip install --upgrade twine
	twine upload dist/*

publish-test: build
	@echo "🚀 Publishing to TestPyPI..."
	pip install --upgrade twine
	twine upload --repository testpypi dist/*

# Example and validation
example-test:
	@echo "Testing PASVG package with example files..."
	PYTHONPATH=src /usr/bin/python3 -m pasvg.cli generate examples/tutorial.md examples/output/
	# Rename the generated PASVG file (which may have a dynamic name) to a fixed name for extraction
	mv examples/output/*.pasvg.svg examples/output/tutorial.pasvg.svg || true
	PYTHONPATH=src /usr/bin/python3 -m pasvg.cli extract examples/output/tutorial.pasvg.svg examples/extracted/
	PYTHONPATH=src /usr/bin/python3 -m pasvg.cli validate examples/output/tutorial.pasvg.svg
	@echo "✅ Example test completed successfully!"

.PHONY: validate
validate:
	@echo "Validating all PASVG files..."
	@if [ -d "examples" ]; then \
		for file in $$(find examples -name "*.pasvg.svg"); do \
			echo "Validating $$file..."; \
			PYTHONPATH=src venv/bin/python -m pasvg.cli validate "$$file" || exit 1; \
		done; \
	else \
		echo "⚠️  No examples directory found"; \
	fi
	@echo "✅ Validation completed!"

# Development workflow
dev-setup: install-dev
	@echo "🚀 PASVG development environment ready!"
	@echo "Run 'make example-test' to test the package"

# CI/CD targets
ci-test: install-dev lint
	PYTHONPATH=src pytest tests/ -v

ci-build: clean build

# Package info
info:
	@echo "Package: pasvg"
	@echo "Version: $(shell python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"
	@echo "Python: $(shell python --version)"
	@echo "Location: $(shell pwd)"
