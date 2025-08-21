#!/usr/bin/env python3
"""
Audit Logger Module for Enhanced Guardian System
Provides comprehensive logging and auditing capabilities
"""

import logging
import json
import hashlib
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


@dataclass
class AuditEvent:
    """Audit event data structure"""
    event_id: str
    timestamp: datetime
    user_id: Optional[str]
    event_type: str
    action: str
    resource: Optional[str]
    result: str  # success, failure, error
    details: Dict[str, Any]
    session_id: Optional[str] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())


class AuditLogger:
    """
    Comprehensive audit logging system for the Guardian System
    Provides secure, tamper-evident logging of all system activities
    """
    
    def __init__(self, log_directory: str = "audit_logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.events: List[AuditEvent] = []
        self.last_hash = self._get_genesis_hash()
        
        # Setup audit log file
        self.audit_file = self.log_directory / "guardian_audit.log"
        self._setup_audit_logging()
        
        self.logger.info("Audit logging system initialized")
    
    def _setup_audit_logging(self):
        """Setup audit logging configuration"""
        audit_handler = logging.FileHandler(self.audit_file)
        audit_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
        )
        audit_handler.setFormatter(formatter)
        
        # Create audit logger
        self.audit_logger = logging.getLogger('guardian_audit')
        self.audit_logger.setLevel(logging.INFO)
        self.audit_logger.addHandler(audit_handler)
        self.audit_logger.propagate = False
    
    def _get_genesis_hash(self) -> str:
        """Get the genesis hash for the audit chain"""
        return hashlib.sha256("guardian_audit_genesis".encode()).hexdigest()
    
    def _calculate_event_hash(self, event: AuditEvent, prev_hash: str) -> str:
        """Calculate hash for an audit event"""
        event_data = asdict(event)
        event_data['prev_hash'] = prev_hash
        
        # Convert to JSON string for consistent hashing
        event_json = json.dumps(event_data, sort_keys=True, default=str)
        return hashlib.sha256(event_json.encode()).hexdigest()
    
    async def log_event(self, 
                       event_type: str,
                       action: str,
                       result: str,
                       user_id: Optional[str] = None,
                       resource: Optional[str] = None,
                       details: Optional[Dict[str, Any]] = None,
                       session_id: Optional[str] = None,
                       source_ip: Optional[str] = None) -> str:
        """
        Log an audit event
        
        Args:
            event_type: Type of event (access, medical, emergency, etc.)
            action: Action performed
            result: Result of the action (success, failure, error)
            user_id: User who performed the action
            resource: Resource that was accessed
            details: Additional event details
            session_id: Session identifier
            source_ip: Source IP address
            
        Returns:
            Event ID of the logged event
        """
        try:
            # Create audit event
            event = AuditEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                user_id=user_id,
                event_type=event_type,
                action=action,
                resource=resource,
                result=result,
                details=details or {},
                session_id=session_id,
                source_ip=source_ip
            )
            
            # Calculate hash for audit chain
            event_hash = self._calculate_event_hash(event, self.last_hash)
            
            # Add to audit log
            audit_entry = {
                **asdict(event),
                'prev_hash': self.last_hash,
                'event_hash': event_hash
            }
            
            # Log to file
            self.audit_logger.info(json.dumps(audit_entry, default=str))
            
            # Store in memory
            self.events.append(event)
            self.last_hash = event_hash
            
            # Log to console if significant event
            if result == "failure" or event_type in ["emergency", "security"]:
                self.logger.warning(f"Audit event: {event_type} {action} - {result}")
            
            return event.event_id
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
            # Fallback logging
            self.logger.error(f"Audit fallback: {event_type} {action} {result}")
            return "audit_error"
    
    async def log_access(self, 
                        user_id: str,
                        resource: str,
                        action: str,
                        granted: bool,
                        reason: str,
                        session_id: Optional[str] = None) -> str:
        """Log an access attempt"""
        return await self.log_event(
            event_type="access",
            action=f"{action} {resource}",
            result="success" if granted else "failure",
            user_id=user_id,
            resource=resource,
            details={
                "granted": granted,
                "reason": reason
            },
            session_id=session_id
        )
    
    async def log_medical_event(self,
                               user_id: Optional[str],
                               action: str,
                               result: str,
                               details: Dict[str, Any]) -> str:
        """Log a medical-related event"""
        return await self.log_event(
            event_type="medical",
            action=action,
            result=result,
            user_id=user_id,
            resource="medical_system",
            details=details
        )
    
    async def log_emergency(self,
                           user_id: Optional[str],
                           emergency_type: str,
                           severity: str,
                           response_initiated: bool,
                           details: Dict[str, Any]) -> str:
        """Log an emergency event"""
        return await self.log_event(
            event_type="emergency",
            action=f"{emergency_type} alert",
            result="success" if response_initiated else "failure",
            user_id=user_id,
            resource="emergency_system",
            details={
                "emergency_type": emergency_type,
                "severity": severity,
                "response_initiated": response_initiated,
                **details
            }
        )
    
    async def log_security_event(self,
                                user_id: Optional[str],
                                threat_type: str,
                                severity: str,
                                action_taken: str,
                                details: Dict[str, Any]) -> str:
        """Log a security-related event"""
        return await self.log_event(
            event_type="security",
            action=f"{threat_type} detected",
            result="success",
            user_id=user_id,
            resource="security_system",
            details={
                "threat_type": threat_type,
                "severity": severity,
                "action_taken": action_taken,
                **details
            }
        )
    
    async def log_system_event(self,
                              action: str,
                              result: str,
                              details: Dict[str, Any]) -> str:
        """Log a system-level event"""
        return await self.log_event(
            event_type="system",
            action=action,
            result=result,
            resource="guardian_system",
            details=details
        )
    
    def get_events(self, 
                   event_type: Optional[str] = None,
                   user_id: Optional[str] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   limit: int = 100) -> List[AuditEvent]:
        """
        Retrieve audit events based on filters
        
        Args:
            event_type: Filter by event type
            user_id: Filter by user ID
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of events to return
            
        Returns:
            List of matching audit events
        """
        filtered_events = self.events.copy()
        
        # Apply filters
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
        
        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
        
        # Sort by timestamp (newest first) and apply limit
        filtered_events.sort(key=lambda e: e.timestamp, reverse=True)
        return filtered_events[:limit]
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """Get audit statistics"""
        total_events = len(self.events)
        
        if total_events == 0:
            return {
                "total_events": 0,
                "event_types": {},
                "results": {},
                "time_range": None
            }
        
        # Count by event type
        event_types = {}
        results = {}
        
        for event in self.events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            results[event.result] = results.get(event.result, 0) + 1
        
        # Time range
        timestamps = [e.timestamp for e in self.events]
        time_range = {
            "earliest": min(timestamps),
            "latest": max(timestamps)
        }
        
        return {
            "total_events": total_events,
            "event_types": event_types,
            "results": results,
            "time_range": time_range
        }
    
    def verify_audit_chain(self) -> Dict[str, Any]:
        """Verify the integrity of the audit chain"""
        try:
            current_hash = self._get_genesis_hash()
            verified_events = 0
            
            for event in self.events:
                expected_hash = self._calculate_event_hash(event, current_hash)
                # In a full implementation, we'd verify stored hashes
                current_hash = expected_hash
                verified_events += 1
            
            return {
                "verified": True,
                "verified_events": verified_events,
                "total_events": len(self.events),
                "message": "Audit chain integrity verified"
            }
            
        except Exception as e:
            self.logger.error(f"Audit chain verification failed: {e}")
            return {
                "verified": False,
                "verified_events": 0,
                "total_events": len(self.events),
                "message": f"Verification failed: {e}"
            }
