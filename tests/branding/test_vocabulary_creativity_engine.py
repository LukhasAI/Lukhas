"""Tests for the VocabularyCreativityEngine symbolic mappings."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


def _load_vocabulary_module() -> ModuleType:
    module_path = Path("branding/vocabularies/vocabulary_creativity_engine.py")

    if "_bridgeutils" not in sys.modules:
        bridgeutils = ModuleType("_bridgeutils")

        def bridge_from_candidates(*_args: Any, **_kwargs: Any) -> tuple[tuple[str, ...], dict[str, Any]]:
            return (), {}

        bridgeutils.bridge_from_candidates = bridge_from_candidates  # type: ignore[attr-defined]
        sys.modules["_bridgeutils"] = bridgeutils

    if "symbolic" not in sys.modules:
        symbolic_pkg = ModuleType("symbolic")
        symbolic_pkg.__path__ = []  # type: ignore[attr-defined]
        sys.modules["symbolic"] = symbolic_pkg

    if "branding" not in sys.modules:
        branding_pkg = ModuleType("branding")
        branding_pkg.__path__ = []  # type: ignore[attr-defined]
        sys.modules["branding"] = branding_pkg

    if "branding.core" not in sys.modules:
        branding_core = ModuleType("branding.core")

        class BrandingAnalysisType(str):
            """Stub analysis type for branding namespace."""

        class BrandingVisionProvider(str):
            """Stub provider type for branding namespace."""

        branding_core.AnalysisType = BrandingAnalysisType  # type: ignore[attr-defined]
        branding_core.VisionProvider = BrandingVisionProvider  # type: ignore[attr-defined]
        sys.modules["branding.core"] = branding_core

    if "symbolic.core" not in sys.modules:
        symbolic_core = ModuleType("symbolic.core")

        class AnalysisType(str):
            """Stub enum-like type for analysis markers."""

        class VisionProvider(str):
            """Stub enum-like type for provider markers."""

        symbolic_core.AnalysisType = AnalysisType  # type: ignore[attr-defined]
        symbolic_core.VisionProvider = VisionProvider  # type: ignore[attr-defined]
        sys.modules["symbolic.core"] = symbolic_core

    if "symbolic.vocabularies" not in sys.modules:
        symbolic_vocab_pkg = ModuleType("symbolic.vocabularies")
        symbolic_vocab_pkg.__path__ = []  # type: ignore[attr-defined]
        sys.modules["symbolic.vocabularies"] = symbolic_vocab_pkg

    if "symbolic.vocabularies.vision_vocabulary" not in sys.modules:
        vision_module = ModuleType("symbolic.vocabularies.vision_vocabulary")

        class VisionSymbolicVocabulary:  # pragma: no cover - stub for tests
            pass

        vision_module.VisionSymbolicVocabulary = VisionSymbolicVocabulary  # type: ignore[attr-defined]
        sys.modules["symbolic.vocabularies.vision_vocabulary"] = vision_module
    spec = importlib.util.spec_from_file_location("branding.vocabularies.vocabulary_creativity_engine", module_path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive guard
        raise RuntimeError("Unable to load vocabulary creativity engine module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _create_engine() -> Any:
    module = _load_vocabulary_module()
    return module.VocabularyCreativityEngine()


def test_map_detected_objects_to_symbols_produces_unique_symbols() -> None:
    engine = _create_engine()
    detected = ["House", "tree", "vehicle", "unknown"]

    symbols = engine.map_detected_objects_to_symbols(detected)

    assert symbols  # at least one symbol returned
    assert "🏠" in symbols
    assert "🌳" in symbols
    assert len(symbols) == len(set(symbols))


def test_map_detected_objects_to_symbols_handles_empty_values() -> None:
    engine = _create_engine()

    symbols = engine.map_detected_objects_to_symbols(["   ", ""])

    assert symbols == []
