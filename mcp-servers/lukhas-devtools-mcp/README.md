# LUKHAS Development Tools MCP Server

**Model Context Protocol server for LUKHAS AI development utilities** - Provides Claude Desktop with comprehensive access to testing infrastructure, code analysis, T4 audit systems, and development tools.

## 🛠️ Development Infrastructure Access

This MCP server exposes **LUKHAS AI's complete development ecosystem** to Claude Desktop:

### **Testing Infrastructure (775 Tests)**
- **Comprehensive testing**: 6 categories including unit, integration, security, GDPR, performance, and contract tests
- **Wave C testing**: 121KB of phenomenological processing tests with memory persistence validation
- **Infrastructure stability**: Python crashes, SQLite threading issues, and import cycles resolved
- **Test safety**: Concurrent operations disabled for stability, threading segfaults fixed

### **Code Analysis & Quality Systems**
- **Ruff analysis**: 1,653 critical syntax errors eliminated, 36.3% system-wide error reduction
- **MyPy analysis**: 660 errors down from 749, focusing on None operations and type safety
- **Priority fixes**: symbolic_network.py (97.6% error reduction), brain_integration.py (88.4% reduction)
- **Lane system**: Perfect lane guard compliance with candidate/ vs lukhas/ separation

### **T4 Audit Framework**
- **Current phase**: STEPS_2 in progress (Block 5 of 6 completed)
- **Coverage improvement**: 15% (up from 1%, targeting 30-40%)
- **Surgical standards**: ≤20 lines per file, no API refactors, type safety priority
- **Quality target**: Sam Altman (scale), Dario Amodei (safety), Demis Hassabis (rigor) execution levels

## 🔧 Available Development Tools

### `test_infrastructure_status`
Complete overview of LUKHAS AI testing infrastructure including all 775 tests, Wave C phenomenological testing, stability improvements, and current execution health across consciousness modules.

### `code_analysis_status`
Comprehensive code analysis including:
- **Ruff error tracking**: Current counts, reduction achievements, priority file fixes
- **MyPy type analysis**: Error counts, None operations, type safety improvements
- **T4 audit progress**: Coverage metrics, surgical change compliance, lane separation
- **Quality improvements**: 36.3% system-wide error reduction documentation

### `t4_audit_status`
Detailed T4 audit framework status:
- **Current phase tracking**: STEPS_2 progress with block completion status
- **Coverage metrics**: Real-time improvement tracking (1% → 15% → 30-40% target)
- **Documentation map**: Links to all T4 audit documentation (STEPS_2, CLAUDE_ONLY_TASKS, etc.)
- **Standards compliance**: Surgical change validation, lane separation enforcement

### `development_utilities`
Complete development toolkit access:
- **Makefile targets**: 15+ commands for testing, fixing, formatting, and quality checks
- **T4 commit process**: Nightly autofix, policy control, TODO annotation systems
- **Analysis tools**: Functional analysis, drift audit, mass error elimination utilities
- **Testing utilities**: Comprehensive test runners, coverage analysis, validation tools

### `module_structure`
Explore LUKHAS AI's 692-module consciousness architecture:
- **Module hierarchy**: Navigate candidate/ (662 modules) vs lukhas/ (30 modules)
- **Lane system**: Development vs production code organization
- **Structure analysis**: Directory trees, file types, modification tracking
- **Consciousness mapping**: Distributed cognitive component organization

### `devtools_operation`
Execute sophisticated development operations:
- **`run_tests`**: Execute test suites with category filtering (unit/integration/security/performance/all)
- **`code_analysis`**: Perform analysis (ruff/mypy/coverage/dependencies/structure)
- **`audit_status`**: Check T4 audit phases (t4/steps_1/steps_2/claude_tasks)
- **`infrastructure_check`**: Validate system infrastructure and stability
- **`development_metrics`**: Gather comprehensive development velocity metrics

## 🚀 Setup for Claude Desktop

### Installation
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-devtools-mcp
npm install
npm run build
```

### Claude Desktop Configuration

Add to your Claude Desktop MCP configuration:

```json
{
  "clients": {
    "claude-desktop": {
      "servers": {
        "lukhas-devtools": {
          "command": "npm",
          "args": ["run", "start"],
          "cwd": "/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-devtools-mcp",
          "env": {
            "LUKHAS_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas"
          }
        }
      }
    }
  }
}
```

### Environment Variables
- `LUKHAS_ROOT` - Path to LUKHAS AI system (default: `/Users/agi_dev/LOCAL-REPOS/Lukhas`)

## 🛠️ Usage Examples

Once connected to Claude Desktop, access comprehensive development tools:

### **Testing Infrastructure**
```
Check the complete testing infrastructure status using test_infrastructure_status
Get Wave C testing details and stability improvements
```

### **Code Quality Analysis**
```
Get comprehensive code analysis using code_analysis_status
Review Ruff/MyPy error reductions and priority file improvements
```

### **T4 Audit Progress**
```
Check current T4 audit status using t4_audit_status
Review STEPS_2 progress and coverage improvements
```

### **Development Utilities**
```
Access all development utilities using development_utilities
Get Makefile targets, T4 commit process, and analysis tools
```

### **Module Structure Exploration**
```
Explore the root module structure using module_structure
Navigate specific paths: module_structure with module_path "candidate/core/"
Navigate consciousness modules: module_structure with module_path "consciousness/"
```

### **Development Operations**
```
Execute run_tests with test_category "integration"
Execute code_analysis with analysis_type "ruff"
Execute audit_status with audit_phase "steps_2"
Execute infrastructure_check to validate system stability
Execute development_metrics to gather velocity metrics
```

## 📊 Development Metrics Dashboard

### **Quality Achievements**
- **Error reduction**: 36.3% system-wide improvement
- **Critical fixes**: 1,653 syntax errors eliminated
- **Infrastructure**: Python crashes, SQLite threading, import cycles resolved
- **Test stability**: 775 tests with comprehensive categories

### **T4 Audit Progress**
- **Coverage**: 15% (up from 1%, target 30-40%)
- **Standards**: Surgical changes (≤20 lines per file)
- **Quality**: Sam Altman/Dario Amodei/Demis Hassabis execution level
- **Phase**: STEPS_2 Block 5 of 6 completed

### **Infrastructure Health** 
- **Consciousness modules**: 692 total (662 candidate + 30 lukhas)
- **Lane separation**: Perfect compliance (0 violations)
- **System stability**: All critical issues resolved
- **MCP readiness**: Full development capability achieved

## 🏗️ Architecture

```
lukhas-devtools-mcp/
├── src/
│   ├── server.ts    # MCP server with development tool handlers
│   └── devtools.ts  # Development utilities and analysis tools
├── scripts/
│   └── test.ts      # Development tools functionality tests
├── package.json     # Dependencies including fast-glob for file operations
├── tsconfig.json    # TypeScript configuration
└── README.md       # This documentation
```

## 🛠️ Development Integration

This MCP server provides **comprehensive development environment access** enabling Claude Desktop to:

### **Monitor Development Progress**
- Track T4 audit progress across multiple phases
- Monitor code quality improvements and error reduction
- Assess infrastructure stability and test execution health

### **Execute Development Operations**
- Run targeted test suites with category filtering
- Perform code analysis with multiple analysis types
- Check audit status across different phases
- Validate infrastructure and gather metrics

### **Navigate Consciousness Architecture**
- Explore 692-module distributed consciousness system
- Navigate lane system (candidate/ vs lukhas/) structure
- Access development utilities and analysis tools

**Revolutionary Development Access**: Claude Desktop can now directly interact with the complete LUKHAS AI development ecosystem - from testing infrastructure to T4 audit systems to consciousness module architecture - enabling sophisticated development assistance and quality monitoring.