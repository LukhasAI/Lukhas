# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

# Schemas Module - Claude AI Context

**Module**: schemas
**Purpose**: JSON schemas, validation schemas, and data specifications
**Lane**: L2 (Integration)
**Language**: JSON Schema
**Last Updated**: 2025-10-18

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
**Last Updated**: 2025-10-18


## 🚀 GA Deployment Status

**Current Status**: 66.7% Ready (6/9 tasks complete)

### Recent Milestones
- ✅ **RC Soak Testing**: 60-hour stability validation (99.985% success rate)
- ✅ **Dependency Audit**: 196 packages, 0 CVEs
- ✅ **OpenAI Façade**: Full SDK compatibility validated
- ✅ **Guardian MCP**: Production-ready deployment
- ✅ **OpenAPI Schema**: Validated and documented

### New Documentation
- docs/GA_DEPLOYMENT_RUNBOOK.md - Comprehensive GA deployment procedures
- docs/DEPENDENCY_AUDIT.md - 196 packages, 0 CVEs, 100% license compliance
- docs/RC_SOAK_TEST_RESULTS.md - 60-hour stability validation (99.985% success)

### Recent Updates
- E402 linting cleanup - 86/1,226 violations fixed (batches 1-8)
- OpenAI façade validation - Full SDK compatibility
- Guardian MCP server deployment - Production ready
- Shadow diff harness - Pre-audit validation framework
- MATRIZ evaluation harness - Comprehensive testing

**Reference**: See [GA_DEPLOYMENT_RUNBOOK.md](./docs/GA_DEPLOYMENT_RUNBOOK.md) for deployment procedures.

---
