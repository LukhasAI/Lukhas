# LUKHAS Module Schema System

A comprehensive, automated system for managing module metadata across the entire LUKHAS AI ecosystem. This system provides structured, machine-readable schemas for all modules, enabling better dependency management, automated validation, and system-wide observability.

## 🎯 Overview

### What We Built

- **113 Module Schemas**: Comprehensive metadata for all LUKHAS modules
- **Enhanced Framework**: Extended your original template with discovery patterns, quality metrics, and automation
- **Automated Generation**: AST-based tooling for schema generation from codebase analysis
- **Validation System**: JSON Schema validation with CI/CD integration
- **Discovery API**: Runtime module registry and search capabilities
- **Visualization Tools**: Interactive dependency graphs and architecture diagrams

### Key Metrics

| Metric | Value |
|--------|-------|
| **Total Modules** | 113 |
| **Modules by Lane** | candidate (29), lukhas (20), branding (22), matriz (6), products (9), tools (27) |
| **Architecture Layers** | foundational (3), infrastructure (6), application (103), interface (1) |
| **Schema Coverage** | 100% automated, requires manual review |
| **Validation Status** | 57/113 schemas valid (needs refinement) |

## 📋 Files and Structure

```
modules/
├── README.md                           # This documentation
├── module_schema_template.yaml         # Enhanced template framework
├── schema_validator.json              # JSON Schema validation rules
├── GENERATION_REPORT.md               # Automated generation report
├── candidate_*.yaml                   # Candidate lane modules (29)
├── lukhas_*.yaml                      # Production modules (20) 
├── branding_*.yaml                    # Branding modules (22)
├── matriz_*.yaml                      # MATRIZ modules (6)
├── products_*.yaml                    # Product modules (9)
└── tools_*.yaml                       # Tooling modules (27)
```

## 🛠 Tooling

### Core Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `module_schema_generator.py` | Generate schemas from codebase | `python tools/module_schema_generator.py .` |
| `module_schema_validator.py` | Validate schemas against rules | `python tools/module_schema_validator.py modules/schema_validator.json modules/` |
| `module_discovery_system.py` | Runtime module registry | `python tools/module_discovery_system.py --command list` |
| `module_dependency_visualizer.py` | Generate dependency graphs | `python tools/module_dependency_visualizer.py --format html` |

### CI/CD Integration

- **GitHub Actions**: `.github/workflows/module_schema_validation.yml`
- **Automated Validation**: Runs on every PR touching module schemas
- **Quality Gates**: Prevents invalid schemas from being merged

## 📊 Enhanced Schema Framework

Your original template has been enhanced with:

### New Sections Added

- **Discovery Patterns**: Import patterns, aliases, file patterns for automated discovery
- **Quality Metrics**: Code quality scores, technical debt ratios, complexity metrics
- **Performance Targets**: SLOs, latency targets, throughput requirements
- **Security Extensions**: Encryption, authentication, compliance tracking
- **Business Context**: Revenue impact, competitive advantage, regulatory requirements

### Key Improvements

1. **Machine Readable**: Full JSON Schema validation
2. **Automated Generation**: AST-based extraction from codebase
3. **Runtime Integration**: Dynamic module registry and discovery
4. **CI/CD Validation**: Automated quality gates
5. **Dependency Analysis**: Cross-module dependency tracking and validation

## 🔍 Usage Examples

### Validate All Schemas
```bash
python tools/module_schema_validator.py modules/schema_validator.json modules/
```

### Search for Modules
```bash
# List all infrastructure modules
python tools/module_discovery_system.py --command list --layer infrastructure

# Search by owner
python tools/module_discovery_system.py --command search --query "@Agent02"

# Get module dependencies
python tools/module_discovery_system.py --command deps --module candidate.memory
```

### Generate Visualizations
```bash
# Interactive HTML dependency graph
python tools/module_dependency_visualizer.py --format html

# Focus on specific module
python tools/module_dependency_visualizer.py --format mermaid --focus candidate.memory

# Architecture summary report
python tools/module_dependency_visualizer.py --format summary
```

## ⚠️ Current Status & Next Steps

### Validation Issues (Expected)

The current validation shows 57/113 schemas valid. Issues include:

1. **Version Format**: Need to convert `"1.0.0"` to `"v1.0.0"` format
2. **Lane Names**: Schema pattern needs to include `branding` and `matriz` lanes
3. **Missing Dependencies**: Many auto-detected dependencies don't exist as modules

### Immediate Actions Needed

#### 1. Schema Refinement (Priority: High)
```bash
# Fix version formats
find modules -name "*.yaml" -exec sed -i 's/version: "1\.0\.0"/version: "v1.0"/' {} \;

# Update JSON Schema to include all lanes
# Edit modules/schema_validator.json line 14:
# "pattern": "^(candidate|lukhas|products|tools|branding|matriz)\\.[a-z_][a-z0-9_]*$"
```

#### 2. Manual Review Process (Priority: High)
For each schema file:
- [ ] **Ownership**: Replace `@AutoGenerated` with actual maintainers
- [ ] **API Surface**: Document actual public APIs and contracts
- [ ] **Dependencies**: Verify and clean up dependency lists
- [ ] **SLOs**: Define realistic service level objectives
- [ ] **Risk Assessment**: Complete risk analysis with proper mitigations

#### 3. Integration (Priority: Medium)
- [ ] **Runtime Integration**: Integrate discovery system with existing services
- [ ] **Monitoring**: Connect schemas with observability systems
- [ ] **Documentation**: Link schemas to existing documentation

## 🚀 Advanced Features

### Module Discovery API

The discovery system provides:
- **Real-time Module Registry**: Dynamic loading of module information
- **Dependency Tracking**: Recursive dependency and dependent analysis
- **Health Monitoring**: Module health checks and status tracking
- **Deployment Planning**: Automatic deployment order calculation

### Dependency Visualization

Multiple output formats:
- **Interactive HTML**: Live, clickable dependency graphs
- **Mermaid Diagrams**: GitHub-compatible markdown diagrams
- **DOT Files**: Graphviz-compatible for advanced layouts
- **Architecture Reports**: Textual analysis and recommendations

### Quality Assurance

Automated validation includes:
- **Schema Compliance**: JSON Schema validation
- **Cross-Reference Checking**: Dependency consistency validation
- **Lane Isolation**: Ensures proper architectural boundaries
- **Semantic Validation**: Business rule enforcement

## 🎉 Success Metrics

This implementation provides:

✅ **Future-Proof Architecture**: Extensible schema system that grows with LUKHAS
✅ **Automated Maintenance**: Minimal manual effort required for updates  
✅ **Developer Experience**: Easy discovery and dependency management
✅ **Quality Assurance**: Automated validation prevents architectural drift
✅ **System Observability**: Clear visibility into module relationships
✅ **Deployment Safety**: Dependency-aware deployment ordering

## 📚 Schema Template Reference

Each module schema includes:

- **Identity**: Name, layer, status, tier classification
- **Discovery**: Import patterns, file patterns, entry points
- **Ownership**: Maintainer, lifecycle, review schedule
- **Contracts**: API surface, versions, compatibility guarantees
- **Dependencies**: Internal/external dependencies, coupling metrics
- **Runtime**: Processes, configuration, resource requirements  
- **Data & Events**: Schemas, event streams, storage patterns
- **Security**: Authentication, authorization, compliance requirements
- **Observability**: Logging, metrics, SLOs, alerting
- **Testing**: Coverage, test types, quality gates
- **Risk Management**: Risk assessment, change control, deprecation
- **Provenance**: Generation metadata, contributors, validation status

This system transforms LUKHAS from an undocumented collection of modules into a well-architected, observable, and manageable AI system with clear boundaries and responsibilities.