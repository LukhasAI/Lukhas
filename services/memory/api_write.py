"""
Memory Write API Service
=======================

High-performance write operations with T4/0.01% excellence:
- Upsert operations (insert/update memory folds)
- Delete operations with soft/hard delete options
- Lifecycle management (expiration, archival)
- Performance target: p95 <100ms, p99 <150ms

Features:
- Async/await for high concurrency
- Transaction support for data consistency
- Circuit breaker protection
- Prometheus metrics
- Backpressure handling
- Batch operations for efficiency
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from lukhas.memory.consciousness_memory_integration import ConsciousnessMemoryIntegrator, MemoryFoldType

from .adapters.vector_store_base import VectorStoreAdapter
from .backpressure import BackpressureManager

# Import services components
from .circuit_breaker import MemoryCircuitBreaker
from .metrics import MemoryMetrics

logger = logging.getLogger(__name__)


class WriteOperationType(Enum):
    """Write operation types"""
    CREATE = "create"
    UPDATE = "update"
    UPSERT = "upsert"
    DELETE = "delete"
    ARCHIVE = "archive"
    RESTORE = "restore"


class DeleteType(Enum):
    """Delete operation types"""
    SOFT = "soft"      # Mark as deleted, keep data
    HARD = "hard"      # Permanently remove data
    ARCHIVE = "archive" # Move to archive storage


@dataclass
class WriteOperation:
    """Write operation request"""
    operation_id: str = field(default_factory=lambda: f"op_{uuid.uuid4().hex[:8]}")
    operation_type: WriteOperationType = WriteOperationType.UPSERT
    fold_id: Optional[str] = None
    content: Optional[str] = None
    fold_type: Optional[MemoryFoldType] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    ttl_seconds: Optional[int] = None
    priority: int = 1


@dataclass
class BatchWriteOperation:
    """Batch write operation request"""
    batch_id: str = field(default_factory=lambda: f"batch_{uuid.uuid4().hex[:8]}")
    operations: List[WriteOperation] = field(default_factory=list)
    atomic: bool = True  # All operations succeed or all fail


@dataclass
class WriteResult:
    """Write operation result"""
    operation_id: str
    fold_id: str
    success: bool
    execution_time_ms: float
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BatchWriteResult:
    """Batch write operation result"""
    batch_id: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    results: List[WriteResult]
    total_time_ms: float
    atomic_rollback: bool = False


class MemoryWriteService:
    """
    High-performance memory write service with T4/0.01% excellence.

    Provides upsert, delete, and lifecycle operations with strict
    performance SLOs and data consistency guarantees.
    """

    def __init__(self,
                 vector_store: VectorStoreAdapter,
                 consciousness_integrator: Optional[ConsciousnessMemoryIntegrator] = None,
                 max_concurrent_writes: int = 25,
                 write_timeout_ms: int = 5000,
                 enable_transactions: bool = True):
        """Initialize memory write service"""
        self.vector_store = vector_store
        self.consciousness_integrator = consciousness_integrator
        self.max_concurrent_writes = max_concurrent_writes
        self.write_timeout_ms = write_timeout_ms
        self.enable_transactions = enable_transactions

        # Service components
        self.circuit_breaker = MemoryCircuitBreaker(
            failure_threshold=3,  # More sensitive for writes
            recovery_timeout_ms=60000  # Longer recovery for writes
        )
        self.backpressure = BackpressureManager(
            max_tokens=max_concurrent_writes,
            refill_rate=5.0  # tokens per second (slower for writes)
        )
        self.metrics = MemoryMetrics()

        # Write coordination
        self._write_semaphore = asyncio.Semaphore(max_concurrent_writes)
        self._active_transactions: Dict[str, Set[str]] = {}

        # Lifecycle management
        self._ttl_cleanup_task = None
        self._start_ttl_cleanup()

        logger.info(f"MemoryWriteService initialized with max_concurrent_writes={max_concurrent_writes}")

    async def upsert_memory_fold(self,
                                fold_id: Optional[str] = None,
                                content: Optional[str] = None,
                                fold_type: MemoryFoldType = MemoryFoldType.EPISODIC,
                                tags: Optional[List[str]] = None,
                                metadata: Optional[Dict[str, Any]] = None,
                                embedding: Optional[List[float]] = None,
                                ttl_seconds: Optional[int] = None) -> WriteResult:
        """
        Upsert (insert or update) a memory fold.
        Target: p95 <100ms, p99 <150ms
        """
        start_time = time.perf_counter()

        # Generate fold_id if not provided
        if not fold_id:
            fold_id = f"fold_{uuid.uuid4().hex}"

        # Validate inputs
        self._validate_upsert_params(fold_id, content, fold_type)

        # Check backpressure
        if not await self.backpressure.acquire_token():
            raise Exception("Service overloaded - backpressure active")

        try:
            operation = WriteOperation(
                operation_type=WriteOperationType.UPSERT,
                fold_id=fold_id,
                content=content,
                fold_type=fold_type,
                tags=tags or [],
                metadata=metadata or {},
                embedding=embedding,
                ttl_seconds=ttl_seconds
            )

            async with self._write_semaphore:
                result = await self.circuit_breaker.call(
                    self._execute_write_operation, operation
                )

            # Record metrics
            write_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_write_latency(
                write_time_ms, WriteOperationType.UPSERT.value, result.success
            )

            logger.debug(f"Upsert completed: {fold_id} in {write_time_ms:.2f}ms")
            return result

        except Exception as e:
            error_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_write_error(WriteOperationType.UPSERT.value, str(e))
            logger.error(f"Upsert failed: {fold_id} after {error_time_ms:.2f}ms - {e}")
            raise
        finally:
            self.backpressure.release_token()

    async def delete_memory_fold(self,
                                fold_id: str,
                                delete_type: DeleteType = DeleteType.SOFT,
                                reason: Optional[str] = None) -> WriteResult:
        """
        Delete memory fold with specified delete type.
        Target: p95 <100ms
        """
        start_time = time.perf_counter()

        if not await self.backpressure.acquire_token():
            raise Exception("Service overloaded - backpressure active")

        try:
            operation = WriteOperation(
                operation_type=WriteOperationType.DELETE,
                fold_id=fold_id,
                metadata={'delete_type': delete_type.value, 'reason': reason}
            )

            async with self._write_semaphore:
                result = await self.circuit_breaker.call(
                    self._execute_delete_operation, operation, delete_type
                )

            # Record metrics
            delete_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_delete_latency(
                delete_time_ms, delete_type.value, result.success
            )

            logger.debug(f"Delete completed: {fold_id} ({delete_type.value}) in {delete_time_ms:.2f}ms")
            return result

        except Exception as e:
            error_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_delete_error(delete_type.value, str(e))
            logger.error(f"Delete failed: {fold_id} after {error_time_ms:.2f}ms - {e}")
            raise
        finally:
            self.backpressure.release_token()

    async def batch_write(self, batch_operation: BatchWriteOperation) -> BatchWriteResult:
        """
        Execute batch write operations with optional atomicity.
        Target: p95 <100ms per operation
        """
        start_time = time.perf_counter()
        results = []
        successful_count = 0
        failed_count = 0
        rollback_performed = False

        if not await self.backpressure.acquire_token():
            raise Exception("Service overloaded - backpressure active")

        try:
            # Start transaction if atomic
            transaction_id = None
            if batch_operation.atomic and self.enable_transactions:
                transaction_id = await self.vector_store.begin_transaction()

            # Execute operations
            for operation in batch_operation.operations:
                try:
                    async with self._write_semaphore:
                        result = await self.circuit_breaker.call(
                            self._execute_write_operation, operation
                        )

                    results.append(result)
                    if result.success:
                        successful_count += 1
                    else:
                        failed_count += 1

                        # If atomic and any operation fails, rollback
                        if batch_operation.atomic:
                            if transaction_id:
                                await self.vector_store.rollback_transaction(transaction_id)
                                rollback_performed = True
                            break

                except Exception as e:
                    failed_count += 1
                    error_result = WriteResult(
                        operation_id=operation.operation_id,
                        fold_id=operation.fold_id or "unknown",
                        success=False,
                        execution_time_ms=0,
                        error_message=str(e)
                    )
                    results.append(error_result)

                    # If atomic and any operation fails, rollback
                    if batch_operation.atomic:
                        if transaction_id:
                            await self.vector_store.rollback_transaction(transaction_id)
                            rollback_performed = True
                        break

            # Commit transaction if successful
            if transaction_id and not rollback_performed:
                await self.vector_store.commit_transaction(transaction_id)

            # Record metrics
            batch_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_batch_write_latency(
                batch_time_ms, len(batch_operation.operations), successful_count
            )

            return BatchWriteResult(
                batch_id=batch_operation.batch_id,
                total_operations=len(batch_operation.operations),
                successful_operations=successful_count,
                failed_operations=failed_count,
                results=results,
                total_time_ms=batch_time_ms,
                atomic_rollback=rollback_performed
            )

        except Exception as e:
            error_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_batch_write_error(str(e))
            logger.error(f"Batch write failed: {batch_operation.batch_id} after {error_time_ms:.2f}ms - {e}")
            raise
        finally:
            self.backpressure.release_token()

    async def expire_memory_folds(self, cutoff_time: datetime) -> int:
        """
        Expire memory folds older than cutoff time.
        Returns count of expired folds.
        """
        start_time = time.perf_counter()

        if not await self.backpressure.acquire_token():
            raise Exception("Service overloaded - backpressure active")

        try:
            expired_count = await self.vector_store.expire_documents(cutoff_time)

            # Record metrics
            expire_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_expire_latency(expire_time_ms, expired_count)

            logger.info(f"Expired {expired_count} memory folds in {expire_time_ms:.2f}ms")
            return expired_count

        except Exception as e:
            error_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_expire_error(str(e))
            logger.error(f"Expire operation failed after {error_time_ms:.2f}ms - {e}")
            raise
        finally:
            self.backpressure.release_token()

    async def _execute_write_operation(self, operation: WriteOperation) -> WriteResult:
        """Execute individual write operation"""
        operation_start = time.perf_counter()

        try:
            # Generate embedding if needed and not provided
            if not operation.embedding and operation.content:
                operation.embedding = await self._generate_embedding(operation.content)

            # Prepare document data
            document_data = {
                'fold_id': operation.fold_id,
                'content': operation.content,
                'fold_type': operation.fold_type.value if operation.fold_type else 'episodic',
                'tags': operation.tags,
                'metadata': operation.metadata,
                'embedding': operation.embedding,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }

            # Add TTL if specified
            if operation.ttl_seconds:
                document_data['expires_at'] = datetime.now(timezone.utc) + timedelta(seconds=operation.ttl_seconds)

            # Execute operation
            if operation.operation_type == WriteOperationType.CREATE:
                success = await self.vector_store.insert_document(document_data)
            elif operation.operation_type == WriteOperationType.UPDATE:
                success = await self.vector_store.update_document(operation.fold_id, document_data)
            else:  # UPSERT
                success = await self.vector_store.upsert_document(document_data)

            execution_time_ms = (time.perf_counter() - operation_start) * 1000

            return WriteResult(
                operation_id=operation.operation_id,
                fold_id=operation.fold_id,
                success=success,
                execution_time_ms=execution_time_ms
            )

        except Exception as e:
            execution_time_ms = (time.perf_counter() - operation_start) * 1000
            return WriteResult(
                operation_id=operation.operation_id,
                fold_id=operation.fold_id or "unknown",
                success=False,
                execution_time_ms=execution_time_ms,
                error_message=str(e)
            )

    async def _execute_delete_operation(self, operation: WriteOperation, delete_type: DeleteType) -> WriteResult:
        """Execute delete operation"""
        operation_start = time.perf_counter()

        try:
            if delete_type == DeleteType.SOFT:
                # Mark as deleted but keep data
                update_data = {
                    'deleted': True,
                    'deleted_at': datetime.now(timezone.utc),
                    'delete_reason': operation.metadata.get('reason')
                }
                success = await self.vector_store.update_document(operation.fold_id, update_data)

            elif delete_type == DeleteType.ARCHIVE:
                # Move to archive storage
                success = await self.vector_store.archive_document(operation.fold_id)

            else:  # HARD delete
                success = await self.vector_store.delete_document(operation.fold_id)

            execution_time_ms = (time.perf_counter() - operation_start) * 1000

            return WriteResult(
                operation_id=operation.operation_id,
                fold_id=operation.fold_id,
                success=success,
                execution_time_ms=execution_time_ms
            )

        except Exception as e:
            execution_time_ms = (time.perf_counter() - operation_start) * 1000
            return WriteResult(
                operation_id=operation.operation_id,
                fold_id=operation.fold_id,
                success=False,
                execution_time_ms=execution_time_ms,
                error_message=str(e)
            )

    async def _generate_embedding(self, content: str) -> List[float]:
        """Generate embedding for content"""
        if self.consciousness_integrator:
            return await self.consciousness_integrator.generate_embedding(content)
        else:
            # Fallback embedding (would need actual implementation)
            return [0.0] * 768  # Placeholder

    def _validate_upsert_params(self,
                               fold_id: str,
                               content: Optional[str],
                               fold_type: MemoryFoldType):
        """Validate upsert parameters"""
        if not fold_id or len(fold_id.strip()) == 0:
            raise ValueError("fold_id cannot be empty")

        if not content or len(content.strip()) == 0:
            raise ValueError("content cannot be empty")

        if not isinstance(fold_type, MemoryFoldType):
            raise ValueError("fold_type must be a valid MemoryFoldType")

    def _start_ttl_cleanup(self):
        """Start background TTL cleanup task"""
        async def ttl_cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(300)  # Run every 5 minutes
                    cutoff_time = datetime.now(timezone.utc)
                    expired_count = await self.expire_memory_folds(cutoff_time)
                    if expired_count > 0:
                        logger.info(f"TTL cleanup: expired {expired_count} memory folds")
                except Exception as e:
                    logger.error(f"TTL cleanup failed: {e}")

        self._ttl_cleanup_task = asyncio.create_task(ttl_cleanup_loop())

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        return {
            **self.metrics.get_metrics(),
            'circuit_breaker_state': self.circuit_breaker.get_state(),
            'backpressure_tokens_available': self.backpressure.get_available_tokens(),
            'active_writes': self.max_concurrent_writes - self._write_semaphore._value,
            'active_transactions': len(self._active_transactions)
        }

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            # Test vector store connection
            await self.vector_store.health_check()

            return {
                'status': 'healthy',
                'service': 'memory_write',
                'performance_metrics': self.get_performance_metrics(),
                'vector_store_healthy': True,
                'circuit_breaker_open': self.circuit_breaker.is_open(),
                'backpressure_active': self.backpressure.is_limiting(),
                'ttl_cleanup_running': self._ttl_cleanup_task and not self._ttl_cleanup_task.done()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'service': 'memory_write',
                'error': str(e),
                'circuit_breaker_open': self.circuit_breaker.is_open(),
                'backpressure_active': self.backpressure.is_limiting()
            }

    async def shutdown(self):
        """Graceful service shutdown"""
        logger.info("Shutting down MemoryWriteService...")

        # Cancel TTL cleanup task
        if self._ttl_cleanup_task:
            self._ttl_cleanup_task.cancel()
            try:
                await self._ttl_cleanup_task
            except asyncio.CancelledError:
                pass

        # Wait for active operations to complete
        async with self._write_semaphore:
            pass  # All operations should be done now

        logger.info("MemoryWriteService shutdown complete")
