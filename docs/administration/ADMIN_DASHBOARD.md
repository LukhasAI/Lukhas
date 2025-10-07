---
status: wip
type: documentation
owner: unknown
module: administration
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# Admin Dashboard Documentation

The LUKHAS  Admin Dashboard provides real-time monitoring, performance tracking, and incident management capabilities.

## Overview

The admin dashboard is accessible at `/admin` and requires API key authentication. It provides:
- Safety mode distribution monitoring
- Tool usage statistics
- Performance p95 trend visualization
- Incident tracking with filters
- CSV export capabilities

## Configuration

### Enable Dashboard
```bash
export FLAG_ADMIN_DASHBOARD=true
export LUKHAS_API_KEY=your-secure-api-key
```

### Performance Monitoring
```bash
export FLAG_OPS_PERF_INGEST=true
export LUKHAS_PERF_DIR=.lukhas_perf  # Optional, defaults to .lukhas_perf
```

## Features

### 1. Overview Page (`/admin`)

The main dashboard displays:
- **Safety Modes (24h)**: Distribution of strict/balanced/creative mode usage
- **Tool Usage (24h)**: Per-tool call counts, success/error rates, p95 latencies
- **Performance Trends**: Sparkline charts for endpoint p95 response times
- **Export Links**: Quick access to CSV downloads

### 2. Performance p95 Trends

#### Setup
1. Enable the feature flag: `FLAG_OPS_PERF_INGEST=true`
2. Set API key: `LUKHAS_API_KEY=your-key`
3. Configure CI to post k6 summaries to `/ops/perf/k6`

#### CI Integration
Add this step to your k6 performance test workflow:
```bash
curl -s -H "x-api-key: $LUKHAS_API_KEY" \
     -H "content-type: application/json" \
     -X POST http://127.0.0.1:8000/ops/perf/k6 \
     --data-binary @out/k6_summary.json
```

#### Viewing Trends
- Navigate to `/admin?hours=24` for 24-hour view
- Navigate to `/admin?hours=168` for 7-day view
- Sparklines automatically appear when data is available
- Shows trends for `/feedback/health`, `/tools/registry`, `/openapi.json`

### 3. Incidents Page (`/admin/incidents`)

#### Filters
- **Time Window**: `?since_hours=24` (24h) or `?since_hours=168` (7d)
- **Tool Filter**: `?tool=browser` to filter by specific tool
- **Combined**: `/admin/incidents?since_hours=168&tool=browser`

#### CSV Export
The CSV export honors all active filters:
```
/admin/incidents.csv?since_hours=168&tool=browser
```

### 4. Tools & Safety Page (`/admin/tools`)

Displays:
- Recent tool call details with timing
- Aggregated summary statistics
- Safety mode distribution

## API Endpoints

### Performance Ingestion

#### POST `/ops/perf/k6`
Ingests k6 performance test summaries.

**Headers:**
- `x-api-key`: Your API key
- `content-type`: application/json

**Body:**
```json
{
  "metrics": {
    "http_req_duration{endpoint:health}": {
      "values": {"p(95)": 101}
    },
    "http_req_duration{endpoint:tools}": {
      "values": {"p(95)": 205}
    }
  }
}
```

**Response:**
```json
{
  "ok": true,
  "saved": true,
  "points": 2
}
```

#### GET `/ops/perf/series`
Retrieves performance time series data.

**Parameters:**
- `endpoint`: Endpoint name (e.g., "health", "tools", "openapi")
- `hours`: Time window in hours (1-720, default: 24)

**Response:**
```json
{
  "points": [
    {"ts": 1234567890000, "p95": 101.5},
    {"ts": 1234567900000, "p95": 98.2}
  ]
}
```

## Security

All admin endpoints require:
1. API key authentication via `x-api-key` header
2. Feature flags to be explicitly enabled
3. HTTPS in production (handled by reverse proxy)

## Monitoring Best Practices

1. **Regular Reviews**: Check dashboard daily for anomalies
2. **Alert Thresholds**: Set up alerts when p95 > acceptable limits
3. **Incident Analysis**: Use filters to identify patterns
4. **Export for Analysis**: Download CSVs for deeper analysis
5. **Trend Monitoring**: Switch between 24h/7d views to spot trends

## Troubleshooting

### Dashboard Not Loading
- Verify `FLAG_ADMIN_DASHBOARD=true`
- Check API key is set correctly
- Ensure service is running

### No Performance Data
- Confirm `FLAG_OPS_PERF_INGEST=true`
- Check CI is posting k6 summaries
- Verify `.lukhas_perf/` directory has write permissions

### Incidents Not Filtering
- Check query parameter syntax
- Ensure time values are within valid range (1-720 hours)
- Tool names are case-insensitive

## Data Retention

- Performance data: Stored in `.lukhas_perf/k6_series.jsonl`
- Incidents: Based on audit log retention policy
- Tool usage: 24-hour rolling window by default

## Future Enhancements

- Real-time WebSocket updates
- Custom alert configurations
- Advanced filtering UI
- Historical comparisons
- Export to monitoring platforms
