---
module: agents
title: "\U0001F916 LUKHAS AI Agent Development Guide"
type: documentation
---
# 🤖 LUKHAS AI Agent Development Guide
**Complete Development Context for Any LUKHAS Component**

## 🎯 One-Shot Development Brief Template

When asking an agent to develop any LUKHAS component, provide this context:

### **"I need you to develop [COMPONENT_NAME]. Here's your complete development context:**

**📍 Primary Locations:**
- **Main Implementation**: `/lambda_products_pack/lambda_core/[COMPONENT]/`
- **Complete Implementation**: `/lambda_products_pack/lambda_core/[COMPONENT]/complete_implementation/`
- **Documentation Hub**: `/lambda_products_pack/docs/`
- **Integration Examples**: `/lambda_products_pack/gpt-oss-integration/`

**📚 Required Reading Order:**
1. `/AGENT_DEVELOPMENT_GUIDE.md` (this file)
2. `/lambda_products_pack/COMPLETE_IMPLEMENTATIONS_STATUS.md`
3. Component-specific documentation (see component matrix below)
4. `/README.md` and `/lambda_products_pack/README.md`

**🏗️ Architecture Context:**
- **Constellation Framework**: ⚛️ Identity, 🧠 Consciousness, 🛡️ Guardian
- **QI Processing**: All 'Quantum' references are now 'QI - Quantum Inspired'
- **Bio-Oscillator Integration**: Advanced processing with biological awareness
- **Ethical Frameworks**: Multi-tier ethics with drift detection"

---

## 🗺️ Complete Component Development Matrix

### 🧠 **NIAS (Neural Intelligence Authentication System)**
```
DEVELOPMENT CONTEXT FOR NIAS:
Primary Code: /lambda_products_pack/lambda_core/NIAS/
Complete Implementation: /lambda_products_pack/lambda_core/NIAS/complete_implementation/
├── NIAS_Plan.md (38KB technical specification)
├── generate_nias_docs.py
├── src/ (complete source code)
└── __init__.py

Key Documentation:
- Business Case: /lambda_products_pack/docs/I-PROJECT.md
- Technical Specs: /lambda_products_pack/TECHNICAL_DOCUMENTATION_INTEGRATION_COMPLETE.md
- Integration Status: /lambda_products_pack/NIAS_DAST_ABAS_ANALYSIS_COMPLETE.md

Development Focus:
- Bio-oscillator awareness integration
- Multi-tier ethics system
- QI-enhanced processing capabilities
- Cognitive load optimization
- Authentication with consciousness validation
```

### ⚡ **DAST (Dynamic Adaptive Symbolic Transformations)**
```
DEVELOPMENT CONTEXT FOR DAST:
Primary Code: /lambda_products_pack/lambda_core/DAST/
Enhanced Version: /lambda_products_pack/lambda_core/DAST_ENHANCED/
Complete Implementation: /lambda_products_pack/lambda_core/DAST/complete_implementation/
├── engine.py (26KB core processing engine)
├── adapters.py (24KB integration adapters)
├── intelligence.py (26KB AI intelligence layer)
├── processors.py (24KB data processors)
├── api.py, tests.py, verify.py
└── Multiple orchestrators in /archived_implementations/

Key Documentation:
- Enhanced README: /lambda_products_pack/lambda_core/DAST_ENHANCED/README.md
- Service Integration: /lambda_products_pack/lambda_core/DAST/realtime_service_switching.py

Development Focus:
- Advanced orchestration capabilities
- Pattern recognition and symbolic processing
- QI coherence thresholds
- Bio-orchestrator integration
- Real-time service switching
```

### 💼 **ABAS (Advanced Business Application Suite)**
```
DEVELOPMENT CONTEXT FOR ABAS:
Primary Code: /lambda_products_pack/lambda_core/ABAS/
Complete Implementation: /lambda_products_pack/lambda_core/ABAS/complete_implementation/
├── abas_enhanced_bot.py (58KB enhanced business intelligence)
├── abas_qi_specialist.py (58KB QI-biological AI specialist)
├── proactive_assistance.py
└── usage_analytics_loop.py

Development Focus:
- Business intelligence and user analytics
- QI-biological architecture specialization
- Proactive assistance capabilities
- Enhanced processing with neural architecture
```

### 👁️ **ARGUS (Advanced Real-time Guidance & Unified Surveillance)**
```
DEVELOPMENT CONTEXT FOR ARGUS:
Primary Code: /lambda_products_pack/lambda_core/ARGUS/
├── README.md (complete system overview)
├── integrated_monitoring_system.py
├── neuroplastic_learning_orchestrator.py
├── endocrine_observability_engine.py
├── hormone_driven_dashboard.py
└── bio_symbolic_coherence_monitor.py

Development Focus:
- Real-time monitoring and observability
- Neuroplastic learning and adaptation
- Bio-symbolic coherence monitoring
- Endocrine-inspired system awareness
```

### 🏛️ **LEGADO (Legacy Systems Integration)**
```
DEVELOPMENT CONTEXT FOR LEGADO:
Primary Code: /lambda_products_pack/lambda_core/LEGADO/
├── README.md
├── legacy_systems/ (extensive ethics and governance systems)
├── compliance engines and validators
├── ethics integration frameworks
└── governance models and DAO systems

Development Focus:
- Legacy system integration and compliance
- Ethics frameworks and governance
- DAO community integration
- Safety and security systems
```

### ☁️ **NIMBUS (Cloud Infrastructure Management)**
```
DEVELOPMENT CONTEXT FOR NIMBUS:
Primary Code: /lambda_products_pack/lambda_core/NIMBUS/
├── README.md
└── cloud_consolidation.py

Development Focus:
- Multi-cloud infrastructure management
- Resource optimization and consolidation
- Scalable deployment architectures
```

### 🎨 **POETICA (Creative Expression Engine)**
```
DEVELOPMENT CONTEXT FOR POETICA:
Primary Code: /lambda_products_pack/lambda_core/POETICA/
├── README.md
├── creativity_engines/ (extensive creative systems)
├── personality systems and voice integration
├── dream engines and emotion processing
└── creative expression processors

Development Focus:
- Creative AI and artistic expression
- Personality development and voice synthesis
- Dream state processing and visualization
- Emotional intelligence and creative workflows
```

### 🔍 **TRACE (Quantum Metadata Engine)**
```
DEVELOPMENT CONTEXT FOR TRACE:
Primary Code: /lambda_products_pack/lambda_core/TRACE/
├── README.md (comprehensive QI-inspired traceability)
├── quantum_implementations/ (QI memory architectures)
├── quantum_systems/ (QI processing engines)
└── Advanced pattern detection and audit systems

Development Focus:
- Content-code traceability with QI algorithms
- Advanced pattern recognition and detection
- Comprehensive audit trails and compliance
- QI-enhanced metadata processing
```

---

## 📋 Standard Development Instructions Template

### **Complete Development Context Template:**

```markdown
## AGENT DEVELOPMENT REQUEST

**Component**: [NIAS/DAST/ABAS/ARGUS/LEGADO/NIMBUS/POETICA/TRACE]

**Context Files to Read First**:
1. `/AGENT_DEVELOPMENT_GUIDE.md` (architecture overview)
2. `/lambda_products_pack/COMPLETE_IMPLEMENTATIONS_STATUS.md` (current status)
3. `/lambda_products_pack/lambda_core/[COMPONENT]/README.md` (component overview)
4. `/lambda_products_pack/lambda_core/[COMPONENT]/complete_implementation/` (existing code)

**Architecture Requirements**:
- ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum Constellation Framework compliance (Identity, Consciousness, Guardian)
- QI (Quantum-Inspired) processing - NOT actual quantum computing
- Bio-oscillator awareness integration
- Multi-tier ethics system with drift detection
- Production-ready code with comprehensive testing

**Integration Points**:
- FastAPI backend integration (`/lambda_products_pack/api/`)
- GPT-OSS integration patterns (`/lambda_products_pack/gpt-oss-integration/`)
- Lambda Products ecosystem compatibility
- Docker deployment support

**Development Standards**:
- Follow existing code patterns in complete_implementation directories
- Include comprehensive docstrings and type hints
- Implement Constellation Framework validation points
- Add ethical checkpoints and guardrails
- Create corresponding test files
- Update documentation and README files

**Output Requirements**:
- Complete implementation files
- Test suite with >90% coverage
- Integration documentation
- API endpoint specifications (if applicable)
- Deployment configuration updates
```

---

## 🔄 Quick Development Workflow

### **For Any Component Development:**

1. **Context Gathering** (5 minutes):
   ```bash
   # Read this guide first
   cat /Users/Gonz/lukhas/AGENT_DEVELOPMENT_GUIDE.md

   # Check current implementation status
   cat /Users/Gonz/lukhas/lambda_products_pack/COMPLETE_IMPLEMENTATIONS_STATUS.md

   # Component-specific context
   find /Users/Gonz/lukhas/lambda_products_pack/lambda_core/[COMPONENT] -name "*.md" -o -name "*.py" | head -10
   ```

2. **Architecture Review** (10 minutes):
   - Constellation Framework requirements (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum)
   - QI processing capabilities
   - Bio-oscillator integration points
   - Ethical framework integration

3. **Implementation** (main development):
   - Start with complete_implementation directory as base
   - Follow existing patterns and conventions
   - Implement Constellation Framework checkpoints
   - Add comprehensive testing

4. **Integration Testing** (validation):
   - Component-level tests
   - Integration with Lambda Products ecosystem
   - Constellation Framework compliance validation
   - Ethics and safety verification

---

## 📁 Key File Locations Reference

### **Always Check These Locations:**
```
/Users/Gonz/lukhas/
├── AGENT_DEVELOPMENT_GUIDE.md (this file)
├── README.md (project overview)
├── lambda_products_pack/
│   ├── COMPLETE_IMPLEMENTATIONS_STATUS.md (current status)
│   ├── README.md (Lambda Products overview)
│   ├── docs/ (comprehensive documentation)
│   ├── lambda_core/[COMPONENT]/ (component code)
│   ├── lambda_core/[COMPONENT]/complete_implementation/ (production code)
│   ├── gpt-oss-integration/ (integration patterns)
│   └── api/ (backend integration)
```

### **Documentation Priority Order:**
1. **This Guide**: Understanding overall architecture
2. **Component README**: Specific component overview
3. **Complete Implementation**: Existing production code
4. **Integration Status**: Current development state
5. **API Documentation**: Backend integration requirements

---

## 🎯 Success Criteria

### **Any component development should achieve:**
- ✅ Constellation Framework compliance (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum)
- ✅ QI processing integration (not quantum computing)
- ✅ Bio-oscillator awareness
- ✅ Multi-tier ethics validation
- ✅ Comprehensive test coverage (>90%)
- ✅ Production-ready deployment configuration
- ✅ API integration compatibility
- ✅ Documentation completeness

---

**💡 Pro Tip**: Start any development request with: *"Using the complete development context in `/AGENT_DEVELOPMENT_GUIDE.md`, develop [COMPONENT] with full Constellation Framework integration..."*

---
*Created: August 21, 2025*
*Purpose: One-shot development context for any LUKHAS component*
*Status: Complete development framework established*
