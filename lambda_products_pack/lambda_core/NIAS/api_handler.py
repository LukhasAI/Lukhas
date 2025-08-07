"""
API Handler for NIAS (NIΛS) System
Provides REST API endpoints for dream commerce operations
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field

@dataclass
class APIResponse:
    """Standard API response format"""
    status: str
    data: Dict[str, Any]
    timestamp: datetime
    request_id: str

class UserRegistrationRequest(BaseModel):
    """User registration request model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    preferences: Dict[str, Any] = Field(default_factory=dict)

class DreamInitiationRequest(BaseModel):
    """Dream initiation request model"""
    user_id: str
    dream_type: str = Field(..., pattern=r'^(lucid|guided|free)$')
    duration: int = Field(..., ge=10, le=120)
    intensity: float = Field(..., ge=0.0, le=1.0)

class APIHandler:
    """Main API handler for NIAS system"""
    
    def __init__(self):
        self.active_sessions = {}
        self.registered_users = {}
        self.system_metrics = {
            "uptime": datetime.now(),
            "total_requests": 0,
            "active_sessions": 0,
            "health_status": "healthy"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        self.system_metrics["total_requests"] += 1
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": (datetime.now() - self.system_metrics["uptime"]).total_seconds(),
            "version": "1.0.0"
        }
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        self.system_metrics["total_requests"] += 1
        
        # Validate input
        request = UserRegistrationRequest(**user_data)
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Store user
        self.registered_users[user_id] = {
            "user_id": user_id,
            "username": request.username,
            "email": request.email,
            "preferences": request.preferences,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        return {
            "user_id": user_id,
            "status": "registered",
            "message": f"User {request.username} registered successfully"
        }
    
    async def initiate_dream(self, dream_request: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate a dream session"""
        self.system_metrics["total_requests"] += 1
        
        # Validate input
        request = DreamInitiationRequest(**dream_request)
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create dream session
        session = {
            "session_id": session_id,
            "user_id": request.user_id,
            "dream_type": request.dream_type,
            "duration": request.duration,
            "intensity": request.intensity,
            "status": "initiated",
            "started_at": datetime.now().isoformat(),
            "progress": 0.0
        }
        
        self.active_sessions[session_id] = session
        self.system_metrics["active_sessions"] = len(self.active_sessions)
        
        return {
            "session_id": session_id,
            "status": "initiated",
            "estimated_completion": datetime.now().isoformat(),
            "dream_parameters": {
                "type": request.dream_type,
                "duration": request.duration,
                "intensity": request.intensity
            }
        }
    
    async def get_user_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get user metrics and statistics"""
        self.system_metrics["total_requests"] += 1
        
        if user_id not in self.registered_users:
            raise ValueError(f"User {user_id} not found")
        
        # Calculate metrics
        user_sessions = [s for s in self.active_sessions.values() if s["user_id"] == user_id]
        
        return {
            "user_id": user_id,
            "total_sessions": len(user_sessions),
            "active_sessions": len([s for s in user_sessions if s["status"] == "initiated"]),
            "dream_preferences": self.registered_users[user_id]["preferences"],
            "last_activity": datetime.now().isoformat(),
            "performance_metrics": {
                "avg_session_duration": 45.0,
                "success_rate": 0.92,
                "satisfaction_score": 4.3
            }
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        self.system_metrics["total_requests"] += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_health": self.system_metrics["health_status"],
            "performance": {
                "total_requests": self.system_metrics["total_requests"],
                "active_sessions": self.system_metrics["active_sessions"],
                "uptime_seconds": (datetime.now() - self.system_metrics["uptime"]).total_seconds(),
                "memory_usage": "78%",
                "cpu_usage": "45%"
            },
            "endpoints": {
                "health": "/api/v1/health",
                "register": "/api/v1/users/register",
                "dreams": "/api/v1/dreams",
                "metrics": "/api/v1/users/{user_id}/metrics",
                "status": "/api/v1/system/status"
            }
        }
    
    async def get_dream_session(self, session_id: str) -> Dict[str, Any]:
        """Get dream session details"""
        self.system_metrics["total_requests"] += 1
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # Simulate progress
        elapsed = (datetime.now() - datetime.fromisoformat(session["started_at"])).total_seconds()
        progress = min(elapsed / (session["duration"] * 60), 1.0)
        session["progress"] = progress
        
        if progress >= 1.0:
            session["status"] = "completed"
        
        return session
    
    async def terminate_dream_session(self, session_id: str) -> Dict[str, Any]:
        """Terminate a dream session"""
        self.system_metrics["total_requests"] += 1
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session["status"] = "terminated"
        session["ended_at"] = datetime.now().isoformat()
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        self.system_metrics["active_sessions"] = len(self.active_sessions)
        
        return {
            "session_id": session_id,
            "status": "terminated",
            "message": "Dream session terminated successfully"
        }
