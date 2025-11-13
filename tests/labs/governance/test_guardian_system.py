import pytest
from unittest.mock import patch, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_guardian_system_initialization_no_components():
    """Test GuardianSystem initialization when no components are available."""
    with patch.dict('sys.modules', {
        'labs.governance.ethics.guardian_reflector': None,
        'labs.governance.guardian_sentinel': None,
        'labs.governance.guardian_shadow_filter': None,
        'labs.governance.ethics.enhanced_guardian': None,
        'labs.governance.ethics.ethics_guardian': None,
    }):
        from labs.governance.guardian_system import GuardianSystem
        guardian_system = GuardianSystem()
        assert not guardian_system.is_available()
        status = guardian_system.get_status()
        assert not status['reflector_available']
        assert not status['sentinel_available']

@pytest.mark.asyncio
async def test_guardian_system_initialization_with_components():
    """Test GuardianSystem initialization with mock components."""
    mock_reflector = MagicMock()
    mock_sentinel = MagicMock()

    with patch.dict('sys.modules', {
        'labs.governance.ethics.guardian_reflector': MagicMock(GuardianReflector=mock_reflector),
        'labs.governance.guardian_sentinel': MagicMock(GuardianSentinel=mock_sentinel),
        'labs.governance.guardian_shadow_filter': None,
        'labs.governance.ethics.enhanced_guardian': None,
        'labs.governance.ethics.ethics_guardian': None,
    }):
        from labs.governance.guardian_system import GuardianSystem
        guardian_system = GuardianSystem()
        assert guardian_system.is_available()
        status = guardian_system.get_status()
        assert status['reflector_available']
        assert status['sentinel_available']

@pytest.mark.asyncio
async def test_validate_action(monkeypatch):
    """Test the validate_action method."""
    # Mock the components
    mock_reflector_instance = MagicMock()
    mock_reflector_instance.reflect_on_decision = AsyncMock(return_value={"status": "ok"})
    mock_reflector = MagicMock(return_value=mock_reflector_instance)

    mock_sentinel_instance = MagicMock()
    mock_sentinel_instance.validate = AsyncMock(return_value={"status": "ok"})
    mock_sentinel = MagicMock(return_value=mock_sentinel_instance)

    # We need to import the module before patching the sys.modules
    from labs.governance import guardian_system

    # Then we can patch the symbols in the already imported module
    monkeypatch.setattr(guardian_system, "GuardianReflector", mock_reflector)
    monkeypatch.setattr(guardian_system, "GuardianSentinel", mock_sentinel)
    monkeypatch.setattr(guardian_system, "GuardianShadowFilter", None)
    monkeypatch.setattr(guardian_system, "EnhancedWorkspaceGuardian", None)
    monkeypatch.setattr(guardian_system, "EthicsGuardian", None)

    gs = guardian_system.GuardianSystem()
    action_data = {"action": "test"}
    results = await gs.validate_action(action_data)

    assert "reflection" in results
    assert results["reflection"]["status"] == "ok"
    assert "sentinel" in results
    assert results["sentinel"]["status"] == "ok"

    mock_reflector_instance.reflect_on_decision.assert_awaited_once_with(action_data)
    mock_sentinel_instance.validate.assert_awaited_once_with(action_data)
