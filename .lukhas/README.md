---
status: wip
type: documentation
---
# LUKHAS System Directories

## .lukhas/
Personal configuration and user-specific settings for LUKHAS AI system.

## .lukhas_audit/
System audit logs and tool incident tracking:
- `audit.jsonl` - General audit trail
- `tool_incidents.jsonl` - Tool usage incidents and errors

## .lukhas_feedback/
User feedback and system learning:
- `feedback.jsonl` - User feedback logs
- `lut.json` - Lookup table for feedback processing

## .lukhas_perf/
Performance monitoring and metrics tracking.

These directories are actively used by the LUKHAS AI system and should not be deleted.
