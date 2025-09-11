# CI / CD and related helpers
.PHONY: ci-local monitor audit promote api-spec audit-status pc-all
ci-local:
	pytest -q --maxfail=1 --disable-warnings --cov=lukhas --cov-report=term
	python3 scripts/testing/smoke_check.py --json out/smoke.json || true
	uvicorn lukhas.api.app:app --port 8000 & echo $$! > .pid; sleep 2; \
	curl -s http://127.0.0.1:8000/openapi.json -o out/openapi.json; \
	kill `cat .pid` || true; rm -f .pid
	@echo 'Artifacts in ./out'

monitor:
	@echo "📊 Generating code quality report..."
	@python tools/scripts/quality_dashboard.py

audit:
	@bash -lc './scripts/audit.sh'

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

promote:
	@if [ -z "$(SRC)" ] || [ -z "$(DST)" ]; then \
		echo "Usage: make promote SRC=candidate/core/<mod> DST=lukhas/core/<mod> [SHIM=candidate->lukhas]"; \
		exit 2; \
	fi
	@python3 tools/scripts/promote_module.py --src $(SRC) --dst $(DST) $(if $(SHIM),--shim-direction $(SHIM),)

api-spec:
	@echo "Starting server to export OpenAPI spec..."
	@mkdir -p out
	@curl -s http://127.0.0.1:8000/openapi.json -o out/openapi.json
	@echo "OpenAPI spec exported to out/openapi.json"

pc-all:
	pre-commit run --all-files || true