## HANDOFF A→B: Claude→GPT5 (Schema & CI)

**Artifact**: `docs/schemas/nodespec_schema.json` + examples (memory_adapter, dream_processor)

**Status**: ✅ Schema validates both examples locally

**Required for Agent B (GPT-5 Pro)**:
1. **Schema Audit**: Create `reports/schema_audit.md` covering:
   - Missing fields analysis (compare to T4 reference)
   - Lane/tier edge cases (0-7 tier boundaries, lane transition rules)
   - Extraplanetary fields sufficiency (DTN, checkpoint cadence, power budgets)
   - Compatibility rules (flat→nested conversion edge cases)
   - Test recommendations

2. **CI Integration**: Add CI job to validate NodeSpec examples
   - Job name: `nodespec-examples-validate`
   - Uses existing `make nodespec-validate` (or inline jsonschema)
   - Fails PR if validation fails

3. **Policy Notes**: Document lane/tier policy enforcement rules
   - How tier 0-7 maps to capability isolation
   - Which fields are required for each lane (candidate vs products)
   - GLYMPH/PQC field requirements by lane

**Deliverable**:
- `reports/schema_audit.md` (1-2 pages)
- `.github/workflows/nodespec-validate.yml` (or add job to t4-pr-ci.yml)
- Policy notes in audit report

**Validation Commands**:
```bash
# Local
make nodespec-validate

# Or directly
python3 - <<'PY'
import json, jsonschema
s=json.load(open('docs/schemas/nodespec_schema.json'))
for e in ['docs/schemas/examples/memory_adapter.json','docs/schemas/examples/dream_processor.json']:
  jsonschema.validate(json.load(open(e)), s)
print('✅ NodeSpec examples OK')
PY
```

**Next**: `HANDOFF B→C` after audit complete
