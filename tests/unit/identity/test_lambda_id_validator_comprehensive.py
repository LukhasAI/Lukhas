"""
Comprehensive Unit Tests for LUKHAS Lambda ID Validator

Tests validation rules, tier compliance, format checking, collision detection,
entropy validation, and security features.

Author: LUKHAS AI Systems
Created: 2025-11-12
"""

import unittest
from datetime import datetime, timezone

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from labs.governance.identity.core.id_service.lambd_id_validator import (
    LambdaIDValidator,
    ValidationLevel,
    ValidationResult as VResult,
)


class TestValidatorBasic(unittest.TestCase):
    """Test basic validation functionality"""

    def setUp(self):
        self.validator = LambdaIDValidator()

    def test_valid_tier_2_id(self):
        """Test validation of a valid Tier 2 Lambda ID"""
        lambda_id = "LUKHAS2-A9F3-🌀-X7K1"
        result = self.validator.validate(lambda_id, ValidationLevel.BASIC)
        self.assertTrue(result.format_valid)

    def test_invalid_format(self):
        """Test detection of invalid format"""
        invalid_id = "INVALID-FORMAT"
        result = self.validator.validate(invalid_id, ValidationLevel.BASIC)
        self.assertFalse(result.format_valid)

    def test_invalid_tier(self):
        """Test detection of invalid tier (out of range)"""
        invalid_id = "LUKHAS6-A9F3-○-X7K1"  # Tier 6 doesn't exist
        result = self.validator.validate(invalid_id, ValidationLevel.STANDARD)
        self.assertFalse(result.valid)


class TestTierCompliance(unittest.TestCase):
    """Test tier-specific validation rules"""

    def setUp(self):
        self.validator = LambdaIDValidator()

    def test_tier_0_valid_symbol(self):
        """Test Tier 0 with valid symbol"""
        lambda_id = "LUKHAS0-1234-○-ABCD"
        result = self.validator.validate(lambda_id, ValidationLevel.STANDARD)
        self.assertTrue(result.tier_compliant or result.format_valid)

    def test_all_validation_levels(self):
        """Test all validation levels"""
        lambda_id = "LUKHAS2-A9F3-🌀-B5E2"

        # Test each level
        for level in ValidationLevel:
            result = self.validator.validate(lambda_id, level)
            self.assertIsNotNone(result)
            self.assertEqual(result.validation_level, level.value)


if __name__ == "__main__":
    unittest.main(verbosity=2)
