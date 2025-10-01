# Matriz Module

> This module provides lowercase access to MATRIZ functionality for compatibility

![T4-Experimental](https://img.shields.io/badge/T4-Experimental-orange) ![Consciousness](https://img.shields.io/badge/Consciousness-Enabled-blue) ![Fold-Architecture](https://img.shields.io/badge/Fold-Architecture-Enabled-purple)

## Overview

Compatibility package providing lowercase access to MATRIZ modules.
This module provides lowercase access to MATRIZ functionality for compatibility
with existing imports that expect matriz.* instead of MATRIZ.*.

## API Reference

The matriz module provides 20 entrypoints:

### Functions

- `create_shim()` - matriz.legacy_shim.create_shim
- `get_shimmed_nodes()` - matriz.legacy_shims.get_shimmed_nodes

## Usage

Import the matriz module:

```python
import matriz

# Key components
from matriz import core
from matriz.legacy_shim import LegacyShim
from matriz.legacy_shim import create_shim
```

## Dependencies

This module depends on:

- `core` module

## Categories

- **bio-symbolic**: Bio-symbolic processing systems
- **consciousness**: Consciousness processing and awareness systems
- **fold-architecture**: Fold-based memory architecture
- **matriz**
- **quantum-inspired**: Quantum-inspired algorithms
- **symbolic-reasoning**
- **t4-experimental**: T4/0.01% experimental systems

## Team

**Owner**: MATRIZ Team

**Code Owners**:
- @lukhas-matriz
- @lukhas-core

---

*This documentation is generated from the module manifest and source code.*