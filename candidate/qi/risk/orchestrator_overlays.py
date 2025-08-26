"""
Risk Orchestrator Overlays
--------------------------
Centralized policy overlay system for LUKHΛS, allowing global, jurisdiction-specific,
and context-specific overrides of risk management settings.

Features:
- Hierarchical YAML overlays (global > jurisdiction > context).
- Hot-reload support for ops teams.
- Schema validation with pydantic.
- Immutable snapshot per TEQ evaluation.
"""

import copy
import threading
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, ValidationError


class OverlaySchema(BaseModel):
    version: str
    global_policies: dict[str, Any]
    jurisdictions: dict[str, dict[str, Any]] = {}
    contexts: dict[str, dict[str, Any]] = {}

class RiskOverlayManager:
    """
    Loads and merges YAML policy overlays from a root directory.
    """

    def __init__(self, overlay_dir: str):
        self.overlay_dir = Path(overlay_dir)
        self._lock = threading.Lock()
        self._overlays: Optional[OverlaySchema] = None
        self._load()

    def _load(self):
        overlay_file = self.overlay_dir / "overlays.yaml"
        if not overlay_file.exists():
            raise FileNotFoundError(f"No overlays.yaml found in {self.overlay_dir}")
        try:
            data = yaml.safe_load(open(overlay_file, encoding="utf-8"))
            self._overlays = OverlaySchema(**data)
        except ValidationError as e:
            raise RuntimeError(f"Overlay schema validation failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load overlays.yaml: {e}")

    def hot_reload(self):
        with self._lock:
            self._load()

    def get_policies(
        self,
        jurisdiction: Optional[str] = None,
        context: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Returns the merged policy dict for the given jurisdiction and context.
        Order of precedence:
          1. global_policies
          2. jurisdiction overrides (if any)
          3. context overrides (if any)
        """
        with self._lock:
            if not self._overlays:
                raise RuntimeError("No overlays loaded")

            merged = copy.deepcopy(self._overlays.global_policies)

            if jurisdiction and jurisdiction in self._overlays.jurisdictions:
                merged = self._deep_merge(
                    merged, self._overlays.jurisdictions[jurisdiction]
                )

            if context and context in self._overlays.contexts:
                merged = self._deep_merge(
                    merged, self._overlays.contexts[context]
                )

            return merged

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        for k, v in override.items():
            if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                base[k] = self._deep_merge(base[k], v)
            else:
                base[k] = copy.deepcopy(v)
        return base

# CLI for ops teams
if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Risk Overlay Manager CLI")
    parser.add_argument("overlay_dir", help="Path to overlays.yaml root dir")
    parser.add_argument("--jurisdiction", help="Jurisdiction code", default=None)
    parser.add_argument("--context", help="Context code", default=None)
    args = parser.parse_args()

    mgr = RiskOverlayManager(args.overlay_dir)
    policies = mgr.get_policies(args.jurisdiction, args.context)
    print(json.dumps(policies, indent=2))
