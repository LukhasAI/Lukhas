import importlib


def test_import_validator_node():
    mod = importlib.import_module("matriz.nodes.validator_node")
    assert hasattr(mod, "ValidatorNode")
