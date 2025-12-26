#!/bin/bash
# Script to run DirectIA tests on Linux/macOS

set -e  # Exit on error

echo "DirectIA Test Suite"
echo "==================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest not found${NC}"
    echo "Install with: pip install pytest pytest-cov"
    exit 1
fi

# Parse arguments
RUN_TYPE="all"
VERBOSE=""
COVERAGE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            RUN_TYPE="unit"
            shift
            ;;
        --integration)
            RUN_TYPE="integration"
            shift
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        --cov|--coverage)
            COVERAGE="--cov=src --cov-report=html --cov-report=term"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--unit|--integration] [-v|--verbose] [--cov]"
            exit 1
            ;;
    esac
done

# Set test path
case $RUN_TYPE in
    unit)
        TEST_PATH="tests/unit/"
        echo -e "${YELLOW}Running unit tests...${NC}"
        ;;
    integration)
        TEST_PATH="tests/integration/"
        echo -e "${YELLOW}Running integration tests...${NC}"
        ;;
    *)
        TEST_PATH="tests/"
        echo -e "${YELLOW}Running all tests...${NC}"
        ;;
esac

# Run tests
pytest $TEST_PATH $VERBOSE $COVERAGE --color=yes --tb=short

# Check exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo ""
    echo -e "${RED}❌ Some tests failed${NC}"
fi

exit $EXIT_CODE
