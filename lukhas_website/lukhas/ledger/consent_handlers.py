"""
LUKHAS Ledger Consent Handlers v2.0.0
=====================================

Idempotent event consumers with at-least-once delivery guarantees.
Implements database projections from event stream with retry logic
and state persistence for T4/0.01% excellence requirements.
"""

import asyncio
import json
import logging
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .event_bus import AsyncEventBus, EventOffset, EventSubscriber
from .events import (
    ConsentCheckedEvent,
    ConsentEvent,
    ConsentGrantedEvent,
    ConsentRevokedEvent,
    EventType,
    TraceCreatedEvent,
)

logger = logging.getLogger(__name__)


@dataclass
class HandlerState:
    """State tracking for event handlers"""
    handler_id: str
    last_processed_offset: int
    processed_event_ids: set = field(default_factory=set)
    error_count: int = 0
    last_error: Optional[str] = None
    last_error_at: Optional[str] = None
    processing_start_time: Optional[float] = None
    total_events_processed: int = 0

    def mark_event_processed(self, event_id: str, offset: int):
        """Mark an event as successfully processed"""
        self.processed_event_ids.add(event_id)
        self.last_processed_offset = max(self.last_processed_offset, offset)
        self.total_events_processed += 1
        self.error_count = 0  # Reset error count on success
        self.last_error = None
        self.last_error_at = None

    def mark_error(self, error_message: str):
        """Mark a processing error"""
        self.error_count += 1
        self.last_error = error_message
        self.last_error_at = datetime.now(timezone.utc).isoformat()

    def is_duplicate_event(self, event_id: str) -> bool:
        """Check if event was already processed (idempotency)"""
        return event_id in self.processed_event_ids

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for persistence"""
        return {
            'handler_id': self.handler_id,
            'last_processed_offset': self.last_processed_offset,
            'processed_event_ids': list(self.processed_event_ids),
            'error_count': self.error_count,
            'last_error': self.last_error,
            'last_error_at': self.last_error_at,
            'total_events_processed': self.total_events_processed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HandlerState':
        """Deserialize state from persistence"""
        return cls(
            handler_id=data['handler_id'],
            last_processed_offset=data.get('last_processed_offset', 0),
            processed_event_ids=set(data.get('processed_event_ids', [])),
            error_count=data.get('error_count', 0),
            last_error=data.get('last_error'),
            last_error_at=data.get('last_error_at'),
            total_events_processed=data.get('total_events_processed', 0),
        )


class BaseEventHandler(EventSubscriber, ABC):
    """Base class for idempotent event handlers"""

    def __init__(self, handler_id: str, db_path: str, max_retries: int = 3, retry_delay: float = 1.0):
        self.handler_id = handler_id
        self.db_path = Path(db_path)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.state = HandlerState(handler_id, 0)
        self._lock = threading.RLock()

        # Initialize handler state storage
        self._init_handler_storage()

        # Load existing state
        self._load_state()

        logger.info(f"Handler {handler_id} initialized with last offset: {self.state.last_processed_offset}")

    def _init_handler_storage(self):
        """Initialize storage for handler state"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS handler_state (
                        handler_id TEXT PRIMARY KEY,
                        last_processed_offset INTEGER NOT NULL,
                        processed_event_ids TEXT,
                        error_count INTEGER DEFAULT 0,
                        last_error TEXT,
                        last_error_at TEXT,
                        total_events_processed INTEGER DEFAULT 0,
                        updated_at TEXT NOT NULL
                    )
                """)

                conn.commit()

            finally:
                conn.close()

    def _load_state(self):
        """Load handler state from database"""
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    SELECT last_processed_offset, processed_event_ids, error_count,
                           last_error, last_error_at, total_events_processed
                    FROM handler_state WHERE handler_id = ?
                """, (self.handler_id,))

                row = cursor.fetchone()
                if row:
                    self.state.last_processed_offset = row[0]
                    self.state.processed_event_ids = set(json.loads(row[1] or '[]'))
                    self.state.error_count = row[2]
                    self.state.last_error = row[3]
                    self.state.last_error_at = row[4]
                    self.state.total_events_processed = row[5] or 0

            finally:
                conn.close()

    def _save_state(self):
        """Save handler state to database"""
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO handler_state (
                        handler_id, last_processed_offset, processed_event_ids,
                        error_count, last_error, last_error_at,
                        total_events_processed, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.handler_id,
                    self.state.last_processed_offset,
                    json.dumps(list(self.state.processed_event_ids)),
                    self.state.error_count,
                    self.state.last_error,
                    self.state.last_error_at,
                    self.state.total_events_processed,
                    datetime.now(timezone.utc).isoformat(),
                ))

                conn.commit()

            finally:
                conn.close()

    async def handle_event(self, event: ConsentEvent, offset: EventOffset) -> bool:
        """Handle event with idempotency and retry logic"""
        # Skip if already processed (idempotency guarantee)
        if self.state.is_duplicate_event(event.event_id):
            logger.debug(f"Skipping duplicate event {event.event_id}")
            return True

        # Skip if offset is too old (already processed)
        if offset.offset <= self.state.last_processed_offset:
            logger.debug(f"Skipping old event at offset {offset.offset}")
            return True

        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                # Process the event
                success = await self._process_event(event, offset)

                if success:
                    # Mark as processed and save state
                    self.state.mark_event_processed(event.event_id, offset.offset)
                    self._save_state()

                    logger.debug(f"Successfully processed event {event.event_id} at offset {offset.offset}")
                    return True
                else:
                    # Processing returned False (soft failure)
                    retry_count += 1
                    if retry_count <= self.max_retries:
                        await asyncio.sleep(self.retry_delay * retry_count)  # Exponential backoff
                    continue

            except Exception as e:
                retry_count += 1
                error_msg = f"Error processing event {event.event_id}: {e!s}"
                logger.error(error_msg)

                self.state.mark_error(error_msg)

                if retry_count <= self.max_retries:
                    logger.info(f"Retrying event {event.event_id} (attempt {retry_count}/{self.max_retries})")
                    await asyncio.sleep(self.retry_delay * retry_count)
                else:
                    logger.error(f"Max retries exceeded for event {event.event_id}")
                    break

        # All retries exhausted
        self._save_state()
        return False

    @abstractmethod
    async def _process_event(self, event: ConsentEvent, offset: EventOffset) -> bool:
        """Process the specific event. Return True for success, False for retry."""
        pass

    def get_handler_metrics(self) -> Dict[str, Any]:
        """Get handler performance metrics"""
        return {
            'handler_id': self.handler_id,
            'last_processed_offset': self.state.last_processed_offset,
            'total_events_processed': self.state.total_events_processed,
            'current_error_count': self.state.error_count,
            'last_error': self.state.last_error,
            'last_error_at': self.state.last_error_at,
            'processed_events_cache_size': len(self.state.processed_event_ids),
        }


class IdempotentConsentHandler(BaseEventHandler):
    """
    Idempotent handler for consent-related events.

    Updates consent_records table projections from event stream
    with at-least-once delivery guarantees.
    """

    def __init__(self, consent_db_path: str, handler_db_path: str = "ledger/consent_handler.db"):
        super().__init__("consent_handler", handler_db_path)
        self.consent_db_path = Path(consent_db_path)

        # Initialize consent database connection
        self._init_consent_database()

        logger.info(f"ConsentHandler initialized with consent DB: {self.consent_db_path}")

    def _init_consent_database(self):
        """Initialize consent database (same schema as original)"""
        self.consent_db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(self.consent_db_path))
        cursor = conn.cursor()

        try:
            # Enable WAL mode for better concurrent access
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=FULL;")
            cursor.execute("PRAGMA foreign_keys=ON;")

            # Consent records table (projection from events)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consent_records (
                    consent_id TEXT PRIMARY KEY,
                    lid TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    scopes TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    lawful_basis TEXT NOT NULL,
                    consent_type TEXT NOT NULL,
                    granted_at TEXT NOT NULL,
                    expires_at TEXT,
                    revoked_at TEXT,
                    data_categories TEXT,
                    third_parties TEXT,
                    processing_locations TEXT,
                    is_active INTEGER DEFAULT 1,
                    trace_id TEXT NOT NULL,
                    withdrawal_method TEXT,
                    renewal_required INTEGER DEFAULT 0,
                    data_subject_rights TEXT,
                    retention_period INTEGER,
                    automated_decision_making INTEGER DEFAULT 0,
                    profiling INTEGER DEFAULT 0,
                    children_data INTEGER DEFAULT 0,
                    sensitive_data INTEGER DEFAULT 0
                )
            """)

            # Indexes for performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_lid_consent ON consent_records(lid)",
                "CREATE INDEX IF NOT EXISTS idx_active_consent ON consent_records(is_active)",
                "CREATE INDEX IF NOT EXISTS idx_expires_at ON consent_records(expires_at)",
                "CREATE INDEX IF NOT EXISTS idx_resource_type ON consent_records(resource_type)",
            ]

            for index_sql in indexes:
                cursor.execute(index_sql)

            conn.commit()

        finally:
            conn.close()

    async def _process_event(self, event: ConsentEvent, offset: EventOffset) -> bool:
        """Process consent-specific events"""
        try:
            if isinstance(event, ConsentGrantedEvent):
                return await self._handle_consent_granted(event)
            elif isinstance(event, ConsentRevokedEvent):
                return await self._handle_consent_revoked(event)
            elif isinstance(event, ConsentCheckedEvent):
                return await self._handle_consent_checked(event)
            else:
                # Not a consent-related event, skip
                return True

        except Exception as e:
            logger.error(f"Error processing consent event {event.event_id}: {e}")
            return False

    async def _handle_consent_granted(self, event: ConsentGrantedEvent) -> bool:
        """Handle consent granted event - insert/update consent record"""
        conn = sqlite3.connect(str(self.consent_db_path))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO consent_records (
                    consent_id, lid, resource_type, scopes, purpose,
                    lawful_basis, consent_type, granted_at, expires_at,
                    data_categories, third_parties, processing_locations,
                    trace_id, withdrawal_method, data_subject_rights,
                    retention_period, automated_decision_making, profiling,
                    children_data, sensitive_data, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                event.consent_id,
                event.lid,
                event.resource_type,
                json.dumps(event.scopes),
                event.purpose,
                event.lawful_basis,
                event.consent_type.value,
                event.granted_at,
                event.expires_at,
                json.dumps(event.data_categories),
                json.dumps(event.third_parties),
                json.dumps(event.processing_locations),
                event.trace_id,
                event.withdrawal_method,
                json.dumps([right.value for right in event.data_subject_rights]),
                event.retention_period,
                1 if event.automated_decision_making else 0,
                1 if event.profiling else 0,
                1 if event.children_data else 0,
                1 if event.sensitive_data else 0,
            ))

            conn.commit()
            logger.debug(f"Consent granted: {event.consent_id}")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to handle consent granted event: {e}")
            return False

        finally:
            conn.close()

    async def _handle_consent_revoked(self, event: ConsentRevokedEvent) -> bool:
        """Handle consent revoked event - mark consent as inactive"""
        conn = sqlite3.connect(str(self.consent_db_path))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE consent_records
                SET revoked_at = ?, is_active = 0
                WHERE consent_id = ? AND lid = ?
            """, (event.revoked_at, event.consent_id, event.lid))

            if cursor.rowcount == 0:
                logger.warning(f"No consent record found to revoke: {event.consent_id}")

            conn.commit()
            logger.debug(f"Consent revoked: {event.consent_id}")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to handle consent revoked event: {e}")
            return False

        finally:
            conn.close()

    async def _handle_consent_checked(self, event: ConsentCheckedEvent) -> bool:
        """Handle consent checked event - could update analytics/audit logs"""
        # For now, just log the check - could be extended for analytics
        logger.debug(f"Consent checked for {event.lid}: {event.action} on {event.resource_type} - {'allowed' if event.allowed else 'denied'}")
        return True


class IdempotentTraceHandler(BaseEventHandler):
    """
    Idempotent handler for Lambda trace events.

    Updates lambda_traces table projections from event stream.
    """

    def __init__(self, trace_db_path: str, handler_db_path: str = "ledger/trace_handler.db"):
        super().__init__("trace_handler", handler_db_path)
        self.trace_db_path = Path(trace_db_path)

        self._init_trace_database()
        logger.info(f"TraceHandler initialized with trace DB: {self.trace_db_path}")

    def _init_trace_database(self):
        """Initialize lambda traces database"""
        self.trace_db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(self.trace_db_path))
        cursor = conn.cursor()

        try:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=FULL;")
            cursor.execute("PRAGMA foreign_keys=ON;")

            # Lambda traces table (same schema as original)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lambda_traces (
                    trace_id TEXT PRIMARY KEY,
                    lid TEXT NOT NULL,
                    parent_trace_id TEXT,
                    action TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    policy_verdict TEXT NOT NULL,
                    capability_token_id TEXT,
                    context TEXT,
                    explanation_unl TEXT,
                    hash TEXT UNIQUE NOT NULL,
                    signature TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    glyph_signature TEXT,
                    triad_identity_verified INTEGER DEFAULT 0,
                    triad_consciousness_aligned INTEGER DEFAULT 0,
                    triad_guardian_approved INTEGER DEFAULT 0,
                    compliance_flags TEXT,
                    chain_integrity TEXT,
                    FOREIGN KEY (parent_trace_id) REFERENCES lambda_traces(trace_id)
                )
            """)

            # Performance indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_lid_traces ON lambda_traces(lid)",
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON lambda_traces(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_policy_verdict ON lambda_traces(policy_verdict)",
                "CREATE INDEX IF NOT EXISTS idx_triad_approved ON lambda_traces(triad_guardian_approved)",
            ]

            for index_sql in indexes:
                cursor.execute(index_sql)

            conn.commit()

        finally:
            conn.close()

    async def _process_event(self, event: ConsentEvent, offset: EventOffset) -> bool:
        """Process trace-related events"""
        try:
            if isinstance(event, TraceCreatedEvent):
                return await self._handle_trace_created(event)
            else:
                # Not a trace event, skip
                return True

        except Exception as e:
            logger.error(f"Error processing trace event {event.event_id}: {e}")
            return False

    async def _handle_trace_created(self, event: TraceCreatedEvent) -> bool:
        """Handle trace created event - insert trace record"""
        conn = sqlite3.connect(str(self.trace_db_path))
        cursor = conn.cursor()

        try:
            # Compute hash and signature (simplified for event sourcing)
            trace_hash = event.compute_hash()
            signature = trace_hash[:32]  # Simplified signature

            cursor.execute("""
                INSERT OR REPLACE INTO lambda_traces (
                    trace_id, lid, parent_trace_id, action, resource,
                    purpose, timestamp, policy_verdict, capability_token_id,
                    context, explanation_unl, hash, signature, created_at,
                    glyph_signature, triad_identity_verified,
                    triad_consciousness_aligned, triad_guardian_approved,
                    compliance_flags, chain_integrity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.trace_id,
                event.lid,
                event.parent_trace_id,
                event.action,
                event.resource,
                event.purpose,
                event.timestamp,
                event.policy_verdict.value,
                event.capability_token_id,
                json.dumps(event.context),
                event.explanation_unl,
                trace_hash,
                signature,
                time.time(),
                event.glyph_signature,
                1 if event.triad_validation.get("identity_verified", False) else 0,
                1 if event.triad_validation.get("consciousness_aligned", False) else 0,
                1 if event.triad_validation.get("guardian_approved", False) else 0,
                json.dumps(event.compliance_flags),
                event.chain_integrity,
            ))

            conn.commit()
            logger.debug(f"Trace created: {event.trace_id}")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to handle trace created event: {e}")
            return False

        finally:
            conn.close()


class ConsentHandlerOrchestrator:
    """
    Orchestrator for managing multiple consent event handlers.

    Provides centralized control and monitoring of all handlers
    with lag detection and performance tracking.
    """

    def __init__(self, event_bus: AsyncEventBus):
        self.event_bus = event_bus
        self.handlers: List[BaseEventHandler] = []
        self.running = False
        self._tasks: List[asyncio.Task] = []

        logger.info("ConsentHandlerOrchestrator initialized")

    def register_handler(self, handler: BaseEventHandler, event_types: List[EventType]):
        """Register handler for specific event types"""
        self.handlers.append(handler)

        for event_type in event_types:
            self.event_bus.subscribe(event_type.value, handler)

        logger.info(f"Registered handler {handler.handler_id} for events: {[et.value for et in event_types]}")

    async def start_processing(self):
        """Start processing events for all handlers"""
        if self.running:
            return

        self.running = True

        # Start catchup processing for each handler
        for handler in self.handlers:
            task = asyncio.create_task(self._process_handler_catchup(handler))
            self._tasks.append(task)

        logger.info(f"Started processing for {len(self.handlers)} handlers")

    async def stop_processing(self):
        """Stop processing and cleanup"""
        self.running = False

        # Cancel all tasks
        for task in self._tasks:
            task.cancel()

        # Wait for graceful shutdown
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        self._tasks.clear()
        logger.info("Stopped all handler processing")

    async def _process_handler_catchup(self, handler: BaseEventHandler):
        """Process catchup events for a specific handler"""
        try:
            while self.running:
                # Get handler's last processed offset
                last_offset = handler.state.last_processed_offset

                # Get latest offset from event bus
                latest_offset = await self.event_bus.get_latest_offset()

                if last_offset < latest_offset:
                    # Process catchup events
                    replay_iterator = await self.event_bus.replay(last_offset + 1, latest_offset + 1)

                    async for event, offset in replay_iterator:
                        if not self.running:
                            break

                        await handler.handle_event(event, offset)

                # Sleep before checking for new events
                await asyncio.sleep(1.0)

        except asyncio.CancelledError:
            logger.info(f"Handler {handler.handler_id} processing cancelled")
        except Exception as e:
            logger.error(f"Error in handler {handler.handler_id} catchup: {e}")

    def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """Get metrics for all handlers"""
        metrics = {
            'total_handlers': len(self.handlers),
            'running': self.running,
            'handlers': []
        }

        for handler in self.handlers:
            handler_metrics = handler.get_handler_metrics()
            metrics['handlers'].append(handler_metrics)

        return metrics

    async def health_check(self) -> Dict[str, Any]:
        """Health check for all handlers"""
        healthy_handlers = 0
        total_processed = 0
        total_errors = 0

        for handler in self.handlers:
            metrics = handler.get_handler_metrics()
            total_processed += metrics['total_events_processed']
            total_errors += metrics['current_error_count']

            if metrics['current_error_count'] < 10:  # Threshold for healthy
                healthy_handlers += 1

        return {
            'status': 'healthy' if healthy_handlers == len(self.handlers) else 'degraded',
            'healthy_handlers': healthy_handlers,
            'total_handlers': len(self.handlers),
            'total_events_processed': total_processed,
            'total_errors': total_errors,
            'running': self.running,
        }
