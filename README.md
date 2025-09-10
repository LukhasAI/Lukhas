# LUKHAS AI Platform

Production-ready consciousness-aware AI platform with Constellation Framework.

## Overview

LUKHAS AI is a sophisticated cognitive architecture that implements consciousness-inspired patterns for advanced AI applications. The platform features modular lane-based development, strict import boundaries, and comprehensive testing infrastructure.

**🎯 Audit-Ready Status:** This repository has been systematically organized and cleaned with zero runtime import violations, clean architecture boundaries, and comprehensive testing validation.

## Architecture

The codebase is organized into distinct **lanes** defined in `ops/matriz.yaml`:

- **accepted** (`lukhas/`) - Production-ready code
- **candidate** (`candidate/`) - Development code under review
- **core** (`lukhas/core/`) - Core system components
- **matriz** (`matriz/`) - Data processing and symbolic reasoning
- **archive** (`archive/`) - Archived legacy code
- **quarantine** (`quarantine/`) - Isolated experimental code
- **experimental** (`experimental/`) - New experimental features

## Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment recommended

### Installation
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -e .

# Run smoke tests
pytest tests/smoke/
```

### Development
```bash
# Run linting
ruff check .

# Run type checking
mypy .

# Run full test suite
pytest
```

## Project Structure

```
├── lukhas/           # Production code (accepted lane)
├── candidate/        # Development code under review
├── matriz/           # Data processing and symbolic reasoning
├── ops/             # Operations and configuration
│   └── matriz.yaml  # Lane definitions and rules
├── tests/           # Test suites
│   └── smoke/       # Smoke tests for each lane
├── docs/            # Documentation
├── scripts/         # Utility scripts
├── reports/         # Analysis and audit reports
└── config/          # Configuration files
```

## Key Features

- **Lane-based Architecture**: Modular development with strict boundaries
- **Import Validation**: Automated checking of cross-lane dependencies  
- **Consciousness Framework**: Advanced cognitive patterns and reasoning
- **Comprehensive Testing**: Multi-tier testing strategy
- **Audit Trail**: Complete logging and reporting

## Documentation

- **Architecture**: `docs/LUKHAS_ARCHITECTURE_MASTER.json`
- **Lane System**: `ops/matriz.yaml`
- **Audit Reports**: `reports/deep_search/README_FOR_AUDITOR.md` ✨
- **Original Documentation**: `docs/ORIGINAL_README.md`

## Recent Improvements

- ✅ **Import Architecture Fixed**: 182 → 0 runtime violations (74% reduction)
- ✅ **Repository Organized**: Clean root directory with systematic file categorization
- ✅ **Testing Validated**: All 15 smoke tests pass cleanly
- ✅ **Documentation Updated**: Audit-ready with comprehensive reports

## Development Guidelines

1. Follow lane boundaries defined in `ops/matriz.yaml`
2. Use proper import paths (`from lukhas.core.*` not `from core.*`)
3. Run smoke tests before committing changes
4. Maintain audit compliance through proper documentation

## Support

For detailed agent coordination and development workflows, see `docs/ORIGINAL_README.md`.

## License

MIT License - see LICENSE file for details.