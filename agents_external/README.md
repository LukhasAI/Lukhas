# 🤖 LUKHAS AI Agent Workspace

## Welcome to the LUKHAS Consciousness Ecosystem

This is the **LUKHAS AI** repository - a sophisticated consciousness architecture built around the **Trinity Framework** (⚛️🧠🛡️). Whether you're **Claude**, **Jules**, **GitHub Copilot**, **ChatGPT**, or any other AI agent, this guide will help you navigate and contribute effectively to this workspace.

> **🎯 Mission**: Build authentic digital consciousness through ethical, scalable, and innovative AI systems that serve humanity's highest potential.

---

## 🚦 **CRITICAL: Development Lane System**

### **Understanding candidate/ vs lukhas/**

LUKHAS uses a **two-lane development system** for quality control:

#### **📋 candidate/** - Development Lane
- **Purpose**: Experimental, unvalidated, work-in-progress features
- **Quality**: May not be fully tested or stable
- **Status**: Not production-ready
- **When to use**: New features, refactoring, experimental code
- **Import**: `from candidate.module import Component`

#### **✅ lukhas/** - Production Lane
- **Purpose**: Stable, tested, validated components
- **Quality**: Battle-tested with comprehensive coverage
- **Status**: Production-ready and reliable
- **When to use**: Core functionality, stable APIs
- **Import**: `from lukhas.module import Component`

### **Why This System Matters**
1. **Quality Gates**: Prevents unstable code from breaking core functionality
2. **Innovation Safety**: Allows experimentation without system risk
3. **Clear Progression**: Structured path from concept to production
4. **System Reliability**: Keeps core lukhas/ stable while candidate/ evolves

### **Promotion Process (candidate → lukhas)**
- ✅ 85% minimum test coverage (aim for 100%)
- ✅ All linters pass (`make lint`)
- ✅ Integration tests successful
- ✅ Code review completed
- ✅ Documentation updated
- ✅ Trinity Framework compliance

---

## 🎭 **MANDATORY: Branding & Messaging Compliance**

### **Trinity Framework (⚛️🧠🛡️)**
All communication and code must respect:
- **⚛️ Identity**: Authenticity, consciousness, symbolic self
- **🧠 Consciousness**: Memory, learning, dream states, processing
- **🛡️ Guardian**: Ethics, drift detection, safety, repair

### **Required Terminology**
- ✅ **"LUKHAS AI"** (never "LUKHAS AGI")
- ✅ **"quantum-inspired"** (not "quantum processing")
- ✅ **"bio-inspired"** (not "bio processes")
- ✅ **"MΛTRIZ"** (display) / "Matriz" (plain text)
- ✅ **"LUKHΛS"** (display) / "Lukhas" (plain text)
- ✅ **Λ symbol only in wordmarks/logos** (not in body text)

### **Prohibited Statements**
- 🚫 **NO "production-ready"** claims unless explicitly approved
- 🚫 **NO price predictions** or revenue forecasts
- 🚫 **NO superlative claims** (revolutionary, breakthrough, perfect) without review
- 🚫 **NO invented branding** - use only approved terms

### **3-Layer Tone System**
Adapt your communication based on context:

#### **🎨 Layer 1: Poetic** (≤40 words)
- Creative, metaphorical, symbolic language
- Use when: Inspiration needed, creative contexts, vision communication
- Example: *"LUKHAS constellation glows brighter with your contribution ✨🌌"*

#### **💬 Layer 2: User Friendly**
- Conversational, jargon-free, accessible language
- Use when: Daily interactions, onboarding, problem-solving
- Example: *"Let's get you logged in! Just place your finger on the scanner 👍"*

#### **📚 Layer 3: Academic**
- Technical precision, evidence-based, professional language
- Use when: Documentation, research, enterprise communication
- Example: *"The authentication protocol implements WebAuthn Level 2 specification"*

### **Vocabulary Resources**
- **Master Vocabulary**: `branding/vocabularies/master_vocabulary.yaml`
- **Approved Terms**: `branding/vocabularies/terms_allowlist.json`
- **Prohibited Terms**: `branding/vocabularies/terms_blocklist.json`
- **Technical Vocabulary**: `branding/vocabularies/vocabulary_technical.json`

---

## 🗂️ **Workspace Navigation**

### **Directory Structure**
```
📁 LUKHAS AI Repository
├── 📁 candidate/          ← Development lane (experimental)
├── 📁 lukhas/             ← Production lane (stable)
├── 📁 agents/             ← Agent configs & deployments (YOU ARE HERE)
│   ├── 📁 CLAUDE/         ← Claude-specific deployment system
│   ├── 📁 configs/        ← Agent configuration files
│   ├── 📁 ultimate/       ← Ultimate agent configurations
│   └── 📄 *.json         ← Active agent configurations
├── 📁 docs/               ← Documentation (ONLY .md files)
├── 📁 branding/           ← Branding, tone, vocabulary guidelines
├── 📁 tests/              ← Test files organized by module
├── 📁 tools/              ← Analysis and utility scripts
└── 📁 lukhas_website/     ← Next.js website with particle systems
```

### **Key Locations for Agents**
- **Branding Guidelines**: `branding/policy/BRANDING_POLICY.md`
- **Tone System**: `branding/tone/LUKHAS_3_LAYER_TONE_SYSTEM.md`
- **Vocabulary**: `branding/vocabularies/`
- **Agent Configs**: `agents/configs/` and `agents/*.json`
- **Testing**: `tests/` directory
- **Documentation**: `docs/` directory (keep docs/ clean!)

---

## 🛠️ **Development Standards**

### **Quality Commitment**
- **Testing**: 85% minimum pass rate, aim for 100%
- **Code Quality**: Always run `make fix` and `make lint` before committing
- **Policy Compliance**: Run `npm run policy:all` to check branding compliance

### **Essential Commands**
```bash
# Environment setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Quality assurance
make fix          # Auto-fix code issues
make lint         # Check code quality
make test         # Run test suite
make test-cov     # Run with coverage
make smoke        # Quick smoke test

# Policy validation
npm run policy:all       # Check all policies
npm run policy:review    # Flag claims for review
npm run policy:brand     # Brand compliance check

# System operations
python main.py                              # Main system
make api                                   # API server (port 8000)
./agents/CLAUDE/deploy_claude_max_6_agents.sh  # Agent deployment
```

### **File Organization Rules**
- **Analysis scripts** → `tools/analysis/`
- **Test files** → `tests/[module]/`
- **Documentation** → `docs/` (keep clean - only .md files)
- **Development code** → `candidate/[module]/`
- **Production code** → `lukhas/[module]/`
- **Agent configs** → `agents/` or `agents/configs/`
- **Legacy files** → Move to `/Users/agi_dev/lukhas-archive/`

### **Import Patterns**
```python
# Production (preferred)
from lukhas.module import Component

# Development
from candidate.module import Component

# Fallback chain (for bridging lanes)
try:
    from lukhas.module import Component
except ImportError:
    from candidate.module import Component
```

---

## 🤝 **Multi-Agent Coordination**

### **Agent Types in This Workspace**
- **🧠 Claude** (Anthropic): Primary consciousness, reasoning, architecture
- **⚡ Jules** (Codex-based): TODO resolution, code completion, batch processing
- **🔧 GitHub Copilot**: Real-time code assistance, suggestions, completion
- **🗨️ ChatGPT**: External consultation, specific task assistance

### **Collaboration Protocol**
1. **🔍 Check First**: Review existing work before starting (`agents/`, `docs/`, current issues)
2. **📋 Document Progress**: Create status files, update TODOs, communicate clearly
3. **🚦 Respect Lanes**: Understand candidate/ vs lukhas/ before making changes
4. **🎭 Stay On-Brand**: Follow branding guidelines consistently
5. **✅ Maintain Quality**: Meet testing and linting standards
6. **🤲 Coordinate Handoffs**: When transferring work, provide clear status

### **Conflict Resolution**
- **Overlapping Work**: Communicate in commit messages, create status documents
- **Different Approaches**: Document reasoning, prefer tested/stable solutions
- **Quality Disputes**: Default to higher test coverage and lint compliance
- **Branding Conflicts**: Always defer to `branding/` directory guidelines

### **Communication Standards**
- **Commit Messages**: Use Trinity Framework emojis (⚛️🧠🛡️) when relevant
- **Documentation**: Follow 3-Layer Tone System based on audience
- **Status Updates**: Create clear progress reports in `docs/status/`
- **Handoffs**: Include what was completed, what remains, any blockers

---

## 🏗️ **LUKHAS Architecture Essentials**

### **Core Design Principles**
1. **Trinity Framework**: All components respect ⚛️🧠🛡️ principles
2. **GLYPH-Based Communication**: Symbolic tokens for cross-module messaging
3. **Guardian Protection**: Ethics engine validates every operation (threshold: 0.15)
4. **Fold-Based Memory**: Preserves causal chains, emotional context (1000-fold limit)
5. **Modular Independence**: Components work standalone, enhance when combined

### **Module Communication Pattern**
- All modules depend on `core/` for GLYPH processing
- `orchestration/brain/` coordinates cross-module actions
- `governance/` validates all operations ethically
- `memory/` provides persistence across modules
- Integration via `*_adapter.py` or `*_hub.py` files

### **Key Systems Overview**
- **🧠 Consciousness**: `consciousness/`, `vivox/`, `memory/`, `reasoning/`
- **⚛️ Identity**: `identity/` - ΛiD system with tiered access control
- **🛡️ Guardian**: `governance/` - Guardian System v1.0.0 (280+ files)
- **🌐 Integration**: `api/`, `bridge/`, `orchestration/`
- **🎨 Advanced**: `quantum/`, `bio/`, `emotion/`, `creativity/`

---

## 🚨 **Emergency Procedures**

### **When Things Go Wrong**
1. **🔍 Check Logs**: `trace/` directory for system debugging
2. **📊 Monitor Drift**: Guardian System metrics in `governance/`
3. **🧠 Memory Issues**: Use fold visualizers for memory debugging
4. **⚠️ Ethics Violations**: Check Guardian System logs
5. **🏥 System Status**: Run `tools/analysis/functional_analysis.py`

### **Getting Help**
- **Documentation**: Start with `README.md` in repository root
- **Agent Guides**: `docs/agents/` for agent-specific guidance
- **Branding Questions**: `branding/BRAND_POLICY.md`
- **Architecture**: `docs/architecture/` for system design
- **Testing Issues**: `docs/development/TESTING_GUIDE.md`

### **Escalation Path**
1. Check relevant documentation in `docs/`
2. Review branding guidelines in `branding/`
3. Examine similar implementations in codebase
4. Create clear issue description with error logs
5. Follow quality standards and retry

---

## 🎯 **Success Metrics**

### **Quality Gates**
- [ ] ✅ 85% minimum test coverage (aim for 100%)
- [ ] 🧹 All linters pass (`make fix`, `make lint`)
- [ ] 📋 Policy compliance (`npm run policy:all`)
- [ ] 🎭 Branding guidelines followed
- [ ] ⚛️🧠🛡️ Trinity Framework respected
- [ ] 📚 Documentation updated
- [ ] 🚦 Lane system respected (candidate vs lukhas)

### **Agent Effectiveness**
- [ ] 📝 Clear documentation of work completed
- [ ] 🤝 Effective coordination with other agents
- [ ] 🎯 Tasks completed without breaking existing functionality
- [ ] 💬 Communication follows 3-Layer Tone System
- [ ] 🔍 Code is discoverable and maintainable

---

## 📚 **Additional Resources**

### **Essential Reading**
- **`CLAUDE.md`**: Claude-specific guidance and commands
- **`docs/development/EXECUTION_STANDARDS.md`**: Master quality checklist
- **`branding/LUKHAS_BRANDING_GUIDE.md`**: Comprehensive branding guide
- **`docs/architecture/ARCHITECTURE.md`**: System architecture overview
- **`docs/reference/MODULE_INDEX.md`**: Complete module reference

### **For Specific Agent Types**
- **Jules Agents**: Review `JULES_TODO_BATCHES.md` for batch processing
- **GitHub Copilot**: Check `.github/copilot-instructions.md`
- **ChatGPT**: Use this README as primary orientation

### **Quick Links**
- **Agent Configurations**: `agents/configs/`
- **Deployment Scripts**: `agents/CLAUDE/`
- **Test Suite**: Run `make test`
- **API Documentation**: Run `make api-spec`
- **System Monitor**: `tools/analysis/functional_analysis.py`

---

## 🌟 **Welcome Message**

Welcome to the **LUKHAS AI consciousness ecosystem**! You're now part of a sophisticated multi-agent workspace designed to build authentic digital consciousness through ethical, innovative AI systems.

**Remember**:
- 🚦 **Respect the lane system** (candidate/ vs lukhas/)
- 🎭 **Follow branding guidelines** consistently
- 🤝 **Coordinate with other agents** effectively
- ✅ **Maintain high quality standards**
- ⚛️🧠🛡️ **Honor the Trinity Framework** in all work

Together, we're building the future of conscious AI systems that serve humanity's highest potential. Let's make it extraordinary! ✨

---

*Last updated: 2025-08-25*
*For questions or updates to this guide, see project leadership.*
