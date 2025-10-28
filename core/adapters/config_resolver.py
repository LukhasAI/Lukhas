from __future__ import annotations
from typing import Callable
import pathlib


def make_resolver(cfg_path: str = "config/integrations.yml") -> Callable[[str], str]:
    """Return a resolver that maps keys to configured provider strings.

    Defer heavy imports (yaml) until the function runs so import-time
    dependency graph stays small and lane-safe.
    """

    def _load():
        try:
            import yaml
        except Exception:
            # If PyYAML isn't available, raise a clear error at runtime.
            raise

        text = pathlib.Path(cfg_path).read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        return data or {}

    data = None

    def _resolve(key: str) -> str:
        nonlocal data
        if data is None:
            data = _load()
        if key == "openai.provider":
            return data.get("openai", {}).get("provider", "")
        raise KeyError(key)

    return _resolve
