# 📁 LUKHAS AI File Delivery Matrix

**For Agents, Developers, and Automated Systems**

This matrix defines exactly where new files should be placed in the LUKHAS AI project structure. **Always consult this matrix before creating new files or directories.**

---

## 🎯 **PRIMARY DELIVERY DESTINATIONS**

### **Configuration Files**
| File Type           | Destination       | Examples                              |
| ------------------- | ----------------- | ------------------------------------- |
| Environment configs | `config/env/`     | `.env.production`, `.env.staging`     |
| Tool configurations | `config/tools/`   | `.eslintrc`, `mypy.ini`, `black.toml` |
| Project settings    | `config/project/` | `lukhas_config.yaml`, `settings.json` |
| Node.js configs     | `config/node/`    | `package.json`, `tsconfig.json`       |

### **Deployment & Infrastructure**
| File Type            | Destination             | Examples                               |
| -------------------- | ----------------------- | -------------------------------------- |
| Deployment scripts   | `deployment/scripts/`   | `deploy-production.sh`, `migrate.sh`   |
| Docker files         | `deployment/docker/`    | `Dockerfile`, `docker-compose.yml`     |
| Cloud configs        | `deployment/cloud/`     | `kubernetes.yaml`, `azure-*.yml`       |
| Platform deployments | `deployment/platforms/` | Consciousness platform, dream commerce |

### **Testing**
| File Type             | Destination            | Examples                                     |
| --------------------- | ---------------------- | -------------------------------------------- |
| Unit tests            | `tests/unit/[module]/` | `test_consciousness.py`                      |
| Integration tests     | `tests/integration/`   | `test_api_flow.py`                           |
| End-to-end tests      | `tests/e2e/`           | `test_user_workflow.py`                      |
| Performance tests     | `tests/performance/`   | `test_load.py`, `benchmark.py`               |
| Test enhancements     | `tests/enhancements/`  | `self-healing-engine.py`                     |
| Domain-specific tests | `tests/[domain]/`      | `tests/candidate/`, `tests/lambda_products/` |

### **Reports & Analytics**
| File Type        | Destination           | Examples                                        |
| ---------------- | --------------------- | ----------------------------------------------- |
| API reports      | `reports/api/`        | `api_test_results.json`                         |
| Security reports | `reports/security/`   | `security_audit.json`, `vulnerability_scan.log` |
| Deployment logs  | `reports/deployment/` | `deploy_20250825.log`                           |
| System analysis  | `reports/analysis/`   | `performance_analysis.json`                     |

### **Media & Assets**
| File Type            | Destination        | Examples                                 |
| -------------------- | ------------------ | ---------------------------------------- |
| Dream images         | `assets/dreams/`   | `dream_001.png`, `generated_art.jpg`     |
| UI assets            | `assets/ui/`       | `icons/`, `logos/`, `components/`        |
| Documentation images | `assets/docs/`     | `architecture_diagram.png`               |
| Brand assets         | `branding/assets/` | Official logos, Trinity Framework assets |

### **Development Resources**
| File Type              | Destination    | Examples                                       |
| ---------------------- | -------------- | ---------------------------------------------- |
| Demos                  | `demos/`       | `genesis_transmission/`, `openai_integration/` |
| Development tools      | `tools/`       | `analyzers/`, `generators/`, `validators/`     |
| Scripts                | `scripts/`     | Utility scripts, automation helpers            |
| Performance monitoring | `performance/` | `optimization_configs/`, `analysis_tools/`     |

---

## 🚨 **DEPRECATED PATHS - DO NOT USE**

### **❌ OLD DIRECTORIES (Consolidated)**
| Old Path            | New Path                | Status         |
| ------------------- | ----------------------- | -------------- |
| `deployments/`      | `deployment/platforms/` | CONSOLIDATED ✅ |
| `demo_suite/`       | `demos/`                | CONSOLIDATED ✅ |
| `perf/`             | `performance/scripts/`  | CONSOLIDATED ✅ |
| `security-reports/` | `reports/security/`     | CONSOLIDATED ✅ |
| `node_configs/`     | `config/node/`          | CONSOLIDATED ✅ |
| `dream_images/`     | `assets/dreams/`        | CONSOLIDATED ✅ |
| `meta_dashboard/`   | `dashboard/meta/`       | CONSOLIDATED ✅ |

---

## 🤖 **FOR AUTOMATED SYSTEMS & AGENTS**

### **Script Integration Guidelines**

#### **Dream Image Generation**
```python
# CORRECT: New dream images go to assets/dreams/
DREAM_OUTPUT_DIR = "assets/dreams/"
dream_file = f"{DREAM_OUTPUT_DIR}dream_{timestamp}.png"
```

#### **Test Result Storage**
```python
# CORRECT: Test results go to reports/
TEST_RESULTS_DIR = "reports/api/"
result_file = f"{TEST_RESULTS_DIR}api_test_{date}.json"
```

#### **Configuration Updates**
```bash
# CORRECT: Environment configs go to config/env/
echo "NEW_VAR=value" >> config/env/.env.production
```

#### **Performance Monitoring**
```python
# CORRECT: Performance data goes to performance/
PERF_DATA_DIR = "performance/benchmarks/"
benchmark_file = f"{PERF_DATA_DIR}benchmark_{module}.json"
```

### **Path Constants for Scripts**
```python
# Use these constants in all LUKHAS AI scripts
PATHS = {
    'config': {
        'env': 'config/env/',
        'tools': 'config/tools/',
        'project': 'config/project/',
        'node': 'config/node/'
    },
    'deployment': {
        'scripts': 'deployment/scripts/',
        'docker': 'deployment/docker/',
        'cloud': 'deployment/cloud/',
        'platforms': 'deployment/platforms/'
    },
    'assets': {
        'dreams': 'assets/dreams/',
        'ui': 'assets/ui/',
        'docs': 'assets/docs/'
    },
    'reports': {
        'api': 'reports/api/',
        'security': 'reports/security/',
        'deployment': 'reports/deployment/',
        'analysis': 'reports/analysis/'
    },
    'tests': {
        'unit': 'tests/unit/',
        'integration': 'tests/integration/',
        'e2e': 'tests/e2e/',
        'performance': 'tests/performance/',
        'enhancements': 'tests/enhancements/'
    }
}
```

---

## 🎯 **DECISION FLOWCHART**

```
New File Created
       ↓
Is it a configuration file?
   YES → config/[env|tools|project|node]/
   NO → Continue
       ↓
Is it for deployment/infrastructure?
   YES → deployment/[scripts|docker|cloud|platforms]/
   NO → Continue
       ↓
Is it a test file?
   YES → tests/[unit|integration|e2e|performance|domain]/
   NO → Continue
       ↓
Is it a report or log?
   YES → reports/[api|security|deployment|analysis]/
   NO → Continue
       ↓
Is it media/assets?
   YES → assets/[dreams|ui|docs]/
   NO → Continue
       ↓
Is it a demo or tool?
   YES → demos/ or tools/
   NO → Check with team lead
```

---

## 📝 **ENFORCEMENT RULES**

### **For Pull Requests**
- ✅ All new files must follow this matrix
- ✅ No files should be created in deprecated paths
- ✅ Scripts must use the path constants defined above
- ✅ Update this matrix when adding new categories

### **For CI/CD Systems**
- ✅ Automated systems must validate file placement
- ✅ Build scripts should fail if deprecated paths are used
- ✅ Generated files must go to appropriate destinations

### **For Development Teams**
- ✅ Consult this matrix before creating new directories
- ✅ Update scripts when changing file locations
- ✅ Document new file categories in this matrix

---

**🧠 Remember: A well-organized project is a scalable project. Following this matrix ensures LUKHAS AI maintains enterprise-grade organization standards.**

---

*Last updated: August 25, 2025 - Post Major Consolidation*
*Version: 1.0 - Enterprise Organization Standard*
