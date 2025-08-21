# README for core/helpers/

## Overview

The `core/helpers/` directory provides a collection of general-purpose utility functions designed to assist with common tasks across the LUKHAS AI system. These helpers cover areas such as string manipulation, data conversion, datetime operations, and handling of collections.

The primary aim of this module is to offer robust, reusable, and well-documented utility functions that simplify development, reduce code duplication, and ensure consistency in performing common operations.

## Symbolic Notes & Conventions

-   **`# ΛUTIL`**: This tag is applied to all primary functions within this module, signifying their role as utility helpers.
-   **`# ΛNOTE`**: Provides context, rationale, or important considerations regarding the utility function's behavior or usage.
-   **`# ΛCAUTION`**: Used for utilities where misuse or specific input conditions might lead to unexpected behavior or security concerns (e.g., sanitization functions, default values in parsers).
-   **`# AINFER`**: Marks functions or logic within functions that perform some form of inference or intelligent interpretation of data, such as inferring boolean values from strings, attempting to parse JSON, or navigating nested data structures.
-   **Symbolic Transformation Logic**: Utilities involved in transforming data (e.g., `sanitize_string_for_logging`, `safe_json_loads`, `to_bool`, `get_nested_value`) are of particular interest as they often involve symbolic interpretation or conversion. These are typically tagged with `# AINFER`.
-   **Headers/Footers**: All Python files (primarily `__init__.py` in this case) must include the standardized header and footer blocks.
-   **Logging**: All helper functions should use `structlog` for logging their operations, especially for `# ΛTRACE` points or warnings.

## Key Utilities

The `core.helpers` module (currently via its `__init__.py`) provides the following key utilities:

### String Manipulation
-   **`sanitize_string_for_logging(input_string: Optional[str]) -> str`**:
    -   Removes control characters and redacts basic sensitive patterns from strings before logging.
    -   `# ΛNOTE`: Important for log security. `# ΛCAUTION`: Rules may need tuning. `# AINFER`: Basic sensitive pattern inference.
-   **`truncate_string(input_string: Optional[str], max_length: int = 100, ellipsis: str = "...") -> str`**:
    -   Truncates a string to a specified maximum length, adding an ellipsis.
    -   `# ΛNOTE`: Useful for concise display in logs or UI.

### Data Conversion
-   **`safe_json_loads(json_string: Optional[str], default: Any = None) -> Any`**:
    -   Safely parses a JSON string, returning a default value on error.
    -   `# ΛNOTE`: Prevents crashes from malformed JSON. `# AINFER`: Attempts JSON parsing.
-   **`to_bool(value: Any) -> bool`**:
    -   Converts various truthy/falsy values (strings like "true", "1"; numbers) to a boolean.
    -   `# ΛNOTE`: Standardizes boolean conversion. `# AINFER`: Infers boolean from input.

### DateTime Utilities
-   **`get_utc_timestamp(format_string: str = "%Y-%m-%dT%H:%M:%S.%fZ") -> str`**:
    -   Returns the current UTC timestamp as a formatted string.
    -   `# ΛNOTE`: Ensures consistent UTC timestamping.

### Collection Utilities
-   **`get_nested_value(data: Dict, path: str, delimiter: str = '.', default: Any = None) -> Any`**:
    -   Retrieves a value from a nested dictionary or list using a dot-delimited path string.
    -   `# ΛNOTE`: Simplifies access to deeply nested data. `# AINFER`: Navigates data structure.

## Intended Symbolic Logic & Use in Diagnostics/Drift Analysis

-   **Symbolic Transformation**: Functions like `safe_json_loads`, `to_bool`, and `get_nested_value` are critical in scenarios where data from various sources (potentially less structured or symbolic in nature) needs to be reliably converted or accessed. Their robustness and clear logging (via `# ΛTRACE`) are important for understanding how symbolic information is processed.
-   **Relevance to Diagnostics/Drift Analysis**:
    -   `sanitize_string_for_logging` and `truncate_string` are vital for producing clean, readable, and secure diagnostic logs.
    -   `get_utc_timestamp` ensures that all diagnostic events and drift metrics can be accurately time-sequenced.
    -   `safe_json_loads` can be used in diagnostic tools that consume or analyze structured log outputs or configuration states, ensuring resilience against malformed data.
    -   `get_nested_value` can be invaluable for diagnostic scripts that need to extract specific metrics or state variables from complex, nested data structures reported by system components. This allows for targeted monitoring and drift detection.
    -   If helper functions are specifically reused by `core/diagnostic_engine/` or similar drift analysis tools, this should be noted or such tools should directly import them.

## How to Use

Import functions directly from the `core.helpers` module:
```python
from core.helpers import truncate_string, safe_json_loads, get_utc_timestamp

timestamp = get_utc_timestamp()
log_message = f"{timestamp} - Processing data: {truncate_string(very_long_data_summary, 50)}"

config_value = safe_json_loads(raw_config_string)
if config_value:
    # Use parsed config
    pass
```

## Contribution Guidelines

-   New helper functions should be general-purpose and not tied to specific business logic of a single component.
-   Ensure comprehensive docstrings, type hinting, and robust error handling.
-   Add `structlog` logging for important operations or decisions within the helper.
-   Follow the established ΛTAG conventions.
-   Write unit tests for all new helper functions to ensure reliability.
-   Update this README when new key utilities are added or significant changes are made.

## Overlap Tracking
Any identified overlaps with other utility modules or potential for refactoring will be noted in `JULES06_OVERLAP_TRACKER.md`.
