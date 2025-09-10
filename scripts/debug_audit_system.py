#!/usr/bin/env python3

import asyncio
import tempfile
from datetime import datetime, timedelta, timezone

from candidate.governance.security.audit_system import AuditEventType, AuditQuery, ComprehensiveAuditSystem


async def debug_audit_system():
    """Debug audit system event storage and retrieval"""

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🔍 Using temp directory: {temp_dir}")

        audit_system = ComprehensiveAuditSystem(temp_dir)

        # Log test events
        print("\n1️⃣ Logging test events...")
        event_ids = []
        for i in range(3):
            event_id = await audit_system.log_event(
                event_type=AuditEventType.DATA_READ,
                message=f"Test event {i}",
                user_id="test_user",
            )
            event_ids.append(event_id)
            print(f"   📝 Logged event {i}: {event_id}")

        # Check buffer before flush
        print(f"\n2️⃣ Events in buffer BEFORE flush: {len(audit_system.event_buffer)}")

        # Flush buffer
        print("\n3️⃣ Flushing buffer...")
        await audit_system._flush_buffer()

        # Check buffer after flush
        print(f"4️⃣ Events in buffer AFTER flush: {len(audit_system.event_buffer)}")

        # Verify integrity
        print("\n5️⃣ Verifying audit integrity...")
        integrity_result = await audit_system.verify_audit_integrity()
        print(f"   ✅ Integrity result: {integrity_result}")

        # Query events
        print("\n6️⃣ Querying stored events...")
        query = AuditQuery(
            start_time=datetime.now(timezone.utc) - timedelta(hours=1),
            end_time=datetime.now(timezone.utc) + timedelta(hours=1),
            limit=100,
        )
        events = await audit_system.query_events(query)
        print(f"   📊 Found {len(events)} events via query_events")

        # Check storage directly
        print("\n7️⃣ Checking storage directly...")
        storage_events = await audit_system.storage.query_events(query)
        print(f"   💾 Found {len(storage_events)} events in storage")

        print(f"\n📁 Storage base path: {audit_system.storage.base_path}")
        import os

        if os.path.exists(audit_system.storage.base_path):
            print("📂 Directory contents:")
            for item in os.listdir(audit_system.storage.base_path):
                item_path = os.path.join(audit_system.storage.base_path, item)
                if os.path.isdir(item_path):
                    print(f"   📁 {item}/")
                    for subitem in os.listdir(item_path):
                        print(f"      📄 {subitem}")
                else:
                    print(f"   📄 {item}")


if __name__ == "__main__":
    asyncio.run(debug_audit_system())
