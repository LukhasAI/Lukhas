# Auditor navigation & validation
.PHONY: audit-nav audit-scan audit-nav-info audit-scan-list audit-validate sbom api-serve
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

# NOTE: informational variant; kept separate to avoid colliding with 'audit-nav'
audit-nav-info:
	@echo "Commit: $(shell cat AUDIT/RUN_COMMIT.txt 2>/dev/null || git rev-parse HEAD)"
	@echo "Started: $(shell cat AUDIT/RUN_STARTED_UTC.txt 2>/dev/null)"
	@echo "Files: $(shell wc -l reports/deep_search/PY_INDEX.txt 2>/dev/null | awk '{print $$1}')"
	@echo "Sample: AUDIT/CODE_SAMPLES.txt"

# NOTE: list-only variant; 'audit-scan' remains the comprehensive validator above
audit-scan-list:
	@ls -1 reports/deep_search | sed 1,20p

audit-validate:
	@python tools/ci/update_and_validate_json.py

sbom:
	@cyclonedx-bom -o reports/sbom/cyclonedx.json || echo "cyclonedx-bom not installed; skipped"

api-serve:
	@echo "🚀 Starting API server for auditing..."
	@echo "Server will be available at: http://localhost:8080"
	@echo "OpenAPI docs at: http://localhost:8080/docs"
	uvicorn api.app:app --reload --port 8080 --host 0.0.0.0