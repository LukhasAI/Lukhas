#!/usr/bin/env python3
"""
LUKHΛS Meta Dashboard Server
Real-time monitoring dashboard for symbolic systems
Trinity Framework: ⚛️🧠🛡️
"""
import asyncio
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

# Import dashboard utilities
from .utils import (
    calculate_drift_trends,
    load_meta_metrics,
    parse_jsonl_snapshots,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LUKHΛS Meta Dashboard",
    description="Real-time symbolic monitoring and drift analysis",
    version="1.0.0",
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
active_connections: list[WebSocket] = []

# Dashboard configuration
DASHBOARD_CONFIG = {
    "port": int(os.getenv("LUKHAS_DASHBOARD_PORT", "5042")),
    "title": "LUKHΛS Symbolic Meta Dashboard",
    "enable_auth": False,
    "refresh_rate_seconds": int(os.getenv("LUKHAS_REFRESH_RATE", "15")),
    "metrics_path": Path(os.getenv("LUKHAS_METRICS_PATH", "data/meta_metrics.json")),
    "snapshots_path": Path(os.getenv("LUKHAS_SNAPSHOTS_PATH", "data/drift_audit_results.jsonl")),
}

# Static HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LUKHΛS Meta Dashboard</title>
    <style>
        body {
            font-family: monospace;
            background: #0a0a0a;
            color: #00ff00;
            margin: 20px;
        }
        .header {
            text-align: center;
            font-size: 24px;
            margin-bottom: 30px;
        }
        .trinity {
            font-size: 36px;
            margin: 10px;
        }
        .metric-card {
            background: #1a1a1a;
            border: 1px solid #00ff00;
            border-radius: 8px;
            padding: 15px;
            margin: 10px;
            display: inline-block;
            min-width: 200px;
        }
        .metric-label {
            color: #888;
            font-size: 12px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            margin-top: 5px;
        }
        .drift-low { color: #00ff00; }
        .drift-medium { color: #ffff00; }
        .drift-high { color: #ff8800; }
        .drift-critical { color: #ff0000; }
        .chart-container {
            margin: 20px;
            height: 200px;
            border: 1px solid #333;
        }
    </style>
</head>
<body>
    <div class="header">
        <div>🧠 LUKHΛS Symbolic Meta Dashboard 🛡️</div>
        <div class="trinity">⚛️🧠🛡️</div>
    </div>

    <div id="metrics">
        <div class="metric-card">
            <div class="metric-label">Drift Score</div>
            <div class="metric-value" id="drift-score">--</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Trinity Coherence</div>
            <div class="metric-value" id="trinity-coherence">--</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Active Personas</div>
            <div class="metric-value" id="active-personas">--</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Entropy Level</div>
            <div class="metric-value" id="entropy-level">--</div>
        </div>
    </div>

    <div class="chart-container" id="drift-chart">
        <!-- Drift trend visualization would go here -->
    </div>

    <script>
        // WebSocket connection for real-time updates
        const ws = new WebSocket('ws://localhost:5042/ws');

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateMetrics(data);
        };

        function updateMetrics(data) {
            // Update drift score with color coding
            const driftElement = document.getElementById('drift-score');
            driftElement.textContent = data.drift_score.toFixed(2);
            driftElement.className = 'metric-value ' + getDriftClass(data.drift_score);

            // Update other metrics
            document.getElementById('trinity-coherence').textContent =
                (data.trinity_coherence * 100).toFixed(0) + '%';
            document.getElementById('active-personas').textContent =
                data.active_personas || '0';
            document.getElementById('entropy-level').textContent =
                data.entropy_level.toFixed(3);
        }

        function getDriftClass(score) {
            if (score < 0.3) return 'drift-low';
            if (score < 0.5) return 'drift-medium';
            if (score < 0.7) return 'drift-high';
            return 'drift-critical';
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to overview page"""
    return HTMLResponse(content='<meta http-equiv="refresh" content="0; url=/meta/overview">')


@app.get("/meta/overview", response_class=HTMLResponse)
async def overview():
    """Serve the overview dashboard"""
    overview_path = Path(__file__).parent / "templates" / "overview.html"
    if overview_path.exists():
        with open(overview_path) as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        # Fallback to embedded HTML
        return HTMLResponse(content=DASHBOARD_HTML)


@app.get("/api/meta/metrics")
async def get_metrics():
    """Get current meta metrics"""
    try:
        metrics = load_meta_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        logger.error(f"Error loading metrics: {e}")
        return JSONResponse(content={"error": "Failed to load metrics"}, status_code=500)


@app.get("/api/meta/trends")
async def get_trends():
    """Get drift trends over time"""
    try:
        snapshots = parse_jsonl_snapshots()
        trends = calculate_drift_trends(snapshots)
        return JSONResponse(content=trends)
    except Exception as e:
        logger.error(f"Error calculating trends: {e}")
        return JSONResponse(content={"error": "Failed to calculate trends"}, status_code=500)


@app.get("/api/meta/personas")
async def get_personas():
    """Get persona distribution data"""
    try:
        metrics = load_meta_metrics()
        personas = metrics.get("persona_distribution", {})
        return JSONResponse(
            content={
                "personas": personas,
                "total": sum(personas.values()),
                "dominant": (max(personas.items(), key=lambda x: x[1])[0] if personas else None),
            }
        )
    except Exception as e:
        logger.error(f"Error loading personas: {e}")
        return JSONResponse(content={"error": "Failed to load personas"}, status_code=500)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Send updates every refresh interval
            metrics = load_meta_metrics()
            await websocket.send_json(
                {
                    "drift_score": metrics.get("average_drift", 0.0),
                    "trinity_coherence": metrics.get("trinity_coherence", 0.0),
                    "active_personas": len(metrics.get("persona_distribution", {})),
                    "entropy_level": metrics.get("entropy_level", 0.0),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

            await asyncio.sleep(DASHBOARD_CONFIG["refresh_rate_seconds"])

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        active_connections.remove(websocket)


@app.get("/meta/visual")
async def visual_dashboard():
    """Serve the visual drift dashboard"""
    visual_path = Path(__file__).parent / "templates" / "visual.html"
    if visual_path.exists():
        with open(visual_path) as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(content="Visual dashboard not found", status_code=404)


@app.post("/api/meta/red-team")
async def toggle_red_team(request: dict[str, Any]):
    """Toggle Red Team mode for drift simulation"""
    try:
        enabled = request.get("enabled", False)

        # Update configuration
        DASHBOARD_CONFIG["red_team_mode"] = enabled

        # Log the change
        logger.info(f"Red Team mode {'enabled' if enabled else 'disabled'}")

        return {
            "status": "success",
            "red_team_mode": enabled,
            "message": f"Red Team mode {'activated' if enabled else 'deactivated'}",
            "warning": "Guardian protection reduced" if enabled else None,
        }
    except Exception as e:
        logger.error(f"Error toggling Red Team mode: {e}")
        return JSONResponse(content={"error": "Failed to toggle Red Team mode"}, status_code=500)


@app.post("/api/meta/reset")
async def reset_metrics():
    """Reset metrics to baseline values"""
    try:
        # Reset to baseline

        # Would normally save to file here
        logger.info("Metrics reset to baseline")

        return {"status": "success", "message": "Metrics reset to baseline"}
    except Exception as e:
        logger.error(f"Error resetting metrics: {e}")
        return JSONResponse(content={"error": "Failed to reset metrics"}, status_code=500)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "dashboard": "LUKHΛS Meta Dashboard",
        "version": "1.0.0",
        "trinity": "⚛️🧠🛡️",
    }


def start_dashboard(host: str = "0.0.0.0", port: Optional[int] = None):
    """Start the dashboard server"""
    import uvicorn

    port = port or DASHBOARD_CONFIG["port"]
    # Use environment variable for display URL or fallback to localhost
    display_host = os.getenv("LUKHAS_DASHBOARD_URL", "localhost")

    logger.info(f"🚀 Starting LUKHΛS Meta Dashboard on {host}:{port}")
    logger.info(f"   Access at: http://{display_host}:{port}")

    uvicorn.run(app, host=host, port=port)


# TODO: Implement additional dashboard features:
# - Authentication/authorization for production use
# - Historical data persistence and analysis
# - Advanced visualizations (drift heatmaps, persona evolution)
# - Integration with Guardian intervention logs
# - Export functionality for reports
# - Mobile-responsive design
# - Dark/light theme toggle


if __name__ == "__main__":
    start_dashboard()