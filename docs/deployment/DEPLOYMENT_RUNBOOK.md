# LUKHAS AI Production Deployment Runbook

## Overview

This runbook provides comprehensive procedures for deploying, monitoring, and maintaining LUKHAS AI in production environments.

## 🚀 Deployment Process

### Prerequisites

- Azure CLI installed and configured
- Docker access to `lukhasai.azurecr.io`
- GitHub Actions secrets configured:
  - `AZURE_CREDENTIALS`
  - `AZURE_SUBSCRIPTION_ID`

### Automated Deployment Pipeline

The production deployment follows a comprehensive CI/CD pipeline:

1. **Security Scanning** (Bandit, Safety, Semgrep)
2. **Quality Gate** (Tests, Coverage ≥85%, Linting)
3. **Build Artifacts** (Docker images, Python packages)
4. **Staging Deployment** with smoke tests
5. **Blue-Green Production Deployment**
6. **Monitoring Setup** and alerting configuration

### Manual Deployment Commands

```bash
# Emergency manual deployment
git tag v1.0.0
git push origin v1.0.0

# Manual staging deployment
gh workflow run production-deployment.yml \
  -f environment=staging

# Manual production deployment
gh workflow run production-deployment.yml \
  -f environment=production
```

## 🔧 System Configuration

### Environment Variables

```bash
# Core Configuration
LUKHAS_ID_SECRET="your-32-char-secret-key"
ETHICS_ENFORCEMENT_LEVEL="strict"
DREAM_SIMULATION_ENABLED="true"
QUANTUM_PROCESSING_ENABLED="true"

# API Keys
OPENAI_API_KEY="your-openai-key"
ANTHROPIC_API_KEY="your-anthropic-key"
GOOGLE_API_KEY="your-google-key"
PERPLEXITY_API_KEY="your-perplexity-key"

# Tool Controls
LUKHAS_ENABLE_BROWSER="true"
LUKHAS_ENABLE_CODE_EXEC="true"
LUKHAS_ENABLE_SCHEDULER="true"
LUKHAS_ENABLE_RETRIEVAL="true"

# Performance Tuning
LUKHAS_MAX_CONTENT_SIZE="1048576"
LUKHAS_REQUEST_TIMEOUT="30"
LUKHAS_RATE_LIMIT_REQUESTS="100"

# Database
DATABASE_URL="postgresql://user:pass@host:port/db"
```

### Resource Requirements

#### Minimum Production Requirements
- **CPU**: 4 vCPUs
- **Memory**: 8 GB RAM
- **Storage**: 50 GB SSD
- **Network**: 1 Gbps

#### Recommended Production Requirements
- **CPU**: 8 vCPUs
- **Memory**: 16 GB RAM
- **Storage**: 100 GB SSD
- **Network**: 2 Gbps

## 📊 Monitoring & Alerting

### Key Metrics

#### System Health
- **Response Time**: <250ms (95th percentile)
- **Error Rate**: <0.1%
- **Uptime**: >99.9%
- **Memory Usage**: <80%

#### Guardian System
- **Drift Score**: <0.15 (critical threshold)
- **Response Time**: <100ms
- **Security Violations**: 0 per hour
- **Ethical Compliance**: 100%

#### Tool Executor
- **Execution Success**: >95%
- **Security Blocks**: <5 per hour
- **Timeout Rate**: <1%
- **Resource Usage**: Within limits

### Alert Runbooks

#### 🚨 Critical Alerts

##### Service Down
```bash
# 1. Check service health
curl -f https://lukhas.ai/health

# 2. Check container status
az containerapp show \
  --name lukhas-ai \
  --resource-group Lukhas \
  --query "properties.runningStatus"

# 3. Check recent deployments
az containerapp revision list \
  --name lukhas-ai \
  --resource-group Lukhas

# 4. Initiate rollback if needed
./rollback.sh
```

##### Guardian System Failure
```bash
# 1. Check Guardian-specific health
curl -f https://lukhas.ai/api/guardian/status

# 2. Review Guardian logs
az containerapp logs show \
  --name lukhas-ai \
  --resource-group Lukhas \
  --container lukhas-ai \
  --follow

# 3. Restart Guardian system
curl -X POST https://lukhas.ai/api/guardian/restart

# 4. Verify recovery
curl -f https://lukhas.ai/api/guardian/status
```

##### High Drift Score
```bash
# 1. Check current drift metrics
curl https://lukhas.ai/api/guardian/drift | jq '.'

# 2. Review recent ethical decisions
curl https://lukhas.ai/api/guardian/decisions?limit=10

# 3. Analyze drift sources
curl https://lukhas.ai/api/guardian/drift/analysis

# 4. If critical, enable safe mode
curl -X POST https://lukhas.ai/api/guardian/safe-mode
```

#### ⚠️ Warning Alerts

##### High Response Time
```bash
# 1. Check performance metrics
curl https://lukhas.ai/metrics | grep response_time

# 2. Analyze slow requests
curl https://lukhas.ai/api/performance/slow-requests

# 3. Check resource utilization
az monitor metrics list \
  --resource lukhas-ai \
  --resource-group Lukhas \
  --metric "CpuUsage,MemoryUsage"

# 4. Scale up if needed
az containerapp update \
  --name lukhas-ai \
  --resource-group Lukhas \
  --min-replicas 3 \
  --max-replicas 10
```

## 🔄 Rollback Procedures

### Automated Rollback

```bash
# Emergency rollback script
./rollback.sh

# Or via Azure CLI
az containerapp ingress traffic set \
  --name lukhas-ai \
  --resource-group Lukhas \
  --traffic-weight lukhas-ai-blue=100 lukhas-ai-green=0
```

### Manual Rollback Steps

1. **Identify Last Known Good Version**
   ```bash
   az containerapp revision list \
     --name lukhas-ai \
     --resource-group Lukhas \
     --query "[?properties.active].name" -o tsv
   ```

2. **Switch Traffic**
   ```bash
   az containerapp ingress traffic set \
     --name lukhas-ai \
     --resource-group Lukhas \
     --traffic-weight previous-revision=100
   ```

3. **Verify Rollback**
   ```bash
   # Health check
   curl -f https://lukhas.ai/health

   # Component checks
   curl -f https://lukhas.ai/api/guardian/status
   curl -f https://lukhas.ai/api/tools/status
   ```

4. **Monitor Post-Rollback**
   - Check error rates return to normal
   - Verify all critical alerts clear
   - Monitor for 30 minutes minimum

## 🛠️ Maintenance Procedures

### Regular Maintenance

#### Daily
- Review monitoring dashboards
- Check alert status
- Verify backup completion
- Review drift scores and ethical decisions

#### Weekly
- Update dependencies (security patches)
- Review performance trends
- Analyze capacity requirements
- Update documentation

#### Monthly
- Full system health assessment
- Security audit review
- Capacity planning review
- Disaster recovery testing

### Database Maintenance

```bash
# Database health check
psql $DATABASE_URL -c "
  SELECT
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
  FROM pg_stat_user_tables
  ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC;"

# Vacuum and analyze
psql $DATABASE_URL -c "VACUUM ANALYZE;"

# Check index usage
psql $DATABASE_URL -c "
  SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
  FROM pg_stat_user_indexes
  ORDER BY idx_scan DESC;"
```

## 🔐 Security Procedures

### Security Incident Response

1. **Immediate Response**
   - Enable Guardian safe mode
   - Check security violation logs
   - Review recent tool executions

2. **Investigation**
   ```bash
   # Check security logs
   curl https://lukhas.ai/api/security/audit | jq '.'

   # Review Guardian decisions
   curl https://lukhas.ai/api/guardian/security-events

   # Check tool executor blocks
   curl https://lukhas.ai/api/tools/security-violations
   ```

3. **Containment**
   - Disable affected tools if needed
   - Increase Guardian sensitivity
   - Review and update security policies

### Certificate Management

```bash
# Check certificate expiry
curl -vI https://lukhas.ai 2>&1 | grep "expire date"

# Renew certificates (if needed)
az containerapp ssl upload \
  --name lukhas-ai \
  --resource-group Lukhas \
  --certificate-file cert.pem \
  --certificate-password "password"
```

## 📞 Emergency Contacts

### On-Call Rotation
- **Primary**: DevOps Team Lead
- **Secondary**: Platform Engineering
- **Escalation**: CTO

### Contact Information
- **Slack**: #lukhas-alerts
- **Email**: ops@lukhas.ai
- **Phone**: Emergency hotline (24/7)

### Escalation Matrix
- **P0 (Critical)**: Immediate response, all hands
- **P1 (High)**: 15-minute response time
- **P2 (Medium)**: 2-hour response time
- **P3 (Low)**: Next business day

## 📚 Additional Resources

- **Monitoring Dashboard**: https://grafana.lukhas.ai
- **Log Aggregation**: https://logs.lukhas.ai
- **API Documentation**: https://docs.lukhas.ai
- **Architecture Diagrams**: https://arch.lukhas.ai
- **Status Page**: https://status.lukhas.ai
