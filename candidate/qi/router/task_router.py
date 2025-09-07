# path: qi/router/task_router.py
from __future__ import annotations

import argparse
import json
import os
from typing import Any

import yaml  # pip install pyyaml

# Reuse your confidence-based planner
from qi.router.confidence_router import ConfidenceRouter
import streamlit as st
from consciousness.qi import qi

PRESETS_PATH_ENV = "LUKHAS_ROUTER_PRESETS"
DEFAULT_PRESETS_PATH = os.path.join("qi", "router", "presets.yaml")


class ConfigError(Exception):
    pass


def _load_yaml(path: str) -> dict[str, Any]:
    if not os.path.exists(path):
        raise ConfigError(f"Preset file not found: {path}")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ConfigError("presets.yaml must be a YAML mapping at the top level.")
    return data


def _validate(cfg: dict[str, Any]) -> None:
    allowed_keys = {"defaults", "tasks", "models"}
    unknown = set(cfg.keys()) - allowed_keys
    if unknown:
        raise ConfigError(f"Unknown top-level keys in presets: {sorted(unknown)}")

    def _check_plan(plan: dict[str, Any], ctx: str):
        # soft schema
        for k in plan:
            if k not in {
                "gen_tokens",
                "retrieval",
                "passes",
                "temperature",
                "tools",
                "retrieval_k",
                "max_input_tokens",
                "allow_models",
                "deny_models",
                "notes",
                "max_output_tokens",
                "min_conf_for_fast",
                "force_path",
                "cap_tokens",
                "cap_latency_ms",
            }:
                raise ConfigError(f"Unknown key '{k}' in {ctx}")

        if "retrieval" in plan and not isinstance(plan["retrieval"], bool):
            raise ConfigError(f"{ctx}.retrieval must be bool")
        if "passes" in plan and not isinstance(plan["passes"], int):
            raise ConfigError(f"{ctx}.passes must be int")
        if "temperature" in plan and not isinstance(plan["temperature"], (int, float)):
            raise ConfigError(f"{ctx}.temperature must be number")
        if "tools" in plan and not isinstance(plan["tools"], (list, tuple)):
            raise ConfigError(f"{ctx}.tools must be list")
        if "allow_models" in plan and not isinstance(plan["allow_models"], (list, tuple)):
            raise ConfigError(f"{ctx}.allow_models must be list")
        if "deny_models" in plan and not isinstance(plan["deny_models"], (list, tuple)):
            raise ConfigError(f"{ctx}.deny_models must be list")

    if "defaults" in cfg and isinstance(cfg["defaults"], dict):
        _check_plan(cfg["defaults"], "defaults")

    tasks = cfg.get("tasks", {}) or {}
    if not isinstance(tasks, dict):
        raise ConfigError("tasks must be a mapping.")
    for name, plan in tasks.items():
        if not isinstance(plan, dict):
            raise ConfigError(f"tasks.{name} must be a mapping.")
        _check_plan(plan, f"tasks.{name}")


class TaskRouter:
    """
    Merges task-specific YAML presets with confidence-aware routing.
    Resolution order for the final plan:
      1) ConfidenceRouter base (fast/normal/deliberate/handoff)
      2) 'defaults' from YAML (applies to all tasks)
      3) Task-specific overrides from YAML (applies to the named task)
    Then applies safety caps (cap_tokens, cap_latency_ms) if present.
    """

    def __init__(
        self,
        presets_path: str | None = None,
        conf_thresholds: tuple[float, float, float] = (0.8, 0.6, 0.4),
    ):
        self.presets_path = os.environ.get(PRESETS_PATH_ENV) or presets_path or DEFAULT_PRESETS_PATH
        self.cfg = _load_yaml(self.presets_path)
        _validate(self.cfg)
        self.conf_router = ConfidenceRouter(conf_thresholds)

    def reload(self) -> None:
        self.cfg = _load_yaml(self.presets_path)
        _validate(self.cfg)

    def plan(
        self,
        *,
        task: str,
        calibrated_conf: float,
        last_path: str | None = None,
        model_id: str | None = None,
        input_tokens_est: int | None = None,
    ) -> dict[str, Any]:
        # 1) base route from confidence
        base = self.conf_router.decide(
            calibrated_conf=calibrated_conf, last_path=last_path
        )  # has: path, gen_tokens, retrieval, passes, temperature, confidence

        # 2) apply global defaults
        out = dict(base)
        defaults = self.cfg.get("defaults", {}) or {}
        out.update(defaults)

        # 3) apply task overrides
        t_cfg = (self.cfg.get("tasks", {}) or {}).get(task, {})
        out.update(t_cfg)

        # 4) optional model allow/deny enforcement (advisory here; you can hard-enforce in caller)
        if model_id:
            allow = out.get("allow_models")
            deny = out.get("deny_models")
            if allow and model_id not in allow:
                out.setdefault("warnings", []).append(f"model '{model_id}' not in allow_models")
            if deny and model_id in deny:
                out.setdefault("warnings", []).append(f"model '{model_id}' is in deny_models")

        # 5) caps & guards
        cap_tokens = out.pop("cap_tokens", None)
        if cap_tokens is not None and isinstance(cap_tokens, int) and out.get("gen_tokens", 0) > cap_tokens:
            out["gen_tokens"] = cap_tokens
            out.setdefault("notes", "")
            out["notes"] += " | capped gen_tokens"

        cap_latency = out.pop("cap_latency_ms", None)
        if cap_latency is not None and isinstance(cap_latency, int):
            # This is advisory — caller should check with Budgeter for precise latency caps
            out.setdefault("notes", "")
            out["notes"] += " | latency cap advisory"

        # 6) min confidence fast path override
        min_fast = out.pop("min_conf_for_fast", None)
        if min_fast is not None and out.get("path") == "fast" and calibrated_conf < float(min_fast):
            # drop to normal settings but keep other overrides
            fallback = self.conf_router.decide(calibrated_conf=self.conf_router.t_norm + 0.001)
            # keep temperature from overrides if present
            for k in ("gen_tokens", "retrieval", "passes", "temperature"):
                out[k] = out.get(k, fallback.get(k, out.get(k)))
            out["path"] = "normal"
            out.setdefault("notes", "")
            out["notes"] += " | demoted from fast by min_conf_for_fast"

        # 7) force_path if explicitly declared
        force = out.pop("force_path", None)
        if force in ("fast", "normal", "deliberate", "handoff"):
            forced = self.conf_router.decide(calibrated_conf=calibrated_conf)
            forced.update({"path": force})
            # merge with our overrides (keeping our knobs)
            for k in (
                "gen_tokens",
                "retrieval",
                "passes",
                "temperature",
                "tools",
                "retrieval_k",
                "max_input_tokens",
                "max_output_tokens",
            ):
                if k in out:
                    forced[k] = out[k]
            out = forced
            out.setdefault("notes", "")
            out["notes"] += " | force_path applied"

        # 8) include some context back for observability
        out["task"] = task
        out["calibrated_confidence"] = round(float(calibrated_conf), 4)
        if model_id:
            out["model_id"] = model_id
        if input_tokens_est is not None:
            out["input_tokens_est"] = int(input_tokens_est)

        return out


# ---------------- CLI ----------------
def main():
    ap = argparse.ArgumentParser(description="Task-specific router (YAML presets + confidence-aware)")
    ap.add_argument(
        "--presets",
        help=f"Path to presets YAML (default: {DEFAULT_PRESETS_PATH} or ${PRESETS_PATH_ENV})",
    )
    ap.add_argument("--task", required=True)
    ap.add_argument("--conf", type=float, required=True, help="Calibrated confidence (0-1)")
    ap.add_argument("--last-path", help="Previous path (fast|normal|deliberate|handoff)")
    ap.add_argument("--model-id")
    ap.add_argument("--input-tokens", type=int)
    args = ap.parse_args()

    r = TaskRouter(presets_path=args.presets)
    plan = r.plan(
        task=args.task,
        calibrated_conf=args.conf,
        last_path=args.last_path,
        model_id=args.model_id,
        input_tokens_est=args.input_tokens,
    )
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
