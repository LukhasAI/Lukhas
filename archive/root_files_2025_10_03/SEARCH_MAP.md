---
status: wip
type: documentation
---
# LUKHAS Search Map

Quick reference for finding components, patterns, and key code in the LUKHAS ecosystem.

## Core Component Searches

### Guardian & Ethics
```bash
# Find Guardian actions and decisions
rg -n "risk_band|action|guardian" ethics/

# Find ethics tags and validations
rg -n "REQUIRE_HUMAN|ALLOW|WARN|BLOCK" --type py

# Find safety thresholds and drift detection
rg -n "drift|threshold|safety" governance/ lukhas/
```

### MATRIZ Envelope System
```bash
# Find MATRIZ envelope processing
rg -n "MATRIZ|envelope" -g '!tests/**' --type py

# Find symbolic processing core
rg -n "glyph|symbolic|token" MATRIZ/ lukhas/core/

# Find bio-symbolic adaptation
rg -n "bio_symbolic|adaptation" --type py
```

### Consciousness & Memory
```bash
# Find consciousness states and processing
rg -n "consciousness|awareness|reflection" candidate/consciousness/ lukhas/

# Find memory systems and folds
rg -n "memory_fold|helix|temporal" candidate/memory/ lukhas/memory/

# Find dream engine and creativity
rg -n "dream|creativity|chaos" candidate/consciousness/creativity/
```

### Identity & Authentication
```bash
# Find Lambda ID and authentication
rg -n "lambda_id|auth|identity" lukhas/identity/ candidate/governance/identity/

# Find WebAuthn and passkey implementations
rg -n "webauthn|passkey|biometric" --type py

# Find consent and ledger systems
rg -n "consent|ledger|privacy" --type py
```

## Architecture & Configuration

### Configuration Files
```bash
# Find all config files
find . -name "*.ini" -o -name "*.yaml" -o -name "*.yml" -o -name "*config*"

# Find environment variable usage
rg -n "ENV|getenv|environ" --type py

# Find feature flags
rg -n "FEATURE_|feature_flag|enable" --type py
```

### API & Orchestration
```bash
# Find API endpoints and routes
rg -n "@app\.|@router\.|@api\." --type py

# Find orchestration and brain hub
rg -n "brain_hub|orchestration|coordinator" --type py

# Find service communication
rg -n "service|adapter|bridge" lukhas/bridge/ candidate/bridge/
```

## Testing & Quality

### Test Organization
```bash
# Find test categories and markers
rg -n "@pytest\.mark\." tests/

# Find integration tests
find tests/ -name "*integration*" -o -name "*e2e*"

# Find mock and fixture usage
rg -n "mock|fixture|patch" tests/
```

### Performance & Monitoring
```bash
# Find performance benchmarks
rg -n "benchmark|perf|performance" tests/ --type py

# Find monitoring and metrics
rg -n "prometheus|metric|monitor" --type py

# Find health checks
rg -n "health|status|alive" --type py
```

## Data & Storage

### Database & Persistence
```bash
# Find database models and queries
rg -n "sqlalchemy|model|query" --type py

# Find JSON data structures
find . -name "*.json" | grep -E "(config|schema|data)"

# Find data validation schemas
rg -n "pydantic|schema|validation" --type py
```

### File Organization by Domain
```bash
# Production code (lukhas/)
ls lukhas/           # Core production modules
ls MATRIZ/           # Symbolic processing system
ls branding/         # Brand and content systems

# Experimental code (candidate/)
ls candidate/        # Research and experimental features
ls products/         # Product-specific implementations
ls deployment/       # Infrastructure and deployment
```

## Quick Navigation

### Entry Points
- `main.py` - Main application entry
- `lukhas/` - Production code modules
- `tests/` - Test suites organized by category
- `docs/` - Architecture and design documentation
- `tools/` - Development and CI utilities

### Key Configuration
- `pyproject.toml` - Python project configuration
- `.env.example` - Environment variable template
- `requirements.txt` - Pinned dependencies
- `pytest.ini` - Test configuration

### Generated Artifacts
- `reports/` - Generated reports and analysis
- `data/` - Runtime data and metrics
- `htmlcov/` - Test coverage reports

## Search by Intent

### "How do I add a new module?"
```bash
# Look at existing module patterns
find lukhas/ -name "__init__.py" | head -5
rg -n "class.*Module|class.*Engine" lukhas/ | head -10
```

### "How does authentication work?"
```bash
# Find auth flow
rg -n "authenticate|authorize|login" lukhas/identity/
rg -A 10 -B 5 "WebAuthn|JWT" --type py
```

### "How are errors handled?"
```bash
# Find error handling patterns
rg -n "except|raise|Error|Exception" lukhas/ | head -10
rg -n "guardian.*error|safety.*error" --type py
```

### "What external services are integrated?"
```bash
# Find external integrations
rg -n "openai|anthropic|google|gmail|dropbox" --type py
find . -name "*adapter*" -o -name "*bridge*" | grep -v __pycache__
```

## Development Workflow

### Before Making Changes
```bash
# Check test coverage for area
.venv/bin/pytest tests/smoke/ -v
rg -n "TODO|FIXME|XXX" lukhas/

# Find related tests
find tests/ -name "*<module_name>*"
```

### Code Quality Checks
```bash
# Find import patterns
rg -n "^from |^import " lukhas/ | sort | uniq -c | sort -nr | head -20

# Find complexity hotspots
find lukhas/ -name "*.py" -exec wc -l {} + | sort -nr | head -10
```

### Debug Information
```bash
# Find logging statements
rg -n "log\.|logger\.|print\(" --type py

# Find debug flags
rg -n "debug|DEBUG|verbose" --type py
```

---

*This search map is generated to help developers and AI assistants quickly locate relevant code and understand the LUKHAS architecture.*