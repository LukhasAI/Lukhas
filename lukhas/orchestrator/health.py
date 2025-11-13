"""
Deep health check for the LUKHAS orchestrator.

This module provides a comprehensive health check that validates the status of critical
dependencies, including:

- Database connection: Verifies that the application can connect to and communicate with the database.
- Memory system: Checks the health and availability of the in-memory cache or data store.
- MATRIZ nodes: Ensures that all cognitive nodes in the MATRIZ engine are operational.
- External APIs: Verifies connectivity to essential third-party services.

The main entry point is the `get_health_status` function, which aggregates the results
of these checks into a single report.
"""

# Mock missing modules for now, as per the instructions.
import sys
from unittest.mock import MagicMock

sys.modules["lukhas.db"] = MagicMock()
sys.modules["lukhas.memory"] = MagicMock()
sys.modules["lukhas.matriz"] = MagicMock()
sys.modules["lukhas.external"] = MagicMock()

import asyncio
from typing import Dict, Any

from lukhas.db import DatabaseManager
from lukhas.memory import MemoryManager
from lukhas.matriz import MatrizManager
from lukhas.external import ExternalAPIManager

async def check_database_connection() -> Dict[str, Any]:
    """Checks the database connection."""
    try:
        db_manager = DatabaseManager()
        await db_manager.connect()
        await db_manager.ping()
        await db_manager.close()
        return {"status": "ok", "details": "Database connection is healthy."}
    except Exception as e:
        return {"status": "error", "details": f"Database connection failed: {e}"}

async def check_memory_system() -> Dict[str, Any]:
    """Checks the memory system."""
    try:
        memory_manager = MemoryManager()
        await memory_manager.check_status()
        return {"status": "ok", "details": "Memory system is healthy."}
    except Exception as e:
        return {"status": "error", "details": f"Memory system check failed: {e}"}

async def check_matriz_nodes() -> Dict[str, Any]:
    """Checks the MATRIZ nodes."""
    try:
        matriz_manager = MatrizManager()
        nodes = await matriz_manager.get_nodes()
        unhealthy_nodes = [node for node in nodes if not node.is_healthy()]
        if unhealthy_nodes:
            return {
                "status": "error",
                "details": f"Unhealthy MATRIZ nodes: {[node.name for node in unhealthy_nodes]}",
            }
        return {"status": "ok", "details": "All MATRIZ nodes are healthy."}
    except Exception as e:
        return {"status": "error", "details": f"MATRIZ nodes check failed: {e}"}

async def check_external_apis() -> Dict[str, Any]:
    """Checks the external APIs."""
    try:
        external_api_manager = ExternalAPIManager()
        await external_api_manager.check_apis()
        return {"status": "ok", "details": "External APIs are healthy."}
    except Exception as e:
        return {"status": "error", "details": f"External API check failed: {e}"}

async def get_health_status() -> Dict[str, Any]:
    """
    Performs a deep health check of the LUKHAS orchestrator.

    This function aggregates the results of the deep checks and returns a detailed
    status, including the status of each component and an overall status.

    The returned dictionary will have the following structure:

    {
        "status": "ok" | "error",
        "components": {
            "database": {
                "status": "ok" | "error",
                "details": "...",
            },
            "memory_system": {
                "status": "ok" | "error",
                "details": "...",
            },
            "matriz_nodes": {
                "status": "ok" | "error",
                "details": "...",
            },
            "external_apis": {
                "status": "ok" | "error",
                "details": "...",
            },
        },
    }
    """
    checks = {
        "database": check_database_connection(),
        "memory_system": check_memory_system(),
        "matriz_nodes": check_matriz_nodes(),
        "external_apis": check_external_apis(),
    }

    results = await asyncio.gather(*checks.values())

    health_status: Dict[str, Any] = {
        "status": "ok",
        "components": {},
    }

    for i, (name, result) in enumerate(zip(checks.keys(), results)):
        health_status["components"][name] = result
        if result["status"] != "ok":
            health_status["status"] = "error"

    return health_status
