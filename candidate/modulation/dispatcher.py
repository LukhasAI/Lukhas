import time
from dataclasses import dataclass
from typing import Any, Optional

import yaml

from lukhas.flags import is_enabled

PRECEDENCE = ["alignment_risk", "stress", "ambiguity", "novelty"]


@dataclass
class Signal:
    name: str
    level: float  # 0..1
    ttl_ms: int
    source: str
    audit_id: str
    ts: float = time.time()


class Modulator:
    def __init__(self, policy_path: str = "modulation_policy.yaml"):
        with open(policy_path) as f:
            self.policy = yaml.safe_load(f)
        self.last_emit_ts = {s["name"]: 0 for s in self.policy["signals"]}

    def _cooldown_ok(self, sig: Signal) -> bool:
        cd = next(s["cooldown_ms"] for s in self.policy["signals"] if s["name"] == sig.name)
        return (sig.ts - self.last_emit_ts[sig.name]) * 1000 >= cd

    def _eval(
        self,
        expr: str,
        x: float,
        current: Any = None,
        ctx: Optional[dict[str, float]] = None,
    ):
        # safe mini-evaluator: supports x, min, max, round, numbers, simple ops,
        # and 'a if cond else b'
        local = {
            "x": x,
            "min": min,
            "max": max,
            "round": round,
            "__builtins__": {},
        }
        if ctx:
            local.update(ctx)
        if " if " in expr and " else " in expr:
            cond = expr.split(" if ")[1].split(" else ")[0]
            true_v = expr.split(" if ")[0].strip()
            false_v = expr.split(" else ")[1].strip()
            val = eval(cond, {}, local)
            return true_v if val else false_v
        return eval(expr, {}, local)

    def combine(self, incoming: list[Signal]) -> dict[str, Any]:
        # 1) cooldown + clamp
        signals: dict[str, float] = {}
        now = time.time()
        for sig in incoming:
            if not self._cooldown_ok(sig):
                continue
            self.last_emit_ts[sig.name] = int(now)
            signals[sig.name] = max(0.0, min(1.0, float(sig.level)))

        # 2) defaults
        # Check FLAG_STRICT_DEFAULT to force strict safety mode
        default_safety_mode = "strict" if is_enabled("strict_default") else "balanced"

        params = {
            "temperature": 0.6,
            "top_p": 0.9,
            "max_output_tokens": 900,
            "reasoning_effort": 0.5,
            "retrieval_k": 6,
            "planner_beam": 2,
            "memory_write": 0.4,
            "safety_mode": default_safety_mode,
            "tool_allowlist": ["retrieval", "browser"],
        }
        ctx = signals.copy()

        # 3) precedence mapping
        for name in sorted(signals.keys(), key=lambda n: PRECEDENCE.index(n)):
            x = signals[name]
            mapping = self.policy["maps"].get(name, {})
            for k, rule in mapping.items():
                current = params.get(k)
                if isinstance(rule, str):
                    params[k] = self._eval(rule, x, current, ctx)
                elif isinstance(rule, list):
                    params[k] = rule

        # 4) bounds
        b = self.policy["bounds"]

        def clamp(v, lo, hi, cast=None):
            v2 = max(lo, min(hi, v))
            return cast(v2) if cast else v2

        params["temperature"] = clamp(float(params["temperature"]), *b["temperature"])
        params["top_p"] = clamp(float(params["top_p"]), *b["top_p"])
        params["max_output_tokens"] = int(
            clamp(int(params["max_output_tokens"]), *b["max_output_tokens"])
        )
        params["retrieval_k"] = int(clamp(int(params["retrieval_k"]), *b["retrieval_k"]))
        params["planner_beam"] = int(clamp(int(params["planner_beam"]), *b["planner_beam"]))
        params["memory_write"] = clamp(float(params["memory_write"]), *b["memory_write"])

        # 5) prompt style
        style = params["safety_mode"]
        params["prompt_style"] = self.policy["prompt_styles"][
            style if style in self.policy["prompt_styles"] else "balanced"
        ]
        return params
