from hub.service_registry import get_service, register_all_providers


def test_quantum_bio_optimizer_provider():
    register_all_providers()
    optimizer = get_service("quantum_bio_optimizer")
    assert optimizer is not None
