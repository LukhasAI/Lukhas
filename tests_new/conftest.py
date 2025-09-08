import pytest
import os
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def settings():
    """Test configuration settings."""
    return {
        "env": "test",
        "debug": os.getenv("PYTEST_DEBUG", "false").lower() == "true"
    }

@pytest.fixture
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "data"

@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory.""" 
    return Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def lukhas_test_config():
    """LUKHAS-specific test configuration."""
    return {
        "consciousness_active": False,
        "dream_simulation_enabled": False,
        "quantum_processing_enabled": False,
        "ethics_enforcement_level": "strict",
    }