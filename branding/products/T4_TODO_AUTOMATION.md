# LUKHAS T4 TODO Automation Suite

The T4 TODO Automation Suite productizes the repository's evidence-first task governance into a branded offer for enterprise customers. It consolidates manifest generation, batch allocation, compliance enforcement, documentation, and orchestration telemetry so operations teams can scale TODO remediation with Constellation Framework discipline.

## Feature Pillars

### Manifest & Allocation Engine
- **Manifest Builder** parses structured markdown TODO sources, cross-checks live code, and enriches entries with TaskIDs, risk, and Constellation dimensions for a verifiable source of truth.【F:tools/ci/build_manifest.py†L3-L358】
- **Complete Allocation** turns manifest snapshots into ready-to-run agent packets with specialty focus, commit templates, and branch naming guidance for every unit of work.【F:tools/ci/complete_todo_allocation.py†L3-L220】
- **Batch Splitter v2** enforces Section 10 allocation ratios, priority routing, and domain expertise matching to keep Jules/Codex queues balanced against risk.【F:tools/ci/split_batches_v2.py†L3-L198】
- **Batch Locker** validates TaskID formats, branch naming, and batch sizing before changesets are declared ready, preventing drift across teams.【F:tools/ci/lock_batches.py†L198-L239】

### Compliance & Annotation Tools
- **Unused Import Validator** runs ruff F401 in production lanes and flags any lines missing the mandated `TODO[T4-UNUSED-IMPORT]` evidence tag, returning machine-readable audit results.【F:tools/ci/check_unused_imports_todo.py†L3-L197】
- **Unused Import Annotator** applies contextual reasons, header banners, and JSONL logging so conscious decisions to keep imports remain documented and reversible.【F:tools/ci/mark_unused_imports_todo.py†L3-L200】

### Documentation Automation
- **Autodoc Header Generator** scans target packages, synthesizes Constellation-aware module docstrings, and emits audit reports for content still awaiting canonical headers.【F:tools/autodoc_headers.py†L200-L320】

### Migration & Maintenance Utilities
- **Promotion Orchestrator** migrates candidate modules into the production namespace, rewrites imports, and ships transitional shims for dependent stacks.【F:tools/scripts/promote_module.py†L120-L199】
- **Duplicate Code Analyzer** and its generated cleanup script spotlight duplicated signatures while queuing consolidation follow-up tasks for manual review.【F:tools/cleanup/duplicate_code_analyzer.py†L288-L337】【F:tools/cleanup/cleanup_duplicates.py†L79-L92】
- **Fix-Later Stub Injector** standardizes placeholder entry points with explicit `TODO(symbol-resolver)` semantics so unfinished integrations remain traceable.【F:tools/fix_later_stubs.py†L60-L107】

### Branding Orchestration & Reporting
- **Elite Content Orchestrator** surveys fourteen content engines, measures voice coherence, and publishes executive reports that reinforce LUKHAS brand standards.【F:branding/orchestration/content_orchestrator.py†L1-L198】【F:branding/orchestration/content_orchestrator.py†L200-L360】
- **System Consolidator** unifies redundant systems into a single consciousness technology platform with logging, schema creation, and migration telemetry.【F:branding/orchestration/system_consolidator.py†L1-L200】
- **System Integrator** writes live integration modules that connect databases, content pipelines, and analytics so consolidated assets remain active.【F:branding/orchestration/system_integrator.py†L1-L200】
- **Comprehensive System Status Report** compiles health analytics, dependency scans, and performance metrics for stakeholders, flagging residual autofix TODOs as part of the roadmap.【F:tools/scripts/system_status_comprehensive_report.py†L1-L160】

## Operational Workflow
1. **Enumerate & Enrich** – Run the manifest builder to capture every TODO with hashes, risk signals, and Constellation categorization before handing work to agents.
2. **Allocate & Lock** – Generate agent-specific batches with the complete allocation tool, refine distribution via Splitter v2, and seal each packet through the locker to enforce T4 governance.
3. **Execute & Annotate** – During remediation, rely on the unused import validator/annotator pair and autodoc generator to keep evidence trails synchronized with coding activity.
4. **Migrate & Consolidate** – Use the promotion orchestrator, duplicate analyzer, and fix-later stubs to migrate modules safely while documenting future tasks.
5. **Report & Orchestrate** – Feed orchestration results and system reports into branding dashboards, ensuring voice coherence, consolidation progress, and system health remain visible to leadership.

## Branding Alignment & Roadmap
The suite anchors the LUKHAS promise of deterministic, Constellation-aligned execution by translating internal automation into a product line for partners seeking disciplined TODO governance. Upcoming releases will expand symbol-resolver implementations within the orchestrators, finalize the autofix backlog in the comprehensive status report, and introduce driftScore/affect_delta telemetry to the manifest pipeline so brand-state metrics stay observable end-to-end.
