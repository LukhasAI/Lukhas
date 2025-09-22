# MATRIZ Orchestrator Canary Deployment

Production-ready canary deployment configuration for LUKHAS MATRIZ Orchestrator with automated traffic splitting, health validation, and rollback capabilities.

## Overview

This canary deployment system provides:
- **Automated Traffic Splitting**: Gradual traffic migration from 10% → 25% → 50% → 100%
- **Health Validation**: Comprehensive SLO monitoring at each stage
- **Automatic Rollback**: Failed deployments automatically revert to stable
- **Multi-Platform Support**: Both Kubernetes (Argo Rollouts) and Docker Compose
- **Observability Integration**: Full OTel tracing and Prometheus metrics

## Architecture

```
Production Traffic
       ↓
   Load Balancer (Traefik/Nginx)
       ↓
┌─────────────────────────┐
│   Traffic Splitting     │
├─────────────────────────┤
│ Stable: 90%    │ Canary: 10% │
│ (Current)      │ (New Version)│
└─────────────────────────┘
       ↓               ↓
   Stable Pods     Canary Pods
       ↓               ↓
   Health Checks   Health Checks
   SLO Monitoring  SLO Monitoring
```

## Quick Start

### Kubernetes Deployment (Recommended)

```bash
# Start canary deployment with 10% traffic
./deployment/canary/deploy-canary.sh start --image=v2.1.0 --traffic=10

# Monitor deployment progress
./deployment/canary/deploy-canary.sh status

# Promote to stable (after validation passes)
./deployment/canary/deploy-canary.sh promote

# Rollback if issues detected
./deployment/canary/deploy-canary.sh rollback
```

### Docker Compose Deployment

```bash
# Start canary with Docker Compose
./deployment/canary/deploy-canary.sh start --platform=docker --image=v2.1.0

# Check status
./deployment/canary/deploy-canary.sh status --platform=docker

# Promote or rollback
./deployment/canary/deploy-canary.sh promote --platform=docker
```

## Configuration Files

### Kubernetes Configuration
- **`matriz-canary-deployment.yaml`**: Argo Rollouts configuration with analysis templates
- **Analysis Templates**: Automated SLO validation at each traffic stage
- **Services**: Separate canary and stable services for traffic splitting

### Docker Configuration
- **`docker-compose.canary.yml`**: Multi-service stack with traffic splitting
- **Traefik Integration**: Header-based routing for canary traffic
- **Health Checks**: Container-level health monitoring

## Traffic Progression

The canary deployment follows this automated progression:

| Stage | Traffic % | Duration | Validation |
|-------|-----------|----------|------------|
| 1     | 10%       | 2 min    | Success Rate ≥ 99.5% |
| 2     | 25%       | 5 min    | Success Rate ≥ 99.5% + P95 ≤ 250ms |
| 3     | 50%       | 10 min   | All SLOs + Error Rate ≤ 0.1% |
| 4     | 100%      | Final    | Comprehensive Health Score ≥ 98% |

## SLO Validation

### Success Rate Monitor
```promql
sum(rate(http_requests_total{job="lukhas-matriz-canary",status!~"5.."}[2m])) /
sum(rate(http_requests_total{job="lukhas-matriz-canary"}[2m])) >= 0.995
```

### Latency Monitor (P95 ≤ 250ms)
```promql
histogram_quantile(0.95,
  sum(rate(lukhas_matriz_pipeline_duration_seconds_bucket{job="lukhas-matriz-canary"}[2m])) by (le)
) <= 0.250
```

### Error Rate Monitor (≤ 0.1%)
```promql
sum(rate(http_requests_total{job="lukhas-matriz-canary",status=~"5.."}[2m])) /
sum(rate(http_requests_total{job="lukhas-matriz-canary"}[2m])) <= 0.001
```

### Comprehensive Health Score (≥ 98%)
```promql
(
  (success_rate * 0.4) +
  (latency_compliance * 0.3) +
  (guardian_performance * 0.3)
) >= 0.98
```

## Manual Traffic Control

### Kubernetes (Argo Rollouts)
```bash
# Set specific traffic weight
kubectl argo rollouts set weight lukhas-matriz-orchestrator 20 -n lukhas-ai

# Skip current analysis and proceed
kubectl argo rollouts promote lukhas-matriz-orchestrator -n lukhas-ai

# Abort and rollback
kubectl argo rollouts abort lukhas-matriz-orchestrator -n lukhas-ai
```

### Docker (Traefik Headers)
```bash
# Test canary version
curl -H "X-Canary-Deploy: canary" https://matriz.lukhas.ai/health

# Normal traffic (stable)
curl https://matriz.lukhas.ai/health
```

## Monitoring & Observability

### Grafana Dashboard
Access the MATRIZ performance dashboard to monitor:
- Request rates and error rates by version
- Latency percentiles (P50, P95, P99)
- Success rate trends
- Resource utilization

### OpenTelemetry Traces
Canary deployments include enhanced tracing:
```bash
# Canary spans include deployment metadata
deployment.strategy=canary
service.version=1.1.0
deployment.environment=production
```

### Prometheus Metrics
Key metrics to monitor during canary:
- `http_requests_total{deployment="canary"}`
- `lukhas_matriz_pipeline_duration_seconds{deployment="canary"}`
- `guardian_decision_duration_seconds{deployment="canary"}`

## Troubleshooting

### Common Issues

#### Canary Fails Health Checks
```bash
# Check canary logs
kubectl logs -l app=lukhas-matriz -l version=canary -n lukhas-ai

# Or for Docker
docker logs lukhas-matriz-canary
```

#### Traffic Not Routing to Canary
```bash
# Verify ingress/traefik configuration
kubectl get ingress -n lukhas-ai
kubectl describe ingress lukhas-matriz-ingress -n lukhas-ai

# Test with explicit header
curl -H "X-Canary-Deploy: canary" https://matriz.lukhas.ai/health
```

#### Analysis Failing
```bash
# Check analysis run status
kubectl get analysisrun -n lukhas-ai

# View analysis details
kubectl describe analysisrun <analysis-run-name> -n lukhas-ai
```

### Recovery Procedures

#### Emergency Rollback
```bash
# Immediate rollback to stable
./deployment/canary/deploy-canary.sh rollback

# Or manually for Kubernetes
kubectl argo rollouts abort lukhas-matriz-orchestrator -n lukhas-ai
```

#### Reset Deployment State
```bash
# Clean up and restart
./deployment/canary/deploy-canary.sh cleanup
./deployment/canary/deploy-canary.sh start --image=stable-version
```

## Security Considerations

### Image Validation
- All canary images must pass security scanning
- SHA256 verification required for production images
- Image signatures validated via cosign

### Network Security
- Canary traffic isolated with network policies
- TLS termination at load balancer
- Internal service mesh encryption

### Access Controls
- Deployment operations require proper RBAC
- Canary promotion requires elevated permissions
- Audit logging for all deployment actions

## Advanced Configuration

### Custom Analysis Templates
Create custom analysis templates for specific SLOs:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: custom-business-metric
spec:
  metrics:
  - name: business-metric
    provider:
      prometheus:
        query: custom_business_metric{version="canary"} >= 100
```

### Multi-Region Deployments
For multi-region setups:

```bash
# Deploy to specific region
KUBECTL_CONTEXT=us-east-1 ./deploy-canary.sh start --image=v2.1.0
KUBECTL_CONTEXT=eu-west-1 ./deploy-canary.sh start --image=v2.1.0
```

### Integration with CI/CD
```yaml
# GitHub Actions example
- name: Deploy Canary
  run: |
    ./deployment/canary/deploy-canary.sh start \
      --image=${{ github.sha }} \
      --traffic=5 \
      --monitoring
```

## Performance Impact

### Resource Overhead
- Canary adds ~20% CPU/memory overhead during deployment
- Network traffic increases by 10-15% due to dual routing
- Monitoring overhead: ~5% additional metrics cardinality

### Deployment Timeline
- **Fast Track**: 17 minutes (2+5+10)
- **Standard**: 30 minutes with extended validation
- **Conservative**: 60 minutes with manual approval gates

---

*For detailed operational procedures, see the [LUKHAS Production Deployment Guide](/docs/guides/PRODUCTION_DEPLOYMENT_GUIDE.md).*