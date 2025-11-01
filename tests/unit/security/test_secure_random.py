# tests/unit/security/test_secure_random.py

import pytest

from security.secure_random import (
    get_quantum_random_bytes,
    get_quantum_random_int,
)


@pytest.mark.tier3
class TestQuantumEntropyStub:
    """
    Tests for the quantum entropy stub functions.
    """

    def test_get_quantum_random_bytes_length(self):
        """
        Test that get_quantum_random_bytes returns the correct number of bytes.
        """
        for i in range(1, 65, 8):
            assert len(get_quantum_random_bytes(i)) == i

    def test_get_quantum_random_bytes_non_deterministic(self):
        """
        Test that get_quantum_random_bytes returns non-deterministic output.
        """
        # It's statistically very unlikely for these to be the same.
        assert get_quantum_random_bytes(32) != get_quantum_random_bytes(32)

    def test_get_quantum_random_bytes_invalid_input(self):
        """
        Test that get_quantum_random_bytes raises appropriate errors for invalid input.
        """
        with pytest.raises(ValueError, match="must be a non-negative integer"):
            get_quantum_random_bytes(-1)

        with pytest.raises(TypeError, match="must be an integer"):
            get_quantum_random_bytes(1.5)

    def test_get_quantum_random_int_range(self):
        """
        Test that get_quantum_random_int returns a value within the specified range.
        """
        min_val = -100
        max_val = 100
        for _ in range(100):
            val = get_quantum_random_int(min_val, max_val)
            assert min_val <= val <= max_val

    def test_get_quantum_random_int_single_value(self):
        """
        Test that get_quantum_random_int returns the single value when min_val == max_val.
        """
        assert get_quantum_random_int(42, 42) == 42

    def test_get_quantum_random_int_invalid_range(self):
        """
        Test that get_quantum_random_int raises ValueError if min_val > max_val.
        """
        with pytest.raises(ValueError, match="min_val cannot be greater than max_val."):
            get_quantum_random_int(10, 1)

    def test_get_quantum_random_int_invalid_input_type(self):
        """
        Test that get_quantum_random_int raises TypeError for non-integer inputs.
        """
        with pytest.raises(TypeError):
            get_quantum_random_int(1.5, 5)

        with pytest.raises(TypeError):
            get_quantum_random_int(1, 5.5)
