#!/usr/bin/env python3
"""
Wave C C5 Monitoring Dashboard
==============================

Real-time monitoring dashboard for the Aka Qualia consciousness processing pipeline.
Provides web-based visualization of metrics, alerts, and system health.
"""

import json
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List
from urllib.parse import parse_qs, urlparse

from observability import CONTENT_TYPE_LATEST, AkaqMetrics, get_observability


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for the monitoring dashboard"""

    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        pass

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/":
            self._serve_dashboard()
        elif parsed_path.path == "/metrics":
            self._serve_prometheus_metrics()
        elif parsed_path.path == "/api/health":
            self._serve_health_check()
        elif parsed_path.path == "/api/summary":
            self._serve_metrics_summary()
        elif parsed_path.path == "/api/live":
            self._serve_live_metrics()
        else:
            self._serve_404()

    def _serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html_content = self._generate_dashboard_html()

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def _serve_prometheus_metrics(self):
        """Serve Prometheus metrics endpoint"""
        obs = get_observability()
        metrics = obs.export_prometheus_metrics()

        self.send_response(200)
        self.send_header("Content-type", CONTENT_TYPE_LATEST)
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(metrics)

    def _serve_health_check(self):
        """Serve health check API"""
        obs = get_observability()
        health = obs.health_check()

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(json.dumps(health, indent=2).encode("utf-8"))

    def _serve_metrics_summary(self):
        """Serve metrics summary API"""
        obs = get_observability()
        summary = obs.get_metrics_summary()

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(json.dumps(summary, indent=2).encode("utf-8"))

    def _serve_live_metrics(self):
        """Serve live metrics for dashboard updates"""
        # Generate some demo live metrics
        live_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_status": "healthy",
            "active_users": 42,
            "scenes_per_minute": 156,
            "memory_usage_mb": 234.5,
            "average_latency_ms": 12.3,
            "consciousness_drift": 0.05,
            "router_queue_depth": 3,
            "glyph_accuracy": 0.94,
            "dream_generation_rate": 2.1,
        }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(live_data).encode("utf-8"))

    def _serve_404(self):
        """Serve 404 response"""
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>404 - Not Found</h1>")

    def _generate_dashboard_html(self) -> str:
        """Generate the dashboard HTML"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wave C Aka Qualia - Monitoring Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.8;
            margin-bottom: 10px;
        }
        
        .trinity-badges {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 15px;
        }
        
        .badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .badge-identity { background: rgba(255, 165, 0, 0.2); border: 1px solid #ffa500; }
        .badge-consciousness { background: rgba(0, 191, 255, 0.2); border: 1px solid #00bfff; }
        .badge-guardian { background: rgba(50, 205, 50, 0.2); border: 1px solid #32cd32; }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
        }
        
        .metric-card h3 {
            font-size: 1.3rem;
            margin-bottom: 15px;
            color: #4facfe;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.7;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-healthy { background-color: #32cd32; }
        .status-warning { background-color: #ffa500; }
        .status-error { background-color: #ff4444; }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            margin-top: 10px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        .links {
            margin-top: 30px;
            text-align: center;
        }
        
        .links a {
            color: #4facfe;
            text-decoration: none;
            margin: 0 15px;
            padding: 10px 20px;
            border: 1px solid #4facfe;
            border-radius: 20px;
            transition: all 0.2s ease;
        }
        
        .links a:hover {
            background: #4facfe;
            color: #1e3c72;
        }
        
        .timestamp {
            text-align: center;
            margin-top: 20px;
            opacity: 0.6;
            font-size: 0.9rem;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .live-indicator {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚛️ Wave C Aka Qualia Dashboard</h1>
        <div class="subtitle">Phenomenological Processing Pipeline Monitoring</div>
        <div class="trinity-badges">
            <div class="badge badge-identity">⚛️ Identity</div>
            <div class="badge badge-consciousness">🧠 Consciousness</div>
            <div class="badge badge-guardian">🛡️ Guardian</div>
        </div>
    </div>
    
    <div class="dashboard-grid">
        <div class="metric-card">
            <h3><span class="status-indicator status-healthy live-indicator"></span>System Status</h3>
            <div class="metric-value" id="system-status">HEALTHY</div>
            <div class="metric-label">Overall System Health</div>
        </div>
        
        <div class="metric-card">
            <h3>🧠 Active Processing</h3>
            <div class="metric-value" id="scenes-per-minute">156</div>
            <div class="metric-label">Scenes per Minute</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 78%"></div>
            </div>
        </div>
        
        <div class="metric-card">
            <h3>🎯 GLYPH Accuracy</h3>
            <div class="metric-value" id="glyph-accuracy">94.2%</div>
            <div class="metric-label">Mapping Precision</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 94%"></div>
            </div>
        </div>
        
        <div class="metric-card">
            <h3>⚡ Response Time</h3>
            <div class="metric-value" id="avg-latency">12.3<span style="font-size: 1rem;">ms</span></div>
            <div class="metric-label">Average Latency</div>
        </div>
        
        <div class="metric-card">
            <h3>🌊 Consciousness Drift</h3>
            <div class="metric-value" id="drift-phi">0.05</div>
            <div class="metric-label">Drift Phi (Target: < 0.15)</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 33%"></div>
            </div>
        </div>
        
        <div class="metric-card">
            <h3>🚦 Router Queue</h3>
            <div class="metric-value" id="queue-depth">3</div>
            <div class="metric-label">Pending Dispatches</div>
        </div>
        
        <div class="metric-card">
            <h3>💾 Memory Usage</h3>
            <div class="metric-value" id="memory-usage">234.5<span style="font-size: 1rem;">MB</span></div>
            <div class="metric-label">Total Storage</div>
        </div>
        
        <div class="metric-card">
            <h3>🌙 Dream Generation</h3>
            <div class="metric-value" id="dream-rate">2.1</div>
            <div class="metric-label">Dreams per Hour</div>
        </div>
    </div>
    
    <div class="links">
        <a href="/metrics">📊 Prometheus Metrics</a>
        <a href="/api/health">🏥 Health Check</a>
        <a href="/api/summary">📋 Metrics Summary</a>
        <a href="https://github.com/anthropics/lukhas">📖 Documentation</a>
    </div>
    
    <div class="timestamp" id="last-updated">
        Last updated: <span class="live-indicator">●</span> <span id="update-time">Loading...</span>
    </div>
    
    <script>
        // Auto-refresh dashboard data
        function updateDashboard() {
            fetch('/api/live')
                .then(response => response.json())
                .then(data => {
                    // Update metric values
                    document.getElementById('system-status').textContent = 
                        data.system_status.toUpperCase();
                    document.getElementById('scenes-per-minute').textContent = 
                        data.scenes_per_minute;
                    document.getElementById('glyph-accuracy').textContent = 
                        (data.glyph_accuracy * 100).toFixed(1) + '%';
                    document.getElementById('avg-latency').innerHTML = 
                        data.average_latency_ms + '<span style="font-size: 1rem;">ms</span>';
                    document.getElementById('drift-phi').textContent = 
                        data.consciousness_drift.toFixed(3);
                    document.getElementById('queue-depth').textContent = 
                        data.router_queue_depth;
                    document.getElementById('memory-usage').innerHTML = 
                        data.memory_usage_mb + '<span style="font-size: 1rem;">MB</span>';
                    document.getElementById('dream-rate').textContent = 
                        data.dream_generation_rate.toFixed(1);
                    
                    // Update timestamp
                    const updateTime = new Date(data.timestamp).toLocaleString();
                    document.getElementById('update-time').textContent = updateTime;
                })
                .catch(error => {
                    console.log('Dashboard update failed:', error);
                });
        }
        
        // Update immediately and then every 5 seconds
        updateDashboard();
        setInterval(updateDashboard, 5000);
        
        // Add some visual flair
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.metric-card');
            cards.forEach((card, index) => {
                setTimeout(() => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    card.style.transition = 'all 0.6s ease';
                    
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100);
                }, index * 100);
            });
        });
    </script>
</body>
</html>"""


class MonitoringDashboard:
    """
    Web-based monitoring dashboard for Wave C Aka Qualia processing.

    Provides real-time visualization of system metrics, health status,
    and performance indicators.
    """

    def __init__(self, host: str = "localhost", port: int = 8088):
        """Initialize monitoring dashboard"""
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False

    def start(self):
        """Start the monitoring dashboard server"""
        if self.running:
            print("⚠️  Dashboard server is already running")
            return

        try:
            self.server = HTTPServer((self.host, self.port), DashboardHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.running = True
            self.server_thread.start()

            print("🚀 Wave C Monitoring Dashboard started")
            print(f"📊 Dashboard: http://{self.host}:{self.port}/")
            print(f"📈 Metrics:   http://{self.host}:{self.port}/metrics")
            print(f"🏥 Health:    http://{self.host}:{self.port}/api/health")

        except Exception as e:
            print(f"❌ Failed to start dashboard server: {e}")
            self.running = False

    def stop(self):
        """Stop the monitoring dashboard server"""
        if not self.running:
            return

        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()

            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5.0)

            self.running = False
            print("🛑 Monitoring dashboard stopped")

        except Exception as e:
            print(f"⚠️  Error stopping dashboard: {e}")

    def is_running(self) -> bool:
        """Check if the dashboard server is running"""
        return self.running and self.server_thread and self.server_thread.is_alive()

    def get_status(self) -> Dict[str, Any]:
        """Get dashboard server status"""
        return {
            "running": self.running,
            "host": self.host,
            "port": self.port,
            "dashboard_url": f"http://{self.host}:{self.port}/",
            "metrics_url": f"http://{self.host}:{self.port}/metrics",
            "health_url": f"http://{self.host}:{self.port}/api/health",
        }


def start_monitoring_dashboard(host: str = "localhost", port: int = 8088) -> MonitoringDashboard:
    """Start monitoring dashboard with default configuration"""
    dashboard = MonitoringDashboard(host=host, port=port)
    dashboard.start()
    return dashboard


if __name__ == "__main__":
    print("🔍 Wave C C5 Monitoring Dashboard")

    # Start the dashboard
    dashboard = start_monitoring_dashboard()

    if dashboard.is_running():
        print("\n✅ Dashboard is running! Press Ctrl+C to stop...")
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping dashboard...")
            dashboard.stop()
            print("✅ Dashboard stopped successfully")
    else:
        print("❌ Failed to start dashboard")
