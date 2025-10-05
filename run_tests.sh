#!/bin/bash
# Run test suite

echo "Running FusionMCP Test Suite..."

# Run pytest with coverage
pytest tests/ -v --tb=short

# Run linting (optional)
# ruff check mcp_server/
# black --check mcp_server/

echo "Tests complete!"
