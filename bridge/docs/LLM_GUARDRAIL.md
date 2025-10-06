---
module: bridge
title: LLM Guardrail Wrapper
type: documentation
---
# LLM Guardrail Wrapper

The `core.bridge.llm_guardrail` module wraps outbound language-model calls with JSON Schema enforcement.

## Usage

```python
from core.bridge import llm_guardrail

schema = {
    "type": "object",
    "properties": {"value": {"type": "number"}},
    "required": ["value"],
}

llm_guardrail.register_llm_callable(lambda prompt: {"value": 42})
response = llm_guardrail.call_llm("score", schema)
```

When `ENABLE_LLM_GUARDRAIL=1` (default), responses failing validation return `{"_rejected": True, "reason": "schema"}` and the downstream LLM is not engaged when schemas are malformed.

## Telemetry

The module tracks attempts, successes, denials, and an approximate p95 latency. Retrieve a snapshot via `llm_guardrail.get_guardrail_metrics()` to emit policy ledger entries for bridge routes.

## Extending

- Register the production LLM client with `register_llm_callable` once governance approves the connector.
- Replace the stub TODO with the actual invocation and thread the resulting payload through the existing schema guard.
- Add driftScore or affect_delta annotations if the wrapper begins to mutate symbolic context.
