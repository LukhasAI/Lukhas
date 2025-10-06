---
status: wip
type: documentation
---
# Audit Entry Point
- Commit: $(cat RUN_COMMIT.txt 2>/dev/null)
- Started: $(cat RUN_STARTED_UTC.txt 2>/dev/null)

## Where to start
- Code indexes: reports/deep_search/PY_INDEX.txt
- Import samples: reports/deep_search/IMPORT_SAMPLES.txt
- File sizes (top): reports/deep_search/SIZES_TOP.txt
- Top importers: reports/deep_search/TOP_IMPORTERS.txt
- Hotspots: reports/deep_search/HOTSPOTS.txt
- Cross-lane: reports/deep_search/CANDIDATE_USED_BY_LUKHAS.txt
- Wrong core imports: reports/deep_search/WRONG_CORE_IMPORTS.txt
- Random code sample: AUDIT/CODE_SAMPLES.txt

## Extended indexes
- Symbols: reports/deep_search/SYMBOLS_INDEX.tsv
- Classes: reports/deep_search/CLASSES_INDEX.txt
- Functions: reports/deep_search/FUNCTIONS_INDEX.txt
- Module map (JSON): reports/deep_search/MODULE_MAP.json
- Import graph (DOT): reports/deep_search/IMPORT_GRAPH.dot
- API endpoints: reports/deep_search/API_ENDPOINTS.txt
- Tests: reports/deep_search/TEST_INDEX.txt
- TODO/FIXME: reports/deep_search/TODO_FIXME_INDEX.txt
- Lane map: reports/deep_search/LANE_MAP.txt
- Package map: reports/deep_search/PACKAGE_MAP.txt

## Master JSON Artifacts (reference)
- LUKHAS_ARCHITECTURE_MASTER.json
- DEPENDENCY_MATRIX.json
- SECURITY_ARCHITECTURE.json
- CONSCIOUSNESS_METRICS.json
- PERFORMANCE_BASELINES.json
- BUSINESS_METRICS.json
- EVOLUTION_ROADMAP.json
- VISUALIZATION_CONFIG.json

## Notes
Treat reports as hints only. Always corroborate with file and line numbers.
