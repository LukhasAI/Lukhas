# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

# mcp-lukhas-sse Module

**LUKHAS mcp-lukhas-sse module implementing specialized mcp-lukhas-sse functionality with 40 components for integrated system operations.**

**Lane**: L2
**Schema**: 3.0.0
**Entrypoints**: 11
**Dependencies**: identity

## Quick Reference

```python
# Import from mcp-lukhas-sse
from mcp-lukhas-sse.chatgpt_server import FlexibleAuthMiddleware
from mcp-lukhas-sse.chatgpt_server import list_directory_tool
from mcp-lukhas-sse.chatgpt_server import read_file_tool
from mcp-lukhas-sse.generate_test_jwt import create_test_jwks
from mcp-lukhas-sse.generate_test_jwt import generate_test_jwt
```

## Components (11 entrypoints)

- `mcp-lukhas-sse.chatgpt_server.FlexibleAuthMiddleware`
- `mcp-lukhas-sse.chatgpt_server.list_directory_tool`
- `mcp-lukhas-sse.chatgpt_server.read_file_tool`
- `mcp-lukhas-sse.generate_test_jwt.create_test_jwks`
- `mcp-lukhas-sse.generate_test_jwt.generate_test_jwt`
- `mcp-lukhas-sse.lukhas_mcp_stdio_manual.LukhasMCPServer`
- `mcp-lukhas-sse.mcp_official_server.MCPServer`
- `mcp-lukhas-sse.minimal_server.OAuth2Middleware`
- `mcp-lukhas-sse.minimal_server.list_directory_tool`
- `mcp-lukhas-sse.minimal_server.read_file_tool`
- `mcp-lukhas-sse.pure_mcp_server.validate_path_security`

## Module Metadata

- **Lane**: L2
- **Schema Version**: 3.0.0
- **Tags**: authentication, mcp-lukhas-sse
- **Dependencies**: identity
- **OpenTelemetry**: 1.37.0

## Related Systems

- **identity**: Dependency integration

---

**Documentation Status**: ✅ Complete
**Last Updated**: 2025-10-18
**Maintainer**: LUKHAS Core Team


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
