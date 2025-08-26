# LUKHAS  Monitoring Setup Guide 📊

## Overview

The LUKHAS  monitoring system provides comprehensive real-time monitoring for all system components including consciousness, memory, ethics, APIs, and system resources. The monitoring infrastructure is built around the Trinity Framework (⚛️🧠🛡️) and provides both technical metrics and high-level insights.

## Architecture

### Components

1. **Unified Dashboard** (`monitoring/unified_dashboard.py`)
   - Real-time system overview
   - WebSocket-based live updates
   - Mobile-responsive interface
   - Alert management

2. **Meta Dashboard** (`meta_dashboard/dashboard_server.py`)
   - Symbolic system monitoring
   - Drift analysis and visualization
   - Trinity coherence tracking
   - Persona distribution

3. **Metrics Collector** (Built into unified dashboard)
   - Automated data collection
   - Multi-source aggregation
   - Historical data retention
   - Alert generation

4. **Setup Automation** (`monitoring/setup_monitoring.py`)
   - One-command deployment
   - Configuration management
   - Service orchestration
   - Production utilities

## Quick Start

### Prerequisites

```bash
# Required Python packages
pip install fastapi uvicorn websockets psutil pyyaml

# Optional: For advanced monitoring
pip install prometheus-client grafana-api
```

### Basic Setup

1. **Navigate to monitoring directory:**
   ```bash
   cd /Users/agi_dev/LOCAL-REPOS/Lukhas/monitoring
   ```

2. **Run automated setup:**
   ```bash
   # Setup and start all monitoring services
   python3 setup_monitoring.py --start-all --create-scripts --wait
   ```

3. **Access dashboards:**
   - **Unified Dashboard**: http://localhost:3000
   - **Meta Dashboard**: http://localhost:5042
   - **API Metrics**: http://localhost:3000/api/metrics

### Manual Setup

1. **Start Unified Dashboard:**
   ```bash
   python3 unified_dashboard.py
   ```

2. **Start Meta Dashboard (optional):**
   ```bash
   python3 ../meta_dashboard/dashboard_server.py
   ```

## Configuration

### Configuration File

The monitoring system uses `monitoring_config.yaml` for configuration:

```yaml
# Core settings
unified_dashboard:
  enabled: true
  host: "0.0.0.0"
  port: 3000
  refresh_rate: 5

alerting:
  enabled: true
  thresholds:
    drift_critical: 0.8
    memory_usage_high: 85.0
    response_time_slow: 1000
```

### Environment Variables

Set these for production deployment:

```bash
export LUKHAS_API_KEY="your-api-key"
export LUKHAS_MONITORING_API_KEY="monitoring-key"
export PROMETHEUS_ENABLED=true
export GRAFANA_URL="http://localhost:3001"
```

## Dashboard Features

### Unified Dashboard (Primary)

#### Real-time Metrics
- **System Health Score** - Overall system wellness (0-100%)
- **API Performance** - Request rates, response times, error rates
- **Consciousness Status** - Awareness level, processing state
- **Memory System** - Fold count, drift score, integrity
- **Guardian System** - Ethics scores, decision rates
- **Dream Engine** - Active dreams, creativity metrics
- **System Resources** - CPU, memory, disk usage
- **Feature Flags** - Current flag status and counts

#### Interactive Features
- **Live Updates** - 5-second refresh via WebSocket
- **Alert Panel** - Clickable alerts with details
- **Health Indicators** - Color-coded status indicators
- **Historical Trends** - Time-based metric visualization

#### Alert System
- **Real-time Notifications** - Immediate alert display
- **Severity Levels** - Critical, Warning, Info classifications
- **Alert History** - Searchable alert log
- **Automated Responses** - Configurable alert actions

### Meta Dashboard (Secondary)

#### Symbolic Monitoring
- **Drift Analysis** - Multi-dimensional drift tracking
- **Trinity Coherence** - Framework harmony metrics
- **Persona Distribution** - Active persona tracking
- **Entropy Levels** - System entropy monitoring

#### Advanced Features
- **Red Team Mode** - Security testing simulation
- **Trend Analysis** - Historical drift patterns
- **Visual Representations** - Symbolic state visualization

## Metrics Collection

### Data Sources

The monitoring system collects data from:

1. **System Metrics** (via psutil)
   - CPU usage, memory consumption
   - Disk space, network activity
   - Process counts, load averages

2. **API Metrics** (via FastAPI)
   - Request rates and response times
   - Error rates and status codes
   - Endpoint-specific performance

3. **Application Metrics** (via  modules)
   - Consciousness awareness levels
   - Memory fold counts and drift scores
   - Ethics decisions and scores
   - Dream engine activity

4. **Feature Flags** (via flags system)
   - Enabled/disabled flag counts
   - Flag state changes
   - Feature adoption metrics

### Data Storage

- **In-Memory** - Current metrics (fast access)
- **Historical Files** - JSONL format for persistence
- **Configurable Retention** - Automatic cleanup (default: 24 hours)

### Data Format

```json
{
  "timestamp": 1641024000.0,
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 67.8
  },
  "api": {
    "requests_per_second": 23.5,
    "average_response_time": 187
  },
  "consciousness": {
    "awareness_level": 0.78,
    "state": "focused"
  }
}
```

## Alert Configuration

### Alert Types

1. **System Alerts**
   - High CPU/memory usage
   - Disk space warnings
   - Process failures

2. **Application Alerts**
   - Memory drift spikes
   - API performance degradation
   - Ethics violations

3. **Security Alerts**
   - Unauthorized access attempts
   - Guardian interventions
   - Unusual activity patterns

### Threshold Configuration

```yaml
alerting:
  thresholds:
    # System
    cpu_critical: 90.0        # CPU usage %
    memory_critical: 90.0     # Memory usage %

    # Application
    drift_critical: 0.8       # Memory drift score
    response_time_slow: 1000  # API response time (ms)
    error_rate_high: 0.05     # Error rate (5%)

    # Consciousness
    awareness_low: 0.3        # Awareness level

    # Ethics
    ethics_score_low: 0.7     # Ethics score threshold
```

### Notification Channels

Configure multiple notification channels:

```yaml
notifications:
  console: true           # Console output
  file: true             # Log files
  webhook: false         # HTTP webhooks
  email: false           # Email notifications
  slack: false           # Slack integration
```

## Production Deployment

### Systemd Services

Create systemd services for production:

```bash
python3 setup_monitoring.py --create-systemd
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lukhas--dashboard
sudo systemctl start lukhas--dashboard
```

### Docker Deployment

```dockerfile
# Dockerfile for monitoring
FROM python:3.9-slim

WORKDIR /app
COPY monitoring/ /app/
COPY requirements-monitoring.txt /app/

RUN pip install -r requirements-monitoring.txt

EXPOSE 3000
CMD ["python3", "unified_dashboard.py"]
```

```bash
# Build and run
docker build -t lukhas-monitoring .
docker run -d -p 3000:3000 --name lukhas-monitor lukhas-monitoring
```

### Load Balancing

For high-availability deployments:

```yaml
# docker-compose.yml
version: '3.8'
services:
  monitoring-1:
    build: .
    ports:
      - "3001:3000"
  monitoring-2:
    build: .
    ports:
      - "3002:3000"
  nginx:
    image: nginx
    ports:
      - "3000:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

## Integration with External Systems

### Prometheus Integration

Export metrics to Prometheus:

```yaml
integrations:
  prometheus:
    enabled: true
    port: 9090
    metrics_path: "/metrics"
```

Access metrics: http://localhost:9090/metrics

### Grafana Dashboards

Import pre-built dashboards:

1. Enable Grafana integration in config
2. Import dashboard JSON from `monitoring/grafana/`
3. Configure Prometheus as data source

### Slack Notifications

Configure Slack webhooks:

```yaml
integrations:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/..."
    channel: "#lukhas-alerts"
```

## Monitoring Best Practices

### Performance Optimization

1. **Adjust Refresh Rates**
   ```yaml
   refresh_rates:
     metrics: 5      # Main metrics (balance between real-time and performance)
     alerts: 10      # Alert checking
     charts: 15      # Chart updates
   ```

2. **Data Retention Management**
   ```yaml
   data_retention_hours: 24    # Keep 24 hours of data
   cleanup_interval: 6         # Clean up every 6 hours
   ```

3. **Resource Allocation**
   - Monitor monitoring system resources
   - Scale WebSocket connections appropriately
   - Use database for large-scale deployments

### Security Considerations

1. **Enable Authentication**
   ```yaml
   security:
     api_key_required: true
     cors:
       allowed_origins: ["https://your-domain.com"]
   ```

2. **Network Security**
   - Use HTTPS in production
   - Restrict dashboard access to internal networks
   - Regular security audits

3. **Data Protection**
   - Encrypt sensitive metrics
   - Regular backup of configuration
   - Access logging and auditing

## Troubleshooting

### Common Issues

1. **Dashboard not loading**
   - Check if services are running: `python3 scripts/monitoring_status.py`
   - Verify port availability: `netstat -tlnp | grep 3000`
   - Check logs: `tail -f logs/monitoring.log`

2. **WebSocket connection failures**
   - Firewall blocking WebSocket ports
   - Reverse proxy configuration issues
   - Browser security settings

3. **Missing metrics data**
   - Module import errors
   - Permission issues accessing system metrics
   - Configuration file syntax errors

### Debug Mode

Enable debug mode for troubleshooting:

```yaml
development:
  debug_mode: true
  verbose_logging: true
```

### Log Analysis

Check different log files:

```bash
# Main application logs
tail -f logs/monitoring.log

# Metrics collection logs
tail -f logs/metrics.log

# Alert system logs
tail -f logs/alerts.log

# Error logs
tail -f logs/errors.log
```

## API Reference

### REST Endpoints

```http
GET /health                 # Health check
GET /api/metrics           # Current metrics
GET /api/alerts            # Current alerts
GET /api/history?hours=24  # Historical data
```

### WebSocket API

```javascript
// Connect to real-time updates
const ws = new WebSocket('ws://localhost:3000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Metrics update:', data);
};
```

## Extending the Monitoring System

### Adding Custom Metrics

1. **Extend MetricsCollector class:**
   ```python
   async def _collect_custom_metrics(self):
       return {
           "custom_metric": get_custom_value(),
           "business_kpi": calculate_kpi()
       }
   ```

2. **Add to dashboard:**
   ```html
   <div class="metric-card">
       <div class="card-title">Custom Metric</div>
       <div class="metric-value" id="custom-metric">--</div>
   </div>
   ```

### Creating Custom Dashboards

1. **Create HTML template:**
   ```html
   <!-- custom_dashboard.html -->
   <div class="custom-panel">
       <h2>Custom Monitoring Panel</h2>
       <div id="custom-content"></div>
   </div>
   ```

2. **Add route:**
   ```python
   @app.get("/custom")
   async def custom_dashboard():
       return HTMLResponse(content=custom_template)
   ```

## Support and Resources

### Documentation
- **Full API Documentation**: `/docs/API_REFERENCE.md`
- **Architecture Overview**: `/docs/ARCHITECTURE.md`
- **Configuration Reference**: `monitoring_config.yaml`

### Support Channels
- **GitHub Issues**: Report bugs and feature requests
- **Discord Community**: Real-time support and discussions
- **Documentation Wiki**: Community-maintained guides

### Contributing
- **Code Contributions**: Submit pull requests
- **Documentation**: Help improve guides
- **Testing**: Test in different environments
- **Feedback**: Share monitoring experiences

---

**Version**: 2.0.0
**Last Updated**: January 2025
**Trinity Framework**: ⚛️🧠🛡️
**Status**: Production Ready ✅
