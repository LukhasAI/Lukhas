# LUKHAS  Documentation Index

Welcome to the LUKHAS  documentation. This index provides quick access to all major documentation resources.

## 📚 Core Documentation

### [Architecture Documentation](./ARCHITECTURE.md)
Comprehensive system architecture guide covering:
- System overview and principles
- Core component architecture
- Module interactions and data flow
- Security architecture
- Performance and scalability patterns
- Development guidelines

### [API Reference](./API_REFERENCE.md)
Complete API documentation including:
- RESTful endpoints for all modules
- Authentication and authorization
- GLYPH token format specification
- WebSocket streaming APIs
- Error handling and rate limiting
- SDK usage examples

### [Deployment Guide](./DEPLOYMENT_GUIDE.md)
Step-by-step deployment instructions:
- Development environment setup
- Docker and Docker Compose configurations
- Kubernetes deployment with Helm
- Production best practices
- Monitoring and observability
- Disaster recovery procedures

## 📊 Visual Documentation

### [Architecture Diagrams](./diagrams/ARCHITECTURE_DIAGRAM.md)
Mermaid-based visual representations:
- System architecture overview
- Data flow sequences
- Module interaction maps
- Security layers
- Deployment topology
- State management flows

## 📈 Reports and Analysis

### [Module Status Reports](./reports/status/)
- [Operational Status Report](./reports/status/_OPERATIONAL_STATUS_REPORT.md)
- [Functional Analysis](./reports/status/_FUNCTIONAL_STATUS_REPORT.md)
- [Import Fix Status](./reports/status/_IMPORT_FIX_STATUS_REPORT.md)

### [Analysis Reports](./reports/analysis/)
- [System Connectivity Analysis](./reports/analysis/_SYSTEM_CONNECTIVITY_REPORT.json)
- [Import Analysis](./reports/analysis/_ACTIVE_IMPORT_ANALYSIS_REPORT.json)
- [Module Dependencies](./reports/analysis/_MODULE_DEPENDENCIES_REPORT.json)

## 🚀 Quick Start Guides

### For Developers
1. Read the [README](../README.md) for project overview
2. Follow [Development Deployment](./DEPLOYMENT_GUIDE.md#development-deployment)
3. Review [API Reference](./API_REFERENCE.md) for integration
4. Check [Architecture](./ARCHITECTURE.md#development-guidelines) for coding standards

### For DevOps
1. Start with [Deployment Guide](./DEPLOYMENT_GUIDE.md)
2. Review [Architecture Diagrams](./diagrams/ARCHITECTURE_DIAGRAM.md#deployment-architecture)
3. Configure [Monitoring](./DEPLOYMENT_GUIDE.md#monitoring--observability)
4. Plan [Disaster Recovery](./DEPLOYMENT_GUIDE.md#disaster-recovery)

### For System Architects
1. Study [Architecture Documentation](./ARCHITECTURE.md)
2. Analyze [Module Architecture](./ARCHITECTURE.md#module-architecture)
3. Review [Security Architecture](./ARCHITECTURE.md#security-architecture)
4. Understand [Data Flow](./diagrams/ARCHITECTURE_DIAGRAM.md#data-flow-architecture)

## 📦 Module-Specific Documentation

Each module contains its own README with specific details:

- [Consciousness Module](../consciousness/README.md) - Awareness and reflection systems
- [Memory Module](../memory/README.md) - DNA helix memory architecture
- [Guardian System](../governance/README.md) - Ethical oversight and protection
- [Dream Engine](../creativity/dream_engine/README.md) - Creative generation
- [VIVOX Extensions](../vivox/README.md) - Advanced capabilities

## 🛠 Tools and Scripts

### Analysis Tools
- [Functional Analysis](../tools/analysis/_FUNCTIONAL_ANALYSIS.py)
- [Import Analysis](../tools/analysis/_ACTIVE_IMPORT_ANALYSIS.py)
- [Connectivity Analysis](../tools/analysis/_SYSTEM_CONNECTIVITY_ANALYSIS.py)

### Utility Scripts
- [Import Fixer](../tools/scripts/fix_imports.py)
- [Syntax Error Fixer](../tools/scripts/fix_syntax_errors.py)
- [Module Enhancer](../tools/scripts/enhance_all_modules.py)

## 📝 Configuration Examples

### Environment Configuration
- [.env.example](../.env.example) - Environment variables template
- [pytest.ini](../pytest.ini) - Test configuration
- [pyproject.toml](../pyproject.toml) - Python project configuration

### Docker Configuration
- [Dockerfile](../Dockerfile) - Main container image
- [docker-compose.yml](../docker-compose.yml) - Local development
- [docker-compose.prod.yml](./examples/docker-compose.prod.yml) - Production setup

## 🔍 Search Documentation

To search across all documentation:

```bash
# Search for a specific term
grep -r "Guardian System" docs/

# Find all mentions of a module
find docs -name "*.md" -exec grep -l "consciousness" {} \;

# Search with context
grep -r -B 2 -A 2 "GLYPH token" docs/
```

## 📞 Support

For additional documentation or clarification:
1. Check module-specific README files
2. Review code comments and docstrings
3. Consult the [API Reference](./API_REFERENCE.md#support)
4. Open an issue on GitHub

## 🔄 Documentation Updates

This documentation is actively maintained. Last updated: January 2024

To contribute to documentation:
1. Follow the existing format and style
2. Include practical examples
3. Update the index when adding new documents
4. Ensure all links are working

---

*LUKHAS  - Pack What Matters*