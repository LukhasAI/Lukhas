"""
Dashboard Alternatives for LUKHAS AI
====================================
Lightweight web dashboard alternatives when Streamlit is not available.
Provides simple HTML/JS dashboards with JSON data binding and basic interactivity.
"""

import json
import logging
import socket
import threading
import time
from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Optional, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class DashboardData:
    """Standard dashboard data structure"""

    title: str
    timestamp: float
    metrics: dict[str, Any]
    charts: list[dict[str, Any]]
    logs: list[str]
    status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class SimpleDashboard:
    """
    Simple HTML/JS dashboard alternative to Streamlit.
    Serves dashboard data via HTTP with auto-refresh and basic interactivity.
    """

    def __init__(self, title: str = "LUKHAS Dashboard", port: int = 8501):
        self.title = title
        self.port = port
        self.data = DashboardData(title=title, timestamp=time.time(), metrics={}, charts=[], logs=[])

        # Server components
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False

        # Dashboard configuration
        self.auto_refresh_interval = 5000  # milliseconds
        self.max_logs = 100

        self.logger = logging.getLogger(f"dashboard.{title.lower().replace(' ', '_')}")

    def add_metric(self, key: str, value: Union[int, float, str], unit: str = "") -> None:
        """Add or update a metric"""
        self.data.metrics[key] = {
            "value": value,
            "unit": unit,
            "timestamp": time.time(),
        }
        self._update_timestamp()

    def add_chart(
        self,
        chart_id: str,
        chart_type: str,
        data: list[dict[str, Any]],
        title: str = "",
        x_axis: str = "x",
        y_axis: str = "y",
    ) -> None:
        """Add or update a chart"""
        chart = {
            "id": chart_id,
            "type": chart_type,  # line, bar, pie, scatter
            "title": title or chart_id.title(),
            "data": data,
            "x_axis": x_axis,
            "y_axis": y_axis,
            "timestamp": time.time(),
        }

        # Update existing chart or add new one
        for i, existing_chart in enumerate(self.data.charts):
            if existing_chart["id"] == chart_id:
                self.data.charts[i] = chart
                break
        else:
            self.data.charts.append(chart)

        self._update_timestamp()

    def add_log(self, message: str, level: str = "INFO") -> None:
        """Add a log message"""
        log_entry = f"[{time.strftime('%H:%M:%S')}] {level}: {message}"
        self.data.logs.append(log_entry)

        # Limit log size
        if len(self.data.logs) > self.max_logs:
            self.data.logs = self.data.logs[-self.max_logs :]

        self._update_timestamp()

    def set_status(self, status: str) -> None:
        """Update dashboard status"""
        self.data.status = status
        self._update_timestamp()

    def start_server(self) -> None:
        """Start the dashboard web server"""
        if self.running:
            self.logger.warning("Server already running")
            return

        try:
            # Check if port is available
            if not self._is_port_available(self.port):
                self.logger.error(f"Port {self.port} is already in use")
                return

            # Create server
            self.server = HTTPServer(("localhost", self.port), self._create_handler())
            self.running = True

            # Start server in background thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()

            self.logger.info(f"Dashboard server started at http://localhost:{self.port}")

        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            self.running = False

    def stop_server(self) -> None:
        """Stop the dashboard web server"""
        if not self.running:
            return

        self.running = False

        if self.server:
            self.server.shutdown()
            self.server = None

        if self.server_thread:
            self.server_thread.join(timeout=5)
            self.server_thread = None

        self.logger.info("Dashboard server stopped")

    def get_url(self) -> str:
        """Get the dashboard URL"""
        return f"http://localhost:{self.port}"

    def _update_timestamp(self) -> None:
        """Update the dashboard timestamp"""
        self.data.timestamp = time.time()

    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return True
        except OSError:
            return False

    def _run_server(self) -> None:
        """Run the HTTP server"""
        try:
            self.server.serve_forever()
        except Exception as e:
            if self.running:  # Only log if not intentionally stopped
                self.logger.error(f"Server error: {e}")

    def _create_handler(self):
        """Create HTTP request handler class"""
        dashboard = self  # Capture reference for handler

        class DashboardHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                # Suppress default HTTP server logging
                pass

            def do_GET(self):
                """Handle GET requests"""
                try:
                    parsed_path = urlparse(self.path)

                    if parsed_path.path == "/":
                        # Serve main dashboard page
                        self._serve_dashboard()
                    elif parsed_path.path == "/data":
                        # Serve dashboard data as JSON
                        self._serve_data()
                    elif parsed_path.path == "/health":
                        # Health check endpoint
                        self._serve_health()
                    else:
                        # 404 for unknown paths
                        self._serve_404()

                except Exception as e:
                    dashboard.logger.error(f"Request handling error: {e}")
                    self._serve_error()

            def _serve_dashboard(self):
                """Serve the main dashboard HTML page"""
                html = dashboard._generate_dashboard_html()
                self._send_response(200, html, "text/html")

            def _serve_data(self):
                """Serve dashboard data as JSON"""
                data = dashboard.data.to_dict()
                json_data = json.dumps(data, indent=2)
                self._send_response(200, json_data, "application/json")

            def _serve_health(self):
                """Serve health check"""
                health = {"status": "healthy", "timestamp": time.time()}
                json_data = json.dumps(health)
                self._send_response(200, json_data, "application/json")

            def _serve_404(self):
                """Serve 404 error"""
                html = "<html><body><h1>404 Not Found</h1></body></html>"
                self._send_response(404, html, "text/html")

            def _serve_error(self):
                """Serve 500 error"""
                html = "<html><body><h1>500 Internal Server Error</h1></body></html>"
                self._send_response(500, html, "text/html")

            def _send_response(self, status_code: int, content: str, content_type: str):
                """Send HTTP response"""
                self.send_response(status_code)
                self.send_header("Content-type", content_type)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))

        return DashboardHandler

    def _generate_dashboard_html(self) -> str:
        """Generate the dashboard HTML page"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2em;
        }}
        .status {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }}
        .status.active {{ background-color: #4CAF50; }}
        .status.warning {{ background-color: #FF9800; }}
        .status.error {{ background-color: #F44336; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .card h2 {{
            margin: 0 0 15px 0;
            color: #333;
            font-size: 1.2em;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        .metric:last-child {{
            border-bottom: none;
        }}
        .metric-value {{
            font-weight: bold;
            color: #667eea;
        }}
        .logs {{
            background: #1e1e1e;
            color: #f5f5f5;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            padding: 15px;
            border-radius: 4px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .chart-placeholder {{
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 4px;
            padding: 40px;
            text-align: center;
            color: #6c757d;
            margin: 10px 0;
        }}
        .auto-refresh {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.8em;
        }}
        .timestamp {{
            font-size: 0.9em;
            opacity: 0.7;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="auto-refresh">Auto-refresh: <span id="countdown">{self.auto_refresh_interval//1000}</span>s</div>

    <div class="header">
        <h1>{self.title}</h1>
        <span class="status" id="status">{self.data.status}</span>
        <div class="timestamp" id="timestamp">Last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.data.timestamp))}</div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>📊 Metrics</h2>
            <div id="metrics">
                {self._generate_metrics_html()}
            </div>
        </div>

        <div class="card">
            <h2>📈 Charts</h2>
            <div id="charts">
                {self._generate_charts_html()}
            </div>
        </div>

        <div class="card">
            <h2>📝 System Logs</h2>
            <div id="logs" class="logs">
                {self._generate_logs_html()}
            </div>
        </div>
    </div>

    <script>
        let refreshInterval = {self.auto_refresh_interval};
        let countdown = refreshInterval / 1000;

        // Auto-refresh functionality
        function updateCountdown() {{
            document.getElementById('countdown').textContent = Math.ceil(countdown);
            countdown -= 1;

            if (countdown < 0) {{
                refreshDashboard();
                countdown = refreshInterval / 1000;
            }}
        }}

        function refreshDashboard() {{
            fetch('/data')
                .then(response => response.json())
                .then(data => {{
                    // Update timestamp
                    const timestamp = new Date(data.timestamp * 1000).toLocaleString();
                    document.getElementById('timestamp').textContent = 'Last updated: ' + timestamp;

                    // Update status
                    const statusElement = document.getElementById('status');
                    statusElement.textContent = data.status;
                    statusElement.className = 'status ' + data.status;

                    // Update metrics
                    let metricsHtml = '';
                    for (const [key, metric] of Object.entries(data.metrics)) {{
                        metricsHtml += `<div class="metric">
                            <span>${{key}}</span>
                            <span class="metric-value">${{metric.value}} ${{metric.unit}}</span>
                        </div>`;
                    }}
                    document.getElementById('metrics').innerHTML = metricsHtml;

                    // Update charts
                    let chartsHtml = '';
                    if (data.charts.length === 0) {{
                        chartsHtml = '<div class="chart-placeholder">No charts available</div>';
                    }} else {{
                        data.charts.forEach(chart => {{
                            chartsHtml += `<div class="chart-placeholder">
                                📊 ${{chart.title}}<br>
                                <small>${{chart.type}} chart with ${{chart.data.length}} data points</small>
                            </div>`;
                        }});
                    }}
                    document.getElementById('charts').innerHTML = chartsHtml;

                    // Update logs
                    const logsHtml = data.logs.join('\\n');
                    const logsElement = document.getElementById('logs');
                    logsElement.textContent = logsHtml;
                    logsElement.scrollTop = logsElement.scrollHeight;
                }})
                .catch(error => {{
                    console.error('Dashboard refresh failed:', error);
                    document.getElementById('status').textContent = 'error';
                    document.getElementById('status').className = 'status error';
                }});
        }}

        // Start countdown timer
        setInterval(updateCountdown, 1000);

        // Initial data load
        setTimeout(refreshDashboard, 1000);
    </script>
</body>
</html>"""

    def _generate_metrics_html(self) -> str:
        """Generate HTML for metrics section"""
        if not self.data.metrics:
            return '<div style="color: #666; font-style: italic;">No metrics available</div>'

        html = ""
        for key, metric in self.data.metrics.items():
            html += f"""<div class="metric">
                <span>{key}</span>
                <span class="metric-value">{metric["value"]} {metric["unit"]}</span>
            </div>"""
        return html

    def _generate_charts_html(self) -> str:
        """Generate HTML for charts section"""
        if not self.data.charts:
            return '<div class="chart-placeholder">No charts available</div>'

        html = ""
        for chart in self.data.charts:
            html += f"""<div class="chart-placeholder">
                📊 {chart["title"]}<br>
                <small>{chart["type"]} chart with {len(chart["data"])} data points</small>
            </div>"""
        return html

    def _generate_logs_html(self) -> str:
        """Generate HTML for logs section"""
        if not self.data.logs:
            return "No logs available"
        return "\n".join(self.data.logs[-20:])  # Show last 20 logs


class StreamlitFallback:
    """
    Fallback class to replace Streamlit functionality.
    Provides similar API but renders to simple dashboard.
    """

    def __init__(self):
        self.dashboard = SimpleDashboard("Streamlit Fallback")
        self.dashboard.start_server()
        self._metric_counter = 0

    def title(self, text: str) -> None:
        """Set dashboard title"""
        self.dashboard.title = text
        self.dashboard.data.title = text

    def header(self, text: str) -> None:
        """Add header (logged as info)"""
        self.dashboard.add_log(f"HEADER: {text}", "INFO")

    def subheader(self, text: str) -> None:
        """Add subheader (logged as info)"""
        self.dashboard.add_log(f"SUBHEADER: {text}", "INFO")

    def write(self, text: str) -> None:
        """Write text (logged as info)"""
        self.dashboard.add_log(f"WRITE: {text}", "INFO")

    def metric(self, label: str, value: Union[int, float, str], delta: Optional[str] = None) -> None:
        """Add metric to dashboard"""
        self.dashboard.add_metric(label, value)
        if delta:
            self.dashboard.add_log(f"METRIC: {label} = {value} (Δ {delta})", "INFO")

    def line_chart(self, data: list[dict[str, Any]], x: str = "x", y: str = "y") -> None:
        """Add line chart"""
        self._metric_counter += 1
        chart_id = f"line_chart_{self._metric_counter}"
        self.dashboard.add_chart(chart_id, "line", data, f"Line Chart {self._metric_counter}", x, y)

    def bar_chart(self, data: list[dict[str, Any]], x: str = "x", y: str = "y") -> None:
        """Add bar chart"""
        self._metric_counter += 1
        chart_id = f"bar_chart_{self._metric_counter}"
        self.dashboard.add_chart(chart_id, "bar", data, f"Bar Chart {self._metric_counter}", x, y)

    def success(self, text: str) -> None:
        """Success message"""
        self.dashboard.add_log(f"SUCCESS: {text}", "SUCCESS")

    def warning(self, text: str) -> None:
        """Warning message"""
        self.dashboard.add_log(f"WARNING: {text}", "WARNING")

    def error(self, text: str) -> None:
        """Error message"""
        self.dashboard.add_log(f"ERROR: {text}", "ERROR")
        self.dashboard.set_status("error")

    def info(self, text: str) -> None:
        """Info message"""
        self.dashboard.add_log(f"INFO: {text}", "INFO")

    def get_url(self) -> str:
        """Get dashboard URL"""
        return self.dashboard.get_url()

    def stop(self) -> None:
        """Stop dashboard server"""
        self.dashboard.stop_server()


# Global fallback instance
_streamlit_fallback = None


def get_streamlit_fallback() -> StreamlitFallback:
    """Get global streamlit fallback instance"""
    global _streamlit_fallback
    if _streamlit_fallback is None:
        _streamlit_fallback = StreamlitFallback()
    return _streamlit_fallback


# Module-level fallback for direct streamlit imports
def create_streamlit_mock():
    """Create a mock streamlit module for import replacement"""

    class StreamlitMock:
        def __init__(self):
            self._fallback = get_streamlit_fallback()

        def __getattr__(self, name):
            return getattr(self._fallback, name, lambda *args, **kwargs: None)

    return StreamlitMock()


# Export key components
__all__ = [
    "SimpleDashboard",
    "StreamlitFallback",
    "DashboardData",
    "get_streamlit_fallback",
    "create_streamlit_mock",
]


# Example usage
if __name__ == "__main__":
    # Demo the dashboard
    dashboard = SimpleDashboard("LUKHAS Demo Dashboard")
    dashboard.start_server()

    # Add some demo data
    dashboard.add_metric("CPU Usage", "45%", "%")
    dashboard.add_metric("Memory", "2.1GB", "GB")
    dashboard.add_metric("Active Users", 127, "users")

    dashboard.add_chart(
        "cpu_history",
        "line",
        [
            {"time": "00:00", "cpu": 30},
            {"time": "00:05", "cpu": 45},
            {"time": "00:10", "cpu": 52},
            {"time": "00:15", "cpu": 38},
        ],
        "CPU Usage Over Time",
        "time",
        "cpu",
    )

    dashboard.add_log("System started successfully")
    dashboard.add_log("Loading consciousness modules")
    dashboard.add_log("Memory folds initialized")

    print(f"Dashboard running at: {dashboard.get_url()}")

    try:
        # Keep running until interrupted
        while True:
            time.sleep(5)
            # Update some demo data
            import random

            dashboard.add_metric("CPU Usage", f"{random.randint(20, 80)}%", "%")
            dashboard.add_log(f"Heartbeat - System healthy at {time.strftime('%H:%M:%S')}")

    except KeyboardInterrupt:
        dashboard.stop_server()
        print("Dashboard stopped")
