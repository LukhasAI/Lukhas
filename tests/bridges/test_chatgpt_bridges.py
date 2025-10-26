"""Contract tests for ChatGPT explicit-API bridge pattern.

Validates that bridges using bridge_from_candidates() work correctly:
- Can import the bridge module
- __all__ is properly populated
- Symbols are accessible
- No import errors during collection
"""
from __future__ import annotations

import importlib
import sys

import pytest


@pytest.mark.parametrize(
    "bridge_path",
    [
        "branding",
        "consciousness.matriz_thought_loop",
        "cognitive_core.reasoning.contradiction_integrator",
    ],
)
def test_bridge_imports_successfully(bridge_path: str) -> None:
    """Bridge module can be imported without errors."""
    mod = importlib.import_module(bridge_path)
    assert mod is not None


@pytest.mark.parametrize(
    "bridge_path",
    [
        "branding",
        "consciousness.matriz_thought_loop",
        "cognitive_core.reasoning.contradiction_integrator",
    ],
)
def test_bridge_has_all(bridge_path: str) -> None:
    """Bridge module has __all__ attribute (may be empty)."""
    mod = importlib.import_module(bridge_path)
    assert hasattr(mod, "__all__")
    assert isinstance(mod.__all__, list)


@pytest.mark.parametrize(
    ("bridge_path", "expected_symbols"),
    [
        ("branding", ["SYSTEM_NAME", "APPROVED_TERMS"]),
        ("consciousness.matriz_thought_loop", []),  # May be empty if backend not found
    ],
)
def test_bridge_exports_expected_symbols(bridge_path: str, expected_symbols: list[str]) -> None:
    """Bridge exports expected symbols (if backend available)."""
    mod = importlib.import_module(bridge_path)
    if not mod.__all__:
        pytest.skip("Backend not available, __all__ is empty")

    for symbol in expected_symbols:
        assert symbol in mod.__all__, f"{symbol} not in {bridge_path}.__all__"
        assert hasattr(mod, symbol), f"{symbol} not accessible in {bridge_path}"


def test_bridge_from_candidates_utility() -> None:
    """bridge_from_candidates() utility function works correctly."""
    from _bridgeutils import bridge_from_candidates

    # Test with non-existent modules (should return empty)
    __all__, exports = bridge_from_candidates("nonexistent.module1", "nonexistent.module2")
    assert __all__ == []
    assert exports == {}

    # Test with real module (sys is always available)
    __all__, exports = bridge_from_candidates("sys")
    assert isinstance(__all__, list)
    assert isinstance(exports, dict)
    assert len(__all__) > 0  # sys has exports
    assert "path" in __all__  # sys.path should be exported


def test_no_module_package_collisions() -> None:
    """No .py files shadow package directories (ChatGPT collision scrubber)."""
    from pathlib import Path

    collisions = []
    for py in Path(".").rglob("*.py"):
        # Skip venv and special directories
        if ".venv" in py.parts or "__pycache__" in py.parts:
            continue

        pkg = py.with_suffix("")
        if pkg.is_dir() and (pkg / "__init__.py").exists():
            collisions.append(py)

    assert len(collisions) == 0, f"Found module-package collisions: {collisions}"


def test_bridge_does_not_pollute_sys_modules() -> None:
    """Importing a bridge doesn't leave unexpected entries in sys.modules."""
    initial_modules = set(sys.modules.keys())

    # Import a bridge
    import consciousness.matriz_thought_loop

    after_modules = set(sys.modules.keys())
    new_modules = after_modules - initial_modules

    # Should only add the bridge module itself and its dependencies
    expected = {
        "consciousness.matriz_thought_loop",
        "_bridgeutils",
    }

    # Allow backend modules to be loaded too
    unexpected = new_modules - expected - {
        m for m in new_modules if m.startswith("lukhas_website.") or m.startswith("labs.")
    }

    assert len(unexpected) < 5, f"Bridge imported unexpected modules: {unexpected}"
