.PHONY: help test smoke api-spec clean install dev api audit-tail
.PHONY: lint format fix fix-imports setup-hooks ci-local monitor test-cov deep-clean quick bootstrap

# Default target
help:
	@echo "LUKHAS PWM Build System"
	@echo "======================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install      - Install dependencies"
	@echo "  setup-hooks  - Setup pre-commit hooks"
	@echo "  bootstrap    - Full setup (install + hooks)"
	@echo ""
	@echo "Development:"
	@echo "  dev          - Run development server"
	@echo "  api          - Run API server"
	@echo "  audit-tail   - Tail audit logs"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         - Run all linters (no fixes)"
	@echo "  format       - Format code with Black"
	@echo "  fix          - Auto-fix all possible issues"
	@echo "  fix-imports  - Fix import issues specifically"
	@echo ""
	@echo "Testing:"
	@echo "  test         - Run test suite"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  smoke        - Run smoke check"
	@echo ""
	@echo "CI/CD:"
	@echo "  ci-local     - Run full CI pipeline locally"
	@echo "  monitor      - Generate code quality report"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        - Clean cache and temp files"
	@echo "  deep-clean   - Deep clean including venv"
	@echo "  api-spec     - Export OpenAPI specification"
	@echo ""
	@echo "Quick Commands:"
	@echo "  quick        - Fix issues and run tests"

# Installation
install:
	@echo "📦 Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-test.txt
	pip install black ruff isort mypy autoflake flake8 pre-commit bandit

# Setup pre-commit hooks
setup-hooks:
	@echo "🔗 Setting up pre-commit hooks..."
	pre-commit install
	pre-commit autoupdate
	@echo "✅ Pre-commit hooks installed!"

# Development server
dev:
	uvicorn serve.main:app --reload --host 0.0.0.0 --port 8000

# API server
api:
	uvicorn lukhas_pwm.api.app:app --reload --port 8000

# Export OpenAPI spec
openapi:
	@mkdir -p out
	curl -s http://127.0.0.1:8000/openapi.json -o out/openapi.json
	@echo "✅ OpenAPI exported to out/openapi.json"

# Live integration test
live:
	python scripts/live_integration_test.py

# Linting (no fixes)
lint:
	@echo "🔍 Running linters..."
	@echo "Running Flake8..."
	-flake8 . --count --statistics --max-line-length=79
	@echo "\nRunning Ruff..."
	-ruff check .
	@echo "\nRunning MyPy..."
	-mypy . --ignore-missing-imports
	@echo "\nRunning Bandit (security)..."
	-bandit -r lukhas_pwm bridge core serve -ll

# Format code
format:
	@echo "🎨 Formatting code with Black..."
	black --line-length 79 lukhas_pwm bridge core serve tests
	@echo "📦 Sorting imports with isort..."
	isort --profile black --line-length 79 lukhas_pwm bridge core serve tests

# Auto-fix all issues
fix:
	@echo "🔧 Auto-fixing all issues..."
	@echo "Removing unused imports..."
	autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive lukhas_pwm bridge core serve
	@echo "Sorting imports..."
	isort --profile black --line-length 79 lukhas_pwm bridge core serve tests
	@echo "Formatting with Black..."
	black --line-length 79 lukhas_pwm bridge core serve tests
	@echo "Fixing with Ruff..."
	ruff check --fix .
	@echo "✅ Auto-fix complete! Running final check..."
	@make lint

# Fix import issues specifically
fix-imports:
	@echo "📦 Fixing import issues..."
	autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive .
	isort --profile black --line-length 79 .

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=lukhas_pwm --cov=bridge --cov=core --cov=serve --cov-report=html --cov-report=term

# Smoke test
smoke:
	python3 smoke_check.py

# Run full CI pipeline locally
ci-local:
	@echo "🚀 Running full CI pipeline locally..."
	@echo "\n1️⃣ Installing dependencies..."
	@make install
	@echo "\n2️⃣ Running linters..."
	@make lint
	@echo "\n3️⃣ Running security checks..."
	bandit -r lukhas_pwm bridge core serve -ll
	@echo "\n4️⃣ Running tests..."
	@make test-cov
	@echo "\n✅ CI pipeline complete!"

# Generate code quality monitoring report
monitor:
	@echo "📊 Generating code quality report..."
	@python tools/scripts/auto_fix_linting.py

# API specification
api-spec:
	@echo "Starting server to export OpenAPI spec..."
	@mkdir -p out
	@curl -s http://127.0.0.1:8000/openapi.json -o out/openapi.json
	@echo "OpenAPI spec exported to out/openapi.json"

# Audit logs
audit-tail:
	@mkdir -p .lukhas_audit && touch .lukhas_audit/audit.jsonl
	tail -f .lukhas_audit/audit.jsonl

# Clean cache and temp files
clean:
	@echo "🧹 Cleaning cache and temp files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf out/
	@echo "✅ Clean complete!"

# Deep clean including virtual environment
deep-clean: clean
	@echo "🧹 Deep cleaning..."
	rm -rf venv .venv
	rm -rf htmlcov .coverage
	rm -rf dist build *.egg-info
	@echo "✅ Deep clean complete!"

# Quick fix and test
quick: fix test
	@echo "✅ Quick fix and test complete!"

# Install and setup everything
bootstrap: install setup-hooks
	@echo "🚀 Bootstrap complete! Run 'make fix' to clean up existing issues."
