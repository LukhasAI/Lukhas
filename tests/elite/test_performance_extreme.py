#!/usr/bin/env python3
"""
Elite Performance & Stress Tests
Pushing systems to their absolute limits
"""

import pytest
import asyncio
import threading
import multiprocessing
import gc
import weakref
import tracemalloc
import cProfile
import pstats
import io
import resource
import time
import random
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
import sys
import os
import psutil
import socket
from typing import List, Dict, Any
from dataclasses import dataclass
from functools import lru_cache
import hashlib

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestPerformanceExtreme:
    """Elite performance tests - memory leaks, deadlocks, resource exhaustion"""
    
    def test_memory_leak_detection(self):
        """Detect memory leaks in object lifecycle"""
        tracemalloc.start()
        
        class LeakyClass:
            def __init__(self):
                self.data = bytearray(10 ** 6)  # 1MB
                self.circular_ref = self  # Circular reference
        
        # Create objects that should be garbage collected
        objects = []
        for i in range(100):
            obj = LeakyClass()
            objects.append(weakref.ref(obj))
            del obj
        
        # Force garbage collection
        gc.collect()
        
        # Check if objects were properly cleaned up
        leaked = sum(1 for ref in objects if ref() is not None)
        
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        # Should have minimal leaks
        assert leaked > 50  # This demonstrates the leak
        
        tracemalloc.stop()
    
    def test_cache_stampede_thundering_herd(self):
        """Test cache stampede problem"""
        cache = {}
        computation_count = {'count': 0}
        
        def expensive_computation(key):
            """Simulate expensive computation"""
            computation_count['count'] += 1
            time.sleep(0.1)  # Simulate slow computation
            return f"result_{key}"
        
        def get_or_compute(key):
            if key not in cache:
                # Multiple threads hit this simultaneously
                result = expensive_computation(key)
                cache[key] = result
            return cache[key]
        
        # Simulate thundering herd
        num_threads = 50
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(get_or_compute, "same_key") 
                      for _ in range(num_threads)]
            results = [f.result() for f in futures]
        
        # Without proper locking, computation happens multiple times
        assert computation_count['count'] > 1  # Demonstrates the problem
    
    def test_deadlock_detection_multiple_locks(self):
        """Test deadlock scenarios with multiple locks"""
        lock1 = threading.Lock()
        lock2 = threading.Lock()
        deadlock_detected = {'detected': False}
        
        def thread1_func():
            with lock1:
                time.sleep(0.01)
                # Try to acquire lock2 while holding lock1
                if not lock2.acquire(timeout=0.1):
                    deadlock_detected['detected'] = True
        
        def thread2_func():
            with lock2:
                time.sleep(0.01)
                # Try to acquire lock1 while holding lock2
                if not lock1.acquire(timeout=0.1):
                    deadlock_detected['detected'] = True
        
        t1 = threading.Thread(target=thread1_func)
        t2 = threading.Thread(target=thread2_func)
        
        t1.start()
        t2.start()
        
        t1.join(timeout=1)
        t2.join(timeout=1)
        
        # Deadlock should be detected
        assert deadlock_detected['detected']
    
    def test_cpu_cache_false_sharing(self):
        """Test false sharing performance degradation"""
        import array
        
        # Create array where adjacent elements are on same cache line
        shared_array = array.array('i', [0] * 16)
        
        def increment_position(arr, index, iterations):
            for _ in range(iterations):
                arr[index] += 1
        
        iterations = 1000000
        
        # Test false sharing (adjacent elements)
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Threads work on adjacent elements (same cache line)
            f1 = executor.submit(increment_position, shared_array, 0, iterations)
            f2 = executor.submit(increment_position, shared_array, 1, iterations)
            f1.result()
            f2.result()
        false_sharing_time = time.perf_counter() - start
        
        # Test without false sharing (distant elements)
        shared_array = array.array('i', [0] * 128)
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Threads work on distant elements (different cache lines)
            f1 = executor.submit(increment_position, shared_array, 0, iterations)
            f2 = executor.submit(increment_position, shared_array, 64, iterations)
            f1.result()
            f2.result()
        no_false_sharing_time = time.perf_counter() - start
        
        # False sharing should be slower
        assert false_sharing_time > no_false_sharing_time * 0.8
    
    @pytest.mark.asyncio
    async def test_async_task_explosion(self):
        """Test system behavior with thousands of async tasks"""
        tasks_created = {'count': 0}
        max_concurrent = {'max': 0}
        current_running = {'count': 0}
        
        async def task_func(task_id):
            tasks_created['count'] += 1
            current_running['count'] += 1
            max_concurrent['max'] = max(max_concurrent['max'], current_running['count'])
            
            await asyncio.sleep(random.uniform(0.001, 0.01))
            
            current_running['count'] -= 1
            return task_id
        
        # Create explosion of tasks
        num_tasks = 10000
        start = time.perf_counter()
        
        tasks = [task_func(i) for i in range(num_tasks)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.perf_counter() - start
        
        # Should handle massive concurrency
        assert tasks_created['count'] == num_tasks
        assert max_concurrent['max'] > 100  # High concurrency
        assert elapsed < 5  # Should complete quickly
    
    def test_gc_pathological_case(self):
        """Test garbage collector with pathological cases"""
        gc.disable()  # Disable automatic GC
        
        # Create deeply nested circular references
        def create_circular_chain(depth):
            if depth == 0:
                return []
            obj = {'data': bytearray(1000), 'next': None}
            obj['next'] = create_circular_chain(depth - 1)
            obj['self'] = obj  # Self-reference
            return obj
        
        # Create many circular structures
        chains = []
        for _ in range(100):
            chains.append(create_circular_chain(100))
        
        # Measure GC time
        start = time.perf_counter()
        collected = gc.collect()  # Force collection
        gc_time = time.perf_counter() - start
        
        gc.enable()
        
        # Pathological case should take measurable time
        assert gc_time > 0.01
        assert collected > 0
    
    def test_lock_convoy_problem(self):
        """Test lock convoy performance problem"""
        lock = threading.Lock()
        counter = {'value': 0}
        convoy_detected = False
        
        def worker(worker_id, iterations):
            timings = []
            for i in range(iterations):
                start = time.perf_counter()
                with lock:
                    counter['value'] += 1
                    # Simulate work while holding lock
                    time.sleep(0.0001)
                elapsed = time.perf_counter() - start
                timings.append(elapsed)
            
            # Check if this thread experienced convoy (increasing wait times)
            avg_first_half = sum(timings[:len(timings)//2]) / (len(timings)//2)
            avg_second_half = sum(timings[len(timings)//2:]) / (len(timings)//2)
            
            return avg_second_half > avg_first_half * 1.5
        
        # Run multiple threads
        num_threads = 10
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, i, 100) for i in range(num_threads)]
            results = [f.result() for f in futures]
        
        # Some threads should experience convoy effect
        convoy_detected = any(results)
        assert convoy_detected
    
    def test_memory_fragmentation(self):
        """Test memory fragmentation issues"""
        allocations = []
        
        # Create fragmented memory pattern
        for i in range(1000):
            # Allocate varying sizes to cause fragmentation
            size = random.randint(1000, 100000)
            data = bytearray(size)
            allocations.append(data)
            
            # Randomly free some allocations
            if random.random() > 0.5 and len(allocations) > 10:
                index = random.randint(0, len(allocations) - 1)
                del allocations[index]
        
        # Measure memory usage
        process = psutil.Process()
        memory_info = process.memory_info()
        rss = memory_info.rss / (1024 * 1024)  # MB
        
        # Calculate actual data size
        actual_size = sum(len(a) for a in allocations) / (1024 * 1024)  # MB
        
        # Fragmentation causes higher memory usage than actual data
        overhead_ratio = rss / actual_size if actual_size > 0 else 1
        assert overhead_ratio > 1.2  # At least 20% overhead
    
    def test_connection_pool_exhaustion(self):
        """Test connection pool exhaustion scenario"""
        class ConnectionPool:
            def __init__(self, max_size=10):
                self.max_size = max_size
                self.connections = []
                self.available = threading.Semaphore(max_size)
                self.exhausted_count = 0
            
            def get_connection(self, timeout=0.1):
                if not self.available.acquire(timeout=timeout):
                    self.exhausted_count += 1
                    raise Exception("Pool exhausted")
                return f"conn_{len(self.connections)}"
            
            def return_connection(self, conn):
                self.available.release()
        
        pool = ConnectionPool(max_size=5)
        
        def greedy_worker():
            """Worker that holds connections too long"""
            conns = []
            try:
                # Try to grab multiple connections
                for _ in range(3):
                    conns.append(pool.get_connection())
                time.sleep(0.2)  # Hold them
            except:
                pass
            finally:
                for conn in conns:
                    pool.return_connection(conn)
        
        # Launch many greedy workers
        threads = [threading.Thread(target=greedy_worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Pool should have been exhausted
        assert pool.exhausted_count > 0
    
    def test_branch_prediction_performance(self):
        """Test CPU branch prediction impact"""
        import random
        
        # Sorted array (predictable branches)
        sorted_array = list(range(10000))
        
        # Random array (unpredictable branches)
        random_array = sorted_array.copy()
        random.shuffle(random_array)
        
        def sum_if_greater(arr, threshold):
            total = 0
            for val in arr:
                if val > threshold:  # Branch
                    total += val
            return total
        
        threshold = 5000
        
        # Measure sorted array (good branch prediction)
        start = time.perf_counter()
        for _ in range(100):
            sum_if_greater(sorted_array, threshold)
        sorted_time = time.perf_counter() - start
        
        # Measure random array (poor branch prediction)
        start = time.perf_counter()
        for _ in range(100):
            sum_if_greater(random_array, threshold)
        random_time = time.perf_counter() - start
        
        # Random should be slower due to branch misprediction
        assert random_time > sorted_time
    
    def test_thread_local_storage_overhead(self):
        """Test thread-local storage performance overhead"""
        import threading
        
        # Global variable (fast)
        global_counter = {'value': 0}
        
        # Thread-local variable (overhead)
        thread_local = threading.local()
        
        def increment_global(iterations):
            for _ in range(iterations):
                global_counter['value'] += 1
        
        def increment_thread_local(iterations):
            thread_local.value = 0
            for _ in range(iterations):
                thread_local.value += 1
            return thread_local.value
        
        iterations = 1000000
        
        # Measure global access
        start = time.perf_counter()
        increment_global(iterations)
        global_time = time.perf_counter() - start
        
        # Measure thread-local access
        start = time.perf_counter()
        increment_thread_local(iterations)
        thread_local_time = time.perf_counter() - start
        
        # Thread-local should have overhead
        assert thread_local_time > global_time
    
    def test_network_buffer_bloat(self):
        """Test network buffer bloat issues"""
        # Simulate large buffer causing latency
        buffer_size = 10 * 1024 * 1024  # 10MB buffer
        data_queue = []
        
        def simulate_network_send(data, buffer_size):
            """Simulate sending data through buffered network"""
            buffer = []
            send_times = []
            
            for chunk in data:
                buffer.append(chunk)
                buffer_bytes = sum(len(c) for c in buffer)
                
                # When buffer fills, "send" it
                if buffer_bytes >= buffer_size:
                    start = time.perf_counter()
                    time.sleep(0.1)  # Simulate network delay
                    send_time = time.perf_counter() - start
                    send_times.append(send_time)
                    buffer.clear()
            
            return send_times
        
        # Generate data chunks
        chunks = [b"x" * 1024 for _ in range(10000)]  # 10MB total
        
        # Large buffer (bloated)
        large_buffer_times = simulate_network_send(chunks, 10 * 1024 * 1024)
        
        # Small buffer (responsive)
        small_buffer_times = simulate_network_send(chunks, 64 * 1024)
        
        # Large buffer should have higher latency spikes
        if large_buffer_times and small_buffer_times:
            assert max(large_buffer_times) > max(small_buffer_times)
    
    def test_spinlock_vs_mutex_performance(self):
        """Test spinlock vs mutex in different scenarios"""
        import threading
        
        class SpinLock:
            def __init__(self):
                self._lock = threading.Lock()
            
            def acquire(self):
                while not self._lock.acquire(blocking=False):
                    pass  # Spin
            
            def release(self):
                self._lock.release()
        
        spinlock = SpinLock()
        mutex = threading.Lock()
        
        def critical_section_short():
            """Very short critical section (good for spinlock)"""
            x = 1 + 1
        
        def critical_section_long():
            """Long critical section (bad for spinlock)"""
            time.sleep(0.001)
        
        def worker_spinlock(iterations, work_func):
            for _ in range(iterations):
                spinlock.acquire()
                work_func()
                spinlock.release()
        
        def worker_mutex(iterations, work_func):
            for _ in range(iterations):
                with mutex:
                    work_func()
        
        # Test with short critical section
        iterations = 1000
        
        # Spinlock with short work
        start = time.perf_counter()
        threads = [threading.Thread(target=worker_spinlock, 
                                   args=(iterations, critical_section_short)) 
                  for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        spinlock_short_time = time.perf_counter() - start
        
        # Mutex with short work
        start = time.perf_counter()
        threads = [threading.Thread(target=worker_mutex, 
                                   args=(iterations, critical_section_short)) 
                  for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        mutex_short_time = time.perf_counter() - start
        
        # For very short critical sections, spinlock might be faster
        # For long critical sections, mutex should be much better
        assert spinlock_short_time < mutex_short_time * 2  # Not terrible for short work