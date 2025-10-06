---
status: wip
type: documentation
---
# Schemas Module Context - Vendor-Neutral AI Guidance
*This file provides domain-specific context for any AI development tool*
*Also available as claude.me for Claude Desktop compatibility*


**Module**: schemas
**Purpose**: JSON schemas, validation schemas, and data specifications
**Lane**: L2 (Integration)
**Language**: JSON Schema
**Last Updated**: 2025-10-02

---

## Module Overview

The schemas module provides comprehensive JSON schemas and validation specifications for LUKHAS AI systems, ensuring data integrity, type safety, and API contract compliance across all modules.

### Key Components
- **JSON Schemas**: JSON Schema definitions
- **Validation Schemas**: Data validation specifications
- **API Schemas**: API request/response schemas
- **Module Schemas**: Module manifest schemas

---

## Module Structure

```
schemas/
├── module.manifest.json         # Schemas manifest (schema v1.0.0)
├── module.manifest.lock.json    # Locked manifest
├── README.md                    # Schemas overview
├── module.manifest.schema.json  # Module manifest schema
├── directory_index.schema.json  # Directory index schema
├── (additional schema files)
├── config/                      # Schema configuration
├── docs/                        # Schema documentation
├── schema/                      # Meta-schemas
└── tests/                       # Schema validation tests
```

---

## Development Guidelines

### 1. Using Schemas

```python
import jsonschema
import json

# Load schema
with open('schemas/module.manifest.schema.json') as f:
    schema = json.load(f)

# Validate data
data = {...}
jsonschema.validate(instance=data, schema=schema)
```

---

## Related Modules

- **Contracts** ([../contracts/](../contracts/)) - API contracts
- **Models** ([../models/](../models/)) - Data models
- **Data** ([../data/](../data/)) - Data processing

---

**Status**: Integration Lane (L2)
**Team**: Core
**Last Updated**: 2025-10-02
