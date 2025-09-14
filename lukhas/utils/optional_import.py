# lukhas/utils/optional_import.py
from importlib import import_module
from types import ModuleType
from typing import Optional

def optional_import(name: str) -> Optional[ModuleType]:
    try:
        return import_module(name)
    except Exception:
        return None
