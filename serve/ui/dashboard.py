"""
LUKHAS UI Dashboard Implementation
Agent 5: User Experience & Feedback Specialist
Implements passkey login, workflow transparency, feedback collection
"""

import os
import uuid

# Import other agents' components (absolute imports; no sys.path hacks)
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from core.identity.lambda_id_core import LukhasIdentityService
from lukhas.governance.consent_ledger.ledger_v1 import ConsentLedgerV1, PolicyEngine
from lukhas.orchestration.context_bus_enhanced import (
    ContextBusOrchestrator,
    WorkflowPipelines,
)

# Initialize FastAPI app
app = FastAPI(
    title="LUKHAS AI Dashboard",
    description="User interface for LUKHAS AI with passkey authentication and workflow transparency",
    version="1.0.0",
)

# Initialize services
identity_service = LukhasIdentityService()
consent_ledger = ConsentLedgerV1()
policy_engine = PolicyEngine(consent_ledger)
orchestrator = ContextBusOrchestrator()


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()

# Feedback storage (in production: use database)
feedback_storage = []


# Request/Response models
class LoginRequest(BaseModel):
    email: str
    display_name: Optional[str] = None


class PasskeyAuthRequest(BaseModel):
    lid: str
    credential: dict[str, Any]


class ConsentRequest(BaseModel):
    lid: str
    resource_type: str
    scopes: list[str]
    purpose: str


class WorkflowRequest(BaseModel):
    lid: str
    workflow_name: str
    context: Optional[dict[str, Any]] = None


class FeedbackSubmission(BaseModel):
    lid: str
    workflow_id: str
    rating: int  # 1-5 stars
    comment: Optional[str] = None
    timestamp: Optional[str] = None


# HTML Templates (inline for simplicity)
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LUKHAS AI - Login</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 400px;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 14px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
            transition: background 0.3s;
        }
        button:hover {
            background: #5a67d8;
        }
        .passkey-btn {
            background: #48bb78;
        }
        .passkey-btn:hover {
            background: #38a169;
        }
        .trinity {
            text-align: center;
            margin-top: 20px;
            font-size: 24px;
        }
        .performance {
            text-align: center;
            color: #48bb78;
            margin-top: 10px;
            font-size: 12px;
        }
    </style>
    <script>
        async function registerWithPasskey() {
            const email = document.getElementById('email').value;
            const displayName = document.getElementById('displayName').value || email;

            // Register user
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, display_name: displayName})
            });

            const data = await response.json();

            if (data.lid && data.passkey_options) {
                // Create passkey
                try {
                    const credential = await navigator.credentials.create(data.passkey_options);

                    // Complete registration
                    const authResponse = await fetch('/api/authenticate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            lid: data.lid,
                            credential: {
                                id: credential.id,
                                response: {
                                    clientDataJSON: arrayBufferToBase64(credential.response.clientDataJSON),
                                    attestationObject: arrayBufferToBase64(credential.response.attestationObject)
                                }
                            }
                        })
                    });

                    const authData = await authResponse.json();
                    if (authData.success) {
                        localStorage.setItem('lid', data.lid);
                        localStorage.setItem('token', authData.token);
                        window.location.href = '/dashboard';
                    }
                } catch (e) {
                    alert('Passkey creation failed: ' + e.message);
                }
            }

            // Show performance
            if (data.performance) {
                document.getElementById('performance').innerHTML =
                    `⚡ Auth latency: ${data.performance.latency_ms.toFixed(2)}ms`;
            }
        }

        function arrayBufferToBase64(buffer) {
            return btoa(String.fromCharCode(...new Uint8Array(buffer)));
        }
    </script>
</head>
<body>
    <div class="login-container">
        <h1>🎭 LUKHAS AI</h1>
        <div class="subtitle">Secure AI with Transparency</div>

        <input type="email" id="email" placeholder="Email" required>
        <input type="text" id="displayName" placeholder="Display Name (optional)">

        <button class="passkey-btn" onclick="registerWithPasskey()">
            🔐 Login with Passkey
        </button>

        <div class="trinity">⚛️ 🧠 🛡️</div>
        <div class="performance" id="performance"></div>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LUKHAS AI - Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f7fafc;
            margin: 0;
            padding: 0;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .container {
            max-width: 1200px;
            margin: 20px auto;
            padding: 0 20px;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .workflow-input {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .workflow-input input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        .btn {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
        }
        .btn:hover {
            background: #5a67d8;
        }
        .consent-prompt {
            background: #fef5e7;
            border: 1px solid #f39c12;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .workflow-narrative {
            background: #2d3748;
            color: #48bb78;
            padding: 15px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            max-height: 400px;
            overflow-y: auto;
        }
        .feedback-section {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
        }
        .stars {
            display: flex;
            gap: 10px;
            margin: 10px 0;
        }
        .star {
            font-size: 30px;
            cursor: pointer;
            color: #cbd5e0;
        }
        .star.active {
            color: #f6ad55;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .metric {
            text-align: center;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
        .metric-label {
            color: #718096;
            margin-top: 5px;
        }
    </style>
    <script>
        let ws = null;
        let currentWorkflowId = null;

        async function connectWebSocket() {
            const lid = localStorage.getItem('lid');
            ws = new WebSocket(`ws://localhost:8000/ws/${lid}`);

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateNarrative(data.message);
            };
        }

        async function runWorkflow() {
            const request = document.getElementById('workflowRequest').value;
            const lid = localStorage.getItem('lid');

            // Request consent first
            await requestConsent();

            // Run workflow
            const response = await fetch('/api/workflow/execute', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    lid: lid,
                    workflow_name: 'Travel Document Analysis',
                    context: {request: request}
                })
            });

            const data = await response.json();
            currentWorkflowId = data.workflow_id;

            // Display results
            if (data.narrative) {
                const narrativeDiv = document.getElementById('narrative');
                narrativeDiv.innerHTML = data.narrative.join('<br>');
            }

            // Show feedback section
            document.getElementById('feedbackSection').style.display = 'block';
        }

        async function requestConsent() {
            const lid = localStorage.getItem('lid');

            // Show consent prompt
            document.getElementById('consentPrompt').style.display = 'block';

            // Grant consent for demo
            const services = ['gmail', 'drive', 'dropbox'];
            for (const service of services) {
                await fetch('/api/consent/grant', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        lid: lid,
                        resource_type: service,
                        scopes: ['read', 'list'],
                        purpose: 'travel_document_analysis'
                    })
                });
            }

            setTimeout(() => {
                document.getElementById('consentPrompt').style.display = 'none';
            }, 2000);
        }

        function updateNarrative(message) {
            const narrativeDiv = document.getElementById('narrative');
            narrativeDiv.innerHTML += message + '<br>';
            narrativeDiv.scrollTop = narrativeDiv.scrollHeight;
        }

        function setRating(rating) {
            const stars = document.querySelectorAll('.star');
            stars.forEach((star, index) => {
                if (index < rating) {
                    star.classList.add('active');
                } else {
                    star.classList.remove('active');
                }
            });
            document.getElementById('ratingValue').value = rating;
        }

        async function submitFeedback() {
            const lid = localStorage.getItem('lid');
            const rating = document.getElementById('ratingValue').value;
            const comment = document.getElementById('feedbackComment').value;

            await fetch('/api/feedback/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    lid: lid,
                    workflow_id: currentWorkflowId,
                    rating: parseInt(rating),
                    comment: comment
                })
            });

            alert('Thank you for your feedback!');
            document.getElementById('feedbackSection').style.display = 'none';
        }

        async function loadMetrics() {
            const response = await fetch('/api/metrics');
            const metrics = await response.json();

            document.getElementById('authLatency').innerHTML = metrics.auth_latency_ms.toFixed(2) + 'ms';
            document.getElementById('handoffLatency').innerHTML = metrics.handoff_latency_ms.toFixed(2) + 'ms';
            document.getElementById('consentActive').innerHTML = metrics.active_consents;
            document.getElementById('workflowsRun').innerHTML = metrics.workflows_completed;
        }

        window.onload = function() {
            connectWebSocket();
            loadMetrics();
            setInterval(loadMetrics, 5000);  // Refresh metrics every 5 seconds
        };
    </script>
</head>
<body>
    <div class="header">
        <h1>🎭 LUKHAS AI Dashboard</h1>
        <div>
            <span id="userLid"></span>
            <button class="btn" onclick="location.href='/logout'">Logout</button>
        </div>
    </div>

    <div class="container">
        <!-- Consent Prompt -->
        <div id="consentPrompt" class="consent-prompt" style="display:none;">
            🛡️ <strong>Consent Required</strong><br>
            LUKHAS needs permission to access your Gmail, Drive, and Dropbox for travel document analysis.
            <button class="btn" style="margin-top:10px;">Grant Access</button>
        </div>

        <!-- Workflow Input -->
        <div class="card">
            <h2>🔄 Run Workflow</h2>
            <div class="workflow-input">
          <input type="text" id="workflowRequest" placeholder="e.g., Summarize my travel documents from Gmail"
              " and Dropbox">
                <button class="btn" onclick="runWorkflow()">Execute</button>
            </div>
        </div>

        <!-- Workflow Narrative -->
        <div class="card">
            <h2>📖 Workflow Progress</h2>
            <div id="narrative" class="workflow-narrative">
                Ready to execute workflows...
            </div>
        </div>

        <!-- Feedback Section -->
        <div id="feedbackSection" class="card" style="display:none;">
            <h2>💭 Provide Feedback</h2>
            <div class="feedback-section">
                <p>How helpful was this analysis?</p>
                <div class="stars">
                    <span class="star" onclick="setRating(1)">⭐</span>
                    <span class="star" onclick="setRating(2)">⭐</span>
                    <span class="star" onclick="setRating(3)">⭐</span>
                    <span class="star" onclick="setRating(4)">⭐</span>
                    <span class="star" onclick="setRating(5)">⭐</span>
                </div>
                <input type="hidden" id="ratingValue" value="0">
                <textarea id="feedbackComment" placeholder="Additional comments (optional)"
                          style="width:100%; padding:10px; margin:10px 0; border:1px solid #ddd; border-radius:6px;"></textarea>
                <button class="btn" onclick="submitFeedback()">Submit Feedback</button>
            </div>
        </div>

        <!-- Performance Metrics -->
        <div class="card">
            <h2>⚡ Performance Metrics</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value" id="authLatency">0.00ms</div>
                    <div class="metric-label">Auth Latency</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="handoffLatency">0.00ms</div>
                    <div class="metric-label">Context Handoff</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="consentActive">0</div>
                    <div class="metric-label">Active Consents</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="workflowsRun">0</div>
                    <div class="metric-label">Workflows Run</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# API Endpoints


@app.get("/")
async def home() -> HTMLResponse:
    """Login page"""
    return HTMLResponse(content=LOGIN_HTML)


@app.get("/dashboard")
async def dashboard() -> HTMLResponse:
    """Main dashboard"""
    return HTMLResponse(content=DASHBOARD_HTML)


@app.post("/api/register")
async def register(request: LoginRequest) -> dict[str, Any]:
    """Register user with ΛID"""
    result = identity_service.register_user(email=request.email, display_name=request.display_name or request.email)
    return result


@app.post("/api/authenticate")
async def authenticate(request: PasskeyAuthRequest) -> dict[str, Any]:
    """Authenticate with passkey"""
    result = identity_service.authenticate(lid=request.lid, method="passkey", credential=request.credential)

    if result["success"]:
        # Create session (in production: use secure session management)
        return {
            "success": True,
            "lid": request.lid,
            "token": result["tokens"]["id_token"],
            "performance": result["performance"],
        }

    return {"success": False, "error": "Authentication failed"}


@app.post("/api/consent/grant")
async def grant_consent(request: ConsentRequest) -> dict[str, Any]:
    """Grant consent for resource access"""
    consent = consent_ledger.grant_consent(
        lid=request.lid,
        resource_type=request.resource_type,
        scopes=request.scopes,
        purpose=request.purpose,
        expires_in_days=90,
    )

    return {"consent_id": consent.consent_id, "granted": True}


@app.post("/api/consent/revoke")
async def revoke_consent(lid: str, consent_id: str) -> dict[str, Any]:
    """Revoke consent"""
    success = consent_ledger.revoke_consent(consent_id, lid)
    return {"revoked": success}


@app.post("/api/workflow/execute")
async def execute_workflow(request: WorkflowRequest) -> dict[str, Any]:
    """Execute workflow with transparency"""

    # Create workflow pipeline
    pipeline = WorkflowPipelines.create_travel_analysis_pipeline(orchestrator)

    # Set adapters to dry-run for demo
    orchestrator.gmail_adapter.set_dry_run(True)
    orchestrator.drive_adapter.set_dry_run(True)
    orchestrator.dropbox_adapter.set_dry_run(True)

    # Execute workflow
    result = await orchestrator.execute_workflow(
        lid=request.lid,
        workflow_name=request.workflow_name,
        steps=pipeline,
        initial_context=request.context,
    )

    return result


@app.get("/api/workflow/status/{workflow_id}")
async def get_workflow_status(workflow_id: str) -> dict[str, Any]:
    """Get workflow status"""
    return orchestrator.get_workflow_status(workflow_id)


@app.post("/api/feedback/submit")
async def submit_feedback(feedback: FeedbackSubmission) -> dict[str, Any]:
    """Submit user feedback"""
    feedback.timestamp = datetime.now(timezone.utc).isoformat()
    feedback_storage.append(feedback.dict())

    # Emit Λ-trace for feedback
    consent_ledger.create_trace(
        lid=feedback.lid,
        action="submit_feedback",
        resource=feedback.workflow_id,
        purpose="user_feedback",
        verdict=policy_engine.PolicyVerdict.ALLOW,
        context={"rating": feedback.rating, "comment": feedback.comment},
    )

    return {"success": True, "feedback_id": f"FB-{uuid.uuid4()}.hex}"}


@app.get("/api/feedback/summary")
async def get_feedback_summary() -> dict[str, Any]:
    """Get feedback summary"""
    if not feedback_storage:
        return {"average_rating": 0, "total_feedback": 0}

    ratings = [f["rating"] for f in feedback_storage]
    return {
        "average_rating": sum(ratings) / len(ratings),
        "total_feedback": len(feedback_storage),
        "recent_comments": [f["comment"] for f in feedback_storage[-5:] if f.get("comment")],
    }


@app.get("/api/metrics")
async def get_metrics() -> dict[str, Any]:
    """Get system metrics"""
    perf_metrics = orchestrator.get_performance_metrics()

    # Get active consents count
    # In production: query database
    active_consents = 3  # Mock value

    return {
        "auth_latency_ms": identity_service.metrics.get("p95_latency", 0),
        "handoff_latency_ms": perf_metrics["handoff_performance"]["p95_ms"],
        "active_consents": active_consents,
        "workflows_completed": perf_metrics["workflows"]["completed"],
        "success_rate": perf_metrics["workflows"]["success_rate"],
    }


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str) -> None:
    """WebSocket for real-time updates"""
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Send workflow updates
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Update: {data}", client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)


@app.get("/logout")
async def logout() -> HTMLResponse:
    """Logout endpoint"""
    return HTMLResponse(content="<script>localStorage.clear(); location.href='/';</script>")


# Privacy Dashboard Extension
@app.get("/privacy")
async def privacy_dashboard() -> HTMLResponse:
    """Privacy and consent management dashboard"""
    privacy_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LUKHAS AI - Privacy Dashboard</title>
        <style>
            /* Reuse styles from main dashboard */
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f7fafc; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; }
            .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
            .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .btn-danger { background: #f56565; }
            .consent-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #e2e8f0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛡️ Privacy & Consent Dashboard</h1>
        </div>
        <div class="container">
            <div class="card">
                <h2>Active Consents</h2>
                <div class="consent-item">
                    <span>Gmail - Read & List Emails</span>
                    <button class="btn btn-danger">Revoke</button>
                </div>
                <div class="consent-item">
                    <span>Google Drive - Read Documents</span>
                    <button class="btn btn-danger">Revoke</button>
                </div>
                <div class="consent-item">
                    <span>Dropbox - Read Files</span>
                    <button class="btn btn-danger">Revoke</button>
                </div>
            </div>

            <div class="card">
                <h2>Data Access Log</h2>
                <p>All your data access is logged with Λ-trace audit records.</p>
                <button class="btn">Export Audit Log</button>
                <button class="btn btn-danger">Delete All Data</button>
            </div>

            <div class="card">
                <h2>GDPR/CCPA Rights</h2>
                <ul>
                    <li>✅ Right to access your data</li>
                    <li>✅ Right to rectification</li>
                    <li>✅ Right to erasure ("right to be forgotten")</li>
                    <li>✅ Right to data portability</li>
                    <li>✅ Right to object to processing</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=privacy_html)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("LUKHAS_BIND_HOST", "127.0.0.1")
    port = int(os.getenv("LUKHAS_BIND_PORT", "8000"))
    print("🎨 Starting LUKHAS UI Dashboard...")
    print(f"📍 Access at: http://{host}:{port}")
    print("⚡ Features: Passkey login, Workflow transparency, Feedback collection")
    uvicorn.run(app, host=host, port=port)
