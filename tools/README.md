# LUKHAS AI Tools Directory

This directory contains comprehensive tooling for development, testing, monitoring, and deployment of the LUKHAS AI system. The tools are organized into functional categories and designed to work together as a complete DevOps ecosystem.

## Directory Structure

```
tools/
├── testing/                     # Test infrastructure and automation
│   ├── test_infrastructure_monitor.py    # Comprehensive test monitoring
│   ├── coverage_metrics_system.py        # Test coverage analysis
│   └── coverage_metrics.db              # Coverage metrics database
├── monitoring/                  # Production monitoring and alerting
│   ├── production_alerting_system.py     # Main alerting system
│   ├── t4_monitoring_integration.py      # T4 observability integration
│   ├── monitoring_dashboard.py           # Web dashboard interface
│   ├── monitoring_config.json            # Monitoring configuration
│   └── alerts.db                        # Alert history database
├── devops/                     # DevOps and deployment automation
│   ├── automated_deployment_pipeline.py  # Deployment automation
│   ├── deployment_config.json           # Deployment configuration
│   └── infrastructure/                  # Infrastructure as Code
│       ├── Dockerfile                   # Container definition
│       ├── docker-compose.yml           # Multi-service orchestration
│       ├── terraform/                   # AWS infrastructure
│       │   ├── main.tf                  # Main Terraform configuration
│       │   ├── variables.tf             # Input variables
│       │   └── outputs.tf               # Output values
│       ├── kubernetes/                  # Kubernetes manifests
│       │   ├── namespace.yaml           # Namespace definitions
│       │   ├── configmap.yaml           # Configuration maps
│       │   └── deployment.yaml          # Application deployment
│       └── .github/workflows/           # CI/CD pipelines
│           └── ci-cd-pipeline.yml       # GitHub Actions workflow
├── dashboards/                 # Monitoring dashboards
│   └── consciousness_drift_monitor.js   # Real-time drift monitoring
└── README.md                   # This file
```

## Tool Categories

### 🧪 Testing Infrastructure (`testing/`)

**Purpose**: Comprehensive test automation, coverage analysis, and quality assurance.

**Key Components**:
- **Test Infrastructure Monitor**: Real-time monitoring of test execution, resource usage, and performance validation
- **Coverage Metrics System**: Detailed test coverage analysis with database storage, quality gates, and trend reporting
- **Automated Test Execution**: Integration with CI/CD pipelines for continuous quality validation

**Usage**:
```bash
# Run comprehensive test monitoring
python tools/testing/test_infrastructure_monitor.py --monitor

# Generate coverage report
python tools/testing/coverage_metrics_system.py --full-report

# Validate test infrastructure
python tools/testing/test_infrastructure_monitor.py --validate
```

### 📊 Monitoring & Alerting (`monitoring/`)

**Purpose**: Production-ready monitoring, alerting, and observability for LUKHAS AI infrastructure.

**Key Components**:
- **Production Alerting System**: Multi-channel alerting with intelligent escalation and rate limiting
- **T4 Monitoring Integration**: Seamless integration with existing T4 observability stack
- **Monitoring Dashboard**: Web-based real-time system status and alert management interface
- **Alert Management**: Comprehensive alert lifecycle management with acknowledgment and resolution tracking

**Usage**:
```bash
# Start production monitoring system
python tools/monitoring/production_alerting_system.py

# Run integrated T4 monitoring
python tools/monitoring/t4_monitoring_integration.py

# Launch web dashboard
python tools/monitoring/monitoring_dashboard.py

# Generate health report
python tools/monitoring/production_alerting_system.py --health-report
```

### 🚀 DevOps & Deployment (`devops/`)

**Purpose**: Automated deployment pipelines, infrastructure management, and CI/CD orchestration.

**Key Components**:
- **Automated Deployment Pipeline**: Blue-green deployments with rollback capabilities and health checks
- **Infrastructure as Code**: Complete Terraform configurations for AWS deployment
- **Container Orchestration**: Docker and Kubernetes manifests for scalable deployment
- **CI/CD Pipelines**: GitHub Actions workflows for automated testing and deployment

**Usage**:
```bash
# Deploy to staging environment
python tools/devops/automated_deployment_pipeline.py --environment staging

# Deploy to production
python tools/devops/automated_deployment_pipeline.py --environment production

# Infrastructure provisioning
cd tools/devops/infrastructure/terraform
terraform init && terraform plan && terraform apply

# Kubernetes deployment
kubectl apply -f tools/devops/infrastructure/kubernetes/
```

### 📈 Dashboards (`dashboards/`)

**Purpose**: Real-time monitoring interfaces and visualization tools.

**Key Components**:
- **Consciousness Drift Monitor**: WebSocket-based real-time monitoring of system consciousness drift
- **Enhanced Reconnection Logic**: Robust connection management with exponential backoff

## Integration Points

### T4 Observability Stack Integration

The monitoring tools seamlessly integrate with the existing T4 Enterprise Observability Stack:

- **Datadog Integration**: Metrics submission and log correlation
- **Prometheus Support**: Metrics exposure for Prometheus scraping
- **OpenTelemetry Tracing**: Distributed tracing integration
- **Custom Metrics**: LUKHAS-specific metrics for consciousness, memory, and guardian systems

### Testing Infrastructure Integration

Testing tools provide comprehensive quality assurance:

- **Coverage Gates**: Automated quality gates based on coverage thresholds
- **Performance Benchmarks**: Regression testing for performance metrics
- **Resource Monitoring**: Real-time tracking of test execution resources
- **Flaky Test Detection**: Identification and tracking of unreliable tests

### Deployment Pipeline Integration

DevOps tools ensure reliable and automated deployments:

- **Environment Promotion**: Automated progression from development to production
- **Health Checks**: Comprehensive validation of deployed services
- **Rollback Capabilities**: Automatic rollback on deployment failures
- **Secret Management**: Secure handling of sensitive configuration

## Configuration

### Environment Variables

Key environment variables for tool configuration:

```bash
# Monitoring Configuration
export DATADOG_API_KEY="your-datadog-api-key"
export DATADOG_APP_KEY="your-datadog-app-key"
export SLACK_WEBHOOK_URL="your-slack-webhook-url"

# Database Configuration
export DATABASE_URL="postgresql://user:pass@host:port/db"
export REDIS_URL="redis://host:port/db"

# Deployment Configuration
export ENVIRONMENT="production"
export AWS_REGION="us-west-2"
export KUBERNETES_NAMESPACE="lukhas-ai"
```

### Configuration Files

- `tools/monitoring/monitoring_config.json`: Monitoring and alerting configuration
- `tools/devops/deployment_config.json`: Deployment pipeline configuration
- `tools/devops/infrastructure/terraform/variables.tf`: Infrastructure variables

## Security Considerations

### Secrets Management

- All sensitive data is managed through AWS Secrets Manager or Kubernetes Secrets
- No hardcoded credentials in configuration files
- Encrypted storage for database credentials and API keys

### Access Control

- RBAC (Role-Based Access Control) for Kubernetes deployments
- IAM roles and policies for AWS resource access
- Service accounts with minimal required permissions

### Network Security

- VPC isolation for infrastructure components
- Security groups with least-privilege access
- TLS encryption for all network communication

## Monitoring and Alerting

### Alert Rules

The system includes predefined alert rules for:

- **System Resources**: CPU, memory, and disk usage thresholds
- **Application Performance**: Response time and error rate monitoring
- **Test Quality**: Coverage regression and test failure alerts
- **Infrastructure Health**: Service availability and network connectivity

### Escalation Policies

- **Low/Medium Alerts**: Team notification via Slack
- **High Alerts**: Email notification with escalation to on-call engineer
- **Critical Alerts**: Immediate notification through multiple channels

### Metrics Collection

Comprehensive metrics collection for:

- **System Performance**: Resource utilization and response times
- **Business Logic**: LUKHAS-specific consciousness and memory metrics
- **Quality Assurance**: Test coverage and success rates
- **Deployment Health**: Deployment frequency and success rates

## Troubleshooting

### Common Issues

1. **Database Connection Failures**
   - Check database credentials in secrets
   - Verify network connectivity
   - Review security group configurations

2. **Monitoring Dashboard Not Loading**
   - Ensure FastAPI dependencies are installed: `pip install fastapi uvicorn`
   - Check port availability (default: 8080)
   - Verify monitoring database accessibility

3. **Deployment Failures**
   - Review deployment logs in the pipeline output
   - Check health check endpoints
   - Verify container resource limits

4. **Alert Spam**
   - Review alert thresholds in configuration
   - Check rate limiting settings
   - Verify alert cooldown periods

### Log Locations

- **Application Logs**: `/app/logs/` (in containers)
- **Monitoring Logs**: `tools/monitoring/alerts.db`
- **Test Logs**: `tools/testing/coverage_metrics.db`
- **Deployment Logs**: CI/CD pipeline artifacts

### Debug Commands

```bash
# Check monitoring system health
python tools/monitoring/production_alerting_system.py --health-check

# Validate test infrastructure
python tools/testing/test_infrastructure_monitor.py --validate

# Test deployment pipeline
python tools/devops/automated_deployment_pipeline.py --dry-run --environment staging

# Check database connectivity
python -c "from tools.monitoring.production_alerting_system import ProductionAlertingSystem; print('DB OK')"
```

## Development Guidelines

### Adding New Tools

1. Follow the established directory structure
2. Include comprehensive error handling and logging
3. Provide configuration options via JSON files
4. Implement health checks and status endpoints
5. Add integration tests for new functionality

### Code Quality Standards

- **Type Hints**: Use type annotations for all function parameters and return values
- **Documentation**: Include docstrings for all classes and methods
- **Error Handling**: Implement graceful error handling with informative messages
- **Testing**: Minimum 80% test coverage for new code
- **Logging**: Use structured logging with appropriate log levels

### Integration Testing

All tools include integration tests that verify:

- Database connectivity and operations
- External service integrations (Datadog, Slack, etc.)
- Configuration loading and validation
- Error handling and recovery mechanisms

## Support and Maintenance

### Regular Maintenance Tasks

1. **Weekly**: Review alert thresholds and update based on system behavior
2. **Monthly**: Clean up old deployment artifacts and log files
3. **Quarterly**: Update infrastructure configurations and security patches
4. **Annually**: Review and update monitoring and alerting strategies

### Performance Optimization

- Monitor resource usage of monitoring tools themselves
- Optimize database queries and indexing
- Review and tune alert evaluation frequencies
- Implement caching where appropriate

### Version Management

- All tools follow semantic versioning
- Breaking changes require major version increments
- Configuration schema changes are documented in migration guides
- Backward compatibility is maintained for at least one major version

---

This comprehensive tooling ecosystem provides enterprise-grade infrastructure management, monitoring, and deployment capabilities for the LUKHAS AI system. The tools are designed to work together seamlessly while remaining modular enough to be used independently as needed.