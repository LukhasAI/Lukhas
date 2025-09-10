"""
Lambda ID Validator Module
==========================

ΛID validation functionality.
"""


class LambdIdValidator:
    """Validator for Lambda ID (ΛID) format and compliance"""

    def __init__(self):
        self.initialized = True

    def validate_lambda_id(self, lambda_id):
        """Validate Lambda ID format"""
        # Basic validation - ΛID should start with Λ
        return lambda_id and lambda_id.startswith("Λ")

    def get_tier_from_lambda_id(self, _lambda_id):
        """Extract tier information from Lambda ID"""
        # Stub implementation
        return "T1"


# Create default validator instance
default_validator = LambdIdValidator()


def validate_lambda_id(lambda_id):
    """Validate Lambda ID using default validator"""
    return default_validator.validate_lambda_id(lambda_id)