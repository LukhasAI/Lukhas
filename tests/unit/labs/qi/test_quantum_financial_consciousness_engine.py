"""Unit tests for the labs quantum financial consciousness engine components."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest


def _find_repo_root(start: Path) -> Path:
    for parent in start.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Repository root not found")


ROOT_PATH = _find_repo_root(Path(__file__).resolve())


def _load_module(module_name: str, relative_path: str):
    module_path = ROOT_PATH / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_module = _load_module(
    "labs.core.qi_financial.quantum_financial_consciousness_engine",
    "labs/core/qi_financial/quantum_financial_consciousness_engine.py",
)
ConsciousnessTokenProtocol = _module.ConsciousnessTokenProtocol


def test_issue_tokens_is_deterministic_for_same_amount() -> None:
    protocol = ConsciousnessTokenProtocol()

    first_token = protocol.issue_tokens(12.5)
    second_token = protocol.issue_tokens(12.5)

    assert first_token == second_token


def test_issue_tokens_scales_with_amount() -> None:
    protocol = ConsciousnessTokenProtocol()

    lower = protocol.issue_tokens(2.0)
    higher = protocol.issue_tokens(42.0)

    assert higher.consciousness_value > lower.consciousness_value
    assert higher.token_id != lower.token_id


@pytest.mark.parametrize("amount", [0.0, -5.0])
def test_issue_tokens_handles_non_positive_amount(amount: float) -> None:
    protocol = ConsciousnessTokenProtocol()

    token = protocol.issue_tokens(amount)

    assert token.consciousness_value == pytest.approx(0.0)
    assert token.resonance_band == "dormant"


def test_issue_tokens_resonance_thresholds_progress_monotonically() -> None:
    protocol = ConsciousnessTokenProtocol()

    dormant = protocol.issue_tokens(0.0)
    emergent = protocol.issue_tokens(1.0)
    harmonic = protocol.issue_tokens(math.e**1.0 - 1)
    radiant = protocol.issue_tokens(math.exp(2.5) - 1)

    assert dormant.resonance_band == "dormant"
    assert emergent.resonance_band == "emergent"
    assert harmonic.resonance_band == "harmonic"
    assert radiant.resonance_band == "radiant"
