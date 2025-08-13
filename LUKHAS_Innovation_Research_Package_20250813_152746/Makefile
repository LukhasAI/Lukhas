# LUKHAS Innovation System Makefile
# Provides convenient commands for setup, testing, and analysis

.PHONY: help setup test quick-test full-test analyze clean docker run-all

# Default target
help:
	@echo "LUKHAS Innovation System - Available Commands:"
	@echo "=============================================="
	@echo "  make setup        - Install dependencies and configure environment"
	@echo "  make test         - Run quick baseline tests (7 scenarios)"
	@echo "  make full-test    - Run comprehensive tests (60 scenarios)"
	@echo "  make analyze      - Analyze test results and generate reports"
	@echo "  make clean        - Clean up generated files and caches"
	@echo "  make docker       - Build and run in Docker container"
	@echo "  make run-all      - Complete setup, test, and analysis pipeline"
	@echo ""
	@echo "Environment Setup:"
	@echo "  1. Copy .env.example to .env"
	@echo "  2. Add your OpenAI API key"
	@echo "  3. Run 'make setup'"

# Setup environment
setup:
	@echo "Setting up LUKHAS Innovation System..."
	python3 -m pip install --upgrade pip
	pip3 install -r requirements.txt
	@if [ ! -f .env ]; then \
		echo "Creating .env from template..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env and add your API keys"; \
	fi
	@echo "Creating directory structure..."
	mkdir -p logs test_results data research_data visualizations
	@echo "✅ Setup complete!"

# Run quick baseline tests
test: quick-test

quick-test:
	@echo "Running quick baseline tests (7 scenarios)..."
	python3 src/test_innovation_quick_baseline.py
	@echo "✅ Quick tests complete!"

# Run full comprehensive tests
full-test:
	@echo "⚠️  Running comprehensive tests (60 scenarios)"
	@echo "This will take approximately 10-15 minutes with API calls..."
	python3 src/test_innovation_research_baseline.py
	@echo "✅ Comprehensive tests complete!"

# Analyze results
analyze:
	@echo "Analyzing test results..."
	python3 src/analyze_pass_rate_factors.py
	@echo "Generating visualizations..."
	python3 src/generate_visualizations.py 2>/dev/null || echo "Visualization script not found"
	@echo "✅ Analysis complete! Check test_results/ directory"

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info
	rm -rf build dist
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✅ Cleanup complete!"

# Docker support
docker:
	@echo "Building Docker container..."
	docker build -t lukhas-innovation:latest .
	@echo "Running tests in container..."
	docker run --env-file .env lukhas-innovation:latest

# Run complete pipeline
run-all: setup test analyze
	@echo "=============================================="
	@echo "✅ Complete pipeline executed successfully!"
	@echo "Results available in test_results/"
	@echo "=============================================="

# Install for development
dev-install:
	pip3 install -e ".[dev]"
	pre-commit install 2>/dev/null || echo "pre-commit not configured"

# Run linting
lint:
	ruff check src/
	black --check src/
	mypy src/ --ignore-missing-imports

# Format code
format:
	black src/
	ruff check --fix src/

# Run with specific API key
test-with-key:
	@read -p "Enter OpenAI API Key: " api_key; \
	OPENAI_API_KEY=$$api_key python3 src/test_innovation_quick_baseline.py

# Generate research report
report:
	@echo "Generating research report..."
	python3 src/generate_report.py
	@echo "Report generated in test_results/RESEARCH_REPORT.pdf"

# Run in verbose mode
verbose-test:
	LOG_LEVEL=DEBUG python3 src/test_innovation_quick_baseline.py

# Performance benchmark
benchmark:
	@echo "Running performance benchmark..."
	time python3 src/test_innovation_quick_baseline.py
	@echo "Benchmark complete!"

# Check system readiness
check:
	@echo "Checking system readiness..."
	@python3 -c "import openai; print('✅ OpenAI library installed')" 2>/dev/null || echo "❌ OpenAI library missing"
	@python3 -c "import numpy; print('✅ NumPy installed')" 2>/dev/null || echo "❌ NumPy missing"
	@python3 -c "import dotenv; print('✅ python-dotenv installed')" 2>/dev/null || echo "❌ python-dotenv missing"
	@test -f .env && echo "✅ .env file exists" || echo "❌ .env file missing"
	@grep -q "OPENAI_API_KEY=" .env 2>/dev/null && echo "✅ API key configured" || echo "⚠️  API key not configured"