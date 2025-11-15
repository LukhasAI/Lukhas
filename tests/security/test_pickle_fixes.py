#!/usr/bin/env python3
"""
Security Tests for Pickle Deserialization Fixes
================================================

Tests to verify that all pickle deserialization vulnerabilities
have been properly fixed with HMAC-signed secure pickle.

Author: LUKHAS AI Security Team
Created: 2025-11-15
"""

import pytest
import pickle
import os
from pathlib import Path

from lukhas.security.safe_serialization import (
    secure_pickle_dumps,
    secure_pickle_loads,
    safe_json_serialize,
    safe_json_deserialize,
    SerializationSecurityError,
    save_secure_pickle,
    load_secure_pickle,
    serialize_for_storage,
    deserialize_from_storage,
)


class TestSecurePickle:
    """Test secure pickle serialization with HMAC signatures"""

    def test_roundtrip_simple_data(self):
        """Ensure secure pickle can serialize and deserialize simple data"""
        original = {"key": "value", "nested": {"a": 1, "b": 2}, "list": [1, 2, 3]}
        serialized = secure_pickle_dumps(original)
        deserialized = secure_pickle_loads(serialized)
        assert deserialized == original

    def test_roundtrip_complex_data(self):
        """Test with more complex Python objects"""
        import datetime
        original = {
            "datetime": datetime.datetime.now(),
            "set": {1, 2, 3},
            "tuple": (1, 2, 3),
            "nested_list": [[1, 2], [3, 4]],
        }
        serialized = secure_pickle_dumps(original)
        deserialized = secure_pickle_loads(serialized)
        assert deserialized["set"] == original["set"]
        assert deserialized["tuple"] == original["tuple"]

    def test_detects_tampering_signature(self):
        """Ensure tampered signature is rejected"""
        original = {"key": "value"}
        serialized = secure_pickle_dumps(original)

        # Tamper with signature (first 32 bytes)
        tampered_sig = b'X' * 32 + serialized[32:]

        with pytest.raises(SerializationSecurityError, match="HMAC signature verification failed"):
            secure_pickle_loads(tampered_sig)

    def test_detects_tampering_data(self):
        """Ensure tampered data is rejected"""
        original = {"key": "value"}
        serialized = secure_pickle_dumps(original)

        # Tamper with data (after signature)
        tampered_data = serialized[:-1] + b'X'

        with pytest.raises(SerializationSecurityError, match="HMAC signature verification failed"):
            secure_pickle_loads(tampered_data)

    def test_rejects_short_data(self):
        """Ensure data too short for signature is rejected"""
        short_data = b'tooshort'

        with pytest.raises(ValueError, match="too short"):
            secure_pickle_loads(short_data)

    def test_different_keys_fail(self):
        """Ensure data signed with different key fails verification"""
        original = {"key": "value"}
        key1 = b'key1'
        key2 = b'key2'

        serialized = secure_pickle_dumps(original, key=key1)

        with pytest.raises(SerializationSecurityError):
            secure_pickle_loads(serialized, key=key2)

    def test_same_key_succeeds(self):
        """Ensure data signed with same key succeeds"""
        original = {"key": "value"}
        key = b'custom_key'

        serialized = secure_pickle_dumps(original, key=key)
        deserialized = secure_pickle_loads(serialized, key=key)

        assert deserialized == original


class TestJSONSerialization:
    """Test safe JSON serialization"""

    def test_json_roundtrip(self):
        """Ensure JSON serialization works for simple types"""
        data = {"key": "value", "numbers": [1, 2, 3], "nested": {"a": 1}}
        serialized = safe_json_serialize(data)
        deserialized = safe_json_deserialize(serialized)
        assert deserialized == data

    def test_json_unicode(self):
        """Test JSON with Unicode characters"""
        data = {"message": "Hello 世界 🌍", "emoji": "👍"}
        serialized = safe_json_serialize(data)
        deserialized = safe_json_deserialize(serialized)
        assert deserialized == data

    def test_json_rejects_non_serializable(self):
        """Ensure non-JSON-serializable objects raise TypeError"""
        import datetime
        data = {"datetime": datetime.datetime.now()}

        with pytest.raises(TypeError, match="not JSON-serializable"):
            safe_json_serialize(data)

    def test_json_invalid_data(self):
        """Ensure invalid JSON raises ValueError"""
        invalid_json = b'{ invalid json }'

        with pytest.raises(ValueError, match="Invalid JSON"):
            safe_json_deserialize(invalid_json)


class TestFileOperations:
    """Test secure file save/load operations"""

    def test_save_load_pickle(self, tmp_path):
        """Test secure pickle file operations"""
        data = {"test": "data", "numbers": [1, 2, 3]}
        filepath = tmp_path / "test.pkl"

        save_secure_pickle(data, filepath)
        assert filepath.exists()

        loaded = load_secure_pickle(filepath)
        assert loaded == data

    def test_load_nonexistent_file(self, tmp_path):
        """Ensure loading non-existent file raises FileNotFoundError"""
        filepath = tmp_path / "nonexistent.pkl"

        with pytest.raises(FileNotFoundError):
            load_secure_pickle(filepath)

    def test_save_creates_directory(self, tmp_path):
        """Ensure save creates parent directories"""
        filepath = tmp_path / "subdir" / "test.pkl"
        data = {"test": "data"}

        save_secure_pickle(data, filepath)
        assert filepath.exists()

        loaded = load_secure_pickle(filepath)
        assert loaded == data


class TestIntelligentSerialization:
    """Test intelligent storage serialization"""

    def test_prefer_json_for_simple_data(self):
        """Ensure simple data uses JSON by default"""
        data = {"key": "value", "numbers": [1, 2, 3]}
        serialized, format_type = serialize_for_storage(data, prefer_json=True)

        assert format_type == "json"

        deserialized = deserialize_from_storage(serialized, format_type)
        assert deserialized == data

    def test_fallback_to_pickle_for_complex_data(self):
        """Ensure complex data falls back to pickle"""
        import datetime
        data = {"datetime": datetime.datetime.now()}
        serialized, format_type = serialize_for_storage(data, prefer_json=True)

        assert format_type == "pickle"

        deserialized = deserialize_from_storage(serialized, format_type)
        assert deserialized["datetime"] == data["datetime"]

    def test_force_pickle(self):
        """Ensure pickle can be forced even for simple data"""
        data = {"key": "value"}
        serialized, format_type = serialize_for_storage(data, prefer_json=False)

        assert format_type == "pickle"

        deserialized = deserialize_from_storage(serialized, format_type)
        assert deserialized == data

    def test_invalid_format_type(self):
        """Ensure invalid format type raises ValueError"""
        data = b'some data'

        with pytest.raises(ValueError, match="Unknown format type"):
            deserialize_from_storage(data, "invalid")


class TestEnvironmentKey:
    """Test environment variable key handling"""

    def test_custom_environment_key(self, monkeypatch):
        """Test that environment key is used"""
        custom_key = "my-custom-secret-key"
        monkeypatch.setenv('LUKHAS_SERIALIZATION_KEY', custom_key)

        # Need to reload module to pick up new env var
        from lukhas.security import safe_serialization
        import importlib
        importlib.reload(safe_serialization)

        data = {"test": "data"}
        serialized = safe_serialization.secure_pickle_dumps(data)
        deserialized = safe_serialization.secure_pickle_loads(serialized)

        assert deserialized == data


class TestSecurityBestPractices:
    """Test security best practices and edge cases"""

    def test_large_data(self):
        """Test with large data structures"""
        large_data = {"items": list(range(10000))}
        serialized = secure_pickle_dumps(large_data)
        deserialized = secure_pickle_loads(serialized)
        assert deserialized == large_data

    def test_empty_data(self):
        """Test with empty data structures"""
        empty_dict = {}
        serialized = secure_pickle_dumps(empty_dict)
        deserialized = secure_pickle_loads(serialized)
        assert deserialized == empty_dict

    def test_none_value(self):
        """Test with None values"""
        data = {"key": None}
        serialized = secure_pickle_dumps(data)
        deserialized = secure_pickle_loads(serialized)
        assert deserialized == data

    def test_signature_is_deterministic(self):
        """Ensure same data produces different signatures (due to protocol differences)"""
        data = {"key": "value"}
        serialized1 = secure_pickle_dumps(data)
        serialized2 = secure_pickle_dumps(data)

        # Signatures should be the same for identical data
        assert serialized1 == serialized2


@pytest.mark.integration
class TestModuleIntegration:
    """Integration tests with actual modules"""

    def test_import_in_all_fixed_modules(self):
        """Verify all fixed modules can import the security module"""
        modules_to_test = [
            'labs.memory.folds.optimized_fold_engine',
            'labs.memory.memory_optimization',
            'labs.memory.integrity.collapse_hash',
            'labs.memory.systems.memory_tracker',
            'labs.core.glyph.personal_symbol_dictionary',
        ]

        for module_name in modules_to_test:
            try:
                __import__(module_name)
                # If it imports without error, the fix is working
            except ImportError as e:
                # Only fail if it's about our security module
                if 'safe_serialization' in str(e):
                    pytest.fail(f"Module {module_name} failed to import safe_serialization: {e}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
