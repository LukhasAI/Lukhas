"""Oracle Colony - core/colonies/oracle_colony.py

This file provides a compact, lane-safe OracleColony implementation that
depends on a pluggable OpenAI provider via `core.adapters.provider_registry`.
The module avoids any static `labs` imports so import-linter won't detect a
production -> labs edge.
"""

import asyncio
import json
import logging
import importlib
from dataclasses import dataclass
logger = logging.getLogger("ΛTRACE.oracle_colony")
from typing import Any, Optional, Dict, List


# NOTE: lazy loader to avoid import-time dependency on `labs`.
def _get_labs() -> Optional[Any]:
	"""
	Lazy import of the `labs` integration. Returns the labs module if found, else None.
	This prevents import-time edges from production modules into labs.
	"""
	try:
		return importlib.import_module("labs")
	except Exception:
		# Deliberately swallow import errors so production lanes without `labs`
		# installed won't fail during module import. Callers should handle None.
		return None
