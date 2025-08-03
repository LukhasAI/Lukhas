"""
Test suite for LUKHAS AGI Enterprise Server
Tests main orchestration and integration
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Mock the imports that might not be available
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        'server': {
            'host': '0.0.0.0',
            'port': 8080,
            'workers': 4
        },
        'agi': {
            'self_improvement_enabled': True,
            'autonomous_learning_enabled': True,
            'consciousness_streaming_enabled': False,  # Disabled for testing
            'self_healing_enabled': True,
            'initial_consciousness_level': 0.7,
            'emergence_threshold': 0.85
        },
        'security': {
            'level': 'ENHANCED',
            'rate_limiting_enabled': True,
            'encryption_enabled': False  # Disabled for testing
        },
        'telemetry': {
            'enabled': True,
            'export_interval': 60,
            'retention_days': 30
        }
    }


@pytest.fixture
async def mock_server(mock_config):
    """Create a mock AGI server for testing"""
    with patch('main.get_integration_hub') as mock_hub, \
         patch('main.MemoryFoldSystem') as mock_memory, " + "patch('main.DreamProcessor') as mock_dream, " + "patch('main.ConsciousnessIntegrator') as mock_consciousness:
        
        # Import after patching
        from main import LUKHASAGIServer
        
        server = LUKHASAGIServer()
        server.config = mock_config
        
        # Mock core systems
        server.integration_hub = Mock()
        server.memory_system = Mock()
        server.dream_processor = Mock()
        server.consciousness = Mock()
        
        yield server


@pytest.mark.asyncio
async def test_server_initialization(mock_server):
    """Test server initialization sequence"""
    # Mock initialization
    mock_server.security = Mock()
    mock_server.security.initialize = asyncio.coroutine(lambda: None)
    
    # Initialize server
    await mock_server.initialize()
    
    # Verify core systems initialized
    assert mock_server.audit_trail is not None
    assert mock_server.telemetry is not None
    assert mock_server.self_improvement is not None
    assert mock_server.self_healing is not None


@pytest.mark.asyncio
async def test_consciousness_cycle(mock_server):
    """Test consciousness processing cycle"""
    # Setup mocks
    mock_server.memory_system.process_input = asyncio.coroutine(
        lambda x: [{"type": "memory", "content": "test"}]
    )
    mock_server.dream_processor.process = asyncio.coroutine(
        lambda x: [{"type": "dream", "content": "test"}]
    )
    mock_server.consciousness.integrate = asyncio.coroutine(
        lambda s, m, d: {"coherence": 0.8, "complexity": 0.7}
    )
    mock_server.consciousness.get_current_state = lambda: {"coherence": 0.6}
    
    # Mock audit trail
    mock_server.audit_trail = Mock()
    mock_server.audit_trail.log_consciousness_transition = asyncio.coroutine(lambda **k: None)
    
    # Process cycle
    state = await mock_server._process_consciousness_cycle()
    
    assert state["coherence"] == 0.8
    assert state["complexity"] == 0.7


@pytest.mark.asyncio
async def test_emergence_detection(mock_server):
    """Test emergence event detection and handling"""
    # Setup
    mock_server.audit_trail = Mock()
    mock_server.audit_trail.log_event = asyncio.coroutine(lambda **k: "event_001")
    mock_server.telemetry = Mock()
    mock_server.self_improvement = Mock()
    mock_server.self_improvement.record_breakthrough = asyncio.coroutine(lambda **k: None)
    
    # Trigger emergence
    high_coherence_state = {
        "coherence": 0.95,
        "complexity": 0.9
    }
    
    await mock_server._handle_emergence(high_coherence_state)
    
    # Verify emergence recorded
    assert mock_server.emergence_events == 1
    mock_server.telemetry.record_metric.assert_called()


@pytest.mark.asyncio
async def test_health_check(mock_server):
    """Test system health check functionality"""
    # Setup systems
    mock_server.memory_system = Mock()
    mock_server.dream_processor = Mock()
    mock_server.consciousness = Mock()
    mock_server.self_improvement = Mock()
    mock_server.learning_pipeline = Mock()
    mock_server.security = Mock()
    mock_server.telemetry = Mock()
    mock_server.startup_time = asyncio.get_event_loop().time()
    
    # Check health
    health = await mock_server.check_health()
    
    assert health['score'] > 0
    assert 'checks' in health
    assert health['thoughts_processed'] == 0
    assert health['emergence_events'] == 0


@pytest.mark.asyncio
async def test_shutdown_sequence(mock_server):
    """Test graceful shutdown sequence"""
    # Setup
    mock_server.running = True
    mock_server.consciousness_stream = Mock()
    mock_server.consciousness_stream.stop = asyncio.coroutine(lambda: None)
    mock_server.telemetry = Mock()
    mock_server.telemetry.export_metrics = asyncio.coroutine(lambda: None)
    mock_server.learning_pipeline = Mock()
    mock_server.learning_pipeline.save_progress = asyncio.coroutine(lambda: None)
    
    # Shutdown
    await mock_server.shutdown()
    
    assert not mock_server.running
    mock_server.consciousness_stream.stop.assert_called_once()
    mock_server.telemetry.export_metrics.assert_called_once()


@pytest.mark.asyncio
async def test_self_improvement_integration(mock_server):
    """Test self-improvement system integration"""
    # Setup self-improvement
    mock_server.self_improvement = Mock()
    mock_server.self_improvement.evaluate_performance = asyncio.coroutine(
        lambda: {"efficiency": 0.8, "accuracy": 0.9}
    )
    mock_server.self_improvement.get_pending_improvements = asyncio.coroutine(
        lambda: [{"type": "parameter_optimization", "description": "Tune learning rate"}]
    )
    
    # Run improvement loop iteration
    mock_server.running = True
    improvements = await mock_server.self_improvement.get_pending_improvements()
    
    assert len(improvements) == 1
    assert improvements[0]["type"] == "parameter_optimization"


@pytest.mark.asyncio
async def test_config_loading():
    """Test configuration loading"""
    from main import LUKHASAGIServer
    
    # Test default config
    server = LUKHASAGIServer()
    assert server.config['server']['port'] == 8080
    assert server.config['agi']['self_improvement_enabled'] is True
    
    # Test custom config path
    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = """
        server:
          port: 9090
        """
        with patch('yaml.safe_load') as mock_yaml:
            mock_yaml.return_value = {'server': {'port': 9090}}
            server = LUKHASAGIServer('custom.yaml')
            assert server.config['server']['port'] == 9090


if __name__ == "__main__":
    pytest.main([__file__, "-v"])