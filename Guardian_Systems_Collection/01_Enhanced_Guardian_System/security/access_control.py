#!/usr/bin/env python3
"""
Access Control Module for Enhanced Guardian System
Manages access permissions and user authentication
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class AccessRequest:
    """Access request data structure"""
    user_id: str
    resource: str
    action: str
    context: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AccessPolicy:
    """Access policy definition"""
    policy_id: str
    resource_pattern: str
    allowed_actions: List[str]
    conditions: Dict[str, Any]
    priority: int = 100


class AccessController:
    """
    Manages access control and permissions for the Guardian System
    """
    
    def __init__(self):
        self.policies: Dict[str, AccessPolicy] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize default policies
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default access policies"""
        # Medical access policy
        medical_policy = AccessPolicy(
            policy_id="medical_access",
            resource_pattern="medical/*",
            allowed_actions=["read", "write", "emergency"],
            conditions={"user_type": ["medical_professional", "emergency_responder"]},
            priority=90
        )
        self.policies[medical_policy.policy_id] = medical_policy
        
        # User data access policy
        user_policy = AccessPolicy(
            policy_id="user_data_access",
            resource_pattern="user_data/*",
            allowed_actions=["read"],
            conditions={"owner": True},
            priority=80
        )
        self.policies[user_policy.policy_id] = user_policy
        
        self.logger.info("Initialized default access policies")
    
    async def check_access(self, request: AccessRequest) -> Dict[str, Any]:
        """
        Check if access should be granted for a request
        
        Args:
            request: Access request to evaluate
            
        Returns:
            Dict containing access decision and details
        """
        try:
            # Find applicable policies
            applicable_policies = self._find_applicable_policies(request)
            
            if not applicable_policies:
                return {
                    "granted": False,
                    "reason": "No applicable policies found",
                    "policy_id": None
                }
            
            # Evaluate policies (highest priority first)
            for policy in sorted(applicable_policies, key=lambda p: p.priority):
                if await self._evaluate_policy(policy, request):
                    self.logger.info(f"Access granted for {request.user_id} to {request.resource}")
                    return {
                        "granted": True,
                        "reason": f"Granted by policy {policy.policy_id}",
                        "policy_id": policy.policy_id
                    }
            
            self.logger.warning(f"Access denied for {request.user_id} to {request.resource}")
            return {
                "granted": False,
                "reason": "No policies granted access",
                "policy_id": None
            }
            
        except Exception as e:
            self.logger.error(f"Access check failed: {e}")
            return {
                "granted": False,
                "reason": f"Access check error: {e}",
                "policy_id": None
            }
    
    def _find_applicable_policies(self, request: AccessRequest) -> List[AccessPolicy]:
        """Find policies that apply to the request"""
        applicable = []
        
        for policy in self.policies.values():
            if self._resource_matches_pattern(request.resource, policy.resource_pattern):
                if request.action in policy.allowed_actions:
                    applicable.append(policy)
        
        return applicable
    
    def _resource_matches_pattern(self, resource: str, pattern: str) -> bool:
        """Check if resource matches pattern (simplified pattern matching)"""
        if pattern.endswith("*"):
            return resource.startswith(pattern[:-1])
        return resource == pattern
    
    async def _evaluate_policy(self, policy: AccessPolicy, request: AccessRequest) -> bool:
        """Evaluate if policy conditions are met"""
        try:
            # Check conditions
            for condition_key, condition_value in policy.conditions.items():
                request_value = request.context.get(condition_key)
                
                if isinstance(condition_value, list):
                    if request_value not in condition_value:
                        return False
                elif isinstance(condition_value, bool):
                    if bool(request_value) != condition_value:
                        return False
                else:
                    if request_value != condition_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Policy evaluation failed: {e}")
            return False
    
    async def create_session(self, user_id: str, user_context: Dict[str, Any]) -> str:
        """Create a new user session"""
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "context": user_context,
            "created_at": datetime.now(),
            "last_accessed": datetime.now()
        }
        
        self.logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    async def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate and return session information"""
        session = self.sessions.get(session_id)
        
        if session:
            session["last_accessed"] = datetime.now()
            return session
        
        return None
    
    async def revoke_session(self, session_id: str) -> bool:
        """Revoke a user session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.logger.info(f"Revoked session {session_id}")
            return True
        
        return False
    
    def add_policy(self, policy: AccessPolicy):
        """Add a new access policy"""
        self.policies[policy.policy_id] = policy
        self.logger.info(f"Added access policy: {policy.policy_id}")
    
    def remove_policy(self, policy_id: str) -> bool:
        """Remove an access policy"""
        if policy_id in self.policies:
            del self.policies[policy_id]
            self.logger.info(f"Removed access policy: {policy_id}")
            return True
        
        return False
    
    def get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user permissions"""
        # This would typically query user roles and permissions
        # For now, return a basic structure
        return {
            "user_id": user_id,
            "permissions": ["basic_access"],
            "roles": ["user"],
            "restrictions": []
        }
