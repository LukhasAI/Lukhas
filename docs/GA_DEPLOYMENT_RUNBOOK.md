# LUKHAS AI Platform - GA Deployment Runbook
**Status**: ✅ PRODUCTION-READY  
**Version**: 1.0  
**Last Updated**: October 18, 2025  
**Deployment Type**: General Availability (GA) Release

---

## Executive Summary

This runbook provides comprehensive deployment procedures for the LUKHAS AI Platform GA release. The platform has completed critical validation milestones including RC soak testing (60-hour stability validation), comprehensive dependency audit (196 packages, 0 CVEs), and operational readiness verification.

**GA Readiness Status**: 6/9 Tasks Complete (66.7%)
- ✅ Task 1: OpenAI façade validation
- ✅ Task 2: Guardian MCP server deployment
- ✅ Task 3: OpenAPI schema validation
- ✅ Task 4: RC soak test completion (99.985% success rate)
- ✅ Task 8: Dependency audit trail (0 CVEs, 100% license compliance)
- ✅ Task 9: GA deployment runbook (this document)
- ⏳ Task 5: Comprehensive testing suite (in progress)
- ⏳ Task 6: Security audit (pending)
- ⏳ Task 7: E402 linting cleanup (86/1,226 violations fixed)

**Critical References**:
- **RC Soak Results**: `docs/RC_SOAK_TEST_RESULTS.md` - 60-hour stability validation
- **Dependency Audit**: `docs/DEPENDENCY_AUDIT.md` - 196 packages, security validated
- **Production Compose**: `deployment/docker-compose.production.yml` - Multi-service orchestration
- **Monitoring Config**: `monitoring/prometheus-config.yml` - Observability stack

---

## Table of Contents

1. [Pre-Deployment Checklist](#1-pre-deployment-checklist)
2. [Deployment Architecture](#2-deployment-architecture)
3. [Deployment Procedures](#3-deployment-procedures)
4. [Monitoring & Observability](#4-monitoring--observability)
5. [Rollback Procedures](#5-rollback-procedures)
6. [Incident Response Playbook](#6-incident-response-playbook)
7. [Post-Deployment Verification](#7-post-deployment-verification)
8. [Operational Runbook](#8-operational-runbook)
9. [Emergency Contacts](#9-emergency-contacts)
10. [Appendix](#10-appendix)

---

## 1. Pre-Deployment Checklist

### 1.1 Infrastructure Prerequisites

**Compute Resources** (minimum requirements):
- [ ] **CPU**: 8 vCPUs (16 vCPUs recommended for production)
- [ ] **Memory**: 32 GB RAM (64 GB recommended)
- [ ] **Storage**: 500 GB SSD (1 TB recommended for audit logs)
- [ ] **Network**: 10 Gbps bandwidth, static IP address
- [ ] **DNS**: A/AAAA records configured for primary domain
- [ ] **TLS Certificates**: Valid certificates for HTTPS (Let's Encrypt or commercial)

**Database Prerequisites**:
- [ ] **PostgreSQL 15+**: Initialized with `lukhas` database
- [ ] **Redis 7+**: Configured with password authentication
- [ ] **Backup Strategy**: Automated daily backups configured
- [ ] **High Availability**: Multi-AZ deployment (production only)

**External Services**:
- [ ] **OpenAI API**: Valid API key with o1 model access
- [ ] **Anthropic API**: Valid API key for Claude integration
- [ ] **Sentry**: DSN configured for error tracking
- [ ] **Email Service**: SMTP credentials for notifications

### 1.2 Security Prerequisites

**Secrets Management**:
- [ ] `POSTGRES_PASSWORD`: PostgreSQL admin password (32+ chars)
- [ ] `REDIS_PASSWORD`: Redis authentication password (32+ chars)
- [ ] `JWT_SECRET`: JWT token signing secret (64+ chars, cryptographically random)
- [ ] `ENCRYPTION_KEY`: Data encryption key (base64-encoded 256-bit key)
- [ ] `AUDIT_ENCRYPTION_KEY`: Audit log encryption key (base64-encoded 256-bit key)
- [ ] `FEDERATION_ID`: Unique federation identifier (UUID v4)
- [ ] `GRAFANA_PASSWORD`: Grafana admin password
- [ ] `OPENAI_API_KEY`: OpenAI API key (sk-...)
- [ ] `ANTHROPIC_API_KEY`: Anthropic API key (sk-ant-...)
- [ ] `SENTRY_DSN`: Sentry error tracking DSN

**Secret Generation Commands**:
```bash
# Generate secure passwords
openssl rand -base64 32  # POSTGRES_PASSWORD, REDIS_PASSWORD
openssl rand -hex 64     # JWT_SECRET

# Generate encryption keys
openssl rand -base64 32  # ENCRYPTION_KEY, AUDIT_ENCRYPTION_KEY

# Generate federation ID
uuidgen  # FEDERATION_ID

# Store in secure vault (Kubernetes Secrets, HashiCorp Vault, etc.)
```

**Security Validation**:
- [ ] All secrets stored in secure vault (no plaintext in repos)
- [ ] TLS 1.3 enforced for all external connections
- [ ] Firewall rules configured (allow 80/443, deny all else)
- [ ] SSH access restricted to authorized keys only
- [ ] Security groups/NSGs configured per least privilege principle

### 1.3 Validation Prerequisites

**RC Soak Test Validation** (Task 4):
- [ ] **Test Completion**: October 18, 2025 @ 15:57:03 BST ✅
- [ ] **Test Duration**: ~60 hours sustained load ✅
- [ ] **Error Rate**: 0.015% (31 errors) - PASS ✅
- [ ] **Rate Limit Handling**: 3,783 HTTP 429s handled gracefully ✅
- [ ] **API Stability**: No catastrophic failures ✅
- [ ] **Risk Assessment**: LOW - Production-ready ✅

**Dependency Audit Validation** (Task 8):
- [ ] **Total Dependencies**: 196 unique packages audited ✅
- [ ] **Security Scan**: 0 CVEs identified ✅
- [ ] **Recent Updates**: 5 security patches merged (Oct 2025) ✅
- [ ] **License Compliance**: 100% permissive/weak copyleft ✅
- [ ] **Supply Chain Security**: Hash verification enabled (pip-tools) ✅
- [ ] **Compliance**: GDPR/SOC 2 ready ✅

**Code Quality Gates**:
- [ ] **Syntax Health**: All Python files compile without errors
- [ ] **Import Health**: E402 violations addressed (86/1,226 fixed, ongoing)
- [ ] **Test Coverage**: Core services ≥75% coverage
- [ ] **Security Scan**: Bandit security scan PASS
- [ ] **Type Checking**: mypy validation PASS (critical modules)

### 1.4 Pre-Flight Checks

**30 Minutes Before Deployment**:
```bash
# 1. Validate Docker images
docker pull postgres:15-alpine
docker pull redis:7-alpine
docker pull prom/prometheus:latest
docker pull grafana/grafana:latest
docker pull jaegertracing/all-in-one:latest

# 2. Validate configuration files
cd /path/to/lukhas
docker-compose -f deployment/docker-compose.production.yml config

# 3. Run syntax validation
find . -name "*.py" -path "./lukhas/*" -exec python3 -m py_compile {} \;

# 4. Check disk space (require 100GB+ free)
df -h | grep -E '/$|/var|/opt'

# 5. Validate network connectivity
curl -I https://api.openai.com/v1/models
curl -I https://api.anthropic.com/v1/messages

# 6. Test database connectivity
psql postgresql://lukhas:${POSTGRES_PASSWORD}@postgres-host:5432/lukhas -c "SELECT version();"

# 7. Validate secrets (DO NOT PRINT, just check)
[ -n "$JWT_SECRET" ] && echo "JWT_SECRET: OK" || echo "JWT_SECRET: MISSING"
[ -n "$ENCRYPTION_KEY" ] && echo "ENCRYPTION_KEY: OK" || echo "ENCRYPTION_KEY: MISSING"
```

**Emergency Abort Criteria** (DO NOT DEPLOY IF):
- ❌ Any secret is missing or invalid
- ❌ Disk space < 100 GB free
- ❌ Database connection fails
- ❌ External API connectivity fails (OpenAI, Anthropic)
- ❌ Docker images fail to pull
- ❌ Configuration validation fails

---

## 2. Deployment Architecture

### 2.1 Service Topology

**Constellation Framework Services**:
```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (Nginx)                     │
│                 Port 80 (HTTP) → 443 (HTTPS)                │
└────────────────────────┬────────────────────────────────────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
    ┌──────▼──────┐ ┌───▼────┐ ┌─────▼──────┐
    │ lukhas-core │ │Identity│ │   Memory   │
    │   :8080     │ │ :8081  │ │   :8082    │
    └──────┬──────┘ └───┬────┘ └─────┬──────┘
           │             │             │
    ┌──────▼──────┐ ┌───▼────────────▼──────┐
    │Consciousness│ │    Governance         │
    │   :8083     │ │      :8084            │
    └──────┬──────┘ └───┬──────────────────┘
           │             │
    ┌──────▼─────────────▼──────┐
    │   PostgreSQL + Redis      │
    │   :5432        :6379      │
    └───────────────────────────┘
```

**Monitoring & Observability Stack**:
```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Prometheus   │  │   Grafana    │  │    Jaeger    │
│   :9090      │  │    :3000     │  │   :16686     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                ┌─────────▼─────────┐
                │  Loki + Promtail  │
                │      :3100        │
                └───────────────────┘
```

### 2.2 Service Dependencies

**Startup Order** (critical for clean deployment):
```
1. postgres      (database foundation)
2. redis         (caching & session storage)
3. jaeger        (distributed tracing)
4. lukhas-memory (memory service - required by consciousness)
5. lukhas-identity (identity service - required by core)
6. lukhas-core   (core orchestration)
7. lukhas-consciousness (consciousness processing)
8. lukhas-governance (audit & compliance)
9. lukhas-gateway (nginx API gateway)
10. prometheus   (metrics collection)
11. grafana      (visualization)
12. loki + promtail (log aggregation)
```

**Health Check Endpoints**:
- **lukhas-core**: `GET http://localhost:8080/health`
- **lukhas-identity**: `GET http://localhost:8081/health`
- **lukhas-memory**: `GET http://localhost:8082/health`
- **lukhas-consciousness**: `GET http://localhost:8083/health`
- **lukhas-governance**: `GET http://localhost:8084/health`

### 2.3 Network Configuration

**External Ports** (expose to internet):
- `80` - HTTP (redirect to HTTPS)
- `443` - HTTPS (API gateway)
- `3000` - Grafana UI (restrict to admin IPs)
- `9090` - Prometheus UI (restrict to admin IPs)
- `16686` - Jaeger UI (restrict to admin IPs)

**Internal Ports** (docker network only):
- `5432` - PostgreSQL
- `6379` - Redis
- `8080-8084` - LUKHAS services
- `3100` - Loki
- `4317` - Jaeger OTLP gRPC

**Firewall Rules**:
```bash
# Allow HTTPS traffic
ufw allow 443/tcp

# Allow HTTP (redirect to HTTPS)
ufw allow 80/tcp

# Allow Grafana (restrict to admin IPs)
ufw allow from 203.0.113.0/24 to any port 3000 proto tcp

# Allow SSH (restrict to admin IPs)
ufw allow from 203.0.113.0/24 to any port 22 proto tcp

# Deny all other inbound
ufw default deny incoming
ufw enable
```

---

## 3. Deployment Procedures

### 3.1 Standard Deployment (Blue-Green)

**Blue-Green Deployment Strategy**:
- **Blue Environment**: Current production (serving traffic)
- **Green Environment**: New deployment (staged, not serving traffic)
- **Cutover**: DNS/load balancer switch from blue → green
- **Rollback**: DNS/load balancer switch from green → blue (instant)

**Step-by-Step Procedure**:

#### Phase 1: Green Environment Deployment (30-45 minutes)

```bash
# 1. Clone repository on green environment
cd /opt/lukhas-green
git clone https://github.com/LukhasAI/Lukhas.git
cd Lukhas
git checkout tags/v1.0.0-GA  # Replace with actual GA tag

# 2. Set up environment variables
cat > .env.production << EOF
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}
JWT_SECRET=${JWT_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}
AUDIT_ENCRYPTION_KEY=${AUDIT_ENCRYPTION_KEY}
FEDERATION_ID=${FEDERATION_ID}
GRAFANA_PASSWORD=${GRAFANA_PASSWORD}
DOMAIN=api.lukhas.ai
OPENAI_API_KEY=${OPENAI_API_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
SENTRY_DSN=${SENTRY_DSN}
EOF

# 3. Build Docker images
docker-compose -f deployment/docker-compose.production.yml build --no-cache

# 4. Start infrastructure services (postgres, redis, jaeger)
docker-compose -f deployment/docker-compose.production.yml up -d postgres redis jaeger

# 5. Wait for databases to be ready (30-60 seconds)
echo "Waiting for PostgreSQL..."
until docker exec lukhas-postgres pg_isready -U lukhas -d lukhas; do sleep 2; done

echo "Waiting for Redis..."
until docker exec lukhas-redis redis-cli --raw incr ping; do sleep 2; done

# 6. Run database migrations
docker-compose -f deployment/docker-compose.production.yml run --rm lukhas-core \
  python -m lukhas.db.migrate upgrade head

# 7. Start LUKHAS services (memory → identity → core → consciousness → governance)
docker-compose -f deployment/docker-compose.production.yml up -d \
  lukhas-memory lukhas-identity lukhas-core lukhas-consciousness lukhas-governance

# 8. Wait for services to be healthy (90-120 seconds)
echo "Waiting for services to be healthy..."
for service in lukhas-memory lukhas-identity lukhas-core lukhas-consciousness lukhas-governance; do
  until docker inspect --format='{{.State.Health.Status}}' $service | grep -q "healthy"; do
    echo "Waiting for $service..."
    sleep 5
  done
  echo "$service is healthy!"
done

# 9. Start API gateway
docker-compose -f deployment/docker-compose.production.yml up -d lukhas-gateway

# 10. Start monitoring stack
docker-compose -f deployment/docker-compose.production.yml up -d \
  prometheus grafana loki promtail
```

#### Phase 2: Smoke Testing (15-20 minutes)

```bash
# 1. Health check all services
for port in 8080 8081 8082 8083 8084; do
  echo "Testing localhost:$port/health"
  curl -f http://localhost:$port/health || echo "FAILED: port $port"
done

# 2. Test identity service (ΛID authentication)
curl -X POST http://localhost:8081/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "smoketest", "email": "smoke@test.local"}'

# 3. Test memory service (fold creation)
curl -X POST http://localhost:8082/api/v1/memory/folds \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TEST_JWT}" \
  -d '{"name": "smoke_test_fold", "description": "Deployment smoke test"}'

# 4. Test consciousness service (dream state)
curl -X GET http://localhost:8083/api/v1/consciousness/state \
  -H "Authorization: Bearer ${TEST_JWT}"

# 5. Test governance service (audit trail)
curl -X GET http://localhost:8084/api/v1/governance/audit/recent \
  -H "Authorization: Bearer ${TEST_JWT}"

# 6. Test API gateway (HTTPS)
curl -k https://localhost/health

# 7. Validate monitoring endpoints
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:16686/  # Jaeger UI
```

#### Phase 3: Load Testing (10-15 minutes)

```bash
# 1. Run basic load test (10 req/s for 5 minutes)
# Use the validated RC soak test patterns
cat > load_test.sh << 'EOF'
#!/bin/bash
for i in {1..3000}; do
  curl -X POST http://localhost:8080/api/v1/chat/completions \
    -H "Authorization: Bearer ${TEST_JWT}" \
    -H "Content-Type: application/json" \
    -d '{"model": "o1-preview", "messages": [{"role": "user", "content": "Hello"}]}' &
  sleep 0.1  # 10 req/s
done
wait
EOF

chmod +x load_test.sh
./load_test.sh

# 2. Monitor error rates during load test
docker logs lukhas-core --tail=100 | grep -i error

# 3. Validate rate limit handling (expect some HTTP 429s)
curl http://localhost:9090/api/v1/query \
  --data-urlencode 'query=rate(lukhas_http_requests_total{status="429"}[5m])'
```

#### Phase 4: Production Cutover (5-10 minutes)

```bash
# 1. Update DNS records (or load balancer)
# Blue (old): api-blue.lukhas.ai → 203.0.113.100
# Green (new): api-green.lukhas.ai → 203.0.113.200
# Production: api.lukhas.ai → 203.0.113.200 (switch to green)

# Example: AWS Route 53 CLI
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://dns-cutover.json

# dns-cutover.json:
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "api.lukhas.ai",
      "Type": "A",
      "TTL": 60,
      "ResourceRecords": [{"Value": "203.0.113.200"}]
    }
  }]
}

# 2. Wait for DNS propagation (60-300 seconds, depends on TTL)
watch -n 5 'dig +short api.lukhas.ai'

# 3. Monitor traffic shift
curl http://localhost:9090/api/v1/query \
  --data-urlencode 'query=rate(lukhas_http_requests_total[1m])'

# 4. Validate production traffic on green environment
docker logs lukhas-core --tail=50 | grep "HTTP/1.1 200"
```

#### Phase 5: Blue Environment Decommission (After 24-hour soak)

```bash
# Wait 24 hours to ensure green environment is stable
# Then decommission blue environment

# 1. Stop blue environment services
cd /opt/lukhas-blue/Lukhas
docker-compose -f deployment/docker-compose.production.yml down

# 2. Backup blue environment data (optional)
docker run --rm -v lukhas-blue_postgres-data:/data -v /backups:/backups \
  alpine tar czf /backups/blue-postgres-$(date +%Y%m%d).tar.gz /data

# 3. Remove blue environment (after backup verification)
docker volume rm lukhas-blue_postgres-data lukhas-blue_redis-data
```

### 3.2 Canary Deployment (Gradual Rollout)

**Use Case**: When risk tolerance is LOW and gradual validation is preferred.

**Canary Strategy**:
- **Canary**: 5% traffic → new deployment
- **Production**: 95% traffic → current deployment
- **Gradual Increase**: 5% → 10% → 25% → 50% → 100% over 6-12 hours

**Implementation** (see `deployment/canary/docker-compose.canary.yml`):
```bash
# 1. Deploy canary environment (same as green deployment)
cd /opt/lukhas-canary
# ... (same steps as Phase 1 above)

# 2. Configure load balancer for weighted routing
# Example: Nginx upstream with weight
upstream lukhas_backend {
  server 203.0.113.100:8080 weight=95;  # Production
  server 203.0.113.200:8080 weight=5;   # Canary
}

# 3. Monitor canary error rates
docker logs lukhas-canary-core | grep -i error

# 4. Gradually increase canary weight (every 2 hours)
# 5% → 10% → 25% → 50% → 100%

# 5. If error rate spikes, rollback canary immediately
# (revert load balancer weights to 100% production, 0% canary)
```

### 3.3 Rollback Procedures

**Immediate Rollback Triggers** (execute rollback within 5 minutes):
- ❌ Error rate > 1% for 5 consecutive minutes
- ❌ Service health checks failing (3+ services down)
- ❌ Database connection failures
- ❌ Critical security vulnerability discovered
- ❌ Data corruption detected

**Rollback Procedure** (Blue-Green):
```bash
# 1. Switch DNS back to blue environment
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://dns-rollback.json

# dns-rollback.json: Change api.lukhas.ai A record back to blue IP

# 2. Wait for DNS propagation (60 seconds with low TTL)
watch -n 5 'dig +short api.lukhas.ai'

# 3. Validate traffic shifted back to blue
curl http://blue-api.lukhas.ai/health

# 4. Stop green environment (save logs first)
docker logs lukhas-core > /var/log/lukhas/rollback-$(date +%Y%m%d-%H%M).log
docker-compose -f deployment/docker-compose.production.yml down

# 5. Investigate rollback root cause
grep -i error /var/log/lukhas/rollback-*.log
```

**Rollback Success Criteria**:
- ✅ DNS propagated (100% traffic on blue)
- ✅ Error rate < 0.1%
- ✅ All health checks passing
- ✅ No active incidents

---

## 4. Monitoring & Observability

### 4.1 Prometheus Metrics

**Critical Metrics** (monitor in real-time during deployment):

**Service Health**:
- `up{job="lukhas-core"}` - Service availability (target: 1.0)
- `lukhas_service_health{service="identity|memory|consciousness|governance"}` - Health status

**HTTP Performance**:
- `lukhas_http_requests_total` - Total requests
- `lukhas_http_request_duration_seconds{quantile="0.99"}` - p99 latency (target: <250ms)
- `lukhas_http_requests_total{status="5xx"}` - 5xx error rate (target: <0.1%)
- `lukhas_http_requests_total{status="429"}` - Rate limit events (monitor trends)

**Identity Service** (ΛID):
- `lukhas_identity_auth_duration_seconds{quantile="0.99"}` - Auth latency (target: <100ms)
- `lukhas_identity_active_sessions` - Active user sessions
- `lukhas_identity_auth_failures_total` - Failed authentication attempts

**Memory Service**:
- `lukhas_memory_folds_total` - Total memory folds
- `lukhas_memory_operations_duration_seconds{quantile="0.99"}` - Memory operation latency
- `lukhas_memory_storage_bytes` - Memory storage usage

**Consciousness Service**:
- `lukhas_consciousness_tick_rate` - Consciousness processing rate (target: 10 Hz)
- `lukhas_consciousness_dream_active` - Dream state status
- `lukhas_consciousness_processing_duration_seconds` - Processing latency

**Governance Service**:
- `lukhas_governance_audit_events_total` - Total audit events
- `lukhas_governance_drift_detections_total` - Constitutional drift detections
- `lukhas_governance_compliance_checks_total` - Compliance validation checks

**External API Monitoring**:
- `lukhas_openai_requests_total` - OpenAI API requests
- `lukhas_openai_request_duration_seconds{quantile="0.99"}` - OpenAI latency
- `lukhas_openai_rate_limits_total` - Rate limit events (from RC soak test)

### 4.2 Grafana Dashboards

**Production Dashboards** (configured in `monitoring/grafana/dashboards/`):

1. **LUKHAS Overview Dashboard**:
   - Service health matrix (all 5 services)
   - Request rate & error rate trends
   - p50/p95/p99 latency
   - Active sessions & memory usage

2. **Constellation Framework Dashboard**:
   - Identity: Authentication success/failure rates
   - Memory: Fold creation & retrieval performance
   - Consciousness: Tick rate & dream state visualization
   - Governance: Audit trail volume & drift detection

3. **External API Dashboard**:
   - OpenAI o1 API: Request volume, latency, rate limits
   - Anthropic Claude API: Request volume, latency
   - Combined error rate trends

4. **Infrastructure Dashboard**:
   - Docker container health
   - PostgreSQL connections & query performance
   - Redis memory usage & hit rate
   - System resource utilization (CPU, memory, disk)

**Access**:
- URL: `https://grafana.lukhas.ai`
- Default User: `admin`
- Default Password: `${GRAFANA_PASSWORD}` (from .env.production)

### 4.3 Alerting Rules

**Critical Alerts** (PagerDuty/Slack integration):

**Service Down** (P1 - Page immediately):
```yaml
alert: LUKHASServiceDown
expr: up{job=~"lukhas-.*"} == 0
for: 2m
severity: critical
description: "LUKHAS service {{ $labels.job }} is down for 2 minutes"
```

**High Error Rate** (P1):
```yaml
alert: LUKHASHighErrorRate
expr: rate(lukhas_http_requests_total{status=~"5.."}[5m]) > 0.01
for: 5m
severity: critical
description: "Error rate > 1% for 5 minutes on {{ $labels.service }}"
```

**Identity Service Degraded** (P2):
```yaml
alert: LUKHASIdentityDegraded
expr: lukhas_identity_auth_duration_seconds{quantile="0.99"} > 0.200
for: 5m
severity: warning
description: "Identity auth p99 latency > 200ms (target: <100ms)"
```

**OpenAI Rate Limiting** (P3 - Info only, expected from RC soak test):
```yaml
alert: LUKHASOpenAIRateLimiting
expr: rate(lukhas_openai_rate_limits_total[5m]) > 1
for: 10m
severity: info
description: "OpenAI rate limiting active (expected under burst load)"
```

### 4.4 Log Aggregation (Loki)

**Log Queries** (common production debugging):

```logql
# Find all errors in last 1 hour
{job="lukhas-core"} |= "error" | json | line_format "{{.timestamp}} {{.level}} {{.message}}"

# Identity authentication failures
{job="lukhas-identity"} |= "auth_failure" | json | line_format "{{.user_id}} {{.reason}}"

# Slow requests (>1s)
{job=~"lukhas-.*"} | json | duration > 1s | line_format "{{.method}} {{.path}} {{.duration}}"

# OpenAI API errors
{job="lukhas-core"} |= "openai" |= "error" | json | line_format "{{.timestamp}} {{.error}}"
```

**Access**:
- Loki URL: `http://localhost:3100` (internal only)
- Query via Grafana Explore: `https://grafana.lukhas.ai/explore`

---

## 5. Rollback Procedures

### 5.1 Automated Rollback Triggers

**Critical Thresholds** (auto-rollback if exceeded):
- Error rate > 5% for 3 consecutive minutes
- Service health checks failing (50%+ services down)
- p99 latency > 5 seconds for 5 minutes
- Database connection pool exhausted

**Auto-Rollback Script** (`scripts/auto_rollback.sh`):
```bash
#!/bin/bash
# Automated rollback based on Prometheus alerts

PROM_URL="http://localhost:9090"
ERROR_THRESHOLD=0.05  # 5%
CONSECUTIVE_FAILURES=3

check_error_rate() {
  curl -s "${PROM_URL}/api/v1/query?query=rate(lukhas_http_requests_total{status=~\"5..\"}[1m])" \
    | jq -r '.data.result[0].value[1]'
}

for i in $(seq 1 $CONSECUTIVE_FAILURES); do
  ERROR_RATE=$(check_error_rate)
  if (( $(echo "$ERROR_RATE > $ERROR_THRESHOLD" | bc -l) )); then
    echo "High error rate detected: $ERROR_RATE (threshold: $ERROR_THRESHOLD)"
    echo "Initiating rollback..."
    ./scripts/rollback_dns.sh  # Switch DNS back to blue
    exit 1
  fi
  sleep 60
done
```

### 5.2 Manual Rollback Procedures

**Step 1: Declare Incident** (immediately):
```bash
# 1. Notify team via Slack/PagerDuty
curl -X POST https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK \
  -H "Content-Type: application/json" \
  -d '{"text": "🚨 PRODUCTION ROLLBACK INITIATED - Error rate exceeds threshold"}'

# 2. Update status page
# https://status.lukhas.ai - "Major Service Disruption - Investigating"
```

**Step 2: Execute DNS Cutback** (within 5 minutes):
```bash
# Switch DNS from green → blue (instant rollback)
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://dns-rollback.json

# Verify DNS propagation (60s with TTL=60)
watch -n 5 'dig +short api.lukhas.ai'
```

**Step 3: Preserve Evidence** (before stopping green):
```bash
# 1. Export all logs
for service in lukhas-core lukhas-identity lukhas-memory lukhas-consciousness lukhas-governance; do
  docker logs $service > /var/log/lukhas/rollback-${service}-$(date +%Y%m%d-%H%M).log
done

# 2. Export Prometheus metrics snapshot
curl http://localhost:9090/api/v1/query \
  --data-urlencode 'query=lukhas_http_requests_total' \
  > /var/log/lukhas/rollback-metrics-$(date +%Y%m%d-%H%M).json

# 3. Export database state (if data corruption suspected)
docker exec lukhas-postgres pg_dump -U lukhas lukhas \
  > /backups/rollback-db-$(date +%Y%m%d-%H%M).sql
```

**Step 4: Stop Green Environment** (after evidence preserved):
```bash
cd /opt/lukhas-green/Lukhas
docker-compose -f deployment/docker-compose.production.yml down
```

**Step 5: Validate Blue Environment** (production restored):
```bash
# 1. Check service health
for port in 8080 8081 8082 8083 8084; do
  curl -f http://localhost:$port/health || echo "FAILED: port $port"
done

# 2. Monitor error rates (should be <0.1%)
curl http://localhost:9090/api/v1/query \
  --data-urlencode 'query=rate(lukhas_http_requests_total{status=~"5.."}[5m])'

# 3. Update status page
# https://status.lukhas.ai - "Service Restored - Monitoring Ongoing"
```

### 5.3 Post-Rollback Investigation

**Root Cause Analysis** (RCA process):
1. **Timeline Reconstruction**: Document exact sequence of events (logs, metrics)
2. **Log Analysis**: Identify first error occurrence, propagation pattern
3. **Metric Correlation**: Compare pre-deployment vs deployment metrics
4. **Code Review**: Review changes introduced in failed deployment
5. **Dependency Analysis**: Check for external service failures (OpenAI, Anthropic)

**RCA Template** (`docs/incidents/RCA-YYYY-MM-DD.md`):
```markdown
# Rollback Root Cause Analysis - [Date]

## Incident Summary
- **Date**: YYYY-MM-DD HH:MM UTC
- **Duration**: X minutes (deployment to rollback)
- **Impact**: Error rate spike to X%, latency increase to Y ms
- **Resolution**: DNS rollback to blue environment

## Timeline
- HH:MM - Green deployment started
- HH:MM - Service health checks passing
- HH:MM - Production traffic cutover initiated
- HH:MM - Error rate spike detected (X%)
- HH:MM - Rollback initiated
- HH:MM - Rollback completed, service restored

## Root Cause
[Detailed analysis of what caused the failure]

## Contributing Factors
[Secondary factors that amplified the issue]

## Resolution
[How the issue was resolved (rollback + fixes)]

## Action Items
- [ ] Fix identified bug (owner: @engineer, due: date)
- [ ] Add test coverage for failure scenario (owner: @qa, due: date)
- [ ] Update deployment procedures to prevent recurrence (owner: @sre, due: date)
- [ ] Review similar code patterns for same bug (owner: @team, due: date)

## Lessons Learned
[What we learned from this incident]
```

---

## 6. Incident Response Playbook

### 6.1 Severity Levels

**P1 - Critical** (page on-call engineer immediately):
- Complete service outage (all services down)
- Data corruption or loss
- Security breach or vulnerability exploit
- Error rate > 10% for 5+ minutes

**P2 - High** (notify on-call, 15-minute SLA):
- Partial service degradation (1-2 services down)
- Error rate 1-10% for 5+ minutes
- Database connection failures
- OpenAI/Anthropic API unavailable

**P3 - Medium** (notify during business hours, 1-hour SLA):
- Performance degradation (latency 2-5x normal)
- Single service health check failure
- Non-critical component failures

**P4 - Low** (log for investigation, no immediate action):
- Expected rate limiting (HTTP 429)
- Minor configuration warnings
- Informational alerts

### 6.2 Incident Response Workflow

**Step 1: Detection & Acknowledgment** (0-2 minutes):
```bash
# 1. Acknowledge PagerDuty alert
# 2. Join incident Slack channel (#incident-YYYYMMDD)
# 3. Declare incident commander (IC)
```

**Step 2: Initial Assessment** (2-5 minutes):
```bash
# 1. Check Grafana dashboards
# https://grafana.lukhas.ai/d/overview

# 2. Review recent deployments
git log --oneline --since="1 hour ago"

# 3. Check service health
for port in 8080 8081 8082 8083 8084; do
  curl -f http://localhost:$port/health || echo "FAILED: port $port"
done

# 4. Review error logs (last 100 lines)
docker logs lukhas-core --tail=100 | grep -i error
```

**Step 3: Triage & Decision** (5-10 minutes):
- **Rollback**: If recent deployment, error rate > 5%, or data corruption risk
- **Hotfix**: If configuration issue, external API failure, or minor bug
- **Scale**: If resource exhaustion (CPU, memory, database connections)
- **Monitor**: If transient issue, error rate < 1%, and self-recovering

**Step 4: Execution** (10-30 minutes):
```bash
# Example: Rollback (see Section 5.2)
./scripts/rollback_dns.sh

# Example: Hotfix configuration
kubectl set env deployment/lukhas-core LUKHAS_LOG_LEVEL=debug
kubectl rollout status deployment/lukhas-core

# Example: Scale up
kubectl scale deployment/lukhas-core --replicas=10
```

**Step 5: Validation** (30-40 minutes):
```bash
# 1. Verify error rate normalized
curl http://localhost:9090/api/v1/query \
  --data-urlencode 'query=rate(lukhas_http_requests_total{status=~"5.."}[5m])'

# 2. Check service health
for port in 8080 8081 8082 8083 8084; do
  curl -f http://localhost:$port/health || echo "FAILED: port $port"
done

# 3. Update status page
# https://status.lukhas.ai - "Service Restored - Monitoring Ongoing"
```

**Step 6: Post-Incident Review** (within 24 hours):
- Complete RCA (see Section 5.3)
- Update runbook with lessons learned
- Schedule incident retrospective meeting

### 6.3 Common Incident Scenarios

**Scenario 1: High Error Rate After Deployment**:
```bash
# Symptom: Error rate > 5% within 10 minutes of cutover
# Root Cause: Code bug introduced in new deployment
# Resolution: Immediate DNS rollback to blue environment
# Prevention: Increase canary duration, improve test coverage
```

**Scenario 2: OpenAI API Rate Limiting**:
```bash
# Symptom: HTTP 429 rate limit responses from OpenAI
# Root Cause: Burst traffic exceeds OpenAI rate limits
# Resolution: Implement exponential backoff, reduce request rate
# Prevention: Set rate limit ceiling (10 req/s), add request queuing
# Note: Expected behavior from RC soak test validation
```

**Scenario 3: Database Connection Pool Exhausted**:
```bash
# Symptom: "connection pool exhausted" errors in logs
# Root Cause: Traffic spike, slow queries, or connection leaks
# Resolution: Scale up database connection pool, optimize slow queries
# Prevention: Monitor connection pool usage, set alerts at 80% utilization
```

**Scenario 4: Memory Service Unresponsive**:
```bash
# Symptom: Memory service health checks failing
# Root Cause: PostgreSQL overload, slow fold retrieval queries
# Resolution: Restart memory service, optimize database indices
# Prevention: Add database query performance monitoring, optimize N+1 queries
```

---

## 7. Post-Deployment Verification

### 7.1 Immediate Verification (0-30 minutes)

**Critical Smoke Tests**:
```bash
# 1. Service health (all 5 services)
./scripts/smoke_test_health.sh

# 2. Identity authentication flow
./scripts/smoke_test_identity.sh

# 3. Memory fold creation
./scripts/smoke_test_memory.sh

# 4. Consciousness dream state
./scripts/smoke_test_consciousness.sh

# 5. Governance audit trail
./scripts/smoke_test_governance.sh

# 6. End-to-end chat completion (OpenAI o1)
./scripts/smoke_test_e2e.sh
```

**Monitoring Validation**:
```bash
# 1. Prometheus targets up
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job, health}'

# 2. Grafana datasource connected
curl http://localhost:3000/api/datasources | jq '.[].name'

# 3. Jaeger receiving traces
curl http://localhost:16686/api/services | jq '.data[]'

# 4. Loki receiving logs
curl http://localhost:3100/loki/api/v1/label/__name__/values | jq '.data[]'
```

### 7.2 Short-Term Validation (1-4 hours)

**Performance Benchmarks** (compare to RC soak test baseline):
```bash
# 1. Baseline request latency
# Target: p99 < 250ms (from RC soak test)
curl http://localhost:9090/api/v1/query \
  --data-urlencode 'query=histogram_quantile(0.99, lukhas_http_request_duration_seconds_bucket)'

# 2. Error rate
# Target: < 0.1% (RC soak test: 0.015%)
curl http://localhost:9090/api/v1/query \
  --data-urlencode 'query=rate(lukhas_http_requests_total{status=~"5.."}[1h])'

# 3. Identity auth latency
# Target: p99 < 100ms
curl http://localhost:9090/api/v1/query \
  --data-urlencode 'query=histogram_quantile(0.99, lukhas_identity_auth_duration_seconds_bucket)'
```

**Resource Utilization**:
```bash
# 1. CPU usage per service
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}"

# 2. Memory usage per service
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"

# 3. Database connections
docker exec lukhas-postgres psql -U lukhas -c "SELECT count(*) FROM pg_stat_activity;"

# 4. Redis memory usage
docker exec lukhas-redis redis-cli info memory | grep used_memory_human
```

### 7.3 Long-Term Validation (4-24 hours)

**Stability Metrics** (compare to 60-hour RC soak test):
- **Error Rate Trend**: Should remain < 0.1% for 24 hours
- **Latency Stability**: p99 latency should not increase over time
- **Memory Leaks**: Monitor memory usage growth (should be stable)
- **Connection Leaks**: Database/Redis connections should stabilize

**Soak Test Validation**:
```bash
# Run lightweight 24-hour soak test (1 req/s sustained)
./scripts/soak_test_24h.sh

# Monitor:
# - Error rate trends
# - Memory usage growth
# - Database connection pool utilization
# - OpenAI rate limit events (should be minimal at 1 req/s)
```

**Business Metrics** (validate with product team):
- **User Registrations**: Identity service metrics
- **Memory Fold Creation**: Memory service metrics
- **Chat Completions**: Core service metrics
- **Audit Trail Volume**: Governance service metrics

---

## 8. Operational Runbook

### 8.1 Daily Operations

**Morning Health Check** (9:00 AM UTC, Monday-Friday):
```bash
# 1. Review overnight alerts
# https://grafana.lukhas.ai/alerting/list

# 2. Check service health
./scripts/daily_health_check.sh

# 3. Review error logs (last 24 hours)
docker logs lukhas-core --since=24h | grep -i error | wc -l

# 4. Validate backups completed
ls -lh /backups/postgres-$(date -d yesterday +%Y%m%d)*.tar.gz

# 5. Review OpenAI API usage
curl http://localhost:9090/api/v1/query \
  --data-urlencode 'query=sum(increase(lukhas_openai_requests_total[24h]))'
```

**Weekly Maintenance** (Sunday 02:00-04:00 UTC):
```bash
# 1. Database vacuum & reindex
docker exec lukhas-postgres psql -U lukhas -c "VACUUM ANALYZE;"

# 2. Redis cache cleanup
docker exec lukhas-redis redis-cli FLUSHDB

# 3. Rotate logs (keep 30 days)
find /var/log/lukhas -name "*.log" -mtime +30 -delete

# 4. Prune old Docker images
docker image prune -a --filter "until=168h" -f

# 5. Backup audit logs to cold storage
tar czf /backups/audit-$(date +%Y%m%d).tar.gz /opt/lukhas/audit/
```

### 8.2 Dependency Updates

**Security Updates** (immediate, within 48 hours):
```bash
# 1. Review Dependabot PRs
# https://github.com/LukhasAI/Lukhas/pulls?q=is:pr+author:app/dependabot

# 2. Test security update in staging
git checkout dependabot/pip/fastapi-0.117.2
docker-compose -f deployment/docker-compose.production.yml build
./scripts/smoke_test_all.sh

# 3. Merge & deploy via canary
git checkout main && git merge dependabot/pip/fastapi-0.117.2
# ... (follow canary deployment in Section 3.2)
```

**Quarterly Dependency Audit** (January, April, July, October):
```bash
# 1. Update docs/DEPENDENCY_AUDIT.md (see Task 8)
./scripts/generate_dependency_audit.sh

# 2. Review for major version updates
pip list --outdated

# 3. Plan upgrade strategy (canary deployments for major versions)
```

### 8.3 Disaster Recovery

**Backup Strategy**:
- **PostgreSQL**: Daily full backup + WAL archiving (PITR)
- **Redis**: Daily RDB snapshots
- **Audit Logs**: Weekly cold storage backup (7-year retention)
- **Configuration**: Git repository (immutable history)

**Recovery Procedures**:

**Database Recovery** (in case of corruption):
```bash
# 1. Stop affected services
docker-compose -f deployment/docker-compose.production.yml stop lukhas-core lukhas-identity lukhas-memory lukhas-governance

# 2. Restore PostgreSQL from backup
docker exec -i lukhas-postgres psql -U lukhas -d lukhas < /backups/postgres-20251018.sql

# 3. Verify data integrity
docker exec lukhas-postgres psql -U lukhas -c "SELECT count(*) FROM lukhas_users;"

# 4. Restart services
docker-compose -f deployment/docker-compose.production.yml start lukhas-core lukhas-identity lukhas-memory lukhas-governance
```

**Complete System Recovery** (disaster scenario):
```bash
# 1. Provision new infrastructure (AWS, GCP, Azure)
# 2. Install Docker & Docker Compose
# 3. Restore configuration from Git
git clone https://github.com/LukhasAI/Lukhas.git
cd Lukhas && git checkout tags/v1.0.0-GA

# 4. Restore secrets from vault (HashiCorp Vault, AWS Secrets Manager)
# 5. Restore PostgreSQL from backup
# 6. Deploy via standard deployment procedures (Section 3.1)
# 7. Validate with smoke tests (Section 7.1)
```

---

## 9. Emergency Contacts

**On-Call Rotation** (24/7 coverage):
- **Primary**: PagerDuty escalation policy
- **Backup**: Slack channel `#oncall-lukhas`

**Escalation Matrix**:
| Role | Contact | Escalation Time |
|------|---------|-----------------|
| On-Call Engineer | PagerDuty | Immediate |
| Engineering Lead | [Name] <email@lukhas.ai> | 15 minutes |
| CTO | [Name] <cto@lukhas.ai> | 30 minutes (P1 only) |
| Security Team | [Name] <security@lukhas.ai> | Immediate (security incidents) |
| Infrastructure SRE | [Name] <sre@lukhas.ai> | 15 minutes (infra issues) |

**External Vendors**:
- **OpenAI Support**: https://help.openai.com/en/ (status: https://status.openai.com/)
- **Anthropic Support**: https://support.anthropic.com/ (status: https://status.anthropic.com/)
- **AWS Support**: Premium support (1-hour SLA for urgent cases)
- **Sentry Support**: support@sentry.io

---

## 10. Appendix

### 10.1 Configuration Templates

**Environment Variables Template** (`.env.production`):
```bash
# Database
POSTGRES_PASSWORD=<32+ char secure password>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=lukhas

# Cache
REDIS_PASSWORD=<32+ char secure password>
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Security
JWT_SECRET=<64+ char hex secret>
ENCRYPTION_KEY=<base64-encoded 256-bit key>
AUDIT_ENCRYPTION_KEY=<base64-encoded 256-bit key>

# Federation
FEDERATION_ID=<UUID v4>
DOMAIN=api.lukhas.ai

# External APIs
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
GRAFANA_PASSWORD=<secure password>

# Guardian
LUKHAS_GUARDIAN_ENABLED=true
LUKHAS_COMPLIANCE_FRAMEWORKS=gdpr,ccpa,soc2

# Observability
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus
```

### 10.2 Useful Commands Reference

**Docker Operations**:
```bash
# View logs (last 100 lines)
docker logs lukhas-core --tail=100 --follow

# Execute command in container
docker exec -it lukhas-core bash

# Restart single service
docker-compose -f deployment/docker-compose.production.yml restart lukhas-core

# View resource usage
docker stats
```

**Database Operations**:
```bash
# Connect to PostgreSQL
docker exec -it lukhas-postgres psql -U lukhas -d lukhas

# Check active connections
docker exec lukhas-postgres psql -U lukhas -c "SELECT count(*) FROM pg_stat_activity;"

# Vacuum database
docker exec lukhas-postgres psql -U lukhas -c "VACUUM ANALYZE;"
```

**Monitoring Queries**:
```bash
# Prometheus query CLI
curl 'http://localhost:9090/api/v1/query?query=up' | jq '.data.result'

# Grafana health check
curl http://localhost:3000/api/health

# Jaeger traces
curl http://localhost:16686/api/traces?service=lukhas-core&limit=10
```

### 10.3 Related Documentation

**LUKHAS AI Platform Documentation**:
- **RC Soak Test Results**: [`docs/RC_SOAK_TEST_RESULTS.md`](./RC_SOAK_TEST_RESULTS.md) - 60-hour stability validation
- **Dependency Audit**: [`docs/DEPENDENCY_AUDIT.md`](./DEPENDENCY_AUDIT.md) - 196 packages, security validated
- **Parallel Plan**: `docs/parallel_plan.md` - GA readiness task breakdown
- **Architecture Guide**: `docs/architecture/` - System design & component overview

**External References**:
- **OpenAI o1 API**: https://platform.openai.com/docs/guides/reasoning
- **Anthropic Claude API**: https://docs.anthropic.com/claude/reference/getting-started
- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/
- **Docker Compose**: https://docs.docker.com/compose/

---

**Document Version**: 1.0  
**Author**: LUKHAS AI Development Team  
**Last Updated**: October 18, 2025  
**Review Schedule**: Quarterly (next: January 18, 2026)  
**Maintainer**: SRE Team <sre@lukhas.ai>

---

**Change Log**:
- **2025-10-18**: Initial GA deployment runbook created (Task 9 completion)
- **Future**: Update after first GA deployment with lessons learned
