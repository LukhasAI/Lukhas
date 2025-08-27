#!/usr/bin/env python3

import asyncio
import tempfile

from candidate.governance.security.audit_system import (
    AuditEvent,
    AuditEventType,
    ComprehensiveAuditSystem,
)


async def debug_kwargs_issue():
    """Debug kwargs handling in log_event"""

    with tempfile.TemporaryDirectory() as temp_dir:
        audit_system = ComprehensiveAuditSystem(temp_dir)

        print("🔍 Testing AuditEvent creation directly...")

        # Test 1: Create AuditEvent directly
        direct_event = AuditEvent(
            event_id="test_direct",
            timestamp=datetime.now(),
            event_type=AuditEventType.DATA_READ,
            category=AuditCategory.SYSTEM_EVENT,
            level=AuditLevel.INFO,
            message="Direct event",
            compliance_relevant=True,
            compliance_frameworks={"gdpr"},
        )
        print(f"   ✅ Direct: compliance_frameworks = {direct_event.compliance_frameworks}")

        # Test 2: Check hasattr
        print(f"   🔍 hasattr(AuditEvent, 'compliance_frameworks'): {hasattr(AuditEvent, 'compliance_frameworks')}")
        print(f"   🔍 hasattr(AuditEvent, 'compliance_relevant'): {hasattr(AuditEvent, 'compliance_relevant')}")

        # Test 3: Simulate the kwargs filtering
        kwargs = {
            "compliance_relevant": True,
            "compliance_frameworks": {"gdpr"},
            "invalid_field": "should_be_filtered"
        }

        filtered_kwargs = {k: v for k, v in kwargs.items() if hasattr(AuditEvent, k)}
        print(f"   🔍 Original kwargs: {kwargs}")
        print(f"   🔍 Filtered kwargs: {filtered_kwargs}")

        # Test 4: Test via log_event
        print("\n🔍 Testing via log_event method...")

        event_id = await audit_system.log_event(
            event_type=AuditEventType.DATA_READ,
            message="Test event via log_event",
            compliance_relevant=True,
            compliance_frameworks={"gdpr"},
        )

        # Get the event from buffer
        buffer_event = audit_system.event_buffer[-1]
        print(f"   📄 Buffer event: compliance_frameworks = {buffer_event.compliance_frameworks}")
        print(f"   📄 Buffer event: compliance_relevant = {buffer_event.compliance_relevant}")


if __name__ == "__main__":
    asyncio.run(debug_kwargs_issue())
