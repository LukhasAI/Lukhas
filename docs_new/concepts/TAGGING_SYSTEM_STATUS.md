---
title: Tagging System Status
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["consciousness", "api", "architecture", "testing", "security"]
facets:
  layer: ["gateway"]
  domain: ["symbolic", "consciousness", "memory"]
  audience: ["dev"]
---

# LUKHAS Tagging System Status

## Overview

The tagging system is **referenced but not actively implemented** in the current codebase. While test files and some references exist, there's no operational tagging module.

## Current State

### References Found

1. **Test File**: `ARCHIVE_NON_PRODUCTION/tests/test_tagging_system.py`
   - Contains basic tests for `SimpleTagResolver` and `DeduplicationCache`
   - Imports from a `tagging` module that doesn't exist in production

2. **Audit Trail Integration**: `core/audit/audit_trail.py`
   - Events can have tags (Set[str])
   - Used for categorizing audit events
   - Example: `tags={"emergence", "consciousness", "milestone"}`

3. **Memory System References**
   - Some memory operations mention tags
   - Commercial API examples show tag usage

### Missing Components

1. **No Core Tagging Module**
   - No `tagging.py` or `tagging/` directory in production
   - The imported `SimpleTagResolver` doesn't exist

2. **No Tag Management System**
   - No tag creation/deletion endpoints
   - No tag hierarchy or relationships
   - No tag validation or normalization

## How Tagging Works Currently

### In Audit Trail
```python
await audit.log_event(
    event_type=AuditEventType.CONSCIOUSNESS_EMERGENCE,
    actor="consciousness_engine",
    details={...},
    tags={"emergence", "consciousness", "milestone"}
)
```

### In Memory Services (Commercial API)
```python
memory = MemoryStore(
    content="Important meeting notes",
    type="text",
    tags=["meeting", "important"],
    importance=0.9
)
```

## Proposed Tagging System Architecture

### Option 1: Implement Full Tagging System
```python
# core/tagging/tag_system.py
class TagSystem:
    def __init__(self):
        self.tag_registry = {}
        self.tag_hierarchies = {}

    def create_tag(self, tag: str, category: str = None):
        """Create and register a new tag"""

    def normalize_tag(self, tag: str) -> str:
        """Normalize tag format"""

    def get_related_tags(self, tag: str) -> List[str]:
        """Get semantically related tags"""
```

### Option 2: Simple Tag Utilities
```python
# core/utils/tags.py
def normalize_tags(tags: List[str]) -> Set[str]:
    """Normalize and deduplicate tags"""
    return {tag.lower().strip() for tag in tags}

def validate_tag(tag: str) -> bool:
    """Validate tag format"""
    return bool(re.match(r'^[a-z0-9_-]+$', tag))
```

### Option 3: Leverage Existing Systems
- Use audit trail tags for all tagging needs
- Store tags as metadata in respective systems
- No centralized tagging system

## Integration with Enterprise Systems

### With Audit Trail
Already integrated - events can be tagged for categorization and search.

### With Memory System
Tags can be stored as memory metadata for retrieval and filtering.

### With Learning System
Tags could categorize knowledge domains and learning progress.

## Recommendations

### For Immediate Use
1. **Document current tag usage** in audit trail and memory systems
2. **Create tag conventions** document for consistency
3. **Use existing tag support** in audit trail for categorization

### For Future Enhancement
1. **Implement tag utilities** for normalization and validation
2. **Create tag search** functionality in audit queries
3. **Add tag-based filtering** to memory and dream systems

### Example Tag Conventions
```
# System tags
system:startup
system:shutdown
system:error

# Consciousness tags
consciousness:emergence
consciousness:state_change
consciousness:coherence_high

# Learning tags
learning:goal_set
learning:milestone
learning:knowledge_acquired

# Security tags
security:access_granted
security:threat_detected
security:audit_required
```

## Decision Required

1. **Keep as-is** - Use existing tag support in audit/memory
2. **Add utilities** - Create basic tag normalization/validation
3. **Full implementation** - Build complete tagging system
4. **Remove references** - Clean up test files and unused imports

The current audit trail and memory systems already support basic tagging, which may be sufficient for enterprise needs.
