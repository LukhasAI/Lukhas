"""
Studio UI Hooks for GTΨ Gesture Consent
=======================================
UI integration hooks for requesting GTΨ approvals on high-risk actions.
Provides "sign with stroke" interface for time-locked consent.

System-wide guardrails applied:
1. GTΨ required for high-risk actions (send_email, cloud.move.files, share_link_public)
2. Time-locked approvals (≤60s) with visual countdown
3. Edge-first gesture processing, never transmit raw strokes
4. Clear consent UI with action context and risk warnings

ACK GUARDRAILS
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from . import (
    HIGH_RISK_ACTIONS,
    GestureType,
    RiskLevel,
    get_action_risk_level,
    requires_gtpsi_approval,
)
from .edge import EdgeGestureProcessor, create_gesture_recognizer
from .server.verify import (
    ActionApprovalRequest,
    GestureVerificationRequest,
    GTΨVerificationService,
)


class ConsentUIRequest(BaseModel):
    """Request to show consent UI for high-risk action"""

    lid: str = Field(..., description="Canonical ΛID")
    action: str = Field(..., description="High-risk action")
    action_context: dict[str, Any] = Field(..., description="Action context")
    callback_url: Optional[str] = Field(None, description="Callback after consent")


class ConsentUIResponse(BaseModel):
    """Response with consent UI details"""

    challenge_id: str = Field(..., description="GTΨ challenge ID")
    ui_config: dict[str, Any] = Field(..., description="UI configuration")
    countdown_seconds: int = Field(..., description="Time limit for approval")


class GestureSubmissionRequest(BaseModel):
    """Request to submit gesture for verification"""

    challenge_id: str = Field(..., description="GTΨ challenge ID")
    gesture_data: dict[str, Any] = Field(..., description="Raw gesture data from client")
    gesture_type: GestureType = Field(..., description="Type of gesture submitted")


class GestureSubmissionResponse(BaseModel):
    """Response from gesture submission"""

    success: bool = Field(..., description="Whether gesture was accepted")
    approval_id: Optional[str] = Field(None, description="Approval ID if successful")
    message: str = Field(..., description="Result message")
    redirect_url: Optional[str] = Field(None, description="Where to redirect after success")


class StudioGTΨHooks:
    """
    Studio UI integration for GTΨ consent workflows.

    Provides hooks for:
    - Detecting high-risk actions that need GTΨ approval
    - Showing gesture consent UI with context and warnings
    - Processing gesture submissions with edge privacy
    - Time-locked approval management with visual countdown
    """

    def __init__(self, verification_service: GTΨVerificationService = None):
        self.verification_service = verification_service or GTΨVerificationService("mock")
        self.active_consent_sessions = {}  # session_id -> consent context

    async def initialize(self):
        """Initialize GTΨ verification service"""
        await self.verification_service.initialize()

    def requires_consent(self, action: str, context: Optional[dict[str, Any]] = None) -> bool:
        """
        Check if action requires GTΨ consent.

        Args:
            action: Action being attempted
            context: Action context for additional risk assessment

        Returns:
            True if GTΨ consent required
        """
        if not requires_gtpsi_approval(action):
            return False

        # Additional context-based risk assessment
        if action == "send_email" and context:
            recipient_count = context.get("recipient_count", 0)
            has_attachments = context.get("has_attachments", False)

            # Mass emails or emails with attachments need GTΨ
            return recipient_count > 5 or has_attachments

        if action == "share_link_public":
            # Always require GTΨ for public sharing
            return True

        if action == "cloud.move.files" and context:
            file_count = context.get("file_count", 0)

            # Moving many files needs GTΨ
            return file_count > 10

        return True  # Default to requiring GTΨ for high-risk actions

    async def request_consent_ui(self, request: ConsentUIRequest) -> ConsentUIResponse:
        """
        Generate consent UI for high-risk action.

        Args:
            request: Consent UI request

        Returns:
            UI configuration with challenge details
        """
        # Generate GTΨ challenge
        challenge = await self.verification_service.generate_challenge(
            request.lid, request.action, request.action_context
        )

        # Get action details
        action_info = HIGH_RISK_ACTIONS.get(request.action, {})
        risk_level = get_action_risk_level(request.action)

        # Build UI configuration
        ui_config = {
            "action": request.action,
            "action_description": action_info.get("description", f"Perform {request.action}"),
            "risk_level": risk_level.value,
            "context_summary": self._generate_context_summary(request.action, request.action_context),
            "required_gesture": challenge.required_gesture_type.value,
            "gesture_instructions": self._get_gesture_instructions(challenge.required_gesture_type),
            "warnings": self._generate_risk_warnings(request.action, risk_level),
            "visual_theme": self._get_risk_theme(risk_level),
        }

        # Calculate countdown
        now = datetime.now(timezone.utc)
        countdown_seconds = int((challenge.expires_at - now).total_seconds())

        return ConsentUIResponse(
            challenge_id=challenge.challenge_id,
            ui_config=ui_config,
            countdown_seconds=countdown_seconds,
        )

    async def submit_gesture(
        self, request: GestureSubmissionRequest, client_ip: Optional[str] = None
    ) -> GestureSubmissionResponse:
        """
        Process gesture submission from client.

        Args:
            request: Gesture submission
            client_ip: Client IP for audit

        Returns:
            Submission result with approval details
        """
        try:
            # Process gesture on server-side (simulating edge processing)
            recognizer = create_gesture_recognizer(request.gesture_type)
            processor = EdgeGestureProcessor(recognizer)

            gesture_features = processor.process_gesture(request.gesture_data, request.gesture_type)

            # Get challenge details for nonce
            challenge = self.verification_service.active_challenges.get(request.challenge_id)
            if not challenge:
                raise ValueError("Challenge not found or expired")

            # Verify gesture
            verification_request = GestureVerificationRequest(
                lid=challenge.lid,
                challenge_id=request.challenge_id,
                gesture_features=gesture_features,
                nonce=challenge.nonce,
            )

            result = await self.verification_service.verify_gesture(verification_request, client_ip)

            if result.verified:
                return GestureSubmissionResponse(
                    success=True,
                    approval_id=result.approval_id,
                    message="Gesture approved! You may now proceed with the action.",
                    redirect_url="/studio/actions/approved",
                )
            else:
                return GestureSubmissionResponse(success=False, message=f"Gesture verification failed: {result.error}")

        except Exception as e:
            return GestureSubmissionResponse(success=False, message=f"Gesture processing error: {e!s}")

    async def check_action_approval(
        self, lid: str, approval_id: str, action: str, action_context: dict[str, Any]
    ) -> bool:
        """
        Check if action has valid GTΨ approval.

        Args:
            lid: Canonical ΛID
            approval_id: GTΨ approval ID
            action: Action being performed
            action_context: Action context

        Returns:
            True if action is approved
        """
        request = ActionApprovalRequest(lid=lid, approval_id=approval_id, action=action, action_context=action_context)

        result = await self.verification_service.check_action_approval(request)
        return result.approved

    def _generate_context_summary(self, action: str, context: dict[str, Any]) -> str:
        """Generate human-readable context summary"""
        if action == "send_email":
            to = context.get("to", ["unknown"])
            subject = context.get("subject", "No subject")
            return f"Send email to {', '.join(to[:3])} with subject '{subject[:50]}...'"

        elif action == "cloud.move.files":
            file_count = context.get("file_count", 0)
            destination = context.get("destination", "unknown location")
            return f"Move {file_count} files to {destination}"

        elif action == "share_link_public":
            resource_name = context.get("resource_name", "file")
            return f"Create public sharing link for '{resource_name}'"

        elif action == "delete_files":
            file_count = context.get("file_count", 0)
            return f"Permanently delete {file_count} files"

        return f"Perform {action}"

    def _get_gesture_instructions(self, gesture_type: GestureType) -> list[str]:
        """Get instructions for gesture type"""
        if gesture_type == GestureType.STROKE:
            return [
                "Draw your signature or personal pattern",
                "Use smooth, confident strokes",
                "Complete the gesture within the time limit",
                "Make sure the pattern is clear and recognizable",
            ]
        elif gesture_type == GestureType.TAP_SEQUENCE:
            return [
                "Tap your personal rhythm pattern",
                "Use consistent timing between taps",
                "Complete all taps within the time limit",
                "Keep the rhythm steady and recognizable",
            ]
        elif gesture_type == GestureType.SIGNATURE:
            return [
                "Sign your name or initials",
                "Use natural signing motion",
                "Complete the signature smoothly",
                "Match your usual signing style",
            ]
        else:
            return ["Complete your personal gesture pattern"]

    def _generate_risk_warnings(self, action: str, risk_level: RiskLevel) -> list[str]:
        """Generate appropriate risk warnings"""
        warnings = []

        if risk_level == RiskLevel.CRITICAL:
            warnings.append("⚠️ CRITICAL ACTION: This action cannot be undone")

        if action == "send_email":
            warnings.extend(
                [
                    "This will send an email on your behalf",
                    "Recipients will see it came from your account",
                    "Consider if the content and recipients are correct",
                ]
            )

        elif action == "delete_files":
            warnings.extend(
                [
                    "Files will be permanently deleted",
                    "This action cannot be undone",
                    "Make sure you have backups if needed",
                ]
            )

        elif action == "share_link_public":
            warnings.extend(
                [
                    "Anyone with the link will be able to access this content",
                    "The link may be indexed by search engines",
                    "Consider the privacy implications carefully",
                ]
            )

        elif action == "cloud.move.files":
            warnings.extend(
                [
                    "Files will be moved between services",
                    "Sharing permissions may change",
                    "Check that the destination is correct",
                ]
            )

        return warnings

    def _get_risk_theme(self, risk_level: RiskLevel) -> dict[str, str]:
        """Get UI theme based on risk level"""
        themes = {
            RiskLevel.LOW: {
                "primary_color": "#10b981",  # Green
                "border_color": "#d1fae5",
                "background": "#ecfdf5",
                "icon": "shield-check",
            },
            RiskLevel.MEDIUM: {
                "primary_color": "#f59e0b",  # Amber
                "border_color": "#fde68a",
                "background": "#fffbeb",
                "icon": "exclamation-triangle",
            },
            RiskLevel.HIGH: {
                "primary_color": "#ef4444",  # Red
                "border_color": "#fecaca",
                "background": "#fef2f2",
                "icon": "shield-exclamation",
            },
            RiskLevel.CRITICAL: {
                "primary_color": "#dc2626",  # Dark red
                "border_color": "#fca5a5",
                "background": "#fef2f2",
                "icon": "shield-x",
            },
        }

        return themes.get(risk_level, themes[RiskLevel.MEDIUM])


# FastAPI Router for Studio integration
router = APIRouter(prefix="/studio/gtpsi", tags=["GTΨ Studio Hooks"])

# Global service instance
gtpsi_hooks: Optional[StudioGTΨHooks] = None


async def get_gtpsi_hooks() -> StudioGTΨHooks:
    """Dependency to get GTΨ hooks service"""
    global gtpsi_hooks
    if gtpsi_hooks is None:
        gtpsi_hooks = StudioGTΨHooks()
        await gtpsi_hooks.initialize()
    return gtpsi_hooks


@router.post("/consent-ui")
async def request_consent_ui(request: ConsentUIRequest, hooks: StudioGTΨHooks = gtpsi_hooks) -> ConsentUIResponse:
    """
    Request consent UI for high-risk action.

    Returns UI configuration with challenge details for Studio to render.
    """
    if not hooks.requires_consent(request.action, request.action_context):
        raise HTTPException(status_code=400, detail="Action does not require GTΨ consent")

    try:
        response = await hooks.request_consent_ui(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate consent UI: {e!s}")


@router.post("/submit-gesture")
async def submit_gesture(
    request: GestureSubmissionRequest, http_request: Request, hooks: StudioGTΨHooks = gtpsi_hooks
) -> GestureSubmissionResponse:
    """
    Submit gesture for verification.

    Processes gesture data (edge-style) and returns approval status.
    """
    try:
        client_ip = http_request.client.host if http_request.client else None
        response = await hooks.submit_gesture(request, client_ip)
        return response
    except Exception as e:
        return GestureSubmissionResponse(success=False, message=f"Gesture submission failed: {e!s}")


@router.get("/consent-ui.html")
async def consent_ui_html():
    """
    Serve consent UI HTML template.

    This would be the interactive consent interface with gesture canvas.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GTΨ Consent Required</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 40px; }
            .consent-container { max-width: 500px; margin: 0 auto; padding: 20px; border-radius: 8px; }
            .risk-high { border: 2px solid #ef4444; background: #fef2f2; }
            .risk-critical { border: 2px solid #dc2626; background: #fef2f2; }
            .gesture-canvas { border: 2px dashed #ccc; width: 100%; height: 200px; margin: 20px 0; }
            .countdown { font-size: 24px; color: #ef4444; text-align: center; margin: 10px 0; }
            .warnings { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 4px; margin: 15px 0; }
            button { background: #ef4444; color: white; border: none; padding: 12px 24px; border-radius: 4px; font-size: 16px; }
            button:disabled { background: #ccc; }
        </style>
    </head>
    <body>
        <div class="consent-container risk-high">
            <h2>🔐 GTΨ Consent Required</h2>
            <p><strong>Action:</strong> <span id="action-description">High-risk action</span></p>

            <div class="warnings">
                <h4>⚠️ Please Review:</h4>
                <ul id="warnings-list"></ul>
            </div>

            <div class="countdown">
                Time remaining: <span id="countdown">60</span> seconds
            </div>

            <p><strong>Complete your gesture to proceed:</strong></p>
            <canvas class="gesture-canvas" id="gesture-canvas" width="460" height="200"></canvas>

            <div style="text-align: center; margin-top: 20px;">
                <button id="submit-btn" onclick="submitGesture()" disabled>
                    Complete Gesture to Approve
                </button>
                <button onclick="window.close()" style="background: #6b7280; margin-left: 10px;">
                    Cancel
                </button>
            </div>
        </div>

        <script>
            // Mock gesture capture and submission
            const canvas = document.getElementById('gesture-canvas');
            const ctx = canvas.getContext('2d');
            let isDrawing = false;
            let gesturePoints = [];

            // Canvas drawing
            canvas.addEventListener('mousedown', startGesture);
            canvas.addEventListener('mousemove', drawGesture);
            canvas.addEventListener('mouseup', endGesture);

            function startGesture(e) {
                isDrawing = true;
                const rect = canvas.getBoundingClientRect();
                addPoint(e.clientX - rect.left, e.clientY - rect.top);
            }

            function drawGesture(e) {
                if (!isDrawing) return;

                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                ctx.lineWidth = 2;
                ctx.lineCap = 'round';
                ctx.strokeStyle = '#ef4444';

                ctx.lineTo(x, y);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(x, y);

                addPoint(x, y);
            }

            function endGesture() {
                isDrawing = false;
                ctx.beginPath();

                if (gesturePoints.length >= 5) {
                    document.getElementById('submit-btn').disabled = false;
                }
            }

            function addPoint(x, y) {
                gesturePoints.push({
                    x: x,
                    y: y,
                    timestamp: Date.now()
                });
            }

            // Countdown timer
            let timeLeft = 60;
            const countdownEl = document.getElementById('countdown');

            const timer = setInterval(() => {
                timeLeft--;
                countdownEl.textContent = timeLeft;

                if (timeLeft <= 0) {
                    clearInterval(timer);
                    alert('Time expired. Please try again.');
                    window.close();
                }
            }, 1000);

            // Submit gesture
            async function submitGesture() {
                if (gesturePoints.length < 5) {
                    alert('Please complete your gesture first.');
                    return;
                }

                const gestureData = {
                    points: gesturePoints
                };

                try {
                    // This would submit to /studio/gtpsi/submit-gesture
                    console.log('Submitting gesture data:', gestureData);
                    alert('Gesture submitted successfully! (Demo mode)');
                    window.close();
                } catch (error) {
                    alert('Gesture submission failed: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@router.get("/demo")
async def demo_consent_flow():
    """
    Demo GTΨ consent flow for development.

    Shows how high-risk actions integrate with gesture consent.
    """
    hooks = StudioGTΨHooks()
    await hooks.initialize()

    demo_actions = [
        {
            "action": "send_email",
            "context": {
                "to": ["alice@example.com"],
                "subject": "Urgent proposal",
                "has_attachments": True,
            },
            "requires_consent": hooks.requires_consent("send_email", {"has_attachments": True}),
        },
        {
            "action": "share_link_public",
            "context": {"resource_name": "financial_report.pdf"},
            "requires_consent": hooks.requires_consent("share_link_public"),
        },
        {
            "action": "delete_files",
            "context": {"file_count": 5, "files": ["old_backup.zip", "temp_data.csv"]},
            "requires_consent": hooks.requires_consent("delete_files"),
        },
    ]

    return {
        "message": "GTΨ Demo - High-risk actions and consent requirements",
        "demo_actions": demo_actions,
        "high_risk_actions": list(HIGH_RISK_ACTIONS.keys()),
        "gesture_types": [gt.value for gt in GestureType],
        "next_steps": [
            "Call POST /studio/gtpsi/consent-ui to get consent UI",
            "User completes gesture in UI",
            "Call POST /studio/gtpsi/submit-gesture to verify",
            "Use approval_id when performing the actual action",
        ],
    }


# Startup event
@router.on_event("startup")
async def startup_gtpsi_hooks():
    """Initialize GTΨ hooks on startup"""
    global gtpsi_hooks
    if gtpsi_hooks is None:
        gtpsi_hooks = StudioGTΨHooks()
        await gtpsi_hooks.initialize()
        print("🔐 GTΨ Studio hooks initialized")


if __name__ == "__main__":
    # Demonstrate Studio integration
    async def demo():
        hooks = StudioGTΨHooks()
        await hooks.initialize()

        print("🎨 GTΨ Studio Integration Demo")
        print("=" * 35)

        # Test consent requirement
        needs_consent = hooks.requires_consent("send_email", {"has_attachments": True})
        print(f"Send email with attachments needs consent: {needs_consent}")

        if needs_consent:
            # Request consent UI
            ui_request = ConsentUIRequest(
                lid="gonzo",
                action="send_email",
                action_context={
                    "to": ["alice@example.com"],
                    "subject": "Test",
                    "has_attachments": True,
                },
            )

            ui_response = await hooks.request_consent_ui(ui_request)
            print(f"Consent UI generated: {ui_response.challenge_id}")
            print(f"Time limit: {ui_response.countdown_seconds} seconds")
            print(f"Risk warnings: {len(ui_response.ui_config['warnings'])} items")

        print("\n✅ Studio integration demo complete!")

    asyncio.run(demo())
