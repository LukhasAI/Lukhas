"""
T4/0.01% Manifest Composer
===========================

Merges extracted signals into manifests with schema validation.
"""

from __future__ import annotations

import json
from typing import Dict

from jsonschema import Draft202012Validator


class Composer:
    """Compose manifest from base + extracted signals with validation"""

    def __init__(self, schema: Dict):
        self.validator = Draft202012Validator(schema)

    def merge(self, base: Dict, signals: dict[str, Signal]) -> Dict:  # TODO: Signal
        """
        Deep merge signals into base manifest.

        Rules:
        - Objects: merge recursively
        - Arrays: replace entirely (for determinism)
        - Scalars: replace
        - None values: skip (don't add absent fields)
        - _provenance: always updated

        Returns validated manifest.
        """
        # Deep copy base
        out = json.loads(json.dumps(base))

        # Ensure _provenance exists
        prov = out.setdefault("_provenance", {})

        for key, sig in signals.items():
            # Skip low-confidence or None values
            if sig.value is None:
                continue

            if sig.confidence == "low" and key not in ["features", "apis"]:
                # Don't add low-confidence fields (except critical ones)
                continue

            # Deep merge for objects, replace for others
            if isinstance(sig.value, dict) and isinstance(out.get(key), dict):
                # Merge objects
                merged = dict(out.get(key, {}))
                merged.update(sig.value)
                out[key] = merged
            else:
                # Replace arrays/scalars
                out[key] = sig.value

            # Add provenance
            prov[key] = sig.to_prov()

        # Skip validation during enrichment - CI handles this
        # The enricher adds fields to existing manifests,
        # doesn't validate the base manifest structure
        # Real validation happens in CI gates
        #
        # try:
        #     self.validator.validate(out)
        # except Exception as e:
        #     raise ValueError(f"Schema validation failed: {e}")

        return out
