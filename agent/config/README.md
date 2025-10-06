---
status: wip
type: documentation
---
# Agent Configuration

This directory contains configuration files for the agent module.

## Configuration Files

### `config.yaml`
Main module configuration including:
- Module metadata and version
- Runtime settings and feature flags
- Performance and monitoring options

### `environment.yaml`
Environment-specific configurations for:
- **Development**: Debug mode enabled, verbose logging
- **Testing**: Optimized for test execution
- **Production**: Security-hardened, performance-optimized

### `logging.yaml`
Comprehensive logging configuration with:
- Multiple output formatters
- Console and file handlers
- Module-specific log levels
- Observability integration

## Usage

```python
import yaml
from pathlib import Path

config_path = Path(__file__).parent / "config.yaml"
with open(config_path) as f:
    config = yaml.safe_load(f)
```

## Environment Variables

Set `LUKHAS_ENV` to override environment-specific settings:
- `development` (default)
- `testing`
- `production`
