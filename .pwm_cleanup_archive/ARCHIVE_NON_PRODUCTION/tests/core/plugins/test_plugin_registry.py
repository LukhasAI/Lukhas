from core.plugin_registry import Plugin, PluginRegistry, PluginType


class DummyPlugin(Plugin):
    def get_plugin_type(self) -> PluginType:
        return PluginType.SYMBOLIC_PROCESSOR

    def get_plugin_name(self) -> str:
        return "dummy"

    def get_version(self) -> str:
        return "0.1"


def test_register_and_retrieve_plugin():
    registry = PluginRegistry()
    plugin = DummyPlugin()
    registry.register_plugin(plugin)

    retrieved = registry.get_plugin(PluginType.SYMBOLIC_PROCESSOR, "dummy")
    assert retrieved is plugin


def test_list_plugins_by_type():
    registry = PluginRegistry()
    plugin = DummyPlugin()
    registry.register_plugin(plugin)

    plugins = registry.list_plugins(PluginType.SYMBOLIC_PROCESSOR)
    assert plugin in plugins
