# Security Test Suite

## Overview
Security test harness for LUKHAS AI, focusing on PQC migration (MATRIZ-007), authentication, and attack resistance.

## Red-Team Tests (MATRIZ-007)

### Prerequisites
```bash
# Install PQC dependencies
pip install liboqs-python

# Or use Docker runner
docker build -f .github/docker/pqc-runner.Dockerfile -t lukhas-pqc-runner .
docker run --rm -v $(pwd):/workspace lukhas-pqc-runner pytest tests/security -v
```

### Test Categories

#### 1. Signature Forgery (RED-TEAM-001 to RED-TEAM-003)
- **RED-TEAM-001**: Random signature forgery
- **RED-TEAM-002**: Message modification with valid signature
- **RED-TEAM-003**: Wrong public key verification

**Run:**
```bash
pytest tests/security/test_pqc_redteam.py::TestPQCSignatureForgery -v
```

#### 2. Key Compromise (RED-TEAM-004 to RED-TEAM-005)
- **RED-TEAM-004**: Key compromise detection
- **RED-TEAM-005**: Dual-signing during rotation

**Run:**
```bash
pytest tests/security/test_pqc_redteam.py::TestKeyCompromise -v
```

#### 3. Replay Attacks (RED-TEAM-006 to RED-TEAM-007)
- **RED-TEAM-006**: Timestamp-based replay detection
- **RED-TEAM-007**: Nonce uniqueness enforcement

**Run:**
```bash
pytest tests/security/test_pqc_redteam.py::TestReplayAttacks -v
```

#### 4. Checkpoint Corruption (RED-TEAM-008 to RED-TEAM-010)
- **RED-TEAM-008**: Single bit flip detection
- **RED-TEAM-009**: Truncation detection
- **RED-TEAM-010**: Signature truncation handling

**Run:**
```bash
pytest tests/security/test_pqc_redteam.py::TestCheckpointCorruption -v
```

#### 5. Dream-State Exfiltration (RED-TEAM-011 to RED-TEAM-012)
- **RED-TEAM-011**: Encrypted checkpoint verification
- **RED-TEAM-012**: Public key safety

**Run:**
```bash
pytest tests/security/test_pqc_redteam.py::TestDreamExfiltration -v
```

#### 6. Performance (RED-TEAM-013 to RED-TEAM-014)
- **RED-TEAM-013**: Sign latency p95 < 50ms
- **RED-TEAM-014**: Verify latency p95 < 10ms

**Run:**
```bash
pytest tests/security/test_pqc_redteam.py::TestPerformance -v
```

### Run All Red-Team Tests
```bash
pytest tests/security -m redteam -v
```

### Run with Coverage
```bash
pytest tests/security --cov=services.registry --cov-report=html
```

## Test Markers

- `@pytest.mark.security` - All security tests
- `@pytest.mark.pqc` - Post-quantum cryptography tests
- `@pytest.mark.redteam` - Red-team attack simulations
- `@pytest.mark.slow` - Tests that take >1s to run

## Expected Results (Week 5)

### Before PQC Migration
```
RED-TEAM-001: PASS (forgery blocked)
RED-TEAM-002: PASS (modification detected)
RED-TEAM-003: PASS (wrong key rejected)
RED-TEAM-004: SKIP (revocation not implemented)
RED-TEAM-005: SKIP (rotation not implemented)
RED-TEAM-006: SKIP (timestamp check not implemented)
RED-TEAM-007: SKIP (nonce tracking not implemented)
RED-TEAM-008: PASS (corruption detected)
RED-TEAM-009: PASS (truncation detected)
RED-TEAM-010: PASS (malformed signature rejected)
RED-TEAM-011: PASS (no plaintext leak)
RED-TEAM-012: PASS (public key safe)
RED-TEAM-013: PASS (sign latency OK)
RED-TEAM-014: PASS (verify latency OK)
```

### After PQC Migration (Week 6)
All tests should PASS with no SKIPs.

## TODO Items for Production

The following features need implementation before production:

### Key Management
- [ ] Key revocation list (CRL) implementation
- [ ] Trust anchor verification
- [ ] Hardware security module (HSM) integration
- [ ] Key rotation automation

### Replay Protection
- [ ] Timestamp validation with configurable window
- [ ] Nonce tracking and deduplication
- [ ] Checkpoint sequence number enforcement

### Monitoring
- [ ] Attack attempt logging
- [ ] Failed verification alerting
- [ ] Key usage metrics
- [ ] Anomaly detection

## Security Incident Response

### High-Severity Findings
1. Stop all registry operations
2. Capture forensic evidence
3. Notify security team
4. Create incident ticket
5. Follow rollback procedure

### Contact
- **Security Team**: security@lukhas.ai
- **On-Call**: See PagerDuty rotation
- **Escalation**: CTO

## Related Documentation

- [MATRIZ-007 Timeline](../../docs/ops/POST_MERGE_ACTIONS.md#matriz-007-pqc-migration-timeline)
- [Monitoring Config](../../docs/ops/monitoring_config.md)
- [Registry Service](../../services/registry/main.py)
- [PQC Runner Setup](../../.github/docker/README.md)

## Benchmark Results

Typical performance on modern hardware:

```
Algorithm: Dilithium2
Key generation: ~0.1ms
Sign:          ~0.5ms (p95 < 1ms)
Verify:        ~0.2ms (p95 < 0.5ms)
Public key:    1312 bytes
Signature:     2420 bytes
```

## Compliance

These tests address:
- **NIST PQC Standards**: Dilithium (FIPS 204 draft)
- **OWASP Top 10**: Cryptographic failures, broken authentication
- **SOC 2**: Cryptographic key management, access controls
