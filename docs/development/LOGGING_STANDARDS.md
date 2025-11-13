# LUKHAS Logging Standards Guide

**Version:** 1.0
**Status:** Adopted
**Last Updated:** 2025-11-10

## 1. Introduction

Effective logging is critical to the health, observability, and maintainability of the LUKHAS AI Platform. Standardized logging practices allow us to:

-   **Debug effectively:** Quickly identify and resolve issues in a complex, distributed system.
-   **Monitor system health:** Create automated alerts and dashboards based on log data.
-   **Perform security audits:** Maintain a clear and structured record of system events.
-   **Understand application behavior:** Analyze performance and usage patterns.

This document outlines the official logging standards for all Python services within the LUKHAS ecosystem. Adherence to these standards is mandatory for all new code and is expected for all refactored legacy code.

## 2. The Standardized Logger Pattern

The cornerstone of our logging strategy is a consistent pattern for instantiating loggers. The correct pattern ensures that our logging is hierarchical, configurable, and free from common issues like duplicate messages.

### The Correct Pattern: One Logger Per Module

Every Python module (`.py` file) should define its own logger instance at the module level. The logger should be named after the module's full import path. The standard library handles this automatically when using the `__name__` special variable.

```python
# in file: lukhas/core/orchestration/async_orchestrator.py
import logging

# CORRECT: Logger is defined at the module level using __name__
logger = logging.getLogger(__name__)

class AsyncOrchestrator:
    def run_pipeline(self):
        logger.info("Asynchronous pipeline starting.")
        # ... logic ...
        logger.debug("Pipeline completed.", extra_details={"stages": 5})

```

**Why this is correct:**

-   **Hierarchy:** `logging.getLogger(__name__)` creates a logger named `lukhas.core.orchestration.async_orchestrator`. This allows us to configure log levels for entire sub-packages (e.g., set `lukhas.core` to `DEBUG` without affecting other modules).
-   **No Name Collisions:** It automatically prevents two different modules from using the same logger name.
-   **Readability:** It's a universally recognized Python idiom.

### Incorrect Patterns to Avoid

**Anti-Pattern 1: Hardcoded Logger Name**

```python
# INCORRECT
import logging
logger = logging.getLogger("my_orchestrator") # Avoid hardcoded strings
```
*Reasoning:* This breaks the module hierarchy and increases the risk of name collisions.

**Anti-Pattern 2: Root Logger Abuse**

```python
# INCORRECT
import logging

def some_function():
    logging.info("A log message from the root logger.") # Avoid using the root logger directly
```
*Reasoning:* Directly using `logging.info()` logs to the root logger. This is difficult to control and configure, as it's the parent of all other loggers. It should only be configured at the application's entry point, not used for logging within modules.

**Anti-Pattern 3: Logger Instantiation Inside Functions/Methods**

```python
# INCORRECT
import logging

class MyClass:
    def do_work(self):
        logger = logging.getLogger(__name__) # Avoid creating loggers inside functions/methods
        logger.info("Doing work.")
```
*Reasoning:* This is inefficient as it re-creates the logger object on every call. It can also interfere with logging configuration and lead to memory leaks if not managed carefully.

## 3. Structured Logging

To make our logs machine-readable and powerfully searchable, LUKHAS uses **structured logging**. Instead of embedding variables into a log string, we pass them as a dictionary of key-value pairs. Our primary tool for this is `structlog`.

### Best Practices for Structured Logging

1.  **Bind Context Early:** Bind important, long-lived context to the logger as early as possible. This context will be automatically included in all subsequent log messages from that logger instance.

    ```python
    import structlog

    logger = structlog.get_logger(__name__)

    def process_request(request):
        # Bind context that is relevant for the entire request
        request_logger = logger.bind(
            request_id=request.id,
            user_id=request.user.id,
            tenant_id=request.user.tenant_id,
        )

        request_logger.info("request_received")
        # ... do work ...
        request_logger.info("request_completed", status_code=200)
    ```

2.  **Log Events, Not Sentences:** The primary log message should be a short, static string that identifies the event, like a metric name. All dynamic information should be in the key-value pairs.

    ```python
    # GOOD: The event is static, details are in the context
    logger.info("user_login_success", user_id="usr_123")

    # AVOID: The event is dynamic and hard to query
    user_id = "usr_123"
    logger.info(f"User {user_id} successfully logged in.")
    ```

3.  **Use Consistent Key Naming:** Adhere to a `snake_case` convention for all log keys. Use consistent names for the same data across the entire platform (e.g., always use `user_id`, not `userID` or `user`).

## 4. Log Level Guidelines

Choosing the correct log level is essential for keeping our logs useful and avoiding excessive noise in production.

| Level      | When to Use                                                                                                | Example                                                                          |
| :--------- | :--------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------- |
| **`DEBUG`**    | Detailed diagnostic information. Useful only for developers actively debugging a specific component. Should be disabled in production. | `logger.debug("cache_miss", key="user:123", db_query="SELECT ...")`                |
| **`INFO`**     | High-level confirmation of normal, significant application events. | `logger.info("service_startup", port=8000)` <br> `logger.info("request_handled", path="/v1/chat", status=200)` |
| **`WARNING`**  | An unexpected event occurred, or a potential problem was detected, but the application is still functioning correctly. Requires human attention eventually. | `logger.warning("deprecated_api_called", endpoint="/v1/legacy")` <br> `logger.warning("config_fallback", key="timeout", value=5)` |
| **`ERROR`**    | A specific operation failed due to a serious error. The request could not be completed, but the application itself is not crashing. | `logger.error("database_query_failed", error="timeout", query="...")` <br> `logger.error("file_not_found", path="/data/model.bin")` |
| **`CRITICAL`** | A severe error that may prevent the application from continuing to run. This indicates a catastrophic failure. | `logger.critical("database_connection_lost")` <br> `logger.critical("missing_critical_config", key="ENCRYPTION_KEY")` |

## 5. Integration with the Observability Stack

All logs produced by LUKHAS services are shipped to a central observability platform (e.g., Datadog, ELK Stack). The structured nature of our logs is what makes this integration powerful.

-   **Search and Filtering:** We can easily filter logs by any context attribute, such as `tenant_id` or `request_id`, to trace a single request's journey across multiple services.
-   **Dashboards:** We can build dashboards that visualize key events, such as login rates (`"user_login_success"`), error rates (`level:error`), and more.
-   **Automated Alerts:** We can create alerts that trigger on specific log patterns, such as a spike in `ERROR` or `CRITICAL` messages from a particular service.

## 6. Enforcing Standards with Linting

To maintain these standards, we employ automated checks using `ruff` and `pre-commit`.

### Ruff Configuration (`.ruff.toml`)

To enforce these logging standards, we enable specific rules from the `flake8-logging-format` (G) and `flake8-logging` (LOG) plugins within our `ruff` configuration.

```toml
# .ruff.toml or pyproject.toml
[tool.ruff]
# ... other config ...

[tool.ruff.lint]
select = [
    "E", "F", "W", # Standard flake8 rules
    "G",           # Enforce flake8-logging-format
    "LOG",         # Enforce flake8-logging
]

# Optional: Ignore specific rules if necessary, but avoid this for logging rules.
# ignore = ["G004"]
```

**Key Rules to Enable:**

-   **`G001`, `G002`, `G003`, `G004`:** These rules ban the use of `str.format`, `%` formatting, `+` concatenation, and f-strings in logging calls, respectively. This is the primary mechanism for enforcing structured logging.
-   **`LOG002`:** Ensures `logging.getLogger(__name__)` is used, maintaining the logger hierarchy.
-   **`LOG007`:** Prevents incorrect usage of `logging.exception`.
-   **`G010`:** Enforces the use of `logging.warning` over the deprecated `logging.warn`.

This configuration ensures that violations of our core logging principles are caught automatically.

### Pre-Commit Hooks (`.pre-commit-config.yaml`)

The `ruff` checks are integrated into our pre-commit hooks to catch violations before code is even committed.

```yaml
# .pre-commit-config.yaml
-   repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
    -   id: ruff
        args: [--fix, --exit-non-zero-on-fix]
```

## 7. Migration Guide for Legacy Code

When refactoring older parts of the codebase, follow these steps to align with current logging standards.

### Example: Before Refactoring

```python
# Old, non-standard logging
import logging

def process_data(data, user):
    logging.warn("Processing data for user %s with %d items." % (user, len(data)))
    try:
        # ... logic ...
        result = complex_operation()
        logging.debug("Operation returned: " + str(result))
    except Exception as e:
        logging.error("Failed to process data! Error: " + str(e))

```

### Example: After Refactoring

```python
# New, standardized logging
import structlog

logger = structlog.get_logger(__name__)

def process_data(data, user):
    log = logger.bind(user_id=user.id, item_count=len(data))
    log.info("data_processing_started")
    try:
        # ... logic ...
        result = complex_operation()
        log.debug("complex_operation_result", result=result)
    except Exception as e:
        # The exception info will be automatically added by the logger
        log.exception("data_processing_failed")

```

**Key Changes:**
1.  A module-level, structured logger (`structlog`) was introduced.
2.  `logging.warn` was changed to `log.warning` (the correct method name).
3.  String formatting was replaced with key-value pairs.
4.  `log.exception()` is used inside the `except` block, which automatically captures the stack trace.

## 8. Automated Checks and Tools

### Checking for Duplicate Loggers

Run this command to find files with multiple logger definitions:

```bash
# Find potential duplicate logger definitions
grep -r "logger = " --include="*.py" . | \
  awk -F: '{print $1}' | sort | uniq -c | \
  awk '$1 > 1 {print "⚠️  " $2 " has " $1 " logger definitions"}'
```

### Automated Fix Script

Use `scripts/fix_duplicate_loggers.py` to automatically fix common logging issues:

```bash
# Dry run - shows what would be changed
python scripts/fix_duplicate_loggers.py --dry-run

# Apply fixes
python scripts/fix_duplicate_loggers.py

# Fix specific directory
python scripts/fix_duplicate_loggers.py --path lukhas/core
```

The script will:
- Remove duplicate logger definitions in the same file
- Replace `logging.warn` with `logging.warning`
- Replace root logger calls with module-level loggers
- Standardize to `logger = logging.getLogger(__name__)` pattern

### Running Linting Checks

```bash
# Check logging standards with ruff
ruff check --select G,LOG .

# Auto-fix where possible
ruff check --select G,LOG --fix .

# Run as part of pre-commit
pre-commit run ruff --all-files
```

## 9. Troubleshooting Common Issues

### Duplicate Log Messages

-   **Cause:** This typically happens when a handler is added to a logger that already has a handler, or whose parent logger has a handler. Log records propagate up the hierarchy (e.g., from `lukhas.core.orchestration` to `lukhas.core` to `lukhas` to the root logger).
-   **Solution:**
    1.  **NEVER** call `logging.basicConfig()` or `logger.addHandler()` in library code (i.e., any module that isn't the main entry point of an application).
    2.  Configuration should happen **ONCE** at the application's startup.
    3.  Ensure `propagate = False` is set on a logger if you are giving it a specific handler and want to prevent its messages from also going to the parent handlers.

### Logger Not Found / Import Errors

-   **Cause:** Incorrect import statement or logger instantiation
-   **Solution:** Always use the standard pattern:
    ```python
    import logging
    logger = logging.getLogger(__name__)  # At module level
    ```

### Performance Impact of Logging

-   **Cause:** Expensive string formatting in log calls, especially at DEBUG level in production
-   **Solution:** Use lazy formatting and appropriate log levels
    ```python
    # GOOD: Lazy evaluation
    logger.debug("Processing %d items", len(items))

    # AVOID: Eager string formatting
    logger.debug(f"Processing {len(items)} items")  # Evaluated even if DEBUG disabled
    ```
