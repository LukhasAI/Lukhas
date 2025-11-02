"""
LUKHAS Ledger Event Bus v2.0.0
==============================

Async event dispatcher with offset-based storage, replay capabilities,
and T4/0.01% excellence performance requirements (p95 append <50ms).

Features:
- Atomic event append operations
- Offset-based event storage and retrieval
- Async publish/subscribe pattern
- Dead letter queue for failed events
- Circuit breaker for resilience
- Replay from any offset
- SHA256 tamper evidence chain
"""

import asyncio
import hashlib
import json
import logging
import sqlite3
import threading
import time
from collections.abc import AsyncIterator
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol

from .events import ConsentEvent, create_event_from_dict, validate_event_schema

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class EventOffset:
    """Event offset for tracking position in event stream"""
    offset: int
    timestamp: str
    event_id: str
    hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventOffset':
        return cls(**data)


@dataclass
class DeadLetterEvent:
    """Event that failed processing and ended up in dead letter queue"""
    original_event: Dict[str, Any]
    error_message: str
    failure_count: int
    first_failure_at: str
    last_failure_at: str
    next_retry_at: Optional[str] = None


class EventSubscriber(Protocol):
    """Protocol for event subscribers"""

    async def handle_event(self, event: ConsentEvent, offset: EventOffset) -> bool:
        """Handle an event. Return True for success, False for retry."""
        ...


class CircuitBreaker:
    """Circuit breaker for event processing resilience"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = CircuitBreakerState.CLOSED
        self._lock = threading.Lock()

    def call(self, func: Callable) -> Callable:
        """Decorator for circuit breaker protection"""
        async def wrapper(*args, **kwargs):
            if not self.can_execute():
                raise Exception("Circuit breaker is OPEN")

            try:
                result = await func(*args, **kwargs)
                self.on_success()
                return result
            except Exception as e:
                self.on_failure()
                raise e

        return wrapper

    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    return True
                return False
            else:  # HALF_OPEN
                return True

    def on_success(self):
        """Called on successful execution"""
        with self._lock:
            self.failure_count = 0
            self.state = CircuitBreakerState.CLOSED

    def on_failure(self):
        """Called on failed execution"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN


class ReplayIterator:
    """Iterator for event replay from specific offset"""

    def __init__(self, bus: 'AsyncEventBus', from_offset: int, to_offset: Optional[int] = None):
        self.bus = bus
        self.from_offset = from_offset
        self.to_offset = to_offset
        self.current_offset = from_offset

    async def __aiter__(self) -> AsyncIterator[tuple[ConsentEvent, EventOffset]]:
        return self

    async def __anext__(self) -> tuple[ConsentEvent, EventOffset]:
        if self.to_offset is not None and self.current_offset >= self.to_offset:
            raise StopAsyncIteration

        event_data = await self.bus._get_event_at_offset(self.current_offset)
        if not event_data:
            raise StopAsyncIteration

        event = create_event_from_dict(event_data['event_data'])
        offset = EventOffset(
            offset=event_data['offset'],
            timestamp=event_data['timestamp'],
            event_id=event_data['event_id'],
            hash=event_data['hash']
        )

        self.current_offset += 1
        return event, offset


class AsyncEventBus:
    """
    High-performance async event bus with T4/0.01% excellence requirements.

    Performance targets:
    - Event append: p95 <50ms
    - Replay: deterministic and fast
    - Storage: atomic and durable
    """

    def __init__(self, db_path: str = "ledger/event_store.db", max_retry_attempts: int = 3):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_retry_attempts = max_retry_attempts

        # Subscribers and handlers
        self.subscribers: Dict[str, List[EventSubscriber]] = {}
        self.dead_letter_queue: List[DeadLetterEvent] = []

        # Circuit breaker for resilience
        self.circuit_breaker = CircuitBreaker()

        # Performance tracking
        self.metrics = {
            'events_appended': 0,
            'append_times': [],
            'replay_times': [],
            'processing_errors': 0,
        }

        # Thread safety
        self._lock = asyncio.Lock()
        self._db_lock = threading.RLock()

        # Initialize database
        self._init_database()

        logger.info(f"AsyncEventBus initialized with store: {self.db_path}")

    def _init_database(self):
        """Initialize event store database with optimized schema"""
        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path), timeout=30.0)
            cursor = conn.cursor()

            try:
                # Enable WAL mode for better concurrency
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("PRAGMA synchronous=FULL;")
                cursor.execute("PRAGMA foreign_keys=ON;")

                # Event store table with offset-based indexing
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS event_store (
                        offset INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id TEXT UNIQUE NOT NULL,
                        event_type TEXT NOT NULL,
                        aggregate_id TEXT NOT NULL,
                        event_data TEXT NOT NULL,
                        hash TEXT NOT NULL,
                        chain_hash TEXT,
                        timestamp TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        correlation_id TEXT,
                        causation_id TEXT,
                        metadata TEXT,
                        schema_version TEXT DEFAULT '2.0.0'
                    )
                """)

                # Dead letter queue table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dead_letter_queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        original_event TEXT NOT NULL,
                        error_message TEXT NOT NULL,
                        failure_count INTEGER DEFAULT 1,
                        first_failure_at TEXT NOT NULL,
                        last_failure_at TEXT NOT NULL,
                        next_retry_at TEXT
                    )
                """)

                # Offset checkpoint table for consumers
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS consumer_checkpoints (
                        consumer_id TEXT PRIMARY KEY,
                        last_processed_offset INTEGER NOT NULL,
                        updated_at TEXT NOT NULL,
                        metadata TEXT
                    )
                """)

                # Performance indexes
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_event_type ON event_store(event_type)",
                    "CREATE INDEX IF NOT EXISTS idx_aggregate_id ON event_store(aggregate_id)",
                    "CREATE INDEX IF NOT EXISTS idx_timestamp ON event_store(timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_correlation_id ON event_store(correlation_id)",
                    "CREATE INDEX IF NOT EXISTS idx_created_at ON event_store(created_at)",
                ]

                for index_sql in indexes:
                    cursor.execute(index_sql)

                conn.commit()
                logger.info("Event store database initialized successfully")

            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                raise
            finally:
                conn.close()

    async def append_event(self, event: ConsentEvent) -> EventOffset:
        """
        Append event to store with atomic operation and performance tracking.
        Target: p95 <50ms
        """
        start_time = time.perf_counter()

        try:
            # Validate event schema
            if not validate_event_schema(event):
                raise ValueError(f"Event failed schema validation: {event.event_id}")

            async with self._lock:
                # Compute event hash for tamper evidence
                event_hash = event.compute_hash()
                event_data = event.to_dict()

                # Get current chain hash for linking
                chain_hash = await self._compute_next_chain_hash(event_hash)

                with self._db_lock:
                    conn = sqlite3.connect(str(self.db_path), timeout=30.0)
                    cursor = conn.cursor()

                    try:
                        cursor.execute("""
                            INSERT INTO event_store (
                                event_id, event_type, aggregate_id, event_data,
                                hash, chain_hash, timestamp, created_at,
                                correlation_id, causation_id, metadata, schema_version
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            event.event_id,
                            event.event_type.value,
                            event.get_aggregate_id(),
                            json.dumps(event_data),
                            event_hash,
                            chain_hash,
                            event.timestamp,
                            time.time(),
                            event.correlation_id,
                            event.causation_id,
                            json.dumps(event.metadata),
                            event.schema_version,
                        ))

                        # Get the assigned offset
                        offset = cursor.lastrowid
                        conn.commit()

                        # Create offset object
                        event_offset = EventOffset(
                            offset=offset,
                            timestamp=event.timestamp,
                            event_id=event.event_id,
                            hash=event_hash
                        )

                        # Track performance
                        append_time_ms = (time.perf_counter() - start_time) * 1000
                        self.metrics['append_times'].append(append_time_ms)
                        self.metrics['events_appended'] += 1

                        # Async dispatch to subscribers (non-blocking)
                        asyncio.create_task(self._dispatch_event(event, event_offset))

                        logger.debug(f"Event appended: {event.event_id} at offset {offset} in {append_time_ms:.2f}ms")

                        return event_offset

                    except Exception:
                        conn.rollback()
                        raise
                    finally:
                        conn.close()

        except Exception as e:
            self.metrics['processing_errors'] += 1
            logger.error(f"Failed to append event {event.event_id}: {e}")
            raise

    async def replay(self, from_offset: int, to_offset: Optional[int] = None) -> ReplayIterator:
        """
        Create iterator for event replay from specified offset.
        Guarantees deterministic replay order.
        """
        start_time = time.perf_counter()

        try:
            iterator = ReplayIterator(self, from_offset, to_offset)

            replay_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics['replay_times'].append(replay_time_ms)

            logger.debug(f"Replay iterator created for offset {from_offset}-{to_offset or 'end'} in {replay_time_ms:.2f}ms")

            return iterator

        except Exception as e:
            logger.error(f"Failed to create replay iterator: {e}")
            raise

    async def _get_event_at_offset(self, offset: int) -> Optional[Dict[str, Any]]:
        """Get event data at specific offset"""
        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    SELECT offset, event_id, event_type, aggregate_id, event_data,
                           hash, chain_hash, timestamp, correlation_id, causation_id, metadata
                    FROM event_store WHERE offset = ?
                """, (offset,))

                row = cursor.fetchone()
                if not row:
                    return None

                return {
                    'offset': row[0],
                    'event_id': row[1],
                    'event_type': row[2],
                    'aggregate_id': row[3],
                    'event_data': json.loads(row[4]),
                    'hash': row[5],
                    'chain_hash': row[6],
                    'timestamp': row[7],
                    'correlation_id': row[8],
                    'causation_id': row[9],
                    'metadata': json.loads(row[10] or '{}'),
                }

            finally:
                conn.close()

    async def _compute_next_chain_hash(self, current_event_hash: str) -> str:
        """Compute chain hash linking to previous event"""
        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    SELECT hash FROM event_store
                    ORDER BY offset DESC LIMIT 1
                """)

                row = cursor.fetchone()
                if not row:
                    # First event in chain
                    return hashlib.sha256(current_event_hash.encode()).hexdigest()

                previous_hash = row[0]
                chain_data = f"{previous_hash}:{current_event_hash}"
                return hashlib.sha256(chain_data.encode()).hexdigest()

            finally:
                conn.close()

    def subscribe(self, event_type: str, subscriber: EventSubscriber):
        """Subscribe to events of specific type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(subscriber)
        logger.info(f"Subscriber registered for event type: {event_type}")

    def unsubscribe(self, event_type: str, subscriber: EventSubscriber):
        """Unsubscribe from events of specific type"""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(subscriber)
                logger.info(f"Subscriber removed for event type: {event_type}")
            except ValueError:
                pass

    async def _dispatch_event(self, event: ConsentEvent, offset: EventOffset):
        """Dispatch event to subscribers with circuit breaker protection"""
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit breaker is open, skipping event dispatch")
            return

        event_type = event.event_type.value
        subscribers = self.subscribers.get(event_type, [])

        for subscriber in subscribers:
            try:
                success = await subscriber.handle_event(event, offset)
                if success:
                    self.circuit_breaker.on_success()
                else:
                    logger.warning(f"Subscriber failed to handle event {event.event_id}")
                    self.circuit_breaker.on_failure()
            except Exception as e:
                logger.error(f"Subscriber error for event {event.event_id}: {e}")
                self.circuit_breaker.on_failure()
                await self._add_to_dead_letter_queue(event, str(e))

    async def _add_to_dead_letter_queue(self, event: ConsentEvent, error_message: str):
        """Add failed event to dead letter queue for retry"""
        dead_letter_event = DeadLetterEvent(
            original_event=event.to_dict(),
            error_message=error_message,
            failure_count=1,
            first_failure_at=datetime.now(timezone.utc).isoformat(),
            last_failure_at=datetime.now(timezone.utc).isoformat(),
        )

        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO dead_letter_queue (
                        original_event, error_message, failure_count,
                        first_failure_at, last_failure_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    json.dumps(dead_letter_event.original_event),
                    dead_letter_event.error_message,
                    dead_letter_event.failure_count,
                    dead_letter_event.first_failure_at,
                    dead_letter_event.last_failure_at,
                ))

                conn.commit()
                logger.warning(f"Event {event.event_id} added to dead letter queue")

            finally:
                conn.close()

    async def get_latest_offset(self) -> int:
        """Get the latest event offset"""
        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            try:
                cursor.execute("SELECT MAX(offset) FROM event_store")
                row = cursor.fetchone()
                return row[0] or 0
            finally:
                conn.close()

    async def save_consumer_checkpoint(self, consumer_id: str, offset: int, metadata: Optional[Dict[str, Any]] = None):
        """Save consumer processing checkpoint"""
        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO consumer_checkpoints (
                        consumer_id, last_processed_offset, updated_at, metadata
                    ) VALUES (?, ?, ?, ?)
                """, (
                    consumer_id,
                    offset,
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(metadata or {}),
                ))

                conn.commit()

            finally:
                conn.close()

    async def get_consumer_checkpoint(self, consumer_id: str) -> Optional[int]:
        """Get consumer's last processed offset"""
        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    SELECT last_processed_offset FROM consumer_checkpoints
                    WHERE consumer_id = ?
                """, (consumer_id,))

                row = cursor.fetchone()
                return row[0] if row else None

            finally:
                conn.close()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring"""
        append_times = self.metrics['append_times']
        replay_times = self.metrics['replay_times']

        return {
            'events_appended': self.metrics['events_appended'],
            'processing_errors': self.metrics['processing_errors'],
            'append_p95_ms': sorted(append_times)[int(len(append_times) * 0.95)] if append_times else 0,
            'append_avg_ms': sum(append_times) / len(append_times) if append_times else 0,
            'replay_avg_ms': sum(replay_times) / len(replay_times) if replay_times else 0,
            'circuit_breaker_state': self.circuit_breaker.state.value,
            'dead_letter_queue_size': len(self.dead_letter_queue),
        }

    async def health_check(self) -> Dict[str, Any]:
        """Health check for event bus"""
        try:
            latest_offset = await self.get_latest_offset()
            metrics = self.get_performance_metrics()

            return {
                'status': 'healthy',
                'latest_offset': latest_offset,
                'metrics': metrics,
                'database_path': str(self.db_path),
                'subscribers_count': sum(len(subs) for subs in self.subscribers.values()),
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
            }
