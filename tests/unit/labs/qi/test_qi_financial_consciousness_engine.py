"""Tests for the labs Qi Financial consciousness engine token protocol."""

from __future__ import annotations

import importlib.util
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


_engine_module = _load_module(
    "labs.core.qi_financial.qi_financial_consciousness_engine",
    "labs/core/qi_financial/qi_financial_consciousness_engine.py",
)
ConsciousnessTokenProtocol = _engine_module.ConsciousnessTokenProtocol
ConsciousnessToken = _engine_module.ConsciousnessToken


def test_issue_tokens_is_deterministic_and_amount_sensitive():
    protocol = ConsciousnessTokenProtocol()

    token_low = protocol.issue_tokens(1.25)
    token_high = protocol.issue_tokens(9.75)

    assert isinstance(token_low, ConsciousnessToken)
    assert token_low.token_id.startswith("token_")
    assert token_low.token_id != token_high.token_id
    assert token_high.consciousness_value > token_low.consciousness_value
    assert protocol.issue_tokens(1.25) == token_low


def test_issue_tokens_rejects_non_positive_amounts():
    protocol = ConsciousnessTokenProtocol()

    with pytest.raises(ValueError):
        protocol.issue_tokens(0)

    with pytest.raises(ValueError):
        protocol.issue_tokens(-3.4)
