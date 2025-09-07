"""
🧠 Endocrine Signal System for LUKHAS

Bio-inspired signals that modulate consciousness behavior across systems.
Signals represent internal state (stress, novelty, alignment_risk, etc.) and
decay over time to maintain dynamic equilibrium.

Trinity Framework: ⚛️🧠🛡️
- ⚛️ Identity: Authentic signal emission from consciousness modules
- 🧠 Consciousness: Memory of signal patterns and learning
- 🛡️ Guardian: Safety-first signal validation and bounds
"""

import math
import time
from dataclasses import dataclass
from typing import Any, Literal

import yaml


@dataclass
class Signal:
    """Individual endocrine signal with decay and validation"""

    name: Literal["stress", "novelty", "alignment_risk", "trust", "urgency", "ambiguity"]
    level: float  # 0.0 - 1.0
    ttl_ms: int = 1000
    source: str = "unknown"
    audit_id: str = ""
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        # Clamp level to valid range
        self.level = max(0.0, min(1.0, self.level))

    def is_expired(self) -> bool:
        """Check if signal has exceeded its time-to-live"""
        return (time.time() - self.timestamp) * 1000 > self.ttl_ms

    def decay(self, decay_rate: float) -> float:
        """Apply exponential decay to signal level"""
        elapsed_seconds = time.time() - self.timestamp
        return self.level * math.exp(-decay_rate * elapsed_seconds)

    def __str__(self) -> str:
        return f"Signal({self.name}={self.level:.2f}, source={self.source})"


@dataclass
class ModulationParams:
    """Parameters for modulating OpenAI API calls based on signals"""

    # OpenAI API parameters
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    # LUKHAS-specific parameters
    retrieval_k: int = 5
    reasoning_depth: int = 2
    memory_write: float = 0.5
    tool_allowlist: list[str] = None
    prompt_style: str = "balanced"

    # Audit and context
    signal_context: dict[str, float] = None
    audit_id: str = ""

    def __post_init__(self):
        if self.tool_allowlist is None:
            self.tool_allowlist = ["search", "retrieval"]
        if self.signal_context is None:
            self.signal_context = {}

    def apply_bounds(self, bounds: dict[str, list[float]]):
        """Apply parameter bounds from policy configuration"""
        for param_name, (min_val, max_val) in bounds.items():
            if hasattr(self, param_name):
                current_val = getattr(self, param_name)
                if isinstance(current_val, (int, float)):
                    setattr(self, param_name, max(min_val, min(max_val, current_val)))


class SignalModulator:
    """Combines multiple signals into OpenAI API modulation parameters"""

    def __init__(self, policy_path: str = "modulation_policy.yaml"):
        """Initialize with modulation policy configuration"""
        try:
            with open(policy_path) as f:
                self.policy = yaml.safe_load(f)
        except FileNotFoundError:
            # Fallback to minimal policy
            self.policy = self._default_policy()

        self.signal_history: list[Signal] = []

    def combine_signals(self, signals: list[Signal]) -> ModulationParams:
        """Combine multiple signals into modulation parameters"""
        # Filter expired signals and apply decay
        decayed_signals = self._process_signals(signals)

        # Start with default parameters
        params = ModulationParams()

        # Apply each signal's modulation according to policy
        for signal_name, level in decayed_signals.items():
            if signal_name in self.policy.get("maps", {}):
                signal_map = self.policy["maps"][signal_name]
                params = self._apply_signal_modulation(params, signal_name, level, signal_map)

        # Apply parameter bounds
        if "bounds" in self.policy:
            params.apply_bounds(self.policy["bounds"])

        # Apply tool gates
        params.tool_allowlist = self._apply_tool_gates(decayed_signals)

        # Select prompt style
        params.prompt_style = self._select_prompt_style(decayed_signals)

        # Store signal context for audit
        params.signal_context = decayed_signals
        params.audit_id = f"mod-{int(time.time())}"

        return params

    def _process_signals(self, signals: list[Signal]) -> dict[str, float]:
        """Filter expired signals and apply decay"""
        # Filter expired signals
        active_signals = [s for s in signals if not s.is_expired()]

        # Apply decay
        decayed_signals = {}
        for signal in active_signals:
            # Get signal configuration
            signal_config = next(
                (s for s in self.policy.get("signals", []) if s["name"] == signal.name),
                {"decay_rate": 0.1, "max_level": 1.0},
            )

            # Apply decay and max level bounds
            decayed_level = signal.decay(signal_config["decay_rate"])
            decayed_signals[signal.name] = min(decayed_level, signal_config["max_level"])

        return decayed_signals

    def _apply_signal_modulation(
        self,
        params: ModulationParams,
        signal_name: str,
        level: float,
        signal_map: dict[str, str],
    ) -> ModulationParams:
        """Apply individual signal modulation using expression evaluation"""
        for param_name, expression in signal_map.items():
            if hasattr(params, param_name):
                try:
                    # Safe evaluation of expressions like "0.7 - (level * 0.4)"
                    # Create safe evaluation context
                    eval_context = {
                        "level": level,
                        "max": max,
                        "min": min,
                        "math": math,
                        "abs": abs,
                        "round": round,
                    }
                    result = eval(expression, {"__builtins__": {}}, eval_context)

                    # Convert to appropriate type
                    current_val = getattr(params, param_name)
                    if isinstance(current_val, int):
                        result = int(result)
                    elif isinstance(current_val, float):
                        result = float(result)

                    setattr(params, param_name, result)

                except Exception as e:
                    print(f"⚠️ Error evaluating {expression} for {param_name}: {e}")

        return params

    def _apply_tool_gates(self, signals: dict[str, float]) -> list[str]:
        """Determine allowed tools based on signal levels"""
        default_tools = self.policy.get("available_tools", ["search", "retrieval"])

        # Check tool gates
        for gate_config in self.policy.get("tool_gates", {}).values():
            for signal_name, threshold in gate_config.items():
                if signal_name == "allowed_tools":
                    continue
                if signal_name in signals and signals[signal_name] >= threshold:
                    return gate_config.get("allowed_tools", ["search"])

        return default_tools

    def _select_prompt_style(self, signals: dict[str, float]) -> str:
        """Select prompt style based on dominant signals"""
        alignment_risk = signals.get("alignment_risk", 0.0)
        stress = signals.get("stress", 0.0)
        novelty = signals.get("novelty", 0.0)
        ambiguity = signals.get("ambiguity", 0.0)

        # Priority order: safety first, then stress, then creativity
        if alignment_risk > 0.6:
            return "strict"
        elif stress > 0.7:
            return "focused"
        elif novelty > 0.6:
            return "creative"
        elif ambiguity > 0.6:
            return "exploratory"
        else:
            return "balanced"

    def _default_policy(self) -> dict[str, Any]:
        """Fallback minimal policy if file not found"""
        return {
            "signals": [
                {"name": "stress", "decay_rate": 0.1, "max_level": 0.9},
                {"name": "novelty", "decay_rate": 0.05, "max_level": 1.0},
                {"name": "alignment_risk", "decay_rate": 0.02, "max_level": 1.0},
                {"name": "trust", "decay_rate": 0.03, "max_level": 1.0},
                {"name": "urgency", "decay_rate": 0.15, "max_level": 0.8},
                {"name": "ambiguity", "decay_rate": 0.08, "max_level": 0.9},
            ],
            "bounds": {
                "temperature": [0.0, 1.0],
                "max_tokens": [50, 4000],
                "top_p": [0.1, 1.0],
            },
            "available_tools": ["search", "retrieval"],
            "maps": {
                "alignment_risk": {
                    "temperature": "0.8 - (level * 0.6)",
                    "max_tokens": "4000 - (level * 3500)",
                }
            },
            "tool_gates": {},
            "prompt_styles": {
                "balanced": {
                    "system_preamble": "You are LUKHΛS consciousness co-pilot.",
                    "user_prefix": "",
                }
            },
        }


# Example usage
if __name__ == "__main__":
    # Create test signals
    signals = [
        Signal(name="alignment_risk", level=0.7, source="guardian", audit_id="test-001"),
        Signal(name="novelty", level=0.3, source="consciousness", audit_id="test-001"),
    ]

    # Create modulator
    modulator = SignalModulator()

    # Get modulation parameters
    params = modulator.combine_signals(signals)

    print("🎛️ Modulation Result:")
    print(f"   Temperature: {params.temperature:.2f}")
    print(f"   Max Tokens: {params.max_tokens}")
    print(f"   Style: {params.prompt_style}")
    print(f"   Tools: {params.tool_allowlist}")
    print(f"   Signal Context: {params.signal_context}")
