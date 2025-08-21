# CLAUDE.md - Guardian Systems Collection

This file provides guidance to Claude Code when working with the Guardian Systems Collection.

## 🛡️ Collection Overview

**Purpose**: Consolidated collection of Guardian and Healthcare systems for LUKHAS AI  
**Total Systems**: 9 complete implementations (5 Guardian + 4 Healthcare)  
**Trinity Alignment**: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian  
**Status**: Awaiting consolidation and integration

## 📂 Directory Structure

```
Guardian_Systems_Collection/
├── 01_Enhanced_Guardian_System/      # ⭐ Most comprehensive (882 lines)
├── 02_LUKHAS_Guardian_Dashboard/     # ⭐ Best visualization (1,079 lines)
├── 03_Lambda_Guardian_Core/          # Lambda-branded implementation
├── 04_Guardian_Reflector_Ethics/     # Advanced ethical reasoning
├── 05_Prototype_Lambda_Guardian/     # Prototype implementation
└── 06_Healthcare_Systems/           
    ├── Enhanced_Guardian_Medical/    # Emergency medical response
    ├── Health_Advisor_Plugin/        # Provider integration
    ├── LUKHAS_Health_Systems/        # AI health monitoring
    └── Bio_Health_Integration/       # Biological patterns
```

## 🎯 Consolidation Goals

### Primary Objectives
1. **Reduce Redundancy**: Merge overlapping Guardian implementations
2. **Unified Architecture**: Create single coherent Guardian system
3. **Preserve Best Features**: Keep unique capabilities from each system
4. **Simplify Integration**: Single entry point for Guardian functionality
5. **Maintain Compliance**: Preserve all safety and ethical features

### Key Systems to Consolidate

**Guardian Core Systems** (Priority 1):
- Enhanced Guardian System (most comprehensive)
- LUKHAS Guardian Dashboard (best visualization)
- Lambda Guardian Core (Lambda branding)
- Guardian Reflector Ethics (ethical reasoning)

**Healthcare Systems** (Priority 2):
- Enhanced Guardian Medical (emergency response)
- Health Advisor Plugin (modular architecture)
- LUKHAS Health Systems (AI health monitoring)

## 🔧 Technical Standards

### Code Quality Requirements
- Python 3.9+ compatibility
- Type hints for all functions
- Docstrings following Google style
- Async/await for I/O operations
- Error handling with specific exceptions
- Logging using standard Python logging

### Architecture Patterns
- **Core Engine**: Single Guardian engine with plugin architecture
- **Module System**: Loadable modules for specific capabilities
- **Event Bus**: Unified event system for cross-module communication
- **Config Management**: YAML-based configuration with validation
- **API Layer**: FastAPI endpoints for external integration

### Naming Conventions
- Classes: `PascalCase` (e.g., `GuardianEngine`)
- Functions: `snake_case` (e.g., `monitor_threats`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DRIFT_THRESHOLD`)
- Private methods: `_leading_underscore`
- Guardian-specific: `guardian_` prefix for public APIs

## 📊 Consolidation Strategy

### Phase 1: Analysis (Current)
- Audit all Guardian implementations
- Identify common patterns and unique features
- Map dependencies and integration points
- Document redundancies and conflicts

### Phase 2: Design
- Create unified Guardian architecture
- Design plugin system for specialized features
- Plan migration path for existing code
- Define consolidated API surface

### Phase 3: Implementation
- Build core Guardian engine
- Migrate features as plugins
- Integrate healthcare systems
- Create unified dashboard

### Phase 4: Testing & Validation
- Unit tests for all components
- Integration testing
- Security audit
- Performance benchmarking

## 🚨 Critical Features to Preserve

### From Enhanced Guardian System
- Comprehensive threat monitoring
- Consent management system
- Medical assistance integration
- Modular component architecture

### From LUKHAS Guardian Dashboard
- Real-time symbolic threat visualization
- Emergency state management
- Trinity Framework integration
- Advanced UI components

### From Guardian Reflector Ethics
- Multi-framework moral reasoning
- Ethical reflection capabilities
- Virtue/deontological/consequentialist ethics
- Moral decision logging

### From Healthcare Systems
- Emergency medical protocols
- Healthcare provider integration
- Medical document OCR
- Bio-pattern recognition

## 🔐 Security & Compliance

### Required Compliance
- HIPAA for healthcare data
- GDPR for personal information
- AI safety standards
- Emergency response protocols

### Security Measures
- Encryption for sensitive data
- Audit logging for all actions
- Access control and authentication
- Threat monitoring and response

## 📈 Performance Targets

- **Response Time**: <100ms for threat detection
- **Dashboard Update**: <250ms refresh rate
- **Emergency Response**: <50ms activation
- **Memory Usage**: <500MB base footprint
- **CPU Usage**: <10% idle, <50% active

## 🔄 Integration Points

### With LUKHAS Core
- Trinity Framework alignment
- GLYPH communication system
- Memory fold integration
- Consciousness module hooks

### External Services
- Healthcare provider APIs
- Emergency services integration
- Monitoring systems
- Audit trail systems

## 📝 Documentation Requirements

### For Each Consolidated Module
- README with usage examples
- API documentation
- Configuration guide
- Integration examples
- Test coverage report

### Overall System
- Architecture overview
- Deployment guide
- Security documentation
- Performance tuning guide
- Migration guide from old systems

## ⚠️ Important Notes

### DO NOT
- Remove safety features during consolidation
- Compromise ethical reasoning capabilities
- Reduce emergency response functionality
- Skip security validations
- Ignore HIPAA/GDPR compliance

### ALWAYS
- Preserve Trinity Framework alignment
- Maintain backward compatibility where possible
- Document breaking changes
- Test emergency protocols
- Validate ethical decisions

## 🎯 Success Metrics

### Consolidation Success
- ✅ Single unified Guardian system
- ✅ All unique features preserved
- ✅ Reduced code duplication by >60%
- ✅ Improved performance metrics
- ✅ Comprehensive test coverage >85%
- ✅ Full documentation coverage
- ✅ Successful integration with LUKHAS core

## 🚀 Quick Start Commands

```bash
# Run analysis on current systems
python analyze_guardians.py

# Test consolidated Guardian
python -m pytest tests/guardian/

# Launch Guardian dashboard
python guardian_dashboard.py

# Run security audit
python security_audit.py

# Performance benchmark
python benchmark_guardian.py
```

## 📞 Support & Resources

- **Main LUKHAS Docs**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/README.md`
- **Trinity Framework**: See `AGENTS.md` for alignment details
- **Guardian Governance**: `governance/` directory
- **Healthcare Compliance**: `docs/healthcare/` directory

---

*Guardian Systems Collection - Defensive AI Safety & Healthcare*  
*Trinity Compliant: ⚛️🧠🛡️*  
*Last Updated: August 21, 2025*