from __future__ import annotations
import importlib
from typing import Any, Callable


class ProviderRegistry:
    """Resolve and instantiate pluggable providers via string paths.

    The resolver callable should return a fully-qualified factory string like
    "some_pkg.some_module:factory". We don't import `labs.*` here.
    """

    def __init__(self, resolver: Callable[[str], str]):
        self._resolver = resolver

    def get_openai(self):
        fq = self._resolver("openai.provider")
        module_path, _, factory_name = fq.partition(":")
        if not module_path:
            raise RuntimeError("Invalid provider path from resolver")
        mod = importlib.import_module(module_path)
        factory = getattr(mod, factory_name or "provide")
        return factory()
