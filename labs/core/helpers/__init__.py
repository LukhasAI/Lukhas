import logging
import time
from datetime import datetime, timezone

import streamlit as st

logger = logging.getLogger(__name__)
# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# MODULE: core.helpers
# DESCRIPTION: Initializes the core.helpers module. This module provides various utility functions
#              for common tasks such as logging, data conversions, string operations, etc.
# DEPENDENCIES: structlog, datetime, re, json
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import datetime
import json
import re
from typing import Any, Optional

import structlog

# ΛTRACE: Initializing logger for core.helpers
log = structlog.get_logger(__name__)
log.info("core.helpers module initialized")  # ΛNOTE: Basic initialization logging for helper utilities.

# --- String Manipulation Utilities ---

# ΛUTIL


def sanitize_string_for_logging(input_string: Optional[str]) -> str:
    """
    Sanitizes a string to remove potentially sensitive information or control characters
    before logging or displaying it.
    # ΛNOTE: Important for preventing log injection or corruption.
    # ΛCAUTION: Sanitization rules might need to be adjusted based on specific security requirements.
    """
    if input_string is None:
        return ""
    # AINFER: Basic inference of sensitive patterns (e.g., looks like an API key)
    # This is a placeholder for more sophisticated pattern matching if needed.
    if re.search(r"(?:api_key|password|secret|token)", input_string, re.IGNORECASE):  # ΛNOTE: Basic keyword check
        # ΛTRACE: Detected potentially sensitive keyword in string
        log.debug("Sanitizing potentially sensitive string for logging.")
        return "[REDACTED_SENSITIVE_STRING]"

    # Remove common control characters except newline and tab
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", input_string)
    return sanitized


# ΛUTIL


def truncate_string(input_string: Optional[str], max_length: int = 100, ellipsis: str = "...") -> str:
    """
    Truncates a string to a maximum length, adding an ellipsis if truncated.
    # ΛNOTE: Useful for displaying long strings in UIs or concise log messages.
    """
    if input_string is None:
        return ""
    if len(input_string) > max_length:
        # ΛTRACE: Truncating string
        log.debug(
            "Truncating string",
            original_length=len(input_string),
            max_length=max_length,
        )
        return input_string[: max_length - len(ellipsis)] + ellipsis
    return input_string


# --- Data Conversion Utilities ---

# ΛUTIL


def safe_json_loads(json_string: Optional[str], default: Any = None) -> Any:
    """
    Safely parses a JSON string. Returns a default value if parsing fails.
    # ΛNOTE: Prevents crashes due to malformed JSON.
    # ΛCAUTION: Ensure the default value is appropriate for the expected data structure.
    """
    if json_string is None:
        return default
    try:
        # AINFER: Attempting to infer JSON structure from string
        # ΛTRACE: Attempting to parse JSON string
        data = json.loads(json_string)
        log.debug("Successfully parsed JSON string", string_length=len(json_string))
        return data
    except json.JSONDecodeError as e:
        # ΛTRACE: JSON parsing failed
        log.warning(
            "Failed to parse JSON string",
            error=str(e),
            input_string=truncate_string(json_string, 200),
        )
        return default


# ΛUTIL


def to_bool(value: Any) -> bool:
    """
    Converts a common variety of truthy/falsy values to a boolean.
    # ΛNOTE: Handles string representations of booleans like "true", "false", "1", "0".
    # AINFER: Infers boolean value from various input types.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        val_lower = value.lower().strip()
        if val_lower in ("true", "yes", "1", "on"):
            return True
        if val_lower in ("false", "no", "0", "off"):
            return False
    if isinstance(value, (int, float)):
        return value != 0
    # ΛTRACE: Could not convert value to bool, returning False
    log.debug(
        "Value could not be reliably converted to boolean, defaulting to False",
        value_type=type(value),
    )
    return False


# --- DateTime Utilities ---

# ΛUTIL


def get_utc_timestamp(format_string: str = "%Y-%m-%dT%H:%M:%S.%fZ") -> str:
    """
    Returns the current UTC timestamp formatted as a string.
    # ΛNOTE: Standardizes timestamp generation to UTC.
    """
    # ΛTRACE: Generating UTC timestamp
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(format_string)
    log.debug("Generated UTC timestamp", timestamp=timestamp)
    return timestamp


# --- Collection Utilities ---

# ΛUTIL


def get_nested_value(data: dict, path: str, delimiter: str = ".", default: Any = None) -> Any:
    """
    Retrieves a value from a nested dictionary using a path string.
    Example: get_nested_value({"a": {"b": {"c": 1}, "a.b.c") -> 1
    # ΛNOTE: Useful for accessing deeply nested configuration or data.
    # AINFER: Navigates nested structure based on path.
    """
    # ΛTRACE: Attempting to get nested value
    log.debug("Getting nested value", path=path, has_data=data is not None)
    keys = path.split(delimiter)
    current_level = data
    for key in keys:
        if isinstance(current_level, dict) and key in current_level:
            current_level = current_level[key]
        elif isinstance(current_level, list):
            try:
                idx = int(key)
                if 0 <= idx < len(current_level):
                    current_level = current_level[idx]
                else:
                    log.warning(
                        "Index out of bounds while getting nested value",
                        key=key,
                        path=path,
                        list_size=len(current_level),
                    )
                    return default
            except ValueError:
                log.warning(
                    "Invalid index for list while getting nested value",
                    key=key,
                    path=path,
                )
                return default
        else:
            log.debug(
                "Key not found or invalid type while getting nested value",
                key=key,
                path=path,
                current_level_type=type(current_level),
            )
            return default
    return current_level


# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# VERSION: 1.0.0
# TIER SYSTEM: CORE_UTILITIES
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Provides common helper functions for string manipulation, data conversion,
#               datetime operations, and collection handling.
# FUNCTIONS: sanitize_string_for_logging, truncate_string, safe_json_loads, to_bool,
#            get_utc_timestamp, get_nested_value
# CLASSES: N/A
# DECORATORS: N/A
# DEPENDENCIES: structlog, datetime, re, json, typing
# INTERFACES: Functions are imported and used by various LUKHAS modules.
# ERROR HANDLING: Functions include error handling (e.g., safe_json_loads) and log warnings.
# LOGGING: ΛTRACE_ENABLED (structlog for module initialization and function operations)
# AUTHENTICATION: N/A
# HOW TO USE:
#   from lukhas.core.helpers import sanitize_string_for_logging, get_utc_timestamp
#   clean_log_message = sanitize_string_for_logging(user_input)
#   current_time_utc = get_utc_timestamp()
# INTEGRATION NOTES: These helpers are general-purpose. For domain-specific utilities,
#                    consider placing them in more specialized modules.
# MAINTENANCE: Add new general-purpose helper functions here. Ensure they are well-documented,
#              robust, and include logging. Add unit tests for new helpers.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
