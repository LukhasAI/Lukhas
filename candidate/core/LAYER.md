# Core Layer

## ✅ Purpose
The Core layer provides foundational utilities, base classes, and common interfaces that all other layers depend on. This is the lowest level of the LUKHAS architecture.

## ✅ What it can depend on
- Standard library modules only
- No dependencies on any other LUKHAS modules

## ❌ What must never import from it
- Nothing - all modules can import from core
- Core is the foundation and has no restrictions on who imports it

## 🔄 Lifecycle events / triggers
- **Initialization**: First module loaded at system startup
- **Configuration**: Loads system-wide configuration before other modules
- **Base Classes**: Provides abstract base classes for all major components
- **Utilities**: Common utilities like logging, metrics, validation
- **Interfaces**: Common interface definitions used across the system

## 🏗️ Key Components
- `base.py`: Base classes for all LUKHAS components
- `interfaces/`: Common interface definitions
- `utilities.py`: Shared utility functions
- `metrics.py`: Base metrics and monitoring
- `config.py`: Configuration management
- `exceptions.py`: Common exception types

## 🎯 Design Principles
1. **Zero Dependencies**: Core depends on nothing except stdlib
2. **Maximum Stability**: Changes here affect everything - must be extremely stable
3. **Pure Functions**: Prefer pure, stateless functions where possible
4. **Type Safety**: All interfaces must be strongly typed
5. **Documentation**: Every public API must be thoroughly documented
