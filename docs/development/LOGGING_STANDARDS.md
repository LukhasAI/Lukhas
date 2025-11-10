# Logging Standards Guide for LUKHAS AI

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-01-10
**Author**: Claude Code Web

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Standard Logger Pattern](#standard-logger-pattern)
- [Log Levels](#log-levels)
- [Structured Logging](#structured-logging)
- [Best Practices](#best-practices)
- [Preventing Duplicate Loggers](#preventing-duplicate-loggers)
- [Linting and Enforcement](#linting-and-enforcement)
- [Integration with Monitoring](#integration-with-monitoring)
- [Migration Guide](#migration-guide)
- [Troubleshooting](#troubleshooting)

---

## Overview

LUKHAS AI uses a **centralized logging system** with standardized patterns to ensure:

- **Consistency**: All modules use the same logging interface
- **No Duplicates**: Single logger instance per module
- **Structured Data**: JSON-formatted logs for production
- **Visual Clarity**: Emoji symbols for different log levels
- **Performance**: Minimal overhead, configurable verbosity

### Key Benefits

✅ **Standardized Pattern**: `get_logger(__name__)` across all modules
✅ **Zero Duplicates**: Cached logger instances prevent `ValueError: Duplicated timeseries`
✅ **Structured Logging**: JSON output for log aggregation systems
✅ **Module Context**: Automatic module name tagging
✅ **Flexible Configuration**: Environment-based log levels

---

## Quick Start

### ✅ CORRECT Pattern (Use This)

```python
from labs.core.common import get_logger

logger = get_logger(__name__)

def process_dream(dream_data):
    logger.info("Processing dream", extra={"dream_id": dream_data.id})
    try:
        result = analyze_dream(dream_data)
        logger.debug("Dream analysis complete", extra={"result": result})
        return result
    except Exception as e:
        logger.error("Dream processing failed", exc_info=True, extra={"dream_id": dream_data.id})
        raise
```

### ❌ INCORRECT Pattern (Don't Do This)

```python
import logging

# ❌ DON'T: Duplicate logger definition
logger = logging.getLogger(__name__)

# ❌ DON'T: Creating multiple loggers in one file
logger1 = logging.getLogger("module1")
logger2 = logging.getLogger("module2")

# ❌ DON'T: Module-level logger configuration
logging.basicConfig(level=logging.DEBUG)  # Conflicts with global config
```

---

## Standard Logger Pattern

### Module-Level Logger

**Rule**: One logger per file, defined at module level.

```python
"""
My Module
=========
Does something important for LUKHAS.
"""
from labs.core.common import get_logger

# ✅ CORRECT: Single logger at module level
logger = get_logger(__name__)


def my_function():
    """Function docstring"""
    logger.info("Function called")
    # ... implementation ...


class MyClass:
    """Class docstring"""

    def method(self):
        """Method docstring"""
        # ✅ Use the module-level logger
        logger.info("Method called")
        # ... implementation ...
```

### Using `__name__` for Logger Names

```python
from labs.core.common import get_logger

# ✅ CORRECT: Always use __name__
logger = get_logger(__name__)

# This automatically creates hierarchical logger names:
# - In file labs/consciousness/dream/processor.py:
#   Logger name becomes: "labs.consciousness.dream.processor"

# - In file matriz/consciousness/reflection/system.py:
#   Logger name becomes: "matriz.consciousness.reflection.system"
```

### Module Context (Optional)

For modules in specific LUKHAS subsystems, add module context:

```python
from labs.core.common import get_logger

# With module context (shows "CONSCIOUSNESS" prefix in logs)
logger = get_logger(__name__, module_name="CONSCIOUSNESS")

logger.info("Dream analysis started")
# Output: ℹ️ 2025-01-10 12:00:00 [CONSCIOUSNESS] labs.consciousness.dream - INFO - Dream analysis started
```

---

## Log Levels

### Level Guidelines

| Level | When to Use | Examples |
|-------|-------------|----------|
| **DEBUG** | Detailed diagnostic information | Variable values, function entry/exit, algorithm steps |
| **INFO** | General informational messages | System startup, configuration loaded, operation completed |
| **WARNING** | Potentially harmful situations | Deprecated API usage, missing optional config, slow performance |
| **ERROR** | Error events that might allow the app to continue | Failed to process request, database query failed, API call failed |
| **CRITICAL** | Very severe errors that may cause the app to abort | Database unreachable, critical service down, unrecoverable state |

### Examples

#### DEBUG

```python
logger.debug("Entering process_dream function", extra={
    "dream_id": dream_id,
    "user_id": user_id,
    "parameters": parameters
})

logger.debug("Computed coherence score", extra={"coherence": 0.87})

logger.debug("Cache lookup result", extra={"key": cache_key, "hit": cache_hit})
```

#### INFO

```python
logger.info("Dream processing started", extra={"dream_id": dream_id})

logger.info("User authenticated successfully", extra={"user_id": user_id})

logger.info("System initialized", extra={"version": "1.0.0", "environment": "production"})
```

#### WARNING

```python
logger.warning("API rate limit approaching", extra={
    "current_rate": 95,
    "limit": 100,
    "time_window": "1 minute"
})

logger.warning("Using deprecated parameter", extra={
    "parameter": "old_param",
    "replacement": "new_param"
})

logger.warning("Cache miss rate high", extra={
    "miss_rate": 0.65,
    "threshold": 0.5
})
```

#### ERROR

```python
logger.error("Failed to process dream", exc_info=True, extra={
    "dream_id": dream_id,
    "error_type": "ValidationError"
})

logger.error("Database query failed", exc_info=True, extra={
    "query": query_text,
    "table": "dreams"
})

logger.error("External API call failed", exc_info=True, extra={
    "api": "OpenAI",
    "endpoint": "/v1/chat/completions",
    "status_code": 429
})
```

#### CRITICAL

```python
logger.critical("Database connection lost", exc_info=True, extra={
    "host": db_host,
    "retries": retry_count
})

logger.critical("Memory limit exceeded", extra={
    "current_usage_mb": 8192,
    "limit_mb": 8000
})

logger.critical("Consciousness engine crash", exc_info=True, extra={
    "component": "MATRIZ",
    "uptime_seconds": uptime
})
```

---

## Structured Logging

### Adding Extra Context

Always use `extra` dictionary for structured data:

```python
# ✅ CORRECT: Structured logging with extra
logger.info("User login", extra={
    "user_id": "user_123",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "timestamp": datetime.utcnow().isoformat()
})

# ❌ INCORRECT: String interpolation loses structure
logger.info(f"User user_123 logged in from 192.168.1.100")
```

### JSON Output Format

In production, enable JSON logging for log aggregation:

```python
from labs.core.common import configure_logging

# Enable JSON logging for production
configure_logging(
    level="INFO",
    json_output=True
)

logger.info("Request processed", extra={
    "request_id": "req_abc123",
    "duration_ms": 45.2,
    "status": "success"
})
```

**Output** (JSON):
```json
{
  "timestamp": "2025-01-10T12:00:00.123Z",
  "level": "INFO",
  "module": "serve.routes",
  "function": "handle_request",
  "line": 42,
  "message": "Request processed",
  "thread": 123456,
  "thread_name": "MainThread",
  "request_id": "req_abc123",
  "duration_ms": 45.2,
  "status": "success"
}
```

### Standard Extra Fields

Use these standard field names for consistency:

```python
# User context
logger.info("Action performed", extra={
    "user_id": "user_123",
    "tier": "premium",
    "session_id": "sess_abc"
})

# Request context
logger.info("API request", extra={
    "request_id": "req_xyz",
    "method": "POST",
    "endpoint": "/api/dream/process",
    "status_code": 200,
    "duration_ms": 150.5
})

# Dream processing context
logger.info("Dream processed", extra={
    "dream_id": "dream_789",
    "quantum_coherence": 0.87,
    "emotional_state": "calm",
    "processing_time_ms": 45.2
})

# Error context
logger.error("Operation failed", exc_info=True, extra={
    "error_type": "ValidationError",
    "error_code": "INVALID_INPUT",
    "retry_count": 3,
    "will_retry": False
})
```

---

## Best Practices

### 1. Never Log Sensitive Data

```python
# ❌ INCORRECT: Logging sensitive data
logger.info(f"User password: {password}")
logger.info(f"API key: {api_key}")
logger.info(f"Credit card: {cc_number}")

# ✅ CORRECT: Log sanitized/redacted data
logger.info("User authenticated", extra={"user_id": user_id})
logger.info("API call made", extra={"api_key_prefix": api_key[:8] + "..."})
logger.info("Payment processed", extra={"cc_last_4": cc_number[-4:]})
```

### 2. Use Exception Info

```python
# ✅ CORRECT: Include full traceback with exc_info=True
try:
    result = risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True, extra={"operation": "risky"})
    raise

# ❌ INCORRECT: Losing exception context
except Exception as e:
    logger.error(f"Error: {str(e)}")  # No traceback!
```

### 3. Avoid Expensive String Formatting

```python
# ✅ CORRECT: Lazy evaluation
logger.debug("Processing %s items", len(items))  # Only formats if DEBUG enabled

# ❌ INCORRECT: Always formats, even if not logged
logger.debug(f"Processing {len(expensive_computation())} items")  # Always runs
```

### 4. Log at Appropriate Levels

```python
# ✅ CORRECT: INFO for important events
logger.info("System started successfully")
logger.info("Dream processing completed", extra={"dream_id": dream_id})

# ❌ INCORRECT: DEBUG for important events (will be missed in production)
logger.debug("System started")  # Too low level for important event
```

### 5. Include Timing Information

```python
import time

# ✅ CORRECT: Log operation duration
start_time = time.time()
result = expensive_operation()
duration_ms = (time.time() - start_time) * 1000

logger.info("Operation completed", extra={
    "operation": "dream_processing",
    "duration_ms": duration_ms,
    "items_processed": len(result)
})
```

### 6. Use Consistent Patterns

```python
# ✅ CORRECT: Consistent log message patterns
logger.info("Dream processing started", extra={"dream_id": dream_id})
# ... processing ...
logger.info("Dream processing completed", extra={"dream_id": dream_id, "duration_ms": duration})

# ❌ INCORRECT: Inconsistent patterns
logger.info(f"Starting dream {dream_id}")
# ... processing ...
logger.info(f"Dream done: {dream_id} took {duration}ms")
```

---

## Preventing Duplicate Loggers

### The Problem

Creating multiple logger instances with the same name causes issues:

```python
# ❌ PROBLEM: Multiple logger definitions
import logging

logger = logging.getLogger(__name__)  # First definition
# ... later in file ...
logger = logging.getLogger(__name__)  # Duplicate! Can cause issues
```

### The Solution

LUKHAS uses a **logger cache** to prevent duplicates:

```python
# From labs/core/common/logger.py
_loggers: dict[str, logging.Logger] = {}

def get_logger(name: str) -> logging.Logger:
    """Get or create a logger instance (cached)"""
    if name in _loggers:
        return _loggers[name]  # Return cached instance

    logger = logging.getLogger(name)
    _configure_logger(logger)
    _loggers[name] = logger  # Cache for future calls
    return logger
```

### Rule: One Logger Per File

```python
# ✅ CORRECT: Single logger definition at module level
from labs.core.common import get_logger

logger = get_logger(__name__)

# All functions and classes use this logger
def function_a():
    logger.info("In function A")

def function_b():
    logger.info("In function B")

class MyClass:
    def method(self):
        logger.info("In method")
```

### Checking for Duplicates

```bash
# Find files with multiple logger definitions
grep -n "logger = " **/*.py | awk -F: '{print $1}' | uniq -d

# Or use the automated script
python tools/fix_logger_imports.py --check
```

---

## Linting and Enforcement

### Pre-Commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: check-logger-imports
        name: Check Logger Imports
        entry: python tools/check_logger_standards.py
        language: system
        types: [python]
        pass_filenames: false
```

### Ruff Configuration

Add to `pyproject.toml` or `.ruff.toml`:

```toml
[tool.ruff]
# Enable custom rules for logger checking
select = ["E", "F", "W", "I"]

[tool.ruff.per-file-ignores]
# Exclude logger.py itself from logger checks
"labs/core/common/logger.py" = ["E402"]

[tool.ruff.lint]
# Custom rules for logger standards
logger-import-pattern = "from labs.core.common import get_logger"
max-loggers-per-file = 1
```

### Automated Checker Script

Create `tools/check_logger_standards.py`:

```python
#!/usr/bin/env python3
"""
Check logging standards compliance across codebase.
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

# Patterns to detect
WRONG_PATTERN = re.compile(r'logger\s*=\s*logging\.getLogger\(')
CORRECT_PATTERN = re.compile(r'from\s+labs\.core\.common\s+import\s+get_logger')
LOGGER_DEFINITION = re.compile(r'^\s*logger\s*=\s*')

def check_file(filepath: Path) -> list[str]:
    """Check a single Python file for logging standards violations."""
    violations = []

    try:
        content = filepath.read_text()
        lines = content.split('\n')

        # Check for wrong import pattern
        if WRONG_PATTERN.search(content):
            violations.append(
                f"{filepath}: Uses logging.getLogger() instead of get_logger()"
            )

        # Check for correct import
        has_correct_import = bool(CORRECT_PATTERN.search(content))

        # Count logger definitions
        logger_count = sum(1 for line in lines if LOGGER_DEFINITION.match(line))

        if logger_count > 1:
            violations.append(
                f"{filepath}: Multiple logger definitions ({logger_count} found)"
            )

        # If defines logger but doesn't use correct import
        if logger_count > 0 and not has_correct_import:
            if 'labs/core/common/logger.py' not in str(filepath):
                violations.append(
                    f"{filepath}: Defines logger but missing 'from labs.core.common import get_logger'"
                )

    except Exception as e:
        violations.append(f"{filepath}: Error checking file: {e}")

    return violations

def main():
    """Check all Python files in the repository."""
    violations = []

    # Find all Python files
    python_files = Path('.').rglob('*.py')

    # Exclude certain directories
    excluded_dirs = {'.venv', 'venv', '__pycache__', '.git', 'node_modules'}

    for filepath in python_files:
        # Skip excluded directories
        if any(excluded in filepath.parts for excluded in excluded_dirs):
            continue

        # Check file
        file_violations = check_file(filepath)
        violations.extend(file_violations)

    # Report violations
    if violations:
        print("❌ Logging Standards Violations Found:\n")
        for violation in violations:
            print(f"  {violation}")
        print(f"\n Total: {len(violations)} violation(s)")
        return 1
    else:
        print("✅ All files comply with logging standards")
        return 0

if __name__ == "__main__":
    sys.exit(main())
```

Usage:

```bash
# Check all files
python tools/check_logger_standards.py

# Run as pre-commit hook
pre-commit run check-logger-imports --all-files
```

---

## Integration with Monitoring

### Log Aggregation

LUKHAS logs integrate with standard aggregation systems:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Grafana Loki**
- **Datadog**
- **CloudWatch Logs**
- **Splunk**

### JSON Logging for Production

```python
from labs.core.common import configure_logging
import os

# Configure based on environment
if os.getenv("ENV") == "production":
    configure_logging(
        level="INFO",
        json_output=True,  # JSON for log aggregation
        log_file="/var/log/lukhas/app.log"
    )
else:
    configure_logging(
        level="DEBUG",
        format_type="detailed",  # Human-readable for dev
        json_output=False
    )
```

### Correlation IDs

Add request correlation IDs for tracing:

```python
import uuid
from contextvars import ContextVar

# Request context
request_id_var: ContextVar[str] = ContextVar('request_id', default=None)

def handle_request(request):
    # Generate correlation ID
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)

    # Include in all logs
    logger.info("Processing request", extra={"request_id": request_id})

    try:
        result = process_request(request)
        logger.info("Request completed", extra={"request_id": request_id})
        return result
    except Exception as e:
        logger.error("Request failed", exc_info=True, extra={"request_id": request_id})
        raise
```

### Metrics from Logs

Extract metrics from structured logs:

```python
# Log with metric information
logger.info("Dream processed", extra={
    "dream_id": dream_id,
    "processing_time_ms": duration,
    "coherence_score": coherence,
    "status": "success"
})

# Log aggregation system can create metrics:
# - avg(processing_time_ms) by status
# - p95(processing_time_ms)
# - count(*) where status="success"
```

---

## Migration Guide

### Migrating Legacy Code

#### Step 1: Update Imports

```python
# OLD (❌)
import logging

logger = logging.getLogger(__name__)

# NEW (✅)
from labs.core.common import get_logger

logger = get_logger(__name__)
```

#### Step 2: Remove Custom Configuration

```python
# OLD (❌)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# NEW (✅)
from labs.core.common import get_logger

logger = get_logger(__name__)
# Configuration is centralized
```

#### Step 3: Convert to Structured Logging

```python
# OLD (❌)
logger.info(f"Processing dream {dream_id} for user {user_id}")

# NEW (✅)
logger.info("Processing dream", extra={
    "dream_id": dream_id,
    "user_id": user_id
})
```

#### Step 4: Consolidate Multiple Loggers

```python
# OLD (❌)
logger1 = logging.getLogger("component1")
logger2 = logging.getLogger("component2")

def func1():
    logger1.info("Function 1")

def func2():
    logger2.info("Function 2")

# NEW (✅)
from labs.core.common import get_logger

logger = get_logger(__name__)

def func1():
    logger.info("Function 1", extra={"component": "component1"})

def func2():
    logger.info("Function 2", extra={"component": "component2"})
```

### Automated Migration

Use the migration script:

```bash
# Dry run (shows what would change)
python tools/fix_logger_imports.py --dry-run

# Apply fixes
python tools/fix_logger_imports.py --fix

# Apply to specific files
python tools/fix_logger_imports.py --fix serve/routes.py matriz/consciousness/system.py
```

---

## Troubleshooting

### Problem: No Logs Appearing

**Symptoms**: Logger calls don't produce output

**Solutions**:

1. Check log level:
   ```python
   from labs.core.common import configure_logging
   configure_logging(level="DEBUG")  # Lower level to see more
   ```

2. Verify logger is configured:
   ```python
   from labs.core.common import get_logger
   logger = get_logger(__name__)
   logger.info("Test message")  # Should appear
   ```

3. Check for log level filtering:
   ```python
   # This won't appear if level is INFO
   logger.debug("Debug message")

   # This will appear
   logger.info("Info message")
   ```

### Problem: Duplicate Log Messages

**Symptoms**: Each log appears multiple times

**Solutions**:

1. Check for multiple logger instances:
   ```bash
   grep -c "logger = " your_file.py
   # Should return 1 (or 0 if using class-level logger)
   ```

2. Verify using `get_logger`:
   ```python
   # ✅ CORRECT
   from labs.core.common import get_logger
   logger = get_logger(__name__)

   # ❌ WRONG (can cause duplicates)
   import logging
   logger = logging.getLogger(__name__)
   logger.addHandler(...)  # Don't add handlers manually
   ```

3. Clear existing handlers:
   ```python
   # The get_logger function handles this automatically
   # But if migrating, may need to clear old handlers
   logger.handlers.clear()
   ```

### Problem: JSON Formatting Not Working

**Symptoms**: Logs not in JSON format in production

**Solutions**:

1. Enable JSON output:
   ```python
   from labs.core.common import configure_logging
   configure_logging(json_output=True)
   ```

2. Verify configuration:
   ```python
   from labs.core.common import _logging_config
   print(_logging_config.get("json_output"))  # Should be True
   ```

3. Check environment:
   ```python
   import os
   if os.getenv("ENV") == "production":
       configure_logging(json_output=True)
   ```

### Problem: Missing Extra Fields

**Symptoms**: `extra` dictionary not appearing in logs

**Solutions**:

1. Use JSON formatter:
   ```python
   configure_logging(json_output=True)
   logger.info("Message", extra={"key": "value"})
   # Extra fields appear in JSON output
   ```

2. Use custom formatter for text logs:
   ```python
   # Extra fields are available in custom formatters
   # See labs/core/common/logger.py for examples
   ```

---

## Summary

### Quick Reference

| Task | Command |
|------|---------|
| **Get Logger** | `from labs.core.common import get_logger` <br> `logger = get_logger(__name__)` |
| **Basic Logging** | `logger.info("Message")` |
| **Structured Logging** | `logger.info("Event", extra={"key": "value"})` |
| **Error Logging** | `logger.error("Error", exc_info=True)` |
| **Configure Logging** | `configure_logging(level="INFO", json_output=True)` |
| **Check Standards** | `python tools/check_logger_standards.py` |

### Checklist

Before committing code:

- [ ] Using `from labs.core.common import get_logger`
- [ ] Only ONE logger definition per file
- [ ] Using `logger = get_logger(__name__)`
- [ ] Including `extra` dict for structured data
- [ ] Using `exc_info=True` for exceptions
- [ ] Not logging sensitive data (passwords, keys, PII)
- [ ] Using appropriate log levels
- [ ] Linting passes: `python tools/check_logger_standards.py`

### Common Patterns

```python
# Module setup
from labs.core.common import get_logger

logger = get_logger(__name__)

# INFO: Important events
logger.info("Operation started", extra={"operation_id": op_id})

# DEBUG: Detailed diagnostics
logger.debug("Variable state", extra={"value": value})

# WARNING: Potential issues
logger.warning("Rate limit approaching", extra={"usage": 95, "limit": 100})

# ERROR: Failures (with traceback)
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True, extra={"operation": "risky"})

# CRITICAL: System-critical failures
logger.critical("Service unavailable", exc_info=True, extra={"service": "database"})
```

---

## Resources

**Implementation Files**:
- [labs/core/common/logger.py](../../labs/core/common/logger.py) - Logger implementation
- [labs/core/common/__init__.py](../../labs/core/common/__init__.py) - Common utilities

**Tools**:
- [tools/check_logger_standards.py](../../tools/check_logger_standards.py) - Standards checker
- [tools/fix_logger_imports.py](../../tools/fix_logger_imports.py) - Migration tool

**Related Documentation**:
- [Prometheus Monitoring Guide](../operations/PROMETHEUS_MONITORING_GUIDE.md)
- [Development Standards](./T4_DEVELOPMENT_STANDARDS.md)

**External Resources**:
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Structured Logging Best Practices](https://www.structlog.org/en/stable/)
- [The 12-Factor App: Logs](https://12factor.net/logs)

---

**Last Updated**: 2025-01-10
**Version**: 1.0.0
**Status**: ✅ Production Ready

🤖 Generated with Claude Code
