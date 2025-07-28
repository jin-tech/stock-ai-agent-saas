#!/bin/bash
"""
E2E Backend Test Runner

This script runs the comprehensive E2E test suite for the backend API.
It can be used in CI/CD pipelines or for local development testing.
"""

set -e  # Exit on any error

echo "========================================="
echo "Stock AI Agent SaaS - Backend E2E Tests"
echo "========================================="

# Change to backend directory
cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up test environment...${NC}"

# Check if pytest is installed
if ! python -m pytest --version > /dev/null 2>&1; then
    echo -e "${YELLOW}Installing pytest...${NC}"
    pip install pytest pytest-asyncio
fi

echo -e "${YELLOW}Running E2E Backend Tests...${NC}"

# Run the comprehensive E2E test suite
if python -m pytest test_e2e_backend.py -v --tb=short --color=yes; then
    echo -e "${GREEN}✅ All E2E tests passed successfully!${NC}"
    echo ""
    echo "Test Coverage:"
    echo "- ✅ Health endpoints and API documentation"
    echo "- ✅ Alert creation with validation"
    echo "- ✅ Alert retrieval with filtering and pagination"
    echo "- ✅ Alert updates (full and partial)"
    echo "- ✅ Alert deletion"
    echo "- ✅ Error handling and edge cases"
    echo "- ✅ Complete workflow testing"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some E2E tests failed!${NC}"
    exit 1
fi