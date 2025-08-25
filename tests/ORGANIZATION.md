# Tests Directory Organization

**Consolidated Test Structure for LUKHAS AI**

## 📁 **Directory Structure**

```
tests/
├── ORGANIZATION.md          # This file - organization guide
├── README.md               # Main test documentation  
├── __init__.py            # Python package initialization
├── conftest.py            # Pytest configuration
├── data/                  # Test data files (consolidated from root test_data/)
│   └── tokens.json        # Token test data
├── metadata/              # Test execution metadata (consolidated from root test_metadata/)
│   ├── baseline_test_*.json      # Baseline test results
│   ├── governance_test_*.json    # Governance test results
│   ├── safety_test_*.json        # Safety test results
│   ├── executive_summary_*.json  # Executive summaries
│   ├── investor_report_*.json    # Investor reports
│   └── test_*.txt                # Test discovery and mapping
├── results/               # Test results and reports (consolidated from root test_results/)
│   ├── *.md               # Test summary reports
│   ├── *.json             # JSON test results
│   ├── *.html             # HTML test reports
│   └── quick_baseline/    # Baseline test results
├── api/                   # API testing
├── branding/              # Brand system tests
├── bridge/                # External API bridge tests
├── canary/                # Canary deployment tests
├── critical_path/         # Critical system flow tests
├── e2e/                   # End-to-end testing
├── elite/                 # Advanced/edge case testing
├── emotion/               # Emotion system tests
├── governance/            # Governance system tests
├── identity/              # Identity & authentication tests
├── integration/           # Integration testing
├── lukhas/                # Core LUKHAS system tests
├── orchestration/         # Orchestration system tests
├── performance/           # Performance & benchmarking
├── qi/                    # QI system tests
├── reasoning/             # Reasoning system tests
├── security/              # Security testing
├── serve/                 # Service layer tests
├── tools/                 # Test analysis and utilities
├── unit/                  # Unit tests
└── vivox/                 # VIVOX system tests
```

## 🔄 **Consolidation Changes (August 2024)**

### **Directories Consolidated**
- ✅ **`test_data/`** → **`tests/data/`**
- ✅ **`test_metadata/`** → **`tests/metadata/`** 
- ✅ **`test_results/`** → **`tests/results/`**

### **Benefits of Consolidation**
1. **Single Test Location**: All testing materials in one organized hierarchy
2. **Clear Separation**: Data, metadata, and results properly categorized
3. **Better Navigation**: Consistent structure for test discovery
4. **Reduced Root Clutter**: Cleaner workspace organization

## 📊 **Test Categories**

### **Core System Tests**
- **Unit Tests**: Component-level testing in `unit/`
- **Integration Tests**: Cross-system testing in `integration/`
- **Critical Path**: Essential system flows in `critical_path/`

### **Specialized Testing**
- **Security**: Red team and vulnerability testing in `security/`
- **Performance**: Benchmarks and stress tests in `performance/`
- **Elite**: Edge cases and chaos engineering in `elite/`
- **E2E**: Full user workflow testing in `e2e/`

### **System-Specific Tests**
- **Identity**: Authentication and ΛID system tests
- **Governance**: Guardian system and compliance tests
- **VIVOX**: VIVOX consciousness system tests
- **Emotion**: Emotional intelligence system tests

## 🛠️ **Test Data Management**

### **Test Data (`tests/data/`)**
- Static test data files
- Configuration fixtures
- Mock data for testing

### **Test Metadata (`tests/metadata/`)**
- Test execution tracking
- Baseline measurements
- Governance compliance records
- Safety validation results

### **Test Results (`tests/results/`)**
- Detailed test reports
- Performance benchmarks
- Coverage analysis
- Stress test outcomes

## 📋 **Running Tests**

### **Main Test Commands**
```bash
# Run all tests
pytest tests/

# Run specific categories
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
pytest tests/security/       # Security tests

# Run with coverage
pytest tests/ --cov=lukhas --cov-report=html

# Quick validation
./tests/run_valid_tests.sh
```

### **Test Discovery**
- All test files follow pattern: `test_*.py`
- Test metadata tracked in `tests/metadata/`
- Results archived in `tests/results/`

## 📖 **Related Documentation**
- **Main Tests README**: `tests/README.md`
- **Test Analysis**: Various `.md` files in `tests/results/`
- **Coverage Reports**: Generated in `tests/results/`

---

**Tests Directory - Consolidated and Organized Structure**

*All LUKHAS AI testing materials in a single, well-organized hierarchy*

*Last updated: August 2024 - Post-consolidation*