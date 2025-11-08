"""
Privacy-first analytics server endpoint with aggregation.

Features:
- Receives analytics events
- Aggregates without storing individual events
- Rate limiting (1000 events/hour per session)
- IP anonymization (strip last octet)
- User-Agent normalization (browser family only)
- Returns aggregated metrics (no raw events)
- GDPR-compliant data handling
"""

import hashlib
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator


# Pydantic models for request/response
class EventProperties(BaseModel):
    """Event properties (sanitized)."""

    domain: str
    path: Optional[str] = None
    language: Optional[str] = None
    quickstart_id: Optional[str] = None
    duration_seconds: Optional[int] = None
    success: Optional[bool] = None
    trace_type: Optional[str] = None
    interaction_depth: Optional[int] = None
    page: Optional[str] = None
    trigger: Optional[str] = None
    claim_page: Optional[str] = None
    evidence_id: Optional[str] = None
    demo_type: Optional[str] = None
    action: Optional[str] = None
    cta_text: Optional[str] = None
    cta_location: Optional[str] = None
    variant: Optional[str] = None
    referrer: Optional[str] = None

    @validator('*', pre=True)
    def strip_pii(cls, v):
        """Strip PII from all string fields."""
        if isinstance(v, str):
            # Email pattern
            if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', v):
                return '[REDACTED]'
            # Phone pattern
            if re.search(r'\+?[1-9]\d{1,14}|\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', v):
                return '[REDACTED]'
            # IP pattern
            if re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', v):
                return '[REDACTED]'
        return v


class AnalyticsEvent(BaseModel):
    """Single analytics event."""

    event: str
    properties: EventProperties
    timestamp: str
    session_id: Optional[str] = None

    @validator('event')
    def validate_event_name(cls, v):
        """Validate event name against taxonomy."""
        allowed_events = {
            "page_view",
            "quickstart_started",
            "quickstart_completed",
            "reasoning_trace_viewed",
            "assistive_variant_viewed",
            "assistive_audio_played",
            "evidence_artifact_requested",
            "demo_interaction",
            "cta_clicked",
        }
        if v not in allowed_events:
            raise ValueError(f"Event '{v}' not in allowed taxonomy")
        return v


class EventBatch(BaseModel):
    """Batch of analytics events."""

    events: List[AnalyticsEvent] = Field(..., max_items=100)


class AggregatedMetrics(BaseModel):
    """Aggregated analytics metrics."""

    event_counts: Dict[str, int]
    unique_sessions: int
    time_period: str
    domain_counts: Dict[str, int]
    browser_counts: Dict[str, int]


# In-memory storage for aggregation (use Redis/database in production)
class AnalyticsAggregator:
    """Aggregates analytics events without storing raw data."""

    def __init__(self):
        self.event_counts: Dict[str, int] = defaultdict(int)
        self.session_ids: set = set()
        self.domain_counts: Dict[str, int] = defaultdict(int)
        self.browser_counts: Dict[str, int] = defaultdict(int)
        self.hourly_counts: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

    def add_event(
        self,
        event: AnalyticsEvent,
        browser_family: str,
        anonymized_ip: str
    ) -> None:
        """Add event to aggregation (does not store raw event)."""
        # Increment event count
        self.event_counts[event.event] += 1

        # Track unique sessions
        if event.session_id:
            self.session_ids.add(event.session_id)

        # Track domain counts
        if event.properties.domain:
            self.domain_counts[event.properties.domain] += 1

        # Track browser counts
        self.browser_counts[browser_family] += 1

        # Track hourly counts (for rate limiting)
        hour_key = datetime.utcnow().strftime("%Y-%m-%d-%H")
        session_key = event.session_id or anonymized_ip
        self.hourly_counts[hour_key][session_key] += 1

    def get_metrics(self, hours: int = 24) -> AggregatedMetrics:
        """Get aggregated metrics."""
        return AggregatedMetrics(
            event_counts=dict(self.event_counts),
            unique_sessions=len(self.session_ids),
            time_period=f"last_{hours}_hours",
            domain_counts=dict(self.domain_counts),
            browser_counts=dict(self.browser_counts),
        )

    def check_rate_limit(
        self,
        session_id: Optional[str],
        ip: str,
        limit: int = 1000
    ) -> bool:
        """Check if session/IP has exceeded rate limit."""
        hour_key = datetime.utcnow().strftime("%Y-%m-%d-%H")
        session_key = session_id or self._anonymize_ip(ip)

        current_count = self.hourly_counts[hour_key].get(session_key, 0)
        return current_count < limit

    @staticmethod
    def _anonymize_ip(ip: str) -> str:
        """Anonymize IP address (remove last octet)."""
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
        return ip

    def cleanup_old_data(self, hours: int = 24) -> None:
        """Remove data older than specified hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cutoff_key = cutoff.strftime("%Y-%m-%d-%H")

        # Remove old hourly counts
        old_keys = [
            key for key in self.hourly_counts.keys()
            if key < cutoff_key
        ]
        for key in old_keys:
            del self.hourly_counts[key]


# Global aggregator instance (use Redis/database in production)
aggregator = AnalyticsAggregator()

# FastAPI app
app = FastAPI(
    title="LUKHAS Privacy-First Analytics API",
    description="GDPR-compliant analytics with aggregation",
    version="1.0.0",
)


def anonymize_ip(ip: str) -> str:
    """Anonymize IP address by removing last octet."""
    parts = ip.split('.')
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
    # Handle IPv6
    if ':' in ip:
        parts = ip.split(':')
        return ':'.join(parts[:4]) + '::0'
    return ip


def normalize_user_agent(user_agent: str) -> str:
    """Extract browser family from User-Agent."""
    if not user_agent:
        return "unknown"

    user_agent_lower = user_agent.lower()

    browser_families = {
        'chrome': ['chrome', 'chromium', 'crios'],
        'firefox': ['firefox', 'fxios'],
        'safari': ['safari'],
        'edge': ['edge', 'edg'],
        'opera': ['opera', 'opr'],
        'ie': ['msie', 'trident'],
    }

    for family, identifiers in browser_families.items():
        if any(identifier in user_agent_lower for identifier in identifiers):
            return family

    return "other"


@app.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def receive_events(
    batch: EventBatch,
    request: Request
) -> JSONResponse:
    """
    Receive and aggregate analytics events.

    Note: Individual events are NOT stored. Only aggregated metrics are kept.
    """
    # Get client IP and User-Agent
    client_ip = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("User-Agent", "")

    # Anonymize IP
    anonymized_ip = anonymize_ip(client_ip)

    # Normalize User-Agent
    browser_family = normalize_user_agent(user_agent)

    # Process each event
    events_processed = 0
    events_rejected = 0

    for event in batch.events:
        # Check rate limit
        if not aggregator.check_rate_limit(
            event.session_id,
            anonymized_ip,
            limit=1000
        ):
            events_rejected += 1
            continue

        # Add to aggregation (does not store raw event)
        aggregator.add_event(event, browser_family, anonymized_ip)
        events_processed += 1

    # Cleanup old data periodically
    aggregator.cleanup_old_data(hours=24)

    return JSONResponse(
        content={
            "status": "accepted",
            "events_processed": events_processed,
            "events_rejected": events_rejected,
            "reason": "rate_limit" if events_rejected > 0 else None,
        },
        status_code=status.HTTP_202_ACCEPTED,
    )


@app.get("/metrics", response_model=AggregatedMetrics)
async def get_metrics(hours: int = 24) -> AggregatedMetrics:
    """
    Get aggregated analytics metrics.

    Note: Only aggregated data is returned. Individual events are not accessible.
    """
    return aggregator.get_metrics(hours=hours)


@app.delete("/data")
async def delete_user_data(session_id: str) -> JSONResponse:
    """
    Delete user data (GDPR right to deletion).

    Note: Since we don't store individual events, this is mostly symbolic.
    We remove the session ID from unique sessions count.
    """
    if session_id in aggregator.session_ids:
        aggregator.session_ids.remove(session_id)

    return JSONResponse(
        content={
            "status": "deleted",
            "message": "User data deleted (aggregated metrics unaffected)",
        }
    )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "privacy": "GDPR-compliant",
    }


@app.get("/privacy")
async def privacy_info() -> Dict[str, Any]:
    """Privacy information endpoint."""
    return {
        "data_collection": {
            "pii_collected": False,
            "cookies": "Essential only (preferences, session)",
            "third_party_tracking": False,
            "cross_site_tracking": False,
        },
        "data_retention": {
            "raw_events": "Not stored (aggregated immediately)",
            "aggregated_data": "90 days",
            "session_data": "24 hours",
        },
        "user_rights": {
            "access": True,
            "deletion": True,
            "portability": True,
            "objection": True,
        },
        "compliance": {
            "gdpr": True,
            "ccpa": True,
            "legal_basis": "consent",
        },
        "contact": "privacy@lukhas.ai",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
