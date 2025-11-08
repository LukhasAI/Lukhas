"""Utilities for importing the production LLM wrapper modules in tests."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

_MODULE_NAME = "labs.bridge.llm_wrappers.openai_modulated_service"
_MODULE_PATH = (
    Path(__file__).resolve().parents[5]
    / "labs"
    / "bridge"
    / "llm_wrappers"
    / "openai_modulated_service.py"
)


def load_openai_modulated_service() -> ModuleType:
    """Load the OpenAI modulated service module from the repository source."""
    if _MODULE_NAME in sys.modules:
        return sys.modules[_MODULE_NAME]

    spec = importlib.util.spec_from_file_location(_MODULE_NAME, _MODULE_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(
            f"Could not load {_MODULE_NAME} from {_MODULE_PATH}"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module
