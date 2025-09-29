# TEQ Policy Replay Guide

## Overview

The TEQ Replay tool enables forensic analysis and regression testing by replaying past policy decisions using cryptographically-sealed receipts. This allows you to:

- **Audit past decisions**: Understand why a request was allowed or blocked
- **Detect policy drift**: Compare historical vs current policy behavior
- **Verify attestations**: Validate cryptographic signatures on receipts
- **Regression testing**: Ensure policy changes don't break expected behavior

## Quick Start

### Basic Replay

```bash
# Replay using receipt ID (supports prefix matching)
python -m qi.safety.teq_replay \
  --id f9115040 \
  --policy-root qi/safety/policy_packs

# Replay from explicit receipt file
python -m qi.safety.teq_replay \
  --receipt /path/to/receipt.json \
  --policy-root qi/safety/policy_packs
```

### With Attestation Verification

```bash
# Verify cryptographic signatures
python -m qi.safety.teq_replay \
  --id <receipt_id> \
  --policy-root qi/safety/policy_packs \
  --verify-att \
  --verify-prov-att
```

### With Overlays

```bash
# Include risk overlays in replay
python -m qi.safety.teq_replay \
  --id <receipt_id> \
  --policy-root qi/safety/policy_packs \
  --overlays qi/risk
```

### JSON Output

```bash
# Machine-readable output for automation
python -m qi.safety.teq_replay \
  --id <receipt_id> \
  --policy-root qi/safety/policy_packs \
  --json | jq .
```

## Output Format

### Human-Readable (Default)

```markdown
# TEQ Replay
- Task: `generate_summary`   Jurisdiction: `global`   Context: `-`
- Receipt ID: `14131b73...`   Artifact SHA: `cf632dd6...`
- Receipt attestation: ✅ verified
- Provenance attestation: —
- Policy fingerprint: `0771cffe39d9c676…`

**Replay verdict:** ❌ BLOCKED

## Reasons
- Missing provenance record.
```

### JSON Format

```json
{
  "task": "generate_summary",
  "jurisdiction": "global",
  "context": null,
  "receipt_id": "14131b73...",
  "artifact_sha": "cf632dd6...",
  "policy_fingerprint": "0771cffe39d9c676...",
  "replay": {
    "allowed": false,
    "reasons": ["Missing provenance record."],
    "checks": null
  },
  "receipt_attestation_ok": true,
  "provenance_attestation_ok": null
}
```

## Key Features

### 1. Receipt Loading

- **Full ID**: Exact 64-character receipt ID
- **Prefix matching**: First 8+ characters (e.g., `f9115040`)
- **Path loading**: Direct path to receipt JSON

### 2. Policy Fingerprinting

The tool generates a deterministic fingerprint of your current policy configuration:

```python
policy_fingerprint = SHA256(all_policy_files + overlays)
```

This allows you to:
- Detect when policies have changed
- Correlate behavior changes with policy updates
- Track policy versions in CI/CD

### 3. Context Reconstruction

The tool rebuilds a minimal TEQ context from the receipt:

- User ID extraction from agents
- Token counts from receipt metadata
- Provenance pointers for validation
- PII masking flags

### 4. Attestation Verification

When enabled, verifies:
- **Receipt attestation**: Ed25519 signature on the receipt's Merkle chain
- **Provenance attestation**: Signature on the underlying provenance record

## Use Cases

### 1. Incident Investigation

```bash
# User reports being blocked unexpectedly
python -m qi.safety.teq_replay \
  --id <receipt_from_incident> \
  --policy-root qi/safety/policy_packs \
  --verify-att
```

### 2. Policy Change Validation

```bash
# Before deploying new policies, replay sample receipts
for receipt in $(ls ~/.lukhas/state/provenance/exec_receipts/*.json | head -10); do
  python -m qi.safety.teq_replay \
    --receipt $receipt \
    --policy-root qi/safety/policy_packs_new \
    --json | jq -r '.replay.allowed'
done
```

### 3. Regression Testing in CI

```bash
# replay_regression.sh
#!/bin/bash
BASELINE_RECEIPTS="test_data/receipts/*.json"
FAILURES=0

for receipt in $BASELINE_RECEIPTS; do
  RESULT=$(python -m qi.safety.teq_replay \
    --receipt $receipt \
    --policy-root $1 \
    --json | jq -r '.replay.allowed')

  EXPECTED=$(jq -r '.expected_allowed' $receipt)

  if [ "$RESULT" != "$EXPECTED" ]; then
    echo "REGRESSION: $(basename $receipt)"
    ((FAILURES++))
  fi
done

exit $FAILURES
```

### 4. Compliance Audit

```bash
# Generate audit report for specific time period
for receipt in $(find ~/.lukhas/state/provenance/exec_receipts -name "*.json" -mtime -30); do
  python -m qi.safety.teq_replay \
    --receipt $receipt \
    --policy-root qi/safety/policy_packs \
    --verify-att \
    --json
done | jq -s '
  group_by(.task) |
  map({
    task: .[0].task,
    total: length,
    blocked: [.[] | select(.replay.allowed == false)] | length,
    verified: [.[] | select(.receipt_attestation_ok == true)] | length
  })'
```

## Advanced Usage

### Replay with Historical Policies

```bash
# Checkout old policy version
git checkout v1.0.0 -- qi/safety/policy_packs

# Replay with historical policies
python -m qi.safety.teq_replay \
  --id <receipt_id> \
  --policy-root qi/safety/policy_packs
```

### Batch Processing

```python
import json
import glob
from qi.safety.teq_replay import replay_from_receipt, _load_receipt

# Process all receipts from last hour
receipts = glob.glob("~/.lukhas/state/provenance/exec_receipts/*.json")
results = []

for receipt_path in receipts[-100:]:  # Last 100
    receipt = _load_receipt(None, receipt_path)
    result = replay_from_receipt(
        receipt=receipt,
        policy_root="qi/safety/policy_packs",
        overlays_dir="qi/risk",
        verify_receipt_attestation=True
    )
    results.append(result)

# Analyze results
blocked = [r for r in results if not r["replay"]["allowed"]]
print(f"Blocked: {len(blocked)}/{len(results)}")
```

### Custom Policy Testing

```python
from qi.safety.teq_replay import replay_from_receipt
import tempfile
import shutil

# Create test policy variant
with tempfile.TemporaryDirectory() as tmpdir:
    # Copy and modify policies
    test_policies = f"{tmpdir}/test_policies"
    shutil.copytree("qi/safety/policy_packs", test_policies)

    # Modify specific rule
    # ... make changes ...

    # Test impact
    result = replay_from_receipt(
        receipt=receipt,
        policy_root=test_policies,
        overlays_dir=None
    )
```

## Troubleshooting

### Receipt Not Found

```bash
# List available receipts
ls -la ~/.lukhas/state/provenance/exec_receipts/

# Use prefix matching (first 8+ chars)
python -m qi.safety.teq_replay --id f9115040 ...
```

### Attestation Verification Fails

- Ensure PyNaCl is installed: `pip install PyNaCl`
- Check that receipt has attestation field
- Verify chain_path exists in attestation

### Different Replay Results

Check if policies changed:
```bash
# Compare fingerprints
python -m qi.safety.teq_replay --id <old_receipt> --json | jq .policy_fingerprint
python -m qi.safety.teq_replay --id <new_receipt> --json | jq .policy_fingerprint
```

## Integration with Other Tools

### With Provenance System

Receipts are automatically generated by:
- `qi.provenance.receipts_hub` - Creates receipts
- `qi.safety.teq_gate_provenance` - TEQ with automatic receipts

### With Risk Overlays

```bash
# Include jurisdiction-specific overlays
python -m qi.safety.teq_replay \
  --id <receipt_id> \
  --policy-root qi/safety/policy_packs \
  --overlays qi/risk
```

### With Consent System

The replay tool respects consent references in receipts:
- `consent_receipt_id` - Links to consent ledger
- `capability_lease_ids` - Links to capability sandbox

## Best Practices

1. **Regular Regression Testing**: Run replay on sample receipts before deploying policy changes
2. **Audit Trail**: Keep receipts for at least 90 days for compliance
3. **Fingerprint Tracking**: Log policy fingerprints with deployments
4. **Attestation Verification**: Enable for high-stakes replays
5. **Automation**: Integrate replay into CI/CD pipelines

## Security Considerations

- Receipts may contain sensitive metadata (user IDs, task types)
- Store receipts with appropriate access controls
- Attestation verification requires access to signing keys
- Policy fingerprints can reveal policy structure

## Performance

- Receipt loading: O(1) with ID, O(n) with prefix
- Replay execution: <10ms typical
- Attestation verification: +5-10ms per signature
- Policy fingerprint: Cached after first computation

## Future Enhancements

- [ ] Bulk replay with parallel processing
- [ ] Differential analysis between policy versions
- [ ] Integration with Grafana for replay metrics
- [ ] ML-based anomaly detection on replay patterns
- [ ] Time-travel debugging with policy snapshots
