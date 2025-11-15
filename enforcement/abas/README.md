# ABAS: Ad-Based Abuse Shield

> **Production-ready policy enforcement with Constitutional AI alignment**

ABAS is an OPA-based (Open Policy Agent) middleware for enforcing GDPR, DSA, and TCF v2.2 compliance in ad targeting systems. It embodies **Constitutional AI principles** (helpful, harmless, honest) in production policy decisions.

---

## 🎯 Features

### Core Policy Enforcement
- ✅ **Minors Protection** (DSA Article 28): Blocks targeted ads for users under 18
- ✅ **Special Categories** (GDPR Article 9): Blocks targeting based on sexual orientation, religion, health, politics, ethnicity
- ✅ **PII Detection**: Conservative regex patterns for email, phone, SSN, credit cards
- ✅ **TCF v2.2 Consent**: Validates P3, P4, storage_p1 for EU personalized targeting
- ✅ **Transparent Denials**: Clear, actionable reasons for every policy decision

### Technical Features
- ⚡ **AsyncTTLCache**: 5-second TTL reduces OPA latency
- 🔒 **Fail-Closed**: Safe by default when OPA unavailable
- 🛡️ **Privacy by Design**: 1024-char body excerpt, no TC string logging
- 🚀 **Early Bypass**: Non-sensitive paths skip policy checks
- 📊 **Constitutional AI Validation**: Claude-powered policy review

---

## 📦 Quick Start

### 1. Using Docker Compose (Recommended)

```bash
# Start OPA + API with ABAS enabled
docker compose -f docker-compose.abas.yml up

# In another terminal, run tests
docker compose -f docker-compose.abas.yml exec opa opa test /policies -v

# Test with curl
curl -X POST http://localhost:8000/v1/responses \
  -H 'Content-Type: application/json' \
  -H 'X-Region: EU' \
  -d '{"text": "I am gay and need support"}' -v

# Expected: 403 {"error": {"message": "blocked: pii detected in request body", ...}}
```

### 2. Manual Setup

```bash
# Install OPA
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa && sudo mv opa /usr/local/bin/

# Start OPA with ABAS policies
opa run --server -a :8181 enforcement/abas &

# Run Rego tests
opa test enforcement/abas -v

# Enable ABAS in your environment
export ABAS_ENABLED=true
export ABAS_FAILCLOSED=true
export OPA_URL=http://127.0.0.1:8181/v1/data/abas/authz/allow
export OPA_REASON_URL=http://127.0.0.1:8181/v1/data/abas/authz/reason

# Start API
uvicorn serve.main:app --port 8000

# Run Python tests
pytest tests/enforcement/test_abas_middleware.py -v
```

---

## 🧪 Testing

### OPA Policy Tests (Rego)
```bash
# Run all policy tests
opa test enforcement/abas -v

# Run specific test file
opa test enforcement/abas/policy_test.rego -v

# Run with coverage
opa test enforcement/abas --coverage
```

**Test Coverage:**
- 9 policy tests (`policy_test.rego`)
- 3 PII detection tests (`pii_detection_test.rego`)

### Python Middleware Tests
```bash
# Unit tests (mocked OPA)
pytest tests/enforcement/test_abas_middleware.py -v

# Integration tests (requires OPA running)
pytest tests/enforcement/test_abas_middleware_integration.py -v

# All tests
pytest tests/enforcement/ -v
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ABAS_ENABLED` | `false` | Enable ABAS middleware (opt-in) |
| `ABAS_FAILCLOSED` | `true` | Fail-closed when OPA unavailable |
| `ABAS_SENSITIVE_PREFIXES` | `/admin,/v1/responses,/nias` | Paths requiring policy checks |
| `ABAS_CACHE_TTL` | `5` | Cache TTL in seconds |
| `ABAS_TIMEOUT` | `2.0` | OPA request timeout in seconds |
| `OPA_URL` | `http://127.0.0.1:8181/v1/data/abas/authz/allow` | OPA policy decision endpoint |
| `OPA_REASON_URL` | `http://127.0.0.1:8181/v1/data/abas/authz/reason` | OPA denial reason endpoint |

### Example Configurations

**Development (fail-open, verbose logging):**
```bash
export ABAS_ENABLED=true
export ABAS_FAILCLOSED=false
export ABAS_CACHE_TTL=1
export LOG_LEVEL=DEBUG
```

**Production (fail-closed, optimized cache):**
```bash
export ABAS_ENABLED=true
export ABAS_FAILCLOSED=true
export ABAS_CACHE_TTL=10
export ABAS_TIMEOUT=1.5
```

**Staging (selective enforcement):**
```bash
export ABAS_ENABLED=true
export ABAS_SENSITIVE_PREFIXES=/v1/responses
export ABAS_FAILCLOSED=false
```

---

## 📋 Policy Logic

### Decision Flow

```
Request → Middleware → Is Sensitive Path?
                              ↓ Yes
                       Extract Headers + Body Excerpt
                              ↓
                       Check Cache (5s TTL)
                              ↓ Miss
                       Call OPA PDP
                              ↓
                  ┌─────────────────────────┐
                  │ ABAS Policy Evaluation  │
                  ├─────────────────────────┤
                  │ 1. Check PII Detection  │
                  │    - Special categories │
                  │    - Email/phone/SSN/CC │
                  │ 2. Check Minors         │
                  │ 3. Check Sensitive Data │
                  │ 4. Check Legal Basis    │
                  │    - EU: TCF v2.2       │
                  │    - Non-EU: Safe mode  │
                  └─────────────────────────┘
                              ↓
                  Allow? → Continue to Handler
                  Deny?  → 403 with Reason
```

### Policy Rules

**1. PII Detection (`pii_detection.rego`)**
- **Deny**: Special categories (gay, muslim, hiv, transgender, religion, politic, ethnicity)
- **Redact**: Email, phone, SSN, credit card patterns
- **None**: Clean content

**2. Minors Protection (`policy.rego`)**
```rego
block_minors {
  input.is_minor == true
}
```
Reason: `"blocked: minors cannot receive targeted ads"`

**3. Sensitive Signals (`policy.rego`)**
```rego
block_sensitive {
  input.using_sensitive_signals == true
}
```
Reason: `"blocked: sensitive data cannot be used for ads"`

**4. EU Consent Requirements (`policy.rego`)**
```rego
legal_basis_eu {
  input.region == "EU"
  input.consent.tcf_present == true
  input.consent.p3 == true  # Ad selection, delivery, reporting
  input.consent.p4 == true  # Personalized ads/content
  input.consent.storage_p1 == true  # Cookie/device storage
}
```
Reason: `"blocked: consent missing for personalization (TCF v2.2 P3/P4/P1)"`

---

## 🔍 Constitutional AI Validation

ABAS includes a **Constitutional AI validator** that uses Claude API to review policies for alignment with "helpful, harmless, honest" principles.

### Run Validation

```bash
# Set API key
export ANTHROPIC_API_KEY=your-key-here

# Run validator
python enforcement/abas/constitutional_validator.py
```

### Example Output

```
🔍 Validating policy.rego...
  Aligned: ✅
  📊 Scores:
    Helpful:   9/10
    Harmless:  10/10
    Honest:    10/10
    Privacy:   9/10
    Legal:     10/10
  💡 Recommendations:
    - Add more specific guidance for TCF consent errors

🎯 Overall Alignment: ✅ PASS
```

See [CONSTITUTIONAL_ALIGNMENT.md](CONSTITUTIONAL_ALIGNMENT.md) for details.

---

## 📊 Performance

### Latency Targets
- **p50**: < 10ms (cache hit)
- **p95**: < 20ms (cache hit)
- **p99**: < 50ms (OPA call)
- **Cache hit rate**: > 80%

### Benchmarking

```bash
# Install dependencies
pip install httpx pytest-benchmark

# Run benchmark
python scripts/benchmark_abas.py --rps 100 --duration 30
```

**Expected results:**
- p50: 8-15ms
- p95: 18-25ms
- 0 errors with OPA available
- Graceful degradation with OPA down

---

## 🛡️ Security & Privacy

### Data Handling
- ✅ **No TC strings in logs**: Consent strings never persisted
- ✅ **Body excerpt**: Max 1024 chars, JSON only
- ✅ **Request restoration**: Downstream handlers see full body
- ✅ **Fail-closed**: Denies on PDP errors (default)

### Compliance
- **GDPR Article 9**: Special categories protection
- **DSA Article 28**: Minors protection
- **TCF v2.2**: P3, P4, storage_p1 validation
- **ePrivacy Directive**: Consent requirements

### Audit Trail
- OPA decision logs (separate from application logs)
- Policy version tracking
- Denial reasons stored for compliance audits

---

## 🚀 Deployment

### Production Checklist

- [ ] Set `ABAS_ENABLED=true` in production environment
- [ ] Set `ABAS_FAILCLOSED=true` for safety
- [ ] Configure OPA with high availability (3+ replicas)
- [ ] Set up OPA bundle server for policy distribution
- [ ] Enable OPA decision logging for audit trail
- [ ] Configure Prometheus metrics for monitoring
- [ ] Set cache TTL based on traffic patterns (5-10s recommended)
- [ ] Test failover scenarios (OPA down, network issues)
- [ ] Document incident response procedures
- [ ] Schedule weekly Constitutional AI validation reviews

### OPA Production Setup

```yaml
# kubernetes/opa-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opa
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: opa
        image: openpolicyagent/opa:latest
        args:
          - "run"
          - "--server"
          - "--addr=0.0.0.0:8181"
          - "--set=decision_logs.console=true"
          - "--set=services.bundleRegistry.url=https://bundles.example.com"
          - "--set=bundles.abas.resource=bundles/abas.tar.gz"
```

---

## 🔧 Troubleshooting

### ABAS not blocking requests

**Check:**
1. Is `ABAS_ENABLED=true`?
2. Is OPA running and reachable? (`curl http://localhost:8181/v1/`)
3. Are policies loaded? (`opa test enforcement/abas -v`)
4. Check path is in `ABAS_SENSITIVE_PREFIXES`

**Debug:**
```bash
# Check OPA health
curl http://localhost:8181/health

# Manual policy query
curl -X POST http://localhost:8181/v1/data/abas/authz/allow \
  -H 'Content-Type: application/json' \
  -d '{"input": {"request": {"path": "/v1/responses", "method": "POST", "body": "I am gay"}, "region": "EU"}}'

# Expected: {"result": false}
```

### High latency

**Check:**
1. Cache hit rate (should be > 80%)
2. OPA response time (`time opa eval ...`)
3. Network latency to OPA server

**Optimize:**
- Increase `ABAS_CACHE_TTL` (5-10s)
- Add more OPA replicas
- Use OPA bundles for faster policy loading
- Profile with `python scripts/benchmark_abas.py`

### Tests failing

```bash
# Rego tests
opa test enforcement/abas -v

# Python tests (unit)
pytest tests/enforcement/test_abas_middleware.py -v -s

# Python tests (integration - requires OPA)
opa run --server -a :8181 enforcement/abas &
pytest tests/enforcement/test_abas_middleware_integration.py -v
```

---

## 📚 Additional Resources

- **[CONSTITUTIONAL_ALIGNMENT.md](CONSTITUTIONAL_ALIGNMENT.md)**: Constitutional AI principles and validation
- **[ABAS_PR_DESCRIPTION.md](../../ABAS_PR_DESCRIPTION.md)**: Full PR checklist and acceptance criteria
- **[OPA Documentation](https://www.openpolicyagent.org/docs/)**: Open Policy Agent reference
- **[TCF v2.2 Spec](https://github.com/InteractiveAdvertisingBureau/GDPR-Transparency-and-Consent-Framework)**: IAB Europe standard

---

## 🤝 Contributing

### Adding New Policies

1. Create `.rego` file in `enforcement/abas/`
2. Add tests in `*_test.rego` file
3. Run `opa test enforcement/abas -v`
4. Run Constitutional AI validator
5. Open PR with `policy:review` label

### Policy Review Process

1. Legal team review (GDPR, DSA, TCF compliance)
2. Security team review (data handling, fail-closed logic)
3. Constitutional AI validation (helpful, harmless, honest)
4. Deployment to staging → 24h monitoring → production

---

## 📄 License

MIT License - See [LICENSE](../../LICENSE) for details

---

**Built with Constitutional AI principles** | **Anthropic Research → Production Systems**

*ABAS demonstrates how "helpful, harmless, honest" translates to production policy enforcement.*
