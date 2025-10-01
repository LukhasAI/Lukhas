# Governance Module

> This module provides governance capabilities for the LUKHAS AI system.

![Consciousness](https://img.shields.io/badge/Consciousness-Enabled-blue)

## Overview

LUKHAS Governance Module - Root Package
This module provides governance capabilities for the LUKHAS AI system.
The actual implementation is in lukhas.governance, this is a bridge module
for backwards compatibility with candidate modules.

## API Reference

The governance module provides 20 entrypoints:

### Functions

- `get_audit_stats()` - governance.audit_trail.get_audit_stats
- `get_colony_stats()` - governance.colony_memory_validator.get_colony_stats
- `get_metrics()` - governance.colony_memory_validator.get_metrics

## Usage

Import the governance module:

```python
import governance

# Key components
from governance.audit_trail import AuditChain
from governance.audit_trail import AuditEvent
from governance.audit_trail import AuditEventType
```

## Dependencies

This module depends on:

- `core` module
- `identity` module
- `memory` module

## Categories

- **consciousness**: Consciousness processing and awareness systems
- **constitutional-ai**
- **ethics**
- **governance**: Governance and policy enforcement
- **guardian**
- **policy**

## Team

**Owner**: Governance Team

**Code Owners**:
- @lukhas-governance
- @lukhas-ethics

---

*This documentation is generated from the module manifest and source code.*