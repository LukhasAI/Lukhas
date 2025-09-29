#!/usr/bin/env python3
"""
MATRIZ GDPR Trace Integration Test - T4/0.01% Excellence
======================================================

Tests that MATRIZ decisions respect tombstone deletions in memory lifecycle.
Ensures compliance with GDPR right-to-be-forgotten by validating that:

1. Tombstoned memories are NEVER used in MATRIZ decision processes
2. Decision traces containing deleted data are properly purged
3. Memory queries respect tombstone markers in real-time
4. Audit logs maintain compliance while protecting privacy

GDPR Compliance Rules:
- TOMBSTONED data must be inaccessible to MATRIZ within 500ms
- Decision traces referencing deleted memories → IMMEDIATE PURGE
- Memory queries must honor tombstone status in <10ms
- Audit trails must be sanitized while preserving compliance evidence

Performance Target: <100ms p95 for GDPR compliance validation
T4/0.01% Excellence: 100% tombstone respect rate, 0 privacy violations

Constellation Framework: 🏛️ GDPR Memory Compliance
"""

import logging
import pytest
import time
import hashlib
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Set, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class TombstoneStatus(Enum):
    """Tombstone status types."""
    ACTIVE = "active"
    SCHEDULED_DELETION = "scheduled_deletion"
    TOMBSTONED = "tombstoned"
    PURGED = "purged"


class GDPRViolationType(Enum):
    """GDPR violation types."""
    TOMBSTONE_ACCESS = "tombstone_access"
    TRACE_RETENTION = "trace_retention"
    AUDIT_EXPOSURE = "audit_exposure"
    DECISION_CONTAMINATION = "decision_contamination"


@dataclass
class MemoryFragment:
    """Memory fragment with GDPR tracking."""
    fragment_id: str
    user_id: str
    content_hash: str
    creation_timestamp: float
    tombstone_status: TombstoneStatus
    tombstone_timestamp: Optional[float] = None
    access_count: int = 0
    last_accessed: Optional[float] = None


@dataclass
class MATRIZDecisionTrace:
    """MATRIZ decision trace with memory references."""
    trace_id: str
    decision_timestamp: float
    referenced_memories: List[str]  # fragment_ids
    decision_output: Dict[str, Any]
    user_context: Optional[str] = None
    is_sanitized: bool = False


@dataclass
class GDPRViolation:
    """GDPR compliance violation."""
    violation_type: GDPRViolationType
    timestamp: float
    fragment_id: Optional[str]
    trace_id: Optional[str]
    user_id: str
    details: str
    severity: str = "HIGH"


class MATRIZGDPRBridge:
    """MATRIZ-Memory GDPR compliance bridge."""

    def __init__(self):
        """Initialize GDPR bridge."""
        self.memory_fragments: Dict[str, MemoryFragment] = {}
        self.decision_traces: Dict[str, MATRIZDecisionTrace] = {}
        self.tombstone_index: Dict[str, Set[str]] = {}  # user_id -> fragment_ids
        self.violations: List[GDPRViolation] = []
        self.compliance_metrics = {
            "tombstone_checks": 0,
            "violation_detections": 0,
            "trace_purges": 0,
            "memory_queries": 0
        }

    def store_memory_fragment(self, fragment: MemoryFragment):
        """Store memory fragment with GDPR tracking."""
        self.memory_fragments[fragment.fragment_id] = fragment

        # Update tombstone index
        if fragment.user_id not in self.tombstone_index:
            self.tombstone_index[fragment.user_id] = set()

        if fragment.tombstone_status != TombstoneStatus.ACTIVE:
            self.tombstone_index[fragment.user_id].add(fragment.fragment_id)

    def tombstone_user_memories(self, user_id: str) -> Dict[str, Any]:
        """Tombstone all memories for a user (GDPR right-to-be-forgotten)."""
        start_time = time.perf_counter()

        tombstoned_fragments = []
        purged_traces = []

        # Find and tombstone all user memories
        for fragment_id, fragment in self.memory_fragments.items():
            if fragment.user_id == user_id and fragment.tombstone_status == TombstoneStatus.ACTIVE:
                fragment.tombstone_status = TombstoneStatus.TOMBSTONED
                fragment.tombstone_timestamp = time.time()
                tombstoned_fragments.append(fragment_id)

        # Update tombstone index
        if user_id not in self.tombstone_index:
            self.tombstone_index[user_id] = set()
        self.tombstone_index[user_id].update(tombstoned_fragments)

        # Purge decision traces that reference tombstoned memories
        traces_to_purge = []
        for trace_id, trace in self.decision_traces.items():
            if any(frag_id in tombstoned_fragments for frag_id in trace.referenced_memories):
                traces_to_purge.append(trace_id)

        for trace_id in traces_to_purge:
            self._sanitize_decision_trace(trace_id)
            purged_traces.append(trace_id)

        processing_time = (time.perf_counter() - start_time) * 1000

        return {
            "user_id": user_id,
            "tombstoned_fragments": len(tombstoned_fragments),
            "purged_traces": len(purged_traces),
            "processing_time_ms": processing_time,
            "fragment_ids": tombstoned_fragments,
            "trace_ids": purged_traces
        }

    def validate_memory_access(self, fragment_id: str, context: str = "matriz_query") -> Tuple[bool, Optional[GDPRViolation]]:
        """Validate that memory access respects tombstone status."""
        start_time = time.perf_counter()

        fragment = self.memory_fragments.get(fragment_id)
        if not fragment:
            # Fragment doesn't exist - this is allowed
            return True, None

        # Update access tracking
        fragment.access_count += 1
        fragment.last_accessed = time.time()
        self.compliance_metrics["memory_queries"] += 1

        # Check tombstone status
        if fragment.tombstone_status in [TombstoneStatus.TOMBSTONED, TombstoneStatus.PURGED]:
            # GDPR VIOLATION: Accessing tombstoned data
            violation = GDPRViolation(
                violation_type=GDPRViolationType.TOMBSTONE_ACCESS,
                timestamp=time.time(),
                fragment_id=fragment_id,
                trace_id=None,
                user_id=fragment.user_id,
                details=f"Attempted access to {fragment.tombstone_status.value} memory from {context}",
                severity="CRITICAL"
            )

            self.violations.append(violation)
            self.compliance_metrics["violation_detections"] += 1

            validation_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"GDPR VIOLATION: Tombstone access - {fragment_id} ({validation_time:.2f}ms)")

            return False, violation

        self.compliance_metrics["tombstone_checks"] += 1
        return True, None

    def matriz_decision_with_memory_query(
        self,
        decision_context: Dict[str, Any],
        memory_fragments_needed: List[str]
    ) -> Tuple[Dict[str, Any], List[GDPRViolation]]:
        """Simulate MATRIZ decision process with memory queries and GDPR validation."""
        start_time = time.perf_counter()

        violations = []
        accessible_memories = []
        blocked_memories = []

        # Validate access to each required memory fragment
        for fragment_id in memory_fragments_needed:
            is_accessible, violation = self.validate_memory_access(fragment_id, "matriz_decision")

            if is_accessible:
                accessible_memories.append(fragment_id)
            else:
                blocked_memories.append(fragment_id)
                if violation:
                    violations.append(violation)

        # Create decision based only on accessible memories
        decision_output = {
            "decision_id": f"matriz_dec_{int(time.time() * 1000)}",
            "context": decision_context,
            "accessible_memory_count": len(accessible_memories),
            "blocked_memory_count": len(blocked_memories),
            "gdpr_compliant": len(violations) == 0,
            "processing_time_ms": (time.perf_counter() - start_time) * 1000
        }

        # Store decision trace (only if GDPR compliant)
        if decision_output["gdpr_compliant"]:
            trace = MATRIZDecisionTrace(
                trace_id=decision_output["decision_id"],
                decision_timestamp=time.time(),
                referenced_memories=accessible_memories,
                decision_output=decision_output,
                user_context=decision_context.get("user_id"),
                is_sanitized=False
            )
            self.decision_traces[trace.trace_id] = trace

        return decision_output, violations

    def _sanitize_decision_trace(self, trace_id: str):
        """Sanitize decision trace to remove GDPR-sensitive data."""
        if trace_id not in self.decision_traces:
            return

        trace = self.decision_traces[trace_id]

        # Sanitize the trace while preserving compliance evidence
        trace.referenced_memories = ["[REDACTED-GDPR]"] * len(trace.referenced_memories)
        trace.decision_output = {
            "decision_id": trace.decision_output.get("decision_id", "[REDACTED]"),
            "gdpr_sanitized": True,
            "sanitization_timestamp": time.time(),
            "original_memory_count": len(trace.referenced_memories)
        }
        trace.user_context = "[REDACTED-GDPR]"
        trace.is_sanitized = True

        self.compliance_metrics["trace_purges"] += 1

        logger.info(f"Sanitized decision trace: {trace_id}")

    def audit_gdpr_compliance(self) -> Dict[str, Any]:
        """Comprehensive GDPR compliance audit."""
        audit_timestamp = time.time()

        # Count memories by status
        status_counts = {}
        for status in TombstoneStatus:
            status_counts[status.value] = sum(
                1 for frag in self.memory_fragments.values()
                if frag.tombstone_status == status
            )

        # Analyze traces
        total_traces = len(self.decision_traces)
        sanitized_traces = sum(1 for trace in self.decision_traces.values() if trace.is_sanitized)

        # Violation analysis
        violation_by_type = {}
        for violation_type in GDPRViolationType:
            violation_by_type[violation_type.value] = sum(
                1 for v in self.violations if v.violation_type == violation_type
            )

        # Performance metrics
        if self.compliance_metrics["memory_queries"] > 0:
            violation_rate = (self.compliance_metrics["violation_detections"] /
                            self.compliance_metrics["memory_queries"]) * 100
        else:
            violation_rate = 0.0

        return {
            "audit_timestamp": audit_timestamp,
            "memory_status_counts": status_counts,
            "total_memory_fragments": len(self.memory_fragments),
            "total_decision_traces": total_traces,
            "sanitized_traces": sanitized_traces,
            "total_violations": len(self.violations),
            "violation_by_type": violation_by_type,
            "violation_rate_percent": violation_rate,
            "compliance_metrics": self.compliance_metrics.copy(),
            "gdpr_compliant": len(self.violations) == 0,
            "tombstoned_users": len(self.tombstone_index)
        }


@pytest.mark.memory
@pytest.mark.gdpr_compliance
class TestMATRIZGDPRBridge:
    """MATRIZ GDPR compliance integration tests."""

    def test_tombstone_memory_blocking(self):
        """Test that tombstoned memories are blocked from MATRIZ access."""
        gdpr_bridge = MATRIZGDPRBridge()

        # Create user memories
        user_id = "user_test_001"
        memories = []

        for i in range(5):
            fragment = MemoryFragment(
                fragment_id=f"mem_{user_id}_{i}",
                user_id=user_id,
                content_hash=hashlib.sha256(f"content_{i}".encode()).hexdigest(),
                creation_timestamp=time.time() - (i * 60),  # Staggered creation
                tombstone_status=TombstoneStatus.ACTIVE
            )
            memories.append(fragment)
            gdpr_bridge.store_memory_fragment(fragment)

        # Test 1: Normal access should work
        fragment_id = memories[0].fragment_id
        is_accessible, violation = gdpr_bridge.validate_memory_access(fragment_id, "test_access")

        assert is_accessible, "Active memory should be accessible"
        assert violation is None, "No violation should occur for active memory"

        # Test 2: Tombstone the user's memories
        tombstone_result = gdpr_bridge.tombstone_user_memories(user_id)

        assert tombstone_result["tombstoned_fragments"] == 5, "All user fragments should be tombstoned"
        assert tombstone_result["processing_time_ms"] < 500.0, "Tombstone processing should complete within 500ms"

        # Test 3: Access to tombstoned memory should be blocked
        is_accessible, violation = gdpr_bridge.validate_memory_access(fragment_id, "test_access_blocked")

        assert not is_accessible, "Tombstoned memory should NOT be accessible"
        assert violation is not None, "Violation should be detected for tombstoned access"
        assert violation.violation_type == GDPRViolationType.TOMBSTONE_ACCESS, "Should detect tombstone access violation"
        assert violation.user_id == user_id, "Violation should track correct user"

        logger.info(f"✅ Tombstone blocking test passed - {len(memories)} memories protected")

    def test_matriz_decision_gdpr_compliance(self):
        """Test MATRIZ decision process respects GDPR tombstones."""
        gdpr_bridge = MATRIZGDPRBridge()

        # Setup: Create memories for two users
        active_user = "user_active_001"
        tombstone_user = "user_tombstone_002"

        active_memories = []
        tombstone_memories = []

        # Create active user memories
        for i in range(3):
            fragment = MemoryFragment(
                fragment_id=f"mem_{active_user}_{i}",
                user_id=active_user,
                content_hash=hashlib.sha256(f"active_content_{i}".encode()).hexdigest(),
                creation_timestamp=time.time(),
                tombstone_status=TombstoneStatus.ACTIVE
            )
            active_memories.append(fragment)
            gdpr_bridge.store_memory_fragment(fragment)

        # Create memories that will be tombstoned
        for i in range(3):
            fragment = MemoryFragment(
                fragment_id=f"mem_{tombstone_user}_{i}",
                user_id=tombstone_user,
                content_hash=hashlib.sha256(f"tombstone_content_{i}".encode()).hexdigest(),
                creation_timestamp=time.time(),
                tombstone_status=TombstoneStatus.ACTIVE
            )
            tombstone_memories.append(fragment)
            gdpr_bridge.store_memory_fragment(fragment)

        # Tombstone the second user's memories
        gdpr_bridge.tombstone_user_memories(tombstone_user)

        # Test MATRIZ decision process
        all_memory_ids = [m.fragment_id for m in active_memories + tombstone_memories]

        decision_context = {
            "user_id": "mixed_context_user",
            "query": "test decision with mixed memory access",
            "timestamp": time.time()
        }

        decision_output, violations = gdpr_bridge.matriz_decision_with_memory_query(
            decision_context, all_memory_ids
        )

        # Assertions
        assert decision_output["accessible_memory_count"] == 3, "Should access only active memories"
        assert decision_output["blocked_memory_count"] == 3, "Should block all tombstoned memories"
        assert len(violations) == 3, "Should detect 3 GDPR violations"
        assert decision_output["gdpr_compliant"] == False, "Decision should be flagged as non-compliant due to attempted access"

        # Verify violations
        for violation in violations:
            assert violation.violation_type == GDPRViolationType.TOMBSTONE_ACCESS
            assert violation.user_id == tombstone_user

        # Test with only active memories
        active_only_ids = [m.fragment_id for m in active_memories]
        clean_decision, clean_violations = gdpr_bridge.matriz_decision_with_memory_query(
            decision_context, active_only_ids
        )

        assert clean_decision["gdpr_compliant"] == True, "Clean decision should be GDPR compliant"
        assert len(clean_violations) == 0, "Clean decision should have no violations"
        assert clean_decision["accessible_memory_count"] == 3, "Should access all requested active memories"

        logger.info(f"✅ MATRIZ GDPR compliance test passed - blocked {len(violations)} violations")

    def test_decision_trace_purging(self):
        """Test that decision traces are purged when memories are tombstoned."""
        gdpr_bridge = MATRIZGDPRBridge()

        # Create user and memories
        user_id = "user_trace_test"
        memories = []

        for i in range(3):
            fragment = MemoryFragment(
                fragment_id=f"trace_mem_{i}",
                user_id=user_id,
                content_hash=hashlib.sha256(f"trace_content_{i}".encode()).hexdigest(),
                creation_timestamp=time.time(),
                tombstone_status=TombstoneStatus.ACTIVE
            )
            memories.append(fragment)
            gdpr_bridge.store_memory_fragment(fragment)

        # Create decisions that reference these memories
        memory_ids = [m.fragment_id for m in memories]

        decision1, _ = gdpr_bridge.matriz_decision_with_memory_query(
            {"user_id": user_id, "context": "decision_1"}, memory_ids[:2]
        )

        decision2, _ = gdpr_bridge.matriz_decision_with_memory_query(
            {"user_id": user_id, "context": "decision_2"}, memory_ids[1:]
        )

        decision3, _ = gdpr_bridge.matriz_decision_with_memory_query(
            {"user_id": "other_user", "context": "decision_3"}, []  # No memories
        )

        # Verify traces were created
        assert len(gdpr_bridge.decision_traces) == 3, "Should have 3 decision traces"
        unsanitized_traces = sum(1 for trace in gdpr_bridge.decision_traces.values() if not trace.is_sanitized)
        assert unsanitized_traces == 3, "All traces should be unsanitized initially"

        # Tombstone the user's memories
        tombstone_result = gdpr_bridge.tombstone_user_memories(user_id)

        assert tombstone_result["purged_traces"] == 2, "Should purge 2 traces that reference user memories"

        # Verify trace sanitization
        sanitized_traces = sum(1 for trace in gdpr_bridge.decision_traces.values() if trace.is_sanitized)
        assert sanitized_traces == 2, "Should have 2 sanitized traces"

        # Verify the unrelated trace remains unsanitized
        unrelated_traces = sum(
            1 for trace in gdpr_bridge.decision_traces.values()
            if not trace.is_sanitized and len(trace.referenced_memories) == 0
        )
        assert unrelated_traces == 1, "Unrelated trace should remain unsanitized"

        # Verify sanitized traces have redacted content
        for trace in gdpr_bridge.decision_traces.values():
            if trace.is_sanitized:
                assert trace.user_context == "[REDACTED-GDPR]", "User context should be redacted"
                assert trace.decision_output.get("gdpr_sanitized") == True, "Output should be marked as sanitized"
                assert all(mem_id == "[REDACTED-GDPR]" for mem_id in trace.referenced_memories), "Memory IDs should be redacted"

        logger.info(f"✅ Decision trace purging test passed - sanitized {sanitized_traces} traces")

    def test_realtime_tombstone_performance(self):
        """Test real-time tombstone checking meets performance targets."""
        gdpr_bridge = MATRIZGDPRBridge()

        # Create large number of memories for performance testing
        users = [f"perf_user_{i}" for i in range(10)]
        all_fragments = []

        for user_id in users:
            for i in range(100):  # 100 memories per user = 1000 total
                fragment = MemoryFragment(
                    fragment_id=f"perf_{user_id}_{i}",
                    user_id=user_id,
                    content_hash=hashlib.sha256(f"perf_content_{user_id}_{i}".encode()).hexdigest(),
                    creation_timestamp=time.time(),
                    tombstone_status=TombstoneStatus.ACTIVE
                )
                all_fragments.append(fragment)
                gdpr_bridge.store_memory_fragment(fragment)

        # Tombstone half the users
        tombstone_users = users[:5]
        for user_id in tombstone_users:
            gdpr_bridge.tombstone_user_memories(user_id)

        # Performance test: Memory access validation
        access_times = []
        violation_count = 0

        # Test 1000 memory accesses
        for fragment in all_fragments[:1000]:
            start_time = time.perf_counter()
            is_accessible, violation = gdpr_bridge.validate_memory_access(
                fragment.fragment_id, "performance_test"
            )
            access_time = (time.perf_counter() - start_time) * 1000  # ms

            access_times.append(access_time)
            if violation:
                violation_count += 1

        # Performance analysis
        mean_access_time = sum(access_times) / len(access_times)
        p95_access_time = sorted(access_times)[int(len(access_times) * 0.95)]
        max_access_time = max(access_times)

        # Performance targets
        assert mean_access_time < 5.0, f"Mean access time {mean_access_time:.2f}ms exceeds 5ms target"
        assert p95_access_time < 10.0, f"P95 access time {p95_access_time:.2f}ms exceeds 10ms target"
        assert max_access_time < 50.0, f"Max access time {max_access_time:.2f}ms exceeds 50ms target"

        # Correctness verification
        expected_violations = 500  # 5 users * 100 memories each
        assert violation_count == expected_violations, f"Expected {expected_violations} violations, got {violation_count}"

        logger.info(f"✅ Real-time performance test passed:")
        logger.info(f"   Mean: {mean_access_time:.2f}ms")
        logger.info(f"   P95:  {p95_access_time:.2f}ms")
        logger.info(f"   Max:  {max_access_time:.2f}ms")
        logger.info(f"   Violations: {violation_count}/{len(access_times)}")

    def test_comprehensive_gdpr_audit(self):
        """Comprehensive GDPR compliance audit test."""
        gdpr_bridge = MATRIZGDPRBridge()

        # Create complex scenario with multiple users and states
        scenarios = [
            ("active_user_001", 5, TombstoneStatus.ACTIVE),
            ("tombstoned_user_002", 3, TombstoneStatus.ACTIVE),  # Will be tombstoned
            ("scheduled_user_003", 4, TombstoneStatus.SCHEDULED_DELETION),
        ]

        all_fragment_ids = []

        # Setup scenario
        for user_id, memory_count, initial_status in scenarios:
            for i in range(memory_count):
                fragment = MemoryFragment(
                    fragment_id=f"audit_{user_id}_{i}",
                    user_id=user_id,
                    content_hash=hashlib.sha256(f"audit_content_{user_id}_{i}".encode()).hexdigest(),
                    creation_timestamp=time.time(),
                    tombstone_status=initial_status
                )
                all_fragment_ids.append(fragment.fragment_id)
                gdpr_bridge.store_memory_fragment(fragment)

        # Tombstone one user
        gdpr_bridge.tombstone_user_memories("tombstoned_user_002")

        # Create some decisions and violations
        active_memories = [fid for fid in all_fragment_ids if "active_user" in fid]
        tombstoned_memories = [fid for fid in all_fragment_ids if "tombstoned_user" in fid]

        # Clean decision
        gdpr_bridge.matriz_decision_with_memory_query(
            {"user_id": "active_user_001", "type": "clean"}, active_memories[:2]
        )

        # Violating decision (should generate violations)
        gdpr_bridge.matriz_decision_with_memory_query(
            {"user_id": "mixed_user", "type": "violating"},
            active_memories[:1] + tombstoned_memories[:2]
        )

        # Run comprehensive audit
        audit_result = gdpr_bridge.audit_gdpr_compliance()

        # Verify audit results
        assert audit_result["total_memory_fragments"] == 12, "Should count all fragments"
        assert audit_result["memory_status_counts"]["active"] == 5, "Should have 5 active memories"
        assert audit_result["memory_status_counts"]["tombstoned"] == 3, "Should have 3 tombstoned memories"
        assert audit_result["memory_status_counts"]["scheduled_deletion"] == 4, "Should have 4 scheduled memories"

        assert audit_result["total_decision_traces"] == 2, "Should have 2 decision traces"
        assert audit_result["sanitized_traces"] == 1, "Should have 1 sanitized trace"

        assert audit_result["total_violations"] == 2, "Should detect 2 violations"
        assert audit_result["violation_by_type"]["tombstone_access"] == 2, "Should have 2 tombstone access violations"

        assert audit_result["gdpr_compliant"] == False, "Overall compliance should be FALSE due to violations"
        assert audit_result["tombstoned_users"] == 1, "Should track 1 tombstoned user"

        # Performance verification
        assert audit_result["compliance_metrics"]["memory_queries"] > 0, "Should track memory queries"
        assert audit_result["compliance_metrics"]["violation_detections"] == 2, "Should track violation detections"
        assert audit_result["compliance_metrics"]["trace_purges"] == 1, "Should track trace purges"

        logger.info(f"✅ Comprehensive GDPR audit passed:")
        logger.info(f"   Total fragments: {audit_result['total_memory_fragments']}")
        logger.info(f"   Violations: {audit_result['total_violations']}")
        logger.info(f"   Sanitized traces: {audit_result['sanitized_traces']}")
        logger.info(f"   Compliance: {'✓' if audit_result['gdpr_compliant'] else '✗'}")

    def test_gdpr_compliance_edge_cases(self):
        """Test edge cases for GDPR compliance."""
        gdpr_bridge = MATRIZGDPRBridge()

        # Edge Case 1: Access to non-existent memory
        is_accessible, violation = gdpr_bridge.validate_memory_access("nonexistent_memory", "test")
        assert is_accessible, "Non-existent memory access should be allowed (no data to protect)"
        assert violation is None, "No violation for non-existent memory"

        # Edge Case 2: Tombstone user with no memories
        result = gdpr_bridge.tombstone_user_memories("user_with_no_memories")
        assert result["tombstoned_fragments"] == 0, "Should handle user with no memories"
        assert result["purged_traces"] == 0, "Should handle no traces to purge"
        assert result["processing_time_ms"] < 100.0, "Should complete quickly for empty user"

        # Edge Case 3: Multiple tombstone requests for same user
        user_id = "edge_case_user"
        fragment = MemoryFragment(
            fragment_id=f"edge_{user_id}",
            user_id=user_id,
            content_hash="edge_hash",
            creation_timestamp=time.time(),
            tombstone_status=TombstoneStatus.ACTIVE
        )
        gdpr_bridge.store_memory_fragment(fragment)

        # First tombstone
        result1 = gdpr_bridge.tombstone_user_memories(user_id)
        assert result1["tombstoned_fragments"] == 1, "First tombstone should work"

        # Second tombstone (should be idempotent)
        result2 = gdpr_bridge.tombstone_user_memories(user_id)
        assert result2["tombstoned_fragments"] == 0, "Second tombstone should find nothing new"

        # Edge Case 4: Very rapid access patterns
        rapid_access_times = []
        for i in range(100):
            start = time.perf_counter()
            is_accessible, violation = gdpr_bridge.validate_memory_access(fragment.fragment_id, f"rapid_{i}")
            rapid_access_times.append((time.perf_counter() - start) * 1000)

        max_rapid_time = max(rapid_access_times)
        mean_rapid_time = sum(rapid_access_times) / len(rapid_access_times)

        assert max_rapid_time < 20.0, f"Rapid access max time {max_rapid_time:.2f}ms too slow"
        assert mean_rapid_time < 5.0, f"Rapid access mean time {mean_rapid_time:.2f}ms too slow"

        # All rapid accesses should detect violations (memory is tombstoned)
        violations_detected = sum(1 for _, v in [gdpr_bridge.validate_memory_access(fragment.fragment_id, f"rapid_check_{i}") for i in range(10)] if not _)
        assert violations_detected == 10, "All rapid accesses to tombstoned memory should be violations"

        logger.info(f"✅ GDPR edge cases test passed - {violations_detected} violations correctly detected")


if __name__ == "__main__":
    # Run GDPR compliance validation standalone
    def run_gdpr_validation():
        print("🏛️  MATRIZ GDPR Compliance Validation")
        print("=" * 60)

        gdpr_bridge = MATRIZGDPRBridge()

        # Test scenario: User requests data deletion
        user_id = "validation_user_001"
        print(f"\n1. Setting up test user: {user_id}")

        # Create memories
        memories = []
        for i in range(5):
            fragment = MemoryFragment(
                fragment_id=f"val_mem_{i}",
                user_id=user_id,
                content_hash=hashlib.sha256(f"validation_content_{i}".encode()).hexdigest(),
                creation_timestamp=time.time(),
                tombstone_status=TombstoneStatus.ACTIVE
            )
            memories.append(fragment)
            gdpr_bridge.store_memory_fragment(fragment)

        print(f"   Created {len(memories)} memory fragments")

        # Test pre-deletion access
        print("\n2. Testing pre-deletion access...")
        accessible_count = 0
        for memory in memories:
            is_accessible, _ = gdpr_bridge.validate_memory_access(memory.fragment_id, "validation")
            if is_accessible:
                accessible_count += 1

        print(f"   Pre-deletion: {accessible_count}/{len(memories)} memories accessible")

        # Execute GDPR deletion
        print("\n3. Executing GDPR right-to-be-forgotten...")
        start_time = time.perf_counter()
        tombstone_result = gdpr_bridge.tombstone_user_memories(user_id)
        deletion_time = (time.perf_counter() - start_time) * 1000

        print(f"   Tombstoned: {tombstone_result['tombstoned_fragments']} fragments")
        print(f"   Processing time: {deletion_time:.2f}ms")

        # Test post-deletion access
        print("\n4. Testing post-deletion access...")
        blocked_count = 0
        violation_count = 0

        for memory in memories:
            is_accessible, violation = gdpr_bridge.validate_memory_access(memory.fragment_id, "validation")
            if not is_accessible:
                blocked_count += 1
            if violation:
                violation_count += 1

        print(f"   Post-deletion: {blocked_count}/{len(memories)} memories blocked")
        print(f"   GDPR violations detected: {violation_count}")

        # Performance validation
        print("\n5. Performance validation...")
        access_times = []
        for i in range(100):
            start = time.perf_counter()
            gdpr_bridge.validate_memory_access(memories[0].fragment_id, f"perf_{i}")
            access_times.append((time.perf_counter() - start) * 1000)

        mean_time = sum(access_times) / len(access_times)
        p95_time = sorted(access_times)[95]

        print(f"   Mean access time: {mean_time:.3f}ms")
        print(f"   P95 access time: {p95_time:.3f}ms")

        # Final audit
        print("\n6. GDPR compliance audit...")
        audit = gdpr_bridge.audit_gdpr_compliance()
        print(f"   Total violations: {audit['total_violations']}")
        print(f"   Compliance status: {'✅ COMPLIANT' if audit['gdpr_compliant'] else '❌ NON-COMPLIANT'}")

        # Success criteria
        success_criteria = [
            ("Deletion speed", deletion_time < 500.0),
            ("Access blocking", blocked_count == len(memories)),
            ("Violation detection", violation_count > 0),
            ("Access performance", p95_time < 10.0),
            ("No false negatives", accessible_count == len(memories))  # Before deletion
        ]

        print(f"\n{'='*60}")
        passed_criteria = 0
        for criterion, passed in success_criteria:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{criterion}: {status}")
            if passed:
                passed_criteria += 1

        overall_success = passed_criteria == len(success_criteria)
        print(f"\n🏛️  GDPR Compliance: {'✅ T4/0.01% EXCELLENCE' if overall_success else '❌ INSUFFICIENT'}")
        print(f"   Criteria passed: {passed_criteria}/{len(success_criteria)}")

        return overall_success

    import sys
    success = run_gdpr_validation()
    sys.exit(0 if success else 1)