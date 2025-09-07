#!/usr/bin/env python3

import asyncio
import tempfile
from datetime import datetime, timedelta

from candidate.governance.security.audit_system import AuditEventType, AuditQuery, ComprehensiveAuditSystem


async def debug_compliance_reporting():
    """Debug compliance reporting issue"""

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🔍 Using temp directory: {temp_dir}")

        audit_system = ComprehensiveAuditSystem(temp_dir)

        # Log compliance-relevant events
        print("\n1️⃣ Logging compliance events...")

        event1_id = await audit_system.log_event(
            event_type=AuditEventType.CONSENT_GRANTED,
            message="User granted consent",
            user_id="test_user",
            compliance_relevant=True,
            compliance_frameworks={"gdpr"},
        )
        print(f"   📝 Logged consent event: {event1_id}")

        event2_id = await audit_system.log_event(
            event_type=AuditEventType.DATA_READ,
            message="User data accessed",
            user_id="test_user",
            compliance_relevant=True,
            compliance_frameworks={"gdpr"},
        )
        print(f"   📝 Logged data read event: {event2_id}")

        # Check buffer
        print(f"\n2️⃣ Events in buffer: {len(audit_system.event_buffer)}")
        for i, event in enumerate(audit_system.event_buffer):
            print(
                f"   📄 Event {i}: {event.event_type.value}, compliance: {event.compliance_relevant}, frameworks: {event.compliance_frameworks}"
            )

        # Test query without flushing (should find buffer events)
        print("\n3️⃣ Testing query (buffer only)...")
        query = AuditQuery(
            start_time=datetime.now(timezone.utc) - timedelta(hours=1),
            end_time=datetime.now(timezone.utc) + timedelta(hours=1),
            compliance_relevant_only=True,
            compliance_frameworks={"gdpr"},
            limit=100,
        )

        events = await audit_system.query_events(query)
        print(f"   📊 Found {len(events)} events via query_events")
        for event in events:
            print(f"      - {event.event_type.value}: {event.message}")

        # Generate compliance report
        print("\n4️⃣ Generating compliance report...")
        start_date = datetime.now(timezone.utc) - timedelta(hours=1)
        end_date = datetime.now(timezone.utc)

        report = await audit_system.generate_compliance_report(
            framework="gdpr", start_date=start_date, end_date=end_date
        )

        print(f"   📋 Report: {report['framework']}")
        print(f"   📊 Total events: {report['summary']['total_events']}")
        print(f"   📈 Events by type: {report['summary']}")

        # Test with flush
        print("\n5️⃣ Testing after buffer flush...")
        await audit_system._flush_buffer()
        print(f"   Events in buffer after flush: {len(audit_system.event_buffer)}")

        events_after_flush = await audit_system.query_events(query)
        print(f"   📊 Found {len(events_after_flush)} events via query_events after flush")

        report_after_flush = await audit_system.generate_compliance_report(
            framework="gdpr", start_date=start_date, end_date=end_date
        )
        print(f"   📊 Total events after flush: {report_after_flush['summary']['total_events']}")


if __name__ == "__main__":
    asyncio.run(debug_compliance_reporting())
