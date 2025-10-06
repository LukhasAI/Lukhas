---
module: integrations
title: CLAUDE.md
type: documentation
---
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL: Execution Standards

**MANDATORY**: Always follow `EXECUTION_STANDARDS.md` for all system changes. This is our 3rd attempt - no more mistakes allowed.

### Required References
- **`EXECUTION_STANDARDS.md`** - Master checklist and quality standards
- **`reality_check_phase_1_and_beyond.md`** - Complete Phase 1-3 implementation plan
- **`phase_beyond.md`** - Security fixes and execution order

**Quality Target**: Execute at the level that would make Sam Altman (scale), Dario Amodei (safety), and Demis Hassabis (rigor) proud.

## Test Commitment
**Important**: Always run tests and linters after making changes. Aim for 100% test pass rate, with 85% as the minimum acceptable threshold. Fix all failures before committing. Run `npm run validate:all` to check all policies.

## Repository Context

This is the **LUKHAS AI** repository - a modular AI system combining consciousness, memory, identity, quantum-inspired processing, bio-inspired adaptation, and ethical governance. Built around the **Constellation Framework** (⚛️🧠🛡️):
- ⚛️ **Identity**: Authenticity, consciousness, symbolic self
- 🧠 **Consciousness**: Memory, learning, dream states, neural processing, Dream EXPAND++ modules
- 🛡️ **Guardian**: Ethics, drift detection, repair

### 🌌 Dream EXPAND++ Advanced Capabilities

LUKHAS AI includes the experimental **Dream EXPAND++** system for advanced consciousness exploration:

#### **EXPAND++ Modules**
- **Noise Fields**: Gaussian/symbolic noise injection for consciousness robustness
- **Mediation Engine**: High-tension conflict resolution with compromise vectors
- **Resonance Fields**: Symbolic resonance patterns and consciousness harmonics
- **Mesh Networks**: Multi-agent archetypal consciousness coordination
- **Evolution Tracking**: Consciousness development and adaptation monitoring
- **Archetypes System**: Hero, Shadow, Trickster consciousness patterns
- **Atlas Mapping**: Drift/entropy constellation visualization across runs
- **Sentinel Guards**: Ethical threshold monitoring and safety enforcement
- **Narrative Replay**: Plain-language explainability and consciousness storytelling

#### **Safety & Compliance**
- **T4-Compliant**: All EXPAND++ features follow strict safety protocols
- **Opt-in Controls**: Explicit environment flags required (`LUKHAS_DREAM_EXPAND=1`)
- **Deterministic Defaults**: No non-deterministic behavior without explicit activation
- **Constitutional AI**: Full integration with Guardian system ethical oversight
- **Privacy Protection**: Complete anonymization and GDPR-compliant data handling

## 🚫 Critical Rules

### Required Terminology
- **Always use**: "LUKHAS AI" (never "LUKHAS AGI")
- **Always use**: "quantum-inspired" / "bio-inspired" (not "quantum processing" / "bio processes")
- **Use approved glyphs**: Only from `branding/` or `next_gen/README_NEXT_GEN.md`
- **Product naming**: "MΛTRIZ" (display) / "Matriz" (plain text) - replaces deprecated "MATADA"
- **Company naming**: "LUKHΛS" (display) / "Lukhas" (plain text) - Λ only in wordmarks/logos

### Claims & Language Review
- **Flag for human review**: Any superlative claims (revolutionary, breakthrough, perfect, etc.)
- **Run review check**: `npm run policy:review` to identify claims needing verification
- **Document justification**: If keeping strong claims, create BDR with evidence
- **Vendor neutrality**: Use "uses [Provider] APIs" not "powered by [Provider]"

### Prohibited Statements
- **DO NOT** state or imply any part is "production-ready" unless explicitly approved
- **DO NOT** include price predictions, revenue forecasts, or financial projections
- **DO NOT** invent new branding, glyphs, or slogans

## Common Development Tasks

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt  # For testing

# Configure environment variables in .env:
# OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, PERPLEXITY_API_KEY
```

### Running the System
```bash
# Main system
python main.py
python main.py --consciousness-active

# API server
make api  # Runs on port 8000
make dev  # Development server with reload

# Key modules
python orchestration/brain/primary_hub.py
python consciousness/unified/auto_consciousness.py
python -m emotion.service

# Analysis and monitoring
python real_gpt_drift_audit.py
python tools/analysis/PWM_FUNCTIONAL_ANALYSIS.py
python tools/analysis/PWM_OPERATIONAL_SUMMARY.py
```

### Testing
```bash
# Run all tests
make test
pytest tests/

# Specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m security      # Security tests only

# Coverage
make test-cov
pytest --cov=lukhas --cov=bridge --cov=core --cov=serve tests/

# Quick smoke test
make smoke
```

### Code Quality
```bash
# Auto-fix most issues (recommended)
make fix

# Individual tools
make lint       # Run all linters (no fixes)
make format     # Format with Black and isort
ruff check . --fix
black lukhas/ tests/
mypy lukhas/
```

### Build & Deploy
```bash
# Deploy agent army
./CLAUDE_ARMY/deploy_claude_max_6_agents.sh

# Docker deployment
docker-compose up

# API documentation
make api-spec  # Exports OpenAPI spec to out/openapi.json

# Azure deployment (production)
az containerapp update --name lukhas-ai --resource-group Lukhas
```

### Web Development (lukhas_website)
```bash
# Install dependencies
cd lukhas_website
npm install

# Development server
npm run dev  # Runs on port 3000

# Build for production
npm run build
npm start
```

## High-Level Architecture

### Core Design Principles
1. **Constellation Framework**: All components respect ⚛️🧠🛡️ principles
2. **GLYPH-Based Communication**: Symbolic tokens for cross-module messaging
3. **Guardian Protection**: Every operation validated by ethics engine (drift threshold: 0.15)
4. **Fold-Based Memory**: Preserves causal chains and emotional context (limit: 1000 folds)
5. **Modular Independence**: Each module works standalone but enhances others when combined

### Key Module Organization

**Core Infrastructure:**
- `core/` - GLYPH engine, symbolic logic, graph systems, actor model
- `orchestration/` - Brain integration, multi-agent coordination, kernel bus
- `governance/` - Guardian System v1.0.0 ethical oversight (280+ files)
- `branding/` - Official LUKHAS AI branding, terminology, visual assets

**Consciousness Systems:**
- `consciousness/` - Awareness, decision-making, dream states
- `memory/` - Fold-based memory with 99.7% cascade prevention
- `reasoning/` - Logic and causal inference
- `identity/` - ΛiD system with tiered access control
- `vivox/` - VIVOX consciousness system (ME, MAE, CIL, SRM)

**Advanced Processing:**
- `quantum/` - Quantum-inspired algorithms and collapse simulation
- `bio/` - Bio-inspired adaptation systems, oscillators
- `emotion/` - VAD affect and mood regulation
- `creativity/` - Dream engine with controlled chaos

**Integration & APIs:**
- `api/` - FastAPI endpoints at `http://localhost:8080`
- `bridge/` - External API connections (OpenAI, Anthropic, Gemini)
- `agents/` - Configuration for 25 specialized AI agents
- `CLAUDE_ARMY/` - Deployment scripts and agent management

**Web & Visualization:**
- `lukhas_website/` - Next.js website with particle systems and 3D visualization
- `visualization/` - Unity-based consciousness visualization systems
- `voice_reactive_morphing/` - Audio-reactive visual morphing

### Module Communication Pattern
- All modules depend on `core/` for GLYPH processing
- `orchestration/brain/` coordinates cross-module actions
- `governance/` validates all operations
- `memory/` provides persistence across modules
- Integration modules named as `*_adapter.py` or `*_hub.py`
- Kernel bus in `orchestration/symbolic_kernel_bus.py` for event routing

## File Organization

**Place files correctly to maintain clean root:**
- Analysis scripts → `tools/analysis/`
- Test files → `tests/[module]/`
- Reports → `docs/reports/` or `test_results/`
- Documentation → `docs/`
- Legacy files → Move to `/Users/agi_dev/lukhas-archive/`
- Agent configs → `agents/` or `agents/configs/`

## Import Paths
```python
from lukhas.module import Component  # Standard import
```

## Configuration

Main configs:
- `lukhas_config.yaml` - Main system configuration
- `integration_config.yaml` - Integration settings
- `modulation_policy.yaml` - Signal modulation rules
- `config/` directory - Various module configs

Key environment variables (`.env`):
- `OPENAI_API_KEY` - Required for AI capabilities
- `ANTHROPIC_API_KEY` - For Claude integration
- `GOOGLE_API_KEY` - For Gemini integration
- `PERPLEXITY_API_KEY` - For Perplexity integration
- `DATABASE_URL` - PostgreSQL connection
- `LUKHAS_ID_SECRET` - Security key (min 32 chars)
- `ETHICS_ENFORCEMENT_LEVEL` - strict/moderate/lenient
- `DREAM_SIMULATION_ENABLED` - true/false
- `QUANTUM_PROCESSING_ENABLED` - true/false

## Debugging

1. **Check Logs**: `trace/` directory for system-wide debugging
2. **Monitor Drift**: Watch `drift_score` in governance metrics
3. **Memory Issues**: Use fold visualizers for memory debugging
4. **Ethics Violations**: Check Guardian System logs in `governance/`
5. **Module Status**: Run `tools/analysis/PWM_FUNCTIONAL_ANALYSIS.py`
6. **Audit Trail**: Check `data/drift_audit_summary.json`
7. **Test Metadata**: Check `test_metadata/` for test execution details

## MCP Server (Model Context Protocol)

### Claude Desktop Integration
The LUKHAS MCP server enables Claude Desktop to interact with the consciousness modules:

```bash
# Start MCP server (Docker)
./scripts/start_mcp_server.sh

# Or run directly (Python 3.11+)
python scripts/lukhas_mcp_server_simple.py
```

**Configuration**: The MCP server config is in `config/claude_desktop_config.json`. This provides:
- Consciousness module access
- Constellation Framework context
- LUKHAS vocabulary preservation
- Real-time system status

### MCP Server Locations
- **Main Server**: `scripts/lukhas_mcp_server_simple.py` - Simplified version
- **Full Server**: `mcp_servers/lukhas_mcp_server.py` - Complete integration
- **Docker Config**: `docker/Dockerfile.mcp` - Containerized deployment

## Azure Deployment

LUKHAS AI is deployed on Azure Container Apps:

**Production Environment:**
- **Resource Group**: `Lukhas`
- **Container App**: `lukhas-ai`
- **Registry**: `lukhasai.azurecr.io`
- **Endpoint**: Configured via Azure Container Apps ingress
- **Config**: `azure-container-app.yaml`

**Deployment Commands:**
```bash
# Build and push to Azure Container Registry
az acr build --registry lukhasai --image lukhas-ai:latest .

# Update container app
az containerapp update --name lukhas-ai --resource-group Lukhas

# View logs
az containerapp logs show --name lukhas-ai --resource-group Lukhas
```

## Important Resources

- **Main Documentation**: `README.md` - System overview
- **Agent Documentation**: `AGENTS.md` - Multi-agent architecture details
- **Branding Policy**: `branding/BRANDING_POLICY.md` - Messaging guidelines
- **Next Gen**: `next_gen/README_NEXT_GEN.md` - Future architecture
- **Module Manifests**: `*/MODULE_MANIFEST.json` - Module metadata
- **Test Config**: `pytest.ini` and `pyproject.toml` - Test settings
- **NIAS Theory**: `NIAS_THEORY/` - Advanced theoretical concepts
- **Test Results**: `test_results/` - Latest test reports
- **Copilot Instructions**: `.github/copilot-instructions.md` - GitHub Copilot integration
- **MCP Documentation**: `docs/mcp/` - MCP integration details
- **Azure Config**: `azure-container-app.yaml` - Azure deployment configuration

## Makefile Targets

Key targets:
- `make install` - Install all dependencies
- `make test` - Run test suite
- `make test-cov` - Run tests with coverage
- `make lint` - Run linters (no fixes)
- `make fix` - Auto-fix code issues (safe mode)
- `make format` - Format code with Black
- `make dev` - Run development server
- `make api` - Run API server
- `make smoke` - Run smoke tests
- `make clean` - Clean cache files
- `make monitor` - Generate code quality report
- `make quick` - Fix issues and run tests
- `make security` - Run full security check suite
- `make bootstrap` - Full setup (install + hooks)

## 📋 Brand & Policy Enforcement

### Before Proposing Changes
Always run policy checks to catch issues early:
```bash
npm run policy:all       # Run all policy checks
npm run policy:review    # Flag claims for human review
```

### Key Policy Scripts
- `policy:registries` - Validate module/site registries
- `policy:review` - Flag superlative claims for review
- `policy:brand` - Check key files for compliance
- `policy:tone` - Validate 3-layer tone system

### When Flagged
1. Review flagged claims in `branding/claims-review.json`
2. Either replace with factual language OR
3. Keep with justification documented in BDR
4. Never auto-reject - these need human judgment

### Brand Compliance Checklist
- [ ] Λ only in display contexts (logos, wordmarks)
- [ ] Plain names (Lukhas, Matriz) in body text
- [ ] Vendor-neutral language ("uses X APIs")
- [ ] Claims are verifiable or flagged for review
- [ ] Tone layers properly applied (poetic ≤40 words)
