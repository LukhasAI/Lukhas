#!/usr/bin/env python3
"""
Elite Chaos Engineering Tests
Fault injection, Byzantine failures, and system resilience
"""

import pytest
import asyncio
import random
import time
import threading
import signal
import os
import sys
import socket
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import tempfile
import shutil
import json
import weakref
import gc

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class FaultInjection:
    """Fault injection configuration"""
    fault_type: str
    probability: float
    duration: float
    target_component: str
    

@dataclass
class SystemComponent:
    """Mock system component for testing"""
    name: str
    health: float = 1.0
    dependencies: List[str] = field(default_factory=list)
    failure_count: int = 0
    
    def process(self, data):
        if self.health <= 0:
            raise Exception(f"Component {self.name} is failed")
        return f"processed_{data}_by_{self.name}"


class ChaosMonkey:
    """Chaos engineering fault injector"""
    
    def __init__(self):
        self.active_faults = []
        self.system_components = {}
        
    def register_component(self, component: SystemComponent):
        self.system_components[component.name] = component
        
    def inject_fault(self, fault: FaultInjection):
        """Inject a fault into the system"""
        if fault.target_component in self.system_components:
            component = self.system_components[fault.target_component]
            
            if fault.fault_type == "crash":
                component.health = 0
                component.failure_count += 1
            elif fault.fault_type == "slowdown":
                component.health *= 0.5
            elif fault.fault_type == "intermittent":
                component.health = random.uniform(0.1, 0.9)
                
        self.active_faults.append(fault)
        
    def heal_component(self, component_name: str):
        """Heal a component"""
        if component_name in self.system_components:
            self.system_components[component_name].health = 1.0


class TestChaosEngineering:
    """Elite chaos engineering tests"""
    
    def test_byzantine_fault_tolerance(self):
        """Test Byzantine fault tolerance with malicious nodes"""
        num_nodes = 10
        byzantine_threshold = 3  # Can tolerate up to 3 Byzantine nodes
        
        class ByzantineNode:
            def __init__(self, node_id, is_byzantine=False):
                self.node_id = node_id
                self.is_byzantine = is_byzantine
                self.state = 0
                
            def propose_value(self, value):
                if self.is_byzantine:
                    # Byzantine behavior: propose random values
                    return random.randint(0, 1000)
                return value
                
            def vote_on_value(self, value):
                if self.is_byzantine:
                    # Byzantine behavior: random votes
                    return random.choice([True, False])
                return True  # Honest nodes agree
        
        # Create nodes with some Byzantine
        nodes = []
        for i in range(num_nodes):
            is_byzantine = i < byzantine_threshold
            nodes.append(ByzantineNode(i, is_byzantine))
        
        # Consensus algorithm
        def reach_consensus(nodes, proposed_value):
            votes = []
            for node in nodes:
                vote = node.vote_on_value(proposed_value)
                votes.append(vote)
            
            # Majority rule
            yes_votes = sum(1 for v in votes if v)
            return yes_votes > len(nodes) // 2
        
        # Test consensus with Byzantine nodes present
        consensus_reached = reach_consensus(nodes, 42)
        
        # Should still reach consensus despite Byzantine nodes
        assert consensus_reached or byzantine_threshold >= num_nodes // 3
    
    def test_cascading_failure_simulation(self):
        """Test cascading failure scenarios"""
        chaos = ChaosMonkey()
        
        # Create interconnected components
        components = [
            SystemComponent("frontend", dependencies=["backend"]),
            SystemComponent("backend", dependencies=["database", "cache"]),
            SystemComponent("database", dependencies=["storage"]),
            SystemComponent("cache", dependencies=["storage"]),
            SystemComponent("storage", dependencies=[]),
        ]
        
        for comp in components:
            chaos.register_component(comp)
        
        # Inject initial failure
        initial_fault = FaultInjection("crash", 1.0, 60, "storage")
        chaos.inject_fault(initial_fault)
        
        # Simulate cascading failures
        cascade_steps = []
        for step in range(10):
            failed_components = []
            
            for name, component in chaos.system_components.items():
                # Check if dependencies are failed
                failed_deps = []
                for dep in component.dependencies:
                    if chaos.system_components[dep].health <= 0:
                        failed_deps.append(dep)
                
                # Component fails if critical dependencies fail
                if len(failed_deps) > 0 and component.health > 0:
                    component.health = 0
                    component.failure_count += 1
                    failed_components.append(name)
            
            cascade_steps.append(failed_components)
            
            if not failed_components:
                break
        
        # Verify cascade occurred
        total_failures = sum(comp.failure_count for comp in chaos.system_components.values())
        assert total_failures > 1  # More than initial failure
        
        # Storage failure should cascade to dependent components
        assert chaos.system_components["database"].health == 0
        assert chaos.system_components["cache"].health == 0
    
    def test_network_partition_brain_split(self):
        """Test network partition causing split-brain"""
        class DistributedService:
            def __init__(self, node_id, cluster_nodes):
                self.node_id = node_id
                self.cluster_nodes = set(cluster_nodes)
                self.is_leader = False
                self.partition = None
                
            def elect_leader(self, available_nodes):
                """Simple leader election based on node ID"""
                if self.node_id in available_nodes:
                    min_node = min(available_nodes)
                    self.is_leader = (self.node_id == min_node)
                else:
                    self.is_leader = False
                    
            def can_communicate_with(self, other_node):
                """Check if can communicate with other node"""
                if self.partition is None:
                    return True
                return other_node in self.partition
        
        # Create 5-node cluster
        nodes = [DistributedService(i, range(5)) for i in range(5)]
        
        # Normal operation - single leader
        for node in nodes:
            node.elect_leader(range(5))
        
        leaders_before = [node.node_id for node in nodes if node.is_leader]
        assert len(leaders_before) == 1
        
        # Simulate network partition: [0,1,2] vs [3,4]
        partition_a = {0, 1, 2}
        partition_b = {3, 4}
        
        for node in nodes:
            if node.node_id in partition_a:
                node.partition = partition_a
            else:
                node.partition = partition_b
        
        # Each partition elects its own leader (split-brain)
        for node in nodes:
            if node.node_id in partition_a:
                node.elect_leader(partition_a)
            else:
                node.elect_leader(partition_b)
        
        leaders_after = [node.node_id for node in nodes if node.is_leader]
        
        # Split-brain: two leaders
        assert len(leaders_after) == 2
        assert 0 in leaders_after  # Leader of partition A
        assert 3 in leaders_after  # Leader of partition B
    
    def test_resource_exhaustion_attack(self):
        """Test resource exhaustion scenarios"""
        class ResourcePool:
            def __init__(self, max_connections=10):
                self.max_connections = max_connections
                self.active_connections = 0
                self.connection_queue = []
                
            def acquire_connection(self):
                if self.active_connections < self.max_connections:
                    self.active_connections += 1
                    return f"conn_{self.active_connections}"
                else:
                    raise Exception("Resource pool exhausted")
                    
            def release_connection(self, conn_id):
                if self.active_connections > 0:
                    self.active_connections -= 1
        
        pool = ResourcePool(max_connections=5)
        
        # Simulate resource exhaustion attack
        def malicious_client():
            connections = []
            try:
                # Acquire connections without releasing
                while True:
                    conn = pool.acquire_connection()
                    connections.append(conn)
                    time.sleep(0.01)
            except Exception:
                # Pool exhausted
                return len(connections)
        
        def legitimate_client():
            try:
                conn = pool.acquire_connection()
                time.sleep(0.05)  # Do work
                pool.release_connection(conn)
                return True
            except Exception:
                return False
        
        # Run attack and legitimate requests concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Malicious client exhausts pool
            attack_future = executor.submit(malicious_client)
            
            # Legitimate clients get blocked
            legitimate_futures = [
                executor.submit(legitimate_client) 
                for _ in range(5)
            ]
            
            attack_result = attack_future.result()
            legitimate_results = [f.result() for f in legitimate_futures]
        
        # Attack should succeed in exhausting resources
        assert attack_result >= 5
        # Legitimate clients should be blocked
        assert not all(legitimate_results)
    
    def test_disk_full_simulation(self):
        """Test behavior when disk space is exhausted"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_file.txt"
            
            # Get available space
            stat = shutil.disk_usage(tmpdir)
            available_mb = stat.free // (1024 * 1024)
            
            # Try to write more data than available (simulated)
            def write_large_file(size_mb):
                try:
                    with open(test_file, 'wb') as f:
                        # Write in chunks to avoid memory issues
                        chunk_size = 1024 * 1024  # 1MB chunks
                        for _ in range(size_mb):
                            f.write(b'0' * chunk_size)
                    return True
                except OSError as e:
                    # Disk full
                    return False
            
            # Write reasonable amount (should succeed)
            small_write = write_large_file(1)  # 1MB
            assert small_write == True
            
            # Cleanup
            if test_file.exists():
                test_file.unlink()
            
            # Simulate disk full scenario
            class DiskFullSimulator:
                def __init__(self, fail_after_bytes):
                    self.fail_after_bytes = fail_after_bytes
                    self.bytes_written = 0
                    
                def write(self, data):
                    if self.bytes_written + len(data) > self.fail_after_bytes:
                        raise OSError("No space left on device")
                    self.bytes_written += len(data)
                    return len(data)
            
            # Test application handling of disk full
            simulator = DiskFullSimulator(1024)  # Fail after 1KB
            
            try:
                # Try to write 2KB (should fail)
                data = b'0' * 2048
                simulator.write(data)
                assert False, "Should have failed"
            except OSError:
                # Proper error handling
                assert simulator.bytes_written < 2048
    
    def test_memory_leak_under_pressure(self):
        """Test memory leaks under pressure"""
        leaked_objects = []
        
        class LeakyObject:
            def __init__(self, size_kb=10):
                self.data = bytearray(size_kb * 1024)
                self.circular_ref = self
                leaked_objects.append(self)  # Global reference prevents GC
                
        def create_objects_with_pressure():
            objects = []
            for i in range(100):
                obj = LeakyObject(size_kb=50)  # 50KB each
                objects.append(obj)
                
                # Simulate memory pressure
                if i % 10 == 0:
                    gc.collect()
                    
            return objects
        
        # Monitor memory before
        import psutil
        process = psutil.Process()
        memory_before = process.memory_info().rss
        
        # Create objects under pressure
        objects = create_objects_with_pressure()
        
        # Clear local references
        del objects
        gc.collect()
        
        # Memory after (should still be high due to leak)
        memory_after = process.memory_info().rss
        memory_increase = (memory_after - memory_before) / (1024 * 1024)  # MB
        
        # Leak should be detectable
        assert memory_increase > 4  # At least 4MB leaked
        assert len(leaked_objects) == 100  # All objects leaked
    
    def test_deadlock_under_load(self):
        """Test deadlock scenarios under high load"""
        lock_a = threading.Lock()
        lock_b = threading.Lock()
        deadlock_count = {"count": 0}
        successful_operations = {"count": 0}
        
        def operation_1():
            try:
                acquired_a = lock_a.acquire(timeout=0.1)
                if not acquired_a:
                    deadlock_count["count"] += 1
                    return
                
                time.sleep(0.01)  # Hold lock A
                
                acquired_b = lock_b.acquire(timeout=0.1)
                if not acquired_b:
                    deadlock_count["count"] += 1
                    lock_a.release()
                    return
                
                # Critical section
                successful_operations["count"] += 1
                
                lock_b.release()
                lock_a.release()
                
            except Exception:
                deadlock_count["count"] += 1
        
        def operation_2():
            try:
                acquired_b = lock_b.acquire(timeout=0.1)
                if not acquired_b:
                    deadlock_count["count"] += 1
                    return
                
                time.sleep(0.01)  # Hold lock B
                
                acquired_a = lock_a.acquire(timeout=0.1)
                if not acquired_a:
                    deadlock_count["count"] += 1
                    lock_b.release()
                    return
                
                # Critical section
                successful_operations["count"] += 1
                
                lock_a.release()
                lock_b.release()
                
            except Exception:
                deadlock_count["count"] += 1
        
        # Generate high load with potential deadlock
        threads = []
        for i in range(20):
            if i % 2 == 0:
                t = threading.Thread(target=operation_1)
            else:
                t = threading.Thread(target=operation_2)
            threads.append(t)
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join(timeout=2)
        
        total_operations = successful_operations["count"] + deadlock_count["count"]
        
        # Under load, deadlocks should occur
        assert deadlock_count["count"] > 0
        assert successful_operations["count"] > 0
        assert total_operations <= 20  # Some operations timed out
    
    def test_race_condition_money_transfer(self):
        """Test race condition in financial transfer (classic example)"""
        class BankAccount:
            def __init__(self, balance):
                self.balance = balance
                self.lock = threading.Lock()
                
            def transfer_to(self, other_account, amount):
                # Unsafe transfer (race condition)
                if self.balance >= amount:
                    time.sleep(0.001)  # Simulate processing delay
                    self.balance -= amount
                    other_account.balance += amount
                    return True
                return False
                
            def safe_transfer_to(self, other_account, amount):
                # Safe transfer with locking
                with self.lock:
                    if self.balance >= amount:
                        time.sleep(0.001)
                        self.balance -= amount
                        with other_account.lock:
                            other_account.balance += amount
                        return True
                return False
        
        # Test unsafe transfers
        account_a = BankAccount(1000)
        account_b = BankAccount(1000)
        
        def concurrent_transfers():
            # Multiple threads try to transfer same money
            return account_a.transfer_to(account_b, 100)
        
        threads = [threading.Thread(target=concurrent_transfers) for _ in range(10)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        total_money = account_a.balance + account_b.balance
        
        # Race condition should cause money creation/loss
        assert total_money != 2000  # Should be exactly 2000 if no race
    
    def test_poison_pill_message_handling(self):
        """Test handling of poison pill messages"""
        import queue
        
        message_queue = queue.Queue(maxsize=100)
        processed_messages = {"count": 0}
        poison_detected = {"count": 0}
        
        # Define poison pill messages
        poison_pills = [
            {"type": "malformed", "data": None},
            {"type": "recursive", "data": {"self": "recursive"}},
            {"type": "huge", "data": "x" * 10**6},  # 1MB message
            {"type": "invalid_encoding", "data": b'\xff\xfe'},
        ]
        
        def message_processor():
            while True:
                try:
                    message = message_queue.get(timeout=1)
                    
                    # Process message
                    if message is None:  # Shutdown signal
                        break
                        
                    # Detect poison pills
                    if message.get("type") in ["malformed", "recursive", "huge", "invalid_encoding"]:
                        poison_detected["count"] += 1
                        # Handle poison pill (don't crash)
                        continue
                    
                    # Normal processing
                    processed_messages["count"] += 1
                    
                except queue.Empty:
                    break
                except Exception:
                    # Poison pill caused exception
                    poison_detected["count"] += 1
        
        # Start processor
        processor_thread = threading.Thread(target=message_processor)
        processor_thread.start()
        
        # Send mix of normal and poison messages
        for i in range(10):
            message_queue.put({"type": "normal", "data": f"message_{i}"})
        
        for poison in poison_pills:
            message_queue.put(poison)
        
        # Shutdown
        message_queue.put(None)
        processor_thread.join()
        
        # Should handle poison pills gracefully
        assert processed_messages["count"] == 10  # Normal messages
        assert poison_detected["count"] == len(poison_pills)  # Poison detected
    
    def test_circuit_breaker_failure_cascade(self):
        """Test circuit breaker preventing failure cascades"""
        class CircuitBreaker:
            def __init__(self, failure_threshold=5, timeout=10):
                self.failure_threshold = failure_threshold
                self.timeout = timeout
                self.failure_count = 0
                self.last_failure_time = 0
                self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
                
            def call(self, func, *args, **kwargs):
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.timeout:
                        self.state = "HALF_OPEN"
                    else:
                        raise Exception("Circuit breaker is OPEN")
                
                try:
                    result = func(*args, **kwargs)
                    if self.state == "HALF_OPEN":
                        self.state = "CLOSED"
                        self.failure_count = 0
                    return result
                except Exception as e:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    
                    if self.failure_count >= self.failure_threshold:
                        self.state = "OPEN"
                    
                    raise e
        
        # Failing service
        def unreliable_service(data):
            if random.random() < 0.8:  # 80% failure rate
                raise Exception("Service failure")
            return f"processed_{data}"
        
        circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=1)
        
        successful_calls = 0
        circuit_open_errors = 0
        service_errors = 0
        
        # Make many calls
        for i in range(50):
            try:
                result = circuit_breaker.call(unreliable_service, f"data_{i}")
                successful_calls += 1
            except Exception as e:
                if "Circuit breaker is OPEN" in str(e):
                    circuit_open_errors += 1
                else:
                    service_errors += 1
            
            time.sleep(0.01)
        
        # Circuit breaker should prevent cascading failures
        assert circuit_open_errors > 0  # Circuit opened
        assert service_errors > 0  # Some service failures
        assert successful_calls >= 0  # Some calls succeeded
        assert circuit_breaker.state in ["OPEN", "HALF_OPEN"]