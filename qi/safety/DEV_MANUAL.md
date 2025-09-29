# LUKHΛS Safety & Compliance Developer Manual

## Architecture Overview

The QI Safety module implements a multi-layered defense system:

```
┌─────────────────────────────────────────┐
│          Application Layer              │
├─────────────────────────────────────────┤
│            TEQ Gate                     │ ← Policy enforcement point
├─────────────────────────────────────────┤
│   Risk Overlays │ Consent │ Provenance │ ← Compliance modules
├─────────────────────────────────────────┤
│     Policy Packs │ Fuzzer │ CI Runner  │ ← Testing & validation
└─────────────────────────────────────────┘
```

## Module Architecture

### 1. Policy Mutation Fuzzer (`policy_mutate.py`)

**Core Components:**
```python
# Deterministic fuzzing engine
def fuzz(
    policy_root: str,
    jurisdiction: str,
    task: str,
    n: int,
    seed: int,
    corpus_path: str,
    context_base: Dict[str, Any],
    require_block_kinds: List[str]
) -> Dict[str, Any]
```

**Data Flow:**
1. Load corpus (YAML) → seeds + attacks
2. Generate mutations deterministically (seed-based RNG)
3. Run each through TEQ gate
4. Track improper passes
5. Return structured report

**Extension Points:**
- Add attack types in `policy_corpus.yaml`
- Custom placeholders for dynamic content
- New task definitions with specific seeds

### 2. Risk Orchestrator Overlays (`orchestrator_overlays.py`)

**Core Classes:**
```python
class OverlaySchema(BaseModel):
    version: str
    global_policies: Dict[str, Any]
    jurisdictions: Dict[str, Dict[str, Any]]
    contexts: Dict[str, Dict[str, Any]]

class RiskOverlayManager:
    def get_policies(jurisdiction, context) -> Dict
    def hot_reload() -> None
    def _deep_merge(base, override) -> Dict
```

**Merge Algorithm:**
```python
# Hierarchical deep merge
result = global_policies
if jurisdiction:
    result = deep_merge(result, jurisdictions[jurisdiction])
if context:
    result = deep_merge(result, contexts[context])
```

**Thread Safety:**
- Uses `threading.Lock()` for concurrent access
- Immutable snapshots per request
- Atomic hot-reload operations

### 3. Consent Ledger (`consent_ledger.py`)

**Storage Layout:**
```
~/.lukhas/state/consent/
├── consent_ledger.jsonl  # Append-only event log
├── consent_index.json    # Fast lookup index
└── [temp files]          # Atomic write operations
```

**Cryptographic Flow:**
```python
# Signing process
steps = [consent_data, details, metadata]
merkle_chain = build_merkle(steps)
attestation = ed25519_sign(merkle_chain)
receipt = {
    "chain_path": path,
    "signature_b64": sig,
    "public_key_b64": pk,
    "root_hash": hash
}
```

**Index Structure:**
```json
{
  "user_id": {
    "purpose": {
      "ts": 1234567890,
      "fields": ["field1", "field2"],
      "duration_days": 365,
      "meta": {}
    }
  }
}
```

**Fan-out Implementation:**
```python
# Best-effort async notification
if WEBHOOK_URL:
    requests.post(url, json=event, timeout=2)
if KAFKA_BROKERS:
    producer.send(topic, key=event_id, value=event)
```

### 4. TEQ Gate Integration

**Fresh Consent Check:**
```python
def _require_fresh_consent(
    self,
    ctx: Dict[str, Any],
    *,
    purpose: str,
    user_key: str = "user_id",
    require_fields: list[str],
    within_days: int = 365
):
    from qi.memory.consent_ledger import is_allowed
    # Extract user, check consent, return TEQ tuple
```

**Check Registration:**
```python
# In _check_one method
if kind == "require_fresh_consent":
    return self._require_fresh_consent(...)
```

## Integration Patterns

### 1. Adding New Policy Checks

```python
# Step 1: Add to TEQ dispatcher
if kind == "your_check":
    return self._your_check(ctx, **chk)

# Step 2: Implement check method
def _your_check(self, ctx, param1, param2):
    # Validation logic
    if not valid:
        return (False, "Error message", "Remediation")
    return (True, "", "")

# Step 3: Add to policy mappings
tasks:
  your_task:
    - kind: your_check
      param1: value1
      param2: value2
```

### 2. Extending Consent System

```python
# Custom consent validator
def validate_custom_consent(user, purpose, custom_field):
    from qi.memory.consent_ledger import _read_index
    ix = _read_index()
    consent = ix.get(user, {}).get(purpose, {})
    # Custom validation logic
    return is_valid

# Integration with TEQ
def _require_custom_consent(self, ctx, **kwargs):
    valid = validate_custom_consent(...)
    if not valid:
        return (False, "Custom consent failed", "Action needed")
    return (True, "", "")
```

### 3. Policy Overlay Plugins

```python
# Custom overlay source
class CustomOverlaySource:
    def load_policies(self) -> Dict:
        # Load from database, API, etc.
        return policies

# Integration
from qi.risk.orchestrator_overlays import RiskOverlayManager

class ExtendedOverlayManager(RiskOverlayManager):
    def __init__(self, overlay_dir, custom_source):
        super().__init__(overlay_dir)
        self.custom = custom_source

    def get_policies(self, **kwargs):
        base = super().get_policies(**kwargs)
        custom = self.custom.load_policies()
        return self._deep_merge(base, custom)
```

## Testing Strategies

### 1. Unit Testing Consent

```python
import pytest
from qi.memory.consent_ledger import record, is_allowed, revoke

def test_consent_lifecycle():
    # Grant
    evt = record("user1", "purpose1", ["field1"], 30)
    assert evt.kind == "grant"

    # Check
    assert is_allowed("user1", "purpose1", require_fields=["field1"])

    # Revoke
    evt = revoke("user1", "purpose1")
    assert evt.kind == "revoke"

    # Verify revoked
    assert not is_allowed("user1", "purpose1")
```

### 2. Integration Testing TEQ

```python
def test_fresh_consent_enforcement():
    from qi.safety.teq_gate import TEQCoupler

    gate = TEQCoupler(policy_dir="test_policies")
    ctx = {
        "user_profile": {"user_id": "test_user"},
        "text": "test query"
    }

    # Should fail without consent
    result = gate.run(task="personalize_reply", context=ctx)
    assert not result.allowed

    # Grant consent
    record("test_user", "personalization", ["style_weights"], 30)

    # Should pass with consent
    result = gate.run(task="personalize_reply", context=ctx)
    assert result.allowed
```

### 3. Fuzzing Test Harness

```python
def test_deterministic_fuzzing():
    from qi.safety.policy_mutate import fuzz

    # Run twice with same seed
    result1 = fuzz(
        policy_root="policies",
        jurisdiction="global",
        task="test_task",
        n=10,
        seed=42
    )

    result2 = fuzz(
        policy_root="policies",
        jurisdiction="global",
        task="test_task",
        n=10,
        seed=42
    )

    # Should be identical
    assert result1 == result2
```

## Performance Optimization

### 1. Consent Index Optimization

```python
# Current: O(1) lookups via nested dict
# For scale, consider:
- Redis for distributed cache
- PostgreSQL with JSONB indexes
- Time-partitioned indexes for historical queries
```

### 2. Policy Overlay Caching

```python
# Add LRU cache for merged policies
from functools import lru_cache

class CachedOverlayManager(RiskOverlayManager):
    @lru_cache(maxsize=128)
    def get_policies(self, jurisdiction, context):
        return super().get_policies(jurisdiction, context)

    def hot_reload(self):
        super().hot_reload()
        self.get_policies.cache_clear()
```

### 3. Parallel TEQ Checks

```python
# Run independent checks concurrently
import asyncio

async def async_teq_check(gate, task, context):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, gate.run, task, context
    )

# Batch processing
tasks = ["task1", "task2", "task3"]
results = await asyncio.gather(*[
    async_teq_check(gate, t, ctx) for t in tasks
])
```

## Security Considerations

### 1. Signing Key Management

```python
# Rotate keys periodically
import nacl.signing

def rotate_signing_keys():
    # Generate new key
    new_key = nacl.signing.SigningKey.generate()

    # Save securely (use KMS in production)
    import keyring
    keyring.set_password(
        "lukhas",
        "consent_signing_key",
        new_key.encode().hex()
    )

    # Keep old key for verification only
    archive_old_key(old_key)
```

### 2. Consent Tampering Protection

```python
# Verify consent integrity
def verify_consent_chain(event_id):
    from qi.ops.provenance import verify

    # Load event
    event = load_event(event_id)

    # Verify Merkle chain
    chain = load_chain(event.receipt["chain_path"])
    root = compute_merkle_root(chain)

    # Verify signature
    verify(
        root,
        event.receipt["signature_b64"],
        event.receipt["public_key_b64"]
    )
```

### 3. Rate Limiting

```python
# Prevent consent spam
from qi.ops.rate_limit import RateLimiter

consent_limiter = RateLimiter(
    max_requests=10,
    window_seconds=60
)

def record_with_limit(user, purpose, fields, days):
    if not consent_limiter.allow(user):
        raise RateLimitExceeded()
    return record(user, purpose, fields, days)
```

## Deployment

### 1. Docker Integration

```dockerfile
FROM python:3.10-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy modules
COPY qi/safety qi/safety
COPY qi/memory qi/memory
COPY qi/risk qi/risk

# Set environment
ENV LUKHAS_STATE=/data/lukhas
ENV CONSENT_WEBHOOK_URL=${CONSENT_WEBHOOK_URL}

# Run safety CI on startup
CMD ["python", "-m", "qi.safety.ci_runner"]
```

### 2. Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: lukhas-safety-config
data:
  overlays.yaml: |
    version: "1.0"
    global_policies:
      teq_checks:
        mask_pii: true
      budget_limits:
        max_tokens: 200000
```

### 3. Monitoring

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

consent_granted = Counter('consent_granted_total', 'Consents granted')
consent_revoked = Counter('consent_revoked_total', 'Consents revoked')
consent_check_duration = Histogram('consent_check_seconds', 'Consent check duration')

# Instrument functions
@consent_check_duration.time()
def is_allowed_monitored(*args, **kwargs):
    return is_allowed(*args, **kwargs)
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'qi'**
```bash
# Add to PYTHONPATH
export PYTHONPATH=/path/to/lukhas:$PYTHONPATH
```

**FileNotFoundError: overlays.yaml**
```python
# Check path resolution
import os
overlay_path = os.path.abspath(overlay_dir)
print(f"Looking for: {overlay_path}/overlays.yaml")
```

**Consent index corruption**
```python
# Rebuild index from ledger
def rebuild_index():
    import json

    index = {}
    with open(RECS, "r") as f:
        for line in f:
            evt = json.loads(line)
            if evt["kind"] == "grant":
                # Add to index
                user = evt["user"]
                purpose = evt["purpose"]
                index.setdefault(user, {})[purpose] = {
                    "ts": evt["ts"],
                    "fields": evt["fields"],
                    "duration_days": evt["duration_days"]
                }
            elif evt["kind"] == "revoke":
                # Remove from index
                if evt["purpose"] == "ALL":
                    index.pop(evt["user"], None)
                else:
                    index.get(evt["user"], {}).pop(evt["purpose"], None)

    _write_index(index)
```

## 5. Capability Sandbox

### Overview
The Capability Sandbox provides deny-by-default isolation for tools and plugins with TTL-based leases.

### Architecture
```python
# Capability types
- "net"                    # Network access
- "api:<name>"            # Named API access
- "fs:read:<glob>"        # File read permission
- "fs:write:<glob>"       # File write permission
```

### Key Components

**CapManager**: Lease management with TTL
- Grant/revoke capabilities per subject
- Persistent or ephemeral leases
- Glob pattern matching for filesystem

**FileGuard**: In-process Python enforcement
- Monkey-patches builtins.open, os.remove, etc.
- Deny-by-default with explicit allowlists
- Audit trail for all operations

**Sandbox**: Activation context manager
- Validates required capabilities
- Enforces FS and ENV restrictions
- Logs enter/exit/denied events

### Important Implementation Notes

**Recursion Prevention**:
The sandbox captures original filesystem functions at import time to prevent recursion when FileGuard is active:
```python
# Captured at module load
_ORIG_OPEN = builtins.open
_ORIG_MAKEDIRS = os.makedirs

# Audit writes bypass FileGuard
def _audit_write(kind, rec):
    with _ORIG_OPEN(path, "a") as f:  # Uses original
        f.write(json.dumps(rec))
```

**Limitations**:
- **In-process only**: This sandbox works for Python tools/plugins. For untrusted binaries, combine with OS-level sandboxes (Docker/Firejail)
- **Glob patterns**: FS checks use fnmatch against absolute paths. Be explicit: `/tmp/**`, `/Users/*/LOCAL-REPOS/**`
- **ENV allowlist**: Prevents accidental secret leakage. Expand per task as needed

### Integration Example

```python
from qi.ops.cap_sandbox import CapManager, Sandbox, SandboxPlan, EnvSpec, FsSpec

mgr = CapManager()
plan = SandboxPlan(
    subject=f"user:{user_id}",
    env=EnvSpec(
        allow=["PATH", "HOME"],
        inject={"NO_PROXY": "*"}
    ),
    fs=FsSpec(
        read=["/Users/*/LOCAL-REPOS/**", "/tmp/**"],
        write=["/tmp/**"]
    ),
    require=["net", "api:search", f"fs:read:/Users/{user_id}/LOCAL-REPOS/**"],
    meta={"task": task_name}
)

with sb.activate(plan):
    # All file operations enforced
    # Child processes get filtered env
    result = run_tool()
```

### Audit Trail
All operations logged to `~/.lukhas/state/audit/caps.jsonl`:
- lease_grant/revoke
- sandbox_enter/exit
- fs_denied events
- sandbox_run commands

## Future Enhancements

### Planned Features
1. **Consent Analytics**: Dashboard for consent metrics
2. **Policy Versioning**: Track policy changes over time
3. **Distributed Consent**: Multi-region consent synchronization
4. **ML-based Fuzzing**: Learn from production failures
5. **Compliance Reports**: Automated GDPR/CCPA reporting

### Integration Points
- GraphQL API for consent management
- Terraform provider for policy deployment
- GitHub Actions for safety CI
- Datadog APM integration
- Slack notifications for violations

## Support

For development questions:
- Review test suite in `qi/safety/tests/`
- Check examples in `qi/safety/examples/`
- File issues at: github.com/lukhas/qi-safety
- Join Discord: discord.gg/lukhas-dev
