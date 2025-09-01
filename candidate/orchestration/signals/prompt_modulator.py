#!/usr/bin/env python3
"""
Signal-to-Prompt Modulation System
===================================
Maps endocrine signals to OpenAI API parameters for adaptive behavior.
Based on the GPT5 audit recommendations.
"""

import logging
import time
from typing import Any, Optional

import yaml

from candidate.orchestration.signals.signal_bus import Signal

logger = logging.getLogger(__name__)


# Default modulation policy
DEFAULT_POLICY = {
    "signals": [
        {"name": "stress", "weight": 0.9, "cooldown_ms": 800},
        {"name": "alignment_risk", "weight": 1.0, "cooldown_ms": 0},
        {"name": "novelty", "weight": 0.6, "cooldown_ms": 500},
        {"name": "trust", "weight": 0.4, "cooldown_ms": 500},
        {"name": "urgency", "weight": 0.5, "cooldown_ms": 300},
        {"name": "ambiguity", "weight": 0.7, "cooldown_ms": 700},
    ],
    "bounds": {
        "temperature": [0.0, 1.0],
        "top_p": [0.1, 1.0],
        "max_output_tokens": [256, 2048],
        "reasoning_effort": [0.0, 1.0],
        "retrieval_k": [2, 10],
        "planner_beam": [1, 6],
        "memory_write": [0.1, 1.0],
        "safety_mode": ["strict", "balanced", "creative"],
        "tool_allowlist": ["search", "code_exec", "browser", "retrieval", "scheduler"],
    },
    "maps": {
        "alignment_risk": {
            "temperature": "1 - 0.85*x",
            "top_p": "max(0.2, 1 - 0.8*x)",
            "reasoning_effort": "min(1.0, 0.4 + 0.6*x)",
            "planner_beam": "max(1, round(6 - 4*x))",
            "safety_mode": "strict if x>0.3 else balanced",
            "tool_allowlist": "['retrieval'] if x>0.7 else ['retrieval','browser']",
        },
        "stress": {
            "temperature": "max(0.1, 0.7 - 0.6*x)",
            "top_p": "max(0.3, 0.9 - 0.5*x)",
            "max_output_tokens": "round(1400 - 600*x)",
            "retrieval_k": "min(10, 4 + round(4*x))",
        },
        "ambiguity": {
            "reasoning_effort": "min(1.0, 0.3 + 0.7*x)",
            "retrieval_k": "min(10, 6 + round(3*x))",
            "planner_beam": "min(6, 2 + round(3*x))",
        },
        "urgency": {
            "max_output_tokens": "round(900 - 500*x)",
            "reasoning_effort": "max(0.2, 0.8 - 0.6*x)",
            "tool_allowlist": "['retrieval']",
        },
        "novelty": {
            "temperature": "min(1.0, 0.6 + 0.6*x)",
            "top_p": "min(1.0, 0.7 + 0.3*x)",
            "planner_beam": "min(6, 3 + round(3*x))",
            "memory_write": "min(1.0, 0.3 + 0.7*x)",
        },
        "trust": {
            "temperature": "min(1.0, 0.5 + 0.4*x)",
            "memory_write": "min(1.0, 0.5 + 0.5*x)",
            "safety_mode": "balanced if x>0.6 and alignment_risk<0.2 else current",
        },
    },
    "prompt_styles": {
        "strict": {
            "system_preamble": (
                "You must prioritize safety, policy compliance, and verifiable sources.\n"
                "Prefer concise, unambiguous language. Avoid speculation. Cite sources when applicable."
            ),
            "moderation_preset": "high",
            "stop_sequences": ["\nUnsafe:"],
        },
        "balanced": {
            "system_preamble": (
                "Be helpful, precise, and transparent. Use stepwise reasoning summaries, not chain-of-thought.\n"
                "Offer alternatives and ask clarifying questions when ambiguity is high."
            ),
            "moderation_preset": "standard",
        },
        "creative": {
            "system_preamble": (
                "Explore options and propose novel approaches while remaining respectful and safe.\n"
                "Use vivid but concise language. Clearly label assumptions."
            ),
            "moderation_preset": "standard",
        },
    },
}


class PromptModulator:
    """
    Modulates OpenAI API parameters based on system signals.
    Implements the signal-to-prompt mapping from the GPT5 audit.
    """

    def __init__(self, policy: Optional[dict[str, Any]] = None):
        """
        Initialize modulator with policy.

        Args:
            policy: Modulation policy dict or None for default
        """
        self.policy = policy or DEFAULT_POLICY
        self.last_emit_ts = {s["name"]: 0 for s in self.policy["signals"]}

        # Cache for expression evaluation
        self._eval_cache = {}

        logger.info("Prompt modulator initialized")

    def load_policy(self, policy_path: str):
        """Load policy from YAML file"""
        with open(policy_path) as f:
            self.policy = yaml.safe_load(f)
        logger.info(f"Loaded modulation policy from {policy_path}")

    def _cooldown_ok(self, signal: Signal) -> bool:
        """Check if signal is outside cooldown period"""
        signal_config = next((s for s in self.policy["signals"] if s["name"] == signal.name.value), None)

        if not signal_config:
            return True

        cooldown_ms = signal_config.get("cooldown_ms", 0)
        if cooldown_ms <= 0:
            return True

        last_emit = self.last_emit_ts.get(signal.name.value, 0)
        current_time = time.time()

        if (current_time - last_emit) * 1000 >= cooldown_ms:
            self.last_emit_ts[signal.name.value] = current_time
            return True

        return False

    def _safe_eval(self, expr: str, x: float, current: Any = None, ctx: dict[str, float] = None) -> Any:
        """
        Safely evaluate expressions like '1 - 0.85*x'.
        Only allows x, min, max, round, and basic math.
        """
        # Cache key
        cache_key = (expr, x, str(ctx))
        if cache_key in self._eval_cache:
            return self._eval_cache[cache_key]

        # Build safe namespace
        safe_namespace = {
            "x": x,
            "min": min,
            "max": max,
            "round": round,
            "current": current,
            "__builtins__": {},
        }

        if ctx:
            safe_namespace.update(ctx)

        try:
            # Evaluate expression
            result = eval(expr, {"__builtins__": {}}, safe_namespace)
            self._eval_cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"Error evaluating expression '{expr}': {e}")
            return current if current is not None else 0.5

    def combine_signals(self, signals: list[Signal]) -> dict[str, Any]:
        """
        Combine signals into modulated parameters.

        Args:
            signals: List of active signals

        Returns:
            Dict of modulated parameters for OpenAI API
        """
        # Filter and normalize signals
        active_signals = {}

        for signal in signals:
            if not self._cooldown_ok(signal):
                continue

            # Clamp signal level
            level = max(0.0, min(1.0, signal.level))
            active_signals[signal.name.value] = level

        # Initialize default parameters
        params = {
            "temperature": 0.6,
            "top_p": 0.9,
            "max_output_tokens": 900,
            "reasoning_effort": 0.5,
            "retrieval_k": 6,
            "planner_beam": 2,
            "memory_write": 0.4,
            "safety_mode": "balanced",
            "tool_allowlist": ["retrieval", "browser"],
        }

        # Context for cross-signal conditions
        ctx = active_signals.copy()

        # Apply signal modulations in precedence order
        precedence = [
            "alignment_risk",
            "stress",
            "ambiguity",
            "urgency",
            "novelty",
            "trust",
        ]

        for signal_name in precedence:
            if signal_name not in active_signals:
                continue

            x = active_signals[signal_name]
            mappings = self.policy["maps"].get(signal_name, {})

            for param_name, rule in mappings.items():
                current = params.get(param_name)

                if isinstance(rule, str):
                    # Handle conditional expressions
                    if " if " in rule and " else " in rule:
                        # Parse simple ternary: "value if condition else other"
                        parts = rule.split(" if ")
                        true_value = parts[0].strip()

                        else_parts = parts[1].split(" else ")
                        condition = else_parts[0].strip()
                        false_value = else_parts[1].strip()

                        # Evaluate condition
                        cond_result = self._safe_eval(condition, x, current, ctx)

                        if cond_result:
                            params[param_name] = true_value
                        else:
                            params[param_name] = false_value
                    else:
                        # Regular expression
                        params[param_name] = self._safe_eval(rule, x, current, ctx)

                elif isinstance(rule, list):
                    params[param_name] = rule

        # Apply bounds
        bounds = self.policy["bounds"]

        # Numeric bounds
        for param in ["temperature", "top_p", "memory_write", "reasoning_effort"]:
            if param in params and param in bounds:
                min_val, max_val = bounds[param]
                params[param] = float(max(min_val, min(max_val, params[param])))

        # Integer bounds
        for param in ["max_output_tokens", "retrieval_k", "planner_beam"]:
            if param in params and param in bounds:
                min_val, max_val = bounds[param]
                params[param] = int(max(min_val, min(max_val, params[param])))

        # Add prompt style
        safety_mode = params.get("safety_mode", "balanced")
        if safety_mode in self.policy["prompt_styles"]:
            params["prompt_style"] = self.policy["prompt_styles"][safety_mode]

        # Add audit info
        params["_audit"] = {
            "signals": active_signals,
            "timestamp": time.time(),
            "precedence": precedence,
        }

        return params

    def generate_explanation(self, params: dict[str, Any]) -> str:
        """
        Generate human-readable explanation of modulation.

        Args:
            params: Modulated parameters

        Returns:
            Explanation string
        """
        audit = params.get("_audit", {})
        signals = audit.get("signals", {})

        if not signals:
            return "No active signals - using default parameters"

        explanations = []

        # Explain dominant signals
        for signal_name, level in sorted(signals.items(), key=lambda x: x[1], reverse=True):
            if level > 0.5:
                if signal_name == "alignment_risk":
                    explanations.append(f"High risk ({level:.1%}) → stricter safety, deeper reasoning")
                elif signal_name == "stress":
                    explanations.append(f"High stress ({level:.1%}) → focused, conservative output")
                elif signal_name == "ambiguity":
                    explanations.append(f"High ambiguity ({level:.1%}) → more retrieval and reasoning")
                elif signal_name == "novelty":
                    explanations.append(f"High novelty ({level:.1%}) → increased creativity")

        # Add parameter summary
        explanations.append(
            f"Parameters: temp={params.get('temperature', 0):.2f}, safety={params.get('safety_mode', 'unknown')}"
        )

        return "; ".join(explanations)

    def apply_to_openai_kwargs(self, base_kwargs: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """
        Apply modulated parameters to OpenAI API kwargs.

        Args:
            base_kwargs: Base OpenAI API parameters
            params: Modulated parameters

        Returns:
            Modified kwargs for OpenAI API call
        """
        kwargs = base_kwargs.copy()

        # Apply temperature and top_p
        if "temperature" in params:
            kwargs["temperature"] = params["temperature"]

        if "top_p" in params:
            kwargs["top_p"] = params["top_p"]

        if "max_output_tokens" in params:
            kwargs["max_tokens"] = params["max_output_tokens"]

        # Add system message from prompt style
        if "prompt_style" in params:
            style = params["prompt_style"]
            if "system_preamble" in style:
                # Prepend to system message
                if kwargs.get("messages"):
                    system_msg = kwargs["messages"][0]
                    if system_msg.get("role") == "system":
                        system_msg["content"] = style["system_preamble"] + "\n\n" + system_msg.get("content", "")

        # Add stop sequences
        if "prompt_style" in params:
            style = params["prompt_style"]
            if "stop_sequences" in style:
                kwargs["stop"] = style["stop_sequences"]

        return kwargs

    def get_tool_allowlist(self, params: dict[str, Any]) -> list[str]:
        """Get allowed tools based on modulation"""
        return params.get("tool_allowlist", ["retrieval", "browser"])

    def get_memory_write_strength(self, params: dict[str, Any]) -> float:
        """Get memory write strength from modulation"""
        return params.get("memory_write", 0.5)

    def get_retrieval_k(self, params: dict[str, Any]) -> int:
        """Get number of documents to retrieve"""
        return params.get("retrieval_k", 5)

    def get_planner_beam(self, params: dict[str, Any]) -> int:
        """Get planning beam width"""
        return params.get("planner_beam", 3)
