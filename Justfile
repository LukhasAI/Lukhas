default: test

# Test commands
test:
	.venv/bin/pytest -m "unit and not slow" -q

it:
	.venv/bin/pytest -m "integration" -q

contracts:
	.venv/bin/pytest -m "contract" -q

e2e:
	.venv/bin/pytest -m "e2e" -q

cov:
	.venv/bin/pytest --cov=lukhas --cov=candidate --cov-report=term-missing

# Documentation commands  
docs:
	.venv/bin/mkdocs serve -a 0.0.0.0:8000

build-docs:
	.venv/bin/mkdocs build --strict

# Development commands
format:
	.venv/bin/black lukhas/ candidate/ tests_new/
	.venv/bin/ruff check --fix lukhas/ candidate/ tests_new/

lint:
	.venv/bin/ruff check lukhas/ candidate/ tests_new/
	.venv/bin/mypy lukhas/

# Quick development cycle
quick: format test

# Full validation
validate: format lint test build-docs

# Setup commands
install:
	pip install -r requirements.txt
	pip install -r requirements-test.txt
	pip install mkdocs mkdocs-material 'mkdocstrings[python]'

# Clean commands
clean:
	rm -rf .pytest_cache/ __pycache__/ *.pyc
	rm -rf site/ site_test/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete