#!/usr/bin/env python3
"""
Production Monitoring Dashboard
==============================
Simple web dashboard for LUKHAS AI monitoring system
Provides real-time system status and alert management

Features:
- Real-time system metrics display
- Active alerts management
- Historical trend visualization
- Alert acknowledgment interface
- System health overview
"""

import asyncio
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

try:
    import uvicorn
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from tools.monitoring.t4_monitoring_integration import T4MonitoringIntegration


class MonitoringDashboard:
    """Web dashboard for monitoring system"""

    def __init__(self):
        self.monitoring_integration = T4MonitoringIntegration()
        self.alerting_system = self.monitoring_integration.alerting_system

        if FASTAPI_AVAILABLE:
            self.app = FastAPI(title="LUKHAS AI Monitoring Dashboard")
            self._setup_routes()
        else:
            self.app = None
            print("FastAPI not available. Install with: pip install fastapi uvicorn")

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            return self._generate_dashboard_html()

        @self.app.get("/api/status")
        async def get_status():
            return await self._get_system_status()

        @self.app.get("/api/metrics")
        async def get_metrics():
            return await self._get_current_metrics()

        @self.app.get("/api/alerts")
        async def get_alerts():
            return self._get_alerts()

        @self.app.post("/api/alerts/{rule_name}/acknowledge")
        async def acknowledge_alert(rule_name: str, request: Request):
            data = await request.json()
            acknowledged_by = data.get("acknowledged_by", "dashboard")
            success = self.alerting_system.acknowledge_alert(rule_name, acknowledged_by)
            if success:
                return {"status": "acknowledged"}
            else:
                raise HTTPException(status_code=404, detail="Alert not found")

        @self.app.get("/api/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

        @self.app.get("/api/metrics/history")
        async def get_metrics_history(hours: int = 24):
            return self._get_metrics_history(hours)

    async def _get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        summary = self.alerting_system.get_alert_summary()
        metrics = await self.monitoring_integration.collect_enhanced_metrics()

        return {
            "overall_health": summary["system_health"],
            "active_alerts": summary["active_alerts"],
            "alerts_by_severity": summary["alerts_by_severity"],
            "current_metrics": {
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "disk_usage_percent": metrics.disk_usage_percent,
                "test_success_rate": metrics.test_success_rate,
                "coverage_percentage": metrics.coverage_percentage,
                "response_time_p95": metrics.response_time_p95,
                "error_rate": metrics.error_rate,
                "active_connections": metrics.active_connections
            },
            "timestamp": metrics.timestamp.isoformat()
        }

    async def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        metrics = await self.monitoring_integration.collect_enhanced_metrics()
        return {
            "timestamp": metrics.timestamp.isoformat(),
            "cpu_percent": metrics.cpu_percent,
            "memory_percent": metrics.memory_percent,
            "disk_usage_percent": metrics.disk_usage_percent,
            "network_io_bytes": metrics.network_io_bytes,
            "test_success_rate": metrics.test_success_rate,
            "coverage_percentage": metrics.coverage_percentage,
            "response_time_p95": metrics.response_time_p95,
            "error_rate": metrics.error_rate,
            "active_connections": metrics.active_connections
        }

    def _get_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts"""
        alerts = []
        for alert in self.alerting_system.active_alerts.values():
            alerts.append({
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "triggered_at": alert.triggered_at.isoformat(),
                "last_updated": alert.last_updated.isoformat(),
                "value": alert.value,
                "threshold": alert.threshold,
                "message": alert.message,
                "tags": list(alert.tags),
                "acknowledged_by": alert.acknowledged_by,
                "escalated": alert.escalated
            })
        return alerts

    def _get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical metrics"""
        try:
            since = datetime.now(timezone.utc) - timedelta(hours=hours)
            with sqlite3.connect(self.alerting_system.db_path) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, cpu_percent, memory_percent, disk_usage_percent,
                           test_success_rate, coverage_percentage, response_time_p95,
                           error_rate, active_connections
                    FROM metrics_history
                    WHERE timestamp > ?
                    ORDER BY timestamp ASC
                """, (since,))

                history = []
                for row in cursor.fetchall():
                    history.append({
                        "timestamp": row[0],
                        "cpu_percent": row[1],
                        "memory_percent": row[2],
                        "disk_usage_percent": row[3],
                        "test_success_rate": row[4],
                        "coverage_percentage": row[5],
                        "response_time_p95": row[6],
                        "error_rate": row[7],
                        "active_connections": row[8]
                    })
                return history
        except Exception as e:
            print(f"Error getting metrics history: {e}")
            return []

    def _generate_dashboard_html(self) -> str:
        """Generate HTML dashboard"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LUKHAS AI Monitoring Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .metric-title {
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .metric-unit {
            color: #888;
            font-size: 14px;
        }
        .status-healthy { color: #28a745; }
        .status-warning { color: #ffc107; }
        .status-degraded { color: #fd7e14; }
        .status-critical { color: #dc3545; }
        .alerts-section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .alert-item {
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid;
        }
        .alert-critical { border-left-color: #dc3545; background-color: #f8d7da; }
        .alert-high { border-left-color: #fd7e14; background-color: #ffeaa7; }
        .alert-medium { border-left-color: #ffc107; background-color: #fff3cd; }
        .alert-low { border-left-color: #28a745; background-color: #d4edda; }
        .btn {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 10px;
        }
        .btn:hover {
            background-color: #0056b3;
        }
        .refresh-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        .last-updated {
            text-align: center;
            color: #666;
            margin-top: 20px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <button class="refresh-btn" onclick="loadData()">🔄 Refresh</button>

    <div class="container">
        <div class="header">
            <h1>LUKHAS AI Monitoring Dashboard</h1>
            <p>Real-time system health and performance monitoring</p>
        </div>

        <div class="metrics-grid" id="metricsGrid">
            <!-- Metrics will be loaded here -->
        </div>

        <div class="alerts-section">
            <h2>Active Alerts</h2>
            <div id="alertsList">
                <!-- Alerts will be loaded here -->
            </div>
        </div>

        <div class="last-updated" id="lastUpdated">
            <!-- Last updated time will be shown here -->
        </div>
    </div>

    <script>
        async function loadData() {
            try {
                // Load system status
                const statusResponse = await fetch('/api/status');
                const status = await statusResponse.json();

                // Load alerts
                const alertsResponse = await fetch('/api/alerts');
                const alerts = await alertsResponse.json();

                updateMetrics(status);
                updateAlerts(alerts);
                updateLastUpdated();

            } catch (error) {
                console.error('Error loading data:', error);
            }
        }

        function updateMetrics(status) {
            const metrics = status.current_metrics;
            const health = status.overall_health;

            const metricsHtml = `
                <div class="metric-card">
                    <div class="metric-title">System Health</div>
                    <div class="metric-value status-${health}">${health.toUpperCase()}</div>
                    <div class="metric-unit">${status.active_alerts} active alerts</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">CPU Usage</div>
                    <div class="metric-value">${metrics.cpu_percent.toFixed(1)}</div>
                    <div class="metric-unit">%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Memory Usage</div>
                    <div class="metric-value">${metrics.memory_percent.toFixed(1)}</div>
                    <div class="metric-unit">%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Disk Usage</div>
                    <div class="metric-value">${metrics.disk_usage_percent.toFixed(1)}</div>
                    <div class="metric-unit">%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Test Success Rate</div>
                    <div class="metric-value">${metrics.test_success_rate.toFixed(1)}</div>
                    <div class="metric-unit">%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Test Coverage</div>
                    <div class="metric-value">${metrics.coverage_percentage.toFixed(1)}</div>
                    <div class="metric-unit">%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Response Time P95</div>
                    <div class="metric-value">${metrics.response_time_p95.toFixed(0)}</div>
                    <div class="metric-unit">ms</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Error Rate</div>
                    <div class="metric-value">${metrics.error_rate.toFixed(2)}</div>
                    <div class="metric-unit">%</div>
                </div>
            `;

            document.getElementById('metricsGrid').innerHTML = metricsHtml;
        }

        function updateAlerts(alerts) {
            if (alerts.length === 0) {
                document.getElementById('alertsList').innerHTML =
                    '<p style="color: #28a745; text-align: center; padding: 20px;">✅ No active alerts</p>';
                return;
            }

            const alertsHtml = alerts.map(alert => `
                <div class="alert-item alert-${alert.severity}">
                    <div style="display: flex; justify-content: between; align-items: center;">
                        <div style="flex: 1;">
                            <strong>${alert.rule_name}</strong> - ${alert.severity.toUpperCase()}
                            <br>
                            <small>${alert.message}</small>
                            <br>
                            <small>Triggered: ${new Date(alert.triggered_at).toLocaleString()}</small>
                            ${alert.acknowledged_by ? `<br><small>Acknowledged by: ${alert.acknowledged_by}</small>` : ''}
                        </div>
                        <div>
                            <strong>${alert.value.toFixed(2)}</strong> / ${alert.threshold.toFixed(2)}
                            ${alert.status === 'active' && !alert.acknowledged_by ?
                                `<button class="btn" onclick="acknowledgeAlert('${alert.rule_name}')">Acknowledge</button>` : ''}
                        </div>
                    </div>
                </div>
            `).join('');

            document.getElementById('alertsList').innerHTML = alertsHtml;
        }

        function updateLastUpdated() {
            const now = new Date().toLocaleString();
            document.getElementById('lastUpdated').innerHTML = `Last updated: ${now}`;
        }

        async function acknowledgeAlert(ruleName) {
            try {
                const response = await fetch(`/api/alerts/${ruleName}/acknowledge`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        acknowledged_by: 'dashboard_user'
                    })
                });

                if (response.ok) {
                    loadData(); // Refresh the data
                }
            } catch (error) {
                console.error('Error acknowledging alert:', error);
            }
        }

        // Auto-refresh every 30 seconds
        setInterval(loadData, 30000);

        // Initial load
        loadData();
    </script>
</body>
</html>
        """

    async def run_dashboard(self, host: str = "127.0.0.1", port: int = 8080):
        """Run the monitoring dashboard"""
        if not FASTAPI_AVAILABLE:
            print("FastAPI not available. Please install with: pip install fastapi uvicorn")
            return

        print(f"Starting LUKHAS AI Monitoring Dashboard on http://{host}:{port}")
        print("Dashboard Features:")
        print("- Real-time system metrics")
        print("- Active alerts management")
        print("- Alert acknowledgment")
        print("- Auto-refresh every 30 seconds")

        # Start background monitoring
        monitoring_task = asyncio.create_task(
            self.monitoring_integration.run_integrated_monitoring()
        )

        try:
            # Run the web server
            config = uvicorn.Config(
                app=self.app,
                host=host,
                port=port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()
        except KeyboardInterrupt:
            print("\nShutting down dashboard...")
        finally:
            monitoring_task.cancel()

    def run_cli_dashboard(self):
        """Run a simple CLI-based dashboard"""
        print("LUKHAS AI Monitoring Dashboard (CLI Mode)")
        print("=" * 50)

        while True:
            try:
                # Clear screen (basic approach)
                print("\033[2J\033[H")

                # Get status
                summary = self.alerting_system.get_alert_summary()

                print("LUKHAS AI System Status")
                print("=" * 50)
                print(f"Overall Health: {summary['system_health'].upper()}")
                print(f"Active Alerts: {summary['active_alerts']}")
                print(f"- Critical: {summary['alerts_by_severity']['critical']}")
                print(f"- High: {summary['alerts_by_severity']['high']}")
                print(f"- Medium: {summary['alerts_by_severity']['medium']}")
                print(f"- Low: {summary['alerts_by_severity']['low']}")
                print()

                if summary['recent_alerts']:
                    print("Recent Alerts:")
                    print("-" * 30)
                    for alert in summary['recent_alerts'][:5]:
                        print(f"[{alert['severity'].upper()}] {alert['rule_name']}")
                        print(f"  {alert['message']}")
                        print(f"  {alert['triggered_at']}")
                        print()

                print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("\nPress Ctrl+C to exit")

                # Wait 30 seconds before refresh
                import time
                time.sleep(30)

            except KeyboardInterrupt:
                print("\nDashboard stopped.")
                break


async def main():
    """Main entry point"""
    dashboard = MonitoringDashboard()

    if FASTAPI_AVAILABLE:
        await dashboard.run_dashboard()
    else:
        dashboard.run_cli_dashboard()


if __name__ == "__main__":
    asyncio.run(main())
