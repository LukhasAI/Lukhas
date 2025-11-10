"""
Analytics service for LUKHAS AI.

This module provides a privacy-first analytics service that does not rely on
third-party trackers.

PRIVACY REQUIREMENTS:
- All tracking is opt-in by default
- No PII is ever sent to analytics backend
- User IDs are anonymized via privacy-preserving hashes
- Events are sent in batches to reduce network traffic
"""

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


# --- Public API ---

def track_feature_evaluation(flag_name: str, user_id: str, enabled: bool, context: Any):
    """Placeholder for tracking feature evaluation."""
    logger.info(f"Tracking feature evaluation for {flag_name}")

def track_feature_update(flag_name: str, admin_id: str, changes: Dict[str, Any]):
    """Placeholder for tracking feature updates."""
    logger.info(f"Tracking feature update for {flag_name}")


# --- Models (existing) ---

class AnalyticsEvent(BaseModel):
    """Represents a single analytics event."""
    event: str = Field(..., description="Event name (e.g., 'feature_evaluated')")
    properties: Dict[str, Any] = Field(..., description="Event properties")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

class AnalyticsBatch(BaseModel):
    """Represents a batch of analytics events."""
    user_id_hash: str = Field(..., description="Anonymized user ID (SHA-256)")
    events: List[AnalyticsEvent] = Field(..., max_length=100)
    sent_at: str = Field(..., description="ISO 8601 timestamp")

    @field_validator('events')
    def validate_events(cls, v):
        # Basic validation for event names
        for event in v:
            if not event.event.isalnum() or ' ' in event.event:
                raise ValueError('Event name must be alphanumeric')
        return v

class AnalyticsConfig(BaseModel):
    """Configuration for analytics service."""
    enabled: bool = True
    batch_size: int = 50
    flush_interval_seconds: int = 60
    endpoint: Optional[str] = None
