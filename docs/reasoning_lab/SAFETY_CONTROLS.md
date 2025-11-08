# Reasoning Lab Safety Controls

**Privacy-preserving demo mode with redaction controls for LUKHAS Reasoning Lab**

Version: 1.0.0
Last Updated: 2025-11-08
GAPS Item: B4

---

## Overview

The Reasoning Lab Safety Controls system provides privacy-preserving capabilities for the LUKHAS Reasoning Lab, our interactive AI reasoning visualization tool. This system ensures that sensitive data (API keys, passwords, PII) is automatically detected and redacted before display or storage.

### Key Features

- **Sensitive Data Detection**: 95%+ detection rate for API keys, passwords, PII, credit cards, and more
- **Multiple Redaction Modes**: Full, partial, hash, and blur redaction options
- **Privacy-Preserving Demo Mode**: Sandboxed execution with ephemeral sessions
- **Real-time Protection**: Automatic detection and redaction as users type
- **Audit Logging**: Complete trail of all redactions for compliance
- **User Control**: Interactive slider for redaction level (None → Paranoid)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              User Input (Reasoning Trace)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│          Sensitive Data Detector                        │
│  • Pattern matching (API keys, emails, etc.)            │
│  • Entropy analysis (unknown secrets)                   │
│  • Configurable thresholds (LOW/MEDIUM/HIGH)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│             Redaction Engine                            │
│  • FULL: [REDACTED-API-KEY]                             │
│  • PARTIAL: sk-a...xyz                                  │
│  • HASH: hash:a1b2c3...                                 │
│  • BLUR: ****-****-****                                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│          Demo Mode (if enabled)                         │
│  • Add watermark                                        │
│  • Rate limiting (10 traces/IP/hour)                    │
│  • Ephemeral storage (1 hour TTL)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Sanitized Output                           │
│  • Safe for display                                     │
│  • Audit logged                                         │
│  • Compliant with privacy policies                      │
└─────────────────────────────────────────────────────────┘
```

---

## How Redaction Works

### Detection Patterns

The system detects the following sensitive data types:

| Type | Pattern Example | Confidence |
|------|----------------|------------|
| **OpenAI API Key** | `sk-abc123xyz...` (48 chars) | 95% |
| **Anthropic API Key** | `sk-ant-abc...` (95+ chars) | 95% |
| **AWS Access Key** | `AKIAIOSFODNN7EXAMPLE` | 95% |
| **Email** | `user@example.com` | 80% |
| **Phone** | `(555) 123-4567` | 75% |
| **Credit Card** | `4532-0151-1283-0366` | 90% |
| **SSN** | `123-45-6789` | 90% |
| **IP Address** | `192.168.1.1` | 70% |
| **UUID** | `550e8400-e29b-...` | 80% |
| **Generic Secret** | High-entropy string (20+ chars) | 60-90% |

### Redaction Modes

#### 1. FULL Redaction (100% - Paranoid)

**Most secure**: Complete replacement with type indicator.

```
Original:  My API key is sk-abc123xyz456789012345678901234567890123456
Redacted:  My API key is [REDACTED-API-KEY]
```

**Use when:**
- Public demonstrations
- Untrusted environments
- Maximum privacy required

#### 2. HASH Redaction (75% - High)

Shows cryptographic hash prefix for verification without revealing data.

```
Original:  My API key is sk-abc123xyz456789012345678901234567890123456
Redacted:  My API key is hash:7f8a9b2c...
```

**Use when:**
- Need to verify same value later
- Debugging without exposing secrets
- Moderate security environments

#### 3. BLUR Redaction (50% - Medium)

Replaces characters with asterisks while preserving structure.

```
Original:  My API key is sk-abc123xyz456789012345678901234567890123456
Redacted:  My API key is **-*****************************************
```

**Use when:**
- Visual length hints needed
- Moderate privacy required
- Internal demonstrations

#### 4. PARTIAL Redaction (25% - Low)

Shows first/last characters for context.

```
Original:  My API key is sk-abc123xyz456789012345678901234567890123456
Redacted:  My API key is sk-a...456
```

**Use when:**
- Debugging with partial context
- Trusted team members
- Low-risk environments

#### 5. NO Redaction (0% - None)

No redaction applied (⚠️ **Use only in secure environments**).

```
Original:  My API key is sk-abc123xyz456789012345678901234567890123456
Redacted:  My API key is sk-abc123xyz456789012345678901234567890123456
```

**Use when:**
- Completely trusted environment
- Secure development machines
- Never in production or demos

---

## Demo Mode Usage

### Enabling Demo Mode

```python
from lukhas.reasoning_lab.demo_mode import DemoMode
from lukhas.reasoning_lab.redaction_engine import RedactionMode

# Initialize demo mode
demo = DemoMode()

# Create session (returns session_id or None if rate limited)
session_id = demo.create_session(ip_address="192.168.1.1")

if session_id:
    # Process reasoning trace
    result = demo.process_reasoning_trace(
        session_id=session_id,
        trace_text="My reasoning with API key sk-abc123...",
        redaction_mode=RedactionMode.FULL
    )

    if result['success']:
        print(result['trace'])  # Redacted + watermarked
        print(f"Detections: {result['detections_count']}")
        print(f"Remaining: {result['session_traces_remaining']}")
```

### Demo Mode Features

1. **Auto-Redaction**: All traces automatically redacted (default: FULL mode)
2. **Watermark**: `⚠️ Demo Mode - Not for Production Use` added to all traces
3. **Rate Limiting**: 10 traces per IP per hour
4. **Ephemeral Storage**: Sessions expire after 1 hour
5. **Sandboxed**: No external API calls allowed
6. **Session Tracking**: Monitor active sessions and usage

### Demo Mode Limits

| Limit | Value | Rationale |
|-------|-------|-----------|
| Traces per session | 10 | Prevent abuse |
| Session TTL | 1 hour | Ephemeral by design |
| Rate limit window | 1 hour | Anti-spam |
| Max concurrent sessions | Unlimited | Scale as needed |

---

## Detection Thresholds

Configure detection sensitivity:

```python
from lukhas.reasoning_lab.sensitive_data_detector import (
    SensitiveDataDetector,
    DetectionThreshold
)

# Low threshold (30%): Detects more, may have false positives
detector_low = SensitiveDataDetector(threshold=DetectionThreshold.LOW)

# Medium threshold (60%): Balanced (default)
detector_medium = SensitiveDataDetector(threshold=DetectionThreshold.MEDIUM)

# High threshold (80%): Selective, fewer false positives
detector_high = SensitiveDataDetector(threshold=DetectionThreshold.HIGH)
```

### Threshold Recommendations

| Scenario | Threshold | Rationale |
|----------|-----------|-----------|
| Public demo | HIGH | Minimize false positives for UX |
| Internal testing | MEDIUM | Balance detection/UX |
| Security audit | LOW | Catch everything, review manually |
| Production | HIGH | Only confident detections |

---

## Privacy Guarantees

### What We Guarantee

✅ **No Storage of Unredacted Data**: All sensitive data is redacted before storage
✅ **No External API Calls in Demo Mode**: Fully sandboxed execution
✅ **Ephemeral Sessions**: Demo sessions auto-delete after 1 hour
✅ **Audit Logging**: Complete trail for compliance
✅ **Opt-Out Redaction**: Enabled by default (user must explicitly disable)
✅ **Rate Limiting**: Prevent abuse and data collection

### What We Log

**Audit logs contain:**
- Timestamp of redaction
- Data type detected (e.g., "api_key_openai")
- Redaction mode used
- SHA-256 hash of original text
- Position in text

**Audit logs DO NOT contain:**
- Original unredacted text
- User identity (unless explicitly provided)
- Content beyond detection metadata

---

## Troubleshooting

### Issue: False Positives

**Problem**: Legitimate text being flagged as sensitive.

**Solution**:
1. Increase detection threshold to HIGH
2. Review flagged patterns in admin dashboard
3. Whitelist specific patterns if needed

### Issue: False Negatives

**Problem**: Sensitive data not detected.

**Solution**:
1. Lower detection threshold to MEDIUM or LOW
2. Check if data type is in supported patterns
3. Report pattern to team for inclusion

### Issue: Session Expired

**Problem**: "Session expired or rate limited" error.

**Solution**:
1. Create new session (sessions expire after 1 hour)
2. Check rate limiting (10 traces per hour)
3. Wait for rate limit window to reset

### Issue: Too Much Redaction

**Problem**: Entire trace is redacted.

**Solution**:
1. Lower redaction mode (try PARTIAL or BLUR)
2. Review what's being detected (may be actual sensitive data!)
3. Use admin dashboard to see detection types

---

## Admin Dashboard

Access the admin dashboard at: `/admin/reasoning_lab_safety`

### Features

1. **Redaction Statistics**
   - Total redactions (by day/week/month)
   - Breakdown by data type
   - Breakdown by redaction mode

2. **Flagged Traces**
   - View traces with high detection counts
   - Review detection types
   - Export for analysis

3. **Threshold Configuration**
   - Adjust detection sensitivity
   - Enable/disable specific patterns
   - Test patterns in real-time

4. **Audit Log Export**
   - Export as JSON or CSV
   - Filter by date range
   - Include/exclude metadata

---

## Integration Examples

### React Component

```tsx
import { RedactionSlider } from '@/components/RedactionSlider';

function MyComponent() {
  const handleRedactionChange = (level) => {
    console.log(`Redaction level: ${level.label} (${level.mode})`);
    // Update backend redaction mode
  };

  return (
    <RedactionSlider
      defaultValue={50}
      onChange={handleRedactionChange}
      showPreview={true}
    />
  );
}
```

### Python Backend

```python
from lukhas.reasoning_lab.sensitive_data_detector import SensitiveDataDetector
from lukhas.reasoning_lab.redaction_engine import RedactionEngine, RedactionMode

# Initialize
detector = SensitiveDataDetector()
redactor = RedactionEngine(audit_logging=True)

# Process user input
user_trace = "My reasoning includes API key sk-abc123..."

# Detect
detections = detector.detect(user_trace)

# Redact
redacted_trace = redactor.redact(user_trace, detections, RedactionMode.FULL)

# Get stats
stats = redactor.get_statistics()
print(f"Redacted {stats['total_redactions']} items")
```

---

## Performance

### Benchmarks

| Operation | Time (ms) | Throughput |
|-----------|-----------|------------|
| Detection (1KB text) | ~5ms | 200 req/s |
| Redaction (10 items) | ~2ms | 500 req/s |
| Demo mode processing | ~10ms | 100 req/s |

### Optimization Tips

1. **Batch Processing**: Process multiple traces together
2. **Caching**: Cache compiled regex patterns
3. **Async**: Use async processing for large traces
4. **Threshold Tuning**: Higher threshold = faster detection

---

## Security Considerations

### Threat Model

**What we protect against:**
- Accidental sensitive data exposure in demos
- API key leakage in screenshots/videos
- PII collection without consent
- Abuse through rate limiting

**What we don't protect against:**
- Intentional data exfiltration by authorized users
- Side-channel attacks
- Browser extensions capturing data
- Screen recording before redaction

### Best Practices

1. **Always Enable in Production**: Never disable redaction in public-facing demos
2. **Regular Audits**: Review audit logs monthly
3. **Threshold Testing**: Test detection accuracy with sample data
4. **User Education**: Explain redaction levels to users
5. **Incident Response**: Have plan for handling detected leaks

---

## API Reference

See inline documentation in:
- `lukhas/reasoning_lab/sensitive_data_detector.py`
- `lukhas/reasoning_lab/redaction_engine.py`
- `lukhas/reasoning_lab/demo_mode.py`
- `lukhas/reasoning_lab/trace_sanitizer.py`

---

## Support

**Questions?** Contact the LUKHAS team or open an issue on GitHub.

**Found a bug?** Report it at: https://github.com/LukhasAI/Lukhas/issues

**Feature request?** We'd love to hear your ideas!

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-08
**Maintainer**: LUKHAS Safety Team
