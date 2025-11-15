# SPDX-License-Identifier: Apache-2.0
"""
Comprehensive SQL injection security tests.

Tests for:
- SQL identifier validation (table names, column names)
- Metadata key validation
- Safe query execution
- QueryBuilder functionality
- SQL injection prevention
"""
import pytest
import sqlite3
from lukhas.security import (
    SQLSecurityError,
    QueryBuilder,
    escape_like_pattern,
    safe_execute,
    validate_metadata_key,
    validate_sql_identifier,
)


class TestSQLIdentifierValidation:
    """Test SQL identifier validation functions."""

    def test_valid_identifiers(self):
        """Test that valid SQL identifiers are accepted."""
        # Simple identifiers
        assert validate_sql_identifier("users") == "users"
        assert validate_sql_identifier("user_data") == "user_data"
        assert validate_sql_identifier("table_2024") == "table_2024"
        assert validate_sql_identifier("_private") == "_private"
        assert validate_sql_identifier("UsersTable") == "UsersTable"

    def test_schema_table_notation(self):
        """Test schema.table notation is accepted."""
        assert validate_sql_identifier("public.users", allow_dots=True) == "public.users"
        assert validate_sql_identifier("mydb.mytable", allow_dots=True) == "mydb.mytable"
        assert validate_sql_identifier("schema.catalog.table", allow_dots=True) == "schema.catalog.table"

    def test_invalid_identifiers_rejected(self):
        """Test that SQL injection attempts are rejected."""
        # SQL injection attempts
        with pytest.raises(SQLSecurityError):
            validate_sql_identifier("users; DROP TABLE")

        with pytest.raises(SQLSecurityError):
            validate_sql_identifier("users--")

        with pytest.raises(SQLSecurityError):
            validate_sql_identifier("users'")

        with pytest.raises(SQLSecurityError):
            validate_sql_identifier("users/*")

        with pytest.raises(SQLSecurityError):
            validate_sql_identifier("users OR 1=1")

        # Special characters
        with pytest.raises(SQLSecurityError):
            validate_sql_identifier("users@table")

        with pytest.raises(SQLSecurityError):
            validate_sql_identifier("users$table")

        with pytest.raises(SQLSecurityError):
            validate_sql_identifier("users#table")

    def test_sql_keywords_rejected(self):
        """Test that SQL keywords are rejected as identifiers."""
        keywords = ['select', 'insert', 'update', 'delete', 'drop', 'create']
        for keyword in keywords:
            with pytest.raises(SQLSecurityError):
                validate_sql_identifier(keyword)
            with pytest.raises(SQLSecurityError):
                validate_sql_identifier(keyword.upper())

    def test_empty_identifier_rejected(self):
        """Test that empty identifiers are rejected."""
        with pytest.raises(SQLSecurityError):
            validate_sql_identifier("")

    def test_dots_not_allowed_without_flag(self):
        """Test that dots are rejected unless allow_dots=True."""
        with pytest.raises(SQLSecurityError):
            validate_sql_identifier("public.users", allow_dots=False)


class TestMetadataKeyValidation:
    """Test metadata key validation functions."""

    def test_valid_metadata_keys(self):
        """Test that valid metadata keys are accepted."""
        assert validate_metadata_key("source") == "source"
        assert validate_metadata_key("user_id") == "user_id"
        assert validate_metadata_key("created-at") == "created-at"
        assert validate_metadata_key("data.field") == "data.field"
        assert validate_metadata_key("key123") == "key123"

    def test_invalid_metadata_keys_rejected(self):
        """Test that SQL injection attempts in metadata keys are rejected."""
        # SQL injection attempts
        with pytest.raises(SQLSecurityError):
            validate_metadata_key("source'; DROP TABLE users--")

        with pytest.raises(SQLSecurityError):
            validate_metadata_key("key' OR '1'='1")

        with pytest.raises(SQLSecurityError):
            validate_metadata_key("key--comment")

        with pytest.raises(SQLSecurityError):
            validate_metadata_key("key/*comment*/")

        # SQL keywords in keys
        with pytest.raises(SQLSecurityError):
            validate_metadata_key("select")

        with pytest.raises(SQLSecurityError):
            validate_metadata_key("union")

    def test_special_characters_rejected(self):
        """Test that dangerous special characters are rejected."""
        with pytest.raises(SQLSecurityError):
            validate_metadata_key("key'value")

        with pytest.raises(SQLSecurityError):
            validate_metadata_key('key"value')

        with pytest.raises(SQLSecurityError):
            validate_metadata_key("key;value")

    def test_empty_key_rejected(self):
        """Test that empty keys are rejected."""
        with pytest.raises(SQLSecurityError):
            validate_metadata_key("")


class TestSQLInjectionPrevention:
    """Test that SQL injection attacks are prevented."""

    def test_parameterized_query_prevents_injection(self):
        """Test that parameterized queries prevent SQL injection."""
        # Set up in-memory SQLite database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE users (id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
        cursor.execute("INSERT INTO users VALUES (2, 'Bob')")

        # Attempt SQL injection - should find nothing
        malicious_input = "1 OR 1=1"
        query = "SELECT * FROM users WHERE id = ?"
        result = cursor.execute(query, (malicious_input,)).fetchall()
        # Should find nothing (treated as literal string, not SQL)
        assert len(result) == 0

        # Valid input should work
        result = cursor.execute(query, (1,)).fetchall()
        assert len(result) == 1
        assert result[0][1] == 'Alice'

        conn.close()

    def test_string_concatenation_vulnerable(self):
        """Demonstrate why string concatenation is dangerous (for documentation)."""
        # Set up in-memory SQLite database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE users (id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
        cursor.execute("INSERT INTO users VALUES (2, 'Bob')")

        # This demonstrates the vulnerability (DON'T DO THIS)
        # We're deliberately showing the unsafe version for educational purposes
        # In production, ALWAYS use parameterized queries
        malicious_input = "1 OR 1=1"
        # UNSAFE: query = f"SELECT * FROM users WHERE id = {malicious_input}"
        # This would return all users instead of just one!

        # The SAFE way:
        query = "SELECT * FROM users WHERE id = ?"
        result = cursor.execute(query, (malicious_input,)).fetchall()
        assert len(result) == 0  # Correctly prevents injection

        conn.close()

    def test_like_pattern_escaping(self):
        """Test LIKE pattern escaping prevents injection."""
        # Set up in-memory SQLite database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE files (id INTEGER, filename TEXT)")
        cursor.execute("INSERT INTO files VALUES (1, 'test_file.txt')")
        cursor.execute("INSERT INTO files VALUES (2, 'test.txt')")
        cursor.execute("INSERT INTO files VALUES (3, 'production.txt')")

        # User input that could be used for wildcard injection
        user_input = "test_file"

        # Without escaping, _ is a wildcard and matches any single character
        query = "SELECT * FROM files WHERE filename LIKE ?"
        result = cursor.execute(query, (f"%{user_input}%",)).fetchall()
        # This would match both "test_file" and "testXfile"

        # With escaping
        safe_pattern = escape_like_pattern(user_input)
        result = cursor.execute(query, (f"%{safe_pattern}%",)).fetchall()
        # This only matches literal "test_file"
        assert len(result) == 1

        conn.close()


class TestQueryBuilder:
    """Test QueryBuilder functionality."""

    def test_basic_query_building(self):
        """Test basic query construction."""
        builder = QueryBuilder("SELECT * FROM users")
        builder.add_where("id = ?").add_param(123)
        builder.add_where("active = ?").add_param(True)

        query, params = builder.build()
        assert "WHERE" in query
        assert "id = ?" in query
        assert "active = ?" in query
        assert params == (123, True)

    def test_query_without_where(self):
        """Test query building without WHERE clauses."""
        builder = QueryBuilder("SELECT * FROM users")
        query, params = builder.build()
        assert query == "SELECT * FROM users"
        assert params == ()

    def test_param_style_question_mark(self):
        """Test question mark parameter style."""
        builder = QueryBuilder("SELECT * FROM users", param_style='?')
        builder.add_param(1).add_param("Alice")
        query, params = builder.build()
        assert params == (1, "Alice")

    def test_param_style_percent_s(self):
        """Test %s parameter style."""
        builder = QueryBuilder("SELECT * FROM users", param_style='%s')
        builder.add_param(1).add_param("Alice")
        query, params = builder.build()
        assert params == (1, "Alice")

    def test_execute_on_cursor(self):
        """Test executing built query on cursor."""
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE users (id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
        cursor.execute("INSERT INTO users VALUES (2, 'Bob')")

        builder = QueryBuilder("SELECT * FROM users")
        builder.add_where("id = ?").add_param(1)
        builder.execute(cursor)

        result = cursor.fetchall()
        assert len(result) == 1
        assert result[0][1] == 'Alice'

        conn.close()


class TestSafeExecute:
    """Test safe_execute functionality."""

    def test_safe_execute_with_params(self):
        """Test safe execution with parameters."""
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE users (id INTEGER, name TEXT)")

        # Should execute safely
        safe_execute(cursor, "INSERT INTO users VALUES (?, ?)", (1, "Alice"))

        result = cursor.execute("SELECT * FROM users").fetchall()
        assert len(result) == 1
        assert result[0][1] == "Alice"

        conn.close()

    def test_safe_execute_without_params(self):
        """Test safe execution without parameters."""
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()

        # Should execute safely
        safe_execute(cursor, "CREATE TABLE users (id INTEGER, name TEXT)")

        # Verify table was created
        result = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        ).fetchall()
        assert len(result) == 1

        conn.close()


class TestLikePatternEscaping:
    """Test LIKE pattern escaping functionality."""

    def test_escape_percent(self):
        """Test escaping % wildcard."""
        assert escape_like_pattern("50%") == "50\\%"
        assert escape_like_pattern("100% complete") == "100\\% complete"

    def test_escape_underscore(self):
        """Test escaping _ wildcard."""
        assert escape_like_pattern("test_value") == "test\\_value"
        assert escape_like_pattern("user_id") == "user\\_id"

    def test_escape_backslash(self):
        """Test escaping backslash."""
        assert escape_like_pattern("path\\to\\file") == "path\\\\to\\\\file"

    def test_escape_combined(self):
        """Test escaping multiple special characters."""
        assert escape_like_pattern("test_50%") == "test\\_50\\%"
        assert escape_like_pattern("C:\\Program Files\\test_app") == "C:\\\\Program Files\\\\test\\_app"

    def test_no_escape_needed(self):
        """Test strings that don't need escaping."""
        assert escape_like_pattern("normal_text") == "normal\\_text"
        assert escape_like_pattern("123") == "123"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
