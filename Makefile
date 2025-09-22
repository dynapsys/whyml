# Modular YAML Manifest System - Makefile
# Automation and build management for the YAML manifest system

# Load environment variables
#include .env
#export

# Default target
.DEFAULT_GOAL := help

# Variables
PROJECT_NAME := modular-yaml-manifest
DOCKER_IMAGE := $(PROJECT_NAME):latest
DOCKER_COMPOSE_FILE := docker-compose.yml

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m

## Help
help: ## Show this help message
	@echo "$(BLUE)Modular YAML Manifest System - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

dev: ## Start development server
	@echo "$(BLUE)Starting development server on port $(PORT)...$(NC)"
	npm run dev

start: ## Start production server
	@echo "$(BLUE)Starting production server...$(NC)"
	npm start

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	python3 -m pytest tests/ -v

lint: ## Run linting
	@echo "$(BLUE)Running linter...$(NC)"
	npm run lint

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	npm run format

## Docker Operations
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	./scripts/docker-build.sh

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	./scripts/docker-run.sh

docker-push: ## Push Docker image to registry
	@echo "$(BLUE)Pushing Docker image...$(NC)"
	./scripts/docker-push.sh

docker-clean: ## Clean Docker images and containers
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	./scripts/docker-clean.sh

## Docker Compose
compose-up: ## Start services with Docker Compose
	@echo "$(BLUE)Starting services with Docker Compose...$(NC)"
	docker-compose up -d

compose-down: ## Stop services with Docker Compose
	@echo "$(BLUE)Stopping services with Docker Compose...$(NC)"
	docker-compose down

compose-logs: ## View Docker Compose logs
	@echo "$(BLUE)Viewing Docker Compose logs...$(NC)"
	docker-compose logs -f

compose-restart: ## Restart services
	@echo "$(BLUE)Restarting services...$(NC)"
	docker-compose restart

## Manifest Operations
manifest-validate: ## Validate all manifests
	@echo "$(BLUE)Validating manifests...$(NC)"
	./scripts/validate-manifests.sh

manifest-convert: ## Convert manifests to all formats
	@echo "$(BLUE)Converting manifests...$(NC)"
	./scripts/convert-manifests.sh

manifest-bundle: ## Bundle manifests with modules
	@echo "$(BLUE)Bundling manifests...$(NC)"
	./scripts/bundle-manifests.sh

manifest-examples: ## Generate example manifests
	@echo "$(BLUE)Generating example manifests...$(NC)"
	./scripts/generate-examples.sh

## Examples and Integration
examples-python: ## Run Python integration examples
	@echo "$(BLUE)Running Python examples...$(NC)"
	./scripts/examples/python-integration.sh

examples-php: ## Run PHP integration examples
	@echo "$(BLUE)Running PHP examples...$(NC)"
	./scripts/examples/php-integration.sh

examples-docker: ## Run Docker rendering examples
	@echo "$(BLUE)Running Docker rendering examples...$(NC)"
	./scripts/examples/docker-rendering.sh

examples-all: ## Run all examples
	@echo "$(BLUE)Running all examples...$(NC)"
	make examples-python
	make examples-php
	make examples-docker

## Documentation
docs-generate: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	./scripts/generate-docs.sh

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	./scripts/serve-docs.sh

## Deployment
deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	./scripts/deploy-staging.sh

deploy-production: ## Deploy to production environment
	@echo "$(BLUE)Deploying to production...$(NC)"
	./scripts/deploy-production.sh

setup-tls: ## Setup TLS certificates for production
	@echo "$(BLUE)Setting up TLS certificates...$(NC)"
	./scripts/setup-tls.sh

## Utility Commands

backup: ## Backup manifests and configurations
	@echo "$(BLUE)Creating backup...$(NC)"
	./scripts/backup.sh

restore: ## Restore from backup
	@echo "$(BLUE)Restoring from backup...$(NC)"
	./scripts/restore.sh

health-check: ## Check system health
	@echo "$(BLUE)Checking system health...$(NC)"
	./scripts/health-check.sh

## Server Management
server-status: ## Check server status
	@echo "$(BLUE)Checking server status...$(NC)"
	curl -s http://localhost:$(PORT)/health || echo "$(RED)Server not running$(NC)"

server-restart: ## Restart server
	@echo "$(BLUE)Restarting server...$(NC)"
	./scripts/restart-server.sh

server-logs: ## View server logs
	@echo "$(BLUE)Viewing server logs...$(NC)"
	./scripts/view-logs.sh

## Performance and Monitoring
performance-test: ## Run performance tests
	@echo "$(BLUE)Running performance tests...$(NC)"
	./scripts/performance-test.sh

monitor: ## Start monitoring
	@echo "$(BLUE)Starting monitoring...$(NC)"
	./scripts/monitor.sh

benchmark: ## Run benchmarks
	@echo "$(BLUE)Running benchmarks...$(NC)"
	./scripts/benchmark.sh

## Quick Commands
quick-start: install dev ## Quick start development environment

full-setup: install docker-build compose-up examples-all ## Full setup with Docker and examples

reset: clean install ## Reset project to clean state

## CI/CD
ci-test: ## Run CI tests
	@echo "$(BLUE)Running CI tests...$(NC)"
	npm test
	make manifest-validate
	make lint

ci-build: ## Build for CI
	@echo "$(BLUE)Building for CI...$(NC)"
	make build
	make docker-build

# DEVELOPMENT SETUP

# Setup development environment
setup-dev:
	@bash scripts/setup-dev.sh

# Install package in development mode
install:
	@bash scripts/install.sh

# Install with all optional dependencies
install-all:
	@echo "📦 Installing EDPMT with all dependencies..."
	pip install -e .[all]
	@echo "✅ EDPMT with all dependencies installed"

# Development setup using PYTHONPATH (no installation required)
dev-setup:
	@echo "🛠️  Setting up EDPMT for development using PYTHONPATH..."
	@echo "📁 Project root: $$(pwd)"
	@echo "🐍 Python version: $$(python3 --version)"
	@echo "📝 Testing EDPMT import..."
	@PYTHONPATH="$$(pwd):$$PYTHONPATH" python3 -c "import edpmt; print(f'✅ EDPMT {edpmt.__version__} loaded via PYTHONPATH')" || { \
		echo "❌ EDPMT import failed"; \
		echo "💡 Make sure you're in the correct directory: $$(pwd)"; \
		exit 1; \
	}
	@echo "🎯 Creating CLI wrapper script..."
	@mkdir -p bin
	@echo '#!/bin/bash' > bin/edpmt
	@echo 'export PYTHONPATH="'"$$(pwd)"':$$PYTHONPATH"' >> bin/edpmt
	@echo 'python3 -m edpmt.cli "$$@"' >> bin/edpmt
	@chmod +x bin/edpmt
	@echo "✅ Development setup complete!"
	@echo "💡 To use EDPMT:"
	@echo "   1. Add to PATH: export PATH=$$(pwd)/bin:$$PATH"
	@echo "   2. Or use directly: ./bin/edpmt server --dev"
	@echo "   3. Or set PYTHONPATH: export PYTHONPATH=$$(pwd):$$PYTHONPATH"

# Create and setup virtual environment
venv-setup:
	@echo "🐍 Creating virtual environment..."
	@python3 -m venv venv --without-pip 2>/dev/null || python3 -m venv venv
	@echo "📦 Installing EDPMT in virtual environment..."
	@venv/bin/python -m ensurepip --upgrade 2>/dev/null || echo "pip already available"
	@venv/bin/pip install --upgrade pip setuptools || echo "⚠️  Pip upgrade failed, continuing..."
	@venv/bin/pip install -e . || { \
		echo "⚠️  Standard pip install failed, trying alternatives..."; \
		venv/bin/pip install -e . --user 2>/dev/null || \
		echo "❌ Virtual environment installation failed"; \
		echo "💡 Try manually: source venv/bin/activate && pip install -e ."; \
		exit 1; \
	}
	@echo "✅ Virtual environment setup complete!"
	@echo "💡 To activate: source venv/bin/activate"
	@echo "💡 Then run: edpmt server --dev"

# ==============================================================================
# DOCKER OPERATIONS
# ==============================================================================

# Build Docker containers
build-docker:
	@echo "🔨 Building EDPMT Docker containers..."
	docker-compose -f examples/docker/docker-compose.yml build
	@echo "✅ Build complete"

# ==============================================================================
# MONITORING
# ==============================================================================

# Show EDPMT server logs
logs-server:
	@tail -f logs/edpmt-server.log 2>/dev/null || echo "No server logs found"

# Monitor GPIO frontend
monitor-frontend:
	@tail -f logs/gpio-frontend.log 2>/dev/null || echo "No frontend logs found"


# Build and publish
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	#$(MAKE) clean

# Version management
bump-major:
	@echo "📈 Bumping major version (x.0.0)..."
	python3 pasvg/scripts/version_bumper.py major --file pyproject.toml

bump-minor:
	@echo "📈 Bumping minor version (x.y.0)..."
	python3 pasvg/scripts/version_bumper.py minor --file pyproject.toml

bump-patch:
	@echo "📈 Bumping patch version (x.y.z)..."
	python3 pasvg/scripts/version_bumper.py patch --file pyproject.toml

bump-version:
	@echo "📈 Bumping patch version automatically..."
	python3 pasvg/scripts/version_bumper.py patch --file pyproject.toml

build: clean
	@echo "🔧 Installing build tools..."
	pip install --upgrade build --break-system-packages
	@echo "📈 Bumping patch version..."
	python3 pasvg/scripts/version_bumper.py patch --file pyproject.toml
	@echo "🏗️  Building package..."
	python3 -m build

publish: build
	@echo "📤 Publishing to PyPI..."
	pip install --upgrade twine
	twine upload dist/*

publish-test: build
	@echo "🚀 Publishing to TestPyPI..."
	pip install --upgrade twine
	twine upload --repository testpypi dist/*


.PHONY: help install dev start test lint format build build-docker \
        docker-build docker-run docker-push docker-clean \
        compose-up compose-down compose-logs compose-restart \
        manifest-validate manifest-convert manifest-bundle manifest-examples \
        examples-python examples-php examples-docker examples-all \
        docs-generate docs-serve \
        deploy-staging deploy-production setup-tls \
        clean backup restore health-check \
        server-status server-restart server-logs \
        performance-test monitor benchmark \
        quick-start full-setup reset \
        ci-test ci-build
