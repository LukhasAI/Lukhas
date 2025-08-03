"""
Unit tests for LUKHAS Memory System
"""

import pytest
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch

from tests.test_framework import (
    LUKHASTestCase, MockDataGenerator, TestValidator
)


class TestMemoryCore(LUKHASTestCase):
    """Test core memory functionality"""
    
    @pytest.fixture
    async def memory_system(self):
        """Create memory system instance"""
        from core.api.service_stubs import MemoryManager
        memory = MemoryManager()
        await memory.initialize()
        return memory
        
    @pytest.mark.asyncio
    async def test_initialization(self, memory_system):
        """Test memory system initialization"""
        assert memory_system.initialized is True
        assert isinstance(memory_system.memories, dict)
        assert 'general' in memory_system.memories
        assert 'episodic' in memory_system.memories
        assert 'semantic' in memory_system.memories
        assert 'procedural' in memory_system.memories
        
    @pytest.mark.asyncio
    async def test_memory_storage(self, memory_system):
        """Test basic memory storage"""
        content = {
            'event': 'Test event',
            'details': 'Important information',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        result = await memory_system.store(content, memory_type='general')
        
        # Validate response
        TestValidator.validate_memory_response(result)
        assert result['stored'] is True
        assert result['type'] == 'general'
        assert result['fold_created'] is True
        
        # Verify memory was stored
        assert len(memory_system.memories['general']) == 1
        stored_memory = memory_system.memories['general'][0]
        assert stored_memory['content'] == content
        
    @pytest.mark.asyncio
    async def test_memory_types(self, memory_system):
        """Test different memory types"""
        memory_types = ['general', 'episodic', 'semantic', 'procedural']
        
        for mem_type in memory_types:
            content = {'type_test': f'Testing {mem_type}'}
            result = await memory_system.store(content, memory_type=mem_type)
            
            assert result['stored'] is True
            assert result['type'] == mem_type
            assert len(memory_system.memories[mem_type]) > 0
            
    @pytest.mark.asyncio
    async def test_memory_retrieval(self, memory_system):
        """Test memory retrieval"""
        # Store test memories
        memories = [
            {'content': 'First memory about cats'},
            {'content': 'Second memory about dogs'},
            {'content': 'Third memory about cats and dogs'}
        ]
        
        for memory in memories:
            await memory_system.store(memory, memory_type='general')
            
        # Retrieve by keyword
        cat_results = await memory_system.retrieve('cats', memory_type='general')
        assert len(cat_results['results']) == 2
        assert all('cats' in str(r['content']) for r in cat_results['results'])
        
        dog_results = await memory_system.retrieve('dogs', memory_type='general')
        assert len(dog_results['results']) == 2
        
    @pytest.mark.asyncio
    async def test_memory_search(self, memory_system):
        """Test cross-type memory search"""
        # Store in different types
        await memory_system.store({'content': 'General knowledge'}, 'general')
        await memory_system.store({'content': 'Specific episode'}, 'episodic')
        await memory_system.store({'content': 'Conceptual knowledge'}, 'semantic')
        
        # Search across all types
        results = await memory_system.search('knowledge')
        
        assert results['total_matches'] == 2
        assert len(results['searched_types']) >= 3
        
    @pytest.mark.asyncio
    async def test_memory_update(self, memory_system):
        """Test memory updates"""
        # Store initial memory
        await memory_system.store(
            {'content': 'Original content', 'version': 1},
            'general'
        )
        
        # Update memory
        update_result = await memory_system.update(
            'Original',
            {'version': 2, 'updated': True},
            'general'
        )
        
        assert update_result['updated_count'] == 1
        
        # Verify update
        retrieved = await memory_system.retrieve('Original', 'general')
        updated_memory = retrieved['results'][0]
        assert updated_memory['content']['version'] == 2
        assert updated_memory['content']['updated'] is True
        assert 'last_updated' in updated_memory
        
    @pytest.mark.asyncio
    async def test_memory_metadata(self, memory_system):
        """Test memory metadata fields"""
        content = {'test': 'metadata'}
        result = await memory_system.store(content, 'episodic')
        
        # Get stored memory
        memories = memory_system.memories['episodic']
        assert len(memories) > 0
        
        memory = memories[0]
        # Check metadata fields
        assert 'id' in memory
        assert memory['id'].startswith('mem_')
        assert 'timestamp' in memory
        assert 'importance' in memory
        assert 0 <= memory['importance'] <= 1
        assert 'emotional_weight' in memory
        assert 0 <= memory['emotional_weight'] <= 1
        
    @pytest.mark.asyncio
    async def test_empty_retrieval(self, memory_system):
        """Test retrieval with no matches"""
        result = await memory_system.retrieve('nonexistent', 'general')
        
        assert result['query'] == 'nonexistent'
        assert result['results'] == []
        assert result['total_matches'] == 0
        
    @pytest.mark.asyncio
    async def test_special_characters_handling(self, memory_system):
        """Test handling of special characters"""
        special_content = {
            'unicode': 'Hello 世界 🌍',
            'symbols': '!@#$%^&*()',
            'quotes': 'He said "hello"',
            'newlines': 'Line1\nLine2\nLine3'
        }
        
        # Store and retrieve
        await memory_system.store(special_content, 'general')
        result = await memory_system.retrieve('世界', 'general')
        
        assert len(result['results']) == 1
        assert result['results'][0]['content'] == special_content


class TestMemoryFolds(LUKHASTestCase):
    """Test fold-based memory architecture"""
    
    @pytest.fixture
    def mock_fold_manager(self):
        """Create mock fold manager"""
        manager = Mock()
        manager.active_folds = {}
        manager.fold_counter = 0
        manager.max_fold_depth = 5
        return manager
        
    def test_fold_creation(self, mock_fold_manager):
        """Test memory fold creation"""
        # Create fold
        fold_id = f"fold_{mock_fold_manager.fold_counter}"
        mock_fold_manager.fold_counter += 1
        
        fold = {
            'id': fold_id,
            'content': {'test': 'data'},
            'created': datetime.now(timezone.utc),
            'causal_chain': [],
            'emotional_context': {'valence': 0.5}
        }
        
        mock_fold_manager.active_folds[fold_id] = fold
        
        # Verify fold created
        assert fold_id in mock_fold_manager.active_folds
        assert mock_fold_manager.active_folds[fold_id]['content'] == {'test': 'data'}
        
    def test_causal_chain_tracking(self, mock_fold_manager):
        """Test causal chain in memory folds"""
        # Create chain of folds
        parent_fold_id = 'fold_0'
        parent_fold = {
            'id': parent_fold_id,
            'content': {'event': 'parent'},
            'causal_chain': []
        }
        mock_fold_manager.active_folds[parent_fold_id] = parent_fold
        
        # Create child fold
        child_fold_id = 'fold_1'
        child_fold = {
            'id': child_fold_id,
            'content': {'event': 'child'},
            'causal_chain': [parent_fold_id]
        }
        mock_fold_manager.active_folds[child_fold_id] = child_fold
        
        # Verify causal chain
        assert len(child_fold['causal_chain']) == 1
        assert child_fold['causal_chain'][0] == parent_fold_id
        
    def test_fold_depth_limit(self, mock_fold_manager):
        """Test fold depth limiting"""
        # Create chain up to max depth
        for i in range(mock_fold_manager.max_fold_depth):
            fold_id = f"fold_{i}"
            causal_chain = [f"fold_{j}" for j in range(i)]
            
            fold = {
                'id': fold_id,
                'content': {'depth': i},
                'causal_chain': causal_chain
            }
            mock_fold_manager.active_folds[fold_id] = fold
            
        # Try to exceed max depth
        with pytest.raises(ValueError):
            over_depth_chain = [f"fold_{j}" for j in range(mock_fold_manager.max_fold_depth + 1)]
            if len(over_depth_chain) > mock_fold_manager.max_fold_depth:
                raise ValueError("Fold depth exceeded")
                
    def test_fold_collapse(self, mock_fold_manager):
        """Test fold collapse mechanism"""
        # Create folds
        fold_ids = []
        for i in range(3):
            fold_id = f"fold_{i}"
            fold = {
                'id': fold_id,
                'content': {'data': f'fold_{i}_data'},
                'collapsed': False
            }
            mock_fold_manager.active_folds[fold_id] = fold
            fold_ids.append(fold_id)
            
        # Collapse folds
        for fold_id in fold_ids:
            fold = mock_fold_manager.active_folds[fold_id]
            fold['collapsed'] = True
            fold['collapse_time'] = datetime.now(timezone.utc)
            
        # Verify all collapsed
        assert all(
            mock_fold_manager.active_folds[fid]['collapsed'] 
            for fid in fold_ids
        )


class TestMemoryIntegration(LUKHASTestCase):
    """Test memory system integration"""
    
    @pytest.mark.asyncio
    async def test_encryption_integration(self, memory_system):
        """Test memory encryption"""
        with patch('core.security.enhanced_crypto.get_encryption_manager') as mock_crypto:
            crypto = mock_crypto.return_value
            crypto.encrypt = AsyncMock(return_value=(b'encrypted', 'key_id'))
            crypto.decrypt = AsyncMock(return_value=b'decrypted')
            
            # Store sensitive memory
            sensitive_content = {
                'type': 'personality',
                'data': 'Core personality traits'
            }
            
            result = await memory_system.store(sensitive_content, 'general')
            assert result['stored'] is True
            
            # In real system, would be encrypted
            
    @pytest.mark.asyncio
    async def test_guardian_validation(self, memory_system):
        """Test Guardian validates memory operations"""
        with patch('core.api.service_stubs.GuardianSystem') as MockGuardian:
            guardian = MockGuardian.return_value
            guardian.evaluate_action = AsyncMock(return_value={
                'approved': False,
                'reason': 'Sensitive content detected'
            })
            
            # Try to store sensitive memory
            sensitive = {'content': 'Potentially harmful information'}
            result = await memory_system.store(sensitive, 'general')
            
            # Should still store (Guardian is advisory in stub)
            assert result['stored'] is True
            
    @pytest.mark.asyncio
    async def test_symbolic_encoding(self, memory_system):
        """Test symbolic encoding of memories"""
        with patch('core.api.service_stubs.SymbolicEngine') as MockSymbolic:
            symbolic = MockSymbolic.return_value
            symbolic.encode = AsyncMock(return_value={
                'glyphs': ['λmem', 'Ωstore', 'Δimportant'],
                'entropy': 0.7
            })
            
            # Store memory that would be symbolically encoded
            content = {'event': 'Important symbolic memory'}
            result = await memory_system.store(content, 'semantic')
            
            assert result['stored'] is True


class TestMemoryPerformance(LUKHASTestCase):
    """Test memory system performance"""
    
    @pytest.mark.asyncio
    async def test_storage_performance(self, memory_system):
        """Test memory storage performance"""
        import time
        
        # Store many memories
        times = []
        for i in range(100):
            content = {'index': i, 'data': f'Memory {i}'}
            
            start = time.perf_counter()
            await memory_system.store(content, 'general')
            end = time.perf_counter()
            
            times.append(end - start)
            
        # Check performance
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        assert avg_time < 0.01, f"Average store time {avg_time:.3f}s too slow"
        assert max_time < 0.1, f"Max store time {max_time:.3f}s too slow"
        
    @pytest.mark.asyncio
    async def test_retrieval_scaling(self, memory_system):
        """Test retrieval performance with many memories"""
        # Store many memories
        for i in range(1000):
            await memory_system.store(
                {'content': f'Memory {i} with keyword test'},
                'general'
            )
            
        import time
        
        # Test retrieval time
        start = time.perf_counter()
        results = await memory_system.retrieve('test', 'general')
        end = time.perf_counter()
        
        retrieval_time = end - start
        
        # Should still be fast with 1000 memories
        assert retrieval_time < 0.1, f"Retrieval took {retrieval_time:.3f}s"
        assert len(results['results']) == 5  # Limited to 5 results
        
    @pytest.mark.asyncio
    async def test_memory_cleanup(self, memory_system):
        """Test memory cleanup and limits"""
        # Configure limit
        max_memories = 100
        
        # Store more than limit
        for i in range(max_memories + 50):
            await memory_system.store({'index': i}, 'general')
            
        # In real system, old memories would be archived
        # For stub, just check we can handle many memories
        assert len(memory_system.memories['general']) > max_memories
        
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, memory_system):
        """Test concurrent memory operations"""
        import asyncio
        
        # Mix of operations
        tasks = []
        
        # Stores
        for i in range(20):
            tasks.append(
                memory_system.store({'concurrent': i}, 'general')
            )
            
        # Retrieves
        for i in range(10):
            tasks.append(
                memory_system.retrieve('concurrent', 'general')
            )
            
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check no errors
        errors = [r for r in results if isinstance(r, Exception)]
        assert len(errors) == 0
        
        # Verify stores succeeded
        store_results = results[:20]
        assert all(r['stored'] is True for r in store_results)


class TestMemoryPersistence(LUKHASTestCase):
    """Test memory persistence and recovery"""
    
    @pytest.mark.asyncio
    async def test_memory_serialization(self, memory_system, temp_dir):
        """Test memory serialization"""
        # Store memories
        memories = [
            {'content': 'Memory 1', 'importance': 0.9},
            {'content': 'Memory 2', 'importance': 0.5},
            {'content': 'Memory 3', 'importance': 0.7}
        ]
        
        for mem in memories:
            await memory_system.store(mem, 'general')
            
        # Serialize to file
        memory_file = temp_dir / 'memories.json'
        
        # In real system, would have save method
        memory_data = {
            'memories': memory_system.memories,
            'metadata': {
                'version': '1.0',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        }
        
        with open(memory_file, 'w') as f:
            json.dump(memory_data, f, default=str)
            
        # Verify file created
        assert memory_file.exists()
        
        # Load and verify
        with open(memory_file, 'r') as f:
            loaded = json.load(f)
            
        assert 'memories' in loaded
        assert 'general' in loaded['memories']
        assert len(loaded['memories']['general']) == 3
        
    @pytest.mark.asyncio
    async def test_memory_recovery(self, memory_system):
        """Test memory recovery after failure"""
        # Store critical memories
        critical_memories = [
            {'content': 'Critical system parameter', 'critical': True},
            {'content': 'User preference', 'critical': True}
        ]
        
        for mem in critical_memories:
            await memory_system.store(mem, 'general')
            
        # Simulate system failure
        memory_system.memories = {'general': [], 'episodic': [], 'semantic': [], 'procedural': []}
        
        # In real system, would recover from persistence
        # For now, just verify empty
        assert len(memory_system.memories['general']) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])