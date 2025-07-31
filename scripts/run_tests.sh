#!/bin/bash
# Script to run different categories of tests

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default to running unit tests
TEST_TYPE="${1:-unit}"

echo -e "${GREEN}Running $TEST_TYPE tests...${NC}"

case $TEST_TYPE in
    "unit")
        echo "Running fast unit tests only..."
        pytest -m "unit" -v --tb=short
        ;;
    "integration")
        echo "Running integration tests..."
        pytest -m "integration" -v --tb=short
        ;;
    "slow")
        echo "Running slow tests (this may take a while)..."
        pytest -m "slow" -v --tb=short
        ;;
    "all")
        echo "Running all tests..."
        pytest -v --tb=short
        ;;
    "quick")
        echo "Running quick smoke tests (unit tests excluding slow ones)..."
        pytest -m "unit and not slow" -v --tb=short
        ;;
    "not-llm")
        echo "Running all tests except LLM tests..."
        pytest -m "not llm" -v --tb=short
        ;;
    "coverage")
        echo "Running tests with coverage..."
        pytest --cov=polyhegel --cov-report=html --cov-report=term -v
        ;;
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo "Available options:"
        echo "  unit        - Run unit tests only (default)"
        echo "  integration - Run integration tests"
        echo "  slow        - Run slow tests"
        echo "  all         - Run all tests"
        echo "  quick       - Run quick smoke tests"
        echo "  not-llm     - Run all tests except LLM tests"
        echo "  coverage    - Run with coverage report"
        exit 1
        ;;
esac

echo -e "${GREEN}Tests completed!${NC}"