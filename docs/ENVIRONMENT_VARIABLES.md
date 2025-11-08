# LUKHAS Environment Variables Reference

**Generated:** 2025-11-06
**Total Variables:** 73
**Source:** Audit scan of Python codebase

This document catalogs all environment variables detected in the LUKHAS codebase, organized by category.

## 🔐 Security & Authentication (10 vars)

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `LUKHAS_ID_SECRET` | Secret key for ΛiD identity system | Yes | - | `your-secret-key-here` |
| `LUKHAS_MASTER_KEY` | Master encryption key for sensitive data | Yes | - | `32-byte-hex-string` |
| `GITHUB_TOKEN` | GitHub API token for integrations | No | - | `ghp_xxxxx` |
| `OPENAI_API_KEY` | OpenAI API key for AI operations | No | - | `sk-xxxxx` |
| `OAUTH_ISSUER` | OAuth issuer URL | No | - | `https://auth.example.com` |
| `OAUTH_AUDIENCE` | OAuth audience identifier | No | - | `lukhas-api` |
| `LUKHAS_CREDENTIALS_PATH` | Path to credentials storage | No | `~/.lukhas/credentials` | `/secure/path` |
| `ALLOW_NO_AUTH` | Allow operations without authentication (dev only) | No | `false` | `true` |
| `ALLOWED_ROOTS` | Allowed root paths for file operations | No | - | `/app,/data` |
| `DATABASE_URL` | Database connection string | No | - | `postgresql://...` |

## 🛡️ Guardian & Ethics (9 vars)

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `GUARDIAN_ETHICS_LEVEL` | Ethics enforcement level (0-3) | No | `2` | `3` |
| `GUARDIAN_TIMEOUT` | Guardian decision timeout (ms) | No | `5000` | `10000` |
| `GUARDIAN_CACHE_TTL` | Guardian cache TTL (seconds) | No | `300` | `600` |
| `GUARDIAN_CONSENSUS_REQUIRED` | Require consensus for decisions | No | `false` | `true` |
| `GUARDIAN_EMERGENCY_DISABLE_PATH` | Emergency disable file path | No | - | `/tmp/guardian_disable` |
| `ENFORCE_ETHICS_DSL` | Enforce Ethics DSL validation | No | `true` | `false` |
| `ETHICS_ENFORCEMENT_LEVEL` | Global ethics enforcement level | No | `standard` | `strict` |
| `DRIFT_THRESHOLD` | Ethical drift detection threshold | No | `0.1` | `0.05` |
| `LUKHAS_GUARDIAN_ENFORCED_LANES` | Lanes requiring Guardian approval | No | `production` | `production,integration` |

## 🎯 Performance & Limits (9 vars)

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `AUTH_P95_TARGET_MS` | P95 latency target for auth (ms) | No | `250` | `200` |
| `CONTEXT_P95_TARGET_MS` | P95 latency target for context (ms) | No | `250` | `200` |
| `API_RATE_LIMIT` | API rate limit (requests/window) | No | `100` | `1000` |
| `LUKHAS_RATE_LIMIT_REQUESTS` | Rate limit requests per window | No | `60` | `120` |
| `LUKHAS_RATE_LIMIT_WINDOW` | Rate limit window (seconds) | No | `60` | `30` |
| `LUKHAS_REQUEST_TIMEOUT` | Request timeout (seconds) | No | `30` | `60` |
| `LUKHAS_MAX_CONTENT_SIZE` | Max content size (bytes) | No | `10485760` | `52428800` |
| `MEMORY_FOLD_LIMIT` | Memory fold limit for consolidation | No | `100` | `200` |
| `LUKHAS_CANARY_PERCENT` | Canary deployment percentage | No | `10` | `25` |

## 🏗️ System Configuration (14 vars)

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `LUKHAS_ENV` | Environment (dev/staging/production) | Yes | `dev` | `production` |
| `LUKHAS_LANE` | Active lane (candidate/core/lukhas) | No | `candidate` | `lukhas` |
| `LUKHAS_ROOT` | LUKHAS installation root path | No | Auto-detected | `/opt/lukhas` |
| `LUKHAS_PYTHON_PATH` | Python path for imports | No | Auto | `/opt/lukhas` |
| `LUKHAS_ENV_EXAMPLE_PATH` | Path to .env.example | No | `.env.example` | `/config/.env.example` |
| `HOST` | Server host address | No | `0.0.0.0` | `127.0.0.1` |
| `LOG_LEVEL` | Logging level | No | `INFO` | `DEBUG` |
| `LUKHAS_LOG_LEVEL` | LUKHAS-specific log level | No | `INFO` | `DEBUG` |
| `LUKHAS_DEBUG` | Enable debug mode | No | `false` | `true` |
| `LUKHAS_EXPERIMENTAL` | Enable experimental features | No | `false` | `true` |
| `BUS_SCHEMA_VERSION` | Event bus schema version | No | `1.0` | `2.0` |
| `MATRIZ_COMPAT_IMPORTS` | Enable MATRIZ compatibility imports | No | `false` | `true` |
| `LUKHAS_MCP_ROOTS` | MCP server root paths | No | - | `/mcp1,/mcp2` |
| `LUKHAS_ADVANCED_TAGS` | Enable advanced tagging | No | `false` | `true` |

## 🧠 Feature Flags (6 vars)

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `LUKHAS_ENABLE_BROWSER` | Enable browser automation | No | `false` | `true` |
| `LUKHAS_ENABLE_CODE_EXEC` | Enable code execution | No | `false` | `true` |
| `LUKHAS_ENABLE_RETRIEVAL` | Enable retrieval capabilities | No | `true` | `false` |
| `LUKHAS_ENABLE_SCHEDULER` | Enable scheduler | No | `true` | `false` |
| `DREAM_SIMULATION_ENABLED` | Enable dream simulation | No | `false` | `true` |
| `PLAN_ETHICS_ENABLED` | Enable ethics in planning | No | `true` | `false` |

## 🎛️ Planning & Execution (3 vars)

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `PLAN_ALLOWED_DOMAINS` | Allowed domains for planning | No | - | `*.example.com` |
| `PLAN_GUARDIAN_ENABLED` | Enable Guardian in planning | No | `true` | `false` |
| `PLAN_ETHICS_ENABLED` | Enable ethics validation in planning | No | `true` | `false` |

## 📊 Uncategorized (22 vars)

These variables are used in the codebase but need further categorization or documentation:

- `ALLOWED_ROOTS`
- `ALLOW_NO_AUTH`
- `API_RATE_LIMIT`
- `AUTH_P95_TARGET_MS`
- `BUS_SCHEMA_VERSION`
- `CONTEXT_P95_TARGET_MS`
- `DATABASE_URL`
- `DREAM_SIMULATION_ENABLED`
- `DRIFT_THRESHOLD`
- `ENFORCE_ETHICS_DSL`
- `ETHICS_ENFORCEMENT_LEVEL`
- `GITHUB_TOKEN`
- `GUARDIAN_CACHE_TTL`
- `GUARDIAN_CONSENSUS_REQUIRED`
- `GUARDIAN_EMERGENCY_DISABLE_PATH`
- `GUARDIAN_ETHICS_LEVEL`
- `GUARDIAN_TIMEOUT`
- `HOST`
- `LOG_LEVEL`
- `LUKHAS_ADVANCED_TAGS`
- `LUKHAS_CANARY_PERCENT`
- `LUKHAS_CREDENTIALS_PATH`

## 🔍 Usage Examples

### Development Environment
```bash
# Minimal development setup
export LUKHAS_ENV=dev
export LUKHAS_LANE=candidate
export LUKHAS_DEBUG=true
export LOG_LEVEL=DEBUG
export GUARDIAN_ETHICS_LEVEL=1
```

### Production Environment
```bash
# Production configuration
export LUKHAS_ENV=production
export LUKHAS_LANE=lukhas
export LUKHAS_DEBUG=false
export LOG_LEVEL=INFO
export GUARDIAN_ETHICS_LEVEL=3
export ETHICS_ENFORCEMENT_LEVEL=strict
export AUTH_P95_TARGET_MS=200
export CONTEXT_P95_TARGET_MS=200
```

### Testing Environment
```bash
# Testing with relaxed constraints
export LUKHAS_ENV=test
export LUKHAS_LANE=candidate
export ALLOW_NO_AUTH=true
export GUARDIAN_TIMEOUT=1000
export LUKHAS_REQUEST_TIMEOUT=10
```

## 🚀 Quick Start

1. **Copy .env.example**: `cp .env.example .env`
2. **Set required variables**: Update `LUKHAS_ID_SECRET` and `LUKHAS_MASTER_KEY`
3. **Configure environment**: Set `LUKHAS_ENV` to your target environment
4. **Review security settings**: Ensure Guardian and ethics settings match your needs
5. **Test configuration**: Run `make doctor` to validate settings

## 📝 Notes

- **Security**: Never commit `.env` files with real secrets to version control
- **Defaults**: Most variables have sensible defaults and are optional
- **Validation**: The system validates required variables on startup
- **Override Priority**: CLI args > Environment variables > Config files > Defaults
- **Documentation**: Auto-generated from codebase audit on 2025-11-06

## 🔗 Related Documentation

- [Guardian Ethics System](./GUARDIAN.md)
- [Lane Architecture](./LANES.md)
- [ΛiD Identity System](./IDENTITY.md)
- [Configuration Guide](./CONFIGURATION.md)

---

**Audit Source:** Generated from comprehensive codebase scan
**Last Updated:** 2025-11-06
**Coverage:** 73/73 detected environment variables documented
