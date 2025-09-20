# LUKHAS AGI Project Architecture Analysis

## 5 Most Critical Architectural Domains

Based on directory analysis, Python package indicators, import patterns, file counts, and sizes, here are the 5 most critical domains:

### 1. **CANDIDATE** (Primary AGI Development)
- **Size**: 467MB, 2,877 Python files
- **Core Components**: `aka_qualia/` (consciousness core), `core/` (193 subdirs), `bio/`, `memory/`, `identity/`
- **Rationale**: Largest active development area with extensive Python packages, contains consciousness processing (`aka_qualia`), and shows heaviest cross-referencing in imports

### 2. **PRODUCTS** (Production Systems)
- **Size**: 193MB, 4,093 Python files  
- **Rationale**: Highest file count indicates mature, deployed systems; likely contains user-facing applications and enterprise solutions

### 3. **MATRIZ** (Core Data Processing Engine)
- **Size**: 632MB, 20 Python files
- **Rationale**: Largest storage footprint with minimal Python files suggests heavy data/model assets; functions as symbolic reasoning engine bridging biological patterns with quantum processing

### 4. **LUKHAS Core** (System Integration)
- **Size**: 1.9MB, 148 Python files
- **Rationale**: Central integration hub with extensive cross-references; symlinked as `core/` indicating system-critical role

### 5. **Consciousness/Memory/Identity** (Constellation Framework)
- **Combined footprint**: Multiple directories across candidate/, lukhas/, and root
- **Rationale**: Distributed across multiple locations indicating architectural importance; forms the consciousness trinity framework

## Hierarchical Architecture Mapping

### 🧠 **Core AGI Systems (Tier 1)**
```
candidate/
├── aka_qualia/          # Consciousness processing core
├── core/                # 193 subdirectories of core systems
├── consciousness/       # Consciousness architectures
├── memory/             # Memory management systems
├── identity/           # Identity and authentication
├── bio/                # Bio-inspired processing
└── governance/         # Ethics and compliance

lukhas/
├── consciousness/      # Core consciousness integration
├── memory/            # Memory system integration
├── identity/          # Identity management
└── core/              # Central system coordination

monitoring/
├── drift_manager.py    # Unified drift management (ethical/memory/identity)
├── __init__.py        # Monitoring module initialization
└── [prometheus configs] # Metrics and alerting
```

### 🔄 **Supporting Infrastructure (Tier 2)**
```
products/               # Production deployments (4,093 files)
├── enterprise/        # Enterprise solutions
├── intelligence/      # Intelligence services
└── experience/        # User experience systems

api/                   # API gateway and interfaces
orchestration/         # Workflow orchestration
ai_orchestration/      # AI-specific orchestration
```

### 🧬 **Research/Experimental Areas (Tier 3)**
```
matriz/                # Symbolic reasoning engine (632MB data)
bio/                   # Bio-inspired algorithms
consciousness/         # Consciousness research
quantum_bio_consciousness/ # Quantum-bio hybrid systems
dream/                 # Dream state processing
emotion/               # Emotion processing systems
```

### 📊 **Documentation/Reporting Areas (Tier 4)**
```
docs/                  # Comprehensive documentation
reports/               # Analysis and audit reports  
tools/                 # Development and analysis tools
tests/                 # Test suites (tier1 markers visible)
audit/                 # Security and compliance audits
```

### 🚀 **Deployment/Operations (Tier 5)**
```
deployment/            # Deployment configurations
ops/                   # Operations and monitoring
ci/                    # Continuous integration
docker/                # Containerization
environments/          # Environment configurations
```

## Key Architectural Insights

1. **Constellation Framework**: The consciousness/memory/identity triad appears distributed across multiple domains, indicating a foundational architectural pattern

2. **Candidate-Centric Development**: The `candidate/` directory serves as the primary development workspace with the highest density of active AGI components

3. **MATRIZ as Data Engine**: Despite few Python files, MATRIZ's 632MB footprint suggests it houses large data models or symbolic processing assets

4. **Production Scale**: Products directory's 4,093 files indicates mature, deployed systems ready for enterprise use

5. **Bio-Quantum Fusion**: Multiple bio and quantum directories suggest hybrid approaches to consciousness processing

## Drift Pipeline Integration

### Unified Drift Management
The `monitoring/drift_manager.py` module provides centralized drift calculation and monitoring:

- **Drift Types**: Ethical, Memory, Identity, and Unified (weighted aggregate)
- **Symbol Attribution**: Identifies top contributing symbols for root cause analysis
- **Integration Points**:
  - `IntegrityProbe` consumes drift scores and triggers alerts
  - Feature-flagged with `LUKHAS_EXPERIMENTAL=1`
  - Prometheus metrics for monitoring (p95 latency targets)
- **Thresholds**:
  - Warning: 0.10
  - Critical: 0.15 (Guardian System standard)
- **Autonomous Repair**: TraceRepairEngine integration for closed-loop correction
- **Telemetry**: Full Prometheus metrics for monitoring and alerting

### Reading top_symbols for Triage
Symbol format: `{domain}.{feature}` (e.g., `ethical.compliance`, `memory.fold_stability`)
Priority: First symbol = highest contributor to drift

## Analysis Methodology

- **Directory Structure**: Mapped 213 top-level directories and subdirectories
- **Python Packages**: Identified 50+ `__init__.py` files indicating formal package structure
- **Import Analysis**: Cross-referenced 33 files with core domain imports
- **Size Analysis**: Measured directory footprints and file counts
- **Architecture JSON**: Referenced LUKHAS_ARCHITECTURE_MASTER.json for tier classifications

*Generated: 2025-09-12*
*Updated: 2025-09-18 - Added drift pipeline integration*