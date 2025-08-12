"""
Memory Module Canary Tests
Validates consolidated memory functionality
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_memory_imports():
    """Test that memory modules can be imported"""
    from lukhas.accepted import memory
    assert memory is not None
    assert hasattr(memory, '__trinity__')

def test_memory_systems():
    """Test core memory systems are available"""
    from lukhas.accepted.memory import fold, causal, episodic, consolidation, colonies
    
    assert fold is not None
    assert causal is not None
    assert episodic is not None
    assert consolidation is not None
    assert colonies is not None

def test_fold_manager():
    """Test fold manager functionality"""
    from lukhas.accepted.memory import get_fold_manager
    
    manager = get_fold_manager()
    assert manager is not None
    
    # Test fold creation
    fold = manager.create_fold("test content")
    assert fold is not None
    assert fold.content == "test content"
    
    # Test cascade prevention
    assert manager.CASCADE_THRESHOLD == 0.997

def test_episodic_memory():
    """Test episodic memory storage"""
    from lukhas.accepted.memory import get_episodic_memory
    
    episodic = get_episodic_memory()
    
    # Store episode
    episode = episodic.store_episode("test episode", tags=["test"])
    assert episode is not None
    
    # Retrieve by tags
    results = episodic.retrieve_by_tags(["test"])
    assert len(results) > 0

def test_memory_colony():
    """Test colony-based distributed memory"""
    from lukhas.accepted.memory import get_memory_colony
    
    colony = get_memory_colony()
    status = colony.get_colony_status()
    
    assert status["total_nodes"] > 0
    assert status["replication_factor"] == 3
    
    # Test storage
    nodes = colony.store_memory("test_id", "test_content")
    assert len(nodes) <= 3  # Replication factor

def test_unified_memory():
    """Test unified memory interface"""
    from lukhas.accepted.memory import get_unified_memory
    
    memory = get_unified_memory()
    
    # Test storage
    result = memory.store("test content", memory_type="episodic")
    assert result is not None
    
    # Test status
    status = memory.get_status()
    assert "trinity" in status
    assert status["trinity"] == "synchronized"

def test_trinity_integration():
    """Test Trinity Framework integration"""
    from lukhas.accepted.memory import trinity_sync
    
    sync_status = trinity_sync()
    assert sync_status['identity'] == '⚛️'
    assert sync_status['consciousness'] == '🧠'
    assert sync_status['guardian'] == '🛡️'
    assert sync_status['memory_status'] == 'synchronized'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
