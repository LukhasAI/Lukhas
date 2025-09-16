"""
OpenAI Modulated Service
========================
Integrates the OpenAI Core Service with the signal-based modulation system
to provide dynamic, context-aware AI responses.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from candidate.orchestration.signals.homeostasis import HomeostasisController
from candidate.orchestration.signals.modulator import PromptModulator

# Import modulation components
from candidate.orchestration.signals.signal_bus import Signal, SignalBus, SignalType

# Import core components
from consciousness.reflection.openai_core_service import (  # MATRIZ Integration: OpenAI core service for Trinity Framework consciousness evolution and modulated reflection processing
    ModelType,
    OpenAICapability,
    OpenAICoreService,
    OpenAIRequest,
    OpenAIResponse,
)

logger = logging.getLogger(__name__)


@dataclass
class ModulatedRequest:
    """Enhanced request with modulation context"""

    base_request: OpenAIRequest
    signal_context: dict[str, float]
    modulation_params: dict[str, Any]
    priority_boost: float = 0.0
    emotional_tone: Optional[str] = None


class OpenAIModulatedService:
    """
    Enhanced OpenAI service with signal-based modulation.
    Adapts AI behavior based on system signals and homeostasis.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize modulated service with all components"""
        # Core service
        self.core_service = OpenAICoreService(api_key)

        # Modulation components
        self.signal_bus = SignalBus()
        self.homeostasis = HomeostasisController()
        self.modulator = PromptModulator()

        # State tracking
        self.active_signals: dict[str, Signal] = {}
        self.modulation_history: list[dict[str, Any]] = []

        # Subscribe to relevant signals
        self._setup_signal_subscriptions()

        logger.info("OpenAI Modulated Service initialized")

    def _setup_signal_subscriptions(self):
        """Subscribe to signals that affect AI behavior"""
        # Subscribe to urgency signals
        self.signal_bus.subscribe(SignalType.URGENCY, self._handle_urgency_signal)

        # Subscribe to novelty signals (for creativity)
        self.signal_bus.subscribe(SignalType.NOVELTY, self._handle_novelty_signal)

        # Subscribe to ambiguity signals
        self.signal_bus.subscribe(SignalType.AMBIGUITY, self._handle_ambiguity_signal)

        # Subscribe to stress signals (affects processing)
        self.signal_bus.subscribe(SignalType.STRESS, self._handle_stress_signal)

    def _handle_urgency_signal(self, signal: Signal):
        """Handle urgency signals by adjusting response speed"""
        self.active_signals["urgency"] = signal
        logger.info(f"Urgency signal received: {signal.level}")

    def _handle_novelty_signal(self, signal: Signal):
        """Handle novelty signals by adjusting creativity"""
        self.active_signals["novelty"] = signal
        logger.info(f"Novelty signal received: {signal.level}")

    def _handle_ambiguity_signal(self, signal: Signal):
        """Handle ambiguity signals by requesting clarification"""
        self.active_signals["ambiguity"] = signal
        logger.info(f"Ambiguity signal received: {signal.level}")

    def _handle_stress_signal(self, signal: Signal):
        """Handle stress signals by adjusting processing"""
        self.active_signals["stress"] = signal
        logger.info(f"Stress signal received: {signal.level}")

    async def process_modulated_request(
        self,
        module: str,
        capability: OpenAICapability,
        data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> OpenAIResponse:
        """
        Process a request with signal-based modulation.

        Args:
            module: Module making the request
            capability: OpenAI capability needed
            data: Request data
            context: Optional context for modulation

        Returns:
            Modulated OpenAI response
        """
        try:
            # Check homeostasis
            homeostasis_state = self.homeostasis.get_system_state()

            # Create signal context
            signal_context = self._create_signal_context(homeostasis_state)

            # Modulate the request if it's text generation
            if capability == OpenAICapability.TEXT_GENERATION:
                data = await self._modulate_text_request(data, signal_context)

            # Determine model based on signals
            model_type = self._select_model_from_signals(signal_context)

            # Create base request
            base_request = OpenAIRequest(
                module=module,
                capability=capability,
                data=data,
                model_preference=model_type,
                priority=self._calculate_priority(signal_context),
            )

            # Process with core service
            response = await self.core_service.process_request(base_request)

            # Post-process response based on signals
            if response.success and capability == OpenAICapability.TEXT_GENERATION:
                response = await self._post_process_response(response, signal_context)

            # Update homeostasis based on response
            await self._update_homeostasis(response, signal_context)

            # Log modulation
            self._log_modulation(base_request, signal_context, response)

            return response

        except Exception as e:
            logger.error(f"Error in modulated request: {e}")
            # Fallback to unmodulated request
            return await self.core_service.process_request(
                OpenAIRequest(module=module, capability=capability, data=data)
            )

    def _create_signal_context(self, homeostasis_state: dict[str, Any]) -> dict[str, float]:
        """Create signal context from current system state"""
        context = {
            "urgency": 0.0,
            "clarity": 1.0,
            "ambiguity": 0.0,
            "complexity": 0.5,
            "emotional_intensity": 0.0,
        }

        # Add active signal levels
        for signal_type, signal in self.active_signals.items():
            if not signal.is_expired():
                context[signal_type] = signal.level

        # Add homeostasis factors
        if homeostasis_state.get("oscillation_detected"):
            context["instability"] = homeostasis_state.get("oscillation_strength", 0.5)

        if homeostasis_state.get("emergency_mode"):
            context["urgency"] = max(context["urgency"], 0.9)

        return context

    async def _modulate_text_request(self, data: dict[str, Any], signal_context: dict[str, float]) -> dict[str, Any]:
        """Modulate text generation request based on signals"""
        # Get original prompt
        original_prompt = data.get("prompt", "")
        if not original_prompt and "messages" in data:
            # Extract from messages
            for msg in reversed(data["messages"]):
                if msg.get("role") == "user":
                    original_prompt = msg.get("content", "")
                    break

        # Modulate the prompt
        modulated_prompt = self.modulator.modulate_prompt(original_prompt, signal_context)

        # Update request data
        if "prompt" in data:
            data["prompt"] = modulated_prompt
        elif "messages" in data:
            # Update last user message
            for msg in reversed(data["messages"]):
                if msg.get("role") == "user":
                    msg["content"] = modulated_prompt
                    break

        # Adjust parameters based on signals
        params = self.modulator.get_modulated_params(signal_context)

        # Update temperature
        if "temperature" in params:
            data["temperature"] = params["temperature"]

        # Update max_tokens
        if "max_tokens" in params:
            data["max_tokens"] = params["max_tokens"]

        # Add reasoning effort for complex tasks
        if signal_context.get("complexity", 0) > 0.7:
            data["reasoning_effort"] = max(0.7, signal_context["complexity"])

        return data

    def _select_model_from_signals(self, signal_context: dict[str, float]) -> ModelType:
        """Select appropriate model based on signal context"""
        urgency = signal_context.get("urgency", 0)
        complexity = signal_context.get("complexity", 0.5)
        clarity = signal_context.get("clarity", 1.0)

        # High urgency -> Fast model
        if urgency > 0.7:
            return ModelType.FAST

        # High complexity or low clarity -> Reasoning model
        if complexity > 0.7 or clarity < 0.3:
            return ModelType.REASONING

        # Creative/emotional context -> Creative model
        if signal_context.get("emotional_intensity", 0) > 0.5:
            return ModelType.CREATIVE

        # Default to fast for efficiency
        return ModelType.FAST

    def _calculate_priority(self, signal_context: dict[str, float]) -> int:
        """Calculate request priority from signals"""
        base_priority = 5

        # Boost for urgency
        urgency_boost = signal_context.get("urgency", 0) * 4

        # Boost for instability
        instability_boost = signal_context.get("instability", 0) * 2

        # Calculate final priority (1-10)
        priority = int(base_priority + urgency_boost + instability_boost)
        return min(10, max(1, priority))

    async def _post_process_response(
        self, response: OpenAIResponse, signal_context: dict[str, float]
    ) -> OpenAIResponse:
        """Post-process response based on signal context"""
        if not response.data or "content" not in response.data:
            return response

        content = response.data["content"]

        # High ambiguity -> Add clarification request
        if signal_context.get("ambiguity", 0) > 0.6:
            content += "\n\n*Note: I detected some ambiguity in your request. Could you please clarify what you meant?*"

        # High urgency -> Add action items
        if signal_context.get("urgency", 0) > 0.7:
            content = f"**URGENT RESPONSE:**\n{content}"

        # Update response
        response.data["content"] = content
        response.data["modulation_applied"] = True
        response.data["signal_context"] = signal_context

        return response

    async def _update_homeostasis(self, response: OpenAIResponse, signal_context: dict[str, float]):
        """Update homeostasis based on response"""
        # Create feedback signal
        feedback_signal = Signal(
            name=SignalType.TRUST if response.success else SignalType.AMBIGUITY,
            source="openai_modulated",
            level=0.7 if response.success else 0.3,
            metadata={
                "response_success": response.success,
                "latency_ms": response.latency_ms,
                "signal_context": signal_context,
            },
        )

        # Publish feedback
        self.signal_bus.publish(feedback_signal)

        # Let homeostasis process
        self.homeostasis.process_signals(self.signal_bus.get_active_signals())

    def _log_modulation(
        self,
        request: OpenAIRequest,
        signal_context: dict[str, float],
        response: OpenAIResponse,
    ):
        """Log modulation for analysis"""
        modulation_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "module": request.module,
            "capability": request.capability.value,
            "signal_context": signal_context,
            "model_used": (request.model_preference.value if request.model_preference else "default"),
            "priority": request.priority,
            "success": response.success,
            "latency_ms": response.latency_ms,
        }

        self.modulation_history.append(modulation_record)

        # Limit history size
        if len(self.modulation_history) > 1000:
            self.modulation_history = self.modulation_history[-500:]

    async def emit_signal(self, signal: Signal):
        """Emit a signal to affect AI behavior"""
        self.signal_bus.publish(signal)

        # Process immediately if urgent
        if signal.name == SignalType.URGENCY and signal.level > 0.8:
            self.homeostasis.process_signals([signal])

    def get_modulation_stats(self) -> dict[str, Any]:
        """Get statistics about modulation"""
        if not self.modulation_history:
            return {"message": "No modulation history available"}

        # Calculate stats
        total_requests = len(self.modulation_history)
        successful = sum(1 for r in self.modulation_history if r["success"])

        # Average signal intensities
        avg_signals = {}
        signal_types = ["urgency", "clarity", "ambiguity", "complexity"]
        for signal_type in signal_types:
            values = [r["signal_context"].get(signal_type, 0) for r in self.modulation_history]
            avg_signals[signal_type] = sum(values) / len(values) if values else 0

        # Model usage
        model_usage = {}
        for record in self.modulation_history:
            model = record.get("model_used", "unknown")
            model_usage[model] = model_usage.get(model, 0) + 1

        return {
            "total_modulated_requests": total_requests,
            "success_rate": successful / total_requests if total_requests > 0 else 0,
            "average_signals": avg_signals,
            "model_usage": model_usage,
            "active_signals": len(self.active_signals),
            "homeostasis_state": self.homeostasis.get_system_state(),
        }


# Convenience functions
async def create_modulated_service(
    api_key: Optional[str] = None,
) -> OpenAIModulatedService:
    """Create and initialize a modulated OpenAI service"""
    service = OpenAIModulatedService(api_key)

    # Emit initial trust signal
    await service.emit_signal(
        Signal(
            name=SignalType.TRUST,
            source="system_init",
            level=0.8,
            metadata={"init": True},
        )
    )

    return service


async def modulated_text_generation(
    module: str, prompt: str, urgency: float = 0.0, complexity: float = 0.5, **kwargs
) -> str:
    """
    Generate text with automatic modulation.

    Args:
        module: Calling module name
        prompt: Text prompt
        urgency: Urgency level (0-1)
        complexity: Complexity level (0-1)
        **kwargs: Additional parameters

    Returns:
        Generated text
    """
    service = await create_modulated_service()

    # Emit relevant signals
    if urgency > 0:
        await service.emit_signal(Signal(name=SignalType.URGENCY, source=module, level=urgency))

    # Process request
    response = await service.process_modulated_request(
        module=module,
        capability=OpenAICapability.TEXT_GENERATION,
        data={"prompt": prompt, **kwargs},
        context={"complexity": complexity},
    )

    if response.success:
        return response.data["content"]
    else:
        raise Exception(f"Modulated text generation failed: {response.error}")


# Example usage
async def demo():
    """Demonstrate modulated OpenAI service"""
    service = await create_modulated_service()

    # Test with different signal contexts

    # 1. Urgent request
    urgent_signal = Signal(name=SignalType.URGENCY, source="demo", level=0.9)
    await service.emit_signal(urgent_signal)

    response1 = await service.process_modulated_request(
        module="demo",
        capability=OpenAICapability.TEXT_GENERATION,
        data={"prompt": "What should I do in case of fire?"},
    )
    print(f"Urgent response: {response1.data.get('content', 'No content')[:100]}...")

    # 2. Complex request
    complexity_signal = Signal(name=SignalType.AMBIGUITY, source="demo", level=0.7)
    await service.emit_signal(complexity_signal)

    response2 = await service.process_modulated_request(
        module="demo",
        capability=OpenAICapability.TEXT_GENERATION,
        data={"prompt": "Explain consciousness"},
    )
    print(f"Complex response: {response2.data.get('content', 'No content')[:100]}...")

    # Get stats
    stats = service.get_modulation_stats()
    print(f"\nModulation Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(demo())
