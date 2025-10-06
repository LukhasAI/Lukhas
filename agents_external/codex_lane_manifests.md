---
status: wip
type: documentation
---
# Codex — Lane Manifests & CI Wiring

## Primary Task
For modules {guardian, orchestrator, memory, consciousness, identity}:
- Ensure each root has module.lane.yaml (lane=candidate unless promoted).
- Tag tests with lane markers; wire CI jobs to honor markers.
- Add artifacts/*_<module>_*validation*.json to promotion evidence.
- Verify import-linter passes; fix any upward imports.
Do not change runtime behavior.

**Output**: artifacts/{module}_lane_wiring_validation.json

## Specific Instructions

### Module Lane Manifest Requirements
```yaml
# module.lane.yaml template
name: lukhas.{module}
lane: candidate            # candidate | integration | production
owner: "@{module}-team"
slo:
  p95_ms:
    tick: 100
    reflect: 10
    decide: 50
    e2e: 250
gates:
  - unit_tests
  - integration_tests
  - perf_e2e
  - schema_guard
  - chaos_fail_closed
  - guardian_enforced
  - telemetry_contracts
  - import_hygiene
artifacts:
  - "artifacts/*{module}*.json"
```

### CI Wiring Requirements
- Add pytest markers: `@pytest.mark.lane("candidate")` or `@pytest.mark.lane("integration")`
- Wire CI job conditions based on lane markers
- Ensure promotion evidence artifacts are generated in `artifacts/` directory

### Import-Linter Validation
- Run `import-linter` to verify no upward lane imports
- candidate → integration: ❌ BLOCKED
- candidate → production: ❌ BLOCKED
- integration → production: ❌ BLOCKED

### Evidence Generation
Create validation artifact with structure:
```json
{
  "module": "lukhas.{module}",
  "validation_timestamp": "ISO8601",
  "lane_wiring": {
    "manifest_present": true,
    "ci_markers_added": true,
    "import_linter_passed": true
  },
  "artifacts_generated": [
    "artifacts/{module}_lane_wiring_validation.json"
  ]
}
```