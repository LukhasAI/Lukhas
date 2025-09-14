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
    status: str
    message: Optional[str] = None


# Consciousness API Models
class ConsciousnessStatus(BaseModel):
    state: str
    awareness_level: float
    active_processes: List[str]


class AwarenessLevel(BaseModel):
    level: float = Field(..., ge=0.0, le=1.0)


class SetAwarenessRequest(BaseModel):
    level: float = Field(..., ge=0.0, le=1.0)


class MemoryQueryRequest(BaseModel):
    query: str


class MemoryQueryResponse(BaseModel):
    results: List[str]


class DreamStateRequest(BaseModel):
    topic: str
    duration_minutes: int


class DreamStateResponse(BaseModel):
    dream_id: str
    status: str
    topic: str


# Identity API Models
class UserIdentity(BaseModel):
    user_id: str
    username: str
    email: str
    created_at: datetime


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str


class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthToken(BaseModel):
    access_token: str
    token_type: str


class AuthzRequest(BaseModel):
    token: str
    resource: str


class AuthzResponse(BaseModel):
    allowed: bool


class ConsolidateRequest(BaseModel):
    primary_user_id: str
    secondary_user_id: str


# Guardian API Models
class SafetyProtocols(BaseModel):
    protocols: List[str]


class EthicsMonitorData(BaseModel):
    monitoring_status: str
    ethical_concerns: List[str]


class ComplianceCheckRequest(BaseModel):
    system: str
    level: str


class ComplianceCheckResponse(BaseModel):
    compliant: bool
    details: str


class AuditTrailRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AuditTrailResponse(BaseModel):
    logs: List[str]
