---
last_review: 2025-09-09
module: unknown
owner: docs-maintainer
status: stable
tags:
- quickstart
- setup
- installation
- howto
title: LUKHAS Quick Start Guide
type: documentation
---
# 🚀 LUKHAS Quick Start Guide

Welcome to LUKHAS  - Pack What Matters! This guide will get you up and running quickly.

## 📋 Prerequisites

- Python 3.9+
- pip or conda
- Git
- Optional: Docker for containerized deployment

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/LukhasAI/Lukhas.git
cd Lukhas
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Core dependencies
pip install -r requirements.txt

# Test dependencies (optional)
pip install -r requirements-test.txt
```

### 4. Configure Environment
```bash
# Copy example environment
cp .env.example .env

# Edit .env with your settings
# Required: OPENAI_API_KEY for NIAS Dream Commerce
```

## 🎯 Quick Test

### Test the System
```bash
# Run main entry point
python main.py

# Run tests
pytest tests/

# Run specific module test
pytest tests/governance/test_governance.py
```

### Test NIAS Dream Commerce
```bash
# Test the enhanced Dream Commerce system
python lambda_products_pack/lambda_core/NIAS/test_nias_comprehensive.py
```

## 📊 System Status

Check system health and performance:
```bash
# Run functional analysis
python tools/analysis/_FUNCTIONAL_ANALYSIS.py

# Check operational status
python tools/analysis/_OPERATIONAL_SUMMARY.py
```

## 🏗️ Architecture Overview

### Core Modules
- **`core/`** - GLYPH engine and symbolic processing (100% functional)
- **`consciousness/`** - Awareness and decision-making (70.9% functional)
- **`memory/`** - Fold-based memory system (72.1% functional)
- **`governance/`** - Guardian System ethical oversight (100% functional)
- **`lambda_products_pack/`** - Commercial AI products including NIAS

### Key Features
- **99%+ System Reliability** - Production-ready
- **Dependency Injection** - Robust service management
- **API Validation** - Comprehensive request validation
- **Async/Await** - Optimized for performance
- **Guardian System** - Ethical AI protection

## 🔌 Integration Examples

### Using NIAS Dream Commerce
```python
from lambda_products_pack.lambda_core.NIAS import DreamCommerceOrchestrator

# Initialize orchestrator
orchestrator = DreamCommerceOrchestrator()

# Start dream commerce session
result = await orchestrator.initiate_dream_commerce("user_123")
```

### Using Guardian System
```python
from governance import GuardianSystem

# Initialize guardian
guardian = GuardianSystem()

# Validate operation
is_safe = await guardian.validate_operation(operation_data)
```

## 📁 Project Structure

```
LUKHAS/
├── docs/           # Documentation and reports
├── tests/          # Test suites
├── tools/          # Analysis and utility scripts
├── test_results/   # Test outputs
├── config/         # Configuration files
└── [modules]/      # Core LUKHAS modules
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Check that all dependencies are installed

2. **API Key Missing**
   - Add your OpenAI API key to `.env`
   - Format: `OPENAI_API_KEY=sk-...`

3. **Test Failures**
   - Run `pip install -r requirements-test.txt`
   - Check logs in `logs/` directory

## 📚 Documentation

- **Main Documentation**: [README.md](README.md)
- **Architecture Guide**: [CLAUDE.md](CLAUDE.md)
- **Constellation Framework**: [README_TRINITY.md](README_TRINITY.md)
- **Phase 2 Achievements**: [docs/planning/completed/PHASE_2_ACHIEVEMENTS.md](docs/planning/completed/PHASE_2_ACHIEVEMENTS.md)

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/LukhasAI/Lukhas/issues)
- **Documentation**: [docs.lukhas.ai](https://docs.lukhas.ai)
- **Discord**: [Join Community](https://discord.gg/lukhas)

## 🎉 Next Steps

1. Explore the [Lambda Products](lambda_products_pack/README.md)
2. Check out the [NIAS Dream Commerce](lambda_products_pack/lambda_core/NIAS/README.md)
3. Run the comprehensive tests to see the system in action
4. Review the Guardian System for ethical AI implementation

---

**Welcome to LUKHAS !** You're now ready to build with production-ready AGI modules.
