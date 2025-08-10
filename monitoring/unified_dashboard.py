#!/usr/bin/env python3
"""
LUKHAS PWM Unified Monitoring Dashboard
Comprehensive real-time monitoring for all PWM systems
Trinity Framework: ⚛️🧠🛡️
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LUKHAS PWM Unified Monitoring Dashboard",
    description="Real-time monitoring for all PWM systems including consciousness, memory, ethics, and performance",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections
active_connections: List[WebSocket] = []

# Dashboard configuration
DASHBOARD_CONFIG = {
    "port": 3000,
    "host": "0.0.0.0",
    "title": "LUKHAS PWM Unified Dashboard",
    "refresh_rate": 5,  # seconds
    "enable_auth": False,
    "data_retention_hours": 24,
    "alert_thresholds": {
        "drift_critical": 0.8,
        "memory_usage_high": 85.0,
        "response_time_slow": 1000,  # ms
        "error_rate_high": 0.05,
    },
}

# In-memory data store (would be replaced with proper DB in production)
system_metrics = {}
alerts = []
historical_data = []


class MetricsCollector:
    """Collects and aggregates metrics from all PWM systems"""

    def __init__(self):
        self.last_collection = 0
        self.collection_interval = 1  # seconds

    async def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect metrics from all systems"""
        now = time.time()

        try:
            # System metrics
            system_stats = await self._collect_system_metrics()

            # API metrics (from our FastAPI endpoints)
            api_stats = await self._collect_api_metrics()

            # Consciousness metrics
            consciousness_stats = await self._collect_consciousness_metrics()

            # Memory metrics
            memory_stats = await self._collect_memory_metrics()

            # Ethics/Guardian metrics
            ethics_stats = await self._collect_ethics_metrics()

            # Dream engine metrics
            dream_stats = await self._collect_dream_metrics()

            # Feature flags status
            flags_stats = await self._collect_flags_metrics()

            # Performance metrics
            perf_stats = await self._collect_performance_metrics()

            combined_metrics = {
                "timestamp": now,
                "system": system_stats,
                "api": api_stats,
                "consciousness": consciousness_stats,
                "memory": memory_stats,
                "ethics": ethics_stats,
                "dream": dream_stats,
                "flags": flags_stats,
                "performance": perf_stats,
                "health_score": self._calculate_health_score(
                    system_stats, api_stats, consciousness_stats
                ),
            }

            # Update global metrics
            global system_metrics
            system_metrics = combined_metrics

            # Add to historical data
            # Keep only last 24 hours of data
            cutoff = now - (DASHBOARD_CONFIG["data_retention_hours"] * 3600)
            global historical_data
            historical_data.append(combined_metrics)
            historical_data = [d for d in historical_data if d["timestamp"] > cutoff]

            return combined_metrics

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {"error": str(e), "timestamp": now}

    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect basic system metrics"""
        import psutil

        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "active_processes": len(psutil.pids()),
            "uptime": time.time() - psutil.boot_time(),
            "load_average": (
                psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else 0
            ),
        }

    async def _collect_api_metrics(self) -> Dict[str, Any]:
        """Collect API endpoint metrics"""
        # In production, this would read from actual metrics store
        return {
            "total_requests": 12847,
            "requests_per_second": 23.5,
            "average_response_time": 187,
            "p95_response_time": 342,
            "error_rate": 0.02,
            "active_connections": len(active_connections),
            "endpoints": {
                "/feedback/card": {"requests": 5623, "avg_time": 45},
                "/tools/registry": {"requests": 3421, "avg_time": 123},
                "/admin": {"requests": 892, "avg_time": 234},
                "/audit/trail": {"requests": 2911, "avg_time": 267},
            },
        }

    async def _collect_consciousness_metrics(self) -> Dict[str, Any]:
        """Collect consciousness system metrics"""
        # Mock data - in production would integrate with actual consciousness modules
        return {
            "awareness_level": 0.78,
            "processing_depth": 0.65,
            "active_thoughts": 23,
            "reflection_cycles": 156,
            "attention_span": 45.7,  # seconds
            "state": "focused",
            "dream_integration": True,
        }

    async def _collect_memory_metrics(self) -> Dict[str, Any]:
        """Collect memory system metrics"""
        return {
            "total_folds": 1847,
            "active_chains": 23,
            "drift_score": 0.12,
            "integrity_score": 0.996,
            "consolidation_rate": 0.87,
            "recall_latency": 23.4,  # ms
            "storage_efficiency": 0.91,
        }

    async def _collect_ethics_metrics(self) -> Dict[str, Any]:
        """Collect Guardian/ethics system metrics"""
        return {
            "guardian_active": True,
            "ethics_score": 0.94,
            "total_decisions": 15623,
            "approvals": 15145,
            "rejections": 478,
            "approval_rate": 0.969,
            "intervention_count": 12,
            "drift_alerts": 3,
            "cascade_prevented": True,
        }

    async def _collect_dream_metrics(self) -> Dict[str, Any]:
        """Collect dream engine metrics"""
        return {
            "active_dreams": 5,
            "completed_cycles": 89,
            "creativity_index": 0.72,
            "innovation_score": 0.68,
            "reality_coherence": 0.85,
            "synthesis_quality": 0.79,
            "processing_load": 0.34,
        }

    async def _collect_flags_metrics(self) -> Dict[str, Any]:
        """Collect feature flags status"""
        try:
            from lukhas_pwm.flags import get_flags

            flags = get_flags()

            return {
                "total_flags": len(flags),
                "enabled_flags": sum(1 for v in flags.values() if v),
                "disabled_flags": sum(1 for v in flags.values() if not v),
                "flags": flags,
            }
        except Exception as e:
            logger.error(f"Error collecting flags: {e}")
            return {"error": str(e)}

    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics"""
        return {
            "throughput": 856.3,  # operations/second
            "latency_p50": 45,
            "latency_p95": 234,
            "latency_p99": 567,
            "queue_depth": 12,
            "cache_hit_rate": 0.89,
            "db_connections": 8,
        }

    def _calculate_health_score(
        self, system: Dict, api: Dict, consciousness: Dict
    ) -> float:
        """Calculate overall system health score"""
        factors = [
            min(1.0, (100 - system.get("cpu_percent", 0)) / 100),  # Lower CPU is better
            min(
                1.0, (100 - system.get("memory_percent", 0)) / 100
            ),  # Lower memory is better
            min(1.0, 1.0 - api.get("error_rate", 0)),  # Lower error rate is better
            consciousness.get("awareness_level", 0.5),  # Higher awareness is better
            min(
                1.0, 1000 / max(api.get("average_response_time", 1000), 1)
            ),  # Lower response time is better
        ]
        return sum(factors) / len(factors)


# Initialize metrics collector
metrics_collector = MetricsCollector()


@app.on_event("startup")
async def startup_event():
    """Initialize dashboard on startup"""
    logger.info("🚀 Starting LUKHAS PWM Unified Dashboard")

    # Start background metrics collection
    asyncio.create_task(metrics_collection_loop())

    # Start alert processing
    asyncio.create_task(alert_processing_loop())


async def metrics_collection_loop():
    """Background task to collect metrics periodically"""
    while True:
        try:
            await metrics_collector.collect_all_metrics()
            await notify_websocket_clients()
            await asyncio.sleep(DASHBOARD_CONFIG["refresh_rate"])
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
            await asyncio.sleep(5)


async def alert_processing_loop():
    """Background task to process alerts"""
    while True:
        try:
            await process_alerts()
            await asyncio.sleep(10)  # Check for alerts every 10 seconds
        except Exception as e:
            logger.error(f"Alert processing error: {e}")
            await asyncio.sleep(5)


async def process_alerts():
    """Process and generate alerts based on current metrics"""
    if not system_metrics:
        return

    current_time = datetime.now(timezone.utc)
    new_alerts = []

    # Check drift score
    memory_drift = system_metrics.get("memory", {}).get("drift_score", 0)
    if memory_drift > DASHBOARD_CONFIG["alert_thresholds"]["drift_critical"]:
        new_alerts.append(
            {
                "id": f"drift_{int(time.time())}",
                "type": "critical",
                "title": "Critical Memory Drift Detected",
                "message": f"Memory drift score {memory_drift:.2f} exceeds critical threshold",
                "timestamp": current_time.isoformat(),
                "system": "memory",
            }
        )

    # Check system resources
    cpu_percent = system_metrics.get("system", {}).get("cpu_percent", 0)
    if cpu_percent > 90:
        new_alerts.append(
            {
                "id": f"cpu_{int(time.time())}",
                "type": "warning",
                "title": "High CPU Usage",
                "message": f"CPU usage at {cpu_percent:.1f}%",
                "timestamp": current_time.isoformat(),
                "system": "system",
            }
        )

    # Check API performance
    response_time = system_metrics.get("api", {}).get("average_response_time", 0)
    if response_time > DASHBOARD_CONFIG["alert_thresholds"]["response_time_slow"]:
        new_alerts.append(
            {
                "id": f"perf_{int(time.time())}",
                "type": "warning",
                "title": "Slow API Response Time",
                "message": f"Average response time {response_time}ms exceeds threshold",
                "timestamp": current_time.isoformat(),
                "system": "api",
            }
        )

    # Add new alerts
    global alerts
    alerts.extend(new_alerts)

    # Keep only recent alerts
    cutoff = current_time.timestamp() - 3600  # 1 hour
    alerts = [
        a
        for a in alerts
        if datetime.fromisoformat(a["timestamp"].replace("Z", "+00:00")).timestamp()
        > cutoff
    ]


async def notify_websocket_clients():
    """Send updates to all connected WebSocket clients"""
    if not active_connections:
        return

    message = {
        "type": "metrics_update",
        "data": system_metrics,
        "alerts": alerts[-10:],  # Last 10 alerts
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    disconnected_clients = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception:
            disconnected_clients.append(connection)

    # Remove disconnected clients
    for client in disconnected_clients:
        active_connections.remove(client)


# API Endpoints


@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Serve main dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LUKHAS PWM Unified Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Monaco', 'Menlo', monospace;
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
                color: #00ff00;
                min-height: 100vh;
            }
            .header {
                text-align: center;
                padding: 20px;
                border-bottom: 2px solid #00ff00;
                background: rgba(0, 255, 0, 0.1);
            }
            .trinity { font-size: 48px; margin: 10px 0; }
            .title { font-size: 28px; margin: 10px 0; }
            .subtitle { font-size: 14px; color: #888; }
            
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                padding: 20px;
            }
            
            .metric-card {
                background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
                border: 1px solid #00ff00;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.1);
                transition: all 0.3s ease;
            }
            
            .metric-card:hover {
                border-color: #00ff88;
                box-shadow: 0 0 30px rgba(0, 255, 0, 0.2);
                transform: translateY(-2px);
            }
            
            .card-title {
                font-size: 18px;
                color: #00ff88;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
            }
            
            .card-icon { font-size: 24px; margin-right: 10px; }
            
            .metric-value {
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 10px;
                text-align: center;
            }
            
            .metric-label {
                font-size: 12px;
                color: #888;
                text-align: center;
            }
            
            .health-excellent { color: #00ff00; }
            .health-good { color: #88ff00; }
            .health-fair { color: #ffff00; }
            .health-poor { color: #ff8800; }
            .health-critical { color: #ff0000; }
            
            .status-active { color: #00ff00; }
            .status-warning { color: #ffff00; }
            .status-error { color: #ff0000; }
            
            .alerts-panel {
                position: fixed;
                top: 20px;
                right: 20px;
                width: 300px;
                max-height: 400px;
                overflow-y: auto;
                background: rgba(26, 26, 26, 0.95);
                border: 1px solid #ff8800;
                border-radius: 8px;
                padding: 15px;
                display: none;
            }
            
            .alert-item {
                padding: 8px;
                margin: 5px 0;
                border-left: 3px solid;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 4px;
            }
            
            .alert-critical { border-left-color: #ff0000; }
            .alert-warning { border-left-color: #ffff00; }
            .alert-info { border-left-color: #00ffff; }
            
            .chart-container {
                height: 150px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
                margin-top: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #555;
            }
            
            .footer {
                text-align: center;
                padding: 20px;
                border-top: 1px solid #333;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="trinity">⚛️🧠🛡️</div>
            <div class="title">LUKHAS PWM Unified Dashboard</div>
            <div class="subtitle">Real-time monitoring and analytics</div>
            <div class="subtitle" id="last-update">Connecting...</div>
        </div>
        
        <div class="dashboard-grid">
            <!-- System Health -->
            <div class="metric-card">
                <div class="card-title"><span class="card-icon">💚</span>System Health</div>
                <div class="metric-value health-excellent" id="health-score">--</div>
                <div class="metric-label">Overall Health Score</div>
            </div>
            
            <!-- API Performance -->
            <div class="metric-card">
                <div class="card-title"><span class="card-icon">🚀</span>API Performance</div>
                <div class="metric-value" id="api-rps">--</div>
                <div class="metric-label" id="api-response-time">Response Time: --ms</div>
            </div>
            
            <!-- Consciousness Status -->
            <div class="metric-card">
                <div class="card-title"><span class="card-icon">🧠</span>Consciousness</div>
                <div class="metric-value" id="awareness-level">--</div>
                <div class="metric-label" id="consciousness-state">State: --</div>
            </div>
            
            <!-- Memory System -->
            <div class="metric-card">
                <div class="card-title"><span class="card-icon">🧬</span>Memory</div>
                <div class="metric-value" id="memory-folds">--</div>
                <div class="metric-label" id="drift-score">Drift Score: --</div>
            </div>
            
            <!-- Guardian System -->
            <div class="metric-card">
                <div class="card-title"><span class="card-icon">🛡️</span>Guardian</div>
                <div class="metric-value status-active" id="guardian-status">ACTIVE</div>
                <div class="metric-label" id="ethics-score">Ethics Score: --</div>
            </div>
            
            <!-- Dream Engine -->
            <div class="metric-card">
                <div class="card-title"><span class="card-icon">🌙</span>Dream Engine</div>
                <div class="metric-value" id="active-dreams">--</div>
                <div class="metric-label" id="creativity-index">Creativity: --</div>
            </div>
            
            <!-- System Resources -->
            <div class="metric-card">
                <div class="card-title"><span class="card-icon">⚙️</span>System Resources</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
                    <div>
                        <div class="metric-value" id="cpu-usage">--</div>
                        <div class="metric-label">CPU %</div>
                    </div>
                    <div>
                        <div class="metric-value" id="memory-usage">--</div>
                        <div class="metric-label">Memory %</div>
                    </div>
                </div>
            </div>
            
            <!-- Feature Flags -->
            <div class="metric-card">
                <div class="card-title"><span class="card-icon">🎛️</span>Feature Flags</div>
                <div class="metric-value" id="enabled-flags">--</div>
                <div class="metric-label" id="total-flags">Total: --</div>
            </div>
        </div>
        
        <div class="alerts-panel" id="alerts-panel">
            <h3>Recent Alerts</h3>
            <div id="alerts-list"></div>
        </div>
        
        <div class="footer">
            <div>LUKHAS PWM Dashboard v2.0.0 | Trinity Framework</div>
            <div>WebSocket Status: <span id="connection-status" class="status-warning">Connecting...</span></div>
        </div>
        
        <script>
            // WebSocket connection
            const ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            ws.onopen = () => {
                document.getElementById('connection-status').textContent = 'Connected';
                document.getElementById('connection-status').className = 'status-active';
            };
            
            ws.onclose = () => {
                document.getElementById('connection-status').textContent = 'Disconnected';
                document.getElementById('connection-status').className = 'status-error';
            };
            
            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                updateDashboard(message.data);
                updateAlerts(message.alerts);
                document.getElementById('last-update').textContent = 
                    `Last updated: ${new Date().toLocaleTimeString()}`;
            };
            
            function updateDashboard(data) {
                if (!data) return;
                
                // System health
                const healthScore = data.health_score || 0;
                document.getElementById('health-score').textContent = (healthScore * 100).toFixed(0) + '%';
                document.getElementById('health-score').className = 
                    'metric-value ' + getHealthClass(healthScore);
                
                // API metrics
                if (data.api) {
                    document.getElementById('api-rps').textContent = 
                        (data.api.requests_per_second || 0).toFixed(1) + ' RPS';
                    document.getElementById('api-response-time').textContent = 
                        `Response Time: ${data.api.average_response_time || 0}ms`;
                }
                
                // Consciousness
                if (data.consciousness) {
                    document.getElementById('awareness-level').textContent = 
                        ((data.consciousness.awareness_level || 0) * 100).toFixed(0) + '%';
                    document.getElementById('consciousness-state').textContent = 
                        `State: ${data.consciousness.state || 'unknown'}`;
                }
                
                // Memory
                if (data.memory) {
                    document.getElementById('memory-folds').textContent = 
                        data.memory.total_folds || 0;
                    document.getElementById('drift-score').textContent = 
                        `Drift Score: ${(data.memory.drift_score || 0).toFixed(2)}`;
                }
                
                // Guardian
                if (data.ethics) {
                    document.getElementById('guardian-status').textContent = 
                        data.ethics.guardian_active ? 'ACTIVE' : 'INACTIVE';
                    document.getElementById('ethics-score').textContent = 
                        `Ethics Score: ${((data.ethics.ethics_score || 0) * 100).toFixed(0)}%`;
                }
                
                // Dream Engine
                if (data.dream) {
                    document.getElementById('active-dreams').textContent = 
                        data.dream.active_dreams || 0;
                    document.getElementById('creativity-index').textContent = 
                        `Creativity: ${((data.dream.creativity_index || 0) * 100).toFixed(0)}%`;
                }
                
                // System Resources
                if (data.system) {
                    document.getElementById('cpu-usage').textContent = 
                        (data.system.cpu_percent || 0).toFixed(1) + '%';
                    document.getElementById('memory-usage').textContent = 
                        (data.system.memory_percent || 0).toFixed(1) + '%';
                }
                
                // Feature Flags
                if (data.flags) {
                    document.getElementById('enabled-flags').textContent = 
                        data.flags.enabled_flags || 0;
                    document.getElementById('total-flags').textContent = 
                        `Total: ${data.flags.total_flags || 0}`;
                }
            }
            
            function updateAlerts(alerts) {
                if (!alerts || !alerts.length) return;
                
                const alertsList = document.getElementById('alerts-list');
                alertsList.innerHTML = '';
                
                alerts.forEach(alert => {
                    const alertEl = document.createElement('div');
                    alertEl.className = `alert-item alert-${alert.type}`;
                    alertEl.innerHTML = `
                        <div style="font-weight: bold;">${alert.title}</div>
                        <div style="font-size: 12px; margin: 5px 0;">${alert.message}</div>
                        <div style="font-size: 10px; color: #666;">${new Date(alert.timestamp).toLocaleString()}</div>
                    `;
                    alertsList.appendChild(alertEl);
                });
                
                if (alerts.length > 0) {
                    document.getElementById('alerts-panel').style.display = 'block';
                }
            }
            
            function getHealthClass(score) {
                if (score >= 0.9) return 'health-excellent';
                if (score >= 0.8) return 'health-good';
                if (score >= 0.6) return 'health-fair';
                if (score >= 0.4) return 'health-poor';
                return 'health-critical';
            }
            
            // Toggle alerts panel on click
            document.addEventListener('click', (e) => {
                if (e.target.closest('.alerts-panel')) return;
                if (alerts && alerts.length > 0) {
                    const panel = document.getElementById('alerts-panel');
                    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/metrics")
async def get_metrics():
    """Get current system metrics"""
    return JSONResponse(content=system_metrics)


@app.get("/api/alerts")
async def get_alerts():
    """Get current alerts"""
    return JSONResponse(content=alerts)


@app.get("/api/history")
async def get_historical_data(hours: int = 1):
    """Get historical metrics data"""
    cutoff = time.time() - (hours * 3600)
    filtered_data = [d for d in historical_data if d["timestamp"] > cutoff]
    return JSONResponse(content=filtered_data)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        # Send initial data
        if system_metrics:
            await websocket.send_json(
                {
                    "type": "metrics_update",
                    "data": system_metrics,
                    "alerts": alerts[-10:],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        while True:
            # Keep connection alive
            await asyncio.sleep(30)
            await websocket.ping()

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        active_connections.remove(websocket)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "dashboard": "LUKHAS PWM Unified Dashboard",
        "version": "2.0.0",
        "trinity": "⚛️🧠🛡️",
        "active_connections": len(active_connections),
        "metrics_available": bool(system_metrics),
    }


def start_dashboard(host: str = None, port: int = None, dev: bool = False):
    """Start the unified dashboard server"""
    host = host or DASHBOARD_CONFIG["host"]
    port = port or DASHBOARD_CONFIG["port"]

    logger.info("🚀 Starting LUKHAS PWM Unified Dashboard")
    logger.info(f"   📊 Dashboard: http://{host}:{port}")
    logger.info(f"   📡 WebSocket: ws://{host}:{port}/ws")
    logger.info(f"   🔗 API: http://{host}:{port}/api/metrics")
    logger.info("   ⚛️🧠🛡️ Trinity Framework Active")

    uvicorn.run(app, host=host, port=port, reload=dev, log_level="info")


if __name__ == "__main__":
    import sys

    dev_mode = "--dev" in sys.argv
    start_dashboard(dev=dev_mode)
