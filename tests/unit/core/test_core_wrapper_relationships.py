from __future__ import annotations

from datetime import datetime, timezone

from core import core_wrapper


class StubSymbol:
    def __init__(self, name: str, properties: dict | None = None):
        self.name = name
        self.properties = properties or {}
        self.created_at = datetime.now(timezone.utc)


class StubRelationship:
    def __init__(self, symbol1: StubSymbol, symbol2: StubSymbol, relationship_type: str, properties: dict | None = None):
        self.symbol1 = symbol1
        self.symbol2 = symbol2
        self.type = relationship_type
        self.properties = properties or {}
        self.created_at = datetime.now(timezone.utc)


class StubSymbolicWorld:
    def __init__(self) -> None:
        self.symbols: dict[str, StubSymbol] = {}
        self.relationships: dict[str, list[StubRelationship]] = {}

    def create_symbol(self, name: str, properties: dict) -> StubSymbol:
        symbol = StubSymbol(name, properties)
        self.symbols[name] = symbol
        return symbol

    def link_symbols(self, symbol1: StubSymbol, symbol2: StubSymbol, relationship_type: str, properties: dict | None = None) -> None:
        relationship = StubRelationship(symbol1, symbol2, relationship_type, properties)
        self.relationships.setdefault(symbol1.name, []).append(relationship)
        self.relationships.setdefault(symbol2.name, []).append(relationship)

    def get_related_symbols(self, symbol: StubSymbol) -> list[StubSymbol]:
        related = []
        for relationship in self.relationships.get(symbol.name, []):
            if relationship.symbol1.name == symbol.name:
                related.append(relationship.symbol2)
            else:
                related.append(relationship.symbol1)
        return related


class StubSymbolicReasoner:
    def __init__(self, world: StubSymbolicWorld) -> None:
        self.world = world

    def reason(self, symbol: StubSymbol) -> dict:
        return {"focus": symbol.name}

    def find_patterns(self, symbols: list[StubSymbol]) -> list[dict]:
        return [{"symbols": [s.name for s in symbols]}]


def test_perform_symbolic_reasoning_includes_relationships():
    registry_snapshot = core_wrapper._REGISTRY.copy()
    dry_run_snapshot = core_wrapper.LUKHAS_DRY_RUN_MODE

    try:
        world = StubSymbolicWorld()
        reasoner = StubSymbolicReasoner(world)
        core_wrapper.register_symbolic_world(world)
        core_wrapper.register_symbolic_reasoner(reasoner)

        symbol_a = world.create_symbol("alpha", {})
        symbol_b = world.create_symbol("beta", {})
        world.link_symbols(symbol_a, symbol_b, "ally", {"confidence": 0.9})

        core_wrapper.LUKHAS_DRY_RUN_MODE = False

        wrapper = core_wrapper.CoreWrapper()
        result = wrapper.perform_symbolic_reasoning("alpha", mode="production")

        assert result.success is True
        assert result.relationships, "Expected relationships to be extracted"
        ally_relationship = next(rel for rel in result.relationships if rel["target"] == "beta")
        assert ally_relationship["type"] == "ally"
        assert ally_relationship["properties"]["confidence"] == 0.9
    finally:
        core_wrapper._REGISTRY.clear()
        core_wrapper._REGISTRY.update(registry_snapshot)
        core_wrapper.LUKHAS_DRY_RUN_MODE = dry_run_snapshot