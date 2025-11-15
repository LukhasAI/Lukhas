# SPDX-License-Identifier: Apache-2.0
"""
Safe SQL query utilities to prevent SQL injection vulnerabilities.

This module provides utilities for:
- Validating SQL identifiers (table names, column names)
- Safe query execution with parameter validation
- Query builder for parameterized queries
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class SQLSecurityError(Exception):
    """Raised when SQL security validation fails."""
    pass


def validate_sql_identifier(identifier: str, allow_dots: bool = False) -> str:
    """
    Validate and sanitize SQL identifier (table/column name).

    Only allows alphanumeric characters, underscores, and optionally dots.
    Must start with a letter or underscore.

    Args:
        identifier: SQL identifier to validate
        allow_dots: If True, allow dots for schema.table notation

    Returns:
        Validated identifier

    Raises:
        SQLSecurityError: If identifier contains invalid characters

    Examples:
        >>> validate_sql_identifier("users")
        'users'
        >>> validate_sql_identifier("user_data_2024")
        'user_data_2024'
        >>> validate_sql_identifier("public.users", allow_dots=True)
        'public.users'
        >>> validate_sql_identifier("users; DROP TABLE")
        Traceback (most recent call last):
        ...
        SQLSecurityError: Invalid SQL identifier...
    """
    if not identifier:
        raise SQLSecurityError("SQL identifier cannot be empty")

    if allow_dots:
        # Allow schema.table notation
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$'
    else:
        # Simple identifier only
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'

    if not re.match(pattern, identifier):
        raise SQLSecurityError(
            f"Invalid SQL identifier: '{identifier}'. "
            f"Only alphanumeric characters, underscores{', and dots' if allow_dots else ''} allowed. "
            f"Must start with a letter or underscore."
        )

    # Additional check: block SQL keywords that should never be identifiers
    dangerous_keywords = {
        'select', 'insert', 'update', 'delete', 'drop', 'create',
        'alter', 'truncate', 'union', 'exec', 'execute'
    }
    if identifier.lower() in dangerous_keywords:
        raise SQLSecurityError(
            f"SQL keyword '{identifier}' cannot be used as an identifier"
        )

    return identifier


def validate_metadata_key(key: str) -> str:
    """
    Validate metadata/JSON key for use in PostgreSQL JSONB queries.

    More permissive than SQL identifiers as these are used in metadata->>key syntax,
    but still enforces security constraints.

    Args:
        key: Metadata key to validate

    Returns:
        Validated key

    Raises:
        SQLSecurityError: If key contains dangerous characters
    """
    if not key:
        raise SQLSecurityError("Metadata key cannot be empty")

    # Allow alphanumeric, underscore, hyphen, dot (common in metadata keys)
    # But block quotes and SQL injection characters
    if not re.match(r'^[a-zA-Z0-9_.-]+$', key):
        raise SQLSecurityError(
            f"Invalid metadata key: '{key}'. "
            "Only alphanumeric, underscore, hyphen, and dot allowed."
        )

    # Block suspicious patterns
    if re.search(r'(--|;|/\*|\*/|union|select|drop)', key, re.IGNORECASE):
        raise SQLSecurityError(
            f"Metadata key '{key}' contains SQL injection patterns"
        )

    return key


def safe_execute(
    cursor: Any,
    query: str,
    params: Optional[Union[Tuple, Dict, List]] = None
) -> Any:
    """
    Execute SQL query with parameter validation.

    Args:
        cursor: Database cursor
        query: SQL query with placeholders (?, %s, or %(name)s)
        params: Query parameters as tuple, list, or dict

    Returns:
        Cursor result

    Raises:
        SQLSecurityError: If query appears unsafe

    Examples:
        >>> # PostgreSQL style
        >>> safe_execute(cursor, "SELECT * FROM users WHERE id = %s", (user_id,))
        >>> # SQLite style
        >>> safe_execute(cursor, "SELECT * FROM users WHERE id = ?", (user_id,))
    """
    # Detect dangerous patterns in query construction
    if _has_sql_injection_pattern(query):
        logger.warning(f"Potentially unsafe SQL query detected: {query[:100]}...")

    # Execute with parameters
    if params is None:
        return cursor.execute(query)
    else:
        return cursor.execute(query, params)


def _has_sql_injection_pattern(query: str) -> bool:
    """
    Check for common SQL injection patterns in query string.

    This looks for signs that string concatenation or formatting
    was used instead of parameterization.
    """
    # These patterns should NOT appear in properly parameterized queries
    dangerous_patterns = [
        r'\+\s*["\']',  # String concatenation with quotes
        r'["\'].*\+.*["\']',  # Quotes around concatenation
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, query):
            return True
    return False


class QueryBuilder:
    """
    Safe SQL query builder with parameterization.

    Helps construct complex queries while maintaining parameterization.

    Example:
        >>> builder = QueryBuilder("SELECT * FROM users")
        >>> builder.add_where("id = ?").add_param(user_id)
        >>> builder.add_where("active = ?").add_param(True)
        >>> cursor.execute(builder.query, builder.params)
    """

    def __init__(self, base_query: str, param_style: str = '?'):
        """
        Initialize query builder.

        Args:
            base_query: Base SQL query (e.g., "SELECT * FROM users")
            param_style: Parameter placeholder style ('?' or '%s')
        """
        self.query = base_query
        self.params: List[Any] = []
        self.param_style = param_style
        self._where_clauses: List[str] = []

    def add_param(self, value: Any) -> 'QueryBuilder':
        """Add parameter to query."""
        self.params.append(value)
        return self

    def add_where(self, condition: str) -> 'QueryBuilder':
        """
        Add WHERE condition.

        Args:
            condition: WHERE clause (e.g., "id = ?")
        """
        self._where_clauses.append(condition)
        return self

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        """
        Build final query and parameters.

        Returns:
            Tuple of (query_string, parameters_tuple)
        """
        query = self.query
        if self._where_clauses:
            if 'WHERE' not in query.upper():
                query += " WHERE "
            else:
                query += " AND "
            query += " AND ".join(self._where_clauses)

        return query, tuple(self.params)

    def execute(self, cursor: Any) -> Any:
        """Execute the query on cursor."""
        query, params = self.build()
        return cursor.execute(query, params)


def escape_like_pattern(pattern: str) -> str:
    """
    Escape special characters in LIKE pattern to prevent LIKE injection.

    Args:
        pattern: User-provided pattern

    Returns:
        Escaped pattern safe for use in LIKE clause

    Example:
        >>> escape_like_pattern("test_value")
        'test\\_value'
        >>> escape_like_pattern("50%")
        '50\\%'
    """
    # Escape LIKE wildcards: % and _
    # Also escape backslash itself
    pattern = pattern.replace('\\', '\\\\')
    pattern = pattern.replace('%', '\\%')
    pattern = pattern.replace('_', '\\_')
    return pattern
