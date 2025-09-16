#!/usr/bin/env python3
"""
LUKHΛS Meta Dashboard Server
Real-time monitoring dashboard for symbolic systems
Trinity Framework: ⚛️🧠🛡️
"""

import asyncio
import json
import logging
import os
import secrets
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Import dashboard utilities
from .utils import (
    analyze_persona_transitions,
    calculate_drift_trends,
    correlate_guardian_interventions,
    detect_drift_anomalies,
    export_dashboard_report,
    load_meta_metrics,
    parse_jsonl_snapshots,
    smooth_time_series,
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
    "history_path": Path(os.getenv("LUKHAS_HISTORY_PATH", "data/meta_history.jsonl")),
    "guardian_log_path": Path(os.getenv("LUKHAS_GUARDIAN_LOG", "data/guardian_interventions.jsonl")),
    "auth_token": os.getenv("LUKHAS_DASHBOARD_TOKEN"),
    "default_theme": os.getenv("LUKHAS_DASHBOARD_THEME", "dark"),
}

if DASHBOARD_CONFIG["auth_token"]:
    DASHBOARD_CONFIG["enable_auth"] = True

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
            transition: background 0.3s ease, color 0.3s ease;
        }
        body[data-theme="light"] {
            background: #f5f5f5;
            color: #1f2933;
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
            background: rgba(26, 26, 26, 0.9);
            border: 1px solid #00ff00;
            border-radius: 8px;
            padding: 15px;
            margin: 10px;
            display: inline-block;
            min-width: 200px;
        }
        body[data-theme="light"] .metric-card {
            background: rgba(255, 255, 255, 0.9);
            border-color: #1f2933;
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
        .theme-toggle {
            margin: 10px auto;
            display: inline-flex;
            padding: 6px 12px;
            border: 1px solid currentColor;
            border-radius: 4px;
            cursor: pointer;
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
        body[data-theme="light"] .chart-container {
            border-color: #ccc;
        }
        @media (max-width: 640px) {
            body {
                margin: 10px;
                font-size: 14px;
            }
            .metric-card {
                min-width: 140px;
                width: calc(50% - 24px);
            }
            .header {
                font-size: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div>🧠 LUKHΛS Symbolic Meta Dashboard 🛡️</div>
        <div class="trinity">⚛️🧠🛡️</div>
        <button class="theme-toggle" onclick="toggleTheme()">Toggle Theme</button>
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
        const ws = new WebSocket(`ws://${window.location.host}/ws`);

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateMetrics(data);
        };

        function toggleTheme() {
            const current = document.body.getAttribute('data-theme');
            const next = current === 'light' ? 'dark' : 'light';
            document.body.setAttribute('data-theme', next);
            localStorage.setItem('lukhas-dashboard-theme', next);
        }

        (function initialiseTheme() {
            const saved = localStorage.getItem('lukhas-dashboard-theme');
            const initial = saved || '%(theme)s';
            document.body.setAttribute('data-theme', initial);
        })();

        function updateMetrics(data) {
            // Update drift score with color coding
            const driftElement = document.getElementById('drift-score');
            driftElement.textContent = data.drift_score.toFixed(2);
            driftElement.className = 'metric-value ' + getDriftClass(data.drift_score);

            // Update other metrics
            document.getElementById('trinity-coherence').textContent =
                (data.triad_coherence * 100).toFixed(0) + '%';
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


class DashboardHistoryStore:
    """Persist dashboard metrics for historical analysis."""

    # ΛTAG: dashboard_history
    def __init__(self, path: Path):
        self.path = path
        self._lock: Optional[asyncio.Lock] = None

    async def _ensure_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def append(self, record: dict[str, Any]) -> None:
        lock = await self._ensure_lock()
        async with lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")

    async def load(self, limit: Optional[int] = None) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        with open(self.path, encoding="utf-8") as handle:
            lines = handle.readlines()

        if limit is not None:
            lines = lines[-limit:]

        history = []
        for line in lines:
            try:
                history.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return history

    async def clear(self) -> None:
        lock = await self._ensure_lock()
        async with lock:
            if self.path.exists():
                self.path.unlink()


history_store = DashboardHistoryStore(DASHBOARD_CONFIG["history_path"])
security = HTTPBearer(auto_error=False)


async def require_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> None:
    """Simple bearer token authentication for production usage."""

    if not DASHBOARD_CONFIG["enable_auth"]:
        return

    expected_token = DASHBOARD_CONFIG.get("auth_token")
    provided = credentials.credentials if credentials else None

    if not expected_token or not provided or not secrets.compare_digest(provided, expected_token):
        raise HTTPException(status_code=401, detail="Unauthorized")


def _load_guardian_interventions() -> list[dict[str, Any]]:
    path = DASHBOARD_CONFIG["guardian_log_path"]
    if not path.exists():
        return []

    interventions = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                interventions.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return interventions


def _dominant_persona_from_metrics(metrics: dict[str, Any]) -> Optional[str]:
    distribution = metrics.get("persona_distribution", {}) or {}
    if not distribution:
        return None
    return max(distribution.items(), key=lambda item: item[1])[0]


def _build_drift_heatmap(snapshots: list[dict[str, Any]], bucket_minutes: int = 60) -> list[dict[str, Any]]:
    buckets: dict[str, list[float]] = {}
    for snapshot in snapshots:
        ts_raw = snapshot.get("timestamp")
        if not ts_raw:
            continue
        try:
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        bucket_time = ts.replace(minute=(ts.minute // bucket_minutes) * bucket_minutes, second=0, microsecond=0)
        bucket_key = bucket_time.isoformat()
        buckets.setdefault(bucket_key, []).append(snapshot.get("drift_score", 0.0))

    heatmap = []
    for key, values in sorted(buckets.items()):
        if not values:
            continue
        heatmap.append({"bucket": key, "average_drift": float(statistics.fmean(values)), "samples": len(values)})

    return heatmap


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
        return HTMLResponse(content=DASHBOARD_HTML % {"theme": DASHBOARD_CONFIG["default_theme"]})


@app.get("/api/meta/metrics", dependencies=[Depends(require_auth)])
async def get_metrics():
    """Get current meta metrics"""
    try:
        metrics = load_meta_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        logger.error(f"Error loading metrics: {e}")
        return JSONResponse(content={"error": "Failed to load metrics"}, status_code=500)


@app.post("/api/meta/metrics", dependencies=[Depends(require_auth)])
async def update_metrics(payload: dict[str, Any]):
    """Persist new metrics payload and append to history."""

    try:
        DASHBOARD_CONFIG["metrics_path"].parent.mkdir(parents=True, exist_ok=True)
        with open(DASHBOARD_CONFIG["metrics_path"], "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

        await history_store.append({"timestamp": datetime.now(timezone.utc).isoformat(), **payload})
        return {"status": "success"}
    except Exception as e:  # pragma: no cover - defensive logging
        logger.error(f"Error updating metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to update metrics")


@app.get("/api/meta/trends", dependencies=[Depends(require_auth)])
async def get_trends():
    """Get drift trends over time"""
    try:
        snapshots = parse_jsonl_snapshots()
        trends = calculate_drift_trends(snapshots)
        return JSONResponse(content=trends)
    except Exception as e:
        logger.error(f"Error calculating trends: {e}")
        return JSONResponse(content={"error": "Failed to calculate trends"}, status_code=500)


@app.get("/api/meta/personas", dependencies=[Depends(require_auth)])
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


@app.get("/api/meta/history", dependencies=[Depends(require_auth)])
async def get_history(limit: Optional[int] = 200):
    """Return persisted dashboard history records."""

    history = await history_store.load(limit=limit)
    return {"count": len(history), "entries": history}


@app.delete("/api/meta/history", dependencies=[Depends(require_auth)])
async def clear_history():
    """Clear persisted dashboard history."""

    await history_store.clear()
    return {"status": "cleared"}


@app.get("/api/meta/drift/analysis", dependencies=[Depends(require_auth)])
async def drift_analysis():
    """Provide smoothed drift data and anomaly detection."""

    snapshots = parse_jsonl_snapshots()
    drift_scores = [snap.get("drift_score", 0.0) for snap in snapshots if "drift_score" in snap]
    smoothed = smooth_time_series(drift_scores)
    anomalies = detect_drift_anomalies(drift_scores)
    heatmap = _build_drift_heatmap(snapshots)

    return {
        "total_points": len(drift_scores),
        "smoothed": smoothed,
        "anomaly_indices": anomalies,
        "heatmap": heatmap,
    }


@app.get("/api/meta/personas/transitions", dependencies=[Depends(require_auth)])
async def persona_transitions(limit: Optional[int] = 200):
    """Analyze persona transitions based on stored history."""

    history = await history_store.load(limit=limit)
    persona_sequence: list[str] = []
    for record in history:
        persona = record.get("dominant_persona") or _dominant_persona_from_metrics(record)
        if persona:
            persona_sequence.append(persona)

    transitions = list(zip(persona_sequence, persona_sequence[1:])) if len(persona_sequence) > 1 else []
    analysis = analyze_persona_transitions(transitions)
    return {"sequence_length": len(persona_sequence), **analysis}


@app.get("/api/meta/guardian", dependencies=[Depends(require_auth)])
async def guardian_correlation(limit: Optional[int] = 200):
    """Correlate Guardian interventions with drift events."""

    interventions = _load_guardian_interventions()
    snapshots = parse_jsonl_snapshots()
    drift_events = snapshots[-limit:] if limit else snapshots
    correlation = correlate_guardian_interventions(interventions, drift_events)
    return correlation


@app.post("/api/meta/export", dependencies=[Depends(require_auth)])
async def export_report(destination: Optional[str] = None):
    """Export metrics and recent history to a JSON report file."""

    metrics = load_meta_metrics()
    history = await history_store.load(limit=500)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "history": history,
    }

    output_path = Path(destination or "exports/meta_dashboard_report.json")
    export_dashboard_report(payload, output_path)
    return {"status": "exported", "path": str(output_path.resolve())}


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
                    "triad_coherence": metrics.get("triad_coherence", 0.0),
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


@app.post("/api/meta/red-team", dependencies=[Depends(require_auth)])
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


@app.post("/api/meta/reset", dependencies=[Depends(require_auth)])
async def reset_metrics():
    """Reset metrics to baseline values"""
    try:
        baseline = {
            "average_drift": 0.0,
            "triad_coherence": 1.0,
            "entropy_level": 0.0,
            "persona_distribution": {},
            "total_evaluations": 0,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        with open(DASHBOARD_CONFIG["metrics_path"], "w", encoding="utf-8") as handle:
            json.dump(baseline, handle, indent=2)

        await history_store.append({"timestamp": baseline["last_updated"], **baseline})
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


if __name__ == "__main__":
    start_dashboard()
