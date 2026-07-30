# Marketplace Platform Makefile

.PHONY: install install-dev test test-cov test-setup lint format run clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  test-setup   - Verify project setup"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  run          - Run the API server"
	@echo "  clean        - Clean temporary files"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies (without PostgreSQL)
install-dev:
	pip install -r requirements-dev.txt

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=src --cov-report=html --cov-report=term-missing

# Verify project setup
test-setup:
	python test_setup.py

# Run linting
lint:
	flake8 src tests
	mypy src

# Format code
format:
	black src tests

# Run the API server
run:
	cd src/api && python main.py

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf *.egg-info
	rm -rf build
	rm -rf dist