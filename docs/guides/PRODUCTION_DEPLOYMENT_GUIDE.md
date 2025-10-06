---
status: wip
type: documentation
---
# LUKHAS  Production Deployment Guide 🚀

## Overview

This guide provides comprehensive instructions for deploying LUKHAS  in a production environment. It covers infrastructure setup, security hardening, performance optimization, monitoring, and maintenance procedures.

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 4 cores (8 recommended)
- RAM: 8GB (16GB recommended)
- Storage: 50GB SSD (100GB recommended)
- Network: 100Mbps (1Gbps recommended)
- OS: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+

**Recommended Production Setup:**
- CPU: 8-16 cores
- RAM: 32-64GB
- Storage: 200GB+ NVMe SSD
- Network: 10Gbps
- Load balancer ready
- Database: PostgreSQL cluster

### Software Dependencies

```bash
# System packages
sudo apt update
sudo apt install -y \
    python3.9 python3.9-dev python3.9-venv \
    postgresql-client redis-tools nginx \
    supervisor htop iotop nethogs \
    curl wget git unzip

# Python dependencies
pip3 install --upgrade pip setuptools wheel
pip3 install -r requirements.txt
pip3 install -r requirements-prod.txt
```

## Infrastructure Setup

### 1. Server Preparation

```bash
# Create dedicated user
sudo useradd -m -s /bin/bash lukhas
sudo usermod -aG sudo lukhas

# Setup directory structure
sudo mkdir -p /opt/lukhas-
sudo chown lukhas:lukhas /opt/lukhas-

# Switch to lukhas user
sudo su - lukhas
cd /opt/lukhas-

# Clone repository
git clone https://github.com/your-org/lukhas-.git
cd lukhas-
```

### 2. Environment Configuration

```bash
# Create production environment file
cp .env.example .env.production

# Edit configuration
nano .env.production
```

**Production Environment Variables:**
```bash
# Application
LUKHAS_ENV=production
LUKHAS_DEBUG=false
LUKHAS_SECRET_KEY=your-super-secure-secret-key-here

# API Configuration
LUKHAS_API_HOST=0.0.0.0
LUKHAS_API_PORT=8080
LUKHAS_API_WORKERS=4

# Database
DATABASE_URL=postgresql://lukhas:password@localhost:5432/lukhas
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50

# Security
LUKHAS_API_KEY=your-secure-api-key
JWT_SECRET_KEY=your-jwt-secret-key
CORS_ORIGINS=https://your-domain.com,https://api.your-domain.com

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
LOG_LEVEL=INFO

# Performance
LUKHAS_CACHE_TTL=300
LUKHAS_MAX_CONCURRENT_REQUESTS=1000
LUKHAS_REQUEST_TIMEOUT=30

# Feature Flags
LUKHAS_FLAG_ADAPTIVE_AI=true
LUKHAS_FLAG_DREAM_ENGINE=true
LUKHAS_FLAG_GUARDIAN_SYSTEM=true
LUKHAS_FLAG_QUANTUM_PROCESSING=false
```

### 3. Database Setup

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres createuser lukhas
sudo -u postgres createdb lukhas -O lukhas
sudo -u postgres psql -c "ALTER USER lukhas PASSWORD 'secure-password';"

# Configure PostgreSQL for production
sudo nano /etc/postgresql/13/main/postgresql.conf
```

**PostgreSQL Optimizations:**
```ini
# Memory
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 512MB
work_mem = 256MB

# Connections
max_connections = 200
shared_preload_libraries = 'pg_stat_statements'

# Logging
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on

# Performance
random_page_cost = 1.1
seq_page_cost = 1.0
```

### 4. Redis Setup

```bash
# Install Redis
sudo apt install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
```

**Redis Configuration:**
```ini
# Memory
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Network
bind 127.0.0.1
port 6379
timeout 300

# Security
requirepass your-redis-password
```

## Application Deployment

### 1. Python Virtual Environment

```bash
# Create virtual environment
python3.9 -m venv /opt/lukhas-/venv

# Activate and install dependencies
source /opt/lukhas-/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-prod.txt

# Install production-specific packages
pip install gunicorn supervisor psycopg2-binary redis
```

### 2. Database Migration

```bash
# Run database migrations
source .env.production
python manage.py migrate

# Create initial data
python manage.py create_admin_user
python manage.py load_initial_data
```

### 3. Performance Optimization Setup

```bash
# Run performance optimization
cd performance
python setup_performance.py

# Run optimization analysis
python optimization_analysis.py

# Apply optimizations
source ../venv/bin/activate
python -c "from optimizations import setup_optimizations; setup_optimizations()"
```

### 4. Application Configuration

Create production configuration file:

```bash
# Create production config
nano lukhas_config.production.yaml
```

**Production Configuration:**
```yaml
# Core Application
app:
  debug: false
  testing: false
  host: "0.0.0.0"
  port: 8080
  workers: 4
  worker_class: "uvicorn.workers.UvicornWorker"
  max_requests: 10000
  max_requests_jitter: 1000
  timeout: 30

# Database Configuration
database:
  url: "${DATABASE_URL}"
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  pool_recycle: 3600
  echo: false

# Caching
cache:
  backend: "redis"
  url: "${REDIS_URL}"
  default_timeout: 300
  max_entries: 10000

# Security
security:
  secret_key: "${LUKHAS_SECRET_KEY}"
  api_key_required: true
  cors_origins:
    - "https://your-domain.com"
    - "https://api.your-domain.com"
  rate_limiting:
    enabled: true
    requests_per_minute: 1000
    burst_size: 100

# Monitoring
monitoring:
  prometheus:
    enabled: true
    port: 9090
  grafana:
    enabled: true
    port: 3001
  logging:
    level: "INFO"
    format: "json"
    file: "/var/log/lukhas-/app.log"
    max_bytes: 10485760
    backup_count: 5

# Performance
performance:
  async_workers: 10
  thread_pool_size: 20
  connection_pool_size: 50
  cache_ttl: 300
  request_timeout: 30
```

## Web Server Setup

### 1. Nginx Configuration

```bash
# Install Nginx
sudo apt install nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/lukhas-
```

**Nginx Configuration:**
```nginx
upstream lukhas_app {
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;  # If running multiple workers
    server 127.0.0.1:8082;
    server 127.0.0.1:8083;
}

server {
    listen 80;
    server_name api.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/your-domain.pem;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Logging
    access_log /var/log/nginx/lukhas--access.log;
    error_log /var/log/nginx/lukhas--error.log;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    limit_req zone=api burst=20 nodelay;

    # Main application
    location / {
        proxy_pass http://lukhas_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # WebSocket support for monitoring
    location /ws {
        proxy_pass http://lukhas_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Static files
    location /static/ {
        alias /opt/lukhas-/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/lukhas- /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. SSL Certificate Setup

```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Process Management

### 1. Systemd Services

Create systemd service file:

```bash
sudo nano /etc/systemd/system/lukhas-.service
```

**Systemd Service Configuration:**
```ini
[Unit]
Description=LUKHAS  Application
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=notify
User=lukhas
Group=lukhas
WorkingDirectory=/opt/lukhas-
Environment=PATH=/opt/lukhas-/venv/bin
EnvironmentFile=/opt/lukhas-/.env.production
ExecStart=/opt/lukhas-/venv/bin/gunicorn lukhas.main:app \
    --bind 0.0.0.0:8080 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --max-requests 10000 \
    --max-requests-jitter 1000 \
    --timeout 30 \
    --keepalive 2 \
    --access-logfile /var/log/lukhas-/access.log \
    --error-logfile /var/log/lukhas-/error.log \
    --log-level info
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

### 2. Monitoring Service

```bash
sudo nano /etc/systemd/system/lukhas--monitoring.service
```

```ini
[Unit]
Description=LUKHAS  Monitoring Dashboard
After=network.target lukhas-.service
Wants=lukhas-.service

[Service]
Type=simple
User=lukhas
Group=lukhas
WorkingDirectory=/opt/lukhas-/monitoring
Environment=PATH=/opt/lukhas-/venv/bin
EnvironmentFile=/opt/lukhas-/.env.production
ExecStart=/opt/lukhas-/venv/bin/python unified_dashboard.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3. Start Services

```bash
# Create log directory
sudo mkdir -p /var/log/lukhas-
sudo chown lukhas:lukhas /var/log/lukhas-

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable lukhas-
sudo systemctl enable lukhas--monitoring
sudo systemctl start lukhas-
sudo systemctl start lukhas--monitoring

# Check status
sudo systemctl status lukhas-
sudo systemctl status lukhas--monitoring
```

## Monitoring & Observability

### 1. Prometheus Setup

```bash
# Install Prometheus
sudo useradd --no-create-home --shell /bin/false prometheus
sudo mkdir /etc/prometheus /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus /var/lib/prometheus

# Download and install
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xzf prometheus-2.40.0.linux-amd64.tar.gz
sudo cp prometheus-2.40.0.linux-amd64/prometheus /usr/local/bin/
sudo cp prometheus-2.40.0.linux-amd64/promtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/prometheus /usr/local/bin/promtool
```

**Prometheus Configuration (`/etc/prometheus/prometheus.yml`):**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "lukhas_rules.yml"

scrape_configs:
  - job_name: 'lukhas-'
    static_configs:
      - targets: ['localhost:8080']
    scrape_interval: 5s
    metrics_path: /metrics

  - job_name: 'lukhas-monitoring'
    static_configs:
      - targets: ['localhost:3000']
    scrape_interval: 10s

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093
```

### 2. Grafana Setup

```bash
# Install Grafana
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt update
sudo apt install grafana

# Configure Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

### 3. Log Management

```bash
# Install log rotation
sudo nano /etc/logrotate.d/lukhas-
```

```
/var/log/lukhas-/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 lukhas lukhas
    postrotate
        systemctl reload lukhas-
    endscript
}
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow necessary ports
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow from specific IPs only
sudo ufw allow from YOUR_MONITORING_IP to any port 9090  # Prometheus
sudo ufw allow from YOUR_ADMIN_IP to any port 3001      # Grafana

sudo ufw enable
```

### 2. System Security

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install security updates automatically
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Configure SSH security
sudo nano /etc/ssh/sshd_config
```

**SSH Security Configuration:**
```ini
# Disable root login
PermitRootLogin no

# Use key-based auth only
PasswordAuthentication no
PubkeyAuthentication yes

# Limit users
AllowUsers lukhas

# Security settings
Protocol 2
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
```

### 3. Application Security

```bash
# Set proper file permissions
sudo chmod 750 /opt/lukhas-
sudo chmod 640 /opt/lukhas-/.env.production
sudo chmod +x /opt/lukhas-/venv/bin/*

# Secure sensitive files
sudo chown root:lukhas /opt/lukhas-/.env.production
sudo chmod 640 /opt/lukhas-/.env.production
```

## Backup Strategy

### 1. Database Backup

```bash
# Create backup script
sudo nano /opt/lukhas-/scripts/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/lukhas-"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="lukhas"

mkdir -p $BACKUP_DIR

# Database backup
pg_dump $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_backup_$DATE.sql.gz"
```

### 2. Application Backup

```bash
# Application backup script
sudo nano /opt/lukhas-/scripts/backup_app.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/lukhas-"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/opt/lukhas-"

mkdir -p $BACKUP_DIR

# Backup configuration and logs
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    $APP_DIR

# Keep only last 7 days for app backups
find $BACKUP_DIR -name "app_backup_*.tar.gz" -mtime +7 -delete

echo "Application backup completed: app_backup_$DATE.tar.gz"
```

### 3. Automated Backup

```bash
# Add to crontab
crontab -e
```

```cron
# Daily database backup at 2 AM
0 2 * * * /opt/lukhas-/scripts/backup_db.sh

# Weekly application backup at 3 AM Sunday
0 3 * * 0 /opt/lukhas-/scripts/backup_app.sh
```

## Deployment Checklist

### Pre-Deployment

- [ ] Server provisioned with adequate resources
- [ ] DNS records configured
- [ ] SSL certificates obtained
- [ ] Database server prepared
- [ ] Redis server configured
- [ ] Firewall rules configured
- [ ] Monitoring infrastructure ready

### Deployment Steps

- [ ] Code deployed to production server
- [ ] Dependencies installed
- [ ] Environment configuration completed
- [ ] Database migrations executed
- [ ] Static files collected
- [ ] Services configured and started
- [ ] Nginx configured and restarted
- [ ] SSL certificates installed

### Post-Deployment

- [ ] Health checks passing
- [ ] Monitoring dashboards operational
- [ ] Log rotation configured
- [ ] Backup scripts tested
- [ ] Performance optimization applied
- [ ] Security hardening completed
- [ ] Load testing executed
- [ ] Documentation updated

## Maintenance Procedures

### Daily Maintenance

1. **Health Monitoring**
   ```bash
   # Check service status
   sudo systemctl status lukhas-
   sudo systemctl status lukhas--monitoring

   # Check application health
   curl https://api.your-domain.com/health

   # Monitor logs for errors
   sudo tail -f /var/log/lukhas-/error.log
   ```

2. **Resource Monitoring**
   ```bash
   # System resources
   htop
   df -h
   free -h

   # Database connections
   sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

   # Redis memory
   redis-cli info memory
   ```

### Weekly Maintenance

1. **Log Analysis**
   ```bash
   # Analyze error patterns
   grep ERROR /var/log/lukhas-/*.log | tail -100

   # Check performance metrics
   grep "slow query" /var/log/lukhas-/*.log
   ```

2. **Security Updates**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade

   # Update Python dependencies
   source venv/bin/activate
   pip list --outdated
   ```

### Monthly Maintenance

1. **Performance Review**
   - Review Grafana dashboards
   - Analyze database performance
   - Check for memory leaks
   - Optimize queries if needed

2. **Backup Verification**
   - Test database restore
   - Verify backup completeness
   - Update backup retention policies

3. **Capacity Planning**
   - Review resource usage trends
   - Plan for scaling needs
   - Update monitoring thresholds

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer Setup**
   ```bash
   # HAProxy configuration for multiple app servers
   backend lukhas_servers
       balance roundrobin
       server app1 10.0.1.10:8080 check
       server app2 10.0.1.11:8080 check
       server app3 10.0.1.12:8080 check
   ```

2. **Database Clustering**
   - PostgreSQL streaming replication
   - Read replicas for scaling reads
   - Connection pooling (PgBouncer)

3. **Caching Layer**
   - Redis cluster setup
   - CDN for static assets
   - Application-level caching

### Vertical Scaling

1. **Resource Optimization**
   - Increase server CPU/RAM
   - Optimize database configuration
   - Tune application workers

2. **Performance Tuning**
   - Database query optimization
   - Connection pool sizing
   - Garbage collection tuning

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   ```bash
   # Check memory usage
   ps aux --sort=-%mem | head

   # Restart services if needed
   sudo systemctl restart lukhas-
   ```

2. **Database Connection Issues**
   ```bash
   # Check database connections
   sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

   # Restart database if needed
   sudo systemctl restart postgresql
   ```

3. **High Response Times**
   ```bash
   # Check application logs
   grep "slow" /var/log/lukhas-/*.log

   # Monitor system resources
   iotop
   nethogs
   ```

### Emergency Procedures

1. **Service Recovery**
   ```bash
   # Restart all services
   sudo systemctl restart lukhas-
   sudo systemctl restart lukhas--monitoring
   sudo systemctl restart nginx
   ```

2. **Database Recovery**
   ```bash
   # Restore from backup
   gunzip db_backup_YYYYMMDD_HHMMSS.sql.gz
   sudo -u postgres psql lukhas < db_backup_YYYYMMDD_HHMMSS.sql
   ```

3. **Emergency Contacts**
   - System Administrator: [contact info]
   - Database Administrator: [contact info]
   - Development Team Lead: [contact info]

---

**Last Updated**: January 2025
**Version**: 1.0.0
**Status**: Production Ready ✅
