.PHONY: test test-unit test-integration test-slow test-all test-quick test-no-llm test-coverage clean help

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
	@echo "Other targets:"
	@echo "  make clean         - Remove cache and temporary files"
	@echo "  make format        - Format code with black"
	@echo "  make lint          - Run linting checks"

# Default test target
test: test-unit

# Test targets
test-unit:
	source .venv/bin/activate && pytest -m "unit" -v --tb=short

test-integration:
	source .venv/bin/activate && pytest -m "integration" -v --tb=short

test-slow:
	source .venv/bin/activate && pytest -m "slow" -v --tb=short

test-all:
	source .venv/bin/activate && pytest -v --tb=short

test-quick:
	source .venv/bin/activate && pytest -m "unit and not slow" -v --tb=short

test-no-llm:
	source .venv/bin/activate && pytest -m "not llm" -v --tb=short

test-coverage:
	source .venv/bin/activate && pytest --cov=polyhegel --cov-report=html --cov-report=term -v

# Utility targets
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +

format:
	source .venv/bin/activate && black polyhegel tests

lint:
	source .venv/bin/activate && ruff check polyhegel tests
	source .venv/bin/activate && mypy polyhegel --ignore-missing-imports