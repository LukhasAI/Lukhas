"""
Tests for the identity interface module.
"""


def test_import_get_lambda_id_validator():
    """
    Tests that the get_lambda_id_validator function can be imported from the
    identity interface module.
    """
    from lukhas.governance.identity.interface import get_lambda_id_validator

    assert callable(get_lambda_id_validator)
