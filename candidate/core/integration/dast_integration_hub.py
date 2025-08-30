"""

#TAG:core
#TAG:integration
#TAG:neuroplastic
#TAG:colony

DAST Integration Hub
Central hub for connecting all DAST components to TrioOrchestrator and Audit System
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from analysis_tools.audit_decision_embedding_engine import DecisionAuditEngine
except ImportError:
    # Fallback for testing
    DecisionAuditEngine = None

try:
    from dast.core.dast_engine import DASTEngine
except ImportError:
    DASTEngine = None

try:
    from ethics.seedra.seedra_core import SEEDRACore
except ImportError:
    SEEDRACore = None

try:
    from candidate.orchestration.golden_trio.trio_orchestrator import TrioOrchestrator
except ImportError:
    TrioOrchestrator = None

try:
    from symbolic.core.symbolic_language import SymbolicLanguageFramework
except ImportError:
    SymbolicLanguageFramework = None

logger = logging.getLogger(__name__)


class DASTIntegrationHub:
    """Central hub for DAST component integration"""

    def __init__(self):
        self.name = "dast_integration_hub"
        self.trio_orchestrator = TrioOrchestrator() if TrioOrchestrator else None
        self.dast_engine = DASTEngine() if DASTEngine else None
        self.audit_engine = DecisionAuditEngine() if DecisionAuditEngine else None
        self.symbolic_framework = SymbolicLanguageFramework() if SymbolicLanguageFramework else None
        self.seedra = SEEDRACore() if SEEDRACore else None

        # Component registry
        self.registered_components = {}
        self.task_tracking = {}
        self.connected_hubs: list[dict[str, Any]] = []

        logger.info("DAST Integration Hub initialized")

    async def initialize(self):
        """Initialize all connections"""
        # Register with TrioOrchestrator
        await self.trio_orchestrator.register_component("dast_integration_hub", self)

        # Initialize audit integration
        await self.audit_engine.initialize()

        # Connect to SEEDRA
        await self.seedra.register_system("dast", self)

        logger.info("DAST Integration Hub fully initialized")
        return True

    async def register_component(
        self, component_name: str, component_path: str, component_instance: Any
    ):
        """Register a DAST component for integration"""
        self.registered_components[component_name] = {
            "path": component_path,
            "instance": component_instance,
            "status": "registered",
            "connections": [],
        }

        # Connect to audit system
        await self._integrate_with_audit(component_name, component_instance)

        # Connect to symbolic framework
        await self._integrate_with_symbolic(component_name, component_instance)

        logger.info(f"Registered DAST component: {component_name}")
        return True

    async def _integrate_with_audit(self, component_name: str, component_instance: Any):
        """Integrate component with audit system"""
        # Wrap component methods with audit trails
        for method_name in dir(component_instance):
            if not method_name.startswith("_") and callable(
                getattr(component_instance, method_name)
            ):
                original_method = getattr(component_instance, method_name)

                async def audited_method(*args, **kwargs):
                    # Pre-execution audit
                    await self.audit_engine.embed_decision(
                        decision_type="DAST",
                        context={
                            "component": component_name,
                            "method": method_name,
                            "args": str(args),
                            "kwargs": str(kwargs),
                        },
                        source=f"dast.{component_name}",
                    )

                    # Execute original method
                    result = await original_method(*args, **kwargs)

                    # Post-execution audit
                    await self.audit_engine.embed_decision(
                        decision_type="DAST_RESULT",
                        context={
                            "component": component_name,
                            "method": method_name,
                            "result": str(result),
                        },
                        source=f"dast.{component_name}",
                    )

                    return result

                # Replace method with audited version
                setattr(component_instance, method_name, audited_method)

    async def _integrate_with_symbolic(self, component_name: str, component_instance: Any):
        """Integrate component with symbolic language framework"""
        # Register component's symbolic patterns
        symbolic_patterns = getattr(component_instance, "symbolic_patterns", {})
        if symbolic_patterns:
            await self.symbolic_framework.register_patterns(
                f"dast.{component_name}", symbolic_patterns
            )

    async def track_task(self, task_id: str, task_data: dict[str, Any]):
        """Track DAST task execution"""
        self.task_tracking[task_id] = {
            "data": task_data,
            "status": "pending",
            "start_time": None,
            "end_time": None,
            "result": None,
        }

        # Notify TrioOrchestrator
        await self.trio_orchestrator.notify_task_created("dast", task_id, task_data)

    async def execute_task(self, task_id: str) -> dict[str, Any]:
        """Execute tracked task with full integration"""
        if task_id not in self.task_tracking:
            return {"error": "Task not found"}

        task = self.task_tracking[task_id]
        task["status"] = "executing"
        task["start_time"] = asyncio.get_event_loop().time()

        try:
            # Execute through DAST engine
            result = await self.dast_engine.execute_task(task["data"])

            task["status"] = "completed"
            task["result"] = result

            # Notify completion
            await self.trio_orchestrator.notify_task_completed("dast", task_id, result)

            return result

        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)

            # Notify failure
            await self.trio_orchestrator.notify_task_failed("dast", task_id, str(e))

            return {"error": str(e)}

        finally:
            task["end_time"] = asyncio.get_event_loop().time()

    def broadcast_to_all_hubs(self, message: dict[str, Any]) -> dict[str, list[Any]]:
        responses = {}
        for hub_info in self.connected_hubs:
            hub_name = hub_info["name"]
            hub = hub_info["instance"]
            try:
                if hasattr(hub, "receive_message"):
                    response = hub.receive_message(message)
                    responses[hub_name] = response
            except Exception as e:
                logger.error(f"Failed to broadcast to {hub_name}: {e}")
                responses[hub_name] = {"error": str(e)}
        return responses

    def receive_message(self, message: dict[str, Any]) -> dict[str, Any]:
        return {
            "hub": self.name,
            "received": True,
            "timestamp": datetime.now().isoformat(),
            "message_id": message.get("id", "unknown"),
        }

    def get_status(self) -> dict[str, Any]:
        """Get integration hub status"""
        return {
            "registered_components": len(self.registered_components),
            "active_tasks": len(
                [t for t in self.task_tracking.values() if t["status"] == "executing"]
            ),
            "completed_tasks": len(
                [t for t in self.task_tracking.values() if t["status"] == "completed"]
            ),
            "failed_tasks": len(
                [t for t in self.task_tracking.values() if t["status"] == "failed"]
            ),
        }


# Singleton instance
_dast_integration_hub = None


def get_dast_integration_hub() -> DASTIntegrationHub:
    """Get or create DAST integration hub instance"""
    global _dast_integration_hub
    if _dast_integration_hub is None:
        _dast_integration_hub = DASTIntegrationHub()
    return _dast_integration_hub
