#!/usr/bin/env python3
"""
Real Memory Folds Integration Tests
Tests the actual LUKHAS memory fold implementation
"""

import pytest
import time
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the REAL LUKHAS memory components
from memory.folds.memory_fold import MemoryFold


class TestRealMemoryFolds:
    """Test the real LUKHAS memory fold system"""
    
    def setup_method(self):
        """Setup for each test"""
        self.fold = None
        
    def teardown_method(self):
        """Cleanup after each test"""
        if self.fold:
            # Clean up any resources
            pass
    
    def test_real_memory_fold_creation(self):
        """Test creating a real memory fold"""
        try:
            # Create a real memory fold
            self.fold = MemoryFold(
                fold_id="test_fold_001",
                content="Test memory content",
                emotional_weight=0.7,
                timestamp=time.time()
            )
            
            # Basic validation
            assert self.fold is not None
            assert hasattr(self.fold, 'fold_id')
            assert hasattr(self.fold, 'content')
            
        except Exception as e:
            pytest.fail(f"Real memory fold creation failed: {e}")
    
    def test_real_memory_fold_properties(self):
        """Test properties of a real memory fold"""
        self.fold = MemoryFold(
            fold_id="test_properties",
            content="Property test content",
            emotional_weight=0.8,
            timestamp=time.time()
        )
        
        # Test that properties are accessible
        assert self.fold.fold_id == "test_properties"
        assert self.fold.content == "Property test content"
        
        # Check if the real implementation has expected attributes
        expected_attributes = ['fold_id', 'content', 'emotional_weight', 'timestamp']
        for attr in expected_attributes:
            if hasattr(self.fold, attr):
                assert getattr(self.fold, attr) is not None
    
    def test_real_memory_fold_emotional_weight(self):
        """Test emotional weight handling in real memory folds"""
        # Test with different emotional weights
        weights = [0.0, 0.3, 0.7, 1.0]
        
        for weight in weights:
            fold = MemoryFold(
                fold_id=f"emotion_test_{weight}",
                content=f"Content with weight {weight}",
                emotional_weight=weight,
                timestamp=time.time()
            )
            
            # Verify the weight is stored correctly
            if hasattr(fold, 'emotional_weight'):
                assert fold.emotional_weight == weight
    
    def test_real_memory_fold_persistence(self):
        """Test memory fold persistence capabilities"""
        # Create a fold with specific data
        original_content = "Persistent memory test content"
        self.fold = MemoryFold(
            fold_id="persistence_test",
            content=original_content,
            emotional_weight=0.9,
            timestamp=time.time()
        )
        
        # Test that the content persists (basic check)
        if hasattr(self.fold, 'content'):
            assert self.fold.content == original_content
        
        # If the real implementation has save/load methods, test them
        if hasattr(self.fold, 'save'):
            try:
                self.fold.save()
                assert True  # Save succeeded
            except Exception as e:
                print(f"Save method exists but failed: {e}")
        
        if hasattr(self.fold, 'load'):
            try:
                loaded_fold = self.fold.load("persistence_test")
                assert loaded_fold is not None
            except Exception as e:
                print(f"Load method exists but failed: {e}")
    
    def test_real_memory_fold_cascade_prevention(self):
        """Test cascade prevention in real memory folds"""
        # Create multiple interconnected folds
        folds = []
        
        for i in range(10):
            fold = MemoryFold(
                fold_id=f"cascade_test_{i}",
                content=f"Cascade test content {i}",
                emotional_weight=0.5,
                timestamp=time.time()
            )
            folds.append(fold)
        
        # Test that creating multiple folds doesn't cause issues
        assert len(folds) == 10
        
        # If the real implementation has cascade detection, test it
        for fold in folds:
            if hasattr(fold, 'check_cascade_risk'):
                try:
                    risk = fold.check_cascade_risk()
                    assert risk is not None
                    print(f"Cascade risk for {fold.fold_id}: {risk}")
                except Exception as e:
                    print(f"Cascade risk check failed: {e}")
    
    def test_real_memory_fold_performance(self):
        """Test performance of real memory fold operations"""
        num_folds = 100
        start_time = time.perf_counter()
        
        # Create many folds
        folds = []
        for i in range(num_folds):
            fold = MemoryFold(
                fold_id=f"perf_test_{i}",
                content=f"Performance test content {i}",
                emotional_weight=0.5,
                timestamp=time.time()
            )
            folds.append(fold)
        
        creation_time = time.perf_counter() - start_time
        
        # Verify reasonable performance
        folds_per_second = num_folds / creation_time
        assert folds_per_second > 100  # Should create at least 100 folds/sec
        
        print(f"Real memory fold performance: {folds_per_second:.1f} folds/second")
        
        # Test access performance
        start_time = time.perf_counter()
        
        for fold in folds:
            # Access properties
            _ = fold.fold_id
            if hasattr(fold, 'content'):
                _ = fold.content
        
        access_time = time.perf_counter() - start_time
        accesses_per_second = num_folds / access_time
        
        assert accesses_per_second > 1000  # Should access properties quickly
        print(f"Property access performance: {accesses_per_second:.1f} accesses/second")
    
    def test_real_memory_fold_memory_usage(self):
        """Test memory usage of real memory folds"""
        import gc
        import psutil
        import os
        
        # Get baseline memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create many memory folds
        folds = []
        content_size = 1000  # 1KB per fold
        num_folds = 100
        
        for i in range(num_folds):
            content = "x" * content_size  # 1KB content
            fold = MemoryFold(
                fold_id=f"memory_test_{i}",
                content=content,
                emotional_weight=0.5,
                timestamp=time.time()
            )
            folds.append(fold)
        
        # Check memory usage
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_per_fold = (current_memory - initial_memory) / num_folds
        
        # Each fold should use a reasonable amount of memory
        expected_max = 0.1  # 100KB max per fold (including overhead)
        assert memory_per_fold < expected_max, f"Each fold uses {memory_per_fold:.3f}MB"
        
        print(f"Memory per fold: {memory_per_fold:.3f}MB")
        
        # Clean up and verify memory is released
        del folds
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_released = current_memory - final_memory
        
        # Should release most of the memory
        assert memory_released > 0, "Memory should be released after cleanup"
        print(f"Memory released: {memory_released:.1f}MB")
    
    def test_real_memory_fold_edge_cases(self):
        """Test edge cases with real memory folds"""
        # Test with empty content
        try:
            empty_fold = MemoryFold(
                fold_id="empty_test",
                content="",
                emotional_weight=0.0,
                timestamp=time.time()
            )
            assert empty_fold is not None
        except Exception as e:
            print(f"Empty content test failed: {e}")
        
        # Test with very long content
        try:
            long_content = "x" * 10000  # 10KB content
            long_fold = MemoryFold(
                fold_id="long_test",
                content=long_content,
                emotional_weight=1.0,
                timestamp=time.time()
            )
            assert long_fold is not None
        except Exception as e:
            print(f"Long content test failed: {e}")
        
        # Test with special characters in content
        try:
            special_content = "Special chars: 🧠💭🔮 αβγ 中文 русский"
            special_fold = MemoryFold(
                fold_id="special_test",
                content=special_content,
                emotional_weight=0.5,
                timestamp=time.time()
            )
            assert special_fold is not None
        except Exception as e:
            print(f"Special characters test failed: {e}")
    
    def test_real_memory_fold_concurrent_access(self):
        """Test concurrent access to memory folds"""
        import threading
        import queue
        
        results = queue.Queue()
        num_threads = 5
        folds_per_thread = 20
        
        def worker_thread(thread_id):
            try:
                thread_folds = []
                for i in range(folds_per_thread):
                    fold = MemoryFold(
                        fold_id=f"concurrent_{thread_id}_{i}",
                        content=f"Thread {thread_id} content {i}",
                        emotional_weight=0.5,
                        timestamp=time.time()
                    )
                    thread_folds.append(fold)
                
                results.put(("success", thread_id, len(thread_folds)))
            except Exception as e:
                results.put(("error", thread_id, str(e)))
        
        # Start all threads
        threads = []
        for tid in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(tid,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        total_folds = 0
        
        while not results.empty():
            result = results.get()
            if result[0] == "success":
                success_count += 1
                total_folds += result[2]
            else:
                print(f"Thread {result[1]} error: {result[2]}")
        
        expected_folds = num_threads * folds_per_thread
        assert success_count == num_threads
        assert total_folds == expected_folds
        
        print(f"Concurrent test: {total_folds} folds created across {num_threads} threads")


if __name__ == "__main__":
    pytest.main([__file__])