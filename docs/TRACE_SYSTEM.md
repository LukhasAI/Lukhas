# LUKHAS AI Trace & Audit System

Complete cryptographic audit trail system for the LUKHAS AI platform with visual exploration capabilities.

## Overview

The LUKHAS Trace System provides production-ready audit capabilities with:

- **W3C PROV-Compatible Receipts**: Standards-friendly provenance tracking with cryptographic attestation
- **Multi-Sink Architecture**: Persistent storage via local files, Kafka, and S3 with at-least-once delivery
- **TEQ Policy Replay**: Forensic analysis and regression testing of policy decisions
- **Visual Trace Graph**: Interactive SVG audit trails with clickable nodes
- **Enhanced REST API**: ETag-based caching, CORS support, and browser integration
- **Single-File HTML Interface**: Complete drill-down exploration without dependencies

## Architecture

### Core Components

1. **Receipt Standard** (`qi/provenance/receipt_standard.py`)
   - W3C PROV-compatible data model
   - Merkle + Ed25519 cryptographic sealing
   - Standards-friendly structure for compliance

2. **Receipts Hub** (`qi/provenance/receipts_hub.py`)
   - Multi-sink emission with at-least-once semantics
   - Local persistence + optional Kafka/S3
   - Sandbox recursion prevention

3. **Enhanced API** (`qi/provenance/receipts_api.py`)
   - FastAPI with comprehensive endpoints
   - ETag-based caching using policy fingerprints
   - CORS support for browser embedding

4. **TEQ Replay Tool** (`qi/safety/teq_replay.py`)
   - Forensic policy analysis
   - Attestation verification
   - Configuration drift detection

5. **Trace Graph Renderer** (`qi/trace/trace_graph.py`)
   - Graphviz DOT generation
   - Clickable SVG with activity/entity/policy clusters
   - Visual audit trail representation

6. **HTML Drill-down Interface** (`web/trace_drilldown.html`)
   - Live trace visualization
   - JSON drill-down for receipts/replays/provenance
   - Public redaction mode for safe sharing

## Quick Start

### 1. Start the API Server

```bash
python3 -m uvicorn qi.provenance.receipts_api:app --port 8095 --reload
```

### 2. Open the HTML Interface

```bash
open web/trace_drilldown.html
```

Configure the interface:
- **API Base**: `http://127.0.0.1:8095`
- **Policy Root**: `qi/safety/policy_packs`
- **Overlays**: `qi/risk` (optional)

### 3. Load and Explore Receipts

1. Get a receipt ID from the API: `GET /receipts`
2. Enter the receipt ID in the HTML interface
3. Click "Load" to fetch receipt, replay, and trace visualization
4. Explore the interactive SVG and JSON drill-down tabs

## API Endpoints

### Core Endpoints

- `GET /receipts` - List recent receipts with metadata
- `GET /receipts/{id}` - Get full receipt JSON
- `GET /healthz` - Health check

### Enhanced Endpoints

- `GET /receipts/{id}/replay.json?policy_root=...` - Fresh TEQ replay
- `GET /receipts/{id}/trace.svg?policy_root=...` - Interactive trace visualization
- `GET /policy/fingerprint?policy_root=...` - Policy configuration hash

### Parameters

- **policy_root**: Path to policy packs directory
- **overlays**: Optional overlays directory
- **link_base**: API base URL for clickable activity nodes
- **prov_base**: Provenance API base for artifact links

## CLI Tools

### TEQ Replay Tool

```bash
# Replay a receipt with current policies
python3 qi/safety/teq_replay.py --receipt-id f9115040... --policy-root qi/safety/policy_packs

# Include attestation verification
python3 qi/safety/teq_replay.py --receipt-id f9115040... --verify-receipt --verify-provenance

# Output JSON for integration
python3 qi/safety/teq_replay.py --receipt-id f9115040... --json
```

### Receipt Generation

Receipts are automatically generated when using the QI Safety system:

```python
from qi.provenance.receipts_hub import emit_receipt

receipt = emit_receipt(
    artifact_sha="abc123...",
    task="generate_summary",
    user_id="agent:user:123",
    service_name="lukhas",
    started_at=time.time(),
    ended_at=time.time() + 5,
    tokens_in=100,
    tokens_out=50,
    latency_ms=150
)
```

## Configuration

### Environment Variables

- `LUKHAS_STATE`: State directory (default: `~/.lukhas/state`)
- `RECEIPTS_API_CORS`: CORS origins (comma-separated)
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka cluster for receipt streaming
- `S3_BUCKET`: S3 bucket for receipt archival

### Policy Fingerprinting

The system uses deterministic policy fingerprinting to detect configuration drift:

1. Scans all `.yaml`, `.yml`, `.json` files in policy directory
2. Includes overlay files if specified
3. Generates SHA256 hash for cache invalidation
4. Powers ETag-based HTTP caching

## Security Features

### Cryptographic Attestation

All receipts include cryptographic attestation:

```json
{
  "attestation": {
    "merkle_root": "sha256:abc123...",
    "signature": "ed25519:def456...",
    "public_key": "ed25519:ghi789...",
    "timestamp": 1702834567.123
  }
}
```

### Public Redaction

The HTML interface includes a public redaction mode that masks:
- SHA hashes (shows first 6 + last 4 characters)
- Email addresses
- File paths (S3, GS, local)
- User IDs within agent identifiers

### Sandbox Isolation

All file operations use captured original functions to prevent capability sandbox recursion:

```python
import builtins
_ORIG_OPEN = builtins.open  # Captured at import

def _audit_write(kind, record):
    with _ORIG_OPEN(path, "a") as f:  # Uses original open
        f.write(json.dumps(record) + "\n")
```

## Testing

### Run All Tests

```bash
python3 qi/provenance/test_enhanced_api.py
```

### Test Individual Components

```bash
# Test receipt standard
python3 qi/provenance/test_receipt_standard.py

# Test receipts hub
python3 qi/provenance/test_receipts_hub.py

# Test TEQ replay
python3 qi/safety/test_teq_replay.py

# Test trace graph
python3 qi/trace/test_trace_graph.py
```

### Requirements

- **Python**: 3.8+
- **FastAPI**: For API server
- **Graphviz**: For SVG rendering (`brew install graphviz`)
- **Cryptography**: For attestation verification

## Integration

### TEQ Safety Integration

The trace system integrates automatically with TEQ safety checks:

```python
# qi/safety/teq_gate_provenance.py
from qi.provenance.receipts_hub import emit_receipt

def teq_check_with_provenance(prompt, **kwargs):
    start_time = time.time()
    result = teq_check(prompt, **kwargs)
    
    # Emit receipt automatically
    emit_receipt(
        artifact_sha=hashlib.sha256(prompt.encode()).hexdigest(),
        task="safety_check",
        started_at=start_time,
        ended_at=time.time(),
        # ... additional metadata
    )
    
    return result
```

### External Service Integration

The multi-sink architecture supports external audit systems:

1. **Local Files**: Immediate persistence for debugging
2. **Kafka**: Real-time streaming to audit dashboards
3. **S3**: Long-term archival and compliance

## Performance

### Caching Strategy

- **ETag-based HTTP caching**: Prevents unnecessary recomputation
- **Policy fingerprinting**: Detects configuration changes
- **SVG caching**: Expensive Graphviz rendering cached by policy state

### Benchmarks

- **Receipt emission**: <5ms per receipt
- **TEQ replay**: <100ms for typical policies
- **SVG generation**: <500ms with caching
- **API latency**: <50ms p95 with ETag cache hits

## Troubleshooting

### Common Issues

1. **Graphviz not found**
   ```bash
   brew install graphviz  # macOS
   apt-get install graphviz  # Linux
   ```

2. **Capability sandbox recursion**
   - Ensure original functions are captured at import time
   - Use `_ORIG_OPEN`, `_ORIG_MAKEDIRS` for audit writes

3. **CORS errors in browser**
   ```bash
   export RECEIPTS_API_CORS="http://localhost:3000,https://yourdomain.com"
   ```

4. **Missing receipts**
   - Check `~/.lukhas/state/provenance/exec_receipts/`
   - Verify QI Safety integration is active

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Compliance

### Standards Alignment

- **W3C PROV**: Compatible data model for provenance interoperability
- **OpenAPI 3.0**: Auto-generated API documentation
- **HTTP Caching**: RFC 7234 compliant ETag implementation
- **CORS**: W3C Cross-Origin Resource Sharing specification

### Audit Trail Integrity

Every receipt includes:
- Cryptographic proof of integrity
- Immutable artifact fingerprints
- Policy configuration snapshots
- Execution context preservation

## Future Enhancements

- **OIDC Integration**: User identity in audit trails
- **Grafana Dashboard**: Real-time audit visualization
- **Policy Diff Tool**: Visual configuration change tracking
- **Webhook Integration**: Real-time audit notifications
- **Retention Policies**: Automated receipt lifecycle management