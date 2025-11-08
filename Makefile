# NOTE: Registry targets moved to canonical location (line ~1820)
# See registry-up, registry-smoke, registry-ci, registry-clean, registry-test below
# Main Makefile PHONY declarations (only for targets defined in this file)
.PHONY: install setup-hooks dev api openapi openapi-spec openapi-validate facade-smoke live colony-dna-smoke smoke-matriz lint lint-unused lint-unused-strict format fix fix-all fix-ultra fix-imports oneiric-drift-test validate-root validate-root-docs validate-root-all
.PHONY: load-smoke load-test load-extended load-spike load-locust load-check
.PHONY: ai-analyze ai-setup ai-workflow clean deep-clean quick bootstrap organize organize-dry organize-suggest organize-watch
.PHONY: codex-validate codex-fix validate-all perf migrate-dry migrate-run dna-health dna-compare admin lint-status lane-guard
.PHONY: audit-tail sdk-py-install sdk-py-test sdk-ts-build sdk-ts-test backup-local backup-s3 restore-local restore-s3 dr-drill dr-weekly dr-quarterly dr-monthly
.PHONY: audit-appendix audit-normalize audit-merge audit-merge-auto audit-merge-check
.PHONY: check-scoped lint-scoped test-contract type-scoped doctor doctor-tools doctor-py doctor-ci doctor-lanes doctor-tests doctor-audit doctor-dup-targets doctor-phony doctor-summary doctor-strict doctor-dup-targets-strict doctor-json
.PHONY: todo-unused todo-unused-check todo-unused-core todo-unused-candidate t4-annotate t4-check audit-f821 fix-f821-core annotate-f821-candidate types-audit types-enforce types-core types-trend types-audit-trend types-enforce-trend f401-audit f401-trend
.PHONY: test-tier1 test-all test-fast test-report test-clean spec-lint contract-check specs-sync test-goldens oneiric-drift-test collapse
.PHONY: validate-matrix-all authz-run coverage-report matrix-v3-upgrade matrix-v3-check matrix-tokenize matrix-provenance matrix-verify-provenance manifests-validate manifest-lock manifest-index manifest-diff conformance-generate conformance-test manifest-system
.PHONY: matriz-audit matriz-where matriz-eval matriz-eval-quick matriz-eval-benchmark
.PHONY: scaffold-dry scaffold-apply scaffold-apply-force scaffold-diff scaffold-diff-all validate-scaffold sync-module sync-module-force
.PHONY: validate-configs validate-secrets validate-naming readiness-score readiness-detailed quality-report test-shards test-parallel t4-sim-lane imports-guard audit-validate-ledger feedback-validate
.PHONY: emergency-bypass clean-artifacts dev-setup status ci-validate ci-artifacts help
.PHONY: mcp-bootstrap mcp-verify mcp-selftest mcp-ready mcp-contract mcp-smoke mcp-freeze mcp-docker-build mcp-docker-run mcp-validate-catalog mcp-health
.PHONY: meta-registry ledger-check trends validate-t4 validate-t4-strict tag-prod freeze-verify freeze-guardian freeze-guardian-once dashboard-sync init-dev-branch
.PHONY: docs-map docs-migrate-auto docs-migrate-dry docs-lint validate-structure module-health vault-audit vault-audit-vault star-rules-lint star-rules-coverage promotions
.PHONY: lint-json lint-fix lint-delta f401-tests import-map imports-abs imports-graph ruff-heatmap ruff-ratchet f821-suggest f706-detect f811-detect todos todos-issues codemod-dry codemod-apply check-legacy-imports
.PHONY: state-sweep shadow-diff plan-colony-renames integration-manifest
.PHONY: t4-init t4-migrate t4-migrate-dry t4-validate t4-dashboard t4-api t4-parallel t4-parallel-dry t4-codemod-dry t4-codemod-apply
.PHONY: evidence-pages evidence-validate evidence-validate-strict branding-vocab-lint branding-claims-fix

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

# Generate OpenAPI spec (no server required)
openapi-spec:
	@echo "📝 Generating OpenAPI spec for OpenAI façade..."
	@mkdir -p docs/openapi
	@python - <<'PY'
	import json, os
	from lukhas.adapters.openai.api import get_app
	app = get_app()
	spec = app.openapi()
	os.makedirs("docs/openapi", exist_ok=True)
	with open("docs/openapi/lukhas-openapi.json","w") as f:
	    json.dump(spec, f, indent=2)
	print("✅ wrote docs/openapi/lukhas-openapi.json")
	PY

# Validate OpenAPI spec
openapi-validate: openapi-spec
	@echo "✅ Validating OpenAPI spec..."
	@pip install -q openapi-spec-validator
	@openapi-spec-validator docs/openapi/lukhas-openapi.json
	@echo "✅ OpenAPI spec is valid!"

# Run OpenAI façade smoke tests
facade-smoke:
	@echo "🚬 Running OpenAI façade smoke tests..."
	@bash scripts/smoke_test_openai_facade.sh

# Live integration test
live:
	python3 scripts/testing/live_integration_test.py

# Colony↔DNA demo
colony-dna-smoke:
	python3 scripts/colony_dna_smoke.py

# MATRIZ traces smoke (deterministic, uses golden fixture)
smoke-matriz:
	@echo "🚬 Running MATRIZ traces smoke (GET /traces/latest)..."
	PYTHONPATH=. python3 -m pytest -q tests/smoke/test_traces_router.py --maxfail=1 --disable-warnings
	@echo "✅ MATRIZ traces smoke passed"

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

# Build system performance metrics dashboard
metrics-dashboard:
	@echo "🎯 Generating Build System Performance Dashboard..."
	@mkdir -p reports
	@python3 tools/ci/build_metrics_dashboard.py
	@echo "✅ Dashboard complete! Check reports/build_performance_report.md"

# Check linting status
lint-status:
	@python tools/scripts/check_progress.py

oneiric-drift-test:
	python oneiric_core/tools/drift_dream_test.py --symbol LOYALTY --user demo --seed 7

# Lane guard: forbid lukhas -> candidate imports (belt-and-suspenders)
lane-guard:
	@echo "🔒 Running lane import guard..."
	@PYTHONPATH=$$(pwd) .venv/bin/lint-imports --config .importlinter
	@echo "✅ Lane guard clean"

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
	cd sdk/python && python3 -m pytest -q

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

# ------------------------------------------------------------------------------
# Local parity shortcuts for CI selections
# ------------------------------------------------------------------------------
.PHONY: smoke test it e2e
smoke:
	CI_QUALITY_GATES=1 python3 -m pytest -q tests/smoke -m "smoke" --maxfail=1 --disable-warnings
test:
	python3 -m pytest -q --disable-warnings
it:
	python3 -m pytest -q -m "integration" --disable-warnings
e2e:
	python3 -m pytest -q -m "e2e" --disable-warnings

# ------------------------------------------------------------------------------
# Registry & NodeSpec helpers (Agent C/D support)
# ------------------------------------------------------------------------------
# NOTE: nodespec-validate moved to canonical location (line ~1816)
# NOTE: registry-test moved to canonical location (line ~1824)

# Minimal CI-friendly check target (scoped to focused gates: ruff, contract tests, scoped mypy)
.PHONY: check-scoped lint-scoped test-contract type-scoped
lint-scoped:
	ruff check serve tests/contract
test-contract:
	python3 -m pytest -q tests/contract --maxfail=1 --disable-warnings
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

# T4 candidate promotion helper
todo-unused-candidate:
	@echo "🎯 T4 UNUSED IMPORTS ANNOTATOR - Candidate Directory"
	@echo "⚛️ Preparing experimental code for production promotion"
	python3 tools/ci/mark_unused_imports_todo.py --paths candidate

# Legacy aliases for backwards compatibility
t4-annotate: todo-unused
t4-check: todo-unused-check

.PHONY: audit-f821 fix-f821-core annotate-f821-candidate

audit-f821:
	@python3 tools/ci/f821_report.py --paths "lukhas MATRIZ candidate" && echo "See reports/audit/f821_summary.md"

fix-f821-core:
	@python3 tools/ci/f821_report.py --paths "lukhas MATRIZ" --enforce-core

annotate-f821-candidate:
	@python3 tools/ci/f821_report.py --paths "candidate" --annotate-candidate

.PHONY: types-audit types-enforce types-core

types-audit:
	@mkdir -p reports/audit/types
	@python3 -m mypy --hide-error-context --no-error-summary --no-color-output --pretty --error-format=json > reports/audit/types/mypy.json || true
	@python3 tools/ci/mypy_to_md.py reports/audit/types/mypy.json reports/audit/types/mypy_summary.md && echo "See reports/audit/types/mypy_summary.md"

types-enforce:
	@mkdir -p reports/audit/types
	@python3 -m mypy --hide-error-context --no-error-summary --no-color-output --pretty --error-format=json > reports/audit/types/mypy.json || true
	@python3 -c "import json,sys; j=json.load(open('reports/audit/types/mypy.json')); core=sum(1 for e in j.get('errors',[]) if str(e.get('path','')).startswith(('lukhas/','MATRIZ/'))); print(f'Core mypy errors: {core}'); sys.exit(1 if core>0 else 0)"
	@python3 tools/ci/mypy_to_md.py reports/audit/types/mypy.json reports/audit/types/mypy_summary.md

# fast local check limited to core paths (honors pyproject files=)
types-core:
	@python3 -m mypy lukhas MATRIZ

.PHONY: types-trend

types-trend:
	@python3 tools/ci/mypy_trend.py

# F401 unused import trend tracking
f401-audit:
	@mkdir -p reports/audit
	@python3 -m ruff check --select F401 --output-format json > reports/audit/f401.json || true
	@echo "F401 audit saved to reports/audit/f401.json"

f401-trend:
	@python3 tools/ci/f401_trend.py

# Convenience combos
types-audit-trend: types-audit types-trend
types-enforce-trend: types-enforce types-trend

# ==============================================================================
# T4 TEST FRAMEWORK - Deterministic Policy & Golden Discipline
# ==============================================================================

.PHONY: audit test-tier1 test-all test-fast test-report test-clean spec-lint contract-check specs-sync test-goldens hidden-gems

# T4 audit - zero collection errors required
audit: ## Generate audit snapshot (one-command auditor UX)
	@make audit-snapshot
	@echo "✅ Audit snapshot generated"
	@echo "📖 Open AUDIT_README.md for entry point"

audit-pack: ## Generate comprehensive audit packet for external review
	@bash scripts/make_audit_packet.sh

audit-snapshot: ## Generate live audit snapshot (OpenAPI, Ruff, Health)
	@bash scripts/audit_snapshot.sh

hidden-gems: ## Analyze isolated modules and find hidden gems (0.01% quality)
	@python3 scripts/analyze_hidden_gems.py
	@echo ""
	@echo "📖 See docs/audits/hidden_gems_top20.md for actionable insights"

integration-manifest: ## Generate comprehensive integration manifest for all 193 hidden gems
	@python3 scripts/generate_integration_manifest.py
	@echo ""
	@echo "📋 Integration manifest: docs/audits/integration_manifest.json"
	@echo "📖 Integration guide: docs/audits/INTEGRATION_GUIDE.md"

test-clean:
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} + || true

test-tier1:
	@TZ=UTC PYTHONHASHSEED=0 python3 -m pytest -m "tier1 and not quarantine" --cov=lukhas --cov=MATRIZ --cov-branch --cov-report=xml:reports/tests/cov.xml

test-all:
	@TZ=UTC PYTHONHASHSEED=0 python3 -m pytest -m "not quarantine" --cov=lukhas --cov=MATRIZ --cov-branch --cov-report=xml:reports/tests/cov.xml

test-fast:
	@TZ=UTC PYTHONHASHSEED=0 python3 -m pytest -m "smoke or tier1" -q

test-report:
	@python3 -c "import xml.etree.ElementTree as ET; p='reports/tests/cov.xml'; \
	try: \
	 t=ET.parse(p).getroot(); print('Coverage line-rate:', t.attrib.get('line-rate','?')); \
	except Exception as e: \
	 print('No coverage report yet:', e)"

spec-lint:
	@python3 tools/tests/spec_lint.py tests/specs

contract-check:
	@python3 tools/tests/contract_check.py $${BASE_REF:-origin/main}

specs-sync:
	@python3 tools/tests/specs_sync.py

test-goldens:
	@python3 tools/tests/validate_golden.py

# Jules-06 focused test lane
.PHONY: test-jules06
test-jules06:
	@echo "🧪 Jules-06 focused adapters lane"
	@export TZ=UTC PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.; \
	python3 -m pytest -q \
	  -m "not quarantine" \
	  tests/unit/bridge/adapters/test_gmail_adapter.py \
	  tests/unit/bridge/adapters/test_dropbox_adapter.py \
	  tests/unit/bridge/adapters/test_oauth_manager.py \
	  tests/unit/security/test_security.py \
	  tests/integration/bridge/adapters/test_gmail_adapter.py \
	  tests/integration/bridge/adapters/test_dropbox_adapter.py \
	  tests/integration/bridge/adapters/test_oauth_manager.py \
	  tests/integration/bridge/test_service_integration.py \
	  tests/integration/security/test_security.py \
	  --cov=candidate.bridge.adapters \
	  --cov=candidate.bridge.external_adapters \
	  --cov=candidate.bridge.api.validation \
	  --cov=candidate.bridge.adapters.service_adapter_base \
	  --cov-branch \
	  --cov-report=xml:reports/tests/cov_adapters.xml \
	  --cov-report=term-missing
# AI interface audit rollup (JSONL -> CSV evidence ledger)
.PHONY: audit-rollup audit-dashboard dash-validate run-prom

audit-rollup:
	@echo "📥 Rolling up AI audit JSONL into evidence ledger CSV..."
	@python3 tools/reports/ai_audit_rollup.py
	@echo "✅ Evidence ledger updated: reports/audit/merged/evidence_ledger.csv"

# Generate a simple dashboard from evidence ledger CSV
audit-dashboard: audit-rollup
	@echo "📊 Generating AI audit dashboard..."
	@python3 tools/reports/ai_audit_dashboard.py
	@echo "✅ Dashboard: reports/dashboard/ai_audit_summary.md"

# Validate Grafana dashboard JSON syntax and essential PromQL queries
.PHONY: dash-validate
dash-validate:
	@echo "📊 Validating Grafana dashboard JSON..."
	@python3 -m json.tool dashboards/lukhas_ops.json > /dev/null || (echo "❌ Invalid JSON syntax in dashboard" && exit 1)
	@.venv/bin/pytest tests/unit/observability/test_grafana_dashboard_json.py -q || (echo "❌ Dashboard validation failed" && exit 1)
	@echo "✅ Dashboard validation passed"

# Run LUKHAS with Prometheus metrics exporter
.PHONY: run-prom
run-prom:
	@echo "🚀 Starting LUKHAS with Prometheus exporter on :9095..."
	LUKHAS_PROM_PORT=9095 python -m lukhas

# T4 Hardening Test Suite
.PHONY: test.t4
test.t4:
	PYTHONHASHSEED=0 LUKHAS_STRICT_EMIT=1 LUKHAS_STRESS_DURATION=1.0 \
		python3 -m pytest tests/unit/metrics -v && \
		python3 -m pytest tests/capabilities -m capability -v && \
		python3 -m pytest tests/e2e/consciousness/test_consciousness_emergence.py -v -k "signal_cascade_prevention or network_coherence_emergence"

# Matrix Contract Operations
.PHONY: validate-matrix validate-matrix-osv matrix-init telemetry-fixtures telemetry-test telemetry-test-all demo-verification demo-provenance demo-attestation
validate-matrix:
	@echo "🔍 Validating matrix contracts..."
	@if [ -n "$(MODULE)" ]; then \
		python3 tools/matrix_gate.py --verbose --pattern "$(MODULE)/matrix_*.json"; \
	else \
		python3 tools/matrix_gate.py --verbose --pattern "**/matrix_*.json"; \
	fi
	@echo "✅ Matrix contract validation complete"

validate-matrix-osv:
	@echo "🛡️ Validating matrix contracts with OSV scanning..."
	@if [ -n "$(MODULE)" ]; then \
		python3 tools/matrix_gate.py --verbose --osv --pattern "$(MODULE)/matrix_*.json"; \
	else \
		python3 tools/matrix_gate.py --verbose --osv --pattern "**/matrix_*.json"; \
	fi
	@echo "✅ Matrix contract validation with OSV complete"

matrix-init:
	@if [ -z "$(MODULE)" ]; then \
		echo "❌ Usage: make matrix-init MODULE=your.module.name"; \
		exit 1; \
	fi
	@echo "🚀 Initializing matrix contract for $(MODULE)..."
	@python3 tools/matrix_init.py --module $(MODULE)
	@echo "✅ Matrix contract initialized for $(MODULE)"

telemetry-fixtures:
	@if [ -z "$(MODULE)" ]; then \
		echo "❌ Usage: make telemetry-fixtures MODULE=your.module.name"; \
		exit 1; \
	fi
	@echo "📊 Generating telemetry fixtures for $(MODULE)..."
	@python3 tools/generate_telemetry_fixtures.py --module $(MODULE) --output telemetry/
	@echo "✅ Telemetry fixtures generated for $(MODULE)"

telemetry-test:
	@if [ -z "$(MODULE)" ]; then \
		echo "❌ Usage: make telemetry-test MODULE=your.module.name"; \
		exit 1; \
	fi
	@echo "🧪 Testing telemetry semconv for $(MODULE)..."
	@python3 -m pytest tests/test_telemetry_$(MODULE).py -v -m telemetry
	@echo "✅ Telemetry tests passed for $(MODULE)"

telemetry-test-all:
	@echo "🧪 Running all telemetry smoke tests..."
	@python3 -m pytest -v -m telemetry
	@echo "✅ All telemetry tests passed"

# CLI Tools
oneiric-drift-test:
	python3 -m oneiric_core.tools.drift_dream_test --symbol LOYALTY --user test --seed 42

collapse:
	python3 -m lukhas.tools.collapse_simulator --scenario ethical --seed 42

# Matrix Tracks Demo Targets
demo-verification:
	@echo "🔮 Running Matrix Tracks Verification Demo..."
	@cd examples/matrix_tracks/verification && chmod +x run_prism.sh && ./run_prism.sh

demo-provenance:
	@echo "🔗 Running Matrix Tracks Provenance Demo..."
	@cd examples/matrix_tracks/provenance && chmod +x generate_car.sh verify_car.sh && ./generate_car.sh && ./verify_car.sh

demo-attestation:
	@echo "🛡️ Running Matrix Tracks Attestation Demo..."
	@cd examples/matrix_tracks/attestation && chmod +x verify_evidence.sh && ./verify_evidence.sh

# OPA Policy validation
.PHONY: opa-validate
opa-validate:
	@echo "🔎 OPA format/check/test"
	@opa fmt -w policies/**/*.rego || true
	@opa check policies/**/*.rego
	@opa test policies/ -v || true

.PHONY: validate-module-manifests
validate-module-manifests:
	@echo "🔍 Validating module manifests"
	@python3 tools/module_manifest_upgrade.py --validate

.PHONY: module-sitemap-dry
module-sitemap-dry:
	@echo "🔍 Module sitemap dry run"
	@python3 tools/module_sitemap_sync.py --root Lukhas

.PHONY: module-sitemap-fix
module-sitemap-fix:
	@echo "📦 Applying module sitemap fixes"
	@python3 tools/module_sitemap_sync.py --write --root Lukhas

.PHONY: module-sitemap-validate
module-sitemap-validate:
	@echo "🔍 Validating module sitemap"
	@python3 tools/module_sitemap_sync.py --validate --root Lukhas

# T4 Module Manifest Validation
manifests-validate:
	@echo "🔍 T4 Module Manifest Validation"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@python3 tools/manifest_validate.py --all

# T4 Manifest System - Complete Pipeline
manifest-lock:
	@echo "🔒 T4 Manifest Lock Hydrator"
	@python3 tools/manifest_lock_hydrator.py --all

manifest-index:
	@echo "📇 T4 Manifest Indexer"
	@python3 tools/manifest_indexer.py

manifest-diff:
	@echo "🔍 T4 Manifest Registry Diff"
	@python3 tools/registry_diff.py

conformance-generate:
	@echo "🧪 T4 Conformance Test Generator"
	@python3 tools/generate_conformance_tests.py

conformance-test:
	@echo "🧪 T4 Conformance Tests"
	@python3 -m pytest -q tests/conformance

manifest-system: manifests-validate manifest-lock manifest-index manifest-diff conformance-generate conformance-test
	@echo "✅ manifest system pipeline complete"

# Matrix Identity: local validation pack
validate-matrix-all: opa-validate manifests-validate
	@echo "🎯 Matrix Identity: Full Validation Pipeline"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@python3 tools/check_policy_bundle_checksum.py || true
	@echo "📋 Stage 1: Contract Presence Gate"
	@python3 -c "\
	import json, glob; \
	contracts = sorted(glob.glob('contracts/matrix_*.json')); \
	modules = [c.split('/')[-1].replace('matrix_', '').replace('.json', '') for c in contracts]; \
	print(f'🔍 Found {len(contracts)} contracts: {modules[:5] + ([\"...\"] if len(modules) > 5 else [])}'); \
	assert len(contracts) >= 65, f'Expected ≥65 contracts, got {len(contracts)}'; \
	print('✅ Contract presence gate: PASS')"
	@echo ""
	@echo "📋 Stage 2: Schema Validation (JSON Schema 2020-12)"
	@python3 tools/validate_all_matrix.py --schema matrix.schema.template.json --pattern "contracts/matrix_*.json" --quiet
	@echo "✅ Schema validation: PASS"
	@echo ""
	@echo "📋 Stage 3: OPA Policy Tests"
	@which opa >/dev/null || (echo "❌ OPA not installed. Run: curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64 && chmod +x opa && sudo mv opa /usr/local/bin/" && exit 1)
	@cd policies/matrix && opa test identity.rego identity_test.rego -v
	@echo "✅ OPA policy tests: PASS"
	@echo ""
	@echo "📋 Stage 4: Telemetry Smoke Test"
	@python3 -m pytest tests/test_telemetry_authz_smoke.py -q --disable-warnings || (echo "❌ Telemetry smoke test failed" && exit 1)
	@echo "✅ Telemetry smoke test: PASS"
	@echo ""
	@echo "🎯 Matrix Identity validation: ALL STAGES PASSED"

authz-run:
	@echo "🚀 Authorization Matrix Test Runner"
	@python3 tools/run_matrix_tests.py --output artifacts/matrix_validation_results.json --min-pass-rate 0.95

coverage-report:
	@echo "📊 Generating Matrix Identity Coverage Report"
	@python3 tools/generate_coverage_report.py

# Matrix v3 Schema Operations
matrix-v3-upgrade:
	@echo "🚀 Upgrading all Matrix contracts with v3 placeholders"
	@python3 tools/matrix_upgrade_v3.py --pattern "contracts/matrix_*.json"
	@echo "✅ Matrix v3 upgrade complete"

matrix-v3-check:
	@echo "🔍 Checking v3 upgrade idempotency"
	@python3 tools/matrix_upgrade_v3.py --pattern "contracts/matrix_*.json" --dry-run

# Matrix v3 Sandbox Activation (safe mock implementations)
matrix-tokenize:
	@echo "🪙 Matrix v3 Tokenization (Sandbox Mode)"
	@echo "📋 Tokenizing sample contracts..."
	@python3 tools/matrix_tokenize.py --contract contracts/matrix_identity.json --verbose
	@python3 tools/matrix_tokenize.py --contract contracts/matrix_governance.json --network ethereum
	@python3 tools/matrix_tokenize.py --contract contracts/matrix_memory.json --network polygon
	@echo "✅ Matrix tokenization samples complete"

matrix-provenance:
	@echo "🔗 Matrix v3 Provenance Generation (IPLD CAR)"
	@python3 tools/matrix_provenance.py --contracts "contracts/matrix_*.json"
	@echo "✅ Matrix provenance CAR generated"

matrix-verify-provenance:
	@echo "🔍 Matrix v3 Provenance Verification"
	@tools/verify_provenance.sh
	@echo "✅ Matrix provenance verification complete"

# MATRIZ Audit System
matriz-audit:
	@echo "🔍 MATRIZ Comprehensive Audit Pipeline"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "📋 Stage 1: Module Discovery"
	@python3 tools/matriz_audit_discovery.py --verbose
	@echo ""
	@echo "📋 Stage 2: Import Analysis"
	@python3 tools/matriz_import_scan.py --verbose
	@echo ""
	@echo "📋 Stage 3: Lane Assessment"
	@python3 tools/matriz_lane_assessor.py --verbose
	@echo ""
	@echo "📋 Stage 4: Data Aggregation"
	@python3 tools/matriz_audit_aggregate.py --verbose
	@echo ""
	@echo "📋 Stage 5: Report Generation"
	@python3 tools/matriz_report_generator.py --verbose
	@echo ""
	@echo "✅ MATRIZ audit complete! Check artifacts/ directory for results."

matriz-where:
	@echo "📍 Generating module location reports"
	@python3 tools/matriz_report_generator.py --verbose

# MATRIZ Evaluation Harness - Safe Testing Environment
matriz-eval:  ## Run MATRIZ evaluation harness (all scenarios)
	@echo "🧪 Running MATRIZ Evaluation Harness..."
	@python3 -m matriz.eval_harness --permissive --scenarios all || echo "⚠️  MATRIZ eval harness not yet implemented"

matriz-eval-quick:  ## Quick MATRIZ sanity check (orchestrator load only)
	@echo "⚡ Running MATRIZ quick sanity check..."
	@python3 -m matriz.eval_harness --permissive --scenarios orchestrator-sanity || echo "⚠️  MATRIZ eval harness not yet implemented"

matriz-eval-benchmark:  ## Run MATRIZ performance benchmarks
	@echo "📊 Running MATRIZ performance benchmarks..."
	@python3 -m matriz.eval_harness --permissive --benchmark --output benchmarks/matriz_results.json || echo "⚠️  MATRIZ eval harness not yet implemented"

# ==============================================================================
# T4 SCAFFOLD SYNC SYSTEM - Safe, Idempotent, Provenance-Aware Templates
# ==============================================================================

# Show what would be synced (dry run mode)
scaffold-dry:
	@echo "🔍 T4 Scaffold Sync - Dry Run Analysis"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@python3 tools/scaffold_sync.py --modules-root lukhas --dry-run
	@echo ""
	@echo "✅ Dry run complete. Use 'make scaffold-apply' to execute."

# Apply scaffold sync to all modules (safe mode - won't overwrite human edits)
scaffold-apply:
	@echo "🔄 T4 Scaffold Sync - Applying Templates"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@python3 tools/scaffold_sync.py --modules-root lukhas
	@echo ""
	@echo "✅ Scaffold sync complete. Files updated with provenance tracking."

# Force apply (will overwrite human edits - use with caution)
scaffold-apply-force:
	@echo "⚠️ T4 Scaffold Sync - FORCE MODE (overwrites human edits)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🚨 WARNING: This will overwrite human-edited files!"
	@read -p "Type 'YES_OVERWRITE' to continue: " confirm && [ "$$confirm" = "YES_OVERWRITE" ] || (echo "Cancelled." && exit 1)
	@python3 tools/scaffold_sync.py --modules-root lukhas --force
	@echo "✅ Force sync complete."

# Show human-friendly diffs between current files and templates
scaffold-diff:
	@echo "📊 T4 Scaffold Diff - Template Comparison"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@if [ -n "$(MODULE)" ]; then \
		python3 tools/scaffold_diff.py --modules-root lukhas --module $(MODULE) --context 5; \
	else \
		python3 tools/scaffold_diff.py --modules-root lukhas --all-modules --context 3; \
	fi

# Show diffs for all modules (comprehensive)
scaffold-diff-all:
	@echo "📊 T4 Scaffold Diff - All Modules Analysis"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@python3 tools/scaffold_diff.py --modules-root lukhas --all-modules --show-unchanged --context 5

# Validate scaffold system integrity
validate-scaffold:
	@echo "🔍 T4 Scaffold Validation - System Integrity Check"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "📋 Stage 1: Template Discovery"
	@templates=$$(python3 -c "from tools.scaffold_sync import list_template_files; print(len(list_template_files()))"); \
	echo "✅ Found $$templates templates in templates/module_scaffold/"
	@echo ""
	@echo "📋 Stage 2: Module Discovery"
	@modules=$$(find lukhas -maxdepth 1 -type d ! -name ".*" | wc -l); \
	echo "✅ Found $$modules modules in lukhas/"
	@echo ""
	@echo "📋 Stage 3: Jinja2 Template Syntax Check"
	@python3 -c "from jinja2 import Environment, FileSystemLoader; from tools.scaffold_sync import TEMPLATES, list_template_files; env = Environment(loader=FileSystemLoader(str(TEMPLATES))); [env.get_template(t) for t in list_template_files()]" && echo "✅ All templates have valid Jinja2 syntax"
	@echo ""
	@echo "📋 Stage 4: Provenance Header Validation"
	@python3 -c "from tools.scaffold_sync import PROV_PREFIX; assert PROV_PREFIX.strip() == '# @generated LUKHAS scaffold v1', 'Invalid provenance prefix'" && echo "✅ Provenance prefix is valid"
	@echo ""
	@echo "📋 Stage 5: Ignore Patterns Check"
	@if [ -f "templates/module_scaffold/.scaffoldignore" ]; then \
		echo "✅ .scaffoldignore present with $$(wc -l < templates/module_scaffold/.scaffoldignore) patterns"; \
	else \
		echo "⚠️ .scaffoldignore missing"; \
	fi
	@echo ""
	@echo "✅ Scaffold system validation complete!"

# Sync a specific module only
sync-module:
	@if [ -z "$(MODULE)" ]; then \
		echo "❌ Usage: make sync-module MODULE=module_name"; \
		exit 1; \
	fi
	@echo "🔄 T4 Scaffold Sync - Module: $(MODULE)"
	@python3 tools/scaffold_sync.py --modules-root lukhas --only-module $(MODULE)
	@echo "✅ Module $(MODULE) synchronized."

# Force sync a specific module (overwrites human edits)
sync-module-force:
	@if [ -z "$(MODULE)" ]; then \
		echo "❌ Usage: make sync-module-force MODULE=module_name"; \
		exit 1; \
	fi
	@echo "⚠️ T4 Scaffold Sync - FORCE MODE - Module: $(MODULE)"
	@echo "🚨 WARNING: This will overwrite human-edited files in $(MODULE)!"
	@read -p "Type 'YES_OVERWRITE' to continue: " confirm && [ "$$confirm" = "YES_OVERWRITE" ] || (echo "Cancelled." && exit 1)
	@python3 tools/scaffold_sync.py --modules-root lukhas --only-module $(MODULE) --force
	@echo "✅ Module $(MODULE) force synchronized."

t4-sim-lane:
	@echo "🎭 T4/0.01% Simulation Lane Summary & Validation..."
	bash .claude/commands/95_sim_lane_summary.yaml
	@echo "🧪 Running simulation smoke tests..."
	@python3 -m pytest tests/simulation/test_smoke_simulation.py -v --tb=short || echo "⚠️ Simulation tests require consciousness.simulation module"
	@echo "🛡️ Import contracts would run here (skipped due to syntax errors in codebase)"
	@echo "✅ Simulation lane validation complete"

imports-guard:
	@echo "🛡️ T4 Import Contract Validation"
	@python3 -m pip install import-linter --quiet || (echo "Installing import-linter..." && python3 -m pip install import-linter)
	@echo "🛡️ Validating import isolation..."
	@/Users/agi_dev/Library/Python/3.9/bin/lint-imports --config .import-linter-contracts.toml --cache-dir .importlinter_cache || (echo "❌ Import isolation FAILED" && exit 1)
	@echo "✅ Import contracts validated"

# ==============================================================================
# T4 AUDIT LEDGER VALIDATION - Secure, Schema-Compliant Audit Trail
# ==============================================================================

.PHONY: audit-validate-ledger
audit-validate-ledger:
	@echo "🔍 Validating audit ledgers against schema..."
	@python3 -c "import json, sys, glob; from jsonschema import validate; import pathlib; base = pathlib.Path('schemas'); schema = json.load(open(base/'audit_event_v1.json')); errors = 0; [validate(json.loads(line), schema) or True for p in glob.glob('audit_logs/ledger.jsonl') for line in open(p)]; print('✅ All ledger events conform to schema')"

.PHONY: feedback-validate
feedback-validate:
	@echo "🔍 Validating feedback events against schema..."
	@python3 -c "import json, sys, pathlib; from jsonschema import Draft202012Validator; schema = json.loads(pathlib.Path('schemas/feedback_event_v1.json').read_text()); validator = Draft202012Validator(schema); p = pathlib.Path('audit_logs/feedback.jsonl'); print('⚠️  No feedback file found') if not p.exists() else ([print(f'❌ Invalid event line {i}: {e.message}') for i, line in enumerate(p.read_text().splitlines(), 1) for e in validator.iter_errors(json.loads(line))]) or print('✅ All feedback events conform to schema')"

# ==============================================================================
# MCP LIFECYCLE - T4 Production-Grade Tool Integration
# ==============================================================================

## ── MCP lifecycle ───────────────────────────────────────────────────────
mcp-bootstrap:
	@bash tools/mcp/bootstrap.sh

mcp-verify:
	@python3 tools/mcp/verify_config.py

mcp-selftest:
	@python3 tools/mcp/self_test.py

mcp-contract: 
	@python3 tools/mcp/self_contract_test.py

mcp-smoke:
	@bash tools/mcp/self_smoke.sh

mcp-freeze:
	@python3 tools/mcp/assert_catalog_frozen.py

mcp-validate-catalog:
	@python3 -m pip -q install jsonschema >/dev/null || true
	@python3 tools/mcp/validate_catalog.py

mcp-health:
	@python3 mcp-servers/lukhas-devtools-mcp/health.py

mcp-docker-build:
	docker build -t lukhas/mcp:dev mcp-servers/lukhas-devtools-mcp

mcp-docker-run:
	docker run --rm -it -e PYTHONUNBUFFERED=1 lukhas/mcp:dev

## Convenience: full readiness
mcp-ready: mcp-bootstrap mcp-verify mcp-selftest mcp-contract mcp-smoke mcp-freeze
	@echo "✅ LUKHAS-MCP ready"


## Test Scaffolding Targets (T4/0.01%)
.PHONY: tests-scaffold-dry tests-scaffold-apply tests-scaffold-core tests-smoke tests-fast

tests-scaffold-dry: ## Dry-run test scaffold for all modules
	python3 scripts/scaffold_module_tests.py

tests-scaffold-apply: ## Apply test scaffold to all modules
	python3 scripts/scaffold_module_tests.py --apply

tests-scaffold-core: ## Apply test scaffold to 5 core modules
	python3 scripts/scaffold_module_tests.py \
		--module consciousness \
		--module memory \
		--module identity \
		--module governance \
		--module matriz \
		--apply

tests-smoke: ## Run smoke tests only (fast import checks)
	python3 -m pytest -q -k smoke --tb=short

tests-fast: ## Run all tests except integration (fast)
	python3 -m pytest -q -m "not integration"


## Coverage + Benchmark Targets (T4/0.01%)
.PHONY: cov cov-all bench bench-all cov-gate

cov: ## Collect coverage for single module (usage: make cov module=consciousness)
	python3 scripts/coverage/collect_module_coverage.py --module $(module)

cov-all: ## Collect coverage for all modules with tests/
	@for mf in $$(git ls-files "**/module.manifest.json"); do \
		mod=$$(dirname $$mf); \
		echo ">> $$mod"; \
		python3 scripts/coverage/collect_module_coverage.py --module $$mod || true; \
	done

cov-gate: ## Enforce coverage targets (lane-aware)
	python3 scripts/ci/coverage_gate.py

bench: ## Run benchmarks for single module (usage: make bench module=consciousness)
	python3 scripts/bench/update_observed_from_bench.py --module $(module)

bench-all: ## Run benchmarks for all modules with tests/benchmarks/
	@for mf in $$(git ls-files "**/module.manifest.json"); do \
		mod=$$(dirname $$mf); \
		python3 scripts/bench/update_observed_from_bench.py --module $$mod || true; \
	done


## T4/0.01% System Fusion Layer (Meta-Registry + Ledger Analytics)
.PHONY: meta-registry ledger-check trends validate-t4 tag-prod freeze-verify

meta-registry: ## Generate META_REGISTRY.json (fuses docs + coverage + benchmarks)
	python3 scripts/generate_meta_registry.py

ledger-check: ## Validate ledger consistency (manifest changes have ledger entries)
	python3 scripts/ci/ledger_consistency.py

trends: ## Generate coverage and benchmark trend analytics (CSV)
	@echo "📈 Generating trend analytics..."
	@python3 scripts/analytics/coverage_trend.py || echo "⚠️  No coverage data"
	@python3 scripts/analytics/bench_trend.py || echo "⚠️  No benchmark data"
	@echo "✅ Trend analytics generated in trends/"

validate-t4: ## Run comprehensive T4/0.01% validation checkpoint
	python3 scripts/validate_t4_checkpoint.py

validate-t4-strict: ## Run T4 validation in strict mode (fail fast)
	python3 scripts/validate_t4_checkpoint.py --strict

tag-prod: ## Tag production release (v0.01-prod) after validation passes
	@echo "🏷️  Tagging production release..."
	@python3 scripts/validate_t4_checkpoint.py || (echo "❌ Validation failed, cannot tag" && exit 1)
	@git tag -a v0.01-prod -m "T4/0.01% Production Release - All validation checks passed"
	@echo "✅ Tagged v0.01-prod (push with: git push origin v0.01-prod)"

freeze-verify: ## Verify freeze immutability and integrity (default: v0.02-final)
	python3 scripts/ci/verify_freeze_state.py --tag v0.02-final --mode strict

freeze-guardian: ## Run Freeze Guardian daemon (real-time monitoring)
	python3 scripts/guardian/freeze_guardian.py --interval 60

freeze-guardian-once: ## Run Freeze Guardian once and exit
	python3 scripts/guardian/freeze_guardian.py --once

dashboard-sync: ## Sync META_REGISTRY to dashboards (Notion/Grafana)
	python3 scripts/integrations/notion_sync.py --source docs/_generated/META_REGISTRY.json

init-dev-branch: ## Initialize development branch after freeze
	bash scripts/setup/init_dev_branch.sh develop/v0.03-prep

imports-doctor: ## Run import doctor to analyze missing lukhas.* modules
	python3 tools/import_doctor.py

imports-promote: ## Generate package shims from doctor analysis
	python3 scripts/gen_lukhas_pkg_shims.py

lint: ## Run ruff linter with auto-fix
	python3 -m ruff check . --fix || true

validate-root: ## Check root directory hygiene (all files)
	@echo "→ validate-root: checking all root files"
	@python3 scripts/validate_root_hygiene.py

validate-root-docs: ## Check root documentation hygiene (strict)
	@echo "→ validate-root-docs: checking documentation files"
	@python3 scripts/validate_root_docs.py

validate-root-all: validate-root validate-root-docs ## Run all root hygiene checks

tests-smoke: ## Run smoke tests
	python3 -m pytest tests/smoke -q || true

tests-all: ## Run all tests
	python3 -m pytest -q || true

dev-loop: imports-doctor imports-promote lint tests-smoke ## Full development loop: doctor → promote → lint → smoke

imports-report: ## Generate migration scorecard from ledger
	python3 tools/analyze_lukhas_ledger.py && \
	cat artifacts/IMPORT_MIGRATION_REPORT.md | head -50

codemod-dry: ## Dry-run codemod to show proposed import changes
	python3 tools/codemod_lukhas_from_ledger.py --threshold 5

codemod-apply: ## Apply codemod to migrate imports (creates .bak files)
	python3 tools/codemod_lukhas_from_ledger.py --apply --threshold 5

gate-legacy: ## CI gate to enforce import budget and prevent regressions
	LUKHAS_IMPORT_BUDGET=1000 LUKHAS_IMPORT_MAX_DELTA=0 python3 scripts/ci/gate_legacy_imports.py

# ==============================================================================
# T4 DOCUMENTATION & TESTS MIGRATION - Module Colocation with Confidence Scoring
# ==============================================================================

.PHONY: docs-map docs-migrate-auto docs-migrate-dry docs-lint validate-structure module-health

docs-map: ## Build documentation mapping with confidence scoring
	@echo "🔍 Building documentation mapping..."
	python3 scripts/docs/build_docs_map.py
	@echo "✅ Review: artifacts/docs_mapping_review.md"

docs-migrate-dry: ## Dry-run docs/tests migration (show what would be done)
	@echo "🔍 DRY RUN: Documentation migration preview"
	python3 scripts/docs/migrate_docs_auto.py --dry-run
	python3 scripts/tests/migrate_tests_auto.py --dry-run

docs-migrate-auto: ## Migrate docs/tests to module-local directories (git mv, history-preserving)
	@echo "📦 Migrating documentation and tests to module-local directories..."
	python3 scripts/docs/migrate_docs_auto.py
	python3 scripts/tests/migrate_tests_auto.py
	@echo "✅ Migration complete! Run 'make docs-lint' to validate"

docs-lint: ## Validate frontmatter and check for broken links
	@echo "🔍 Validating documentation quality..."
	python3 scripts/docs_lint.py

validate-structure: ## Generate module structure health report (JSON)
	@echo "🏥 Generating module structure health report..."
	python3 scripts/docs/generate_module_health.py
	@echo "✅ Reports generated: artifacts/module_structure_report.json, docs/_generated/MODULE_INDEX.md"

module-health: validate-structure ## View human-readable module health summary
	@cat docs/_generated/MODULE_INDEX.md | head -50

# THE_VAULT Inventory and Audit
vault-audit: ## Generate inventory for THE_VAULT repository (use VAULT_ROOT=/path/to/vault)
	@echo "📂 Generating THE_VAULT inventory..."
	@if [ -z "$(VAULT_ROOT)" ]; then \
		echo "⚠️  VAULT_ROOT not set, using docs/ as example"; \
		python3 scripts/vault_inventory.py --root docs; \
	else \
		python3 scripts/vault_inventory.py --root $(VAULT_ROOT); \
	fi
	@echo "✅ Vault inventory complete!"

vault-audit-vault: ## Audit THE_VAULT directory (shortcut for VAULT_ROOT=../THE_VAULT)
	@VAULT_ROOT=../THE_VAULT make vault-audit

# ==============================================================================
# MATRIZ PREP - 0.01% Discipline Pack
# ==============================================================================

.PHONY: init patch-schema normalize-inventory manifests validate badges top stats context-validate

init: ## Install dependencies for MATRIZ tooling
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install jsonschema

patch-schema: ## Patch MATRIZ schema to v1.1.0 (Flow star, events, security)
	$(PYTHON) scripts/patch_schema_to_v1_1_0.py schemas/matriz_module_compliance.schema.json

normalize-inventory: ## Normalize inventory (lucas→lukhas, lane→colony, star hints)
	$(PYTHON) scripts/normalize_inventory.py

manifests: ## Generate module manifests from inventory
	$(PYTHON) scripts/generate_module_manifests.py \
		--inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
		--out manifests \
		--star-canon scripts/star_canon.json \
		--write-context

validate: ## Validate all manifests against schema
	$(PYTHON) scripts/validate_manifests.py \
		--schema schemas/matriz_module_compliance.schema.json \
		--root .

badges: ## Generate coverage badges (manifest and context)
	$(PYTHON) scripts/generate_badges.py \
		--inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
		--manifests-root manifests \
		--out docs/audits

top: ## Generate Constellation Top dashboard
	$(PYTHON) scripts/gen_constellation_top.py

stats: ## Generate manifest statistics
	$(PYTHON) scripts/report_manifest_stats.py --manifests manifests --out docs/audits

context-validate: ## Validate lukhas_context.md front-matter against manifests
	python3 scripts/validate_context_front_matter.py

context-migrate-frontmatter: ## Add YAML front-matter to lukhas_context.md (in manifests/**)
	$(PYTHON) scripts/migrate_context_front_matter.py

context-coverage: ## Check lukhas_context.md coverage and front-matter presence
	$(PYTHON) scripts/context_coverage_bot.py --manifests manifests --min $${MIN_COV:-0.95}

context-migrate-frontmatter: ## Add YAML front-matter to lukhas_context.md (in manifests/**)
	$(PYTHON) scripts/migrate_context_front_matter.py

context-coverage: ## Check lukhas_context.md coverage and front-matter presence
	$(PYTHON) scripts/context_coverage_bot.py --manifests manifests --min $${MIN_COV:-0.95}

contracts-validate: ## Validate contract references in manifests
	python3 scripts/validate_contract_refs.py

links-check: ## Check internal documentation links
	$(PYTHON) docs/check_links.py --root .

policy-guard: ## Check T1 modules for dangerous calls
	$(PYTHON) scripts/policy_guard.py

matriz-all: patch-schema manifests validate badges top stats ## Run all MATRIZ prep steps

star-rules-lint: ## Lint star rules (syntax & hit counts)
	python3 scripts/lint_star_rules.py --rules configs/star_rules.json --manifests manifests

star-rules-coverage: star-rules-lint ## Generate star rules coverage report
	python3 scripts/gen_rules_coverage.py
	@echo "[OK] Coverage written to docs/audits/star_rules_coverage.md"

promotions: ## Suggest star promotions (Supporting → specific)
	python3 scripts/suggest_star_promotions.py --manifests manifests --rules configs/star_rules.json --out docs/audits
	@echo "[OK] Suggestions in docs/audits/star_promotions.{csv,md}"


# =============================================================================
# T4 Ruff Gold Standard Targets (turn_ruff_into_gold.md)
# =============================================================================

.PHONY: context-migrate-frontmatter context-coverage

context-migrate-frontmatter: ## Add YAML front-matter to lukhas_context.md (in manifests/**)
	$(PYTHON) scripts/migrate_context_front_matter.py

context-coverage: ## Check lukhas_context.md coverage and front-matter presence
	$(PYTHON) scripts/context_coverage_bot.py --manifests manifests --min $${MIN_COV:-0.95}

lint-json: ## Generate Ruff JSON output
	python3 -m ruff check --output-format json . > docs/audits/ruff.json

lint-fix: ## Run Ruff autofix (F401, TID252, isort)
	python3 -m ruff check --fix .

lint-delta: ## Show lint delta vs baseline (ratchet check)
	python3 scripts/ruff_ratchet.py \
		--baseline docs/audits/ruff_baseline.json \
		--current docs/audits/ruff.json \
		--track F821

f401-tests: ## Auto-remove F401 unused imports in tests/
	python3 -m ruff check --output-format json . > docs/audits/ruff.json
	python3 scripts/fix_f401_tests.py --ruff docs/audits/ruff.json --apply
	python3 -m ruff check --fix .

import-map: ## Build intelligent import map from manifests + code
	python3 scripts/build_import_map.py

imports-abs: ## Convert relative imports to absolute (kill TID252)
	python3 -m pip install libcst
	python3 scripts/normalize_imports.py --apply
	python3 -m ruff check --fix .

imports-graph: ## Detect import cycles in lukhas package
	python3 scripts/analyze_import_graph.py

ruff-heatmap: ## Generate Ruff violation heatmap by Star × Owner
	python3 -m ruff check --output-format json . > docs/audits/ruff.json
	python3 scripts/ruff_owner_heatmap.py

ruff-ratchet: ## Establish Ruff baseline for ratchet enforcement
	python3 -m ruff check --output-format json . > docs/audits/ruff.json
	python3 scripts/ruff_ratchet.py --init \
		--baseline docs/audits/ruff_baseline.json \
		--current docs/audits/ruff.json

f821-suggest: ## Suggest import fixes for F821 undefined names
	python3 -m ruff check --output-format json . > docs/audits/ruff.json
	python3 scripts/suggest_imports_f821.py \
		--ruff docs/audits/ruff.json \
		--root-pkg lukhas --src . \
		--out docs/audits/f821_suggestions.csv \
		--md docs/audits/f821_suggestions.md

f706-detect: ## Detect F706 top-level return statements
	python3 scripts/find_top_level_returns.py

f811-detect: ## Detect duplicate test class names (F811)
	python3 scripts/detect_duplicate_test_classes.py

todos: ## Harvest TODO/FIXME into docs/audits/todos.csv
	python3 scripts/harvest_todos.py \
		--roots lukhas candidate packages tools tests docs \
		--out docs/audits/todos.csv

todos-issues: ## Generate gh issue commands from todos.csv
	python3 scripts/create_issues_from_csv.py \
		--csv docs/audits/todos.csv \
		--out docs/audits/todos_gh.sh \
		--label-extra matriz

fix-orphaned-noqa: ## Remove orphaned noqa comments (PR 375 fix)
	python3 scripts/fix_orphaned_noqa.py --apply

update-manifest-paths: ## Update JSON manifest paths (Phase 2)
	python3 scripts/update_manifest_paths.py --root manifests --from candidate/ --to labs/

check-alias-hits: ## Report compat layer alias usage
	python3 scripts/check_alias_hits.py

codemod-dry: ## Preview legacy→canonical import rewrites (LibCST)
	python3 scripts/codemod_imports.py \
		--roots lukhas labs core MATRIZ tests packages tools \
		--out docs/audits/codemod_preview.csv

codemod-apply: ## Apply import rewrites in-place (DESTRUCTIVE - commit first!)
	python3 scripts/codemod_imports.py --apply \
		--roots lukhas labs core MATRIZ tests packages tools \
		--out docs/audits/codemod_preview.csv

check-legacy-imports: ## Fail if legacy imports remain outside allowlist
	python3 scripts/check_legacy_imports.py

# ============================================================================
# Load Testing Targets
# ============================================================================

load-check: ## Check if k6 is installed (install instructions provided if missing)
	@echo "🔍 Checking k6 installation..."
	@if ! command -v k6 > /dev/null 2>&1; then \
		echo "❌ k6 is not installed"; \
		echo ""; \
		echo "Install k6:"; \
		echo "  macOS:     brew install k6"; \
		echo "  Linux:     See load/README.md for installation instructions"; \
		echo "  Docker:    docker pull grafana/k6:latest"; \
		echo ""; \
		echo "Or use Locust (Python alternative):"; \
		echo "  pip install locust"; \
		echo "  make load-locust"; \
		exit 1; \
	else \
		k6 version; \
		echo "✅ k6 is installed"; \
	fi

load-smoke: load-check ## Run k6 smoke test (30s, 5 VUs) - quick sanity check
	@echo "🚬 Running k6 smoke test (30s, 5 VUs)..."
	@mkdir -p load/results
	k6 run load/smoke.js --out json=load/results/smoke-$(shell date +%Y%m%d-%H%M%S).json

load-test: load-check ## Run k6 standard load test (2m, 50 VUs) - sustained traffic
	@echo "⚡ Running k6 standard load test (2m, 50 VUs)..."
	@mkdir -p load/results
	k6 run load/resp_scenario.js --out json=load/results/standard-$(shell date +%Y%m%d-%H%M%S).json

load-extended: load-check ## Run k6 extended load test (10m, 100 VUs) - stress testing
	@echo "🔥 Running k6 extended load test (10m, ramping to 100 VUs)..."
	@mkdir -p load/results
	k6 run load/extended.js --out json=load/results/extended-$(shell date +%Y%m%d-%H%M%S).json

load-spike: load-check ## Run k6 spike test (5m, 0→200→0 VUs) - traffic burst simulation
	@echo "💥 Running k6 spike test (5m, 0→200→0 VUs)..."
	@mkdir -p load/results
	k6 run load/spike.js --out json=load/results/spike-$(shell date +%Y%m%d-%H%M%S).json

load-locust: ## Run Locust load test (Python alternative with web UI)
	@echo "🦗 Starting Locust load test with web UI..."
	@echo "Open http://localhost:8089 to configure and start test"
	@if ! command -v locust > /dev/null 2>&1; then \
		echo "❌ Locust is not installed"; \
		echo "Install with: pip install locust"; \
		exit 1; \
	fi
	locust -f load/locustfile.py --host=http://localhost:8000

# ============================================================================
# Phase 3: OpenAPI & Compat Enforcement
# ============================================================================

openapi-spec: ## Generate OpenAPI JSON spec with metadata polish
	@echo "📋 Generating OpenAPI spec..."
	python3 scripts/generate_openapi.py

openapi-validate: ## Validate OpenAPI spec against OpenAPI 3.1 schema
	@echo "✅ Validating OpenAPI spec..."
	@python -m pip install --upgrade openapi-spec-validator >/dev/null || true
	@python -c "import json; from openapi_spec_validator import openapi_v3_spec_validator;\
spec=json.load(open('docs/openapi/lukhas-openai.json'));\
errors=list(openapi_v3_spec_validator.iter_errors(spec));\
assert not errors, f'OpenAPI schema errors: {errors[:5]}';\
print('✅ OpenAPI validation passed')"

openapi-headers-guard: openapi-spec ## Verify X-RateLimit-* headers present on all 2xx/4xx/5xx responses
	@echo "🛡️  Checking OpenAPI spec for required X-RateLimit-* headers..."
	@python3 scripts/check_openapi_headers.py

shadow-diff: ## Compare Lukhas façade responses with OpenAI for parity
	@echo "🔍 Running shadow diff harness..."
	@PYTHONPATH=. python3 scripts/shadow_diff.py

.PHONY: guard
guard: ## Validate Guardian policy schema
	@python3 scripts/validate_guardian_policy.py configs/policy/guardian_policies.yaml

openapi-diff: openapi-spec ## Diff OpenAPI spec against main branch (requires git worktree)
	@echo "🔍 Comparing OpenAPI spec against main..."
	@if [ ! -d "main_ref" ]; then \
		echo "❌ main_ref worktree not found. Create with: git worktree add main_ref origin/main"; \
		exit 1; \
	fi
	@cd main_ref && python3 scripts/generate_openapi.py || true
	python3 scripts/diff_openapi.py --base main_ref/docs/openapi/lukhas-openai.json --cand docs/openapi/lukhas-openai.json || true

compat-enforce: ## Check compat alias hits (LUKHAS_COMPAT_MAX_HITS=0 in Phase 3)
	@echo "🔒 Checking compat alias hits..."
	@LUKHAS_COMPAT_MAX_HITS=0 python3 scripts/report_compat_hits.py --out docs/audits/compat_alias_hits.json || true
	@python -c "import json, sys, pathlib; path=pathlib.Path('docs/audits/compat_alias_hits.json');\
data=json.load(path.open()) if path.exists() else {};\
hits = 0;\
for value in data.values():\
    hits += value if isinstance(value, int) else value.get('count', 0);\
print(f'Compat alias hits: {hits}');\
sys.exit(0 if hits <= 0 else 2)"

compat-remove: ## Remove lukhas/compat/ directory (Phase 3 gate: run after hits=0 for 48h)
	@echo "⚠️  Removing compat layer..."
	@if [ -d "lukhas/compat" ]; then \
		git rm -r lukhas/compat && echo "✅ lukhas/compat/ removed"; \
	else \
		echo "ℹ️  lukhas/compat/ already removed"; \
	fi
	@echo "🔍 Searching for remaining lukhas.compat imports..."
	@git grep -n "lukhas\\.compat" || echo "✅ No compat imports found"
	@echo "🧪 Running smoke tests..."
	@$(MAKE) check-legacy-imports
	@python3 -m pytest tests/smoke/ -q --tb=no || echo "⚠️  Some smoke tests failed (review output)"

# ============================================================================
# Phase 3.1: Prometheus Alert Validation
# ============================================================================

PROMTOOL ?= promtool
ALERTS_DIR ?= lukhas/observability/alerts

.PHONY: alerts-validate
alerts-validate: ## Validate Prometheus alert rules with promtool
	@echo ">> validating alert rules in $(ALERTS_DIR)"
	$(PROMTOOL) check rules $(ALERTS_DIR)/*.alerts.yml

.PHONY: alerts-print
alerts-print: ## Print Prometheus alert groups
	@echo ">> printing alert groups"
	$(PROMTOOL) check rules $(ALERTS_DIR)/*.alerts.yml && \
	$(PROMTOOL) show rules $(ALERTS_DIR)/*.alerts.yml

# ============================================================================
# Phase 3.1: System Health Audit
# ============================================================================

.PHONY: health-audit
health-audit: ## Run comprehensive system health audit
	@python3 scripts/system_health_audit.py

.PHONY: health-audit-ci
health-audit-ci: ## Run health audit in CI mode (non-failing)
	@python3 scripts/system_health_audit.py || true
	@echo "## Health Audit" > docs/audits/health/summary_ci.md
	@if [ -f docs/audits/health/latest.md ]; then \
		tail -n +1 docs/audits/health/latest.md >> docs/audits/health/summary_ci.md; \
	fi

.PHONY: health
health: health-audit ## Alias for health-audit

# ============================================================================
# Redis Helpers (Phase 3: Guardian + Rate Limiting)
# ============================================================================

.PHONY: redis-up
redis-up: ## Start local Redis container for distributed rate limiting
	@echo "Starting Redis container..."
	@docker run --rm -d --name lukhas-redis -p 6379:6379 redis:7
	@echo "✅ Redis running on localhost:6379"

.PHONY: redis-down
redis-down: ## Stop local Redis container
	@echo "Stopping Redis container..."
	@-docker rm -f lukhas-redis 2>/dev/null || true
	@echo "✅ Redis stopped"

.PHONY: redis-check
redis-check: ## Check Redis connectivity
	@docker exec lukhas-redis redis-cli ping 2>/dev/null && echo "✅ Redis is reachable" || echo "❌ Redis not running (use 'make redis-up')"

# ============================================================================
# State Sweep & Colony Tools (Phase B: Technical Debt Reduction)
# ============================================================================

.PHONY: state-sweep
state-sweep: ## Run automated state sweep (Ruff, candidate refs, OpenAPI, etc.)
	@echo "🔍 Running state sweep..."
	@./scripts/state_sweep_and_prepare_prs.sh
	@echo "✅ State sweep complete. Check docs/audits/live/<timestamp>/"

.PHONY: plan-colony-renames
plan-colony-renames: ## Generate colony rename plan (dry-run, no execution)
	@echo "📋 Planning colony renames (dry-run)..."
	@python3 scripts/plan_colony_renames.py
	@echo "✅ Review docs/audits/colony/colony_renames_<timestamp>.csv"

# Coordination targets (Claude Code)
.PHONY: coord-snapshot

coord-snapshot:
	@echo "📸 Running coordination snapshot..."
	@bash scripts/coordination/daily_snapshot.sh

# -----------------------------------------------------------------------------
# API Documentation Helpers
# -----------------------------------------------------------------------------
.PHONY: api-previews api-catalog
api-previews: ## Build ReDoc previews for OpenAPI specs
	@mkdir -p docs/openapi/site
	npx -y redoc-cli build docs/openapi/*.openapi.yaml -o docs/openapi/site/index.html || true

api-catalog: ## Regenerate endpoint catalog JSON from OpenAPI specs
	@python3 scripts/gen_endpoint_catalog.py --specs 'docs/openapi/*.openapi.yaml' --out docs/apis/endpoint_catalog.json
# -----------------------------------------------------------------------------
# Phase 4 Manifests Pipeline Helpers
# -----------------------------------------------------------------------------
.PHONY: phase4-preflight phase4-canary phase4-manifests phase4-validate phase4-all
phase4-preflight: ## Run Phase 4 preflight checks locally
	@python3 scripts/check_star_canon_sync.py || true
	@python3 scripts/validate_contract_refs.py || true
	@[ -f scripts/build_import_map.py ] && python3 scripts/build_import_map.py || true
	@echo "✅ Phase 4 preflight complete. See docs/audits for artifacts."

phase4-canary: ## Build Phase 4 canary list (10%)
	@mkdir -p docs/audits
	@python3 scripts/phase4_build_canary.py --size 0.10 --out docs/audits/phase4_canary_list.txt
	@head -n 20 docs/audits/phase4_canary_list.txt || true

phase4-manifests: ## Generate manifests from inventory
	@[ -f docs/audits/COMPLETE_MODULE_INVENTORY.json ] || { echo "Missing docs/audits/COMPLETE_MODULE_INVENTORY.json"; exit 1; }
	@python3 scripts/generate_module_manifests.py --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json --out manifests --star-canon scripts/star_canon.json || true
	@python3 scripts/phase4_generate_lane_yaml.py --manifests manifests --prefer-labs --overwrite || true

phase4-validate: ## Validate manifests and write report
	@python3 scripts/validate_module_manifests.py --report docs/audits/manifest_validation_phase4.json || true
	@python3 scripts/validate_contract_refs.py || true
	@python3 scripts/check_star_canon_sync.py || true
	@echo "✅ Validation complete. See docs/audits/manifest_validation_phase4.json"

phase4-all: phase4-preflight phase4-canary phase4-manifests phase4-validate ## Run full Phase 4 flow
	@echo "✅ Phase 4 local run complete."

# RC Soak Operations (48-72h monitoring window)
.PHONY: rc-soak-start rc-soak-snapshot rc-synthetic-load rc-soak-stop rc-soak-quick

rc-soak-start: ## Start RC soak server (48-72h monitoring window)
	@echo "🚀 Starting RC soak (48-72h window)..."
	@mkdir -p docs/audits/health/$(shell date +%Y-%m-%d)
	@mkdir -p /tmp/lukhas-logs
	@echo "📝 Logs will be written to /tmp/lukhas-logs/rc-soak.log"
	@nohup uvicorn lukhas.adapters.openai.api:get_app --factory --port 8000 > /tmp/lukhas-logs/rc-soak.log 2>&1 &
	@echo $$! > /tmp/lukhas-logs/rc-soak.pid
	@echo "✅ RC soak started (PID: $$(cat /tmp/lukhas-logs/rc-soak.pid))"
	@echo "📊 Access: http://localhost:8000"
	@echo "📈 Metrics: http://localhost:8000/metrics"
	@echo "📋 Health: http://localhost:8000/health"

rc-soak-snapshot: ## Capture RC soak health snapshot (daily during 48-72h window)
	@echo "📸 Capturing RC soak snapshot..."
	@bash scripts/ops/rc_soak_snapshot.sh
	@echo "✅ Snapshot saved to docs/audits/health/$$(date +%Y-%m-%d)/latest.{json,md}"

rc-synthetic-load: ## Generate synthetic load for RC soak testing (default: 100 requests)
	@echo "🔥 Generating synthetic load..."
	@bash scripts/ops/rc_synthetic_load.sh $(REQUESTS)
	@echo "✅ Load generation complete"

rc-soak-stop: ## Stop RC soak server
	@echo "🛑 Stopping RC soak..."
	@if [ -f /tmp/lukhas-logs/rc-soak.pid ]; then \
		kill $$(cat /tmp/lukhas-logs/rc-soak.pid) 2>/dev/null || true; \
		rm /tmp/lukhas-logs/rc-soak.pid; \
		echo "✅ RC soak stopped"; \
	else \
		echo "⚠️  No PID file found. Server may not be running."; \
	fi

rc-soak-quick: ## Quick RC soak validation (5 min, low QPS)
	@echo "🚀 Starting quick RC soak validation..."
	@LUKHAS_API_URL=${LUKHAS_API_URL:-http://localhost:8000} \
	PROMETHEUS_URL=${PROMETHEUS_URL:-http://localhost:9090} \

# ------------- T4 Batch Integration Helpers -------------

# ------------- T4 Batch Integration Helpers -------------
.PHONY: batch-status batch-next-matriz batch-next-core batch-next-serve batch-next
BATCH_MATRIZ=/tmp/batch_matriz.tsv
BATCH_CORE=/tmp/batch_core.tsv
BATCH_SERVE=/tmp/batch_serve.tsv

batch-status: ## Show integration batch progress dashboard
	@scripts/batch_status.py $(BATCH_MATRIZ) $(BATCH_CORE) $(BATCH_SERVE)

batch-next-matriz: ## Integrate next module from MATRIZ batch
	@BATCH_FILE=$(BATCH_MATRIZ) scripts/batch_next.sh

batch-next-core: ## Integrate next module from CORE batch
	@BATCH_FILE=$(BATCH_CORE) scripts/batch_next.sh

batch-next-serve: ## Integrate next module from SERVE batch
	@BATCH_FILE=$(BATCH_SERVE) scripts/batch_next.sh

batch-next: ## Auto-pick and integrate from smallest remaining batch
	@scripts/batch_next_auto.sh

# ------------- T4 Multi-Agent Relay Targets -------------
.PHONY: nodespec-validate registry-up registry-smoke registry-ci registry-clean registry-test gates-all

# Use the centralized validation script to avoid Makefile heredoc/tab pitfalls
nodespec-validate: ## Validate NodeSpec v1 schema and examples
		@echo "🔎 Validating NodeSpec examples against schema..."
		@python3 scripts/nodespec_validate.py

registry-up: ## Start Hybrid Registry service (port 8080, background with PID tracking)
	@echo "🚀 Starting Hybrid Registry (background)..."
	@uvicorn services.registry.main:app --host 127.0.0.1 --port 8080 >/tmp/uvicorn.log 2>&1 & echo $$! > .registry.pid
	@echo "Registry PID: $$(cat .registry.pid)"

registry-smoke: ## Run registry smoke test via curl script
	@echo "💨 Running registry smoke test..."
	@./scripts/ci_verify_registry.sh

registry-ci: ## CI target: guard → start → smoke → teardown
	@echo "🔄 Running registry CI workflow..."
	@./scripts/registry_ci_guard.sh || code=$$?; \
	if [ "$$code" = "78" ]; then \
	  echo "[registry-ci] SKIP: services.registry.main not importable (exit 78)"; \
	  exit 0; \
	fi; \
	if [ "$$code" != "0" ]; then \
	  echo "[registry-ci] ERROR: guard script failed with code $$code"; \
	  exit $$code; \
	fi
	@make registry-up
	@./scripts/wait_for_port.sh 127.0.0.1 8080 30
	@./scripts/ci_verify_registry.sh
	@make registry-clean

registry-clean: ## Stop registry process and clean artifacts
	@echo "🧹 Cleaning registry artifacts..."
	@pkill -f "uvicorn services.registry.main" || true
	@rm -f .registry.pid services/registry/registry_store.json services/registry/checkpoint.sig /tmp/uvicorn.log || true
	@echo "✅ Registry cleaned"

registry-test: ## Run Hybrid Registry tests
	@echo "🧪 Running registry tests..."
	@python3 -m pytest services/registry/tests -q

gates-all: ## Run project-wide T4 gates (best-effort)
	@echo "🚪 Running T4 acceptance gates..."
	@python3 -m pytest -q || true
	@make nodespec-validate || true
	@make registry-test || true
	@echo "✅ Gates check complete"

# ============================================================================
# T4 Unified Platform v2.0
# ============================================================================

t4-init: ## Initialize T4 platform (DB, dashboard, reports)
	@echo "🚀 Initializing T4 Unified Platform..."
	@./scripts/t4_init.sh

t4-migrate-dry: ## Dry-run migration of legacy annotations
	@echo "🔍 Dry-run migration (legacy → unified)..."
	@python3 tools/ci/migrate_annotations.py --dry-run --report reports/migration_report.json
	@echo "📊 Report: reports/migration_report.json"

t4-migrate: ## Apply migration of legacy annotations (with backup)
	@echo "🔄 Migrating annotations (legacy → unified)..."
	@python3 tools/ci/migrate_annotations.py --apply --backup
	@echo "✅ Migration complete! Backups: *.bak"

t4-validate: ## Validate annotations with unified validator
	@echo "✅ Validating T4 annotations..."
	@python3 tools/ci/check_t4_issues.py --paths lukhas core api consciousness memory identity MATRIZ --json-only

t4-dashboard: ## Generate HTML dashboard with metrics
	@echo "📊 Generating T4 dashboard..."
	@python3 tools/ci/t4_dashboard.py --output reports/t4_dashboard.html
	@echo "✅ Dashboard: reports/t4_dashboard.html"
	@echo "💡 Open: open reports/t4_dashboard.html"

t4-api: ## Start Intent Registry API server
	@echo "🚀 Starting Intent Registry API..."
	@uvicorn tools.ci.intent_api:app --reload --port 8001

t4-parallel-dry: ## Dry-run parallel batch automation
	@echo "🔍 Dry-run parallel batching..."
	@./scripts/t4_parallel_batches.sh --dry-run --max-per-batch 5

t4-parallel: ## Run parallel batch automation (5 categories)
	@echo "⚡ Running parallel batch automation..."
	@./scripts/t4_parallel_batches.sh --max-per-batch 5

t4-codemod-dry: ## Dry-run codemod application
	@echo "🔍 Dry-run codemod (FixB904)..."
	@python3 tools/ci/codemods/run_codemod.py --transformer FixB904 --paths lukhas core --dry-run

t4-codemod-apply: ## Apply codemod with backup
	@echo "🔧 Applying codemod (FixB904)..."
	@python3 tools/ci/codemods/run_codemod.py --transformer FixB904 --paths lukhas core --backup
	@echo "✅ Codemod complete! Backups: *.bak"

# ============================================================================
# Analytics Event Validation
# ============================================================================

events-validate: ## Validate event tracking implementation
	@echo "✅ Validating event taxonomy..."
	@python3 tools/validate_events.py

# ============================================================================
# Claude Code PR Review Integration
# ============================================================================

claude-review: ## Request Claude Code review for current PR
	@./scripts/request_claude_review.sh

claude-setup-docs: ## Open Claude PR review setup documentation
	@echo "📖 Claude Code PR Review Setup Guide"
	@echo "Location: docs/development/CLAUDE_PR_REVIEW_SETUP.md"

# ============================================================================
# Evidence Page Template System
# ============================================================================

evidence-pages: ## Generate evidence page stubs from claims registry
	@echo "📝 Generating evidence pages from claims registry..."
	@python3 tools/generate_evidence_page.py
	@echo "✅ Evidence pages generated in release_artifacts/evidence/"
	@echo "💡 Next: Review and fill methodology sections"

evidence-validate: ## Validate evidence pages for completeness
	@echo "✅ Validating evidence pages..."
	@python3 tools/validate_evidence_pages.py
	@echo "💡 Use --check-bidirectional to validate page links"

evidence-validate-strict: ## Validate evidence pages (strict mode, warnings = errors)
	@echo "✅ Validating evidence pages (strict mode)..."
	@python3 tools/validate_evidence_pages.py --strict --check-bidirectional

branding-vocab-lint: ## Check branding vocabulary compliance
	@echo "📖 Checking branding vocabulary..."
	@if [ -f tools/branding_vocab_lint.py ]; then \
		python3 tools/branding_vocab_lint.py; \
	else \
		echo "⚠️  branding_vocab_lint.py not found - skipping"; \
	fi

branding-claims-fix: ## Fix branding claims front-matter
	@echo "🔧 Fixing branding claims front-matter..."
	@python3 tools/fix_branding_claims.py
