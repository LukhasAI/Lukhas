"""
Tests for the BioHub module using pytest.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Import the module under test. Patches will be applied to prevent side effects.
from core.symbolic.bio_hub import BioHub, _bio_hub_instance, get_bio_hub


@pytest.fixture(autouse=True)
def reset_bio_hub_singleton():
    """Fixture to reset the BioHub singleton instance before each test."""
    global _bio_hub_instance
    _bio_hub_instance = None
    yield
    _bio_hub_instance = None

# By default, mock out the service loading for focused unit tests.
@patch('core.symbolic.bio_hub.BioHub._register_bio_processing_services', MagicMock())
@patch('core.symbolic.bio_hub.BioHub._register_bio_symbolic_services', MagicMock())
@patch('core.symbolic.bio_hub.BioHub._register_analysis_services', MagicMock())
@patch('core.symbolic.bio_hub.BioHub._register_with_service_discovery', MagicMock())
def test_initialization():
    """Test that the BioHub initializes without errors."""
    bio_hub = BioHub()
    assert isinstance(bio_hub, BioHub)
    assert bio_hub.is_initialized

@patch('core.symbolic.bio_hub.BioHub._initialize_services', MagicMock())
def test_singleton():
    """Test that get_bio_hub returns a singleton."""
    instance1 = get_bio_hub()
    instance2 = get_bio_hub()
    assert instance1 is instance2

@patch('core.symbolic.bio_hub.BioHub._initialize_services', MagicMock())
def test_register_and_get_service():
    """Test service registration and retrieval."""
    bio_hub = BioHub()
    mock_service = MagicMock()
    bio_hub.register_service("test_service", mock_service)
    retrieved_service = bio_hub.get_service("test_service")
    assert retrieved_service is mock_service
    assert bio_hub.get_service("non_existent_service") is None

@pytest.mark.asyncio
@patch('core.symbolic.bio_hub.BioHub._initialize_services', MagicMock())
async def test_event_handling():
    """Test event handler registration and processing."""
    bio_hub = BioHub()
    mock_handler = AsyncMock()
    bio_hub.register_event_handler("test_event", mock_handler)
    await bio_hub.process_event("test_event", {"data": "test"})
    mock_handler.assert_awaited_once_with({"data": "test"})

@pytest.mark.asyncio
@patch('core.symbolic.bio_hub.BioHub._initialize_services', MagicMock())
async def test_bio_symbolic_event_processing():
    """Test the main bio-symbolic event processing pathway."""
    bio_hub = BioHub()
    mock_bio_processor = MagicMock()
    mock_bio_processor.process = AsyncMock(return_value={"processed": True})
    mock_symbolic_processor = MagicMock()
    mock_symbolic_processor.interpret_bio_data = AsyncMock(return_value={"interpreted": True})

    with patch.object(bio_hub, 'get_service') as mock_get_service:
        mock_get_service.side_effect = lambda name: {
            "bio_processor": mock_bio_processor,
            "bio_symbolic_processor": mock_symbolic_processor
        }.get(name)
        result = await bio_hub.process_bio_symbolic_event({"data": "test"})

    mock_bio_processor.process.assert_awaited_once_with({"data": "test"})
    mock_symbolic_processor.interpret_bio_data.assert_awaited_once_with({"processed": True})
    assert result["bio"] == {"processed": True}

@pytest.mark.asyncio
@patch('core.symbolic.bio_hub.BioHub._initialize_services', MagicMock())
async def test_bio_symbolic_event_processing_with_errors():
    """Test the error handling in the bio-symbolic event processing pathway."""
    bio_hub = BioHub()
    mock_bio_processor = MagicMock()
    mock_bio_processor.process = AsyncMock(side_effect=Exception("bio error"))
    mock_symbolic_processor = MagicMock()
    mock_symbolic_processor.interpret_bio_data = AsyncMock(side_effect=Exception("symbolic error"))

    with patch.object(bio_hub, 'get_service') as mock_get_service:
        mock_get_service.side_effect = lambda name: {
            "bio_processor": mock_bio_processor,
            "bio_symbolic_processor": mock_symbolic_processor
        }.get(name)
        result = await bio_hub.process_bio_symbolic_event({"data": "test"})

    assert "error" in result["bio"]
    assert "error" in result["symbolic"]
    assert result["bio"]["error"] == "bio error"
    assert result["symbolic"]["error"] == "symbolic error"

@pytest.mark.asyncio
@patch('core.symbolic.bio_hub.BioHub._initialize_services', MagicMock())
async def test_health_check():
    """Test the health check logic for various service states."""
    bio_hub = BioHub()
    healthy_service = MagicMock()
    healthy_service.health_check = AsyncMock(return_value={"status": "healthy"})
    unhealthy_service = MagicMock()
    unhealthy_service.health_check = AsyncMock(side_effect=Exception("service down"))
    no_health_check_service = MagicMock()
    delattr(no_health_check_service, 'health_check')

    bio_hub.register_service("healthy", healthy_service)
    bio_hub.register_service("unhealthy", unhealthy_service)
    bio_hub.register_service("no_health_check", no_health_check_service)

    health = await bio_hub.health_check()
    assert health["status"] == "degraded"
    assert health["services"]["healthy"]["status"] == "healthy"
    assert health["services"]["unhealthy"]["status"] == "error"
    assert health["services"]["no_health_check"]["status"] == "active"

# The following tests are for the initialization logic itself, so we don't mock it away.
def test_initialize_services_calls_all_registration_methods():
    """Verify that the main initializer calls all sub-initializers."""
    with patch.object(BioHub, '_register_bio_processing_services') as mock_proc, \
         patch.object(BioHub, '_register_bio_symbolic_services') as mock_sym, \
         patch.object(BioHub, '_register_analysis_services') as mock_an, \
         patch.object(BioHub, '_register_with_service_discovery') as mock_disc:

        hub = BioHub()

        mock_proc.assert_called_once()
        mock_sym.assert_called_once()
        mock_an.assert_called_once()
        mock_disc.assert_called_once()

# To test the error handling within the registration methods, we patch the
# built-in __import__ function.
@patch('builtins.__import__', side_effect=ImportError("test import error"))
def test_registration_methods_handle_import_error(mock_import):
    """
    Test that the hub initializes gracefully even if service modules cannot be imported.
    """
    hub = BioHub()
    # The test passes if no exception is raised and the hub still initializes.
    assert hub.is_initialized
    # No services should be registered due to the import errors.
    assert len(hub.services) == 0
    # Ensure our mock was actually called.
    mock_import.assert_called()
