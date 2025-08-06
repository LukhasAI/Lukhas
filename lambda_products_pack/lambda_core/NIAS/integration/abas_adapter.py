"""
ABAS Integration Adapter for NIΛS
Integrates Lambda Boundary Attention System with NIAS message processing
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta

# Add ABAS to the path
abas_path = Path(__file__).parent.parent.parent / "ΛBAS"
sys.path.insert(0, str(abas_path))

try:
    from abas_core import ΛBAS, AttentionState, AttentionRequest, AttentionMetrics
    ABAS_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("ΛBAS integration available")
except ImportError as e:
    ABAS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"ΛBAS not available: {e}")
    
    # Mock classes for fallback
    class AttentionState:
        AVAILABLE = "available"
        FOCUSED = "focused"
        FLOW_STATE = "flow_state"
        OVERLOADED = "overloaded"
        RECOVERING = "recovering"
        INTERRUPTED = "interrupted"
        OFFLINE = "offline"
    
    class AttentionRequest:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    class AttentionMetrics:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


class NIASABASAdapter:
    """
    Adapter that integrates ΛBAS attention system with NIΛS message processing.
    
    This adapter:
    - Translates NIΛS message requests into ΛBAS attention requests
    - Maps ΛBAS attention states to NIΛS emotional states
    - Handles attention boundary enforcement for message delivery
    - Provides fallback behavior when ΛBAS is unavailable
    """
    
    def __init__(self):
        self.abas_available = ABAS_AVAILABLE
        self.abas_instance = None
        
        if self.abas_available:
            try:
                self.abas_instance = ΛBAS()
                logger.info("ΛBAS instance initialized for NIΛS integration")
            except Exception as e:
                logger.error(f"Failed to initialize ΛBAS: {e}")
                self.abas_available = False
                self.abas_instance = None
        
        # State mapping between ABAS and NIAS
        self.attention_to_emotional_mapping = self._initialize_state_mapping()
        
        # Message type to cognitive cost mapping
        self.cognitive_cost_mapping = self._initialize_cognitive_costs()
        
        # Registered users for ABAS
        self.registered_users = set()
        
        logger.info(f"NIΛS-ΛBAS adapter initialized (ABAS available: {self.abas_available})")
    
    def _initialize_state_mapping(self) -> Dict[str, str]:
        """Map ABAS attention states to NIAS emotional states"""
        return {
            AttentionState.AVAILABLE: "neutral",
            AttentionState.FOCUSED: "focused", 
            AttentionState.FLOW_STATE: "receptive",
            AttentionState.OVERLOADED: "stressed",
            AttentionState.RECOVERING: "relaxed",
            AttentionState.INTERRUPTED: "overwhelmed",
            AttentionState.OFFLINE: "unavailable"
        }
    
    def _initialize_cognitive_costs(self) -> Dict[str, float]:
        """Initialize cognitive cost estimates for different message types"""
        return {
            "notification": 0.2,
            "promotional": 0.4,
            "educational": 0.6,
            "interactive": 0.7,
            "urgent": 0.3,
            "dream_seed": 0.5,
            "widget": 0.4,
            "feedback_request": 0.3
        }
    
    async def register_user(self, user_id: str, initial_metrics: Optional[Dict] = None) -> bool:
        """Register user with ABAS for attention tracking"""
        if not self.abas_available or not self.abas_instance:
            logger.debug(f"ABAS not available, skipping user registration: {user_id}")
            return True  # Fallback: pretend success
        
        try:
            # Register with ABAS
            success = await self.abas_instance.register_user(user_id)
            
            if success:
                self.registered_users.add(user_id)
                
                # Update initial attention metrics if provided
                if initial_metrics:
                    attention_metrics = self._convert_to_attention_metrics(initial_metrics)
                    await self.abas_instance.update_attention_metrics(user_id, attention_metrics)
                
                logger.info(f"User {user_id} registered with ΛBAS")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to register user {user_id} with ΛBAS: {e}")
            return False
    
    async def check_attention_availability(
        self, 
        user_id: str, 
        message: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if user attention is available for message delivery.
        This replaces the mock emotional gating in NIAS Engine.
        
        Returns:
            {
                "approved": bool,
                "attention_state": str,
                "emotional_state": str,  # Mapped for NIAS compatibility
                "defer_until": Optional[str],
                "reason": str,
                "confidence": float,
                "lambda_trace": str
            }
        """
        
        # Fallback behavior if ABAS not available
        if not self.abas_available or not self.abas_instance:
            return self._fallback_attention_check(user_id, message, user_context)
        
        try:
            # Ensure user is registered
            if user_id not in self.registered_users:
                await self.register_user(user_id)
            
            # Create ABAS attention request
            attention_request = self._create_attention_request(message, user_context)
            
            # Get ABAS decision
            decision = await self.abas_instance.request_attention(user_id, attention_request)
            
            # Get current attention state for mapping
            attention_status = await self.abas_instance.get_attention_status(user_id)
            attention_state = attention_status.get("attention_state", "available")
            
            # Map to emotional state for NIAS compatibility
            emotional_state = self.attention_to_emotional_mapping.get(
                attention_state, "neutral"
            )
            
            # Format response for NIAS
            response = {
                "approved": decision.decision == "allow",
                "attention_state": attention_state,
                "emotional_state": emotional_state,
                "defer_until": decision.defer_until.isoformat() if decision.defer_until else None,
                "reason": " ".join(decision.reasoning),
                "confidence": decision.confidence,
                "lambda_trace": decision.lambda_trace,
                "abas_decision": decision.decision
            }
            
            logger.debug(f"ΛBAS attention check for {user_id}: {decision.decision} ({emotional_state})")
            return response
            
        except Exception as e:
            logger.error(f"ΛBAS attention check failed for {user_id}: {e}")
            return self._fallback_attention_check(user_id, message, user_context, error=str(e))
    
    def _create_attention_request(
        self, 
        message: Dict[str, Any], 
        user_context: Dict[str, Any]
    ) -> AttentionRequest:
        """Create ABAS attention request from NIAS message"""
        
        # Determine message characteristics
        message_type = message.get("type", "notification")
        urgency = message.get("priority", 1) / 5.0  # Convert 1-5 scale to 0-1
        
        # Estimate cognitive cost
        cognitive_cost = self.cognitive_cost_mapping.get(message_type, 0.4)
        
        # Adjust cognitive cost based on message complexity
        if message.get("dream_seed"):
            cognitive_cost += 0.2
        if message.get("interactive_elements"):
            cognitive_cost += 0.1
        if len(message.get("description", "")) > 200:
            cognitive_cost += 0.1
        
        cognitive_cost = min(1.0, cognitive_cost)  # Cap at 1.0
        
        # Estimate duration
        duration_estimate = self._estimate_duration(message)
        
        # Determine interruptibility
        interruptibility = self._calculate_interruptibility(message, urgency)
        
        # Context tags for ABAS boundary checking
        context_tags = []
        if message.get("brand_targeting"):
            context_tags.append("commercial")
        if message.get("dream_seed"):
            context_tags.append("dream")
        if message.get("feedback_required"):
            context_tags.append("feedback")
        if urgency >= 0.8:
            context_tags.append("urgent")
        
        return AttentionRequest(
            id=message.get("message_id", f"nias_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            source="nias_message_delivery",
            urgency=urgency,
            cognitive_cost=cognitive_cost,
            duration_estimate=duration_estimate,
            interruptibility=interruptibility,
            context_tags=context_tags,
            metadata={
                "message_type": message_type,
                "brand_id": message.get("brand_id"),
                "tier": user_context.get("tier"),
                "has_dream_seed": bool(message.get("dream_seed"))
            }
        )
    
    def _estimate_duration(self, message: Dict[str, Any]) -> float:
        """Estimate time required to process message (in minutes)"""
        base_duration = 1.0  # 1 minute base
        
        # Adjust based on message complexity
        if message.get("interactive_elements"):
            base_duration += 2.0
        if message.get("dream_seed"):
            base_duration += 1.5
        if message.get("feedback_required"):
            base_duration += 1.0
        
        # Adjust based on content length
        description_length = len(message.get("description", ""))
        if description_length > 100:
            base_duration += (description_length - 100) / 200.0  # +0.5 min per 100 chars
        
        return min(10.0, base_duration)  # Cap at 10 minutes
    
    def _calculate_interruptibility(self, message: Dict[str, Any], urgency: float) -> float:
        """Calculate how acceptable it is to interrupt for this message"""
        
        # Base interruptibility inversely related to cognitive cost
        base_interruptibility = 1.0 - self.cognitive_cost_mapping.get(
            message.get("type", "notification"), 0.4
        )
        
        # Urgent messages are more interruptible
        urgency_bonus = urgency * 0.3
        
        # Some message types are inherently less interruptible
        if message.get("dream_seed"):
            base_interruptibility -= 0.2  # Dreams need the right moment
        if message.get("educational"):
            base_interruptibility -= 0.1  # Learning needs focus
        
        return max(0.1, min(1.0, base_interruptibility + urgency_bonus))
    
    def _fallback_attention_check(
        self, 
        user_id: str, 
        message: Dict[str, Any], 
        user_context: Dict[str, Any],
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fallback attention check when ABAS is unavailable"""
        
        # Simple heuristic-based attention check
        current_hour = datetime.now().hour
        recent_interactions = len(user_context.get("recent_interactions", []))
        
        # Determine basic emotional state
        if recent_interactions > 10:
            emotional_state = "overwhelmed"
            approved = False
            reason = "High interaction volume detected"
        elif 9 <= current_hour <= 17:
            emotional_state = "focused" 
            approved = message.get("priority", 1) >= 4  # Only high priority during work hours
            reason = "Work hours - only high priority messages"
        elif 20 <= current_hour <= 22:
            emotional_state = "relaxed"
            approved = True
            reason = "Evening relaxation time - messages welcome"
        else:
            emotional_state = "neutral"
            approved = True
            reason = "Standard availability"
        
        if error:
            reason += f" (ABAS error: {error})"
        
        return {
            "approved": approved,
            "attention_state": "available" if approved else "busy",
            "emotional_state": emotional_state,
            "defer_until": None,
            "reason": reason,
            "confidence": 0.6,  # Lower confidence for fallback
            "lambda_trace": f"FALLBACK_{user_id}_{datetime.now().strftime('%H%M%S')}",
            "abas_decision": "fallback"
        }
    
    def _convert_to_attention_metrics(self, metrics_dict: Dict[str, Any]) -> AttentionMetrics:
        """Convert dictionary metrics to ABAS AttentionMetrics object"""
        if not self.abas_available:
            return None
            
        return AttentionMetrics(
            focus_level=metrics_dict.get("focus_level", 0.5),
            cognitive_load=metrics_dict.get("cognitive_load", 0.5),
            interruption_cost=metrics_dict.get("interruption_cost", 0.0),
            attention_residue=metrics_dict.get("attention_residue", 0.0),
            flow_probability=metrics_dict.get("flow_probability", 0.0),
            recovery_rate=metrics_dict.get("recovery_rate", 1.0),
            multitask_penalty=metrics_dict.get("multitask_penalty", 0.0),
            last_updated=datetime.now()
        )
    
    async def update_user_attention_metrics(
        self, 
        user_id: str, 
        metrics: Dict[str, Any]
    ) -> bool:
        """Update user attention metrics in ABAS"""
        if not self.abas_available or not self.abas_instance:
            return True  # Fallback: pretend success
        
        try:
            attention_metrics = self._convert_to_attention_metrics(metrics)
            success = await self.abas_instance.update_attention_metrics(user_id, attention_metrics)
            
            if success:
                logger.debug(f"Updated attention metrics for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update attention metrics for {user_id}: {e}")
            return False
    
    async def get_attention_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get attention analytics from ABAS"""
        if not self.abas_available or not self.abas_instance:
            return {"error": "ABAS not available"}
        
        try:
            return await self.abas_instance.get_attention_status(user_id)
        except Exception as e:
            logger.error(f"Failed to get attention analytics for {user_id}: {e}")
            return {"error": str(e)}
    
    def is_abas_available(self) -> bool:
        """Check if ABAS integration is available"""
        return self.abas_available and self.abas_instance is not None
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of ABAS integration"""
        status = {
            "abas_available": self.abas_available,
            "registered_users": len(self.registered_users),
            "integration_mode": "full" if self.abas_available else "fallback"
        }
        
        if self.abas_available and self.abas_instance:
            try:
                system_metrics = self.abas_instance.get_system_metrics()
                status["abas_metrics"] = system_metrics
            except Exception as e:
                status["abas_error"] = str(e)
        
        return status


# Global adapter instance
_global_abas_adapter = None

def get_abas_adapter() -> NIASABASAdapter:
    """Get the global ABAS adapter instance"""
    global _global_abas_adapter
    if _global_abas_adapter is None:
        _global_abas_adapter = NIASABASAdapter()
    return _global_abas_adapter