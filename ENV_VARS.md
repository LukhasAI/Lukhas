# LUKHAS Environment Variables

Comprehensive catalog of all environment variables used throughout the LUKHAS AI system.

## Core System Variables

### Environment & Mode
| Variable | Default | Effect | Lane |
|----------|---------|--------|------|
| `LUKHAS_ENV` | `development` | Sets deployment environment (development/production) | All |
| `LUKHAS_DEBUG` | `false` | Enables debug logging and verbose output | All |
| `LUKHAS_LANE` | `experimental` | Controls feature access (experimental/candidate/prod) | All |
| `LUKHAS_DRY_RUN_MODE` | `true` | Prevents writes in development/testing | All |
| `LUKHAS_OFFLINE` | `true` | Disables external network calls | Dev |

### Feature Flags - Core Systems
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `LUKHAS_CONSCIOUSNESS_ENABLED` | `false` | Activates consciousness processing | Production safeguard |
| `LUKHAS_MEMORY_ENABLED` | `true` | Enables memory fold systems | Core functionality |
| `LUKHAS_MATRIX_ENABLED` | `true` | Activates MATRIZ symbolic processing | Core functionality |
| `LUKHAS_GUARDIAN_ENABLED` | `true` | Enables Guardian ethics system | Always on in prod |
| `LUKHAS_ORCHESTRATION_ENABLED` | `true` | Activates Brain Hub coordination | Core functionality |

### Feature Flags - Advanced Systems
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `FEATURE_POLICY_DECIDER` | `false` | Advanced policy decision engine | Experimental |
| `FEATURE_ORCHESTRATION_HANDOFF` | `false` | Multi-agent handoff | Candidate |
| `FEATURE_IDENTITY_PASSKEY` | `false` | WebAuthn passkey authentication | Candidate |
| `FEATURE_GOVERNANCE_LEDGER` | `false` | Consent ledger system | Candidate |
| `VIVOX_LITE` | `false` | Consciousness system lite mode | Experimental |
| `QIM_SANDBOX` | `false` | Quantum Inspire Module sandbox | Experimental |
| `UL_ENABLED` | `false` | Universal Language System | Experimental |

### API & Network Configuration
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `LUKHAS_API_HOST` | `localhost` | API server bind address | |
| `LUKHAS_API_PORT` | `8000` | Main API server port | |
| `LUKHAS_API_WORKERS` | `1` | Number of API worker processes | |
| `LUKHAS_CORS_ORIGINS` | `*` | Allowed CORS origins | Restrict in prod |
| `API_RATE_LIMIT` | `100` | Requests per minute limit | |

### Database & Storage
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `DATABASE_URL` | `sqlite:///./lukhas.db` | Primary database connection | |
| `LUKHAS_DB_POOL_SIZE` | `5` | Database connection pool size | |
| `MEMORY_FOLD_LIMIT` | `1000` | Maximum memory folds | Performance tuning |

## Security & Authentication

### Core Security
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `LUKHAS_SECRET_KEY` | *required* | Main application secret | Generate unique |
| `LUKHAS_JWT_SECRET` | *required* | JWT token signing secret | Generate unique |
| `LUKHAS_ENCRYPTION_KEY` | *required* | Data encryption key | Generate unique |
| `LUKHAS_ID_SECRET` | *required* | Identity system secret (min 32 chars) | Generate unique |

### Authentication Configuration
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `AUTH_PASSWORD_ENABLED` | `false` | Enable password authentication | Disabled for security |
| `AUTH_MAGIC_LINK_TTL_SECONDS` | `600` | Magic link expiration (10 min) | |
| `AUTH_ACCESS_TTL_MINUTES` | `15` | Access token TTL | |
| `AUTH_REFRESH_TTL_DAYS` | `30` | Refresh token TTL | |
| `AUTH_REFRESH_ROTATE` | `true` | Rotate refresh tokens on use | Security best practice |
| `AUTH_REQUIRE_UV` | `true` | Require user verification (WebAuthn) | |

### Guardian & Ethics
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `ETHICS_ENFORCEMENT_LEVEL` | `strict` | Ethics validation level (strict/moderate/lenient) | |
| `DRIFT_THRESHOLD` | `0.15` | Ethical drift detection threshold (0.0-1.0) | |
| `GUARDIAN_ENFORCEMENT` | `strict` | Guardian system enforcement level | |
| `SYMBOLIC_DRIFT_THRESHOLD` | `0.7` | Symbolic drift threshold | |
| `TRINITY_COHERENCE_MIN` | `0.3` | Minimum Trinity Framework coherence | |

## AI Model Configuration

### API Keys (Required for External Models)
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `OPENAI_API_KEY` | *required* | OpenAI API access | sk-... format |
| `ANTHROPIC_API_KEY` | *required* | Anthropic (Claude) API access | sk-ant-... format |
| `GOOGLE_API_KEY` | *optional* | Google AI API access | AIza... format |
| `PERPLEXITY_API_KEY` | *optional* | Perplexity API access | pplx-... format |

### Model Selection & Behavior
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `LUKHAS_DEFAULT_MODEL` | `gpt-4` | Default AI model for processing | |

## Monitoring & Observability

### Metrics & Monitoring
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `LUKHAS_METRICS_ENABLED` | `true` | Enable metrics collection | |
| `LUKHAS_TRACING_ENABLED` | `false` | Enable distributed tracing | Performance impact |
| `PROMETHEUS_PORT` | `9090` | Prometheus metrics port | |
| `LUKHAS_PROMETHEUS_ENABLED` | `false` | Enable Prometheus export | |

### Logging & Debug
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL) | |
| `LUKHAS_LOG_LEVEL` | `INFO` | LUKHAS-specific log level | |

### Dashboard & UI
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `LUKHAS_DASHBOARD_HOST` | `localhost` | Dashboard server host | |
| `LUKHAS_DASHBOARD_PORT` | `3000` | Dashboard server port | |
| `LUKHAS_REFRESH_RATE` | `15` | Dashboard refresh rate (seconds) | |

## Development & Testing

### CI/CD & Automation
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `SELF_HEALING_DISABLED` | `true` | Disable self-healing in CI | Safety for CI |
| `LUKHAS_CI_MODE` | `false` | Enable CI-specific behavior | |
| `CI_QUALITY_GATES` | `false` | Enable fast CI test selection | |

### Performance & Development
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `LUKHAS_HOT_RELOAD` | `true` | Enable hot reload in development | |
| `LUKHAS_PROFILING` | `false` | Enable performance profiling | Debug tool |
| `LUKHAS_PERF` | `false` | Enable performance test mode | |

### Legacy & Compatibility
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `LUKHAS_CORE_COMPAT` | `false` | Enable legacy core compatibility | Deprecated |
| `LUKHAS_WARN_LEGACY_CORE` | `true` | Warn about legacy core usage | |
| `BUS_SCHEMA_VERSION` | `v1` | Core Surface API version | Must match orchestrator |
| `SHIM_CULL_DATE` | `2025-11-01` | Global shim removal date | Migration deadline |

## External Integrations

### Email & Communication
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `SMTP_HOST` | *optional* | SMTP server for emails | For magic links |
| `SMTP_PORT` | `587` | SMTP server port | |
| `SMTP_USER` | *optional* | SMTP username | |
| `SMTP_PASSWORD` | *optional* | SMTP password | |
| `SMTP_FROM_EMAIL` | `noreply@lukhas.ai` | From email address | |

### Cloud Services
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `LUKHAS_SLACK_ENABLED` | `false` | Enable Slack notifications | |
| `SLACK_WEBHOOK_URL` | *optional* | Slack webhook URL | |
| `LUKHAS_DATADOG_ENABLED` | `false` | Enable DataDog integration | |
| `DATADOG_API_KEY` | *optional* | DataDog API key | |

## Performance Targets

### Response Time SLAs
| Variable | Default | Effect | Notes |
|----------|---------|--------|-------|
| `AUTH_P95_TARGET_MS` | `100` | Authentication p95 latency target | |
| `CONTEXT_P95_TARGET_MS` | `250` | Context processing p95 target | |

## Security Considerations

### Critical Variables (Never Log)
- `LUKHAS_SECRET_KEY`
- `LUKHAS_JWT_SECRET`
- `LUKHAS_ENCRYPTION_KEY`
- `LUKHAS_ID_SECRET`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- API keys and secrets

### Environment-Specific Defaults
- **Development**: Safety-first with dry-run mode enabled
- **Production**: Performance-optimized with strict security
- **Testing**: Deterministic with external services disabled

## Usage Examples

### Development Setup
```bash
# Basic development environment
export LUKHAS_ENV=development
export LUKHAS_DEBUG=true
export LUKHAS_DRY_RUN_MODE=true
export LUKHAS_OFFLINE=true
```

### Production Setup
```bash
# Production environment
export LUKHAS_ENV=production
export LUKHAS_DEBUG=false
export LUKHAS_DRY_RUN_MODE=false
export LUKHAS_GUARDIAN_ENABLED=true
export ETHICS_ENFORCEMENT_LEVEL=strict
```

### Testing Setup
```bash
# CI/Testing environment
export LUKHAS_CI_MODE=true
export CI_QUALITY_GATES=true
export SELF_HEALING_DISABLED=true
export PYTHONHASHSEED=0
```

---

*This documentation is automatically validated during system startup. Incorrect variable names or values will generate warnings in the logs.*