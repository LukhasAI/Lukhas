import os
import sys
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import Mock, patch

import pytest

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ======================================================================
# T4-GRADE TEST CONFIGURATION
# ======================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up T4-grade test environment before any tests run."""
    # Set environment variables for testing
    os.environ.update({
        "ENVIRONMENT": "testing",
        "LUKHAS_TESTING": "true", 
        "LUKHAS_LOG_LEVEL": "DEBUG",
        "ETHICS_ENFORCEMENT_LEVEL": "strict",
        "GUARDIAN_ACTIVE": "true",
        "BRIDGE_DRY_RUN": "true",
    })
    
    # Configure test logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    
    # Suppress noisy loggers
    for logger_name in ["urllib3", "requests", "asyncio"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    yield


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory(prefix="lukhas_test_") as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide T4-grade mock configuration for tests."""
    return {
        "safety_mode": "strict",
        "debug": True,
        "max_retries": 3,
        "timeout": 30,
        "drift_threshold": 0.15,
        "enable_logging": True,
        "enable_monitoring": False,
    }


@pytest.fixture
def performance_timer():
    """T4 performance measurement utility."""
    import time
    
    class PerformanceTimer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
        
        @property
        def elapsed(self) -> float:
            if self.start_time is None or self.end_time is None:
                return 0.0
            return self.end_time - self.start_time
        
        def assert_under_ms(self, max_ms: float, message: str = ""):
            max_seconds = max_ms / 1000.0
            assert self.elapsed < max_seconds, \
                f"Performance test failed: {self.elapsed*1000:.1f}ms > {max_ms}ms {message}"
    
    return PerformanceTimer()


# Enforce minimal realism in "reality" tests
def pytest_collection_modifyitems(items):
    for item in items:
        if item.get_closest_marker("no_mock"):
            item.add_marker(pytest.mark.block_mocks)
        
        # Auto-mark tests by location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)


def pytest_runtest_setup(item):
    if item.get_closest_marker("block_mocks"):
        # Disarm common mocking channels in reality tests
        os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"


# def pytest_sessionfinish(session, exitstatus):
#     rep = session.config.pluginmanager.getplugin("terminalreporter")
#     skips = sum(1 for _ in rep.stats.get("skipped", []))
#     xfails = sum(1 for _ in rep.stats.get("xfailed", []))
#     if skips + xfails > 5:
#         pytest.exit(
#             f"Too many skipped/xfail tests ({skips + xfails}). Tighten scope.",
#             returncode=1,
#         )
