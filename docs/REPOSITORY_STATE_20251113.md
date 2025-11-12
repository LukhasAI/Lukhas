# Repository State as of 2025-11-13

## Project Overview
- **Name**: lukhas-ai
- **Version**: 1.0.0
- **Python Version**: >=3.9

## Module Inventory

| Module | Version | Assigned Lane | Dependencies |
|---|---|---|---|
| `lukhas.adapters` | N/A | LUKHAS |   |
| `lukhas.adapters.dast_adapter` | N/A | LUKHAS | `__future__, collections, dataclasses, typing, typing_extensions` |
| `lukhas.adapters.openai` | N/A | LUKHAS |   |
| `lukhas.adapters.openai.api` | N/A | LUKHAS | `__future__, serve, typing` |
| `lukhas.analytics` | N/A | LUKHAS | `lukhas` |
| `lukhas.analytics.privacy_client` | N/A | LUKHAS | `dataclasses, datetime, enum, hashlib, random, re, time, typing` |
| `lukhas.api` | N/A | LUKHAS |   |
| `lukhas.api.analytics` | N/A | LUKHAS | `logging, pydantic, typing` |
| `lukhas.api.auth` | N/A | LUKHAS | `datetime, jwt, passlib` |
| `lukhas.api.auth_helpers` | N/A | LUKHAS | `fastapi, functools, lukhas, os, time` |
| `lukhas.api.auth_routes` | N/A | LUKHAS | `fastapi, lukhas, pydantic` |
| `lukhas.api.features` | N/A | LUKHAS | `fastapi, logging, lukhas, pydantic, typing` |
| `lukhas.cli` | N/A | LUKHAS |   |
| `lukhas.cli.guided` | N/A | LUKHAS | `__future__, argparse, pathlib, rich, subprocess, sys, time, typing` |
| `lukhas.cli.troubleshoot` | N/A | LUKHAS | `__future__, pathlib, rich, shutil, socket, subprocess, sys, typing` |
| `lukhas.consciousness` | N/A | LUKHAS | `labs, logging, os, typing` |
| `lukhas.dream` | N/A | LUKHAS | `asyncio, collections, labs, logging, os, time, typing, uuid` |
| `lukhas.features` | N/A | LUKHAS | `lukhas` |
| `lukhas.features.flags_service` | N/A | LUKHAS | `datetime, enum, hashlib, logging, os, pathlib, time, typing, yaml` |
| `lukhas.features.testing` | N/A | LUKHAS | `collections, contextlib, lukhas, pathlib, pytest, tempfile, typing, yaml` |
| `lukhas.glyphs` | N/A | LUKHAS | `asyncio, candidate, labs, logging, os, time, typing` |
| `lukhas.governance` | N/A | LUKHAS |   |
| `lukhas.governance.audit` | N/A | LUKHAS | `lukhas` |
| `lukhas.governance.audit.config` | N/A | LUKHAS | `dataclasses, pathlib, typing` |
| `lukhas.governance.audit.events` | N/A | LUKHAS | `dataclasses, enum, json, time, typing, uuid` |
| `lukhas.governance.audit.logger` | N/A | LUKHAS | `lukhas, time, typing` |
| `lukhas.governance.audit.storage` | N/A | LUKHAS | `abc, collections, json, logging, lukhas, os, threading, time, typing` |
| `lukhas.governance.auth` | N/A | LUKHAS | `dependencies` |
| `lukhas.governance.auth.dependencies` | N/A | LUKHAS | `fastapi, logging, typing` |
| `lukhas.governance.gdpr` | N/A | LUKHAS | `lukhas` |
| `lukhas.governance.gdpr.config` | N/A | LUKHAS | `dataclasses` |
| `lukhas.governance.gdpr.routes` | N/A | LUKHAS | `fastapi, lukhas, pydantic, typing` |
| `lukhas.governance.gdpr.service` | N/A | LUKHAS | `dataclasses, json, lukhas, time, typing, uuid` |
| `lukhas.governance.rate_limit` | N/A | LUKHAS | `config, middleware, storage` |
| `lukhas.governance.rate_limit.config` | N/A | LUKHAS | `dataclasses, typing` |
| `lukhas.governance.rate_limit.middleware` | N/A | LUKHAS | `config, fastapi, logging, starlette, storage, time, typing` |
| `lukhas.governance.rate_limit.storage` | N/A | LUKHAS | `abc, collections, dataclasses, threading, time` |
| `lukhas.identity` | N/A | LUKHAS | `_bridgeutils, importlib, lukhas` |
| `lukhas.identity.token_types` | N/A | LUKHAS | `__future__, datetime, time, typing, typing_extensions` |
| `lukhas.identity.webauthn_credential` | N/A | LUKHAS | `__future__, threading, typing, typing_extensions` |
| `lukhas.identity.webauthn_verify` | N/A | LUKHAS | `__future__, base64, cryptography, hashlib, hmac, json, lukhas, struct, typing, typing_extensions` |
| `lukhas.memory` | N/A | LUKHAS |   |
| `lukhas.memory.index` | N/A | LUKHAS | `collections, numpy, typing` |
| `lukhas.memory.prometheus_metrics` | N/A | LUKHAS | `__future__, logging, lukhas` |
| `lukhas.observability` | N/A | LUKHAS |   |
| `lukhas.observability.custom_metrics` | N/A | Unknown |   |
| `lukhas.observability.distributed_tracing` | N/A | LUKHAS | `__future__, asyncio, functools, opentelemetry, typing` |
| `lukhas.observability.lane_metrics` | N/A | Unknown |   |
| `lukhas.observability.log_aggregation` | N/A | LUKHAS | `logging, logging_loki, lukhas, os, structlog, sys, unittest` |
| `lukhas.observability.otel_config` | N/A | LUKHAS | `fastapi, logging, lukhas, opentelemetry, typing` |
| `lukhas.observability.prometheus_config` | N/A | Unknown |   |
| `lukhas.observability.slo_monitoring` | N/A | LUKHAS | `lukhas, unittest` |
| `lukhas.orchestrator` | N/A | LUKHAS | `lukhas` |
| `lukhas.orchestrator.cancellation` | N/A | LUKHAS | `asyncio, datetime, logging, typing` |
| `lukhas.orchestrator.config` | N/A | LUKHAS | `dataclasses` |
| `lukhas.orchestrator.exceptions` | N/A | LUKHAS | `typing` |
| `lukhas.orchestrator.executor` | N/A | LUKHAS | `asyncio, logging, lukhas, typing` |
| `lukhas.orchestrator.health` | N/A | LUKHAS | `asyncio, lukhas, sys, typing, unittest` |
| `lukhas.orchestrator.interfaces` | N/A | LUKHAS | `typing` |
| `lukhas.orchestrator.pipeline` | N/A | LUKHAS | `asyncio, logging, lukhas, typing` |