# RFC-0010 — Dreams ↔︎ Flow Integration

**Goal:** Shift `/v1/dreams` out of stub; call Flow star module with constraints + seed; persist trace.
**Trace Contract (schema):**

```python
@dataclass
class DreamTrace:
    id: str
    model: str
    seed: str
    constraints: Dict[str, Any]
    steps: List[Dict[str, Any]]  # thought/action/observation frames
    duration_ms: int
```
