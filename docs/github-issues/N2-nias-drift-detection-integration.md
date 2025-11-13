# [N2] NIAS Drift Detection Integration

**Labels**: `enhancement`, `nias`, `security`, `ml`
**Priority**: High
**Milestone**: Q2 2026
**Estimated Effort**: 5-8 days

---

## Problem Statement

NIAS (Non Intrusive Advertisements Systems) currently logs audit events but the `drift_score` field is always `null` (placeholder implementation). Without drift detection:
1. **No Anomaly Detection**: Cannot identify unusual request patterns (attacks, bots, abuse)
2. **No Behavioral Baseline**: No understanding of "normal" vs "abnormal" traffic
3. **Manual Review Required**: Security team must manually review logs (time-consuming)
4. **Reactive Security**: Only detect attacks after damage done (no real-time flagging)

**Current Code** (`lukhas/guardian/nias/middleware.py:82-84`):
```python
def _estimate_drift(request: Request) -> Optional[float]:
    # TODO: Integrate with actual drift detection module
    return None
```

## Proposed Solution

Implement behavioral drift detection using **Isolation Forest** (unsupervised anomaly detection):

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    NIAS Middleware                       │
│                                                           │
│  1. Extract Features ────────────────────────────────┐  │
│     (route, method, caller, time, headers, etc.)     │  │
│                                                        │  │
│  2. DriftDetector.score() ──────────────────────────┐ │  │
│     - Load trained Isolation Forest model           │ │  │
│     - Compute anomaly score (0.0-1.0)               │ │  │
│     - Return drift_score                            │ │  │
│                                                       │ │  │
│  3. NIASAuditEvent(drift_score=0.85) ───────────────┘ │  │
│     - Write to JSONL with score                       │  │
│                                                         │  │
│  4. Alert on High Drift ────────────────────────────────┘  │
│     - If drift_score > 0.8: log warning, send Slack alert │
│                                                           │
└───────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Offline Training Pipeline                   │
│                                                           │
│  1. Load Historical NIAS Logs (past 30 days)            │
│  2. Extract Features (same as online)                    │
│  3. Train Isolation Forest (contamination=0.01)          │
│  4. Save Model (pickle or joblib)                        │
│  5. Deploy to S3 / Model Registry                        │
│                                                           │
│  Scheduled: Daily at 2 AM UTC                            │
└───────────────────────────────────────────────────────────┘
```

### Feature Engineering

**Features** (20 total):
1. **Route Hash**: Hash of route path (e.g., MD5(`/v1/chat/completions`))
2. **Method**: One-hot encoded (GET=0, POST=1, PUT=2, DELETE=3)
3. **Hour of Day**: 0-23 (detect unusual times)
4. **Day of Week**: 0-6 (detect weekend anomalies)
5. **Caller Frequency**: Requests per hour from this caller
6. **Response Time**: Normalized duration_ms (z-score)
7. **Status Code**: One-hot encoded (200, 401, 403, 404, 500)
8. **User-Agent Hash**: Hash of User-Agent header
9. **Content-Type Hash**: Hash of Content-Type header
10. **Accept Hash**: Hash of Accept header
11. **Route Length**: Length of route path (long paths suspicious)
12. **Query Param Count**: Number of query parameters (if available)
13. **Header Count**: Total number of headers
14. **Caller Entropy**: Shannon entropy of caller ID (detect randomized IDs)
15. **Sequential Requests**: Time since last request from this caller
16. **Error Rate**: Fraction of 4xx/5xx in last 10 requests from caller
17. **Method Diversity**: Unique methods used by caller in last hour
18. **Route Diversity**: Unique routes accessed by caller in last hour
19. **Geographic Variance**: If caller location changes (IP geolocation)
20. **TLS Version**: SSL/TLS protocol version (old versions suspicious)

### Implementation

**Module**: `lukhas/guardian/drift/detector.py`
```python
"""Drift detection for NIAS using Isolation Forest."""
import hashlib
import pickle
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.ensemble import IsolationForest
from starlette.requests import Request


class DriftDetector:
    """Real-time drift detection for API requests."""

    def __init__(self, model_path: str = "models/drift_detector.pkl"):
        """Load trained Isolation Forest model."""
        self.model_path = Path(model_path)
        if self.model_path.exists():
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
        else:
            # Fallback: untrained model (all scores = 0.5)
            self.model = None

        # Feature extraction cache (caller frequency, etc.)
        self._caller_cache = {}

    def extract_features(self, request: Request) -> np.ndarray:
        """Extract 20-dimensional feature vector from request."""
        features = []

        # 1. Route hash
        route_hash = int(hashlib.md5(str(request.url.path).encode()).hexdigest()[:8], 16)
        features.append(route_hash / 1e10)  # Normalize

        # 2. Method (one-hot)
        method_map = {"GET": 0, "POST": 1, "PUT": 2, "DELETE": 3, "PATCH": 4}
        features.append(method_map.get(request.method, 5))

        # 3-4. Time features
        now = datetime.utcnow()
        features.append(now.hour)  # 0-23
        features.append(now.weekday())  # 0-6

        # 5. Caller frequency (requests/hour)
        caller = request.headers.get("OpenAI-Organization") or "unknown"
        caller_freq = self._caller_cache.get(caller, 0)
        features.append(min(caller_freq, 1000))  # Cap at 1000

        # 6. Response time (placeholder - set during write)
        features.append(0.0)  # Will be filled by middleware

        # 7. Status code (placeholder)
        features.append(0)

        # 8-10. Header hashes
        user_agent = request.headers.get("user-agent", "")
        features.append(int(hashlib.md5(user_agent.encode()).hexdigest()[:8], 16) / 1e10)

        content_type = request.headers.get("content-type", "")
        features.append(int(hashlib.md5(content_type.encode()).hexdigest()[:8], 16) / 1e10)

        accept = request.headers.get("accept", "")
        features.append(int(hashlib.md5(accept.encode()).hexdigest()[:8], 16) / 1e10)

        # 11-13. Request complexity
        features.append(len(str(request.url.path)))  # Route length
        features.append(len(request.query_params))  # Query param count
        features.append(len(request.headers))  # Header count

        # 14. Caller entropy
        caller_entropy = -sum(c / len(caller) * np.log2(c / len(caller)) for c in set(caller.encode()) if c > 0)
        features.append(caller_entropy)

        # 15-20. Behavioral features (simplified - use cache)
        features.extend([0.0] * 6)  # Placeholder for complex features

        return np.array(features).reshape(1, -1)

    def score(self, request: Request) -> float:
        """Compute drift score (0.0 = normal, 1.0 = highly anomalous)."""
        if self.model is None:
            return 0.5  # Unknown (no model trained)

        features = self.extract_features(request)
        anomaly_score = self.model.decision_function(features)[0]

        # Convert to 0.0-1.0 range (sigmoid-like transformation)
        drift_score = 1.0 / (1.0 + np.exp(-anomaly_score))

        return max(0.0, min(1.0, drift_score))  # Clamp


# Global detector instance (initialized once)
_detector = None


def get_drift_detector() -> DriftDetector:
    """Get global drift detector (lazy initialization)."""
    global _detector
    if _detector is None:
        _detector = DriftDetector()
    return _detector
```

**Integration** (`lukhas/guardian/nias/middleware.py`):
```python
from lukhas.guardian.drift.detector import get_drift_detector

def _estimate_drift(request: Request) -> Optional[float]:
    """Estimate drift score using trained Isolation Forest."""
    try:
        detector = get_drift_detector()
        return detector.score(request)
    except Exception as e:
        logger.warning(f"Drift detection failed: {e}")
        return None  # Fail-safe
```

### Training Pipeline

**Script**: `scripts/train_drift_detector.py`
```python
"""Train drift detector from historical NIAS logs."""
import json
from pathlib import Path
import pickle

import numpy as np
from sklearn.ensemble import IsolationForest

# 1. Load NIAS logs (past 30 days)
logs = []
for log_file in Path("audits/").glob("nias_events.jsonl*"):
    with open(log_file) as f:
        logs.extend(json.loads(line) for line in f)

# 2. Extract features (simplified - use full feature engineering)
features = []
for log in logs:
    route_hash = int(hashlib.md5(log["route"].encode()).hexdigest()[:8], 16) / 1e10
    method = {"GET": 0, "POST": 1}.get(log["method"], 2)
    hour = datetime.fromisoformat(log["ts"]).hour
    # ... (20 features total)
    features.append([route_hash, method, hour, ...])

X = np.array(features)

# 3. Train Isolation Forest (1% contamination = 1% anomalies expected)
model = IsolationForest(
    n_estimators=100,
    contamination=0.01,
    random_state=42,
    n_jobs=-1
)
model.fit(X)

# 4. Save model
with open("models/drift_detector.pkl", "wb") as f:
    pickle.dump(model, f)

print(f"✅ Drift detector trained on {len(X)} samples")
```

**Cron Job** (daily retraining):
```yaml
# .github/workflows/train-drift-detector.yml
name: Train Drift Detector
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download NIAS logs
        run: |
          aws s3 sync s3://lukhas-audit-logs/nias/ audits/

      - name: Train model
        run: python3 scripts/train_drift_detector.py

      - name: Upload model
        run: |
          aws s3 cp models/drift_detector.pkl s3://lukhas-models/drift/drift_detector_$(date +%Y%m%d).pkl
```

## Acceptance Criteria

- [ ] `DriftDetector` class implemented with 20-feature extraction
- [ ] Isolation Forest model trained on 30 days historical data
- [ ] `drift_score` field populated in NIAS events (no longer null)
- [ ] High drift alerts (score > 0.8) sent to Slack `#security-alerts` channel
- [ ] Daily retraining pipeline deployed via GitHub Actions
- [ ] Dashboard: Grafana panel showing drift score distribution
- [ ] Documentation: `docs/nias/DRIFT_DETECTION.md`
- [ ] At least 5 real anomalies detected in first week

## Testing Strategy

```bash
# Unit tests
pytest tests/drift/test_detector.py

# Integration tests (with mock NIAS)
pytest tests/integration/test_nias_drift.py

# Offline evaluation (test on known attacks)
python3 scripts/evaluate_drift_detector.py --dataset tests/data/known_attacks.jsonl
```

## Monitoring & Alerting

**Metrics**:
- `nias_drift_score{caller,route}` (histogram, 0.0-1.0)
- `nias_high_drift_events_total{severity="critical|high"}` (counter)
- `drift_detector_errors_total` (counter, if model loading fails)

**Alerts**:
```yaml
- alert: HighDriftDetected
  expr: nias_drift_score > 0.8
  for: 5m
  annotations:
    summary: "High drift detected: {{$labels.caller}} on {{$labels.route}}"
    description: "Drift score: {{$value}}, potential attack or bot activity"
```

## Related Issues

- #N3: NIAS PII Detection Integration
- #D4: ZAP CI/CD Enhancements (cross-validate drift with DAST findings)
- #XXX: ABAS integration (deny requests with high drift scores)

## References

- [Isolation Forest Paper](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)
- [scikit-learn IsolationForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [NIAS PLAN](../../docs/nias/NIAS_PLAN.md)
- Gonzo Spec: `docs/gonzo/SYSTEMS_2.md` (N2 section)

---

**Created**: 2025-11-13
**Author**: Security Enhancement Team
**Reviewers**: @security-team, @ml-team
