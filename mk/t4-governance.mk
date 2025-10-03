# T4/0.01% Governance & Quality System
# =====================================
#
# One-shot orchestration for T4 quality gates, reporting, and external visibility.
#
# Targets:
#   enrich          - Enrich all manifests with semantic data
#   registry        - Generate MODULE_REGISTRY.json
#   slo-report      - Generate SLO dashboard
#   backfill-notion - Backfill Notion multi-select options
#   sync-notion-dry - Dry-run Notion sync with diff preview
#   sync-notion     - Sync manifests to Notion
#   quality         - Run all CI quality gates
#   revert:last     - Revert last manifest changes from ledger

.PHONY: enrich registry slo-report backfill-notion sync-notion-dry sync-notion quality
.PHONY: validate-schema validate-vocab validate-queue validate-registry validate-slo
.PHONY: revert-last t4-help

# Main workflows
enrich:
	@echo "🔍 Enriching manifests..."
	python scripts/enrich_manifests.py

registry:
	@echo "📋 Generating MODULE_REGISTRY.json..."
	python scripts/generate_module_registry.py

slo-report:
	@echo "📊 Generating SLO dashboard..."
	python scripts/report_slo.py

backfill-notion:
	@echo "🔄 Backfilling Notion multi-select options..."
	python scripts/notion_backfill.py --features --tags --apply

sync-notion-dry:
	@echo "🔄 Notion sync (dry-run)..."
	python scripts/notion_sync.py --all --dry-run --report-md

sync-notion:
	@echo "🔄 Syncing to Notion..."
	python scripts/notion_sync.py --all --report-md

# Quality gates (CI)
validate-schema:
	@echo "✓ Schema validation..."
	@python3 scripts/ci/validate_schema.py

validate-vocab:
	@echo "✓ Vocabulary validation..."
	@python3 scripts/ci/validate_vocab.py

validate-queue:
	@echo "✓ Review queue validation..."
	@python3 scripts/ci/validate_review_queue.py

validate-registry:
	@echo "✓ Registry vs filesystem validation..."
	@python3 scripts/ci/registry_vs_fs.py

validate-slo:
	@echo "✓ SLO violations check..."
	@python3 scripts/ci/slo_gate.py

# All quality gates
quality: validate-schema validate-vocab validate-queue validate-registry validate-slo
	@echo ""
	@echo "✅ All T4/0.01% quality gates passed"

# Incident response
revert-last:
	@echo "⚠️  Reverting last manifest changes from ledger..."
	@echo "❌ Not yet implemented - manually restore from git or ledger"
	@echo "   See manifests/.ledger/*.ndjson for change history"

# Help
t4-help:
	@echo "T4/0.01% Governance System"
	@echo "=========================="
	@echo ""
	@echo "Workflows:"
	@echo "  make enrich              - Enrich manifests with semantic data"
	@echo "  make registry            - Generate MODULE_REGISTRY.json"
	@echo "  make slo-report          - Generate SLO dashboard"
	@echo "  make backfill-notion     - Backfill Notion options"
	@echo "  make sync-notion-dry     - Notion sync (dry-run)"
	@echo "  make sync-notion         - Sync to Notion"
	@echo ""
	@echo "Quality Gates:"
	@echo "  make quality             - Run all CI gates"
	@echo "  make validate-schema     - Schema validation"
	@echo "  make validate-vocab      - Vocab validation"
	@echo "  make validate-queue      - Review queue validation"
	@echo "  make validate-registry   - Registry vs FS validation"
	@echo "  make validate-slo        - SLO violation check"
	@echo ""
	@echo "Incident Response:"
	@echo "  make revert-last         - Revert last changes"
