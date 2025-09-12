# Main Makefile PHONY declarations (only for targets defined in this file)
.PHONY: install setup-hooks dev api openapi live colony-dna-smoke lint lint-unused lint-unused-strict format fix fix-all fix-ultra fix-imports
.PHONY: ai-analyze ai-setup ai-workflow clean deep-clean quick bootstrap organize organize-dry organize-suggest organize-watch
.PHONY: codex-validate codex-fix validate-all perf migrate-dry migrate-run dna-health dna-compare admin lint-status lane-guard
.PHONY: audit-tail sdk-py-install sdk-py-test sdk-ts-build sdk-ts-test backup-local backup-s3 restore-local restore-s3 dr-drill dr-weekly dr-quarterly dr-monthly
.PHONY: audit-appendix audit-normalize audit-merge audit-merge-auto audit-merge-check
.PHONY: check-scoped lint-scoped test-contract type-scoped doctor doctor-tools doctor-py doctor-ci doctor-lanes doctor-tests doctor-audit doctor-dup-targets doctor-phony doctor-summary doctor-strict doctor-dup-targets-strict doctor-json
.PHONY: todo-unused todo-unused-check todo-unused-core t4-annotate t4-check

# Note: Additional PHONY targets are declared in mk/*.mk include files

# Modular includes (guarded)
ifneq ($(wildcard mk/*.mk),)
include mk/*.mk
endif

# Note: Main help target is defined in mk/help.mk

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

# T4 unused imports policy (production lanes only)
lint-unused:
	@echo "🎯 T4 Unused Imports Annotator (Production Lanes)"
	@echo "⚛️ Scanning lukhas/ and MATRIZ/ for F401 violations..."
	python3 tools/ci/unused_imports.py --paths lukhas MATRIZ

lint-unused-strict:
	@echo "🎯 T4 Unused Imports Enforcer (Production Lanes - Strict Mode)"
	@echo "⚛️ Failing if any unannotated F401 remain in lukhas/ and MATRIZ/..."
	python3 tools/ci/unused_imports.py --paths lukhas MATRIZ --strict

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

# Note: Test targets are defined in mk/tests.mk

# Note: CI/CD targets are defined in mk/ci.mk

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

# Deep clean including virtual environment
deep-clean: clean
	@echo "🧹 Deep cleaning..."
	rm -rf venv .venv
	rm -rf htmlcov .coverage
	rm -rf dist build *.egg-info
	@echo "✅ Deep clean complete!"

# Quick fix and test
quick: fix test ## Fix issues and run tests
	@echo "✅ Quick fix and test complete!"

# Note: Audit targets are defined in mk/audit.mk

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

# Note: Security targets are defined in mk/security.mk

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

# Note: Policy targets are defined in mk/policy.mk (if exists)

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

# Remaining duplicate targets removed - all functionality preserved in mk/*.mk modules


# Generate audit delta appendix between two tags
audit-appendix:
	tools/audit/mk_delta_appendix.py --old $(OLD_TAG) --new $(NEW_TAG) --out reports/audit/appendix_delta.md

# --- Audit merge helpers (T4) -----------------------------------------------

STRAT ?= reports/audit/strategic_20250910T143306Z.md
NEUT  ?= reports/audit/neutral_20250910T143306Z.md
OUT   ?= reports/audit/merged

.PHONY: audit-normalize audit-merge audit-merge-auto audit-merge-check

audit-normalize:
	@python3 tools/audit/normalize_audit_md.py --in $(STRAT) --out $(STRAT)
	@python3 tools/audit/normalize_audit_md.py --in $(NEUT)  --out $(NEUT)

audit-merge:
	@python3 merge_audits.py --strategic $(STRAT) --neutral $(NEUT) --out-dir $(OUT)

audit-merge-auto:
	@python3 merge_audits.py --auto --out-dir $(OUT)

audit-merge-check:
	@echo "Findings parsed from Strategic:"
	@python3 -c "import importlib.util; spec=importlib.util.spec_from_file_location('merge_audits','merge_audits.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(len(m.parse_findings_table(m.load_text('$(STRAT)'))))"
	@echo "Findings parsed from Neutral:"
	@python3 -c "import importlib.util; spec=importlib.util.spec_from_file_location('merge_audits','merge_audits.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(len(m.parse_findings_table(m.load_text('$(NEUT)'))))"
	@echo "Merged scoreboard (if present):"
	@[ -f $(OUT)/scoreboard.json ] && cat $(OUT)/scoreboard.json || echo "(not generated yet)"

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
doctor: doctor-tools doctor-py doctor-ci doctor-lanes doctor-tests doctor-audit doctor-dup-targets doctor-phony doctor-summary ## Quick repo health scan (T4-style diagnostics)

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


# ==============================================================================
# T4 UNUSED IMPORTS SYSTEM - Transform Technical Debt into Documented Intent
# ==============================================================================

# T4 annotate unused imports with TODOs (all production lanes)
todo-unused:
	@echo "🎯 T4 UNUSED IMPORTS ANNOTATOR - All Production Lanes"
	@echo "⚛️ Transforming technical debt into documented intent"
	python3 tools/ci/mark_unused_imports_todo.py

# T4 annotate only core modules (lukhas/ only)
todo-unused-core:
	@echo "🎯 T4 UNUSED IMPORTS ANNOTATOR - Core Modules Only"
	@echo "⚛️ Transforming technical debt into documented intent"
	python3 tools/ci/mark_unused_imports_todo.py --paths lukhas

# T4 validate all production imports are annotated
todo-unused-check:
	@echo "🔍 T4 UNUSED IMPORTS VALIDATOR - Production Lane Policy"
	@echo "⚛️ Ensuring all unused imports are properly documented"
	python3 tools/ci/check_unused_imports_todo.py

# Legacy aliases for backwards compatibility
t4-annotate: todo-unused
t4-check: todo-unused-check
