# LUKHAS Innovation Research Package - Makefile

.PHONY: help install test test-quick test-full analyze clean docker-build docker-run validate

help:
	@echo "LUKHAS Innovation Research Package"
	@echo "=================================="
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test        - Run quick baseline tests"
	@echo "  make test-full   - Run comprehensive test suite"
	@echo "  make analyze     - Run analysis on test results"
	@echo "  make validate    - Validate package integrity"
	@echo "  make docker-build - Build Docker container"
	@echo "  make docker-run  - Run tests in Docker"
	@echo "  make clean       - Clean generated files"

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	cp -n .env.example .env || true

test: test-quick

test-quick:
	@echo "Running quick baseline tests..."
	python -m pytest tests/test_innovation_quick_baseline.py -v

test-full:
	@echo "Running full test suite..."
	python -m pytest tests/ -v --cov=src --cov-report=html

analyze:
	@echo "Analyzing test results..."
	python src/analyze_pass_rate_factors.py
	@echo "Results saved to test_results/"

validate:
	@echo "Validating research package..."
	python validate_package.py

docker-build:
	docker build -t lukhas/research:latest .

docker-run:
	docker run --rm -v $(PWD)/test_results:/app/test_results \
		--env-file .env lukhas/research:latest

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -rf test_results/*.json visualizations/*.png
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Development helpers
format:
	black src/ tests/
	flake8 src/ tests/

typecheck:
	mypy src/ tests/

# Research package specific
package:
	@echo "Creating distributable research package..."
	tar -czf LUKHAS_Research_Package_$(shell date +%Y%m%d_%H%M%S).tar.gz \
		--exclude='__pycache__' \
		--exclude='.git' \
		--exclude='*.pyc' \
		.