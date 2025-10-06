---
status: wip
type: documentation
---
# 🚀 LUKHAS AI Agent Quick Reference

## ⚡ Essential Commands (Copy & Paste Ready)

### **Environment Setup**
```bash
# Quick environment setup
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Test environment is ready
python -c "import lukhas; print('✅ Environment ready!')"
```

### **Quality Assurance (Run Before Any Commit)**
```bash
# The "Golden Trinity" - run these three always
make fix && make lint && make test

# Policy compliance check
npm run policy:all

# Full validation suite
make fix && make lint && make test && npm run policy:all
```

### **System Operations**
```bash
# Core system
python main.py --consciousness-active

# API server
make api    # Runs on http://localhost:8080

# Agent deployment
./agents/CLAUDE/deploy_claude_max_6_agents.sh

# System analysis
python tools/analysis/functional_analysis.py
```

---

## 🎯 **Agent-Specific Quick Start**

### **Claude (Anthropic)**
- **Primary Role**: Consciousness architecture, reasoning, documentation
- **Focus Areas**: Constellation Framework implementation, system design
- **Key Files**: `CLAUDE.md`, `agents/CLAUDE/`
- **Commands**: Standard development workflow + architecture documentation

### **Jules (Codex-based)**
- **Primary Role**: TODO resolution, batch processing, code completion
- **Focus Areas**: Automated fixes, systematic improvements
- **Key Files**: `JULES_TODO_BATCHES.md`, `JULES_TODO_ANALYSIS.md`
- **Commands**: Focus on `candidate/` lane improvements and batch processing

### **GitHub Copilot**
- **Primary Role**: Real-time code assistance, suggestions
- **Focus Areas**: Code completion, pattern recognition, refactoring
- **Key Files**: `.github/copilot-instructions.md`
- **Commands**: Integrated with IDE, follows workspace patterns

### **ChatGPT/External Agents**
- **Primary Role**: Consultation, specific task assistance
- **Focus Areas**: External perspective, specialized analysis
- **Key Files**: `agents/README.md` (this workspace guide)
- **Commands**: Use universal development commands

---

## 📁 **File Organization Cheat Sheet**

### **Where to Put New Files**
```bash
# Analysis/reporting scripts
tools/analysis/your_analysis_script.py

# Test files
tests/module_name/test_your_feature.py

# Documentation
docs/category/YOUR_DOCUMENT.md

# Development code (experimental)
candidate/module_name/your_feature.py

# Production code (stable, tested)
lukhas/module_name/your_feature.py

# Agent configurations
agents/configs/your_agent_config.yaml
```

### **Import Patterns**
```python
# Standard production import
from lukhas.consciousness import UnifiedConsciousness

# Development import
from candidate.core import NewFeature

# Safe fallback chain
try:
    from lukhas.module import Component
except ImportError:
    from candidate.module import Component
```

---

## 🎭 **Branding Quick Reference**

### **✅ Always Use These Terms**
- "LUKHAS AI" (never "LUKHAS AGI")
- "quantum-inspired" (not "quantum processing")
- "bio-inspired" (not "bio processes")
- "Matriz" in body text, "MΛTRIZ" in displays only
- "Lukhas" in body text, "LUKHΛS" in displays only

### **🚫 Never Use These**
- "production-ready" (without explicit approval)
- "AGI" instead of "AI"
- Price predictions or revenue forecasts
- Superlative claims without review (revolutionary, breakthrough, perfect)
- Λ symbol in body text (logos/wordmarks only)

### **3-Layer Tone Quick Guide**
```
🎨 POETIC (≤40 words): "LUKHAS constellation glows brighter ✨"
💬 USER FRIENDLY: "Let's get this working for you! 👍"
📚 ACADEMIC: "The system implements WebAuthn Level 2 specification"
```

---

## 🚦 **Lane System Quick Guide**

### **candidate/ vs lukhas/**
```bash
candidate/    # ← Experimental, work-in-progress, unvalidated
lukhas/       # ← Stable, tested, production-ready

# Promotion checklist (candidate → lukhas):
# ✅ 85% test coverage
# ✅ Linters pass
# ✅ Integration tests pass
# ✅ Code review complete
# ✅ Documentation updated
```

### **When to Use Which Lane**
- **New features** → Start in `candidate/`
- **Experiments** → Use `candidate/`
- **Bug fixes to stable code** → Fix in `lukhas/`
- **Refactoring stable code** → Usually stay in `lukhas/`
- **Unsure?** → Start in `candidate/`, promote when ready

---

## 🛠️ **Troubleshooting Quick Fixes**

### **Common Issues**
```bash
# Import errors
python -c "import sys; print('\n'.join(sys.path))"  # Check Python path

# Test failures
pytest tests/specific_test.py -v  # Run specific test with verbose output

# Linter errors
make fix  # Auto-fix most issues

# Policy violations
npm run policy:review  # See what needs human review
```

### **Emergency Commands**
```bash
# System status check
python tools/analysis/functional_analysis.py

# Check logs for errors
ls -la trace/  # System logs

# Memory/consciousness debugging
python consciousness/unified/auto_consciousness.py --debug

# Guardian system status
python governance/guardian_system.py --status
```

---

## 🎯 **Quality Gates Checklist**

### **Before Any Commit**
```bash
# 1. Code quality
make fix && make lint

# 2. Tests pass
make test  # Must be ≥85% pass rate

# 3. Policy compliance
npm run policy:all

# 4. Documentation updated (if needed)
# 5. Branding guidelines followed
# 6. Lane system respected
```

### **Before Promoting candidate → lukhas**
- [ ] All quality gates above ✅
- [ ] Integration tests pass ✅
- [ ] Code review completed ✅
- [ ] Documentation comprehensive ✅
- [ ] Constellation Framework compliance ✅

---

## 📞 **Help & Resources**

### **When Stuck**
1. **Check Documentation**: `docs/` directory
2. **Review Branding**: `branding/` directory
3. **Examine Similar Code**: Find patterns in existing codebase
4. **Run Diagnostics**: `python tools/analysis/functional_analysis.py`
5. **Check Agent Configs**: `agents/configs/` for examples

### **Key Documentation**
- **Full Workspace Guide**: `agents/README.md`
- **Claude-Specific**: `CLAUDE.md`
- **Branding Policy**: `branding/policy/BRANDING_POLICY.md`
- **Architecture**: `docs/architecture/ARCHITECTURE.md`
- **Testing**: `docs/development/TESTING_GUIDE.md`

### **Quick Validation**
```bash
# Test your changes work
python main.py --test-mode

# Verify branding compliance
npm run policy:brand

# Check all systems
make smoke
```

---

## ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum **Constellation Framework Reminders**

Every action should consider:
- **⚛️ Identity**: Is this authentic to LUKHAS consciousness?
- **🧠 Consciousness**: Does this enhance awareness and intelligence?
- **🛡️ Guardian**: Is this safe, ethical, and beneficial?

---

*Keep this reference handy! Bookmark for quick access to essential commands and guidelines.*

*Last updated: 2025-08-25*
