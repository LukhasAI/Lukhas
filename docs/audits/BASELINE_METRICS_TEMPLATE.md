# Baseline Metrics — v0.9.0-rc

**Collection Period**: [START_TIMESTAMP] to [END_TIMESTAMP] (6 hours)
**Collection Date**: YYYY-MM-DD
**Traffic Volume**: [AVG_REQ_PER_SEC] req/sec average
**Total Requests**: [TOTAL_REQUESTS] requests during baseline window

---

## Guardian PDP Performance

### Latency Metrics
- **P50 latency**: [VALUE]ms (median decision time)
- **P95 latency**: [VALUE]ms (SLO target: <10ms)
- **P99 latency**: [VALUE]ms (should be <20ms)

**Analysis**:
- ✅ P95 within SLO | ⚠️ P95 approaching SLO | ❌ P95 exceeds SLO
- [Notes on latency patterns, if any spikes observed]

### Decision Rate
- **Decisions per second**: [VALUE] decisions/sec
- **Total decisions**: [COUNT] decisions during baseline

**Breakdown by outcome**:
- Allow: [COUNT] ([PERCENT]%)
- Deny: [COUNT] ([PERCENT]%)

---

## Guardian Denial Metrics

### Overall Denial Rate
- **Denial rate**: [VALUE]% (ratio of denies to total decisions)
- **Expected range**: 5-15% (depends on policy strictness)

**Analysis**:
- ✅ Within expected range | ⚠️ Higher than expected | ❌ Critically high

### Denial Rate by Scope
Top 5 scopes by denial rate:

| Scope | Denial Rate | Total Denials | Notes |
|-------|-------------|---------------|-------|
| [SCOPE_1] | [RATE]% | [COUNT] | [Expected/Unexpected] |
| [SCOPE_2] | [RATE]% | [COUNT] | [Expected/Unexpected] |
| [SCOPE_3] | [RATE]% | [COUNT] | [Expected/Unexpected] |
| [SCOPE_4] | [RATE]% | [COUNT] | [Expected/Unexpected] |
| [SCOPE_5] | [RATE]% | [COUNT] | [Expected/Unexpected] |

### Top Denial Reasons
Top 10 denial reasons:

| Reason | Count | Percentage | Notes |
|--------|-------|------------|-------|
| [REASON_1] | [COUNT] | [PERCENT]% | [Policy rule ID, expected?] |
| [REASON_2] | [COUNT] | [PERCENT]% | [Policy rule ID, expected?] |
| [REASON_3] | [COUNT] | [PERCENT]% | [Policy rule ID, expected?] |
| ... | ... | ... | ... |

**Analysis**:
- Top denial reason represents [X]% of all denials
- Policy coverage: [Good/Needs review]
- Unexpected denials: [None / List]

---

## Rate Limiting Metrics

### Hit Rate (429 Rejections)
- **RL hit rate**: [VALUE]% (percentage of requests rate-limited)
- **Target**: <5% (healthy traffic pattern)
- **Total 429s**: [COUNT] rejections

**Analysis**:
- ✅ Below 5% (healthy) | ⚠️ 5-10% (elevated) | ❌ >10% (high)

### Near-Exhaustion Metrics
- **Near-exhaustion ratio**: [VALUE]% of principals with <20% quota remaining
- **Target**: <30% of principals
- **Principals near exhaustion**: [COUNT] out of [TOTAL_PRINCIPALS]

**Top 5 principals by utilization**:

| Principal (hashed) | Utilization | Remaining | Status |
|-------------------|-------------|-----------|--------|
| [HASH_1] | [PERCENT]% | [TOKENS] | [OK/Warning/Critical] |
| [HASH_2] | [PERCENT]% | [TOKENS] | [OK/Warning/Critical] |
| [HASH_3] | [PERCENT]% | [TOKENS] | [OK/Warning/Critical] |
| [HASH_4] | [PERCENT]% | [TOKENS] | [OK/Warning/Critical] |
| [HASH_5] | [PERCENT]% | [TOKENS] | [OK/Warning/Critical] |

### Utilization Metrics
- **Average utilization**: [VALUE]% across all principals
- **Max utilization**: [VALUE]% (single principal max)
- **Expected range**: Avg 20-60%, Max <90%

**Analysis**:
- ✅ Healthy utilization | ⚠️ High utilization | ❌ Over-utilized

### Hit Rate by Route
Top 5 endpoints by rate limit hits:

| Route | Hit Rate | 429 Count | Notes |
|-------|----------|-----------|-------|
| [ROUTE_1] | [RATE]% | [COUNT] | [Expected/Review quota] |
| [ROUTE_2] | [RATE]% | [COUNT] | [Expected/Review quota] |
| [ROUTE_3] | [RATE]% | [COUNT] | [Expected/Review quota] |
| [ROUTE_4] | [RATE]% | [COUNT] | [Expected/Review quota] |
| [ROUTE_5] | [RATE]% | [COUNT] | [Expected/Review quota] |

**Analysis**:
- Hot endpoints: [List routes with >10% hit rate]
- Quota adjustments needed: [Yes/No - which routes]

---

## Combined Health Score

### Health Score Metrics
- **Combined health score**: [VALUE] (0-1 scale, target >0.85)
- **Components**:
  - Denial rate factor: [VALUE] (40% weight)
  - RL hit rate factor: [VALUE] (40% weight)
  - PDP latency factor: [VALUE] (20% weight)

**Analysis**:
- ✅ Score >0.85 (excellent) | ⚠️ Score 0.70-0.85 (acceptable) | ❌ Score <0.70 (poor)

---

## Traffic Patterns

### Request Volume
- **Requests per second**: [MIN]-[MAX] (range during baseline)
- **Peak traffic**: [VALUE] req/sec at [TIMESTAMP]
- **Lowest traffic**: [VALUE] req/sec at [TIMESTAMP]

### Traffic by Endpoint
Top 5 endpoints by request volume:

| Endpoint | Requests | Req/Sec | Percentage |
|----------|----------|---------|------------|
| [ENDPOINT_1] | [COUNT] | [RATE] | [PERCENT]% |
| [ENDPOINT_2] | [COUNT] | [RATE] | [PERCENT]% |
| [ENDPOINT_3] | [COUNT] | [RATE] | [PERCENT]% |
| [ENDPOINT_4] | [COUNT] | [RATE] | [PERCENT]% |
| [ENDPOINT_5] | [COUNT] | [RATE] | [PERCENT]% |

### Traffic by Time (Hourly Breakdown)
| Hour | Requests | Avg Req/Sec | Denials | 429s |
|------|----------|-------------|---------|------|
| [HH:00] | [COUNT] | [RATE] | [COUNT] | [COUNT] |
| [HH:00] | [COUNT] | [RATE] | [COUNT] | [COUNT] |
| [HH:00] | [COUNT] | [RATE] | [COUNT] | [COUNT] |
| [HH:00] | [COUNT] | [RATE] | [COUNT] | [COUNT] |
| [HH:00] | [COUNT] | [RATE] | [COUNT] | [COUNT] |
| [HH:00] | [COUNT] | [RATE] | [COUNT] | [COUNT] |

**Patterns observed**:
- Peak hours: [TIME_RANGE]
- Low traffic periods: [TIME_RANGE]
- Traffic distribution: [Uniform / Bursty / Cyclical]

---

## Rule Evaluation Coverage

### Rule Evaluation Frequency
- **Rules evaluated per decision**: [VALUE] (average)
- **Total rule evaluations**: [COUNT]
- **Coverage**: [VALUE]% of decisions triggered rule evaluations

**Top 10 most-evaluated rules**:

| Rule ID | Evaluations | Eval/Sec | Effect | Notes |
|---------|-------------|----------|--------|-------|
| [RULE_1] | [COUNT] | [RATE] | [Allow/Deny] | [Expected/Review] |
| [RULE_2] | [COUNT] | [RATE] | [Allow/Deny] | [Expected/Review] |
| [RULE_3] | [COUNT] | [RATE] | [Allow/Deny] | [Expected/Review] |
| ... | ... | ... | ... | ... |

**Analysis**:
- Hot rules (>50% eval rate): [List]
- Unused rules (0 evals): [List or "None"]
- Policy optimization opportunities: [Notes]

---

## Anomalies & Issues

### Observed Issues
- [Issue 1 description, timestamp, resolution]
- [Issue 2 description, timestamp, resolution]
- OR "No anomalies observed during baseline collection"

### Warnings Triggered
- [Alert name, timestamp, duration, resolution]
- OR "No alerts fired during baseline period"

### Unexpected Patterns
- [Pattern description and analysis]
- OR "All patterns within expected ranges"

---

## Prometheus Query Log

### Queries Used for Baseline Collection

```promql
# PDP latency
avg_over_time(guardian:pdp_latency:p50[6h])
avg_over_time(guardian:pdp_latency:p95[6h])
avg_over_time(guardian:pdp_latency:p99[6h])

# Denial rate
avg_over_time(guardian:denial_rate:ratio[6h])
avg_over_time(guardian:denial_rate:by_scope[6h])
topk(10, sum(rate(lukhas_guardian_denied_total[6h])) by (reason))

# Rate limiting
avg_over_time(rl:hit_rate:ratio[6h])
avg_over_time(rl:near_exhaustion:ratio[6h])
avg_over_time(rl:utilization:avg[6h])
max_over_time(rl:utilization:max[6h])

# Health score
avg_over_time(lukhas:guardian_rl:health_score[6h])

# Traffic volume
sum(rate(http_requests_total[6h]))
sum(increase(http_requests_total[6h]))
```

---

## Baseline Assessment

### Overall Health
- **Guardian PDP**: ✅ Healthy | ⚠️ Warning | ❌ Critical
- **Rate Limiting**: ✅ Healthy | ⚠️ Warning | ❌ Critical
- **Combined**: ✅ Healthy | ⚠️ Warning | ❌ Critical

### Readiness for Continued Soak
- **Ready to proceed**: ✅ Yes | ⚠️ With caveats | ❌ No
- **Caveats/Actions**: [List any adjustments needed before continuing]

### Recommendations
1. [Recommendation 1 - e.g., "Monitor denial rate for scope X closely"]
2. [Recommendation 2 - e.g., "Consider increasing quota for /v1/responses endpoint"]
3. [Recommendation 3 - e.g., "Review policy rule efficiency for hot rules"]
4. OR "No adjustments needed; proceed with soak period"

---

## Sign-Off

**Baseline collected by**: [Name/Agent]
**Review date**: YYYY-MM-DD
**Approved for soak continuation**: ✅ Yes | ❌ No

**Reviewer notes**:
[Any additional observations or guidance for soak period monitoring]

---

**Next Steps**:
1. Continue monitoring per [RC_SOAK_MONITORING_PLAN.md](RC_SOAK_MONITORING_PLAN.md)
2. Run daily health checks using `scripts/rc_soak_health_check.sh`
3. Compare daily metrics against this baseline
4. Document deviations in `docs/audits/rc-soak/YYYY-MM-DD-checklist.md`
5. After 48-72h, compile final soak report

---

_Template version: 1.0.0_
_RC Version: v0.9.0-rc_
_Generated: 2025-10-14_
