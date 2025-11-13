# LUKHAS AI Status Page

Public-facing system status page with real-time Prometheus metrics

## Features

- **Real-time System Health** - Live status indicators from Prometheus
- **API Uptime** - 99.9% uptime tracking
- **Performance Metrics** - p50, p95, p99 latencies
- **Cache Analytics** - Hit rates and performance
- **Task Queue Monitoring** - Queue length and processing rates
- **Incident Timeline** - Historical incidents and maintenance windows

## Quick Start

### Development

```bash
cd products/status_page
python -m http.server 8080
```

Open http://localhost:8080

### Production Deployment

#### Cloudflare Pages

```bash
wrangler pages publish src --project-name lukhas-status
```

#### Vercel

```bash
vercel --prod
```

## Architecture

```
┌──────────────────┐
│  Static HTML/JS  │
└────────┬─────────┘
         │ Fetch metrics
┌────────┴─────────┐
│   Prometheus     │ ← localhost:9090
└────────┬─────────┘
         │
┌────────┴─────────┐
│   LUKHAS API     │ ← Instrumented services
└──────────────────┘
```

## Configuration

Edit `src/config.js` to set Prometheus endpoint:

```javascript
const CONFIG = {
  prometheusUrl: 'http://localhost:9090',
  refreshInterval: 30000, // 30 seconds
  historyDays: 30
};
```

## Success Metrics

- **Page Load**: <1s
- **Auto-refresh**: Every 30s
- **Uptime Display**: 99.9%+
- **Historical Data**: 24h, 7d, 30d views
