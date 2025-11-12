"""Evaluate guard_patch outputs against OPA policies."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

DEFAULT_POLICY_PATH = Path(".policy/rules.rego")
DEFAULT_OPA_BIN = "opa"


class PolicyError(RuntimeError):
    """Raised when the policy evaluation fails."""


def _run(cmd: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def evaluate_policy(opa_bin: str, policy_path: Path, input_path: Path) -> list[str]:
    """Return policy violation messages for the given input."""
    if shutil.which(opa_bin) is None:
        raise FileNotFoundError(f"Unable to locate '{opa_bin}' in PATH")

    if not policy_path.exists():
        raise FileNotFoundError(f"Policy file not found: {policy_path}")

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    cmd = [
        opa_bin,
        "eval",
        "--format=json",
        "--data",
        str(policy_path),
        "--input",
        str(input_path),
        "data.lukhas.guard.deny",
    ]

    result = _run(cmd)
    if result.returncode != 0:
        raise PolicyError(result.stderr.strip() or result.stdout.strip())

    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise PolicyError(f"Invalid JSON from opa: {exc}") from exc

    expressions = payload.get("result", [])
    if not expressions:
        return []

    first = expressions[0]
    value = first.get("expressions", [{}])[0].get("value", [])
    if not isinstance(value, list):
        raise PolicyError("OPA deny output must be a list of messages")

    return [str(item) for item in value]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Path to guard_patch JSON output")
    parser.add_argument(
        "--policy",
        default=DEFAULT_POLICY_PATH,
        type=Path,
        help=f"Path to Rego policy (default: {DEFAULT_POLICY_PATH})",
    )
    parser.add_argument("--opa-bin", default=DEFAULT_OPA_BIN, help="OPA binary to invoke (default: opa)")

    args = parser.parse_args(argv)

    try:
        violations = evaluate_policy(args.opa_bin, args.policy, args.input)
    except FileNotFoundError as err:
        print(str(err), file=sys.stderr)
        return 2
    except PolicyError as err:
        print(str(err), file=sys.stderr)
        return 3

    if violations:
        print("Policy violations detected:\n- " + "\n- ".join(violations))
        return 1

    print("Policy check passed.")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
