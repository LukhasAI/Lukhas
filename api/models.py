"""
API Models for LUKHAS Expansion
===============================
This module defines the Pydantic models for the API expansion.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Generic Models
class StatusResponse(BaseModel):
    """A generic status response."""
    status: str
    message: Optional[str] = None


# Consciousness API Models
class ConsciousnessStatus(BaseModel):
    """The status of the consciousness API."""
    state: str
    awareness_level: float
    active_processes: List[str]


class AwarenessLevel(BaseModel):
    """The awareness level of the consciousness API."""
    level: float = Field(..., ge=0.0, le=1.0)


class SetAwarenessRequest(BaseModel):
    """A request to set the awareness level of the consciousness API."""
    level: float = Field(..., ge=0.0, le=1.0)


class MemoryQueryRequest(BaseModel):
    """A request to query the memory of the consciousness API."""
    query: str


class MemoryQueryResponse(BaseModel):
    """A response to a memory query."""
    results: List[str]


class DreamStateRequest(BaseModel):
    """A request to enter a dream state."""
    topic: str
    duration_minutes: int


class DreamStateResponse(BaseModel):
    """A response to a dream state request."""
    dream_id: str
    status: str
    topic: str


# Identity API Models
class UserIdentity(BaseModel):
    """A user identity."""
    user_id: str
    username: str
    email: str
    created_at: datetime


class CreateUserRequest(BaseModel):
    """A request to create a user."""
    username: str
    email: str
    password: str


class UpdateUserRequest(BaseModel):
    """A request to update a user."""
    username: Optional[str] = None
    email: Optional[str] = None


class AuthRequest(BaseModel):
    """A request to authenticate a user."""
    username: str
    password: str


class AuthToken(BaseModel):
    """An authentication token."""
    access_token: str
    token_type: str


class AuthzRequest(BaseModel):
    """A request to authorize a user."""
    token: str
    resource: str


class AuthzResponse(BaseModel):
    """A response to an authorization request."""
    allowed: bool


class ConsolidateRequest(BaseModel):
    """A request to consolidate two users."""
    primary_user_id: str
    secondary_user_id: str


# Guardian API Models
class SafetyProtocols(BaseModel):
    """A list of safety protocols."""
    protocols: List[str]


class EthicsMonitorData(BaseModel):
    """Data from the ethics monitor."""
    monitoring_status: str
    ethical_concerns: List[str]


class ComplianceCheckRequest(BaseModel):
    """A request to check for compliance."""
    system: str
    level: str


class ComplianceCheckResponse(BaseModel):
    """A response to a compliance check."""
    compliant: bool
    details: str


class AuditTrailRequest(BaseModel):
    """A request for an audit trail."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AuditTrailResponse(BaseModel):
    """A response to an audit trail request."""
    logs: List[str]
