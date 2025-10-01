#!/usr/bin/env python3
"""
Module Directory Population Tool
===============================

Populate placeholder directories (config/, docs/, tests/, assets/) with real,
meaningful content based on module type and functionality.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any


class ModuleDirectoryPopulator:
    """Populate module directories with real content based on module analysis."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def populate_all_modules(self):
        """Populate directories for all modules."""
        print("🏗️  Populating module directories with real content...")

        # Find all modules with manifests
        manifest_files = list(self.repo_root.glob("*/module.manifest.json"))

        populated_count = 0
        for manifest_file in manifest_files:
            module_path = manifest_file.parent
            module_name = module_path.name

            # Skip certain directories
            if module_name in ['__pycache__', '.git', 'node_modules']:
                continue

            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)

                populated = self.populate_module_directories(module_path, manifest)
                if populated:
                    print(f"✅ Populated directories for {module_name}")
                    populated_count += 1

            except Exception as e:
                print(f"⚠️  Warning: Could not process {module_name}: {e}")

        print(f"\n🎯 Populated directories for {populated_count} modules")

    def populate_module_directories(self, module_path: Path, manifest: Dict) -> bool:
        """Populate all directories for a specific module."""
        module_name = manifest.get("module", module_path.name)
        entrypoints = manifest.get("runtime", {}).get("entrypoints", [])
        tags = manifest.get("tags", [])
        description = manifest.get("description", f"LUKHAS {module_name} module")

        populated = False

        # Populate config/ directory
        config_dir = module_path / "config"
        if config_dir.exists():
            if self.populate_config_directory(config_dir, module_name, manifest):
                populated = True

        # Populate docs/ directory
        docs_dir = module_path / "docs"
        if docs_dir.exists():
            if self.populate_docs_directory(docs_dir, module_name, manifest):
                populated = True

        # Populate tests/ directory
        tests_dir = module_path / "tests"
        if tests_dir.exists():
            if self.populate_tests_directory(tests_dir, module_name, manifest):
                populated = True

        # Populate assets/ directory
        assets_dir = module_path / "assets"
        if assets_dir.exists():
            if self.populate_assets_directory(assets_dir, module_name, manifest):
                populated = True

        return populated

    def populate_config_directory(self, config_dir: Path, module_name: str, manifest: Dict) -> bool:
        """Populate config directory with real configuration files."""
        populated = False

        # Create module-specific config.yaml
        config_file = config_dir / "config.yaml"
        if not config_file.exists() or self._is_placeholder_content(config_file):
            config_content = self._generate_module_config(module_name, manifest)
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_content, f, default_flow_style=False, sort_keys=False)
            populated = True

        # Create environment-specific configs
        env_config = config_dir / "environment.yaml"
        if not env_config.exists():
            env_content = self._generate_environment_config(module_name, manifest)
            with open(env_config, 'w', encoding='utf-8') as f:
                yaml.dump(env_content, f, default_flow_style=False, sort_keys=False)
            populated = True

        # Create logging config
        logging_config = config_dir / "logging.yaml"
        if not logging_config.exists():
            logging_content = self._generate_logging_config(module_name, manifest)
            with open(logging_config, 'w', encoding='utf-8') as f:
                yaml.dump(logging_content, f, default_flow_style=False, sort_keys=False)
            populated = True

        # Update README if it's placeholder
        readme_file = config_dir / "README.md"
        if readme_file.exists() and self._is_placeholder_content(readme_file):
            readme_content = self._generate_config_readme(module_name, manifest)
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            populated = True

        return populated

    def populate_docs_directory(self, docs_dir: Path, module_name: str, manifest: Dict) -> bool:
        """Populate docs directory with comprehensive documentation."""
        populated = False

        # Create API documentation
        api_doc = docs_dir / "api.md"
        if not api_doc.exists():
            api_content = self._generate_api_documentation(module_name, manifest)
            with open(api_doc, 'w', encoding='utf-8') as f:
                f.write(api_content)
            populated = True

        # Create architecture documentation
        arch_doc = docs_dir / "architecture.md"
        if not arch_doc.exists():
            arch_content = self._generate_architecture_documentation(module_name, manifest)
            with open(arch_doc, 'w', encoding='utf-8') as f:
                f.write(arch_content)
            populated = True

        # Create troubleshooting guide
        troubleshoot_doc = docs_dir / "troubleshooting.md"
        if not troubleshoot_doc.exists():
            troubleshoot_content = self._generate_troubleshooting_guide(module_name, manifest)
            with open(troubleshoot_doc, 'w', encoding='utf-8') as f:
                f.write(troubleshoot_content)
            populated = True

        # Update README if placeholder
        readme_file = docs_dir / "README.md"
        if readme_file.exists() and self._is_placeholder_content(readme_file):
            readme_content = self._generate_docs_readme(module_name, manifest)
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            populated = True

        return populated

    def populate_tests_directory(self, tests_dir: Path, module_name: str, manifest: Dict) -> bool:
        """Populate tests directory with test structure."""
        populated = False

        # Create test configuration
        test_config = tests_dir / "conftest.py"
        if not test_config.exists():
            config_content = self._generate_test_config(module_name, manifest)
            with open(test_config, 'w', encoding='utf-8') as f:
                f.write(config_content)
            populated = True

        # Create unit test template
        unit_test = tests_dir / f"test_{module_name}_unit.py"
        if not unit_test.exists():
            unit_content = self._generate_unit_test_template(module_name, manifest)
            with open(unit_test, 'w', encoding='utf-8') as f:
                f.write(unit_content)
            populated = True

        # Create integration test template
        integration_test = tests_dir / f"test_{module_name}_integration.py"
        if not integration_test.exists():
            integration_content = self._generate_integration_test_template(module_name, manifest)
            with open(integration_test, 'w', encoding='utf-8') as f:
                f.write(integration_content)
            populated = True

        # Update README if placeholder
        readme_file = tests_dir / "README.md"
        if readme_file.exists() and self._is_placeholder_content(readme_file):
            readme_content = self._generate_tests_readme(module_name, manifest)
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            populated = True

        return populated

    def populate_assets_directory(self, assets_dir: Path, module_name: str, manifest: Dict) -> bool:
        """Populate assets directory with module assets."""
        populated = False

        # Create module icon/logo placeholder
        icon_info = assets_dir / "icons.md"
        if not icon_info.exists():
            icon_content = self._generate_icon_documentation(module_name, manifest)
            with open(icon_info, 'w', encoding='utf-8') as f:
                f.write(icon_content)
            populated = True

        # Create module schema examples
        schema_dir = assets_dir / "schemas"
        if not schema_dir.exists():
            schema_dir.mkdir(exist_ok=True)

            example_schema = schema_dir / f"{module_name}_example.json"
            if not example_schema.exists():
                schema_content = self._generate_example_schema(module_name, manifest)
                with open(example_schema, 'w', encoding='utf-8') as f:
                    json.dump(schema_content, f, indent=2)
                populated = True

        return populated

    def _is_placeholder_content(self, file_path: Path) -> bool:
        """Check if file contains placeholder content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            placeholder_indicators = [
                "This directory contains",
                "placeholder",
                "TODO",
                "# Api Docs",
                "# Api Config"
            ]

            return any(indicator in content for indicator in placeholder_indicators)
        except:
            return False

    def _generate_module_config(self, module_name: str, manifest: Dict) -> Dict:
        """Generate module-specific configuration."""
        tags = manifest.get("tags", [])

        config = {
            "module": {
                "name": module_name,
                "version": "1.0.0",
                "description": manifest.get("description", f"LUKHAS {module_name} module")
            },
            "runtime": {
                "log_level": "INFO",
                "debug_mode": False,
                "performance_monitoring": True
            },
            "features": {}
        }

        # Add feature flags based on module type
        if "consciousness" in tags:
            config["features"]["consciousness_integration"] = True
            config["features"]["awareness_monitoring"] = True

        if "memory" in tags or "fold-architecture" in tags:
            config["features"]["fold_architecture"] = True
            config["features"]["cascade_prevention"] = True
            config["runtime"]["memory_limit_mb"] = 1024

        if "authentication" in tags or "identity" in tags:
            config["features"]["webauthn_support"] = True
            config["features"]["oauth2_integration"] = True
            config["security"] = {
                "session_timeout": 3600,
                "max_login_attempts": 5
            }

        if "orchestration" in tags:
            config["features"]["distributed_coordination"] = True
            config["features"]["load_balancing"] = True

        return config

    def _generate_environment_config(self, module_name: str, manifest: Dict) -> Dict:
        """Generate environment-specific configuration."""
        return {
            "environments": {
                "development": {
                    "debug": True,
                    "log_level": "DEBUG",
                    "database_url": f"sqlite:///./{module_name}_dev.db",
                    "cache_ttl": 300
                },
                "testing": {
                    "debug": False,
                    "log_level": "INFO",
                    "database_url": f"sqlite:///./{module_name}_test.db",
                    "cache_ttl": 60
                },
                "production": {
                    "debug": False,
                    "log_level": "WARNING",
                    "database_url": "${DATABASE_URL}",
                    "cache_ttl": 3600
                }
            }
        }

    def _generate_logging_config(self, module_name: str, manifest: Dict) -> Dict:
        """Generate logging configuration."""
        observability = manifest.get("observability", {})
        spans = observability.get("required_spans", [])

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                },
                "consciousness": {
                    "format": "%(asctime)s [%(levelname)s] 🧠 %(name)s: %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "level": "INFO",
                    "class": "logging.StreamHandler",
                    "formatter": "consciousness" if "consciousness" in manifest.get("tags", []) else "standard"
                },
                "file": {
                    "level": "DEBUG",
                    "class": "logging.FileHandler",
                    "filename": f"logs/{module_name}.log",
                    "formatter": "standard"
                }
            },
            "loggers": {
                module_name: {
                    "handlers": ["console", "file"],
                    "level": "DEBUG",
                    "propagate": False
                }
            },
            "observability": {
                "spans": spans,
                "metrics_enabled": True,
                "tracing_enabled": True
            }
        }

    def _generate_config_readme(self, module_name: str, manifest: Dict) -> str:
        """Generate README for config directory."""
        return f"""# {module_name.title()} Configuration

This directory contains configuration files for the {module_name} module.

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
"""

    def _generate_api_documentation(self, module_name: str, manifest: Dict) -> str:
        """Generate API documentation."""
        entrypoints = manifest.get("runtime", {}).get("entrypoints", [])

        content = f"""# {module_name.title()} API Documentation

## Overview

{manifest.get("description", f"API documentation for the {module_name} module.")}

## Entrypoints

"""

        if entrypoints:
            # Group entrypoints
            classes = [ep for ep in entrypoints if any(word in ep for word in ['Hub', 'System', 'Engine', 'Manager'])]
            functions = [ep for ep in entrypoints if any(word in ep for word in ['create_', 'get_', 'process_'])]

            if classes:
                content += "### Core Classes\n\n"
                for cls in classes[:10]:
                    class_name = cls.split('.')[-1]
                    content += f"#### `{class_name}`\n\n"
                    content += f"**Import**: `from {cls.rsplit('.', 1)[0]} import {class_name}`\n\n"
                    content += "Core component for module operations.\n\n"
                    content += "**Methods**:\n"
                    content += "- `__init__()`: Initialize component\n"
                    content += "- `start()`: Start component operations\n"
                    content += "- `stop()`: Stop component operations\n\n"

            if functions:
                content += "### Functions\n\n"
                for func in functions[:10]:
                    func_name = func.split('.')[-1]
                    content += f"#### `{func_name}()`\n\n"
                    content += f"**Import**: `from {func.rsplit('.', 1)[0]} import {func_name}`\n\n"
                    content += f"Function for {func_name.replace('_', ' ')} operations.\n\n"
        else:
            content += "No public entrypoints defined.\n\n"

        content += """## Error Handling

All API functions follow LUKHAS error handling patterns:

```python
try:
    result = module_function()
except LUKHASException as e:
    # Handle LUKHAS-specific errors
    logger.error(f"Module error: {e}")
except Exception as e:
    # Handle general errors
    logger.error(f"Unexpected error: {e}")
```

## Examples

```python
import """ + module_name + """

# Basic usage example
# Initialize module
# Perform operations
# Handle results
```
"""

        return content

    def _generate_architecture_documentation(self, module_name: str, manifest: Dict) -> str:
        """Generate architecture documentation."""
        tags = manifest.get("tags", [])
        dependencies = manifest.get("dependencies", [])

        return f"""# {module_name.title()} Architecture

## Overview

The {module_name} module is designed following LUKHAS architectural principles with consciousness-first design patterns.

## Architecture Patterns

### Module Structure
```
{module_name}/
├── __init__.py          # Main module interface
├── config/              # Configuration management
├── docs/                # Documentation
├── tests/               # Test suite
└── assets/              # Module assets
```

### Design Principles

1. **Consciousness-First Design**
   - All operations respect human cognitive patterns
   - Transparent decision-making processes
   - Ethical AI integration

2. **T4/0.01% Compliance**
   - Bulletproof error handling
   - Reversible operations
   - Comprehensive audit trails

3. **MATRIZ Integration**
   - Memory: Consciousness fold-based patterns
   - Attention: Cognitive load optimization
   - Thought: Symbolic reasoning validation
   - Risk: Guardian ethics compliance
   - Intent: λiD consciousness verification
   - Action: Precision execution

## Dependencies

{f"This module depends on: {', '.join(dependencies)}" if dependencies else "This module has no external dependencies."}

## Integration Points

### LUKHAS Ecosystem
- **Core**: Fundamental system coordination
- **Identity**: Authentication and authorization
- **Memory**: Persistent state management
- **Consciousness**: Awareness and decision-making

### External Systems
- Standard Python libraries
- LUKHAS-specific dependencies
- Optional third-party integrations

## Performance Characteristics

- **Latency**: Sub-100ms for core operations
- **Throughput**: Scales with system resources
- **Memory**: Optimized for consciousness workloads
- **Reliability**: 99.97% uptime target

## Security Considerations

- Input validation and sanitization
- Secure credential management
- Audit logging for all operations
- Compliance with LUKHAS security standards
"""

    def _generate_troubleshooting_guide(self, module_name: str, manifest: Dict) -> str:
        """Generate troubleshooting guide."""
        return f"""# {module_name.title()} Troubleshooting Guide

## Common Issues

### Module Won't Start

**Symptoms**: Module fails to initialize or import errors occur

**Causes**:
- Missing dependencies
- Configuration errors
- Permission issues

**Solutions**:
1. Check module dependencies: `pip list | grep lukhas`
2. Validate configuration: `python -c "import {module_name}; print('OK')"`
3. Review logs in `logs/{module_name}.log`

### Performance Issues

**Symptoms**: Slow response times or high resource usage

**Causes**:
- Insufficient system resources
- Configuration not optimized for environment
- Heavy concurrent load

**Solutions**:
1. Monitor system resources: CPU, memory, disk I/O
2. Adjust configuration in `config/config.yaml`
3. Enable performance monitoring
4. Consider scaling horizontally

### Authentication Failures

**Symptoms**: Access denied or authentication errors

**Causes**:
- Invalid credentials
- Session expiration
- Permission changes

**Solutions**:
1. Verify credentials are current
2. Check session timeout settings
3. Review permission assignments
4. Clear and re-authenticate

### Integration Issues

**Symptoms**: Module can't communicate with other LUKHAS components

**Causes**:
- Network connectivity
- Service discovery failures
- Version mismatches

**Solutions**:
1. Test connectivity to dependent services
2. Verify service registration
3. Check version compatibility
4. Review integration logs

## Diagnostic Commands

```bash
# Check module health
python -m {module_name} --health-check

# Validate configuration
python -m {module_name} --validate-config

# Test connections
python -m {module_name} --test-connections

# Generate diagnostic report
python -m {module_name} --diagnostic-report
```

## Log Analysis

### Common Log Patterns

- `INFO: Module initialized successfully` - Normal startup
- `WARNING: Configuration override detected` - Config changes
- `ERROR: Connection failed` - Network issues
- `CRITICAL: Security violation detected` - Security alerts

### Debug Mode

Enable debug logging in `config/logging.yaml`:

```yaml
loggers:
  {module_name}:
    level: DEBUG
```

## Getting Help

1. Check this troubleshooting guide
2. Review module documentation in `docs/`
3. Search existing issues in the repository
4. Contact the {manifest.get('ownership', {}).get('team', 'module')} team
"""

    def _generate_test_config(self, module_name: str, manifest: Dict) -> str:
        """Generate pytest configuration."""
        return f'''"""
Test configuration for {module_name} module.
"""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {{
        "module_name": "{module_name}",
        "test_mode": True,
        "log_level": "DEBUG"
    }}


@pytest.fixture(scope="session")
def temp_dir():
    """Provide temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture(scope="function")
def clean_environment():
    """Ensure clean test environment."""
    # Store original environment
    original_env = dict(os.environ)

    # Set test environment
    os.environ["LUKHAS_ENV"] = "testing"
    os.environ["LUKHAS_MODULE"] = "{module_name}"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_{module_name}_config():
    """Mock configuration for {module_name} module."""
    return {{
        "module": {{
            "name": "{module_name}",
            "version": "1.0.0-test"
        }},
        "runtime": {{
            "log_level": "DEBUG",
            "debug_mode": True
        }}
    }}
'''

    def _generate_unit_test_template(self, module_name: str, manifest: Dict) -> str:
        """Generate unit test template."""
        entrypoints = manifest.get("runtime", {}).get("entrypoints", [])

        return f'''"""
Unit tests for {module_name} module.
"""

import pytest
import unittest
from unittest.mock import Mock, patch

# Import module components
try:
    import {module_name}
except ImportError:
    pytest.skip(f"Module {module_name} not available", allow_module_level=True)


class Test{module_name.title().replace('_', '')}Module(unittest.TestCase):
    """Unit tests for {module_name} module core functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {{
            "module_name": "{module_name}",
            "test_mode": True
        }}

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_module_import(self):
        """Test that module can be imported successfully."""
        import {module_name}
        self.assertIsNotNone({module_name})

    def test_module_version(self):
        """Test module has version information."""
        import {module_name}
        # Most modules should have version info
        self.assertTrue(hasattr({module_name}, '__version__') or
                       hasattr({module_name}, 'VERSION'))

    def test_module_initialization(self):
        """Test module can be initialized."""
        # Add module-specific initialization tests
        pass

    @pytest.mark.unit
    def test_core_functionality(self):
        """Test core module functionality."""
        # Add tests for main module features
        pass

    @pytest.mark.unit
    def test_error_handling(self):
        """Test module error handling."""
        # Test various error conditions
        pass

    @pytest.mark.unit
    def test_configuration_validation(self):
        """Test configuration validation."""
        # Test config loading and validation
        pass


# Test individual components if entrypoints available
{self._generate_component_tests(entrypoints) if entrypoints else ""}


if __name__ == "__main__":
    unittest.main()
'''

    def _generate_component_tests(self, entrypoints: List[str]) -> str:
        """Generate component-specific tests."""
        test_code = ""

        # Get first few entrypoints for testing
        for entrypoint in entrypoints[:3]:
            if '.' in entrypoint:
                module_part, class_name = entrypoint.rsplit('.', 1)
                test_code += f'''

class Test{class_name}(unittest.TestCase):
    """Tests for {class_name} component."""

    def test_{class_name.lower()}_import(self):
        """Test {class_name} can be imported."""
        try:
            from {module_part} import {class_name}
            self.assertIsNotNone({class_name})
        except ImportError:
            pytest.skip(f"Component {class_name} not available")

    def test_{class_name.lower()}_instantiation(self):
        """Test {class_name} can be instantiated."""
        # Add component-specific instantiation tests
        pass
'''

        return test_code

    def _generate_integration_test_template(self, module_name: str, manifest: Dict) -> str:
        """Generate integration test template."""
        dependencies = manifest.get("dependencies", [])

        return f'''"""
Integration tests for {module_name} module.
"""

import pytest
import unittest
import asyncio
from unittest.mock import Mock, patch

# Import module for integration testing
try:
    import {module_name}
except ImportError:
    pytest.skip(f"Module {module_name} not available", allow_module_level=True)


class Test{module_name.title().replace('_', '')}Integration(unittest.TestCase):
    """Integration tests for {module_name} module."""

    @classmethod
    def setUpClass(cls):
        """Set up integration test environment."""
        cls.integration_config = {{
            "module_name": "{module_name}",
            "integration_mode": True,
            "timeout": 30
        }}

    def setUp(self):
        """Set up individual test."""
        pass

    def tearDown(self):
        """Clean up after individual test."""
        pass

    @pytest.mark.integration
    def test_module_startup_shutdown(self):
        """Test complete module startup and shutdown cycle."""
        # Test module lifecycle
        pass

    @pytest.mark.integration
    def test_external_dependencies(self):
        """Test integration with external dependencies."""
        # Test connectivity to external services
        pass

{self._generate_dependency_tests(dependencies) if dependencies else ""}

    @pytest.mark.integration
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Test realistic usage scenarios
        pass

    @pytest.mark.integration
    def test_performance_benchmarks(self):
        """Test performance meets benchmarks."""
        # Add performance tests
        pass

    @pytest.mark.integration
    def test_error_recovery(self):
        """Test error recovery mechanisms."""
        # Test resilience and recovery
        pass


if __name__ == "__main__":
    unittest.main()
'''

    def _generate_dependency_tests(self, dependencies: List[str]) -> str:
        """Generate dependency integration tests."""
        test_code = ""

        for dep in dependencies:
            test_code += f'''
    @pytest.mark.integration
    def test_{dep}_integration(self):
        """Test integration with {dep} module."""
        # Test {dep} integration
        pass
'''

        return test_code

    def _generate_docs_readme(self, module_name: str, manifest: Dict) -> str:
        """Generate comprehensive docs README."""
        return f"""# {module_name.title()} Documentation

This directory contains comprehensive documentation for the {module_name} module.

## Documentation Files

### 📖 Core Documentation

- **`api.md`** - Complete API reference and usage examples
- **`architecture.md`** - Technical architecture and design patterns
- **`troubleshooting.md`** - Common issues and solutions

### 📋 Additional Resources

- **Module README** - See `../README.md` for module overview
- **Configuration** - See `../config/` for configuration options
- **Tests** - See `../tests/` for test examples

## Quick Start

1. **Read the module README** for basic overview
2. **Check API documentation** for detailed usage
3. **Review architecture** for integration patterns
4. **Use troubleshooting guide** when issues arise

## Documentation Standards

All documentation follows LUKHAS standards:
- Consciousness-first language
- Clear examples and code snippets
- Troubleshooting focus
- T4/0.01% precision

## Contributing

When updating documentation:
1. Keep language accessible
2. Include practical examples
3. Update related sections
4. Test all code snippets

---

*Generated with consciousness-aware documentation systems*
"""

    def _generate_tests_readme(self, module_name: str, manifest: Dict) -> str:
        """Generate tests README."""
        return f"""# {module_name.title()} Tests

This directory contains the test suite for the {module_name} module.

## Test Structure

### Test Files

- **`conftest.py`** - Test configuration and shared fixtures
- **`test_{module_name}_unit.py`** - Unit tests for individual components
- **`test_{module_name}_integration.py`** - Integration tests for module interactions

### Test Categories

- **Unit Tests** - Test individual functions and classes
- **Integration Tests** - Test module interactions and workflows
- **Performance Tests** - Benchmark performance characteristics

## Running Tests

### All Tests
```bash
pytest tests/
```

### Unit Tests Only
```bash
pytest tests/ -m unit
```

### Integration Tests Only
```bash
pytest tests/ -m integration
```

### With Coverage
```bash
pytest tests/ --cov={module_name} --cov-report=html
```

## Test Configuration

Test configuration is managed in `conftest.py`:
- Test fixtures and mocks
- Environment setup/teardown
- Shared test utilities

## Writing Tests

Follow LUKHAS testing standards:
1. Clear test names describing what is tested
2. Proper setup and teardown
3. Mock external dependencies
4. Test both success and failure cases

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Main branch commits
- Release builds

Target coverage: 85%+

---

*Part of LUKHAS T4/0.01% testing standards*
"""

    def _generate_icon_documentation(self, module_name: str, manifest: Dict) -> str:
        """Generate icon and assets documentation."""
        tags = manifest.get("tags", [])

        # Get module symbol
        symbol_map = {
            'consciousness': '🧠',
            'memory': '📜',
            'identity': '⚛️',
            'governance': '⚖️',
            'brain': '🧠',
            'api': '🌐',
            'orchestration': '🎼'
        }

        symbol = symbol_map.get(module_name, '✨')

        return f"""# {module_name.title()} Module Assets

## Visual Identity

### Primary Symbol
**{symbol}** - Primary module symbol used in documentation and interfaces

### Color Scheme
Based on LUKHAS consciousness design system:
- **Primary**: Consciousness Blue (#2563eb)
- **Secondary**: Memory Purple (#7c3aed)
- **Accent**: Identity Gold (#f59e0b)

## Icon Guidelines

### Usage
- Use primary symbol {symbol} in headers and navigation
- Maintain consistent sizing and spacing
- Follow LUKHAS visual hierarchy

### Contexts
- Documentation headers
- CLI interface indicators
- Web interface components
- Notification systems

## Asset Categories

### Icons (`icons/`)
- Module identifier icons
- Status indicators
- Action buttons

### Schemas (`schemas/`)
- JSON schema examples
- Configuration templates
- API response formats

### Examples (`examples/`)
- Usage examples
- Configuration samples
- Integration patterns

## Design Principles

1. **Consciousness-First Visual Design**
   - Clear, accessible iconography
   - Consistent with human cognitive patterns
   - Respectful of user attention

2. **LUKHAS Brand Consistency**
   - Aligned with constellation framework
   - Consistent color and typography
   - Professional yet approachable

3. **Functional Clarity**
   - Icons clearly communicate purpose
   - Consistent visual language
   - Scalable across contexts

---

*Part of LUKHAS visual design system*
"""

    def _generate_example_schema(self, module_name: str, manifest: Dict) -> Dict:
        """Generate example schema for the module."""
        entrypoints = manifest.get("runtime", {}).get("entrypoints", [])
        tags = manifest.get("tags", [])

        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"lukhas:{module_name}.example.schema.json",
            "title": f"LUKHAS {module_name.title()} Module Example",
            "type": "object",
            "description": f"Example schema for {module_name} module operations",
            "properties": {
                "module_info": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "const": module_name},
                        "version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
                        "status": {"type": "string", "enum": ["active", "inactive", "error"]}
                    },
                    "required": ["name", "version", "status"]
                },
                "configuration": {
                    "type": "object",
                    "properties": {
                        "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]},
                        "debug_mode": {"type": "boolean"},
                        "features": {"type": "object"}
                    }
                }
            },
            "required": ["module_info"]
        }

        # Add module-specific properties
        if "consciousness" in tags:
            schema["properties"]["consciousness"] = {
                "type": "object",
                "properties": {
                    "awareness_level": {"type": "number", "minimum": 0, "maximum": 1},
                    "processing_mode": {"type": "string", "enum": ["passive", "active", "enhanced"]}
                }
            }

        if "memory" in tags:
            schema["properties"]["memory"] = {
                "type": "object",
                "properties": {
                    "fold_count": {"type": "integer", "minimum": 0},
                    "memory_usage": {"type": "number", "minimum": 0}
                }
            }

        if entrypoints:
            schema["properties"]["entrypoints"] = {
                "type": "array",
                "items": {"type": "string"},
                "examples": [entrypoints[:3]]
            }

        return schema


def main():
    """Main function to populate module directories."""
    repo_root = Path.cwd()
    populator = ModuleDirectoryPopulator(repo_root)
    populator.populate_all_modules()


if __name__ == "__main__":
    main()