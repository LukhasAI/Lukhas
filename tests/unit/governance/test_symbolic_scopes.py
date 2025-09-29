from lukhas.governance.identity.core.sent.symbolic_scopes import SymbolicScopesManager


def test_define_scope_updates_symbol_registry():
    manager = SymbolicScopesManager(config={})
    manager.define_scope(
        "quantum_bridge",
        "🪐",
        "Quantum bridge consent",
        {"tier_5": {"required": False, "enhanced_security": True}},
    )

    assert manager.scope_hierarchy["quantum_bridge"]["symbol"] == "🪐"
    assert manager.get_symbolic_representation(["quantum_bridge"]) == "🪐"
    assert manager.parse_symbolic_consent("🪐") == ["quantum_bridge"]


def test_scope_requirements_reflect_tier_boundaries():
    manager = SymbolicScopesManager(config={})
    requirements = manager.get_scope_requirements("memory", 4)

    assert requirements["available"] is True
    assert requirements["restricted"] is False
    assert requirements["requirements"].get("enhanced_security") is True


def test_validate_scope_access_respects_tier_and_grants():
    manager = SymbolicScopesManager(
        config={
            "user_tiers": {"alice": 2, "lambda_root": 5},
            "granted_scopes": {
                "alice": ["analytics"],
                "lambda_root": ["memory", "integration"],
            },
        }
    )

    assert manager.validate_scope_access("alice", "analytics") is True
    assert manager.validate_scope_access("alice", "memory") is False
    assert manager.validate_scope_access("lambda_root", "integration") is True


def test_symbolic_consent_roundtrip_parsing():
    manager = SymbolicScopesManager(config={})
    symbolic = manager.get_symbolic_representation(["audio", "analytics", "trace"])

    assert symbolic
    assert manager.parse_symbolic_consent(symbolic) == ["audio", "analytics", "trace"]
