# MATRIZ Evaluation Harness

**Document Status**: Production Ready  
**Last Updated**: 2025-10-16  
**Maintainer**: LUKHAS AI Team  

---

## Overview

The MATRIZ Evaluation Harness provides a safe, controlled environment for testing MATRIZ orchestrator integration without risking production systems. It enables validation of symbolic processing, bounded trace generation, and schema compliance.

### Purpose

- **Safe Testing**: Run MATRIZ in permissive mode without production impact
- **Validation**: Verify orchestrator behavior with fixed prompts
- **Schema Compliance**: Ensure outputs match expected formats
- **Performance Baseline**: Establish latency and token usage benchmarks

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ MATRIZ Evaluation Harness                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────┐ │
│  │ Test Fixtures│───>│ Orchestrator │───>│ Validator   │ │
│  │              │    │              │    │             │ │
│  │ - Fixed      │    │ - Permissive │    │ - Schema    │ │
│  │   Prompts    │    │   Mode       │    │ - Bounds    │ │
│  │ - Scenarios  │    │ - Bounded    │    │ - Output    │ │
│  │              │    │   Traces     │    │             │ │
│  └──────────────┘    └──────────────┘    └─────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Safety Guardrails                                    │ │
│  │ - Max Token Limits                                   │ │
│  │ - Timeout Protection                                 │ │
│  │ - No External API Calls                              │ │
│  │ - Read-Only File System                              │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Safety Guarantees

### Permissive Mode

The harness runs MATRIZ in **permissive mode** which ensures:

1. **No Production Impact**: Isolated from live systems
2. **Deterministic**: Fixed inputs produce consistent outputs
3. **Bounded**: Token limits prevent runaway generation
4. **Observable**: All traces logged for inspection

### Guardrails

| Guardrail | Default | Purpose |
|-----------|---------|---------|
| Max Tokens | 2048 | Prevent excessive generation |
| Timeout | 30s | Avoid hanging tests |
| API Calls | Disabled | No external dependencies |
| File Write | Disabled | Read-only execution |

---

## Usage

### Quick Start

```bash
# Run evaluation harness
make matriz-eval

# Run specific scenario
make matriz-eval SCENARIO=orchestrator-sanity

# Run with verbose output
make matriz-eval VERBOSE=1
```

### Python API

```python
from matriz.eval_harness import EvalHarness, Scenario

# Initialize harness
harness = EvalHarness(
    permissive=True,
    max_tokens=2048,
    timeout=30
)

# Define test scenario
scenario = Scenario(
    name="orchestrator-basic",
    prompt="Analyze this cognitive pattern: consciousness emerges from complexity",
    expected_schema="matriz.schemas.CognitiveAnalysis",
    expected_bounds={"tokens": (100, 500), "latency_ms": (0, 5000)}
)

# Run evaluation
result = harness.evaluate(scenario)

# Validate results
assert result.schema_valid, f"Schema mismatch: {result.schema_errors}"
assert result.within_bounds, f"Bounds violated: {result.bounds_report}"
assert result.trace_complete, f"Incomplete trace: {result.trace_status}"
```

---

## Test Scenarios

### Scenario 1: Orchestrator Load

**Purpose**: Verify orchestrator initializes and processes basic requests.

```python
scenario = Scenario(
    name="orchestrator-load",
    prompt="Hello MATRIZ",
    expected_schema="matriz.schemas.SimpleResponse",
    expected_bounds={"tokens": (1, 100), "latency_ms": (0, 1000)}
)
```

**Success Criteria**:
- ✅ Orchestrator loads without errors
- ✅ Response generated within 1s
- ✅ Output matches SimpleResponse schema
- ✅ Token count < 100

### Scenario 2: Fixed Prompt Validation

**Purpose**: Test deterministic behavior with fixed prompts.

```python
fixed_prompts = [
    "Analyze symbolic pattern: ⚛️🧠🛡️",
    "Generate consciousness trace for: identity formation",
]

for prompt in fixed_prompts:
    scenario = Scenario(
        name=f"fixed-prompt-{hash(prompt)}",
        prompt=prompt,
        expected_schema="matriz.schemas.SymbolicAnalysis",
        expected_bounds={"tokens": (50, 300), "latency_ms": (0, 3000)}
    )
    result = harness.evaluate(scenario)
    assert result.schema_valid
```

**Success Criteria**:
- ✅ All prompts complete successfully
- ✅ Outputs are deterministic (same prompt → same output)
- ✅ Schema validation passes
- ✅ Latency within bounds

### Scenario 3: Bounded Trace Generation

**Purpose**: Verify traces are bounded and don't exhibit runaway behavior.

```python
scenario = Scenario(
    name="bounded-trace",
    prompt="Generate deep analysis with maximum detail",
    expected_schema="matriz.schemas.DeepAnalysis",
    expected_bounds={"tokens": (100, 2048), "latency_ms": (0, 30000)},
    max_tokens=2048  # Hard limit
)
```

**Success Criteria**:
- ✅ Trace stops at max_tokens limit
- ✅ Output is well-formed (no truncation mid-sentence)
- ✅ No timeout errors
- ✅ Memory usage < 500MB

---

## Schema Validation

### Supported Schemas

| Schema | Purpose | Fields |
|--------|---------|--------|
| `SimpleResponse` | Basic text responses | `text`, `tokens`, `latency_ms` |
| `SymbolicAnalysis` | Symbolic pattern analysis | `pattern`, `interpretation`, `confidence` |
| `CognitiveAnalysis` | Consciousness patterns | `state`, `coherence`, `trace` |
| `DeepAnalysis` | Complex reasoning | `reasoning`, `conclusions`, `evidence` |

### Custom Validation

```python
from matriz.eval_harness import SchemaValidator

# Define custom schema
class CustomSchema:
    required_fields = ["output", "metadata"]
    optional_fields = ["trace", "diagnostics"]
    
    @staticmethod
    def validate(data):
        # Custom validation logic
        return all(field in data for field in CustomSchema.required_fields)

# Register schema
SchemaValidator.register("custom", CustomSchema)

# Use in scenario
scenario = Scenario(
    name="custom-test",
    prompt="Test custom schema",
    expected_schema="custom"
)
```

---

## Performance Benchmarks

### Expected Performance

| Scenario | Tokens | Latency (p50) | Latency (p95) | Memory |
|----------|--------|---------------|---------------|--------|
| Orchestrator Load | 10-50 | 100ms | 500ms | 50MB |
| Fixed Prompt | 50-300 | 500ms | 2s | 100MB |
| Bounded Trace | 500-2048 | 5s | 15s | 300MB |

### Performance Regression Detection

```python
# Run benchmarks
results = harness.run_benchmarks()

# Check for regressions
baseline = harness.load_baseline("benchmarks/baseline.json")
regressions = harness.detect_regressions(results, baseline, threshold=1.2)

if regressions:
    print(f"⚠️ Performance regressions detected: {regressions}")
    # Alert or fail CI
```

---

##  Safety Notes

### ⚠️ Important Warnings

1. **Permissive Mode Only**: Never run eval harness in production mode
2. **Resource Limits**: Always set max_tokens and timeout
3. **No External APIs**: Disable all external service calls
4. **Read-Only**: File system must be read-only
5. **Isolation**: Run in sandboxed environment (Docker recommended)

### Security Considerations

- **No PII**: Avoid using real user data in test scenarios
- **Synthetic Data**: Use generated/mocked data only
- **Audit Logs**: All evaluations logged for security review
- **Access Control**: Limit who can run evaluations

---

## Makefile Integration

Add to `Makefile`:

```makefile
.PHONY: matriz-eval
matriz-eval:  ## Run MATRIZ evaluation harness
	@echo "🧪 Running MATRIZ Evaluation Harness..."
	python3 -m matriz.eval_harness --permissive --scenarios all

.PHONY: matriz-eval-quick
matriz-eval-quick:  ## Quick MATRIZ sanity check
	@echo "⚡ Running MATRIZ quick sanity check..."
	python3 -m matriz.eval_harness --permissive --scenarios orchestrator-sanity

.PHONY: matriz-eval-benchmark
matriz-eval-benchmark:  ## Run MATRIZ performance benchmarks
	@echo "📊 Running MATRIZ performance benchmarks..."
	python3 -m matriz.eval_harness --permissive --benchmark --output benchmarks/results.json
```

---

## Troubleshooting

### Common Issues

**Issue**: `Orchestrator fails to load`  
**Solution**: Check MATRIZ dependencies installed: `pip install -r requirements.txt`

**Issue**: `Schema validation fails`  
**Solution**: Verify schema version matches: `python3 -m matriz.schemas --version`

**Issue**: `Timeout errors`  
**Solution**: Increase timeout or reduce max_tokens: `--timeout 60`

**Issue**: `Bounded trace exceeds limits`  
**Solution**: Lower max_tokens or check for infinite loops

---

## Integration with CI/CD

### GitHub Actions

```yaml
name: MATRIZ Evaluation

on: [pull_request]

jobs:
  matriz-eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run MATRIZ Eval
        run: make matriz-eval
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: matriz-eval-results
          path: matriz_eval_results.json
```

---

## References

- [MATRIZ Architecture](../arquitectura/MATRIZ_ARCHITECTURE.md)
- [Orchestrator Documentation](../api/ORCHESTRATOR_API.md)
- [Schema Definitions](../schemas/MATRIZ_SCHEMAS.md)
- [Safety Guidelines](../security/SAFETY_GUIDELINES.md)

---

## Changelog

### 2025-10-16
- Initial documentation created
- Added orchestrator sanity tests
- Documented bounded trace validation
- Added schema compliance checks

---

**Contact**: If you encounter issues or have questions, reach out to the LUKHAS AI team or file an issue on GitHub.
