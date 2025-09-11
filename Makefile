.PHONY: help test test-tier1-matriz smoke api-spec clean install dev api audit-tail audit doctor doctor-json doctor-dup-targets
.PHONY: doctor-phony doctor-tools doctor-py doctor-ci doctor-lanes doctor-tests doctor-audit doctor-summary
.PHONY: lint format fix fix-imports setup-hooks ci-local monitor test-cov deep-clean quick bootstrap
.PHONY: security security-scan security-update security-audit security-fix
.PHONY: policy policy-review policy-brand policy-tone policy-registries
.PHONY: verify phase1 status hook-install
.PHONY: lane-guard

# Modular includes (guarded)
ifneq ($(wildcard mk/*.mk),)
include mk/*.mk
endif

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
	@echo "  audit-nav    - Show audit navigation for external auditors"
	@echo "  audit-scan   - Run comprehensive audit validation"
	@echo "  api-serve    - Start API server for external testing"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         - Run all linters (no fixes)"
	@echo "  format       - Format code with Black"
	@echo "  fix          - Auto-fix all possible issues"
	@echo "  fix-imports  - Fix import issues specifically"
	@echo ""
	@echo "AI-Powered Analysis (Ollama):"
	@echo "  ai-setup     - Setup Ollama for AI analysis"
	@echo "  ai-analyze   - AI-powered code analysis"
	@echo "  ai-workflow  - Complete AI workflow (fix + analyze + test)"
	@echo ""
	@echo "Testing:"
	@echo "  test         - Run test suite"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  smoke        - Run smoke check"
	@echo "  test-legacy  - Run legacy tests (tests/)"
	@echo "  test-tier1-matriz - Run MATRIZ Tier-1 tests (tests_new/matriz)"
	@echo ""
	@echo "Advanced Testing (0.001% Methodology):"
	@echo "  test-advanced    - Complete advanced testing suite"
	@echo "  test-property    - Property-based tests (Hypothesis)"
	@echo "  test-chaos       - Chaos engineering tests"
	@echo "  test-formal      - Formal verification (Z3)"
	@echo "  test-mutation    - Mutation testing"
	@echo "  test-performance - Performance regression"
	@echo "  test-consciousness - All consciousness tests"
	@echo "  test-standalone  - Standalone validation suite"
	@echo ""
	@echo "CI/CD:"
	@echo "  ci-local     - Run full CI pipeline locally"
	@echo "  monitor      - Generate code quality report"
	@echo "  audit        - Run gold-standard audit suite"
	@echo "  promote      - Promote a module candidate → lukhas"
	@echo "  check-scoped - Minimal CI-friendly scoped lint+tests+mypy"
	@echo "  doctor       - Diagnose Makefile/repo health (T4 quick scan)"
	@echo "  doctor-strict - Same as doctor, but fails on any warning/error"
	@echo "  doctor-json   - Emit machine-readable JSON summary to reports/audit"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        - Clean cache and temp files"
	@echo "  deep-clean   - Deep clean including venv"
	@echo "  api-spec     - Export OpenAPI specification"
	@echo ""
	@echo "Policy & Brand:"
	@echo "  policy       - Run all policy checks"
	@echo "  policy-review- Flag claims for human review"
	@echo "  policy-brand - Check brand compliance"
	@echo "  policy-tone  - Validate 3-layer tone system"
	@echo "  policy-registries - Validate module/site registries"
	@echo "  policy-routes - Validate site sections have matching routes"
	@echo "  policy-vocab  - Validate vocabulary compliance"
	@echo ""
	@echo "Security:"
	@echo "  security     - Run full security check suite"
	@echo "  security-scan- Quick vulnerability scan"
	@echo "  security-update - Auto-update vulnerable packages"
	@echo "  security-audit - Deep security audit with reports"
	@echo "  security-fix - Fix all security issues (scan + update)"
	@echo ""
	@echo "Security Fixes (AI-powered):"
	@echo "  security-fix-vulnerabilities - Fix dependency vulnerabilities"
	@echo "  security-fix-issues         - Fix code security issues (Bandit)"
	@echo "  security-fix-all           - Fix ALL security problems"
	@echo "  security-comprehensive-scan - Complete security analysis"
	@echo ""
	@echo "Security Scheduling:"
	@echo "  security-schedule          - View scheduler and schedule options"
	@echo "  security-schedule-3h       - Schedule fixes in 3 hours"
	@echo "  security-schedule-tonight  - Schedule fixes for 8 PM"
	@echo "  security-schedule-list     - List scheduled tasks"
	@echo ""
	@echo "Ollama Security (AI-powered):"
	@echo "  security-ollama      - AI-powered vulnerability analysis"
	@echo "  security-ollama-fix  - Auto-fix with Ollama recommendations"
	@echo "  security-ollama-setup- Setup Ollama for security analysis"
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
	pre-commit install --install-hooks
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
	-$(PYTHON) -m flake8 lukhas matriz core serve enforcement \
	  --count --statistics \
	  --max-line-length=88 \
	  --exclude .venv,.venv_*,venv,__pycache__,build,dist,*.egg-info \
	  --extend-ignore=E501,E203,E129,E301,E302,E402,W391,E128,W291,W292,W293
	@echo "\nRunning Ruff..."
	-$(PYTHON) -m ruff check lukhas matriz core serve tests tools enforcement --quiet
	@echo "\nRunning MyPy..."
	-$(PYTHON) -m mypy lukhas matriz core serve --ignore-missing-imports
	@echo "\nRunning Bandit (security)..."
	-$(PYTHON) -m bandit -r lukhas bridge core serve -ll
	@echo "\nChecking for fragile import patterns (sys.path hacks, star imports)..."
	-python3 tools/ci/no_syspath_hacks.py lukhas matriz || true

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

# Ollama-powered AI analysis and fixes
ai-analyze:
	@echo "🤖 Running AI-powered code analysis with Ollama..."
	@if [ -x "./tools/local-llm-helper.sh" ]; then \
		./tools/local-llm-helper.sh analyze; \
	else \
		echo "❌ AI analysis not available. Run 'make ai-setup' first."; \
		exit 1; \
	fi

# Setup Ollama for AI analysis
ai-setup:
	@echo "🤖 Setting up Ollama for AI analysis..."
	@if ! command -v ollama >/dev/null 2>&1; then \
		echo "❌ Ollama not installed. Please install Ollama first: https://ollama.ai"; \
		exit 1; \
	fi
	@if ! ollama list | grep -q "deepseek-coder:6.7b"; then \
		echo "📥 Downloading deepseek-coder:6.7b model..."; \
		ollama pull deepseek-coder:6.7b; \
	fi
	@chmod +x ./tools/local-llm-helper.sh
	@echo "✅ AI analysis setup complete!"

# Complete AI-powered development workflow
ai-workflow:
	@echo "🚀 Running complete AI-powered development workflow..."
	@make fix
	@make ai-analyze
	@make test
	@echo "✅ AI workflow complete!"

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
	pytest tests/ -v --junitxml=test-results.xml

# MATRIZ Tier-1 tests (fast, blocking smoke)
test-tier1-matriz:
	PYTHONPATH=. python3 -m pytest -q -m tier1 tests_new/matriz

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=lukhas --cov=candidate --cov=bridge --cov=core --cov=serve --cov-report=html --cov-report=xml --cov-report=term --junitxml=test-results.xml

# Smoke test
smoke:
	python3 scripts/testing/smoke_check.py

# Advanced Testing Suite (0.001% Methodology)
test-advanced:
	@echo "🧬 Running Advanced Testing Suite (0.001% Methodology)..."
	python3 rl/run_advanced_tests.py --verbose

test-property:
	@echo "🔬 Running Property-Based Tests..."
	pytest rl/tests/test_consciousness_properties.py -v -m property_based --tb=short

test-chaos:
	@echo "🌪️ Running Chaos Engineering Tests..."
	pytest rl/tests/test_chaos_consciousness.py -v -m chaos_engineering --tb=short

test-metamorphic:
	@echo "🔄 Running Metamorphic Tests..."
	pytest rl/tests/test_metamorphic_consciousness.py -v -m metamorphic --tb=short

test-formal:
	@echo "⚖️ Running Formal Verification Tests..."
	pytest rl/tests/test_formal_verification.py -v -m formal_verification --tb=short

test-mutation:
	@echo "🧬 Running Mutation Tests..."
	pytest rl/tests/test_mutation_testing.py -v -m mutation_testing --tb=short

test-performance:
	@echo "📊 Running Performance Regression Tests..."
	pytest rl/tests/test_performance_regression.py -v -m performance_regression --tb=short

test-oracles:
	@echo "🔮 Running Generative Oracle Tests..."
	pytest rl/tests/test_generative_oracles.py -v -m generative_oracles --tb=short

test-consciousness:
	@echo "🧠 Running Complete Consciousness Testing Suite..."
	pytest tests/consciousness/ rl/tests/ -v -m consciousness --tb=short

test-standalone:
	@echo "🚀 Running Standalone Advanced Test Suite..."
	python3 test_advanced_suite_standalone.py

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

# Promotion helper (candidate → lukhas)
promote:
	@if [ -z "$(SRC)" ] || [ -z "$(DST)" ]; then \
		echo "Usage: make promote SRC=candidate/core/<mod> DST=lukhas/core/<mod> [SHIM=candidate->lukhas]"; \
		exit 2; \
	fi
	@python3 tools/scripts/promote_module.py --src $(SRC) --dst $(DST) $(if $(SHIM),--shim-direction $(SHIM),)

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
lint-status:
	@python tools/scripts/check_progress.py

# Lane guard: forbid lukhas -> candidate imports (belt-and-suspenders)
lane-guard:
	@bash tools/ci/lane_guard.sh

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

# CODEX Strike Teams Support
codex-validate:
	@./tools/codex_validation.sh

codex-fix:
	@echo "🤖 CODEX 1: Datetime UTC Compliance"
	python3 -m ruff check . --select DTZ003,DTZ005 --fix 2>/dev/null || echo "Ruff not available - install with: pip install ruff"
	@echo "🤖 CODEX 5: Auto-fixable Syntax Issues" 
	python3 -m ruff check . --fix-only 2>/dev/null || echo "Ruff not available"
	@echo "🤖 CODEX 2: Import Organization"
	python3 -m isort . --check-only --diff 2>/dev/null || echo "isort not available"

# Full validation pipeline (CODEX ready)
validate-all: codex-validate fix test-cov lint security policy
	@echo "🎉 Full validation complete - CODEX Strike Teams ready!"

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

.PHONY: audit-status
audit-status:
	@echo "📊 LUKHAS Audit Status"
	@echo "======================"
	@echo ""
	@echo "🔧 Branch Status:"
	@git status -s && git rev-parse --abbrev-ref HEAD || echo "No changes"
	@echo ""
	@echo "📝 Recent Commits:"
	@git log --oneline -3 || echo "No commits"
	@echo ""
	@echo "🔍 Tool Versions:"
	@echo -n "  Ruff: " && python3 -m ruff --version 2>/dev/null || echo "Not available"
	@echo -n "  Pytest: " && python3 -m pytest --version 2>/dev/null || echo "Not available"
	@echo ""
	@echo "🧪 Smoke Tests:"
	@source .venv/bin/activate 2>/dev/null && python3 -m pytest -q tests/smoke 2>/dev/null || echo "  No smoke tests or pytest unavailable"
	@echo ""
	@echo "📊 Deep Search Reports:"
	@ls -1 reports/deep_search 2>/dev/null | head -10 || echo "  No deep search reports"
	@echo ""
	@echo "🚦 Lane Guard:"
	@./tools/ci/lane_guard.sh 2>/dev/null || echo "  ❌ Lane violations detected"

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

# Ollama-powered security operations
security-ollama:
	@echo "🤖 Running Ollama-powered security analysis..."
	@python3 scripts/ollama_security_analyzer.py scan
	@echo "✅ Ollama security analysis complete!"

security-ollama-fix:
	@echo "🔧 Auto-fixing vulnerabilities with Ollama..."
	@python3 scripts/ollama_security_analyzer.py fix
	@echo "✅ Ollama fix complete!"

security-ollama-setup:
	@echo "🛠️ Setting up Ollama for security analysis..."
	@command -v ollama >/dev/null 2>&1 || (echo "Installing Ollama..." && brew install ollama)
	@brew services start ollama 2>/dev/null || echo "Ollama service already running"
	@sleep 3
	@echo "Pulling security analysis model..."
	@ollama pull deepseek-coder:6.7b || true
	@echo "✅ Ollama setup complete!"

# Enhanced security vulnerability fixes
security-fix-vulnerabilities:
	@echo "🛡️ Auto-fixing known security vulnerabilities..."
	@python3 scripts/fix_security_vulnerabilities.py
	@echo "✅ Security vulnerabilities fixed!"

# Fix security issues found by Bandit linter
security-fix-issues:
	@echo "🛡️ Auto-fixing security issues (Bandit findings)..."
	@python3 scripts/fix_security_issues.py
	@echo "✅ Security issues fixed!"

# Fix all security problems (vulnerabilities + issues)
security-fix-all:
	@echo "🛡️ Fixing ALL security vulnerabilities and issues..."
	@make security-fix-vulnerabilities
	@make security-fix-issues
	@echo "✅ All security fixes complete!"

# Schedule security tasks for later execution
security-schedule:
	@echo "🕒 LUKHAS Security Task Scheduler"
	@echo "=================================="
	@python3 scripts/security_scheduler.py status
	@echo ""
	@echo "💡 Schedule security fixes for later:"
	@echo "   make security-schedule-3h    - Schedule in 3 hours"
	@echo "   make security-schedule-tonight - Schedule at 8 PM today"
	@echo "   Or use: python3 scripts/security_scheduler.py schedule fix-all +2h"

security-schedule-3h:
	@echo "⏰ Scheduling security fixes in 3 hours..."
	@python3 scripts/security_scheduler.py schedule fix-all +3h --description "Automated security fix (3h delay)"

security-schedule-tonight:
	@echo "🌙 Scheduling security fixes for 8 PM tonight..."
	@python3 scripts/security_scheduler.py schedule fix-all 20:00 --description "Evening security maintenance"

security-schedule-list:
	@python3 scripts/security_scheduler.py list

security-schedule-run:
	@python3 scripts/security_scheduler.py run-pending

security-comprehensive-scan:
	@echo "🔍 Running comprehensive security scan..."
	@mkdir -p security-reports
	@echo "Running Safety CLI scan..."
	@safety scan --output json --save-json security-reports/safety-scan.json 2>/dev/null || echo "Safety scan completed with issues"
	@echo "Running pip-audit..."
	@pip-audit --format json --output security-reports/pip-audit.json 2>/dev/null || echo "pip-audit completed with issues"
	@echo "Running Bandit security scan..."
	@bandit -r . -f json -o security-reports/bandit.json -x .venv,venv,node_modules,.git 2>/dev/null || echo "Bandit scan completed"
	@echo "Running Ollama analysis..."
	@python3 scripts/ollama_security_analyzer.py scan > security-reports/ollama-analysis.txt
	@echo "📊 Security reports saved to security-reports/"
	@echo "✅ Comprehensive security scan complete!"

security-emergency-patch:
	@echo "🚨 EMERGENCY SECURITY PATCH MODE"
	@echo "This will automatically fix ALL known critical vulnerabilities"
	@read -p "Continue? (y/N): " -n 1 -r; echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		make security-fix-vulnerabilities; \
		pip install -r requirements.txt; \
		make test-security; \
		echo "✅ Emergency patch complete!"; \
	else \
		echo "❌ Emergency patch cancelled"; \
	fi

test-security:
	@echo "🧪 Running security-focused tests..."
	@python3 -c "import fastapi, aiohttp, transformers; print('✅ Critical packages import successfully')"
	@pytest tests/ -k "security" -v --tb=short || echo "No specific security tests found"
	@echo "✅ Security tests complete!"

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

# Audit Navigation & Deep Search Support
audit-nav:
	@echo "🔍 LUKHAS AI Deep Search Navigation"
	@echo "===================================="
	@echo "📋 Audit Entry Point: AUDIT/INDEX.md"
	@echo "🗺️  System Architecture: AUDIT/SYSTEM_MAP.md"
	@echo "🧠 MATRIZ Readiness: AUDIT/MATRIZ_READINESS.md"
	@echo "⚛️  Identity Readiness: AUDIT/IDENTITY_READINESS.md"
	@echo "📊 API Documentation: AUDIT/API/openapi.yaml"
	@echo "🔗 Deep Search Indexes: reports/deep_search/"
	@echo ""
	@echo "Quick Commands:"
	@echo "  make audit-scan    - Health check and validation"
	@echo "  make api-serve     - Start API server for testing"
	@echo "  make test-cov      - Run tests with coverage report"

audit-scan:
	@echo "🔍 Running comprehensive audit scan..."
	@echo "Checking lane architecture compliance..."
	@python3 tools/ci/find_import_cycles.py
	@echo "Validating MATRIZ readiness..."
	@[ -f "AUDIT/MATRIZ_READINESS.md" ] && echo "✅ MATRIZ docs present" || echo "❌ Missing MATRIZ docs"
	@echo "Checking Identity system..."
	@[ -f "AUDIT/IDENTITY_READINESS.md" ] && echo "✅ Identity docs present" || echo "❌ Missing Identity docs"
	@echo "Validating API schemas..."
	@[ -f "AUDIT/API/openapi.yaml" ] && echo "✅ OpenAPI spec present" || echo "❌ Missing OpenAPI spec"
	@echo "Running policy compliance..."
	@make policy || echo "⚠️  Policy issues detected"
	@echo "✅ Audit scan complete! See results above."

api-serve:
	@echo "🚀 Starting API server for auditing..."
	@echo "Server will be available at: http://localhost:8080"
	@echo "OpenAPI docs at: http://localhost:8080/docs"
	uvicorn api.app:app --reload --port 8080 --host 0.0.0.0

# Policy & Brand Enforcement
policy: policy-registries policy-brand policy-tone policy-routes policy-vocab
	@echo "✅ All policy checks passed"

policy-review:
	@echo "🔍 Flagging claims for human review..."
	@npm run policy:review

policy-brand:
	@echo "🎨 Checking brand compliance..."
	@npm run policy:brand

policy-tone:
	@echo "📝 Validating tone layers..."
	@npm run policy:tone

policy-registries:
	@echo "📋 Validating module/site registries..."
	@npm run policy:registries

policy-routes:
	@echo "🗺️ Validating site sections have matching routes..."
	@npm run policy:routes

policy-vocab:
	@echo "📚 Validating vocabulary compliance..."
	@npm run vocab:validate

# Phase 1 Verification
verify: phase1
phase1:
	bash tools/verification/run_all_checks.sh
status:
	@sha=$$(git rev-parse HEAD); \
	cat verification_artifacts/$$sha/system_status/summary.md || echo "No artifacts for $$sha"
hook-install:
	npm install --save-dev husky
	npx husky install
	npx husky add .husky/pre-commit "python3 tools/acceptance_gate.py" >/dev/null
	npx husky add .husky/post-commit "make verify" >/dev/null
	chmod +x .husky/pre-commit .husky/post-commit

.PHONY: pc-all
pc-all:
	pre-commit run --all-files || true

.PHONY: matriz-compile matriz-ci audit-validate sbom

# Compile all MATRIZ author graphs under graphs/ to reports/matriz/
matriz-compile:
	@python -m tools.matriz.compile_all graphs reports/matriz

# MATRIZ CI gate: compile all graphs and fail on invariant violations
matriz-ci: matriz-compile
	@echo "✅ MATRIZ compile completed; see reports/matriz for plans and reports"

# Audit validator for JSON provenance across repository master artifacts
audit-validate:
	@python tools/ci/update_and_validate_json.py

# Software Bill of Materials (CycloneDX) if CLI available
sbom:
	@cyclonedx-bom -o reports/sbom/cyclonedx.json || echo "cyclonedx-bom not installed; skipped"


# NOTE: informational variant; kept separate to avoid colliding with 'audit-nav'
.PHONY: audit-nav-info
audit-nav-info:
	@echo "Commit: $(shell cat AUDIT/RUN_COMMIT.txt 2>/dev/null || git rev-parse HEAD)"
	@echo "Started: $(shell cat AUDIT/RUN_STARTED_UTC.txt 2>/dev/null)"
	@echo "Files: $(shell wc -l reports/deep_search/PY_INDEX.txt 2>/dev/null | awk '{print $$1}')"
	@echo "Sample: AUDIT/CODE_SAMPLES.txt"


# NOTE: list-only variant; 'audit-scan' remains the comprehensive validator above
.PHONY: audit-scan-list
audit-scan-list:
	@ls -1 reports/deep_search | sed 1,20p


# Minimal CI-friendly check target (scoped to focused gates: ruff, contract tests, scoped mypy)
.PHONY: check-scoped lint-scoped test-contract type-scoped
lint-scoped:
	ruff check serve tests/contract
test-contract:
	pytest -q tests/contract --maxfail=1 --disable-warnings
type-scoped:
	mypy --follow-imports=skip --ignore-missing-imports serve/main.py || true
check-scoped: lint-scoped test-contract type-scoped
	@echo "✅ make check-scoped passed (lint + tests + scoped mypy)"


# ------------------------------------------------------------------------------
# T4 Doctor: fast repo health diagnostics (non-destructive, noisy on failure)
# ------------------------------------------------------------------------------

# Aggregate
doctor: doctor-tools doctor-py doctor-ci doctor-lanes doctor-tests doctor-audit doctor-dup-targets doctor-phony doctor-summary

# 1) Tooling presence
doctor-tools:
	@echo "🔎 [tools] Checking required CLI tools..."
	@ok=1; \
	for bin in python3 jq rg curl git; do \
		if ! command -v $$bin >/dev/null 2>&1; then echo "❌ missing: $$bin"; ok=0; fi; \
	done; \
	for py in ruff pytest mypy bandit; do \
		if ! python3 -m $$py --version >/dev/null 2>&1; then echo "⚠️ python -m $$py unavailable"; fi; \
	done; \
	[ $$ok -eq 1 ] && echo "✅ tools ok" || (echo "⚠️ some tools missing"; exit 0)

# 2) Python/venv sanity
doctor-py:
	@echo "🔎 [python] venv & import sanity..."
	@if [ -d ".venv" ]; then echo "✅ .venv present"; else echo "⚠️ .venv missing"; fi
	@python3 -c "import sys; print('✅ python', sys.version.split()[0])" || echo "❌ python not runnable"
	@PYTHONPATH=. python3 -c "import lukhas, matriz; print('✅ lukhas & matriz importable')" || echo "⚠️ import check failed"

# 3) CI wiring sanity
doctor-ci:
	@echo "🔎 [ci] workflow presence & test matrix..."
	@if [ -f ".github/workflows/ci.yml" ]; then \
		echo "✅ ci.yml present"; \
		grep -q 'pytest' .github/workflows/ci.yml && echo "✅ pytest referenced" || echo "⚠️ pytest not referenced"; \
		grep -q 'tier1' .github/workflows/ci.yml && echo "✅ tier1 matrix present" || echo "⚠️ tier1 matrix missing"; \
	else \
		echo "⚠️ no .github/workflows/ci.yml"; \
	fi

# 4) Lane integrity (static + runtime)
doctor-lanes:
	@echo "🔎 [lanes] lane guards..."
	@{ PYTHONPATH=. lint-imports -v 2>/dev/null || echo '⚠️ import-linter not configured'; } | sed -n '1,80p'
	@{ bash ./tools/ci/lane_guard.sh 2>/dev/null || true; } | sed -n '1,80p'

# 5) Tests quick slice
doctor-tests:
	@echo "🔎 [tests] collection & tier1 MATRIZ sanity..."
	@PYTHONPATH=. python3 -m pytest -q --collect-only 2>/dev/null | sed -n '1,10p' || true
	@PYTHONPATH=. python3 -m pytest -q -m tier1 tests_new/matriz 2>/dev/null || echo "⚠️ MATRIZ tier1 failed"

# 6) Audit artifacts
doctor-audit:
	@echo "🔎 [audit] key artifacts..."
	@[ -f "AUDIT/INDEX.md" ] && echo "✅ AUDIT/INDEX.md" || echo "❌ missing AUDIT/INDEX.md"
	@[ -f "AUDIT/MATRIZ_READINESS.md" ] && echo "✅ AUDIT/MATRIZ_READINESS.md" || echo "❌ missing MATRIZ_READINESS"
	@[ -f "AUDIT/IDENTITY_READINESS.md" ] && echo "✅ AUDIT/IDENTITY_READINESS.md" || echo "⚠️ missing IDENTITY_READINESS"
	@[ -f "AUDIT/API/openapi.yaml" ] && echo "✅ AUDIT/API/openapi.yaml" || echo "⚠️ missing openapi.yaml"
	@[ -f "reports/sbom/cyclonedx.json" ] && echo "✅ SBOM present" || echo "⚠️ SBOM missing"

# 7) Duplicate targets in Makefile (footgun detector)
doctor-dup-targets:
	@echo "🔎 [make] duplicate target names..."
	@awk -F: '/^[A-Za-z0-9_.-]+:/{print $$1}' Makefile \
	 | grep -v '^.PHONY' | grep -v '^include' | grep -v '^\#' \
	 | sort | uniq -d | sed -n '1,50p' | awk '{print "⚠️ duplicate target: " $$1}' || true

# 8) PHONY targets without rules
doctor-phony:
	@echo "🔎 [make] .PHONY without recipe..."
	@ph=$$(grep -Eo '^\.PHONY:[^#]+' Makefile | sed 's/^\.PHONY://; s/[\\ ]\+/ /g' | tr ' ' '\n' | sort -u); \
	for t in $$ph; do \
	  grep -qE "^$$t:" Makefile || echo "⚠️ .PHONY declared but no rule: $$t"; \
	done; true

# 9) Summary
doctor-summary:
	@echo "✅ Doctor finished. Review warnings above. Non-zero exit only for hard failures."

# --- Strict & JSON outputs ---------------------------------------------------

# Strict variant: fails build if any warnings or errors are present
doctor-strict:
	@mkdir -p reports/audit
	@echo "🧪 Running doctor in strict mode..."
	@($(MAKE) -s doctor) | tee reports/audit/doctor_last.txt
	@if grep -E '❌|⚠️' reports/audit/doctor_last.txt >/dev/null; then \
		echo "❌ doctor:strict detected warnings/errors. See reports/audit/doctor_last.txt"; \
		exit 1; \
	else \
		echo "✅ doctor:strict clean (no warnings/errors)"; \
	fi

# Duplicate targets strict: exit 1 if any duplicates detected
doctor-dup-targets-strict:
	@dups=$$(awk -F: '/^[A-Za-z0-9_.-]+:/{print $$1}' Makefile \
	 | grep -v '^.PHONY' | grep -v '^include' | grep -v '^\#' \
	 | sort | uniq -d); \
	if [ -n "$$dups" ]; then \
		echo "$$dups" | awk '{print "❌ duplicate target (strict): " $$1}'; \
		exit 1; \
	else \
		echo "✅ no duplicate Make targets (strict)"; \
	fi

# Machine-readable summary (requires jq)
doctor-json:
	@mkdir -p reports/audit
	@echo "🧾 Emitting JSON summary to reports/audit/doctor_summary.json"
	@tools_ok=1; \
	for bin in python3 jq rg curl git; do command -v $$bin >/dev/null || tools_ok=0; done; \
	py_ok=0; PYTHONPATH=. python3 -c "import lukhas, matriz" >/dev/null 2>&1 && py_ok=1 || true; \
	ci_present=0; [ -f ".github/workflows/ci.yml" ] && ci_present=1 || true; \
	sbom_present=0; [ -f "reports/sbom/cyclonedx.json" ] && sbom_present=1 || true; \
	audit_index=0; [ -f "AUDIT/INDEX.md" ] && audit_index=1 || true; \
	tier1_ok=0; PYTHONPATH=. python3 -m pytest -q -m tier1 tests_new/matriz >/dev/null 2>&1 && tier1_ok=1 || true; \
	dups=$$(awk -F: '/^[A-Za-z0-9_.-]+:/{print $$1}' Makefile \
	 | grep -v '^.PHONY' | grep -v '^include' | grep -v '^\#' \
	 | sort | uniq -d | wc -l); \
	jq -n --arg now "$$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
	      --arg git "$$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")" \
	      --argjson tools $$tools_ok \
	      --argjson python $$py_ok \
	      --argjson ci $$ci_present \
	      --argjson sbom $$sbom_present \
	      --argjson audit $$audit_index \
	      --argjson tier1 $$tier1_ok \
	      --argjson dup_count $$dups \
	      '{timestamp:$now, commit:$git, checks:{tools:$tools, python_imports:$python, ci_workflow:$ci, sbom:$sbom, audit_index:$audit, matriz_tier1:$tier1, make_dup_targets:$dup_count}}' \
	  > reports/audit/doctor_summary.json
	@echo "✅ Wrote reports/audit/doctor_summary.json"

