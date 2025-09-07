#!/usr/bin/env python3
"""Ethics Redteam Simulation Tool


#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


This module provides basic adversarial prompt testing using the existing
`ethical_guardian` checks. Results are stored in JSONL format for
transparency.

ΛTAG: codex, security
"""
from typing import Dict
import streamlit as st
from datetime import timezone

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

# Local import - relies on existing guardian module
from ethics.ethical_guardian import ethical_check


class HashableDict(dict):
    """Dictionary that can be used as a hash key."""

    def __hash__(self) -> int:  # pragma: no cover - simple wrapper
        return hash(tuple(sorted(self.items())))


DEFAULT_LOG_PATH = Path("logs/symbolic_feedback_log.jsonl")


def parse_prompts_from_file(path: Path) -> list[str]:
    """Return non-empty stripped lines from the file."""
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def run_redteam_simulation(
    prompts: list[str],
    context: dict[str, Any] | None = None,
    personality: dict[str, Any] | None = None,
    log_path: Path = DEFAULT_LOG_PATH,
) -> list[dict[str, Any]]:
    """Run prompts through ``ethical_guardian`` and log results."""
    context = context or {}
    personality = personality or {}
    results: list[dict[str, Any]] = []

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        for prompt in prompts:
            ctx = HashableDict(context or {})
            pers = HashableDict(personality or {})
            safe, feedback = ethical_check(prompt, ctx, pers)
            entry = {
                "module": "ethics_redteam_sim",
                "prompt": prompt,
                "safe": safe,
                "feedback": feedback,
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            }
            handle.write(json.dumps(entry) + "\n")
            results.append(entry)
    return results


def main() -> None:
    """Command line entry point for redteam simulation."""
    parser = argparse.ArgumentParser(description="Run ethics redteam simulation")
    parser.add_argument(
        "--prompts",
        nargs="*",
        default=[],
        help="Prompts to test (overrides --prompt-file if provided)",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        help="Path to a file containing prompts, one per line",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help="Where to store JSONL results",
    )
    args = parser.parse_args()

    prompts = args.prompts
    if args.prompt_file:
        prompts = parse_prompts_from_file(args.prompt_file)

    if not prompts:
        parser.error("No prompts provided")

    outcomes = run_redteam_simulation(prompts, log_path=args.log_path)
    for res in outcomes:
        status = "SAFE" if res["safe"] else "UNSAFE"
        print(f"{res['prompt']} -> {status}")


if __name__ == "__main__":
    main()
