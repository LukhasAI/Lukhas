from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass
from typing import Any

STATE = os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
BUDGET_FILE = os.path.join(STATE, "budget_state.json")
CONF_FILE = os.path.join(STATE, "budget_config.json")


@dataclass
class BudgetConfig:
    default_token_cap: int = 200_000  # per-run soft cap
    default_latency_ms: int = 10_000
    user_overrides: dict[str, dict[str, Any]] = None  # {user_id: {"token_cap":..., "latency_ms":...}}
    task_overrides: dict[str, dict[str, Any]] = None  # {task: {...}}
    model_costs: dict[str, dict[str, float]] = None  # {model: {"tok_per_char": 0.35, "lat_ms_per_tok": 0.02}}

    def to_dict(self):
        return {
            "default_token_cap": self.default_token_cap,
            "default_latency_ms": self.default_latency_ms,
            "user_overrides": self.user_overrides or {},
            "task_overrides": self.task_overrides or {},
            "model_costs": self.model_costs or {"default": {"tok_per_char": 0.35, "lat_ms_per_tok": 0.02}},
        }


def _load_json(path: str, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def _save_json(path: str, obj: Any):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


class Budgeter:
    """
    Lightweight cost governor. Tracks rolling usage and estimates planned cost.
    - plan(text, model, target_tokens) -> dict with tokens_planned, latency_est_ms
    - check(user, task, plan) -> dict with 'ok' and 'reason' if exceeded
    - commit(user, task, actual_tokens, latency_ms) -> record usage
    """

    def __init__(self):
        self.conf = BudgetConfig(**_load_json(CONF_FILE, {}))
        self.state = _load_json(BUDGET_FILE, {"runs": []})  # append-only ring in real life

    def save(self):
        _save_json(CONF_FILE, self.conf.to_dict())
        _save_json(BUDGET_FILE, self.state)

    # ---- planning ----
    def plan(
        self,
        *,
        text: str = "",
        model: str = "default",
        target_tokens: int | None = None,
    ) -> dict[str, Any]:
        # Ensure model_costs has default
        if not self.conf.model_costs:
            self.conf.model_costs = {"default": {"tok_per_char": 0.35, "lat_ms_per_tok": 0.02}}
        costs = self.conf.model_costs.get(model) or self.conf.model_costs.get(
            "default", {"tok_per_char": 0.35, "lat_ms_per_tok": 0.02}
        )
        tok_per_char = float(costs.get("tok_per_char", 0.35))
        lat_per_tok = float(costs.get("lat_ms_per_tok", 0.02))

        input_tok = math.ceil(len(text) * tok_per_char)
        gen_tok = int(target_tokens or max(256, input_tok // 2))
        tokens_planned = input_tok + gen_tok
        latency_ms = int(tokens_planned * lat_per_tok)

        energy_wh = (tokens_planned / 1000.0) * float(costs.get("wh_per_ktok", 0.5))
        return {
            "tokens_planned": tokens_planned,
            "latency_est_ms": latency_ms,
            "energy_wh": energy_wh,
            "input_tokens": input_tok,
            "gen_tokens": gen_tok,
            "model": model,
        }

    # ---- limits ----
    def _caps(self, user_id: str | None, task: str | None) -> dict[str, int]:
        cap = self.conf.default_token_cap
        lat = self.conf.default_latency_ms
        if task and (self.conf.task_overrides or {}).get(task):
            t = self.conf.task_overrides[task]
            cap = int(t.get("token_cap", cap))
            lat = int(t.get("latency_ms", lat))
        if user_id and (self.conf.user_overrides or {}).get(user_id):
            u = self.conf.user_overrides[user_id]
            cap = int(u.get("token_cap", cap))
            lat = int(u.get("latency_ms", lat))
        return {"token_cap": cap, "latency_ms": lat}

    def check(self, *, user_id: str | None, task: str | None, plan: dict[str, Any]) -> dict[str, Any]:
        caps = self._caps(user_id, task)
        reasons = []
        if plan["tokens_planned"] > caps["token_cap"]:
            reasons.append(f"tokens_planned {plan['tokens_planned']} > cap {caps['token_cap']}")
        if plan["latency_est_ms"] > caps["latency_ms"]:
            reasons.append(f"latency_est_ms {plan['latency_est_ms']} > cap {caps['latency_ms']}")
        return {"ok": not reasons, "reasons": reasons, "caps": caps}

    # ---- accounting ----
    def commit(
        self,
        *,
        user_id: str | None,
        task: str | None,
        actual_tokens: int,
        latency_ms: int,
        meta: dict[str, Any] | None = None,
    ):
        self.state["runs"].append(
            {
                "ts": time.time(),
                "user": user_id,
                "task": task,
                "tokens": int(actual_tokens),
                "latency_ms": int(latency_ms),
                "meta": meta or {},
            }
        )
        # in a real system, consider trimming old entries or summarising
        self.save()


# CLI convenience
if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Lukhas Budget Governor")
    ap.add_argument("--plan-text", default="")
    ap.add_argument("--model", default="default")
    ap.add_argument("--target-tokens", type=int)
    ap.add_argument("--user")
    ap.add_argument("--task")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--actual-tokens", type=int, default=0)
    ap.add_argument("--latency-ms", type=int, default=0)
    args = ap.parse_args()

    b = Budgeter()
    plan = b.plan(text=args.plan_text, model=args.model, target_tokens=args.target_tokens)
    verdict = b.check(user_id=args.user, task=args.task, plan=plan)
    out = {"plan": plan, "verdict": verdict}
    print(json.dumps(out, indent=2))
    if args.commit:
        b.commit(
            user_id=args.user,
            task=args.task,
            actual_tokens=args.actual_tokens or plan["tokens_planned"],
            latency_ms=args.latency_ms or plan["latency_est_ms"],
        )
        print("Committed usage.")
