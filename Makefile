.PHONY: help test smoke api-spec clean install dev api audit-tail audit
.PHONY: lint format fix fix-imports setup-hooks ci-local monitor test-cov deep-clean quick bootstrap
.PHONY: security security-scan security-update security-audit security-fix

# Default target
help:
	@echo "LUKHAS  Build System"
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
	@echo "  audit        - Run gold-standard audit suite"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        - Clean cache and temp files"
	@echo "  deep-clean   - Deep clean including venv"
	@echo "  api-spec     - Export OpenAPI specification"
	@echo ""
	@echo "Security:"
	@echo "  security     - Run full security check suite"
	@echo "  security-scan- Quick vulnerability scan"
	@echo "  security-update - Auto-update vulnerable packages"
	@echo "  security-audit - Deep security audit with reports"
	@echo "  security-fix - Fix all security issues (scan + update)"
	@echo ""
	@echo "Backup & DR:"
	@echo "  backup-local - Create local backup into .lukhas_backup/out"
	@echo "  backup-s3    - Create backup and upload to S3 (env required)"
	@echo "  restore-local- Verify and extract a backup locally"
	@echo "  restore-s3   - Verify and extract a backup from S3"
	@echo "  dr-drill     - Dry-run restore from last S3 manifest"
	@echo "  dr-weekly    - Trigger weekly DR dry-run workflow"
	@echo "  dr-quarterly - Trigger quarterly DR full-restore workflow"
	@echo "  dr-monthly   - Trigger monthly DR dry-run workflow"
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
	uvicorn lukhas.api.app:app --reload --port 8000

# Export OpenAPI spec
openapi:
	@mkdir -p out
	curl -s http://127.0.0.1:8000/openapi.json -o out/openapi.json
	@echo "✅ OpenAPI exported to out/openapi.json"

# Live integration test
live:
	python3 scripts/testing/live_integration_test.py

# Colony↔DNA demo
colony-dna-smoke:
	python3 scripts/colony_dna_smoke.py

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
	-bandit -r lukhas bridge core serve -ll

# Format code
format:
	@echo "🎨 Formatting code with Black..."
	black --line-length 79 lukhas bridge core serve tests
	@echo "📦 Sorting imports with isort..."
	isort --profile black --line-length 79 lukhas bridge core serve tests

# Auto-fix all issues (smart mode - won't break code)
fix:
	@echo "🔧 Running Smart Fix (safe mode)..."
	@python tools/scripts/smart_fix.py

# Aggressive fix (use with caution - will fix 90% of issues)
fix-all:
	@echo "🔥 Running Aggressive Fix..."
	@python tools/scripts/aggressive_fix.py

# Ultra fix - maximum aggression (last resort)
fix-ultra:
	@echo "☠️ ULTRA FIX MODE - This WILL change your code significantly!"
	@echo "Removing ALL unused code..."
	@autoflake --in-place --remove-unused-variables --remove-all-unused-imports --remove-duplicate-keys --recursive .
	@echo "Fixing ALL PEP8 issues..."
	@autopep8 --in-place --recursive --aggressive --aggressive --max-line-length 88 .
	@echo "Formatting everything..."
	@black --line-length 88 .
	@echo "Final Ruff pass..."
	@ruff check --fix --unsafe-fixes .
	@echo "✅ Ultra fix complete!"

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
	pytest tests/ --cov=lukhas --cov=bridge --cov=core --cov=serve --cov-report=html --cov-report=term

# Smoke test
smoke:
	python3 scripts/testing/smoke_check.py

# Run full CI pipeline locally
ci-local:
	pytest -q --maxfail=1 --disable-warnings --cov=lukhas --cov-report=term
	python3 scripts/testing/smoke_check.py --json out/smoke.json || true
	uvicorn lukhas.api.app:app --port 8000 & echo $$! > .pid; sleep 2; \
	curl -s http://127.0.0.1:8000/openapi.json -o out/openapi.json; \
	kill `cat .pid` || true; rm -f .pid
	@echo 'Artifacts in ./out'

# Generate code quality monitoring report
monitor:
	@echo "📊 Generating code quality report..."
	@python tools/scripts/quality_dashboard.py

# Performance smoke (k6)
perf:
	@mkdir -p out
	BASE_URL=$${BASE_URL:-http://127.0.0.1:8000} \
	SUMMARY_JSON=out/k6_summary.json \
	k6 run perf/k6_smoke.js

# DNA migration helpers
migrate-dry:
	python3 scripts/migrate_memory_to_dna.py --limit 50

migrate-run:
	python3 scripts/migrate_memory_to_dna.py

dna-health:
	curl -s http://127.0.0.1:8000/dna/health | jq

dna-compare:
	@if [ -z "$$KEY" ]; then echo "Usage: make dna-compare KEY=your_key"; exit 1; fi
	curl -s "http://127.0.0.1:8000/dna/compare?key=$$KEY" | jq

# Admin dashboard helper
admin:
	open http://127.0.0.1:8000/admin || true

# Check linting status
status:
	@python tools/scripts/check_progress.py

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

# File organization
organize:
	@echo "🧹 Organizing root directory..."
	@python3 scripts/file-organizer.py organize
	@echo "✅ Organization complete!"

organize-dry:
	@echo "🔍 Dry run - checking what would be organized..."
	@python3 scripts/file-organizer.py organize --dry-run

organize-suggest:
	@echo "💡 Suggesting new organization rules..."
	@python3 scripts/file-organizer.py suggest

organize-watch:
	@echo "👁️ Starting file organization watch mode..."
	@python3 scripts/file-organizer.py watch --interval 300

# Install and setup everything
bootstrap: install setup-hooks
	@echo "🚀 Bootstrap complete! Run 'make fix' to clean up existing issues."

# Security operations
security: security-audit security-scan
	@echo "✅ Full security check complete!"

security-scan:
	@echo "🔍 Running quick security scan..."
	@pip install -q safety pip-audit 2>/dev/null || true
	@echo "Checking with safety..."
	@safety check --short-report 2>/dev/null || echo "⚠️ Some vulnerabilities found"
	@echo "\nChecking with pip-audit..."
	@pip-audit --desc 2>/dev/null || echo "⚠️ Some vulnerabilities found"
	@echo "✅ Security scan complete!"

security-update:
	@echo "🔧 Running automated security updates..."
	@pip install -q safety pip-audit 2>/dev/null || true
	@python3 scripts/security-update.py --auto --no-test
	@echo "✅ Security updates complete!"

security-audit:
	@echo "🔒 Running deep security audit..."
	@pip install -q safety pip-audit bandit 2>/dev/null || true
	@mkdir -p security-reports
	@echo "Running safety check..."
	@safety check --json --output security-reports/safety-report.json 2>/dev/null || true
	@safety check --short-report || true
	@echo "\nRunning pip-audit..."
	@pip-audit --desc --format json --output security-reports/pip-audit.json 2>/dev/null || true
	@echo "\nRunning bandit..."
	@bandit -r . -f json -o security-reports/bandit-report.json 2>/dev/null || true
	@echo "\n📊 Security reports saved to security-reports/"
	@echo "✅ Security audit complete!"

security-fix: security-scan security-update test
	@echo "✅ Security issues fixed and tested!"

# Advanced security automation
security-autopilot:
	@echo "🚀 Running Security Autopilot..."
	@python3 scripts/security-autopilot.py fix

security-monitor:
	@echo "👁️ Starting continuous security monitoring..."
	@python3 scripts/security-autopilot.py monitor --continuous --interval 3600

security-status:
	@echo "📊 Security Status:"
	@python3 scripts/security-autopilot.py status

# SDK helpers
sdk-py-install:
	cd sdk/python && pip install -e .

sdk-py-test:
	cd sdk/python && pytest -q

sdk-ts-build:
	cd sdk/ts && npm i && npm run build

sdk-ts-test:
	cd sdk/ts && npm test

# Backup & DR helpers
backup-local:
	@mkdir -p .lukhas_backup/out
	@echo "Creating local backup..."
	@python3 scripts/backup_create.py --include lukhas data \
		--exclude "*.tmp" "*.log" \
		--outdir .lukhas_backup/out | tee .lukhas_backup/out/backup_create.out.json

backup-s3:
	@[ -n "$$BACKUP_S3_BUCKET" ] || (echo "BACKUP_S3_BUCKET is required" && exit 1)
	@mkdir -p .lukhas_backup/out
	@BACKUP_INCLUDE="lukhas data" BACKUP_PREFIX="s3" OUTDIR=".lukhas_backup/out" bash scripts/backup.sh

restore-local:
	@[ -n "$$MANIFEST" ] || (echo "Usage: make restore-local MANIFEST=path/to.manifest.json [TARGET=_restore]" && exit 1)
	@python3 scripts/restore.py --manifest "$$MANIFEST" $${TARBALL:+--tarball "$$TARBALL"} --target "$$TARGET"

restore-s3:
	@[ -n "$$MANIFEST" ] || (echo "Usage: make restore-s3 MANIFEST=s3://bucket/key.manifest.json [TARGET=_restore]" && exit 1)
	@python3 scripts/restore.py --manifest "$$MANIFEST" $${TARBALL:+--tarball "$$TARBALL"} --target "$$TARGET"

dr-drill:
	@if [ -n "$$MANIFEST" ]; then \
		python3 scripts/restore.py --manifest "$$MANIFEST" $${TARBALL:+--tarball "$$TARBALL"} --dry_run; \
	else \
		jq -re '.last_s3_manifest' .lukhas_backup/last_success.json >/dev/null || (echo "No last_success.json or missing last_s3_manifest" && exit 1); \
		python3 scripts/restore.py --manifest "$$(jq -r '.last_s3_manifest' .lukhas_backup/last_success.json)" --dry_run; \
	fi

dr-weekly:
	gh workflow run dr-dryrun-weekly.yml

dr-quarterly:
	gh workflow run dr-full-restore-quarterly.yml

dr-monthly:
	gh workflow run dr-dryrun-monthly.yml

# Gold Standard Audit
audit:
	@bash -lc './scripts/audit.sh'
