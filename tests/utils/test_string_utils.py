"""
Tests for String Manipulation Utilities

Simple utility tests for string operations, formatting, and transformations.
Real implementations only, no mocks needed.

Trinity Framework: 🛡️ Guardian · 🏗️ Architecture
"""

import re
from typing import List, Optional

import pytest

# ============================================================================
# String Casing Tests
# ============================================================================

@pytest.mark.unit
def test_to_snake_case():
    """Test conversion to snake_case."""
    def to_snake_case(text: str) -> str:
        """Convert text to snake_case."""
        # Insert underscore before capitals
        text = re.sub(r'(?<!^)(?=[A-Z])', '_', text)
        return text.lower()
    
    assert to_snake_case("camelCase") == "camel_case"
    assert to_snake_case("PascalCase") == "pascal_case"
    assert to_snake_case("alreadySnake_case") == "already_snake_case"
    assert to_snake_case("HTTPSConnection") == "h_t_t_p_s_connection"


@pytest.mark.unit
def test_to_camel_case():
    """Test conversion to camelCase."""
    def to_camel_case(text: str) -> str:
        """Convert text to camelCase."""
        parts = text.split('_')
        if not parts:
            return text
        
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])
    
    assert to_camel_case("snake_case") == "snakeCase"
    assert to_camel_case("multiple_word_string") == "multipleWordString"
    assert to_camel_case("single") == "single"
    assert to_camel_case("already_camelCase") == "alreadyCamelcase"


@pytest.mark.unit
def test_to_pascal_case():
    """Test conversion to PascalCase."""
    def to_pascal_case(text: str) -> str:
        """Convert text to PascalCase."""
        parts = text.split('_')
        return ''.join(word.capitalize() for word in parts)
    
    assert to_pascal_case("snake_case") == "SnakeCase"
    assert to_pascal_case("multiple_words") == "MultipleWords"
    assert to_pascal_case("single") == "Single"


@pytest.mark.unit
def test_to_kebab_case():
    """Test conversion to kebab-case."""
    def to_kebab_case(text: str) -> str:
        """Convert text to kebab-case."""
        # Convert to snake_case first, then replace underscores
        text = re.sub(r'(?<!^)(?=[A-Z])', '_', text)
        return text.lower().replace('_', '-')
    
    assert to_kebab_case("camelCase") == "camel-case"
    assert to_kebab_case("PascalCase") == "pascal-case"
    assert to_kebab_case("snake_case") == "snake-case"


# ============================================================================
# String Truncation Tests
# ============================================================================

@pytest.mark.unit
def test_truncate_simple():
    """Test simple string truncation."""
    def truncate(text: str, max_length: int) -> str:
        """Truncate string to max_length."""
        if len(text) <= max_length:
            return text
        return text[:max_length]
    
    assert truncate("short", 10) == "short"
    assert truncate("this is a long string", 10) == "this is a "
    assert truncate("exact", 5) == "exact"


@pytest.mark.unit
def test_truncate_with_ellipsis():
    """Test string truncation with ellipsis."""
    def truncate_ellipsis(text: str, max_length: int) -> str:
        """Truncate string with ellipsis."""
        if len(text) <= max_length:
            return text
        
        if max_length < 3:
            return text[:max_length]
        
        return text[:max_length - 3] + "..."
    
    assert truncate_ellipsis("short", 10) == "short"
    assert truncate_ellipsis("this is a very long string", 15) == "this is a ve..."
    assert truncate_ellipsis("exact", 5) == "exact"
    assert truncate_ellipsis("toolong", 6) == "too..."


@pytest.mark.unit
def test_truncate_word_boundary():
    """Test truncation at word boundary."""
    def truncate_words(text: str, max_length: int) -> str:
        """Truncate at word boundary."""
        if len(text) <= max_length:
            return text
        
        # Find last space before max_length
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            return text[:last_space] + "..."
        
        return truncated + "..."
    
    text = "this is a long sentence with many words"
    result = truncate_words(text, 20)
    
    # Should break at word boundary
    assert len(result) <= 23  # 20 + "..."
    assert not result.endswith("ng...")  # Should not break mid-word


# ============================================================================
# String Padding Tests
# ============================================================================

@pytest.mark.unit
def test_pad_left():
    """Test left padding."""
    def pad_left(text: str, width: int, char: str = ' ') -> str:
        """Pad string on the left."""
        if len(text) >= width:
            return text
        return char * (width - len(text)) + text
    
    assert pad_left("123", 5) == "  123"
    assert pad_left("test", 10, '0') == "000000test"
    assert pad_left("already_long", 5) == "already_long"


@pytest.mark.unit
def test_pad_right():
    """Test right padding."""
    def pad_right(text: str, width: int, char: str = ' ') -> str:
        """Pad string on the right."""
        if len(text) >= width:
            return text
        return text + char * (width - len(text))
    
    assert pad_right("123", 5) == "123  "
    assert pad_right("test", 10, '-') == "test------"
    assert pad_right("already_long", 5) == "already_long"


@pytest.mark.unit
def test_pad_center():
    """Test center padding."""
    def pad_center(text: str, width: int, char: str = ' ') -> str:
        """Center text with padding."""
        if len(text) >= width:
            return text
        
        total_padding = width - len(text)
        left_padding = total_padding // 2
        right_padding = total_padding - left_padding
        
        return char * left_padding + text + char * right_padding
    
    assert pad_center("test", 10) == "   test   "
    assert pad_center("hi", 6) == "  hi  "
    assert pad_center("odd", 8) == "  odd   "


# ============================================================================
# String Extraction Tests
# ============================================================================

@pytest.mark.unit
def test_extract_between():
    """Test extracting text between delimiters."""
    def extract_between(text: str, start: str, end: str) -> Optional[str]:
        """Extract text between start and end delimiters."""
        start_idx = text.find(start)
        if start_idx == -1:
            return None
        
        start_idx += len(start)
        end_idx = text.find(end, start_idx)
        
        if end_idx == -1:
            return None
        
        return text[start_idx:end_idx]
    
    assert extract_between("hello [world] test", "[", "]") == "world"
    assert extract_between("no brackets here", "[", "]") is None
    assert extract_between("<tag>content</tag>", "<tag>", "</tag>") == "content"


@pytest.mark.unit
def test_extract_all_between():
    """Test extracting all occurrences between delimiters."""
    def extract_all_between(text: str, start: str, end: str) -> List[str]:
        """Extract all occurrences between delimiters."""
        results = []
        current_pos = 0
        
        while True:
            start_idx = text.find(start, current_pos)
            if start_idx == -1:
                break
            
            start_idx += len(start)
            end_idx = text.find(end, start_idx)
            
            if end_idx == -1:
                break
            
            results.append(text[start_idx:end_idx])
            current_pos = end_idx + len(end)
        
        return results
    
    text = "[first] some text [second] more [third]"
    results = extract_all_between(text, "[", "]")
    
    assert len(results) == 3
    assert results == ["first", "second", "third"]


# ============================================================================
# String Splitting Tests
# ============================================================================

@pytest.mark.unit
def test_split_preserve_quotes():
    """Test splitting while preserving quoted strings."""
    def split_preserve_quotes(text: str, delimiter: str = ' ') -> List[str]:
        """Split text preserving quoted strings."""
        parts = []
        current = []
        in_quotes = False
        
        for char in text:
            if char == '"':
                in_quotes = not in_quotes
            elif char == delimiter and not in_quotes:
                if current:
                    parts.append(''.join(current))
                    current = []
                continue
            
            current.append(char)
        
        if current:
            parts.append(''.join(current))
        
        return parts
    
    text = 'arg1 "quoted string" arg3'
    parts = split_preserve_quotes(text)
    
    assert len(parts) == 3
    assert parts[1] == '"quoted string"'


@pytest.mark.unit
def test_split_max_parts():
    """Test splitting with maximum parts."""
    def split_max(text: str, delimiter: str, max_parts: int) -> List[str]:
        """Split text with maximum number of parts."""
        return text.split(delimiter, max_parts - 1)
    
    text = "a:b:c:d:e"
    
    assert split_max(text, ":", 3) == ["a", "b", "c:d:e"]
    assert split_max(text, ":", 2) == ["a", "b:c:d:e"]


# ============================================================================
# String Cleaning Tests
# ============================================================================

@pytest.mark.unit
def test_remove_punctuation():
    """Test removing punctuation."""
    def remove_punctuation(text: str) -> str:
        """Remove punctuation from text."""
        return re.sub(r'[^\w\s]', '', text)
    
    assert remove_punctuation("hello, world!") == "hello world"
    assert remove_punctuation("test-case_123") == "testcase_123"
    assert remove_punctuation("no punctuation") == "no punctuation"


@pytest.mark.unit
def test_remove_extra_spaces():
    """Test removing extra spaces."""
    def remove_extra_spaces(text: str) -> str:
        """Collapse multiple spaces to single space."""
        return ' '.join(text.split())
    
    assert remove_extra_spaces("hello    world") == "hello world"
    assert remove_extra_spaces("  leading and trailing  ") == "leading and trailing"
    assert remove_extra_spaces("multiple   spaces   here") == "multiple spaces here"


@pytest.mark.unit
def test_remove_numbers():
    """Test removing numbers."""
    def remove_numbers(text: str) -> str:
        """Remove all numbers from text."""
        return re.sub(r'\d', '', text)
    
    assert remove_numbers("test123") == "test"
    assert remove_numbers("abc123def456") == "abcdef"
    assert remove_numbers("no numbers here") == "no numbers here"


# ============================================================================
# String Comparison Tests
# ============================================================================

@pytest.mark.unit
def test_fuzzy_match():
    """Test fuzzy string matching."""
    def fuzzy_match(str1: str, str2: str, threshold: float = 0.8) -> bool:
        """Simple fuzzy string matching."""
        str1 = str1.lower()
        str2 = str2.lower()
        
        if str1 == str2:
            return True
        
        # Levenshtein-like simple check
        max_len = max(len(str1), len(str2))
        if max_len == 0:
            return True
        
        # Count matching characters
        matches = sum(c1 == c2 for c1, c2 in zip(str1, str2))
        similarity = matches / max_len
        
        return similarity >= threshold
    
    assert fuzzy_match("hello", "hello")
    assert fuzzy_match("test", "test")
    assert not fuzzy_match("completely", "different")


@pytest.mark.unit
def test_starts_with_any():
    """Test if string starts with any of the prefixes."""
    def starts_with_any(text: str, prefixes: List[str]) -> bool:
        """Check if text starts with any of the prefixes."""
        return any(text.startswith(prefix) for prefix in prefixes)
    
    assert starts_with_any("hello world", ["hello", "hi", "hey"])
    assert not starts_with_any("goodbye", ["hello", "hi", "hey"])
    assert starts_with_any("test_function", ["test_", "demo_"])


@pytest.mark.unit
def test_ends_with_any():
    """Test if string ends with any of the suffixes."""
    def ends_with_any(text: str, suffixes: List[str]) -> bool:
        """Check if text ends with any of the suffixes."""
        return any(text.endswith(suffix) for suffix in suffixes)
    
    assert ends_with_any("test.py", [".py", ".txt", ".md"])
    assert not ends_with_any("test.js", [".py", ".txt", ".md"])
    assert ends_with_any("README.md", [".md", ".txt"])


# ============================================================================
# ΛID String Operations Tests
# ============================================================================

@pytest.mark.unit
def test_lambda_id_format():
    """Test ΛID string formatting."""
    def format_lambda_id(tier: str, user_id: str) -> str:
        """Format ΛID string."""
        return f"Λ_{tier}_{user_id}"
    
    assert format_lambda_id("alpha", "user123") == "Λ_alpha_user123"
    assert format_lambda_id("beta", "test") == "Λ_beta_test"


@pytest.mark.unit
def test_lambda_id_display():
    """Test ΛID display formatting."""
    def display_lambda_id(lambda_id: str) -> str:
        """Format ΛID for display."""
        parts = lambda_id.split('_')
        if len(parts) != 3:
            return lambda_id
        
        tier = parts[1].capitalize()
        user_id = parts[2]
        
        return f"{tier} User: {user_id}"
    
    assert display_lambda_id("Λ_alpha_user123") == "Alpha User: user123"
    assert display_lambda_id("Λ_beta_test") == "Beta User: test"


@pytest.mark.unit
def test_lambda_id_mask():
    """Test ΛID masking for privacy."""
    def mask_lambda_id(lambda_id: str) -> str:
        """Mask ΛID user_id for privacy."""
        parts = lambda_id.split('_')
        if len(parts) != 3:
            return lambda_id
        
        user_id = parts[2]
        if len(user_id) <= 6:
            return lambda_id
        
        masked_id = f"{user_id[:4]}***{user_id[-2:]}"
        return f"{parts[0]}_{parts[1]}_{masked_id}"
    
    result = mask_lambda_id("Λ_alpha_user12345678")
    assert "user***78" in result
    assert "Λ_alpha" in result


# ============================================================================
# Capability Tests
# ============================================================================

@pytest.mark.capability
def test_string_pipeline():
    """Test complete string processing pipeline."""
    def process_input(text: str) -> str:
        """Process user input through pipeline."""
        # 1. Remove extra whitespace
        text = ' '.join(text.split())
        
        # 2. Strip
        text = text.strip()
        
        # 3. Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # 4. Convert to lowercase
        text = text.lower()
        
        # 5. Remove extra spaces again
        text = ' '.join(text.split())
        
        return text
    
    messy_input = "  Hello,  World!   How  are   you?  "
    clean_output = process_input(messy_input)
    
    assert clean_output == "hello world how are you"
    assert "  " not in clean_output
    assert clean_output.islower()


@pytest.mark.capability
def test_text_analysis_pipeline():
    """Test text analysis pipeline."""
    text = "The quick brown fox jumps over the lazy dog"
    
    # Word count
    words = text.split()
    assert len(words) == 9
    
    # Character count (no spaces)
    chars = len(text.replace(' ', ''))
    assert chars == 35
    
    # Unique words
    unique = len(set(word.lower() for word in words))
    assert unique == 8  # "the" appears twice
    
    # Average word length
    avg_length = sum(len(word) for word in words) / len(words)
    assert 3 < avg_length < 5


@pytest.mark.capability
def test_trinity_symbol_formatting():
    """Test Trinity Framework symbol formatting."""
    trinity_symbols = {
        "identity": "⚛️",
        "consciousness": "🧠",
        "guardian": "🛡️",
        "lukhas.memory": "✦",
        "vision": "🔬",
        "bio": "🌱",
        "dream": "🌙",
        "ethics": "⚖️",
        "quantum": "⚛️"
    }
    
    def format_trinity_message(component: str, message: str) -> str:
        """Format message with Trinity symbol."""
        symbol = trinity_symbols.get(component, "🔹")
        return f"{symbol} {component.capitalize()}: {message}"
    
    result = format_trinity_message("identity", "ΛID validated")
    assert "⚛️" in result
    assert "Identity" in result
    assert "ΛID validated" in result
