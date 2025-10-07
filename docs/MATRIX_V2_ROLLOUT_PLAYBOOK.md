---
status: wip
type: documentation
owner: unknown
module: root
redirect: false
moved_to: null
---

# MATRIX v2 Rollout Playbook 🚀

This playbook defines the **operational steps** for rolling out Matrix Contracts v2 across all LUKHAS modules.
It bridges the gap between schema brilliance and everyday developer adoption.

## 📋 Quick Start Checklist

- [ ] Copy existing module contract template
- [ ] Generate telemetry fixtures from real module runs
- [ ] Add semconv smoke tests to test suite
- [ ] Wire OSV scanning into CI (with graceful fallback)
- [ ] Validate locally with `make validate-matrix`

## 🔧 Step-by-Step Commands

### 1. Bootstrap new module contract
```bash
make matrix-init MODULE=your.module.name
```

### 2. Generate telemetry fixtures from real runs
```bash
python3 tools/generate_telemetry_fixtures.py --module your.module.name --output telemetry/
```

### 3. Add telemetry smoke tests
```bash
# Copy template and customize for your module
cp tests/test_telemetry_semconv.py tests/test_telemetry_your_module.py
# Edit spans and metrics to match your module's contract
```

### 4. Validate locally before CI
```bash
make validate-matrix MODULE=your.module.name
python3 -m pytest tests/test_telemetry_your_module.py -v -m telemetry
```

### 5. Test OSV scanning (optional)
```bash
python3 tools/matrix_gate.py --pattern "your_module/matrix_*.json" --verbose --osv
```

### 6. Commit contract + fixtures
```bash
git add your_module/matrix_*.json telemetry/ tests/test_telemetry_your_module.py
git commit -m "feat(matrix): add contract + telemetry fixtures for your.module.name"
```

## ⚠️ Common Gotchas & Solutions

### OSV scanner segfaults on minimal SBOMs
**Problem:** OSV-scanner crashes on CycloneDX BOMs with no dependencies
**Solution:** Add at least one dependency entry to CycloneDX SBOM
**Fallback:** Graceful degradation mode logs alerts instead of failing CI

### Semconv drift across OpenTelemetry versions
**Problem:** Span attributes don't match required semantic conventions
**Solution:** Pin `opentelemetry_semconv_version` in contract and validate with smoke tests
**Check:** Run `pytest -m telemetry` to catch drift early

### CI timeout on large PRISM models
**Problem:** Statistical model checking takes too long in CI
**Solution:** Start with report-only mode, tighten to hard gates once stable
**Command:** `prism --report-only models/your_module.pm`

### Missing telemetry in production spans
**Problem:** Real spans don't have attributes specified in contract
**Solution:** Use contract as source of truth, add attributes to instrumentation code
**Validate:** Smoke tests will catch missing semconv attributes

## 🚦 Rollout Stages

### Week 1: Core Modules
- [ ] `memory` - fold-based recall system
- [ ] `identity` - authentication and λID system
- [ ] `consciousness` - awareness and emergence patterns

### Week 2: Integration Modules
- [ ] `api` - REST/GraphQL endpoints
- [ ] `orchestration` - multi-AI workflows
- [ ] `governance` - ethics and safety systems

### Week 3: Peripheral Modules
- [ ] `adapters` - external service integrations
- [ ] `monitoring` - observability and metrics
- [ ] `quantum` - quantum-inspired algorithms

## 🔍 Success Metrics

### Zero Fragility
- ✅ **Zero CI failures** due to OSV tool crashes (graceful fallback confirmed)
- ✅ **No flaky tests** from quantitative thresholds (existence checks only)
- ✅ **Deterministic validation** across all environments

### Quality Gates Working
- ✅ **100% semconv compliance** on new spans/metrics
- ✅ **OSV high-severity gate** catching real vulnerabilities in SBOMs
- ✅ **Schema validation** preventing contract drift

### Developer Experience
- ✅ **Sub-5-minute** local validation cycle
- ✅ **Clear error messages** when gates fail
- ✅ **Copy-paste commands** that work out of the box

## 🎯 Cultural Rule

**No PR merges if:**
- OSV High > 0 (when scanner succeeds)
- Telemetry semconv attributes missing
- Matrix contracts out of sync with implementation

**Graceful degradation allowed, silent failure never.**

## 📈 Future v2 Enhancements

### Phase 3: Stochastic Verification
- **PRISM integration** → probabilistic property verification
- Start report-only, graduate to merge-blocking gates
- Target: memory cascade prevention ≥ 99.7% confidence

### Phase 4: Tamper-Evident History
- **IPLD CAR generation** → content-addressed provenance
- Each contract evaluation → tamper-evident CAR root CID
- Enables audit trails and "happens-before" reasoning

### Phase 5: Runtime Attestation
- **RATS/EAT verifier** → runtime attestation validation
- Extend beyond CI/CD into production guarantees
- Policy checks → log mode → hard runtime gates

## 🛠️ Helper Scripts

### Matrix Operations
```bash
# Initialize new module contract
make matrix-init MODULE=new.module

# Validate all contracts
make validate-matrix

# Validate specific module
make validate-matrix MODULE=memory

# Run with OSV scanning
make validate-matrix-osv
```

### Telemetry Operations
```bash
# Generate fixtures from instrumented runs
make telemetry-fixtures MODULE=memory

# Test semconv compliance
make telemetry-test MODULE=memory

# Test all telemetry smoke tests
make telemetry-test-all
```

## 🔧 Troubleshooting

### Contract validation fails
```bash
# Check schema compliance
jsonschema -i your_module/matrix_*.json schemas/matrix.schema.json

# Debug with Python
python3 tools/matrix_gate.py --pattern "your_module/matrix_*.json" --verbose
```

### Telemetry smoke tests fail
```bash
# Check fixture exists
test -f telemetry/your_module_spans.json

# Validate fixture structure
python3 -c "import json; print(json.load(open('telemetry/your_module_spans.json')))"

# Run single test with verbose output
pytest tests/test_telemetry_your_module.py::test_spans_exist -v
```

### OSV scan issues
```bash
# Test SBOM validity
cyclonedx validate --input-file sbom/your_module.cdx.json

# Manual OSV scan
osv-scanner --sbom sbom/your_module.cdx.json --format json

# Check fallback behavior
python3 tools/matrix_gate.py --osv --verbose 2>&1 | grep ALERT
```

## 📚 Reference Links

- [JSON Schema 2020-12 Spec](https://json-schema.org/draft/2020-12/schema)
- [OpenTelemetry Semantic Conventions v1.37.0](https://opentelemetry.io/docs/specs/semconv/)
- [CycloneDX SBOM Specification v1.5](https://cyclonedx.org/specification/overview/)
- [OSV Scanner Documentation](https://osv.dev/docs/)
- [RATS/EAT Attestation RFC 9334](https://datatracker.ietf.org/doc/rfc9334/)

## 🤝 Getting Help

1. **Check existing contracts** in `memory/`, `identity/`, `consciousness/` for examples
2. **Run validation locally** before opening PRs
3. **Check CI logs** for specific gate failures and OSV alerts
4. **Review smoke test failures** for missing telemetry attributes

---

**Remember:** Matrix v2 is designed for operational resilience. Trust the fallback logic, but investigate alerts promptly. Quality gates should feel like guardrails, not obstacles.