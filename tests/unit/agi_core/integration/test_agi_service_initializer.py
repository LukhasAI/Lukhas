from agi_core.integration.agi_service_initializer import AGIServiceConfiguration, AGIServiceInitializer


class DummyConfig(AGIServiceConfiguration):
    def __init__(self):
        self.service_configs = {
            "svc_a": {"priority": 2},
            "svc_b": {"priority": 1},
            "svc_c": {"priority": 3},
        }


def test_resolve_dependency_order_sorts_by_priority():
    initializer = AGIServiceInitializer(config=DummyConfig())
    order = initializer._resolve_dependency_order()
    assert order == ["svc_b", "svc_a", "svc_c"]
