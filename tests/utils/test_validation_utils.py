"""
Tests for Data Validation Utilities

Simple validation tests for input sanitization, format validation, and data constraints.
Real implementations only, no mocks needed.

Trinity Framework: 🛡️ Guardian · 🔒 Security
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List

import pytest

# ============================================================================
# Email Validation Tests
# ============================================================================

@pytest.mark.unit
def test_email_validation_valid():
    """Test valid email formats."""
    valid_emails = [
        "user@example.com",
        "test.user@domain.co.uk",
        "first.last+tag@company.org",
        "user123@test-domain.com",
        "a@b.c",
    ]

    # Simple email regex
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    for email in valid_emails:
        assert re.match(email_pattern, email), f"Valid email rejected: {email}"


@pytest.mark.unit
def test_email_validation_invalid():
    """Test invalid email formats."""
    invalid_emails = [
        "invalid",
        "@example.com",
        "user@",
        "user @example.com",
        "user@example",
        "user..name@example.com",
        "",
    ]

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    for email in invalid_emails:
        assert not re.match(email_pattern, email), f"Invalid email accepted: {email}"


# ============================================================================
# URL Validation Tests
# ============================================================================

@pytest.mark.unit
def test_url_validation_valid():
    """Test valid URL formats."""
    valid_urls = [
        "https://example.com",
        "http://test.org/path",
        "https://sub.domain.com/path?query=value",
        "http://localhost:8000",
        "https://api.service.io/v1/endpoint",
    ]

    url_pattern = r"^https?://[a-zA-Z0-9.-]+(:[0-9]+)?(/.*)?$"

    for url in valid_urls:
        assert re.match(url_pattern, url), f"Valid URL rejected: {url}"


@pytest.mark.unit
def test_url_validation_invalid():
    """Test invalid URL formats."""
    invalid_urls = [
        "not a url",
        "ftp://example.com",  # Wrong protocol
        "//example.com",      # Missing protocol
        "http://",            # Incomplete
        "javascript:alert('xss')",
        "",
    ]

    url_pattern = r"^https?://[a-zA-Z0-9.-]+(:[0-9]+)?(/.*)?$"

    for url in invalid_urls:
        assert not re.match(url_pattern, url), f"Invalid URL accepted: {url}"


# ============================================================================
# String Length Validation Tests
# ============================================================================

@pytest.mark.unit
def test_string_length_validation():
    """Test string length constraints."""
    def validate_length(text: str, min_len: int, max_len: int) -> bool:
        """Validate string length is within bounds."""
        return min_len <= len(text) <= max_len

    # Valid lengths
    assert validate_length("hello", 1, 10)
    assert validate_length("test", 4, 4)
    assert validate_length("a" * 50, 1, 100)

    # Invalid lengths
    assert not validate_length("", 1, 10)  # Too short
    assert not validate_length("a" * 20, 1, 10)  # Too long


@pytest.mark.unit
def test_password_strength_validation():
    """Test password strength validation."""
    def validate_password(password: str) -> bool:
        """Validate password meets strength requirements."""
        if len(password) < 8:
            return False

        # Must have uppercase, lowercase, digit, special char
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        return has_upper and has_lower and has_digit and has_special

    # Valid passwords
    assert validate_password("SecureP@ss123")
    assert validate_password("MyP@ssw0rd!")

    # Invalid passwords
    assert not validate_password("short")
    assert not validate_password("alllowercase123!")
    assert not validate_password("ALLUPPERCASE123!")
    assert not validate_password("NoSpecialChar123")
    assert not validate_password("NoDigits!@#")


# ============================================================================
# Numeric Range Validation Tests
# ============================================================================

@pytest.mark.unit
def test_numeric_range_validation():
    """Test numeric value range validation."""
    def validate_range(value: float, min_val: float, max_val: float) -> bool:
        """Validate number is within range."""
        return min_val <= value <= max_val

    # Valid ranges
    assert validate_range(5, 0, 10)
    assert validate_range(0, 0, 100)
    assert validate_range(100, 0, 100)
    assert validate_range(3.14, 0, 10)

    # Invalid ranges
    assert not validate_range(-1, 0, 10)
    assert not validate_range(11, 0, 10)
    assert not validate_range(1000, 0, 100)


@pytest.mark.unit
def test_percentage_validation():
    """Test percentage validation (0-100)."""
    def validate_percentage(value: float) -> bool:
        """Validate value is valid percentage."""
        return 0 <= value <= 100

    # Valid percentages
    assert validate_percentage(0)
    assert validate_percentage(50)
    assert validate_percentage(100)
    assert validate_percentage(75.5)

    # Invalid percentages
    assert not validate_percentage(-1)
    assert not validate_percentage(101)
    assert not validate_percentage(1000)


# ============================================================================
# Format Validation Tests
# ============================================================================

@pytest.mark.unit
def test_iso_timestamp_validation():
    """Test ISO timestamp format validation."""
    valid_timestamps = [
        "2025-10-09T10:30:00Z",
        "2025-10-09T10:30:00+00:00",
        "2025-10-09T10:30:00.123456Z",
    ]

    # ISO 8601 pattern (simplified)
    iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"

    for timestamp in valid_timestamps:
        assert re.match(iso_pattern, timestamp)


@pytest.mark.unit
def test_uuid_validation():
    """Test UUID format validation."""
    valid_uuids = [
        "550e8400-e29b-41d4-a716-446655440000",
        "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        "00000000-0000-0000-0000-000000000000",
    ]

    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

    for uuid in valid_uuids:
        assert re.match(uuid_pattern, uuid.lower())


@pytest.mark.unit
def test_hex_color_validation():
    """Test hex color format validation."""
    valid_colors = [
        "#FFFFFF",
        "#000000",
        "#FF5733",
        "#abc123",
    ]

    hex_pattern = r"^#[0-9A-Fa-f]{6}$"

    for color in valid_colors:
        assert re.match(hex_pattern, color)

    # Invalid colors
    invalid_colors = ["#FFF", "#GGGGGG", "FFFFFF", "#12345"]
    for color in invalid_colors:
        assert not re.match(hex_pattern, color)


# ============================================================================
# Data Type Validation Tests
# ============================================================================

@pytest.mark.unit
def test_json_structure_validation():
    """Test JSON structure validation."""
    def validate_user_json(data: Dict[str, Any]) -> bool:
        """Validate user JSON has required fields."""
        required_fields = ["user_id", "email", "tier"]
        return all(field in data for field in required_fields)

    # Valid structure
    valid_data = {
        "user_id": "user123",
        "email": "user@example.com",
        "tier": "alpha"
    }
    assert validate_user_json(valid_data)

    # Invalid structure (missing fields)
    invalid_data = {
        "user_id": "user123",
        "email": "user@example.com"
    }
    assert not validate_user_json(invalid_data)


@pytest.mark.unit
def test_list_validation():
    """Test list content validation."""
    def validate_list(items: List[Any], item_type: type, max_items: int = 100) -> bool:
        """Validate list contains items of correct type and size."""
        if len(items) > max_items:
            return False

        return all(isinstance(item, item_type) for item in items)

    # Valid lists
    assert validate_list([1, 2, 3], int)
    assert validate_list(["a", "b", "c"], str)
    assert validate_list([], str)  # Empty list is valid

    # Invalid lists
    assert not validate_list([1, "2", 3], int)  # Mixed types
    assert not validate_list(["a"] * 200, str, max_items=100)  # Too many items


# ============================================================================
# Sanitization Tests
# ============================================================================

@pytest.mark.unit
def test_whitespace_sanitization():
    """Test whitespace sanitization."""
    def sanitize_whitespace(text: str) -> str:
        """Remove leading/trailing whitespace and collapse internal whitespace."""
        return " ".join(text.split())

    # Test cases
    assert sanitize_whitespace("  hello  world  ") == "hello world"
    assert sanitize_whitespace("hello\n\nworld") == "hello world"
    assert sanitize_whitespace("hello\t\tworld") == "hello world"
    assert sanitize_whitespace("   ") == ""


@pytest.mark.unit
def test_special_character_removal():
    """Test special character removal."""
    def remove_special_chars(text: str) -> str:
        """Remove special characters, keep alphanumeric and spaces."""
        return re.sub(r"[^a-zA-Z0-9\s]", "", text)

    # Test cases
    assert remove_special_chars("hello@world!") == "helloworld"
    assert remove_special_chars("test-123") == "test123"
    assert remove_special_chars("hello world") == "hello world"


@pytest.mark.unit
def test_html_tag_removal():
    """Test HTML tag removal."""
    def remove_html_tags(text: str) -> str:
        """Remove HTML tags from text."""
        return re.sub(r"<[^>]+>", "", text)

    # Test cases
    assert remove_html_tags("<p>Hello</p>") == "Hello"
    assert remove_html_tags("<b>Bold</b> text") == "Bold text"
    assert remove_html_tags("No tags here") == "No tags here"
    assert remove_html_tags("<script>alert('xss')</script>") == "alert('xss')"


# ============================================================================
# Boundary Value Tests
# ============================================================================

@pytest.mark.unit
def test_boundary_integer_validation():
    """Test integer boundary validation."""
    def validate_int32(value: int) -> bool:
        """Validate value fits in 32-bit signed integer."""
        return -2147483648 <= value <= 2147483647

    # Valid values
    assert validate_int32(0)
    assert validate_int32(2147483647)
    assert validate_int32(-2147483648)

    # Invalid values
    assert not validate_int32(2147483648)  # Overflow
    assert not validate_int32(-2147483649)  # Underflow


@pytest.mark.unit
def test_boundary_string_validation():
    """Test string boundary validation."""
    def validate_username(username: str) -> bool:
        """Validate username (3-20 chars, alphanumeric + underscore)."""
        if not (3 <= len(username) <= 20):
            return False

        return re.match(r"^[a-zA-Z0-9_]+$", username) is not None

    # Valid usernames
    assert validate_username("user123")
    assert validate_username("test_user")
    assert validate_username("abc")  # Minimum length
    assert validate_username("a" * 20)  # Maximum length

    # Invalid usernames
    assert not validate_username("ab")  # Too short
    assert not validate_username("a" * 21)  # Too long
    assert not validate_username("user@123")  # Invalid char
    assert not validate_username("user name")  # Space not allowed


# ============================================================================
# Composite Validation Tests
# ============================================================================

@pytest.mark.unit
def test_user_registration_validation():
    """Test complete user registration validation."""
    def validate_registration(data: Dict[str, str]) -> tuple[bool, List[str]]:
        """Validate user registration data. Returns (is_valid, errors)."""
        errors = []

        # Email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, data.get("email", "")):
            errors.append("Invalid email format")

        # Password validation
        password = data.get("password", "")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")

        # Tier validation
        if data.get("tier") not in ["alpha", "beta", "gamma", "delta"]:
            errors.append("Invalid tier")

        return len(errors) == 0, errors

    # Valid registration
    valid_data = {
        "email": "user@example.com",
        "password": "SecureP@ss123",
        "tier": "alpha"
    }
    is_valid, errors = validate_registration(valid_data)
    assert is_valid
    assert len(errors) == 0

    # Invalid registration
    invalid_data = {
        "email": "invalid_email",
        "password": "short",
        "tier": "invalid"
    }
    is_valid, errors = validate_registration(invalid_data)
    assert not is_valid
    assert len(errors) == 3


# ============================================================================
# Capability Tests
# ============================================================================

@pytest.mark.capability
def test_validation_pipeline_capability():
    """Test complete validation pipeline."""
    def validate_api_request(data: Dict[str, Any]) -> bool:
        """Validate API request data."""
        # 1. Check required fields
        if "user_id" not in data or "action" not in data:
            return False

        # 2. Validate user_id format
        if not isinstance(data["user_id"], str) or len(data["user_id"]) == 0:
            return False

        # 3. Validate action
        valid_actions = ["read", "write", "delete", "update"]
        if data["action"] not in valid_actions:
            return False

        # 4. Validate optional timestamp
        if "timestamp" in data:
            iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
            if not re.match(iso_pattern, data["timestamp"]):
                return False

        return True

    # Valid requests
    valid_request = {
        "user_id": "user123",
        "action": "read",
        "timestamp": "2025-10-09T10:00:00Z"
    }
    assert validate_api_request(valid_request)

    # Invalid requests
    invalid_requests = [
        {"action": "read"},  # Missing user_id
        {"user_id": "user123", "action": "invalid"},  # Invalid action
        {"user_id": "", "action": "read"},  # Empty user_id
    ]

    for request in invalid_requests:
        assert not validate_api_request(request)


@pytest.mark.capability
def test_data_sanitization_capability():
    """Test complete data sanitization capability."""
    def sanitize_user_input(text: str) -> str:
        """Sanitize user input for safe storage/display."""
        # 1. Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # 2. Remove extra whitespace
        text = " ".join(text.split())

        # 3. Trim to max length
        max_length = 1000
        if len(text) > max_length:
            text = text[:max_length]

        # 4. Strip leading/trailing whitespace
        text = text.strip()

        return text

    # Test sanitization
    dirty_input = "  <script>alert('xss')</script>  Hello   World!  " + ("x" * 2000)
    clean_output = sanitize_user_input(dirty_input)

    # Verify sanitization
    assert "<script>" not in clean_output
    assert "  " not in clean_output  # No double spaces
    assert len(clean_output) <= 1000
    assert not clean_output.startswith(" ")
    assert not clean_output.endswith(" ")
