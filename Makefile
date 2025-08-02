.PHONY: test test-unit test-integration test-slow test-all test-quick test-no-llm test-coverage clean help agents agents-start agents-stop agents-status agents-restart typecheck build docs install-dev ci-setup ci-deps ci-security docs-serve

# Python executable - detect if we're in CI or local dev
PYTHON := $(shell if [ -f .venv/bin/python ]; then echo ".venv/bin/python"; else echo "python"; fi)

# Default target
help:
	@echo "Available test targets:"
	@echo "  make test          - Run unit tests (default)"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-slow     - Run slow tests"
	@echo "  make test-all      - Run all tests"
	@echo "  make test-quick    - Run quick smoke tests (unit without slow)"
	@echo "  make test-no-llm   - Run all tests except LLM tests"
	@echo "  make test-coverage - Run tests with coverage report"
	@echo ""
	@echo "A2A Agent targets:"
	@echo "  make agents-start  - Start all A2A agent servers"
	@echo "  make agents-stop   - Stop all A2A agent servers" 
	@echo "  make agents-status - Check status of A2A agent servers"
	@echo "  make agents-restart- Restart all A2A agent servers"
	@echo ""
	@echo "Other targets:"
	@echo "  make clean         - Remove cache and temporary files"
	@echo "  make format        - Format code with black"
	@echo "  make lint          - Run linting checks"
	@echo "  make typecheck     - Run type checking with mypy"
	@echo "  make build         - Build Python package"
	@echo "  make docs          - Build documentation"
	@echo "  make docs-serve    - Serve documentation locally"
	@echo "  make install-dev   - Install development dependencies"
	@echo ""
	@echo "CI targets:"
	@echo "  make ci-setup      - Setup CI environment"
	@echo "  make ci-deps       - Install CI dependencies with constraints"
	@echo "  make ci-security   - Run security scans"

# Default test target
test: test-unit

# Test targets
test-unit:
	$(PYTHON) -m pytest -m "unit" -v --tb=short

test-integration:
	$(PYTHON) -m pytest -m "integration" -v --tb=short

test-slow:
	$(PYTHON) -m pytest -m "slow" -v --tb=short

test-all:
	$(PYTHON) -m pytest -v --tb=short

test-quick:
	$(PYTHON) -m pytest -m "unit and not slow" -v --tb=short

test-no-llm:
	$(PYTHON) -m pytest -m "not llm" -v --tb=short

test-coverage:
	$(PYTHON) -m pytest --cov=polyhegel --cov-report=html --cov-report=term -v

# Utility targets
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +

format:
	$(PYTHON) -m black polyhegel tests

lint:
	$(PYTHON) -m ruff check polyhegel tests
	$(PYTHON) -m black --check polyhegel tests

typecheck:
	@echo "🔍 Running type checking with mypy..."
	$(PYTHON) -m mypy polyhegel --config-file mypy.ini
	@echo "✅ Type check passed"

build:
	$(PYTHON) -m build

docs:
	@echo "📚 Building documentation..."
	$(PYTHON) -m mkdocs build

install-dev:
	$(PYTHON) -m pip install -e .[dev]

# CI-specific targets
ci-setup:
	@echo "🔧 Setting up CI environment..."
	$(PYTHON) -m pip install --upgrade pip

ci-deps:
	@echo "📦 Installing dependencies with constraints..."
	pip install --constraint constraints.txt "numpy<2.0"
	pip install --constraint constraints.txt --no-binary scikit-learn-extra "scikit-learn-extra"
	pip install --constraint constraints.txt -e .[dev]

ci-security:
	@echo "🔍 Running security scans..."
	pip install safety bandit pip-audit
	pip-audit --format=json --output=audit-results.json || echo "⚠️  pip-audit found issues"
	bandit -r polyhegel -f json -o bandit-results.json || echo "⚠️  bandit found issues"  
	safety check --json --output safety-results.json || echo "⚠️  safety found issues"

docs-serve:
	@echo "📚 Serving documentation locally..."
	$(PYTHON) -m mkdocs serve

# A2A Agent management
agents-start:
	@echo "🚀 Starting Polyhegel A2A Agent Ecosystem..."
	./scripts/run-all-agents.sh start

agents-stop:  
	@echo "🛑 Stopping Polyhegel A2A Agent Ecosystem..."
	./scripts/run-all-agents.sh stop

agents-status:
	@echo "📊 Checking Polyhegel A2A Agent Status..."
	./scripts/run-all-agents.sh status

agents-restart:
	@echo "🔄 Restarting Polyhegel A2A Agent Ecosystem..."
	./scripts/run-all-agents.sh restart

# Convenience aliases
agents: agents-start