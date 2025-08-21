"""
Data Models for Health Advisor Plugin

Defines the data models used for storing health records and related information
with HIPAA compliance in mind.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
import uuid

@dataclass
class HealthRecord:
    """Represents a health record with versioning support"""
    record_id: str
    user_id: str
    record_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    version: int = 1
    previous_version_id: Optional[str] = None

    def to_json(self) -> str:
        """Convert record to JSON string"""
        return json.dumps({
            "record_id": self.record_id,
            "user_id": self.user_id,
            "record_type": self.record_type,
            "data": self.data,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "version": self.version,
            "previous_version_id": self.previous_version_id
        })

    @classmethod
    def from_json(cls, json_str: str) -> 'HealthRecord':
        """Create record from JSON string"""
        data = json.loads(json_str)
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)

    def create_new_version(self, updates: Dict[str, Any]) -> 'HealthRecord':
        """Create a new version of the record with updates"""
        return HealthRecord(
            record_id=str(uuid.uuid4()),
            user_id=self.user_id,
            record_type=self.record_type,
            data={**self.data, **updates},
            metadata=self.metadata,
            created_at=datetime.utcnow(),
            version=self.version + 1,
            previous_version_id=self.record_id
        )

@dataclass
class DiagnosticSession:
    """Represents a diagnostic session"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "active"
    symptoms: List[Dict[str, Any]] = None
    diagnoses: List[Dict[str, Any]] = None
    recommendations: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None

    def to_json(self) -> str:
        """Convert session to JSON string"""
        return json.dumps({
            "session_id": self.session_id,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "symptoms": self.symptoms or [],
            "diagnoses": self.diagnoses or [],
            "recommendations": self.recommendations or [],
            "metadata": self.metadata or {}
        })

    @classmethod
    def from_json(cls, json_str: str) -> 'DiagnosticSession':
        """Create session from JSON string"""
        data = json.loads(json_str)
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data['end_time']:
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        return cls(**data)

@dataclass
class UserData:
    """Represents user-specific data and preferences"""
    user_id: str
    created_at: datetime
    preferences: Dict[str, Any]
    medical_history: List[Dict[str, Any]]
    active_conditions: List[Dict[str, Any]]
    medications: List[Dict[str, Any]]
    allergies: List[Dict[str, Any]]
    metadata: Dict[str, Any]

    def to_json(self) -> str:
        """Convert user data to JSON string"""
        return json.dumps({
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "preferences": self.preferences,
            "medical_history": self.medical_history,
            "active_conditions": self.active_conditions,
            "medications": self.medications,
            "allergies": self.allergies,
            "metadata": self.metadata
        })

    @classmethod
    def from_json(cls, json_str: str) -> 'UserData':
        """Create user data from JSON string"""
        data = json.loads(json_str)
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)
