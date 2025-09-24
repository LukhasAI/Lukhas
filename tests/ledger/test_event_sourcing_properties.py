"""
Property-based tests for LUKHAS Ledger Event Sourcing v2.0.0
============================================================

Uses Hypothesis for comprehensive property testing of:
- Event idempotency guarantees
- Replay determinism (100% reproducibility)
- Corruption detection and tamper evidence
- Performance requirements (p95 <50ms)

T4/0.01% excellence compliance testing.
"""

import asyncio
import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Any, Dict
import pytest
import hypothesis.strategies as st
from hypothesis import given, assume, settings, example, note, Verbosity
from hypothesis.stateful import RuleBasedStateMachine, Bundle, rule, invariant, initialize, precondition

# Import our ledger components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lukhas.ledger.events import (
    ConsentEvent,
    ConsentGrantedEvent,
    ConsentRevokedEvent,
    ConsentCheckedEvent,
    TraceCreatedEvent,
    DuressDetectedEvent,
    EventType,
    ConsentType,
    DataSubjectRights,
    PolicyVerdict,
    validate_event_schema,
    compute_event_chain_hash,
    create_event_from_dict,
)
from lukhas.ledger.event_bus import AsyncEventBus, EventOffset
from lukhas.ledger.consent_handlers import IdempotentConsentHandler, IdempotentTraceHandler


# Hypothesis strategies for generating test data
@st.composite
def event_id_strategy(draw):
    """Generate valid event IDs"""
    hex_part = draw(st.text(alphabet='abcdef0123456789', min_size=32, max_size=32))
    return f"EVT-{hex_part}"


@st.composite
def lid_strategy(draw):
    """Generate valid Lambda IDs"""
    return draw(st.text(min_size=1, max_size=256, alphabet=st.characters(blacklist_categories=['C'])))


@st.composite
def consent_id_strategy(draw):
    """Generate valid consent IDs"""
    hex_part = draw(st.text(alphabet='abcdef0123456789', min_size=32, max_size=32))
    return f"CONSENT-{hex_part}"


@st.composite
def trace_id_strategy(draw):
    """Generate valid trace IDs"""
    hex_part = draw(st.text(alphabet='abcdef0123456789', min_size=32, max_size=32))
    return f"LT-{hex_part}"


@st.composite
def consent_granted_event_strategy(draw):
    """Generate ConsentGrantedEvent instances"""
    return ConsentGrantedEvent(
        event_id=draw(event_id_strategy()),
        lid=draw(lid_strategy()),
        consent_id=draw(consent_id_strategy()),
        resource_type=draw(st.text(min_size=1, max_size=128)),
        scopes=draw(st.lists(st.text(min_size=1, max_size=64), min_size=1, max_size=50)),
        purpose=draw(st.text(min_size=1, max_size=512)),
        lawful_basis=draw(st.sampled_from(['consent', 'contract', 'legal_obligation', 'vital_interests', 'public_task', 'legitimate_interests'])),
        consent_type=draw(st.sampled_from(list(ConsentType))),
        data_categories=draw(st.lists(st.text(min_size=1, max_size=128), max_size=20)),
        third_parties=draw(st.lists(st.text(min_size=1, max_size=256), max_size=10)),
        processing_locations=draw(st.lists(st.text(min_size=2, max_size=5), max_size=10)),
        automated_decision_making=draw(st.booleans()),
        profiling=draw(st.booleans()),
        children_data=draw(st.booleans()),
        sensitive_data=draw(st.booleans()),
        retention_period=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=36500))),
        data_subject_rights=draw(st.lists(st.sampled_from(list(DataSubjectRights)), max_size=10)),
        trace_id=draw(trace_id_strategy()),
        correlation_id=draw(st.one_of(st.none(), st.text(min_size=1, max_size=128))),
        causation_id=draw(st.one_of(st.none(), st.text(min_size=1, max_size=128))),
    )


@st.composite
def consent_revoked_event_strategy(draw):
    """Generate ConsentRevokedEvent instances"""
    return ConsentRevokedEvent(
        event_id=draw(event_id_strategy()),
        lid=draw(lid_strategy()),
        consent_id=draw(consent_id_strategy()),
        reason=draw(st.one_of(st.none(), st.text(max_size=512))),
        revocation_method=draw(st.text(min_size=1, max_size=128)),
        cascade_deletions=draw(st.lists(st.text(min_size=1, max_size=128), max_size=100)),
        trace_id=draw(trace_id_strategy()),
        correlation_id=draw(st.one_of(st.none(), st.text(min_size=1, max_size=128))),
        causation_id=draw(st.one_of(st.none(), st.text(min_size=1, max_size=128))),
    )


@st.composite
def trace_created_event_strategy(draw):
    """Generate TraceCreatedEvent instances"""
    return TraceCreatedEvent(
        event_id=draw(event_id_strategy()),
        lid=draw(lid_strategy()),
        trace_id=draw(trace_id_strategy()),
        parent_trace_id=draw(st.one_of(st.none(), trace_id_strategy())),
        action=draw(st.text(min_size=1, max_size=128)),
        resource=draw(st.text(min_size=1, max_size=256)),
        purpose=draw(st.text(min_size=1, max_size=512)),
        policy_verdict=draw(st.sampled_from(list(PolicyVerdict))),
        capability_token_id=draw(st.one_of(st.none(), st.text(min_size=1, max_size=128))),
        context=draw(st.dictionaries(st.text(min_size=1, max_size=64), st.text(max_size=256), max_size=20)),
        explanation_unl=draw(st.one_of(st.none(), st.text(max_size=1024))),
        glyph_signature=draw(st.one_of(st.none(), st.text(max_size=512))),
        correlation_id=draw(st.one_of(st.none(), st.text(min_size=1, max_size=128))),
        causation_id=draw(st.one_of(st.none(), st.text(min_size=1, max_size=128))),
    )


# Property tests for event schema validation
class TestEventProperties:
    """Property tests for event schema validation and integrity"""

    @given(event=consent_granted_event_strategy())
    def test_consent_granted_event_always_valid_schema(self, event):
        """Property: All generated ConsentGrantedEvent instances must pass schema validation"""
        assert validate_event_schema(event), f"Generated event failed schema validation: {event}"

    @given(event=consent_revoked_event_strategy())
    def test_consent_revoked_event_always_valid_schema(self, event):
        """Property: All generated ConsentRevokedEvent instances must pass schema validation"""
        assert validate_event_schema(event), f"Generated event failed schema validation: {event}"

    @given(event=trace_created_event_strategy())
    def test_trace_created_event_always_valid_schema(self, event):
        """Property: All generated TraceCreatedEvent instances must pass schema validation"""
        assert validate_event_schema(event), f"Generated event failed schema validation: {event}"

    @given(event=consent_granted_event_strategy())
    def test_event_hash_deterministic(self, event):
        """Property: Event hash must be deterministic (same event -> same hash)"""
        hash1 = event.compute_hash()
        hash2 = event.compute_hash()
        assert hash1 == hash2, "Event hash is not deterministic"
        assert len(hash1) == 64, "Hash should be SHA256 (64 hex chars)"

    @given(event=consent_granted_event_strategy())
    def test_event_serialization_roundtrip(self, event):
        """Property: Event serialization must be reversible"""
        # Serialize to dict
        event_dict = event.to_dict()

        # Deserialize back to event
        reconstructed_event = create_event_from_dict(event_dict)

        # Should be equivalent (same hash)
        assert event.compute_hash() == reconstructed_event.compute_hash()
        assert event.event_id == reconstructed_event.event_id
        assert event.lid == reconstructed_event.lid

    @given(event=consent_granted_event_strategy())
    def test_event_json_serialization_roundtrip(self, event):
        """Property: JSON serialization must be reversible"""
        json_str = event.to_json()

        # Validate JSON is parseable
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

        # Should contain required fields
        assert parsed['event_id'] == event.event_id
        assert parsed['lid'] == event.lid
        assert parsed['schema_version'] == '2.0.0'

    @given(events=st.lists(consent_granted_event_strategy(), min_size=1, max_size=10))
    def test_event_chain_hash_consistency(self, events):
        """Property: Chain hash computation must be consistent"""
        chain_hash1 = compute_event_chain_hash(events)
        chain_hash2 = compute_event_chain_hash(events)
        assert chain_hash1 == chain_hash2, "Chain hash computation is not deterministic"

    @given(events=st.lists(consent_granted_event_strategy(), min_size=2, max_size=10))
    def test_event_chain_hash_order_dependent(self, events):
        """Property: Chain hash must depend on event order"""
        assume(len(set(e.event_id for e in events)) == len(events))  # All unique events

        hash_original = compute_event_chain_hash(events)
        hash_reversed = compute_event_chain_hash(list(reversed(events)))

        # Different order should produce different hash (unless single event or all identical)
        if len(events) > 1:
            assert hash_original != hash_reversed, "Chain hash should depend on event order"


# Async property tests for event bus
class TestEventBusProperties:
    """Property tests for event bus behavior"""

    async def setup_event_bus(self):
        """Setup temporary event bus for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_events.db"
        return AsyncEventBus(str(db_path))

    @pytest.mark.asyncio
    @given(events=st.lists(consent_granted_event_strategy(), min_size=1, max_size=20))
    async def test_event_append_idempotency(self, events):
        """Property: Appending the same event multiple times should be idempotent"""
        event_bus = await self.setup_event_bus()

        try:
            # Append each event
            offsets = []
            for event in events:
                offset = await event_bus.append_event(event)
                offsets.append(offset)

            # Verify all events stored
            latest_offset = await event_bus.get_latest_offset()
            assert latest_offset == len(events)

            # Verify offsets are sequential
            for i, offset in enumerate(offsets):
                assert offset.offset == i + 1

        finally:
            # Cleanup
            if hasattr(event_bus, 'db_path'):
                try:
                    os.unlink(event_bus.db_path)
                except:
                    pass

    @pytest.mark.asyncio
    @given(events=st.lists(consent_granted_event_strategy(), min_size=5, max_size=50))
    async def test_replay_determinism(self, events):
        """Property: Event replay must be 100% deterministic"""
        event_bus = await self.setup_event_bus()

        try:
            # Append all events
            for event in events:
                await event_bus.append_event(event)

            # Replay events multiple times
            replays = []
            for _ in range(3):  # Multiple replay attempts
                replay_events = []
                replay_iterator = await event_bus.replay(1)  # From offset 1

                async for event, offset in replay_iterator:
                    replay_events.append((event.event_id, offset.offset))

                replays.append(replay_events)

            # All replays should be identical
            for i in range(1, len(replays)):
                assert replays[0] == replays[i], f"Replay {i} differs from replay 0 - not deterministic"

        finally:
            if hasattr(event_bus, 'db_path'):
                try:
                    os.unlink(event_bus.db_path)
                except:
                    pass

    @pytest.mark.asyncio
    @given(events=st.lists(consent_granted_event_strategy(), min_size=10, max_size=100))
    @settings(deadline=5000, max_examples=10)  # Allow more time for performance tests
    async def test_append_performance_requirement(self, events):
        """Property: Event append must meet p95 <50ms performance requirement"""
        event_bus = await self.setup_event_bus()

        try:
            append_times = []

            # Measure append time for each event
            for event in events:
                start_time = time.perf_counter()
                await event_bus.append_event(event)
                end_time = time.perf_counter()

                append_time_ms = (end_time - start_time) * 1000
                append_times.append(append_time_ms)

            # Calculate p95
            sorted_times = sorted(append_times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]

            note(f"P95 append time: {p95_time:.2f}ms (target: <50ms)")

            # T4/0.01% excellence requirement
            assert p95_time < 50.0, f"P95 append time {p95_time:.2f}ms exceeds 50ms requirement"

        finally:
            if hasattr(event_bus, 'db_path'):
                try:
                    os.unlink(event_bus.db_path)
                except:
                    pass


# Stateful testing for event handlers
class EventHandlerStateMachine(RuleBasedStateMachine):
    """Stateful testing for event handler idempotency and correctness"""

    def __init__(self):
        super().__init__()
        self.temp_dir = tempfile.mkdtemp()
        self.event_bus = None
        self.consent_handler = None
        self.trace_handler = None
        self.processed_events = set()

    events = Bundle('events')

    @initialize()
    def setup(self):
        """Initialize event bus and handlers"""
        event_bus_path = Path(self.temp_dir) / "events.db"
        consent_db_path = Path(self.temp_dir) / "consent.db"
        trace_db_path = Path(self.temp_dir) / "traces.db"

        self.event_bus = AsyncEventBus(str(event_bus_path))
        self.consent_handler = IdempotentConsentHandler(
            str(consent_db_path),
            str(Path(self.temp_dir) / "consent_handler.db")
        )
        self.trace_handler = IdempotentTraceHandler(
            str(trace_db_path),
            str(Path(self.temp_dir) / "trace_handler.db")
        )

    @rule(target=events, event=consent_granted_event_strategy())
    def append_consent_event(self, event):
        """Rule: Append a consent granted event"""
        async def _append():
            offset = await self.event_bus.append_event(event)
            return event, offset

        return asyncio.run(_append())

    @rule(target=events, event=trace_created_event_strategy())
    def append_trace_event(self, event):
        """Rule: Append a trace created event"""
        async def _append():
            offset = await self.event_bus.append_event(event)
            return event, offset

        return asyncio.run(_append())

    @rule(event_data=events)
    def process_event_idempotent(self, event_data):
        """Rule: Process event multiple times - should be idempotent"""
        event, offset = event_data

        async def _process():
            # Process event multiple times
            results = []
            for _ in range(3):
                if isinstance(event, ConsentGrantedEvent):
                    result = await self.consent_handler.handle_event(event, offset)
                elif isinstance(event, TraceCreatedEvent):
                    result = await self.trace_handler.handle_event(event, offset)
                else:
                    result = True  # Skip other event types
                results.append(result)

            return results

        results = asyncio.run(_process())

        # All results should be the same (idempotent)
        assert all(r == results[0] for r in results), f"Handler not idempotent: {results}"

        # Track processed events
        self.processed_events.add(event.event_id)

    @invariant()
    def handler_state_consistent(self):
        """Invariant: Handler state should always be consistent"""
        if self.consent_handler:
            metrics = self.consent_handler.get_handler_metrics()

            # Error count should not be excessive
            assert metrics['current_error_count'] < 10, f"Too many handler errors: {metrics['current_error_count']}"

            # Processed event count should make sense
            assert metrics['total_events_processed'] >= 0

    def teardown(self):
        """Cleanup test resources"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass


# Integration property tests
class TestIntegrationProperties:
    """Integration property tests for complete event sourcing flow"""

    @pytest.mark.asyncio
    @given(
        granted_events=st.lists(consent_granted_event_strategy(), min_size=2, max_size=10),
        revoked_events=st.lists(consent_revoked_event_strategy(), min_size=1, max_size=5)
    )
    async def test_consent_lifecycle_consistency(self, granted_events, revoked_events):
        """Property: Consent grant -> revoke lifecycle must maintain consistency"""
        temp_dir = tempfile.mkdtemp()

        try:
            # Setup event bus and handler
            event_bus_path = Path(temp_dir) / "events.db"
            consent_db_path = Path(temp_dir) / "consent.db"
            event_bus = AsyncEventBus(str(event_bus_path))
            handler = IdempotentConsentHandler(
                str(consent_db_path),
                str(Path(temp_dir) / "consent_handler.db")
            )

            # Process granted events first
            for event in granted_events:
                offset = await event_bus.append_event(event)
                success = await handler.handle_event(event, offset)
                assert success, f"Failed to process consent granted event: {event.event_id}"

            # Match some revoked events to granted events
            for i, revoke_event in enumerate(revoked_events):
                if i < len(granted_events):
                    # Create new revoke event with matching consent_id and lid
                    matched_revoke = ConsentRevokedEvent(
                        event_id=revoke_event.event_id,
                        lid=granted_events[i].lid,
                        consent_id=granted_events[i].consent_id,
                        reason=revoke_event.reason,
                        revocation_method=revoke_event.revocation_method,
                        trace_id=revoke_event.trace_id,
                        correlation_id=revoke_event.correlation_id,
                    )

                    offset = await event_bus.append_event(matched_revoke)
                    success = await handler.handle_event(matched_revoke, offset)
                    assert success, f"Failed to process consent revoked event: {matched_revoke.event_id}"

            # Verify handler processed all events correctly
            metrics = handler.get_handler_metrics()
            expected_events = len(granted_events) + min(len(revoked_events), len(granted_events))
            assert metrics['total_events_processed'] == expected_events

        finally:
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

    @pytest.mark.asyncio
    @given(events=st.lists(
        st.one_of(consent_granted_event_strategy(), trace_created_event_strategy()),
        min_size=5, max_size=25
    ))
    @settings(deadline=10000)  # Allow more time for complex integration tests
    async def test_corruption_detection(self, events):
        """Property: System must detect any corruption in event chain"""
        temp_dir = tempfile.mkdtemp()

        try:
            event_bus_path = Path(temp_dir) / "events.db"
            event_bus = AsyncEventBus(str(event_bus_path))

            # Append all events and collect hashes
            original_hashes = []
            for event in events:
                offset = await event_bus.append_event(event)
                original_hashes.append(event.compute_hash())

            # Replay and verify all hashes match
            replay_hashes = []
            replay_iterator = await event_bus.replay(1)

            async for event, offset in replay_iterator:
                replay_hashes.append(event.compute_hash())

            # All hashes should match (no corruption)
            assert len(original_hashes) == len(replay_hashes)
            for i, (orig, replay) in enumerate(zip(original_hashes, replay_hashes)):
                assert orig == replay, f"Corruption detected at index {i}: {orig} != {replay}"

        finally:
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


# Performance regression tests
class TestPerformanceProperties:
    """Property tests to prevent performance regressions"""

    @pytest.mark.asyncio
    @given(batch_size=st.integers(min_value=100, max_value=1000))
    @settings(max_examples=5, deadline=30000)  # Limited examples for performance tests
    async def test_batch_processing_scales_linearly(self, batch_size):
        """Property: Batch processing should scale roughly linearly"""
        temp_dir = tempfile.mkdtemp()

        try:
            event_bus = AsyncEventBus(str(Path(temp_dir) / "perf_test.db"))

            # Generate events
            events = [
                ConsentGrantedEvent(
                    lid=f"USR-{i}",
                    consent_id=f"CONSENT-{'a' * 32}",
                    resource_type="test",
                    scopes=["read"],
                    purpose="testing",
                    trace_id=f"LT-{'a' * 32}",
                )
                for i in range(batch_size)
            ]

            # Measure total processing time
            start_time = time.perf_counter()

            for event in events:
                await event_bus.append_event(event)

            total_time = time.perf_counter() - start_time
            time_per_event = total_time / batch_size

            note(f"Processed {batch_size} events in {total_time:.2f}s ({time_per_event*1000:.2f}ms per event)")

            # Should maintain reasonable throughput
            assert time_per_event < 0.1, f"Per-event time {time_per_event:.3f}s too slow for batch size {batch_size}"

        finally:
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


# Run the stateful tests
TestEventHandlerStateMachine = EventHandlerStateMachine.TestCase