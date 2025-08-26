# LUKHAS Enterprise Tools Suite

Production-grade tools for operating LUKHAS AI at scale, with security, observability, and compliance built-in.

## 🛡️ Security Scanner

Comprehensive security vulnerability detection and remediation system.

### Features
- **Multi-layer vulnerability detection**: Python, JavaScript, Docker, system packages
- **Secret scanning**: API keys, passwords, tokens, connection strings
- **SBOM generation**: Software Bill of Materials in CycloneDX format
- **Risk scoring**: Advanced risk assessment based on CVSS scores
- **Auto-remediation**: Safe automatic fixes for known vulnerabilities

### Usage
```python
from tools.enterprise.security_scanner import SecurityScanner

scanner = SecurityScanner()
results = await scanner.scan_complete()

print(f"Vulnerabilities: {results['summary']['total_vulnerabilities']}")
print(f"Secrets Found: {results['summary']['secrets_found']}")
```

### Configuration
```yaml
# security_scanner.yaml
scan_paths:
  - .
exclude_paths:
  - __pycache__
  - node_modules
  - .git
secret_scanning:
  enabled: true
  custom_patterns:
    - type: api_key
      pattern: 'LUKHAS_[A-Z0-9]{32}'
vulnerability_scanning:
  python: true
  javascript: true
  docker: true
auto_fix_threshold: 0.8
```

## 📊 Structured Audit Logger

Enterprise-grade audit logging with compliance and tamper detection.

### Features
- **Structured events**: Type-safe audit events with validation
- **Encryption at rest**: Optional AES encryption for sensitive logs
- **Tamper detection**: Hash chain verification for log integrity
- **Compliance ready**: GDPR/CCPA compliant with configurable retention
- **High performance**: Async I/O with buffering and compression
- **Query interface**: Search and filter historical audit logs

### Usage
```python
from tools.enterprise.structured_audit_logger import AuditLogger, log_login, log_data_access

# Initialize
audit_logger = AuditLogger(
    encryption_key="your-secret-key",
    retention_days=2555  # 7 years
)

# Log events
await log_login(audit_logger, "user123", success=True, ip_address="192.168.1.1")

await log_data_access(
    audit_logger,
    user_id="user123",
    resource_type="memory",
    resource_id="mem_456",
    action="fold_memory",
    tier_level=3
)

# Query logs
events = await audit_logger.query(
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now(),
    actor_id="user123"
)

# Verify integrity
integrity = await audit_logger.verify_integrity(start_date, end_date)
```

### Event Types
- Authentication: login, logout, access control
- Data operations: CRUD, import/export
- System operations: start/stop, config changes, deployments
- Security events: scans, vulnerabilities, key rotations
- Compliance: checks, violations, audit access
- LUKHAS-specific: memory folds, consciousness states, tier access

## 🏥 Health Check System

Comprehensive health monitoring with subsystem checks and intelligent alerting.

### Features
- **Multi-component support**: Database, cache, API, queue, storage, LUKHAS modules
- **Async health checks**: Parallel execution for fast results
- **Prometheus metrics**: Built-in metrics for monitoring
- **Alert callbacks**: Customizable alerting on status changes
- **Historical tracking**: Track health over time
- **Dependency mapping**: Understand component relationships

### Usage
```python
from tools.enterprise.health_check_system import (
    HealthCheckSystem,
    DatabaseHealthCheck,
    RedisHealthCheck,
    HTTPHealthCheck
)

# Initialize
health_system = HealthCheckSystem()

# Register checks
health_system.register_check(
    "database",
    ComponentType.DATABASE,
    DatabaseHealthCheck("postgresql://localhost/lukhas")
)

health_system.register_check(
    "redis",
    ComponentType.CACHE,
    RedisHealthCheck("redis://localhost:6379")
)

# Add alert callback
async def alert_callback(result):
    if result.status == HealthStatus.UNHEALTHY:
        await send_slack_alert(result)

health_system.register_alert_callback(alert_callback)

# Run checks
results = await health_system.check_all()
```

### Metrics Endpoint
```python
# Get Prometheus metrics
metrics = health_system.get_metrics()

# Expose via HTTP
@app.get("/metrics")
async def metrics():
    return Response(metrics, media_type=CONTENT_TYPE_LATEST)
```

## 🔍 Observability System

Real-time monitoring with ML-based anomaly detection and root cause analysis.

### Features
- **ML anomaly detection**: Isolation Forest with time-series features
- **Smart alerting**: Reduce noise with intelligent thresholds
- **Root cause analysis**: Automatic correlation detection
- **Baseline learning**: Hourly and weekly patterns
- **Multi-source metrics**: Prometheus, custom metrics, logs
- **Action suggestions**: Intelligent remediation recommendations

### Usage
```python
from tools.enterprise.observability_system import ObservabilitySystem

config = {
    "prometheus_url": "http://localhost:9090",
    "anomaly_contamination": 0.1,
    "alert_rules": [{
        "name": "memory_fold_latency",
        "metric_query": "lukhas_memory_fold_duration_seconds",
        "threshold": 5.0,
        "comparison": ">",
        "duration": "5m",
        "severity": "warning",
        "ml_enabled": True
    }]
}

obs_system = ObservabilitySystem(config)
await obs_system.initialize()

# Get active alerts
alerts = await obs_system.get_active_alerts()

# Get metrics summary
summary = await obs_system.get_metrics_summary()
```

### LUKHAS-Specific Monitoring
- Memory fold performance
- Consciousness drift detection
- Tier access violations
- Emotional state stability
- Quantum processing efficiency

## 🚀 API Framework

Enterprise API with versioning, type safety, and OpenAPI documentation.

### Features
- **API versioning**: Support v1 (deprecated), v2 (current), v3 (future)
- **Type safety**: Pydantic models with validation
- **OpenAPI/Swagger**: Auto-generated documentation
- **Rate limiting**: Redis-based with configurable limits
- **Request tracing**: Correlation IDs and structured logging
- **Security**: JWT authentication with tier-based access
- **Monitoring**: Prometheus metrics and health checks

### Usage
```python
from tools.enterprise.api_framework import create_app, MemoryFoldRequest

app = create_app({
    "cors_origins": ["https://lukhas.ai"],
    "rate_limit": 100
})

# Example endpoint with full type safety
@app.post("/api/v2/consciousness/reflect",
          response_model=APIResponse[ConsciousnessReflection])
async def reflect(
    request: ReflectionRequest,
    user: Dict = Depends(get_current_user)
) -> APIResponse[ConsciousnessReflection]:
    # Implementation
    pass
```

### Versioning Strategy
- **v1**: Legacy support (deprecated)
- **v2**: Current stable API
- **v3**: Future features (GraphQL, WebSocket)

### Security Features
- JWT token validation
- Tier-based access control
- Rate limiting per API key
- Request signing support
- Audit logging integration

## 🔧 Installation

```bash
# Install all enterprise tools
pip install -r tools/enterprise/requirements.txt

# Install specific tools
pip install pydantic fastapi prometheus-client structlog
```

## 🏗️ Architecture

```
enterprise/
├── security_scanner.py      # Vulnerability detection
├── structured_audit_logger.py # Compliance logging
├── health_check_system.py   # System health monitoring
├── observability_system.py  # Metrics and alerting
├── api_framework.py        # REST API framework
└── requirements.txt        # Dependencies
```

## 🚦 Production Deployment

### Docker Support
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY tools/enterprise /app/enterprise
RUN pip install -r enterprise/requirements.txt

# Run with proper user
RUN useradd -m lukhas
USER lukhas

CMD ["uvicorn", "enterprise.api_framework:app", "--host", "0.0.0.0"]
```

### Environment Variables
```bash
# Security
ENCRYPTION_KEY=your-256-bit-key
JWT_SECRET=your-jwt-secret

# External Services
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:pass@localhost/lukhas
PROMETHEUS_URL=http://localhost:9090

# Monitoring
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
SENTRY_DSN=https://...@sentry.io/...

# LUKHAS Configuration
LUKHAS_TIER_ENFORCEMENT=strict
LUKHAS_AUDIT_LEVEL=verbose
```

## 📈 Monitoring Dashboard

### Grafana Configuration
Import the provided dashboards:
- `dashboards/security-overview.json`
- `dashboards/api-performance.json`
- `dashboards/system-health.json`
- `dashboards/lukhas-specific.json`

### Key Metrics
- API request rate and latency
- Security scan results
- System resource usage
- LUKHAS module performance
- Audit log volume

## 🧪 Testing

```bash
# Run all tests
pytest tools/enterprise/tests/

# Run with coverage
pytest --cov=enterprise --cov-report=html

# Load testing
locust -f tools/enterprise/tests/load_test.py
```

## 📚 Best Practices

1. **Security First**: Always enable encryption for audit logs
2. **Monitor Everything**: Use health checks and observability
3. **Version APIs**: Never break backward compatibility
4. **Type Safety**: Use Pydantic models for all data
5. **Async by Default**: Leverage async/await for performance
6. **Fail Gracefully**: Always have fallback mechanisms
7. **Document APIs**: Keep OpenAPI schemas up to date

## 🤝 Integration with LUKHAS

These tools are designed to integrate seamlessly with LUKHAS core modules:

```python
# Example: Monitoring consciousness drift
from consciousness.systems.engine import LUKHASConsciousnessEngine
from tools.enterprise.observability_system import ObservabilitySystem

# Register consciousness metrics
obs_system.register_metric_source(
    consciousness_engine.get_metrics
)

# Add consciousness-specific alerts
obs_system.add_alert_rule({
    "name": "consciousness_anomaly",
    "metric_query": "lukhas_consciousness_stability",
    "comparison": "anomaly",
    "ml_enabled": True
})
```

## 📄 License

These enterprise tools are part of the LUKHAS AI system and follow the same licensing terms.

---

Built with ❤️ for production LUKHAS deployments.
