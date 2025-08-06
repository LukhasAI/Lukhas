#!/usr/bin/env python3
"""
NIΛS Emotional Filter - Advanced emotional state analysis and protection
Part of the Lambda Products Suite by LUKHAS AI
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math

from .nias_core import EmotionalState, SymbolicMessage

logger = logging.getLogger("Lambda.NIΛS.EmotionalFilter")

class EmotionalProtectionLevel(Enum):
    """Levels of emotional protection"""
    MINIMAL = "minimal"      # Basic stress protection
    STANDARD = "standard"    # Standard emotional filtering
    ENHANCED = "enhanced"    # Advanced emotional awareness
    GUARDIAN = "guardian"    # Maximum emotional protection

class EmotionalTransition(Enum):
    """Types of emotional transitions"""
    GRADUAL = "gradual"      # Slow emotional change
    SUDDEN = "sudden"        # Rapid emotional shift
    CYCLICAL = "cyclical"    # Recurring emotional pattern
    THERAPEUTIC = "therapeutic"  # Healing-oriented change

@dataclass
class EmotionalVector:
    """Comprehensive emotional state representation"""
    stress: float = 0.0           # 0.0 = calm, 1.0 = extreme stress
    energy: float = 0.5           # 0.0 = exhausted, 1.0 = energetic
    focus: float = 0.5            # 0.0 = scattered, 1.0 = laser focused
    creativity: float = 0.5       # 0.0 = blocked, 1.0 = highly creative
    openness: float = 0.5         # 0.0 = closed off, 1.0 = very open
    stability: float = 0.8        # 0.0 = unstable, 1.0 = very stable
    dream_residue: bool = False   # Post-dream vulnerable state
    attention_capacity: float = 1.0  # Available attention (0.0-1.0)
    emotional_momentum: float = 0.0  # Rate of emotional change
    last_updated: datetime = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()
        
        # Auto-calculate attention capacity based on stress and stability
        self.attention_capacity = max(0.1, (1.0 - self.stress) * self.stability)

@dataclass
class EmotionalProfile:
    """User's emotional profile and preferences"""
    user_id: str
    baseline_vector: EmotionalVector
    protection_level: EmotionalProtectionLevel
    sensitivity_factors: Dict[str, float]  # Sensitivity to different emotional triggers
    preferred_transitions: List[EmotionalTransition]
    blocked_emotional_tones: List[EmotionalState]
    therapeutic_goals: List[str]  # e.g., ["reduce_stress", "increase_creativity"]
    circadian_preferences: Dict[str, Any]  # Time-based emotional preferences

class EmotionalFilter:
    """
    Advanced emotional state analysis and protection for NIΛS
    
    Features:
    - Real-time emotional state monitoring
    - Therapeutic message filtering
    - Circadian rhythm awareness
    - Emotional momentum tracking
    - Adaptive protection thresholds
    - Integration with biometric data
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.user_profiles: Dict[str, EmotionalProfile] = {}
        self.emotional_history: Dict[str, List[Tuple[datetime, EmotionalVector]]] = {}
        self.therapeutic_rules: Dict[str, Dict] = {}
        
        # Load default therapeutic rules
        self._initialize_therapeutic_rules()
        
        logger.info("NIΛS Emotional Filter initialized")
    
    def _default_config(self) -> Dict:
        """Default emotional filter configuration"""
        return {
            "stress_threshold_high": 0.8,
            "stress_threshold_medium": 0.5,
            "dream_residue_protection_minutes": 30,
            "emotional_momentum_sensitivity": 0.1,
            "circadian_awareness": True,
            "biometric_integration": False,
            "therapeutic_mode": True,
            "adaptive_thresholds": True
        }
    
    def _initialize_therapeutic_rules(self):
        """Initialize therapeutic filtering rules"""
        self.therapeutic_rules = {
            "high_stress": {
                "allowed_tones": [EmotionalState.CALM],
                "max_intensity": 0.3,
                "message_types": ["calming", "breathing", "grounding"],
                "blocked_types": ["urgent", "exciting", "overwhelming"]
            },
            "creative_flow": {
                "allowed_tones": [EmotionalState.CREATIVE, EmotionalState.CALM],
                "max_intensity": 0.8,
                "message_types": ["inspirational", "creative", "artistic"],
                "blocked_types": ["analytical", "logical", "disruptive"]
            },
            "focus_mode": {
                "allowed_tones": [EmotionalState.FOCUSED, EmotionalState.CALM],
                "max_intensity": 0.4,
                "message_types": ["supportive", "minimal"],
                "blocked_types": ["distracting", "social", "entertainment"]
            },
            "dream_recovery": {
                "allowed_tones": [EmotionalState.CALM],
                "max_intensity": 0.2,
                "message_types": ["gentle", "grounding"],
                "blocked_types": ["all_except_emergency"]
            }
        }
    
    async def create_user_profile(self, user_id: str, 
                                 baseline_vector: Optional[EmotionalVector] = None,
                                 protection_level: EmotionalProtectionLevel = EmotionalProtectionLevel.STANDARD) -> EmotionalProfile:
        """Create emotional profile for a user"""
        if baseline_vector is None:
            baseline_vector = EmotionalVector()  # Use defaults
        
        profile = EmotionalProfile(
            user_id=user_id,
            baseline_vector=baseline_vector,
            protection_level=protection_level,
            sensitivity_factors={
                "stress": 1.0,
                "energy_depletion": 1.0,
                "focus_disruption": 1.0,
                "creative_blocking": 0.8,
                "emotional_overwhelm": 1.2
            },
            preferred_transitions=[EmotionalTransition.GRADUAL],
            blocked_emotional_tones=[],
            therapeutic_goals=["maintain_balance"],
            circadian_preferences={
                "morning_sensitivity": 0.8,
                "evening_sensitivity": 1.2,
                "night_protection": True
            }
        )
        
        self.user_profiles[user_id] = profile
        self.emotional_history[user_id] = []
        
        logger.info(f"Created emotional profile for user {user_id}")
        return profile
    
    async def update_emotional_state(self, user_id: str, 
                                   emotional_vector: EmotionalVector) -> bool:
        """Update user's current emotional state"""
        if user_id not in self.user_profiles:
            logger.error(f"User profile not found: {user_id}")
            return False
        
        try:
            # Calculate emotional momentum
            if user_id in self.emotional_history and self.emotional_history[user_id]:
                last_timestamp, last_vector = self.emotional_history[user_id][-1]
                time_delta = (datetime.now() - last_timestamp).total_seconds() / 60.0  # minutes
                
                if time_delta > 0:
                    stress_change = emotional_vector.stress - last_vector.stress
                    emotional_vector.emotional_momentum = stress_change / max(1.0, time_delta)
            
            # Store in history
            self.emotional_history[user_id].append((datetime.now(), emotional_vector))
            
            # Keep only recent history (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.emotional_history[user_id] = [
                (timestamp, vector) for timestamp, vector in self.emotional_history[user_id]
                if timestamp > cutoff_time
            ]
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating emotional state: {e}")
            return False
    
    async def filter_message(self, message: SymbolicMessage, user_id: str,
                           current_emotional_state: Optional[EmotionalVector] = None) -> Dict[str, Any]:
        """
        Filter message based on user's emotional state
        
        Args:
            message: The message to filter
            user_id: User identifier
            current_emotional_state: Current emotional state (optional)
            
        Returns:
            Dictionary with filtering results
        """
        if user_id not in self.user_profiles:
            return {
                "approved": False,
                "reason": "User profile not found",
                "action": "block"
            }
        
        profile = self.user_profiles[user_id]
        
        # Use provided state or get most recent
        if current_emotional_state is None:
            if user_id in self.emotional_history and self.emotional_history[user_id]:
                _, current_emotional_state = self.emotional_history[user_id][-1]
            else:
                current_emotional_state = profile.baseline_vector
        
        try:
            # 1. Dream residue protection
            dream_check = await self._check_dream_residue_protection(
                message, current_emotional_state, profile
            )
            if not dream_check["approved"]:
                return dream_check
            
            # 2. Stress level protection
            stress_check = await self._check_stress_protection(
                message, current_emotional_state, profile
            )
            if not stress_check["approved"]:
                return stress_check
            
            # 3. Emotional tone matching
            tone_check = await self._check_emotional_tone_compatibility(
                message, current_emotional_state, profile
            )
            if not tone_check["approved"]:
                return tone_check
            
            # 4. Intensity vs capacity
            intensity_check = await self._check_intensity_capacity(
                message, current_emotional_state, profile
            )
            if not intensity_check["approved"]:
                return intensity_check
            
            # 5. Therapeutic goals alignment
            therapeutic_check = await self._check_therapeutic_alignment(
                message, current_emotional_state, profile
            )
            if not therapeutic_check["approved"]:
                return therapeutic_check
            
            # 6. Circadian considerations
            if self.config["circadian_awareness"]:
                circadian_check = await self._check_circadian_compatibility(
                    message, profile
                )
                if not circadian_check["approved"]:
                    return circadian_check
            
            # All checks passed
            return {
                "approved": True,
                "reason": "Message approved by emotional filter",
                "action": "deliver",
                "delivery_recommendation": await self._get_delivery_recommendation(
                    message, current_emotional_state, profile
                )
            }
            
        except Exception as e:
            logger.error(f"Error in emotional filtering: {e}")
            return {
                "approved": False,
                "reason": f"Filtering error: {str(e)}",
                "action": "block"
            }
    
    async def _check_dream_residue_protection(self, message: SymbolicMessage,
                                            emotional_state: EmotionalVector,
                                            profile: EmotionalProfile) -> Dict[str, Any]:
        """Check dream residue protection"""
        if not emotional_state.dream_residue:
            return {"approved": True}
        
        # Only allow emergency or therapeutic messages during dream residue
        if message.metadata and message.metadata.get("emergency", False):
            return {"approved": True, "reason": "Emergency override during dream residue"}
        
        # Allow gentle, therapeutic messages
        therapeutic_rule = self.therapeutic_rules.get("dream_recovery", {})
        if (message.emotional_tone in therapeutic_rule.get("allowed_tones", []) and
            message.intensity <= therapeutic_rule.get("max_intensity", 0.2)):
            return {"approved": True, "reason": "Therapeutic message approved during dream residue"}
        
        return {
            "approved": False,
            "reason": "Dream residue protection - message deferred",
            "action": "defer",
            "defer_minutes": self.config["dream_residue_protection_minutes"]
        }
    
    async def _check_stress_protection(self, message: SymbolicMessage,
                                     emotional_state: EmotionalVector,
                                     profile: EmotionalProfile) -> Dict[str, Any]:
        """Check stress-based protection"""
        stress_level = emotional_state.stress
        
        if stress_level >= self.config["stress_threshold_high"]:
            # High stress - only calming messages
            if message.emotional_tone != EmotionalState.CALM:
                return {
                    "approved": False,
                    "reason": f"High stress level ({stress_level:.2f}) - only calming messages allowed",
                    "action": "defer",
                    "suggestion": "Transform to calming tone"
                }
            
            # Even calming messages must be gentle
            if message.intensity > 0.3:
                return {
                    "approved": False,
                    "reason": "Message intensity too high for high stress state",
                    "action": "transform",
                    "suggested_intensity": 0.3
                }
        
        elif stress_level >= self.config["stress_threshold_medium"]:
            # Medium stress - reduce intensity
            max_intensity = 0.6
            if message.intensity > max_intensity:
                return {
                    "approved": False,
                    "reason": f"Message intensity too high for stress level ({stress_level:.2f})",
                    "action": "transform",
                    "suggested_intensity": max_intensity
                }
        
        return {"approved": True}
    
    async def _check_emotional_tone_compatibility(self, message: SymbolicMessage,
                                                emotional_state: EmotionalVector,
                                                profile: EmotionalProfile) -> Dict[str, Any]:
        """Check if message emotional tone is compatible with current state"""
        # Check blocked tones for this user
        if message.emotional_tone in profile.blocked_emotional_tones:
            return {
                "approved": False,
                "reason": f"Message tone {message.emotional_tone.value} blocked by user preferences",
                "action": "block"
            }
        
        # Context-specific tone checking
        if emotional_state.focus >= 0.8:  # High focus state
            if message.emotional_tone not in [EmotionalState.FOCUSED, EmotionalState.CALM]:
                return {
                    "approved": False,
                    "reason": "Message tone would disrupt focus state",
                    "action": "defer",
                    "defer_reason": "preserve_focus"
                }
        
        if emotional_state.creativity >= 0.8:  # Creative flow state
            if message.emotional_tone == EmotionalState.STRESSED:
                return {
                    "approved": False,
                    "reason": "Stressful message would disrupt creative flow",
                    "action": "defer",
                    "defer_reason": "preserve_creativity"
                }
        
        return {"approved": True}
    
    async def _check_intensity_capacity(self, message: SymbolicMessage,
                                      emotional_state: EmotionalVector,
                                      profile: EmotionalProfile) -> Dict[str, Any]:
        """Check if message intensity matches attention capacity"""
        attention_capacity = emotional_state.attention_capacity
        message_intensity = message.intensity
        
        # Apply user-specific sensitivity
        sensitivity = profile.sensitivity_factors.get("emotional_overwhelm", 1.0)
        adjusted_capacity = attention_capacity / sensitivity
        
        if message_intensity > adjusted_capacity:
            return {
                "approved": False,
                "reason": f"Message intensity ({message_intensity:.2f}) exceeds attention capacity ({adjusted_capacity:.2f})",
                "action": "transform",
                "suggested_intensity": min(adjusted_capacity * 0.8, message_intensity * 0.7)
            }
        
        return {"approved": True}
    
    async def _check_therapeutic_alignment(self, message: SymbolicMessage,
                                         emotional_state: EmotionalVector,
                                         profile: EmotionalProfile) -> Dict[str, Any]:
        """Check if message aligns with therapeutic goals"""
        if not self.config["therapeutic_mode"]:
            return {"approved": True}
        
        therapeutic_goals = profile.therapeutic_goals
        
        for goal in therapeutic_goals:
            if goal == "reduce_stress" and emotional_state.stress > 0.5:
                if message.emotional_tone in [EmotionalState.STRESSED, EmotionalState.OVERWHELMED]:
                    return {
                        "approved": False,
                        "reason": f"Message conflicts with therapeutic goal: {goal}",
                        "action": "block"
                    }
            
            elif goal == "increase_focus" and emotional_state.focus < 0.5:
                if message.intensity > 0.5:
                    return {
                        "approved": False,
                        "reason": f"High intensity message conflicts with focus improvement goal",
                        "action": "transform",
                        "suggested_intensity": 0.4
                    }
        
        return {"approved": True}
    
    async def _check_circadian_compatibility(self, message: SymbolicMessage,
                                           profile: EmotionalProfile) -> Dict[str, Any]:
        """Check circadian rhythm compatibility"""
        current_hour = datetime.now().hour
        circadian_prefs = profile.circadian_preferences
        
        # Night protection
        if circadian_prefs.get("night_protection", True) and (22 <= current_hour or current_hour <= 6):
            if message.intensity > 0.3:
                return {
                    "approved": False,
                    "reason": "Night protection - high intensity messages blocked",
                    "action": "defer",
                    "defer_until": "morning"
                }
        
        # Morning sensitivity
        if 6 <= current_hour <= 10:
            morning_sensitivity = circadian_prefs.get("morning_sensitivity", 1.0)
            max_intensity = 0.7 * morning_sensitivity
            
            if message.intensity > max_intensity:
                return {
                    "approved": False,
                    "reason": "Morning sensitivity - reducing message intensity",
                    "action": "transform",
                    "suggested_intensity": max_intensity
                }
        
        # Evening sensitivity
        if 18 <= current_hour <= 22:
            evening_sensitivity = circadian_prefs.get("evening_sensitivity", 1.0)
            if evening_sensitivity > 1.0 and message.emotional_tone == EmotionalState.CALM:
                # Evening is a good time for calming messages
                return {"approved": True, "reason": "Evening calm message preferred"}
        
        return {"approved": True}
    
    async def _get_delivery_recommendation(self, message: SymbolicMessage,
                                         emotional_state: EmotionalVector,
                                         profile: EmotionalProfile) -> Dict[str, Any]:
        """Get recommendation for optimal message delivery"""
        recommendations = {
            "timing": "immediate",
            "method": "visual",
            "intensity_adjustment": None,
            "tone_adjustment": None
        }
        
        # Timing recommendations
        if emotional_state.focus >= 0.8:
            recommendations["timing"] = "defer_until_break"
        elif emotional_state.creativity >= 0.8:
            recommendations["timing"] = "gentle_immediate"
        
        # Method recommendations
        if (message.voice_tag and 
            emotional_state.stress < 0.3 and 
            profile.protection_level != EmotionalProtectionLevel.GUARDIAN):
            recommendations["method"] = "voice"
        
        # Intensity adjustments
        optimal_intensity = min(message.intensity, emotional_state.attention_capacity * 0.9)
        if optimal_intensity != message.intensity:
            recommendations["intensity_adjustment"] = optimal_intensity
        
        return recommendations
    
    def get_emotional_insights(self, user_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get emotional insights for a user over specified time period"""
        if user_id not in self.emotional_history:
            return {"error": "No emotional history found"}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_history = [
            (timestamp, vector) for timestamp, vector in self.emotional_history[user_id]
            if timestamp > cutoff_time
        ]
        
        if not recent_history:
            return {"error": "No recent emotional data"}
        
        # Calculate trends
        stress_values = [vector.stress for _, vector in recent_history]
        energy_values = [vector.energy for _, vector in recent_history]
        focus_values = [vector.focus for _, vector in recent_history]
        
        return {
            "user_id": user_id,
            "time_period_hours": hours,
            "data_points": len(recent_history),
            "stress": {
                "current": stress_values[-1],
                "average": sum(stress_values) / len(stress_values),
                "trend": "increasing" if stress_values[-1] > stress_values[0] else "decreasing",
                "peak": max(stress_values),
                "low": min(stress_values)
            },
            "energy": {
                "current": energy_values[-1],
                "average": sum(energy_values) / len(energy_values),
                "trend": "increasing" if energy_values[-1] > energy_values[0] else "decreasing"
            },
            "focus": {
                "current": focus_values[-1],
                "average": sum(focus_values) / len(focus_values),
                "peak_focus_periods": len([v for v in focus_values if v >= 0.8])
            },
            "recommendations": await self._generate_wellness_recommendations(recent_history)
        }
    
    async def _generate_wellness_recommendations(self, 
                                               history: List[Tuple[datetime, EmotionalVector]]) -> List[str]:
        """Generate wellness recommendations based on emotional patterns"""
        recommendations = []
        
        if not history:
            return recommendations
        
        # Analyze patterns
        stress_values = [vector.stress for _, vector in history]
        avg_stress = sum(stress_values) / len(stress_values)
        
        if avg_stress > 0.7:
            recommendations.append("Consider stress reduction techniques - average stress is high")
        
        focus_values = [vector.focus for _, vector in history]
        focus_periods = [v for v in focus_values if v >= 0.8]
        
        if len(focus_periods) / len(focus_values) < 0.2:
            recommendations.append("Focus enhancement techniques recommended - low focus periods detected")
        
        # Check for emotional volatility
        stress_changes = [abs(stress_values[i] - stress_values[i-1]) 
                         for i in range(1, len(stress_values))]
        if stress_changes and sum(stress_changes) / len(stress_changes) > 0.3:
            recommendations.append("High emotional volatility detected - consider stability practices")
        
        return recommendations