"""
Comprehensive Test Suite for Distributed Memory Fold System
==========================================================

Tests the Distributed Memory Fold System, the advanced distributed memory
architecture that provides Byzantine fault-tolerant memory management for
LUKHAS consciousness networks. This system implements consensus algorithms,
distributed storage, temporal coherence, and intelligent memory optimization
across multiple nodes.

Test Coverage Areas:
- Distributed memory architecture and node management
- Byzantine fault tolerance and consensus algorithms
- Memory fold creation, management, and synchronization
- Temporal coherence and memory persistence
- Cross-node communication and data replication
- Memory optimization and intelligent caching
- Performance optimization and scalability
- Error handling and fault recovery mechanisms
"""
import pytest
import time
import asyncio
import threading
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from core.memory.distributed_memory_fold import (
    DistributedMemoryFold,
    MemoryNode,
    ConsensusAlgorithm,
    MemoryFoldManager,
    ByzantineFaultTolerance,
    TemporalCoherence,
    MemoryReplication,
    DistributedConsensus,
    MemoryOptimizer,
    FoldSynchronizer,
    get_distributed_memory_system,
)


class TestDistributedMemoryFold:
    """Comprehensive test suite for the Distributed Memory Fold System."""

    @pytest.fixture
    def memory_nodes(self):
        """Create a cluster of memory nodes for testing."""
        nodes = []
        for i in range(5):
            node = MemoryNode(
                node_id=f"memory_node_{i}",
                node_address=f"192.168.1.{100 + i}",
                node_port=8000 + i,
                storage_capacity=1024 * 1024 * 100,  # 100MB
                replication_factor=3,
                consensus_threshold=0.6
            )
            nodes.append(node)
        return nodes

    @pytest.fixture
    def distributed_memory_fold(self, memory_nodes):
        """Create a distributed memory fold instance."""
        return DistributedMemoryFold(
            cluster_nodes=memory_nodes,
            replication_factor=3,
            consensus_algorithm="pbft",  # Practical Byzantine Fault Tolerance
            enable_temporal_coherence=True,
            enable_intelligent_optimization=True,
            memory_persistence_enabled=True
        )

    @pytest.fixture
    def sample_memory_data(self):
        """Create sample memory data for testing."""
        return {
            "memory_id": "test_memory_001",
            "content": {
                "consciousness_state": "active_processing",
                "symbolic_data": [
                    {"symbol": "identity", "value": 0.9, "confidence": 0.85},
                    {"symbol": "memory", "value": 0.8, "confidence": 0.9},
                    {"symbol": "ethics", "value": 0.95, "confidence": 0.92}
                ],
                "temporal_markers": [
                    {"timestamp": time.time(), "event": "creation"},
                    {"timestamp": time.time() - 100, "event": "last_access"}
                ]
            },
            "metadata": {
                "creation_time": datetime.now(timezone.utc),
                "access_pattern": "frequent",
                "importance_score": 0.85,
                "retention_policy": "long_term"
            },
            "security": {
                "encryption_enabled": True,
                "access_control": ["consciousness_engine", "memory_system"],
                "integrity_hash": "sha256_hash_placeholder"
            }
        }

    @pytest.fixture
    def consensus_algorithm(self):
        """Create a consensus algorithm instance."""
        return ConsensusAlgorithm(
            algorithm_type="pbft",
            fault_tolerance_threshold=1,  # Can tolerate 1 Byzantine fault
            consensus_timeout=10.0,
            minimum_participants=3
        )

    @pytest.fixture
    def memory_fold_manager(self, distributed_memory_fold):
        """Create a memory fold manager instance."""
        return MemoryFoldManager(
            distributed_system=distributed_memory_fold,
            max_concurrent_operations=10,
            fold_synchronization_interval=30.0,
            optimization_enabled=True
        )

    # Basic System Functionality Tests
    def test_distributed_memory_fold_initialization(self, distributed_memory_fold, memory_nodes):
        """Test distributed memory fold initializes correctly."""
        assert distributed_memory_fold.cluster_nodes == memory_nodes
        assert distributed_memory_fold.replication_factor == 3
        assert distributed_memory_fold.consensus_algorithm == "pbft"
        assert distributed_memory_fold.enable_temporal_coherence is True
        assert distributed_memory_fold.enable_intelligent_optimization is True

    def test_memory_node_initialization(self, memory_nodes):
        """Test memory node initialization."""
        node = memory_nodes[0]
        assert node.node_id == "memory_node_0"
        assert node.node_address == "192.168.1.100"
        assert node.node_port == 8000
        assert node.storage_capacity == 1024 * 1024 * 100
        assert node.replication_factor == 3

    def test_cluster_formation(self, distributed_memory_fold):
        """Test cluster formation and node discovery."""
        # Start cluster formation
        formation_result = distributed_memory_fold.form_cluster()
        
        # Verify cluster formation
        assert formation_result.cluster_formed is True
        assert formation_result.active_nodes >= 3  # Minimum for consensus
        assert formation_result.leader_node is not None

    def test_node_health_monitoring(self, distributed_memory_fold):
        """Test node health monitoring."""
        # Check node health
        health_report = distributed_memory_fold.check_cluster_health()
        
        # Verify health monitoring
        assert health_report.total_nodes == 5
        assert health_report.healthy_nodes >= 3
        assert health_report.cluster_status in ["healthy", "degraded", "critical"]

    # Memory Storage and Retrieval Tests
    @pytest.mark.asyncio
    async def test_memory_storage_basic(self, distributed_memory_fold, sample_memory_data):
        """Test basic memory storage across distributed nodes."""
        # Store memory data
        storage_result = await distributed_memory_fold.store_memory(sample_memory_data)
        
        # Verify storage success
        assert storage_result.storage_successful is True
        assert storage_result.replicas_created >= 3
        assert storage_result.memory_id == sample_memory_data["memory_id"]

    @pytest.mark.asyncio
    async def test_memory_retrieval_basic(self, distributed_memory_fold, sample_memory_data):
        """Test basic memory retrieval from distributed storage."""
        # Store memory first
        await distributed_memory_fold.store_memory(sample_memory_data)
        
        # Retrieve memory
        retrieval_result = await distributed_memory_fold.retrieve_memory(
            memory_id=sample_memory_data["memory_id"]
        )
        
        # Verify retrieval success
        assert retrieval_result.retrieval_successful is True
        assert retrieval_result.memory_data["memory_id"] == sample_memory_data["memory_id"]
        assert retrieval_result.data_integrity_verified is True

    @pytest.mark.asyncio
    async def test_memory_replication(self, distributed_memory_fold, sample_memory_data):
        """Test memory replication across multiple nodes."""
        # Store memory with specific replication factor
        storage_result = await distributed_memory_fold.store_memory(
            memory_data=sample_memory_data,
            replication_factor=4
        )
        
        # Verify replication
        assert storage_result.replicas_created == 4
        assert len(storage_result.replica_locations) == 4

    @pytest.mark.asyncio
    async def test_memory_update_propagation(self, distributed_memory_fold, sample_memory_data):
        """Test memory update propagation across nodes."""
        # Store initial memory
        await distributed_memory_fold.store_memory(sample_memory_data)
        
        # Update memory data
        updated_data = sample_memory_data.copy()
        updated_data["content"]["consciousness_state"] = "updated_processing"
        
        # Propagate update
        update_result = await distributed_memory_fold.update_memory(
            memory_id=sample_memory_data["memory_id"],
            updated_data=updated_data
        )
        
        # Verify update propagation
        assert update_result.update_successful is True
        assert update_result.nodes_updated >= 3
        assert update_result.consistency_achieved is True

    # Consensus Algorithm Tests
    @pytest.mark.asyncio
    async def test_byzantine_fault_tolerance(self, distributed_memory_fold, sample_memory_data):
        """Test Byzantine fault tolerance during consensus."""
        # Simulate Byzantine fault (1 node sending conflicting data)
        byzantine_node = distributed_memory_fold.cluster_nodes[0]
        byzantine_node.simulate_byzantine_behavior = True
        
        # Store memory with Byzantine node present
        storage_result = await distributed_memory_fold.store_memory(sample_memory_data)
        
        # Should achieve consensus despite Byzantine fault
        assert storage_result.storage_successful is True
        assert storage_result.consensus_achieved is True
        assert storage_result.byzantine_faults_detected == 1

    @pytest.mark.asyncio
    async def test_consensus_with_node_failure(self, distributed_memory_fold, sample_memory_data):
        """Test consensus achievement with node failures."""
        # Simulate node failure
        failed_node = distributed_memory_fold.cluster_nodes[0]
        failed_node.is_online = False
        
        # Store memory with failed node
        storage_result = await distributed_memory_fold.store_memory(sample_memory_data)
        
        # Should achieve consensus with remaining nodes
        assert storage_result.storage_successful is True
        assert storage_result.active_participants >= 3

    @pytest.mark.asyncio
    async def test_consensus_timeout_handling(self, distributed_memory_fold, sample_memory_data):
        """Test consensus timeout handling."""
        # Set very short consensus timeout
        distributed_memory_fold.consensus_timeout = 0.1
        
        # Simulate slow network conditions
        for node in distributed_memory_fold.cluster_nodes:
            node.network_latency = 1.0  # 1 second latency
        
        # Attempt storage with timeout
        with pytest.raises(TimeoutError):
            await distributed_memory_fold.store_memory(sample_memory_data)

    @pytest.mark.asyncio
    async def test_consensus_algorithm_switching(self, distributed_memory_fold, sample_memory_data):
        """Test switching between consensus algorithms."""
        # Start with PBFT
        assert distributed_memory_fold.consensus_algorithm == "pbft"
        
        # Switch to Raft
        switch_result = await distributed_memory_fold.switch_consensus_algorithm("raft")
        assert switch_result.algorithm_switched is True
        assert distributed_memory_fold.consensus_algorithm == "raft"
        
        # Verify storage works with new algorithm
        storage_result = await distributed_memory_fold.store_memory(sample_memory_data)
        assert storage_result.storage_successful is True

    # Temporal Coherence Tests
    @pytest.mark.asyncio
    async def test_temporal_coherence_validation(self, distributed_memory_fold, sample_memory_data):
        """Test temporal coherence validation."""
        # Store memory with temporal markers
        await distributed_memory_fold.store_memory(sample_memory_data)
        
        # Validate temporal coherence
        coherence_result = await distributed_memory_fold.validate_temporal_coherence(
            memory_id=sample_memory_data["memory_id"]
        )
        
        # Verify temporal coherence
        assert coherence_result.coherence_valid is True
        assert coherence_result.temporal_consistency >= 0.8

    @pytest.mark.asyncio
    async def test_temporal_ordering_enforcement(self, distributed_memory_fold):
        """Test temporal ordering enforcement across distributed nodes."""
        # Create sequence of memory updates
        memory_sequence = []
        for i in range(5):
            memory_data = {
                "memory_id": f"sequence_memory_{i}",
                "content": {"sequence_number": i, "timestamp": time.time() + i},
                "metadata": {"creation_time": datetime.now(timezone.utc)}
            }
            memory_sequence.append(memory_data)
        
        # Store memories in sequence
        for memory_data in memory_sequence:
            await distributed_memory_fold.store_memory(memory_data)
        
        # Verify temporal ordering
        ordering_result = await distributed_memory_fold.validate_temporal_ordering(
            memory_ids=[m["memory_id"] for m in memory_sequence]
        )
        
        assert ordering_result.ordering_correct is True
        assert ordering_result.sequence_violations == 0

    @pytest.mark.asyncio
    async def test_memory_aging_and_retention(self, distributed_memory_fold, sample_memory_data):
        """Test memory aging and retention policies."""
        # Set short retention policy
        sample_memory_data["metadata"]["retention_policy"] = "short_term"
        sample_memory_data["metadata"]["creation_time"] = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Store aged memory
        await distributed_memory_fold.store_memory(sample_memory_data)
        
        # Apply retention policies
        retention_result = await distributed_memory_fold.apply_retention_policies()
        
        # Verify retention handling
        assert retention_result.policies_applied > 0
        assert retention_result.memories_processed >= 1

    # Memory Optimization Tests
    @pytest.mark.asyncio
    async def test_intelligent_memory_optimization(self, distributed_memory_fold):
        """Test intelligent memory optimization algorithms."""
        # Create varied memory data with different access patterns
        memory_data_frequent = {
            "memory_id": "frequent_access_001",
            "content": {"data": "frequently_accessed"},
            "metadata": {"access_pattern": "frequent", "importance_score": 0.9}
        }
        
        memory_data_rare = {
            "memory_id": "rare_access_001",
            "content": {"data": "rarely_accessed"},
            "metadata": {"access_pattern": "rare", "importance_score": 0.3}
        }
        
        # Store both memories
        await distributed_memory_fold.store_memory(memory_data_frequent)
        await distributed_memory_fold.store_memory(memory_data_rare)
        
        # Apply optimization
        optimization_result = await distributed_memory_fold.optimize_memory_distribution()
        
        # Verify optimization
        assert optimization_result.optimization_applied is True
        assert optimization_result.performance_improvement > 0.0

    @pytest.mark.asyncio
    async def test_memory_caching_optimization(self, distributed_memory_fold, sample_memory_data):
        """Test memory caching optimization."""
        # Store memory
        await distributed_memory_fold.store_memory(sample_memory_data)
        
        # Access memory multiple times to trigger caching
        for _ in range(5):
            await distributed_memory_fold.retrieve_memory(sample_memory_data["memory_id"])
        
        # Check caching effectiveness
        cache_stats = await distributed_memory_fold.get_cache_statistics()
        
        assert cache_stats.cache_hit_rate > 0.5
        assert cache_stats.performance_improvement > 0.0

    @pytest.mark.asyncio
    async def test_memory_compression_optimization(self, distributed_memory_fold):
        """Test memory compression optimization."""
        # Create large memory data
        large_memory_data = {
            "memory_id": "large_memory_001",
            "content": {"large_data": "x" * 10000},  # 10KB of data
            "metadata": {"compression_enabled": True}
        }
        
        # Store with compression
        storage_result = await distributed_memory_fold.store_memory(large_memory_data)
        
        # Verify compression
        assert storage_result.compression_applied is True
        assert storage_result.compression_ratio > 0.5

    # Fault Recovery Tests
    @pytest.mark.asyncio
    async def test_node_failure_recovery(self, distributed_memory_fold, sample_memory_data):
        """Test recovery from node failures."""
        # Store memory across nodes
        await distributed_memory_fold.store_memory(sample_memory_data)
        
        # Simulate node failure
        failed_node = distributed_memory_fold.cluster_nodes[0]
        failed_node.is_online = False
        
        # Trigger recovery
        recovery_result = await distributed_memory_fold.recover_from_node_failure(failed_node)
        
        # Verify recovery
        assert recovery_result.recovery_successful is True
        assert recovery_result.data_restored is True
        assert recovery_result.cluster_health_restored is True

    @pytest.mark.asyncio
    async def test_data_corruption_recovery(self, distributed_memory_fold, sample_memory_data):
        """Test recovery from data corruption."""
        # Store memory
        await distributed_memory_fold.store_memory(sample_memory_data)
        
        # Simulate data corruption on one node
        corrupted_node = distributed_memory_fold.cluster_nodes[0]
        corrupted_node.simulate_data_corruption = True
        
        # Retrieve memory (should detect and recover from corruption)
        retrieval_result = await distributed_memory_fold.retrieve_memory(
            memory_id=sample_memory_data["memory_id"],
            verify_integrity=True
        )
        
        # Verify corruption detection and recovery
        assert retrieval_result.retrieval_successful is True
        assert retrieval_result.corruption_detected is True
        assert retrieval_result.data_restored_from_replicas is True

    @pytest.mark.asyncio
    async def test_network_partition_handling(self, distributed_memory_fold, sample_memory_data):
        """Test handling of network partitions."""
        # Create network partition (split cluster into two groups)
        partition_1 = distributed_memory_fold.cluster_nodes[:3]
        partition_2 = distributed_memory_fold.cluster_nodes[3:]
        
        # Simulate network partition
        for node in partition_2:
            node.network_partition = True
        
        # Store memory in majority partition
        storage_result = await distributed_memory_fold.store_memory(
            memory_data=sample_memory_data,
            partition_tolerance=True
        )
        
        # Should succeed with majority partition
        assert storage_result.storage_successful is True
        assert storage_result.partition_handled is True

    # Performance and Scalability Tests
    @pytest.mark.asyncio
    async def test_storage_performance_under_load(self, distributed_memory_fold):
        """Test storage performance under high load."""
        start_time = time.time()
        
        # Store multiple memories concurrently
        storage_tasks = []
        for i in range(20):
            memory_data = {
                "memory_id": f"perf_test_{i}",
                "content": {"data": f"performance_test_data_{i}"},
                "metadata": {"creation_time": datetime.now(timezone.utc)}
            }
            task = distributed_memory_fold.store_memory(memory_data)
            storage_tasks.append(task)
        
        # Wait for all storage operations
        results = await asyncio.gather(*storage_tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify performance
        assert total_time < 10.0  # Under 10 seconds for 20 memories
        successful_operations = sum(1 for r in results if r.storage_successful)
        assert successful_operations >= 18  # At least 90% success rate

    @pytest.mark.asyncio
    async def test_retrieval_performance_under_load(self, distributed_memory_fold, sample_memory_data):
        """Test retrieval performance under high load."""
        # Store test memory
        await distributed_memory_fold.store_memory(sample_memory_data)
        
        start_time = time.time()
        
        # Retrieve memory multiple times concurrently
        retrieval_tasks = []
        for _ in range(50):
            task = distributed_memory_fold.retrieve_memory(sample_memory_data["memory_id"])
            retrieval_tasks.append(task)
        
        # Wait for all retrieval operations
        results = await asyncio.gather(*retrieval_tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify performance
        assert total_time < 5.0  # Under 5 seconds for 50 retrievals
        successful_retrievals = sum(1 for r in results if r.retrieval_successful)
        assert successful_retrievals == 50  # 100% success rate expected

    def test_memory_efficiency_under_load(self, distributed_memory_fold):
        """Test memory efficiency under sustained load."""
        import gc
        
        # Get initial memory
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Store and retrieve many memories
        for i in range(30):
            memory_data = {
                "memory_id": f"memory_test_{i}",
                "content": {"data": f"test_data_{i}"},
                "metadata": {"creation_time": datetime.now(timezone.utc)}
            }
            
            # Store and immediately retrieve
            asyncio.run(distributed_memory_fold.store_memory(memory_data))
            asyncio.run(distributed_memory_fold.retrieve_memory(memory_data["memory_id"]))
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Verify reasonable memory usage
        object_growth = final_objects - initial_objects
        assert object_growth < 500  # Should not create excessive objects

    # Integration and Compatibility Tests
    def test_memory_fold_manager_integration(self, memory_fold_manager, sample_memory_data):
        """Test integration with memory fold manager."""
        # Use manager to store memory
        storage_result = asyncio.run(
            memory_fold_manager.managed_store_memory(sample_memory_data)
        )
        
        # Verify manager integration
        assert storage_result.management_applied is True
        assert storage_result.storage_successful is True

    @pytest.mark.asyncio
    async def test_cross_system_memory_access(self, distributed_memory_fold, sample_memory_data):
        """Test cross-system memory access integration."""
        # Store memory with specific access controls
        sample_memory_data["security"]["access_control"] = ["consciousness_engine", "identity_system"]
        
        await distributed_memory_fold.store_memory(sample_memory_data)
        
        # Test access from allowed system
        access_result = await distributed_memory_fold.access_memory_as_system(
            memory_id=sample_memory_data["memory_id"],
            accessing_system="consciousness_engine"
        )
        
        assert access_result.access_granted is True

    @pytest.mark.asyncio
    async def test_memory_synchronization_across_folds(self, distributed_memory_fold):
        """Test memory synchronization across different memory folds."""
        # Create multiple memory folds
        fold_1_data = {"memory_id": "fold_1_memory", "content": {"fold": 1}}
        fold_2_data = {"memory_id": "fold_2_memory", "content": {"fold": 2}}
        
        # Store in different folds
        await distributed_memory_fold.store_memory(fold_1_data, fold_id="fold_1")
        await distributed_memory_fold.store_memory(fold_2_data, fold_id="fold_2")
        
        # Synchronize folds
        sync_result = await distributed_memory_fold.synchronize_memory_folds(
            fold_ids=["fold_1", "fold_2"]
        )
        
        assert sync_result.synchronization_successful is True
        assert sync_result.conflicts_resolved >= 0

    # Global Function Tests
    def test_get_distributed_memory_system_singleton(self):
        """Test global distributed memory system singleton."""
        system1 = get_distributed_memory_system()
        system2 = get_distributed_memory_system()
        
        # Should return the same instance
        assert system1 is system2

    # Cleanup and Resource Management Tests
    @pytest.mark.asyncio
    async def test_system_shutdown_and_cleanup(self, distributed_memory_fold):
        """Test graceful system shutdown and cleanup."""
        # Start system operations
        await distributed_memory_fold.form_cluster()
        
        # Store some test data
        test_data = {"memory_id": "shutdown_test", "content": {"test": "data"}}
        await distributed_memory_fold.store_memory(test_data)
        
        # Initiate graceful shutdown
        shutdown_result = await distributed_memory_fold.graceful_shutdown(timeout=10.0)
        
        # Verify shutdown
        assert shutdown_result.shutdown_successful is True
        assert shutdown_result.data_persisted is True
        assert shutdown_result.cluster_disbanded is True

    @pytest.mark.asyncio
    async def test_memory_persistence_across_restarts(self, distributed_memory_fold, sample_memory_data):
        """Test memory persistence across system restarts."""
        # Store memory with persistence enabled
        await distributed_memory_fold.store_memory(sample_memory_data)
        
        # Simulate system restart
        restart_result = await distributed_memory_fold.simulate_system_restart()
        
        # Verify memory persistence
        assert restart_result.restart_successful is True
        
        # Try to retrieve previously stored memory
        retrieval_result = await distributed_memory_fold.retrieve_memory(
            memory_id=sample_memory_data["memory_id"]
        )
        
        assert retrieval_result.retrieval_successful is True
        assert retrieval_result.memory_data["memory_id"] == sample_memory_data["memory_id"]