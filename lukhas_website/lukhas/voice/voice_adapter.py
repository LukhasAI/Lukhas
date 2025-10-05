#!/usr/bin/env python3
"""
LUKHAS Voice Adapter
Adaptive voice processing for different contexts and audiences
Constellation Framework Integration
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class VoiceStyle(Enum):
    """Available voice styles"""
    CONSCIOUSNESS = "consciousness"
    IDENTITY = "identity"
    GUARDIAN = "guardian"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    FORMAL = "formal"
    CASUAL = "casual"
    EMPATHETIC = "empathetic"


@dataclass
class AdaptationContext:
    """Context for voice adaptation"""
    audience: str = "general"
    purpose: str = "communication"
    formality_level: float = 0.5
    technical_level: float = 0.5
    emotional_level: float = 0.5
    constellation_focus: Optional[str] = None


@dataclass
class AdaptationResult:
    """Result of voice adaptation"""
    original_text: str
    adapted_text: str
    style_applied: str
    context_used: AdaptationContext
    adaptation_metrics: Dict[str, float]
    metadata: Dict[str, Any]


class VoiceAdapter:
    """
    Adaptive voice processing system
    Adjusts voice output based on context, audience, and purpose
    """

    def __init__(self,
                 default_style: VoiceStyle = VoiceStyle.CONSCIOUSNESS,
                 enable_context_learning: bool = True,
                 constellation_integration: bool = True):
        """Initialize voice adapter"""
        self.default_style = default_style
        self.enable_context_learning = enable_context_learning
        self.constellation_integration = constellation_integration
        self.initialized = True

        # Adaptation configurations
        self.style_configs = {
            VoiceStyle.CONSCIOUSNESS: {
                "tone": "contemplative",
                "depth": 0.8,
                "complexity": 0.7,
                "empathy": 0.8,
                "technical": 0.6
            },
            VoiceStyle.IDENTITY: {
                "tone": "authentic",
                "depth": 0.7,
                "complexity": 0.6,
                "empathy": 0.7,
                "technical": 0.5
            },
            VoiceStyle.GUARDIAN: {
                "tone": "protective",
                "depth": 0.6,
                "complexity": 0.7,
                "empathy": 0.6,
                "technical": 0.7
            },
            VoiceStyle.TECHNICAL: {
                "tone": "precise",
                "depth": 0.5,
                "complexity": 0.9,
                "empathy": 0.3,
                "technical": 0.9
            },
            VoiceStyle.CREATIVE: {
                "tone": "imaginative",
                "depth": 0.8,
                "complexity": 0.6,
                "empathy": 0.7,
                "technical": 0.4
            },
            VoiceStyle.FORMAL: {
                "tone": "professional",
                "depth": 0.5,
                "complexity": 0.7,
                "empathy": 0.4,
                "technical": 0.6
            },
            VoiceStyle.CASUAL: {
                "tone": "friendly",
                "depth": 0.4,
                "complexity": 0.4,
                "empathy": 0.6,
                "technical": 0.3
            },
            VoiceStyle.EMPATHETIC: {
                "tone": "caring",
                "depth": 0.7,
                "complexity": 0.5,
                "empathy": 0.9,
                "technical": 0.4
            }
        }

        # Context learning storage
        self.context_history = []
        self.adaptation_preferences = {}

        logger.info(f"🎭 Voice Adapter initialized with {len(self.style_configs)} styles")

    def adapt(self,
              text: str,
              style: Union[str, VoiceStyle] = None,
              context: Optional[AdaptationContext] = None,
              learn_from_adaptation: bool = True) -> AdaptationResult:
        """
        Adapt text to specified style and context

        Args:
            text: Input text to adapt
            style: Voice style to apply
            context: Adaptation context
            learn_from_adaptation: Whether to learn from this adaptation

        Returns:
            AdaptationResult with adapted text and metrics
        """
        if not text.strip():
            return self._create_empty_result(text)

        # Resolve style
        if isinstance(style, str):
            try:
                style = VoiceStyle(style)
            except ValueError:
                logger.warning(f"Unknown style '{style}', using default")
                style = self.default_style
        elif style is None:
            style = self.default_style

        # Use default context if not provided
        if context is None:
            context = AdaptationContext()

        # Get style configuration
        style_config = self.style_configs.get(style, self.style_configs[self.default_style])

        # Apply voice adaptation
        adapted_text = self._apply_style_adaptation(text, style, style_config, context)

        # Apply constellation integration if enabled
        if self.constellation_integration:
            adapted_text = self._apply_constellation_adaptation(adapted_text, style, context)

        # Calculate adaptation metrics
        metrics = self._calculate_adaptation_metrics(text, adapted_text, style_config)

        # Create result
        result = AdaptationResult(
            original_text=text,
            adapted_text=adapted_text,
            style_applied=style.value,
            context_used=context,
            adaptation_metrics=metrics,
            metadata={
                "style_config": style_config,
                "constellation_integration": self.constellation_integration,
                "context_learning": self.enable_context_learning
            }
        )

        # Learn from adaptation if enabled
        if learn_from_adaptation and self.enable_context_learning:
            self._learn_from_adaptation(result)

        return result

    def _apply_style_adaptation(self,
                              text: str,
                              style: VoiceStyle,
                              config: Dict[str, float],
                              context: AdaptationContext) -> str:
        """Apply style-specific adaptation"""
        adapted = text

        # Apply tone adjustment
        adapted = self._apply_tone_adjustment(adapted, config["tone"], config)

        # Apply complexity adjustment
        adapted = self._apply_complexity_adjustment(adapted, config["complexity"], context)

        # Apply empathy adjustment
        adapted = self._apply_empathy_adjustment(adapted, config["empathy"])

        # Apply technical level adjustment
        adapted = self._apply_technical_adjustment(adapted, config["technical"], context)

        return adapted

    def _apply_constellation_adaptation(self,
                                      text: str,
                                      style: VoiceStyle,
                                      context: AdaptationContext) -> str:
        """Apply Constellation Framework-specific adaptations"""
        if not self.constellation_integration:
            return text

        # Apply constellation-specific adaptations based on focus
        if context.constellation_focus:
            if context.constellation_focus == "identity":
                text = self._adapt_for_identity_focus(text, style)
            elif context.constellation_focus == "consciousness":
                text = self._adapt_for_consciousness_focus(text, style)
            elif context.constellation_focus == "guardian":
                text = self._adapt_for_guardian_focus(text, style)

        return text

    def _apply_tone_adjustment(self, text: str, tone: str, config: Dict[str, float]) -> str:
        """Apply tone-specific adjustments"""
        # Placeholder for tone adjustment implementation
        return text

    def _apply_complexity_adjustment(self, text: str, complexity: float, context: AdaptationContext) -> str:
        """Apply complexity level adjustments"""
        # Adjust based on both style complexity and context technical level
        target_complexity = (complexity + context.technical_level) / 2
        # Placeholder for complexity adjustment implementation
        return text

    def _apply_empathy_adjustment(self, text: str, empathy_level: float) -> str:
        """Apply empathy level adjustments"""
        # Placeholder for empathy adjustment implementation
        return text

    def _apply_technical_adjustment(self, text: str, technical_level: float, context: AdaptationContext) -> str:
        """Apply technical level adjustments"""
        # Placeholder for technical adjustment implementation
        return text

    def _adapt_for_identity_focus(self, text: str, style: VoiceStyle) -> str:
        """Adapt for identity-focused communication"""
        # Placeholder for identity focus adaptation
        return text

    def _adapt_for_consciousness_focus(self, text: str, style: VoiceStyle) -> str:
        """Adapt for consciousness-focused communication"""
        # Placeholder for consciousness focus adaptation
        return text

    def _adapt_for_guardian_focus(self, text: str, style: VoiceStyle) -> str:
        """Adapt for guardian-focused communication"""
        # Placeholder for guardian focus adaptation
        return text

    def _calculate_adaptation_metrics(self,
                                    original: str,
                                    adapted: str,
                                    config: Dict[str, float]) -> Dict[str, float]:
        """Calculate adaptation quality metrics"""
        return {
            "adaptation_ratio": len(adapted) / max(len(original), 1),
            "style_alignment": sum(config.values()) / len(config),
            "text_coherence": 0.85,  # Placeholder
            "context_relevance": 0.80,  # Placeholder
            "constellation_integration": 0.75 if self.constellation_integration else 0.0
        }

    def _learn_from_adaptation(self, result: AdaptationResult) -> None:
        """Learn from adaptation for future improvements"""
        if self.enable_context_learning:
            # Store adaptation for learning
            self.context_history.append({
                "style": result.style_applied,
                "context": result.context_used,
                "metrics": result.adaptation_metrics,
                "success_indicators": self._extract_success_indicators(result)
            })

            # Limit history size
            if len(self.context_history) > 1000:
                self.context_history = self.context_history[-800:]

    def _extract_success_indicators(self, result: AdaptationResult) -> Dict[str, float]:
        """Extract success indicators from adaptation result"""
        return {
            "coherence_score": result.adaptation_metrics.get("text_coherence", 0.0),
            "relevance_score": result.adaptation_metrics.get("context_relevance", 0.0),
            "adaptation_quality": result.adaptation_metrics.get("style_alignment", 0.0)
        }

    def _create_empty_result(self, text: str) -> AdaptationResult:
        """Create result for empty input"""
        return AdaptationResult(
            original_text=text,
            adapted_text=text,
            style_applied=self.default_style.value,
            context_used=AdaptationContext(),
            adaptation_metrics={},
            metadata={"empty_input": True}
        )

    def get_available_styles(self) -> List[str]:
        """Get list of available voice styles"""
        return [style.value for style in VoiceStyle]

    def get_style_config(self, style: Union[str, VoiceStyle]) -> Optional[Dict[str, float]]:
        """Get configuration for a specific style"""
        if isinstance(style, str):
            try:
                style = VoiceStyle(style)
            except ValueError:
                return None
        return self.style_configs.get(style)

    def get_adapter_status(self) -> Dict[str, Any]:
        """Get adapter status and metrics"""
        return {
            "initialized": self.initialized,
            "default_style": self.default_style.value,
            "available_styles": len(self.style_configs),
            "constellation_integration": self.constellation_integration,
            "context_learning": self.enable_context_learning,
            "adaptation_history_size": len(self.context_history),
            "styles": list(self.style_configs.keys())
        }
