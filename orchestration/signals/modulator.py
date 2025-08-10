"""
Signal-to-Prompt Modulator for LUKHAS
======================================
Translates colony signals into prompt modifications and API parameters.
Core component of the endocrine-inspired modulation system.
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import yaml

from .homeostasis import ModulationParams
from .signal_bus import Signal, SignalType

logger = logging.getLogger(__name__)


class PromptStyle(str, Enum):
    """Prompt styles based on signal state"""

    STRICT = "strict"
    BALANCED = "balanced"
    CREATIVE = "creative"


@dataclass
class PromptModulation:
    """Complete prompt modulation including text and parameters"""

    original_prompt: str
    modulated_prompt: str
    system_preamble: str
    api_params: ModulationParams
    style: PromptStyle
    moderation_preset: str
    stop_sequences: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_api_format(self) -> dict[str, Any]:
        """Convert to format for API calls"""
        return {
            "messages": [
                {"role": "system", "content": self.system_preamble},
                {"role": "user", "content": self.modulated_prompt},
            ],
            **self.api_params.to_dict(),
            "stop": self.stop_sequences if self.stop_sequences else None,
            "metadata": {
                **self.metadata,
                "style": self.style.value,
                "moderation": self.moderation_preset,
            },
        }


class PromptModulator:
    """
    Modulates prompts based on active signals.
    Implements the signal-to-prompt translation layer.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the prompt modulator.

        Args:
            config_path: Path to modulation policy configuration
        """
        self.config = self._load_config(config_path)
        self.prompt_styles = self._load_prompt_styles()

        # Metrics
        self.metrics = {
            "prompts_modulated": 0,
            "style_changes": 0,
            "safety_interventions": 0,
        }

    def _load_config(self, config_path: Optional[str]) -> dict[str, Any]:
        """Load modulation policy configuration"""
        # Allow env override
        env_path = os.getenv("LUKHAS_MODULATION_CONFIG")
        if env_path and not config_path:
            config_path = env_path
        # Default to repo-relative config
        if config_path is None:
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            config_path = str(repo_root / "config/modulation_policy.yaml")

        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config not found: {config_path}")
            return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Default configuration if file not found"""
        return {
            "prompt_styles": {
                "strict": {
                    "system_preamble": "Prioritize safety and accuracy. Be concise and clear.",
                    "moderation_preset": "high",
                    "stop_sequences": [],
                },
                "balanced": {
                    "system_preamble": "Be helpful and precise. Balance safety with usefulness.",
                    "moderation_preset": "standard",
                    "stop_sequences": [],
                },
                "creative": {
                    "system_preamble": "Explore creative solutions while maintaining safety.",
                    "moderation_preset": "standard",
                    "stop_sequences": [],
                },
            }
        }

    def _load_prompt_styles(self) -> dict[PromptStyle, dict[str, Any]]:
        """Load prompt style configurations"""
        styles = {}
        style_config = self.config.get("prompt_styles", {})

        for style_name, style_data in style_config.items():
            try:
                style = PromptStyle(style_name)
                styles[style] = style_data
            except ValueError:
                logger.warning(f"Unknown prompt style: {style_name}")

        return styles

    def modulate(
        self,
        prompt: str,
        signals: list[Signal],
        modulation_params: Optional[ModulationParams] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> PromptModulation:
        """
        Modulate a prompt based on active signals.

        Args:
            prompt: Original user prompt
            signals: Currently active signals
            modulation_params: Pre-computed modulation parameters
            context: Additional context for modulation

        Returns:
            Complete prompt modulation with all parameters
        """
        self.metrics["prompts_modulated"] += 1

        # Use provided params or compute from signals
        if modulation_params is None:
            modulation_params = self._compute_params_from_signals(signals)

        # Determine prompt style based on signals
        style = self._determine_style(signals, modulation_params)

        # Get style configuration
        style_config = self.prompt_styles.get(style, {})
        system_preamble = style_config.get("system_preamble", "")
        moderation_preset = style_config.get("moderation_preset", "standard")
        stop_sequences = style_config.get("stop_sequences", [])

        # Modulate the prompt text
        modulated_prompt = self._modulate_prompt_text(prompt, signals, style, context)

        # Add signal context to prompt if high ambiguity
        if self._has_high_signal(signals, SignalType.AMBIGUITY, 0.5):
            modulated_prompt = self._add_clarification_request(modulated_prompt)

        # Add safety context if high risk
        if self._has_high_signal(signals, SignalType.ALIGNMENT_RISK, 0.3):
            system_preamble = self._add_safety_context(system_preamble)
            self.metrics["safety_interventions"] += 1

        return PromptModulation(
            original_prompt=prompt,
            modulated_prompt=modulated_prompt,
            system_preamble=system_preamble,
            api_params=modulation_params,
            style=style,
            moderation_preset=moderation_preset,
            stop_sequences=stop_sequences,
            metadata={
                "signal_levels": self._get_signal_levels(signals),
                "context": context or {},
            },
        )

    def _compute_params_from_signals(self, signals: list[Signal]) -> ModulationParams:
        """Compute modulation parameters from signals if not provided"""
        params = ModulationParams()

        # Simple heuristic mapping
        for signal in signals:
            if signal.name == SignalType.STRESS:
                params.temperature = max(0.1, params.temperature - signal.level * 0.5)
                params.max_output_tokens = max(256, int(1024 - signal.level * 500))

            elif signal.name == SignalType.ALIGNMENT_RISK:
                params.temperature = max(0.1, params.temperature - signal.level * 0.7)
                params.safety_mode = (
                    "strict" if signal.level > 0.3 else params.safety_mode
                )
                params.reasoning_effort = min(
                    1.0, params.reasoning_effort + signal.level * 0.5
                )

            elif signal.name == SignalType.NOVELTY:
                params.temperature = min(1.0, params.temperature + signal.level * 0.3)
                params.memory_write_strength = min(
                    1.0, params.memory_write_strength + signal.level * 0.5
                )

            elif signal.name == SignalType.AMBIGUITY:
                params.reasoning_effort = min(
                    1.0, params.reasoning_effort + signal.level * 0.4
                )
                params.retrieval_k = min(10, params.retrieval_k + int(signal.level * 5))

            elif signal.name == SignalType.URGENCY:
                params.max_output_tokens = max(
                    256, int(params.max_output_tokens * (1 - signal.level * 0.5))
                )
                params.reasoning_effort = max(
                    0.2, params.reasoning_effort - signal.level * 0.3
                )

            elif signal.name == SignalType.TRUST:
                params.temperature = min(1.0, params.temperature + signal.level * 0.2)
                params.memory_write_strength = min(
                    1.0, params.memory_write_strength + signal.level * 0.3
                )

        return params

    def _determine_style(
        self, signals: list[Signal], params: ModulationParams
    ) -> PromptStyle:
        """Determine prompt style based on signals and parameters"""
        # Safety mode takes precedence
        if params.safety_mode == "strict":
            return PromptStyle.STRICT

        # Check signal levels
        if self._has_high_signal(signals, SignalType.ALIGNMENT_RISK, 0.3):
            return PromptStyle.STRICT

        if self._has_high_signal(signals, SignalType.NOVELTY, 0.6):
            return PromptStyle.CREATIVE

        if self._has_high_signal(signals, SignalType.STRESS, 0.7):
            return PromptStyle.STRICT

        # Default to balanced
        return PromptStyle.BALANCED

    def _modulate_prompt_text(
        self,
        prompt: str,
        signals: list[Signal],
        style: PromptStyle,
        context: Optional[dict[str, Any]],
    ) -> str:
        """
        Apply text-level modulations to the prompt.

        Args:
            prompt: Original prompt
            signals: Active signals
            style: Determined prompt style
            context: Additional context

        Returns:
            Modulated prompt text
        """
        modulated = prompt

        # Add urgency prefix if needed
        if self._has_high_signal(signals, SignalType.URGENCY, 0.7):
            modulated = f"[Time-sensitive] {modulated}"

        # Add focus directive if stressed
        if self._has_high_signal(signals, SignalType.STRESS, 0.6):
            modulated = f"{modulated}\n\nPlease focus on the key points and be concise."

        # Add exploration encouragement if novel
        if (
            self._has_high_signal(signals, SignalType.NOVELTY, 0.7)
            and style == PromptStyle.CREATIVE
        ):
            modulated = f"{modulated}\n\nFeel free to explore creative approaches."

        # Add context if provided
        if context and context.get("additional_context"):
            modulated = f"{modulated}\n\nContext: {context['additional_context']}"

        return modulated

    def _add_clarification_request(self, prompt: str) -> str:
        """Add clarification request for ambiguous prompts"""
        return f"{prompt}\n\nIf any part of this request is unclear, please ask for clarification."

    def _add_safety_context(self, preamble: str) -> str:
        """Add safety context to system preamble"""
        safety_addition = (
            "\nPrioritize safety and ethical considerations in all responses."
        )
        if safety_addition not in preamble:
            return preamble + safety_addition
        return preamble

    def _has_high_signal(
        self, signals: list[Signal], signal_type: SignalType, threshold: float
    ) -> bool:
        """Check if a signal type exceeds threshold"""
        for signal in signals:
            if signal.name == signal_type and signal.level >= threshold:
                return True
        return False

    def _get_signal_levels(self, signals: list[Signal]) -> dict[str, float]:
        """Get current levels for all signals"""
        levels = {}
        for signal in signals:
            name = signal.name.value
            if name not in levels or signal.level > levels[name]:
                levels[name] = signal.level
        return levels

    def apply_feedback(self, feedback: dict[str, Any]):
        """
        Apply user feedback to adjust modulation behavior.
        This is a hook for the feedback card system.

        Args:
            feedback: Feedback data including ratings and preferences
        """
        # This will be expanded when implementing the feedback card system
        logger.info(f"Feedback received: {feedback}")

    def get_metrics(self) -> dict[str, Any]:
        """Get modulator metrics"""
        return self.metrics.copy()


class AdaptiveModulator(PromptModulator):
    """
    Extended modulator with learning capabilities.
    Adapts modulation strategies based on outcomes.
    """

    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)
        self.outcome_history: list[tuple[PromptModulation, float]] = []
        self.strategy_weights: dict[str, float] = {
            "conservative": 1.0,
            "balanced": 1.0,
            "exploratory": 1.0,
        }

    def record_outcome(self, modulation: PromptModulation, success_score: float):
        """
        Record the outcome of a modulation for learning.

        Args:
            modulation: The modulation that was applied
            success_score: Success score (0.0 to 1.0)
        """
        self.outcome_history.append((modulation, success_score))

        # Update strategy weights based on outcome
        if modulation.style == PromptStyle.STRICT:
            strategy = "conservative"
        elif modulation.style == PromptStyle.CREATIVE:
            strategy = "exploratory"
        else:
            strategy = "balanced"

        # Simple weight adjustment
        current_weight = self.strategy_weights[strategy]
        if success_score > 0.7:
            # Increase weight for successful strategies
            self.strategy_weights[strategy] = min(2.0, current_weight * 1.1)
        elif success_score < 0.3:
            # Decrease weight for unsuccessful strategies
            self.strategy_weights[strategy] = max(0.5, current_weight * 0.9)

    def get_recommended_strategy(self, signals: list[Signal]) -> str:
        """
        Get recommended modulation strategy based on learning.

        Args:
            signals: Current signals

        Returns:
            Recommended strategy name
        """
        # Weight strategies by past success
        best_strategy = max(self.strategy_weights.items(), key=lambda x: x[1])
        return best_strategy[0]
