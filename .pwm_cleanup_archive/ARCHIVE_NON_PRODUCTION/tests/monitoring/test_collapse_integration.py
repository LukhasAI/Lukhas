"""
═══════════════════════════════════════════════════════════════════════════════
║ 🧪 LUKHAS AI - COLLAPSE INTEGRATION TESTS
║ Basic tests for collapse integration helper
╚═══════════════════════════════════════════════════════════════════════════════
"""

import pytest

from core.monitoring.collapse_integration import (
    CollapseIntegration,
    integrate_collapse_tracking,
)


class DummyOrchestrator:
    async def run(self):
        pass

    async def get_component_health(self):
        return {}


class DummyEthics:
    pass


@pytest.mark.asyncio
async def test_integrate_returns_instance():
    orchestrator = DummyOrchestrator()
    ethics = DummyEthics()
    integration = integrate_collapse_tracking(orchestrator, ethics)
    assert isinstance(integration, CollapseIntegration)
    assert integration.orchestrator is orchestrator
    assert integration.ethics_sentinel is ethics
