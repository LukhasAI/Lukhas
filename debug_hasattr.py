#!/usr/bin/env python3

from candidate.governance.security.audit_system import AuditEvent

print("🔍 Testing hasattr on AuditEvent fields:")
print(f"hasattr(AuditEvent, 'compliance_relevant'): {hasattr(AuditEvent, 'compliance_relevant')}")
print(f"hasattr(AuditEvent, 'compliance_frameworks'): {hasattr(AuditEvent, 'compliance_frameworks')}")
print(f"hasattr(AuditEvent, 'event_id'): {hasattr(AuditEvent, 'event_id')}")
print(f"hasattr(AuditEvent, 'message'): {hasattr(AuditEvent, 'message')}")

# Check AuditEvent annotations
print(f"\n🔍 AuditEvent annotations:")
for field, annotation in AuditEvent.__annotations__.items():
    print(f"  {field}: {annotation}")
