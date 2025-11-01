import pytest

# Skip MATRIZ orchestrator E2E tests when labs async orchestrator is unavailable
pytest.importorskip(
    "labs.core.orchestration.async_orchestrator",
    reason="labs async orchestrator not available in default dev env",
)

