# LUKHAS  Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Development Deployment](#development-deployment)
4. [Production Deployment](#production-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Configuration Management](#configuration-management)
7. [Monitoring & Observability](#monitoring--observability)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)
10. [Disaster Recovery](#disaster-recovery)

## Prerequisites

### System Requirements

**Development Environment:**
- CPU: 4+ cores
- RAM: 16GB minimum
- Storage: 50GB SSD
- OS: Linux/macOS/Windows with WSL2

**Production Environment:**
- CPU: 16+ cores (32+ recommended)
- RAM: 64GB minimum (128GB recommended)
- Storage: 500GB NVMe SSD
- OS: Ubuntu 20.04 LTS or RHEL 8+

### Software Dependencies

```bash
# Core Requirements
- Python 3.9+
- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 14+
- Redis 7.0+

# Optional (for full deployment)
- Kubernetes 1.25+
- Helm 3.10+
- Prometheus 2.40+
- Grafana 9.0+
```

### API Keys & Credentials

Create `.env` file with required credentials:

```bash
# OpenAI API (required for embeddings)
OPENAI_API_KEY=sk-...

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=lukhas
POSTGRES_USER=lukhas
POSTGRES_PASSWORD=<secure-password>

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=<secure-password>

# Security
JWT_SECRET=<random-256-bit-key>
ENCRYPTION_KEY=<random-256-bit-key>

# Guardian System
GUARDIAN_ETHICS_LEVEL=STRICT
GUARDIAN_CONSENSUS_REQUIRED=3
```

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/lukhas.git
cd lukhas
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Initialize Database

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run migrations
python scripts/init_database.py

# Seed initial data
python scripts/seed_data.py
```

### 4. Start Development Server

```bash
# Start all services
python orchestration/brain/primary_hub.py

# Or use the development script
./scripts/dev_start.sh
```

### 5. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Run tests
pytest tests/
```

## Development Deployment

### Using Docker Compose

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  brain-hub:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
    environment:
      - ENVIRONMENT=development
      - LOG_LEVEL=DEBUG
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: lukhas_dev
      POSTGRES_USER: lukhas
      POSTGRES_PASSWORD: dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass dev_password
    ports:
      - "6379:6379"

  guardian:
    build:
      context: ./governance
    environment:
      - ETHICS_LEVEL=MODERATE
      - DEVELOPMENT_MODE=true
    ports:
      - "8001:8001"

volumes:
  postgres_data:
```

Start development environment:

```bash
# Build and start all services
docker-compose -f docker-compose.dev.yml up --build

# Run in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f brain-hub
```

### Hot Reload Configuration

Enable hot reload for faster development:

```python
# config/development.py
DEBUG = True
RELOAD = True
WORKERS = 1  # Single worker for debugging

# Module hot reload
MODULE_WATCH_PATHS = [
    "consciousness/",
    "memory/",
    "reasoning/",
    "governance/"
]
```

## Production Deployment

### 1. Build Production Images

```dockerfile
# Dockerfile.prod
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY . .

# Create non-root user
RUN useradd -m -u 1000 lukhas && chown -R lukhas:lukhas /app
USER lukhas

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build images:

```bash
# Build all production images
docker build -t lukhas/brain-hub:latest -f Dockerfile.prod .
docker build -t lukhas/guardian:latest -f governance/Dockerfile .
docker build -t lukhas/memory:latest -f memory/Dockerfile .
```

### 2. Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  brain-hub:
    image: lukhas/brain-hub:latest
    restart: always
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    depends_on:
      - postgres
      - redis
      - guardian

  guardian:
    image: lukhas/guardian:latest
    restart: always
    environment:
      - ETHICS_LEVEL=STRICT
      - CONSENSUS_REQUIRED=3
    deploy:
      replicas: 5  # Odd number for consensus

  api-gateway:
    image: lukhas/api-gateway:latest
    restart: always
    ports:
      - "443:443"
    environment:
      - SSL_CERT=/certs/fullchain.pem
      - SSL_KEY=/certs/privkey.pem
    volumes:
      - ./certs:/certs:ro

  postgres:
    image: postgres:14-alpine
    restart: always
    environment:
      POSTGRES_DB: lukhas
      POSTGRES_USER: lukhas
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    secrets:
      - db_password

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass_file /run/secrets/redis_password
    volumes:
      - redis_data:/data
    secrets:
      - redis_password

volumes:
  postgres_data:
  redis_data:

secrets:
  db_password:
    file: ./secrets/db_password.txt
  redis_password:
    file: ./secrets/redis_password.txt
```

### 3. SSL/TLS Configuration

```nginx
# nginx.conf for API Gateway
server {
    listen 443 ssl http2;
    server_name api.lukhas.ai;

    ssl_certificate /certs/fullchain.pem;
    ssl_certificate_key /certs/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://brain-hub:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://brain-hub:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Kubernetes Deployment

### 1. Namespace Setup

```yaml
# k8s/namespaces.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: lukhas-core
---
apiVersion: v1
kind: Namespace
metadata:
  name: lukhas-modules
---
apiVersion: v1
kind: Namespace
metadata:
  name: lukhas-data
```

### 2. Core Deployments

```yaml
# k8s/brain-hub-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: brain-hub
  namespace: lukhas-core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: brain-hub
  template:
    metadata:
      labels:
        app: brain-hub
    spec:
      containers:
      - name: brain-hub
        image: lukhas/brain-hub:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: brain-hub
  namespace: lukhas-core
spec:
  selector:
    app: brain-hub
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 3. Guardian System Deployment

```yaml
# k8s/guardian-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: guardian
  namespace: lukhas-core
spec:
  serviceName: guardian
  replicas: 5
  selector:
    matchLabels:
      app: guardian
  template:
    metadata:
      labels:
        app: guardian
    spec:
      containers:
      - name: guardian
        image: lukhas/guardian:latest
        env:
        - name: ETHICS_LEVEL
          value: "STRICT"
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
```

### 4. Helm Chart

```yaml
# helm/lukhas-/values.yaml
global:
  environment: production
  image:
    registry: docker.io
    tag: latest
    pullPolicy: IfNotPresent

brainHub:
  replicas: 3
  resources:
    requests:
      memory: 2Gi
      cpu: 1000m
    limits:
      memory: 4Gi
      cpu: 2000m

guardian:
  replicas: 5
  ethicsLevel: STRICT
  consensusRequired: 3

postgresql:
  enabled: true
  auth:
    database: lukhas
    username: lukhas
  persistence:
    size: 100Gi
    storageClass: fast-ssd

redis:
  enabled: true
  auth:
    enabled: true
  persistence:
    size: 10Gi

monitoring:
  prometheus:
    enabled: true
  grafana:
    enabled: true
    adminPassword: changeme
```

Deploy with Helm:

```bash
# Add Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install LUKHAS
helm install lukhas- ./helm/lukhas- \
  --namespace lukhas-core \
  --create-namespace \
  --values ./helm/lukhas-/values.yaml
```

## Configuration Management

### Environment-Specific Configs

```python
# config/base.py
class BaseConfig:
    # Core settings
    APP_NAME = "LUKHAS "
    VERSION = "1.0.0"

    # Guardian settings
    GUARDIAN_ENABLED = True
    ETHICS_FRAMEWORK = "multi-framework"

    # Memory settings
    MEMORY_BACKEND = "postgresql"
    MEMORY_CACHE = "redis"
    DNA_HELIX_DRIFT_THRESHOLD = 0.3

    # Module settings
    MODULE_TIMEOUT = 30  # seconds
    MODULE_RETRY_COUNT = 3

# config/production.py
class ProductionConfig(BaseConfig):
    ENVIRONMENT = "production"
    DEBUG = False
    LOG_LEVEL = "INFO"

    # Performance
    WORKERS = 4
    WORKER_CONNECTIONS = 1000

    # Security
    REQUIRE_HTTPS = True
    SESSION_COOKIE_SECURE = True
    HSTS_ENABLED = True
```

### Secret Management

```bash
# Using Kubernetes Secrets
kubectl create secret generic postgres-secret \
  --from-literal=password='your-secure-password' \
  --namespace lukhas-core

# Using HashiCorp Vault
vault kv put secret/lukhas/production \
  postgres_password='your-secure-password' \
  redis_password='another-secure-password' \
  jwt_secret='your-jwt-secret'
```

## Monitoring & Observability

### Prometheus Configuration

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'brain-hub'
    kubernetes_sd_configs:
    - role: pod
      namespaces:
        names:
        - lukhas-core
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_label_app]
      action: keep
      regex: brain-hub

  - job_name: 'guardian'
    kubernetes_sd_configs:
    - role: pod
      namespaces:
        names:
        - lukhas-core
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_label_app]
      action: keep
      regex: guardian
```

### Grafana Dashboards

Key metrics to monitor:

1. **System Health**:
   - Module availability
   - Response times
   - Error rates
   - Guardian approval rates

2. **Performance**:
   - Request throughput
   - Processing latency
   - Memory usage
   - CPU utilization

3. **Business Metrics**:
   - Active users
   - Memory operations
   - Dream engine creativity score
   - Consciousness awareness levels

### Logging Configuration

```python
# logging_config.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/lukhas/app.log',
            'maxBytes': 104857600,  # 100MB
            'backupCount': 10,
            'formatter': 'json'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}
```

## Troubleshooting

### Common Issues

1. **Guardian Rejection Loop**
   ```bash
   # Check Guardian logs
   kubectl logs -n lukhas-core -l app=guardian --tail=100

   # Verify ethics configuration
   kubectl describe configmap guardian-config -n lukhas-core
   ```

2. **Memory Drift Errors**
   ```python
   # Check drift levels
   python scripts/check_memory_drift.py

   # Force repair if needed
   python scripts/repair_memory.py --memory-id <id> --method partial_heal
   ```

3. **Module Communication Failures**
   ```bash
   # Check GLYPH token flow
   kubectl logs -n lukhas-core brain-hub-0 | grep GLYPH

   # Verify module connectivity
   kubectl exec -n lukhas-core brain-hub-0 -- python -c "
   from orchestration.brain import test_connectivity
   test_connectivity.run()
   "
   ```

### Debug Mode

Enable debug mode for detailed diagnostics:

```bash
# Set debug environment
export LUKHAS_DEBUG=true
export LOG_LEVEL=DEBUG

# Enable module tracing
export GLYPH_TRACE=true
export GUARDIAN_VERBOSE=true

# Start with debug flags
python orchestration/brain/primary_hub.py --debug --trace-glyphs
```

## Maintenance

### Regular Tasks

**Daily**:
- Monitor Guardian approval rates
- Check memory drift levels
- Review error logs

**Weekly**:
- Backup PostgreSQL database
- Update module configurations
- Run integration tests

**Monthly**:
- Security updates
- Performance optimization
- Capacity planning review

### Database Maintenance

```bash
# Backup database
pg_dump -h localhost -U lukhas lukhas > backup_$(date +%Y%m%d).sql

# Vacuum and analyze
psql -h localhost -U lukhas -d lukhas -c "VACUUM ANALYZE;"

# Check table sizes
psql -h localhost -U lukhas -d lukhas -c "
SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

### Updates and Upgrades

```bash
# Rolling update in Kubernetes
kubectl set image deployment/brain-hub brain-hub=lukhas/brain-hub:v1.1.0 -n lukhas-core

# Rollback if needed
kubectl rollout undo deployment/brain-hub -n lukhas-core

# Update with Helm
helm upgrade lukhas- ./helm/lukhas- \
  --namespace lukhas-core \
  --values ./helm/lukhas-/values.yaml \
  --atomic \
  --cleanup-on-fail
```

## Disaster Recovery

### Backup Strategy

1. **Database Backups**:
   - Automated daily backups
   - Point-in-time recovery enabled
   - Off-site backup storage

2. **Configuration Backups**:
   ```bash
   # Backup all configs
   kubectl get configmap -n lukhas-core -o yaml > configs_backup.yaml
   kubectl get secret -n lukhas-core -o yaml > secrets_backup.yaml
   ```

3. **Memory Helix Backups**:
   ```python
   # Export all memories
   python scripts/export_memories.py --format json --output backups/memories_$(date +%Y%m%d).json
   ```

### Recovery Procedures

1. **Complete System Recovery**:
   ```bash
   # Restore database
   psql -h localhost -U lukhas -d lukhas < backup_20240115.sql

   # Restore configurations
   kubectl apply -f configs_backup.yaml
   kubectl apply -f secrets_backup.yaml

   # Restart all services
   kubectl rollout restart deployment -n lukhas-core
   ```

2. **Partial Recovery**:
   ```python
   # Restore specific memories
   python scripts/restore_memories.py --input backups/memories_20240115.json --memory-ids mem1,mem2

   # Repair corrupted modules
   python scripts/repair_module.py --module consciousness --check-integrity
   ```

### High Availability Setup

```yaml
# Multi-region deployment
regions:
  primary:
    location: us-east-1
    brain_hub_replicas: 3
    guardian_replicas: 5
  secondary:
    location: eu-west-1
    brain_hub_replicas: 2
    guardian_replicas: 3
  dr:
    location: ap-southeast-1
    brain_hub_replicas: 1
    guardian_replicas: 3
```

## Performance Tuning

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_memory_timestamp ON memories(created_at);
CREATE INDEX idx_glyph_source_target ON glyph_tokens(source_module, target_module);
CREATE INDEX idx_guardian_decisions ON guardian_log(decision, timestamp);

-- Partition large tables
CREATE TABLE memories_2024 PARTITION OF memories
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### Caching Strategy

```python
# Redis caching configuration
CACHE_CONFIG = {
    'memory_ttl': 3600,  # 1 hour
    'glyph_ttl': 300,    # 5 minutes
    'guardian_ttl': 60,  # 1 minute
    'max_connections': 100,
    'connection_pool_kwargs': {
        'max_connections': 50,
        'retry_on_timeout': True
    }
}
```

### Resource Limits

```yaml
# Optimal resource allocation
resources:
  brain_hub:
    requests: {memory: "2Gi", cpu: "1000m"}
    limits: {memory: "4Gi", cpu: "2000m"}
  guardian:
    requests: {memory: "4Gi", cpu: "2000m"}
    limits: {memory: "8Gi", cpu: "4000m"}
  memory:
    requests: {memory: "8Gi", cpu: "1000m"}
    limits: {memory: "16Gi", cpu: "2000m"}
  consciousness:
    requests: {memory: "2Gi", cpu: "500m"}
    limits: {memory: "4Gi", cpu: "1000m"}
```

## Conclusion

This deployment guide provides comprehensive instructions for deploying LUKHAS  in various environments. Key considerations:

1. **Start Simple**: Begin with Docker Compose for development
2. **Scale Gradually**: Move to Kubernetes as needs grow
3. **Monitor Everything**: Use Prometheus/Grafana from day one
4. **Backup Regularly**: Implement automated backup procedures
5. **Test Disaster Recovery**: Practice recovery procedures regularly

For additional support, consult the module-specific documentation or contact the LUKHAS  development team.
