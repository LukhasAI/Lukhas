"""
Integration tests for all 25 hidden gems modules.

Tests that all modules can be imported and their schemas are valid.
"""
import json
from pathlib import Path

import pytest


class TestTop25HiddenGemsIntegration:
    """Test suite for verifying all 25 integrated hidden gems modules."""

    def test_matriz_consciousness_modules_import(self):
        """Test that all MATRIZ consciousness modules can be imported."""
        # Module 1-11: MATRIZ consciousness
        from matriz.consciousness.cognitive import adapter
        from matriz.consciousness.core import engine_poetic
        from matriz.consciousness.reflection import (
            dreamseed_unified,
            id_reasoning_engine,
            integrated_safety_system,
            memory_hub,
            orchestration_service,
            reflection_layer,
            swarm,
            symbolic_drift_analyzer,
        )

        assert id_reasoning_engine is not None
        assert swarm is not None
        assert orchestration_service is not None
        assert memory_hub is not None
        assert dreamseed_unified is not None
        assert reflection_layer is not None
        assert symbolic_drift_analyzer is not None
        assert integrated_safety_system is not None
        assert adapter is not None
        assert engine_poetic is not None

    def test_matriz_memory_modules_import(self):
        """Test that all MATRIZ memory modules can be imported."""
        # Module 12-13: MATRIZ memory
        from matriz.memory.core import unified_memory_orchestrator
        from matriz.memory.temporal import hyperspace_dream_simulator

        assert unified_memory_orchestrator is not None
        assert hyperspace_dream_simulator is not None

    def test_matriz_orchestration_modules_import(self):
        """Test that MATRIZ orchestration modules can be imported."""
        # Module 11: MATRIZ orchestration
        from matriz.orchestration import async_orchestrator

        assert async_orchestrator is not None

    def test_core_governance_modules_import(self):
        """Test that core governance modules can be imported."""
        # Module 14-15: Core governance
        from core.governance import guardian_system_integration
        from core.governance.consent_ledger import ledger_v1

        assert guardian_system_integration is not None
        assert ledger_v1 is not None

        # Verify key classes exist
        assert hasattr(ledger_v1, 'ConsentLedgerV1')
        assert hasattr(ledger_v1, 'PolicyVerdict')

    def test_core_system_modules_import(self):
        """Test that core system modules can be imported."""
        # Module 16-27: Core system modules
        import core.oracle_nervous_system
        from core.api import service_stubs
        from core.audit import audit_decision_embedding_engine
        from core.bridge import dream_commerce
        from core.colonies import oracle_colony
        from core.consciousness import id_reasoning_engine
        from core.glyph import glyph_memory_integration
        from core.identity import constitutional_ai_compliance
        from core.integration import executive_decision_integrator
        from core.orchestration import gpt_colony_orchestrator
        from core.symbolic import vocabulary_creativity_engine
        from core.verifold import verifold_unified

        assert glyph_memory_integration is not None
        assert executive_decision_integrator is not None
        assert vocabulary_creativity_engine is not None
        assert gpt_colony_orchestrator is not None
        assert dream_commerce is not None
        assert id_reasoning_engine is not None
        assert service_stubs is not None
        assert verifold_unified is not None
        assert oracle_colony is not None
        assert constitutional_ai_compliance is not None
        assert audit_decision_embedding_engine is not None
        assert core.oracle_nervous_system is not None

    def test_all_schemas_exist(self):
        """Test that all 26 MATRIZ schemas exist and are valid JSON."""
        schemas = [
            # MATRIZ consciousness
            "matriz/consciousness/reflection/id_reasoning_engine.schema.json",
            "matriz/consciousness/reflection/swarm.schema.json",
            "matriz/consciousness/reflection/orchestration_service.schema.json",
            "matriz/consciousness/reflection/memory_hub.schema.json",
            "matriz/consciousness/reflection/dreamseed_unified.schema.json",
            "matriz/consciousness/reflection/reflection_layer.schema.json",
            "matriz/consciousness/reflection/symbolic_drift_analyzer.schema.json",
            "matriz/consciousness/reflection/integrated_safety_system.schema.json",
            "matriz/consciousness/cognitive/adapter.schema.json",
            "matriz/consciousness/core/engine_poetic.schema.json",

            # MATRIZ memory
            "matriz/memory/core/unified_memory_orchestrator.schema.json",
            "matriz/memory/temporal/hyperspace_dream_simulator.schema.json",

            # MATRIZ orchestration
            "matriz/orchestration/async_orchestrator.schema.json",

            # Core governance
            "core/governance/guardian_system_integration.schema.json",
            "core/governance/consent_ledger/ledger_v1.schema.json",

            # Core system
            "core/glyph/glyph_memory_integration.schema.json",
            "core/integration/executive_decision_integrator.schema.json",
            "core/symbolic/vocabulary_creativity_engine.schema.json",
            "core/orchestration/gpt_colony_orchestrator.schema.json",
            "core/bridge/dream_commerce.schema.json",
            "core/consciousness/id_reasoning_engine.schema.json",
            "core/oracle_nervous_system.schema.json",
            "core/api/service_stubs.schema.json",
            "core/verifold/verifold_unified.schema.json",
            "core/colonies/oracle_colony.schema.json",
            "core/identity/constitutional_ai_compliance.schema.json",
            "core/audit/audit_decision_embedding_engine.schema.json",
        ]

        for schema_path in schemas:
            full_path = Path(__file__).parent.parent.parent / schema_path
            assert full_path.exists(), f"Schema not found: {schema_path}"

            # Validate JSON structure
            with open(full_path) as f:
                schema_data = json.load(f)
                assert "module" in schema_data
                assert "version" in schema_data
                assert "type" in schema_data
                assert "matriz_compatible" in schema_data
                assert schema_data["matriz_compatible"] is True
                assert "capabilities" in schema_data
                assert "sends" in schema_data["capabilities"]
                assert "receives" in schema_data["capabilities"]

    def test_schema_signal_interfaces(self):
        """Test that schemas define proper signal interfaces."""
        schema_path = Path(__file__).parent.parent.parent / "core/governance/guardian_system_integration.schema.json"

        with open(schema_path) as f:
            schema = json.load(f)

            # Verify send signals
            assert len(schema["capabilities"]["sends"]) > 0
            for signal in schema["capabilities"]["sends"]:
                assert "signal" in signal
                assert "schema" in signal
                assert "frequency" in signal
                assert "latency_target_ms" in signal

            # Verify receive signals
            assert len(schema["capabilities"]["receives"]) > 0
            for signal in schema["capabilities"]["receives"]:
                assert "signal" in signal
                assert "schema" in signal
                assert "handler" in signal
                assert "required" in signal

    def test_constellation_integration_defined(self):
        """Test that modules define Constellation Framework integration."""
        schema_path = Path(__file__).parent.parent.parent / "core/governance/guardian_system_integration.schema.json"

        with open(schema_path) as f:
            schema = json.load(f)

            assert "constellation_integration" in schema
            assert "stars" in schema["constellation_integration"]
            assert isinstance(schema["constellation_integration"]["stars"], list)
            assert "validates" in schema["constellation_integration"]
            assert "blocks_on_failure" in schema["constellation_integration"]

    def test_performance_requirements_defined(self):
        """Test that all schemas define performance requirements."""
        schemas_to_check = [
            "core/governance/guardian_system_integration.schema.json",
            "matriz/consciousness/reflection/swarm.schema.json",
            "core/audit/audit_decision_embedding_engine.schema.json",
        ]

        for schema_rel_path in schemas_to_check:
            schema_path = Path(__file__).parent.parent.parent / schema_rel_path

            with open(schema_path) as f:
                schema = json.load(f)

                assert "performance" in schema
                assert "max_latency_ms" in schema["performance"]
                assert "target_latency_p95_ms" in schema["performance"]
                assert "memory_limit_mb" in schema["performance"]
                assert "cpu_cores" in schema["performance"]

                # Verify reasonable values
                assert schema["performance"]["max_latency_ms"] > 0
                assert schema["performance"]["max_latency_ms"] <= 10000  # 10 seconds max
                assert schema["performance"]["memory_limit_mb"] > 0
                assert schema["performance"]["cpu_cores"] > 0

    def test_init_files_expose_modules(self):
        """Test that __init__.py files properly expose modules."""
        # Test core.governance exposes guardian_system_integration
        from core import governance
        assert hasattr(governance, 'guardian_system_integration')

        # Test matriz.consciousness.reflection exposes all modules
        from matriz.consciousness import reflection
        assert hasattr(reflection, 'swarm')
        assert hasattr(reflection, 'id_reasoning_engine')
        assert hasattr(reflection, 'memory_hub')

    def test_guardian_system_integration_classes(self):
        """Test that guardian_system_integration has expected classes."""
        from core.governance.guardian_system_integration import (
            GuardianSystemIntegration,
            GuardianValidationRequest,
            GuardianValidationResponse,
            ValidationResult,
        )

        assert GuardianSystemIntegration is not None
        assert GuardianValidationRequest is not None
        assert GuardianValidationResponse is not None
        assert ValidationResult is not None

    def test_consent_ledger_classes(self):
        """Test that consent_ledger has expected classes."""
        from core.governance.consent_ledger.ledger_v1 import (
            ConsentLedgerV1,
            ConsentType,
            PolicyVerdict,
        )

        assert ConsentLedgerV1 is not None
        assert PolicyVerdict is not None
        assert ConsentType is not None

    def test_id_reasoning_engine_classes(self):
        """Test that id_reasoning_engine has expected classes."""
        from matriz.consciousness.reflection.id_reasoning_engine import (
            AccessTier,
            ComplianceRegion,
            EmotionalMemoryVector,
            LukhasIdManager,
        )

        assert AccessTier is not None
        assert ComplianceRegion is not None
        assert EmotionalMemoryVector is not None
        assert LukhasIdManager is not None

    @pytest.mark.smoke
    def test_all_modules_importable_smoke(self):
        """Smoke test: verify all 27 modules can be imported without errors."""
        modules = [
            # MATRIZ consciousness (11)
            "matriz.consciousness.reflection.id_reasoning_engine",
            "matriz.consciousness.reflection.swarm",
            "matriz.consciousness.reflection.orchestration_service",
            "matriz.consciousness.reflection.memory_hub",
            "matriz.consciousness.reflection.dreamseed_unified",
            "matriz.consciousness.reflection.reflection_layer",
            "matriz.consciousness.reflection.symbolic_drift_analyzer",
            "matriz.consciousness.reflection.integrated_safety_system",
            "matriz.consciousness.cognitive.adapter",
            "matriz.consciousness.core.engine_poetic",
            "matriz.orchestration.async_orchestrator",

            # MATRIZ memory (2)
            "matriz.memory.core.unified_memory_orchestrator",
            "matriz.memory.temporal.hyperspace_dream_simulator",

            # Core governance (2)
            "core.governance.guardian_system_integration",
            "core.governance.consent_ledger.ledger_v1",

            # Core system (12)
            "core.glyph.glyph_memory_integration",
            "core.integration.executive_decision_integrator",
            "core.symbolic.vocabulary_creativity_engine",
            "core.orchestration.gpt_colony_orchestrator",
            "core.bridge.dream_commerce",
            "core.consciousness.id_reasoning_engine",
            "core.oracle_nervous_system",
            "core.api.service_stubs",
            "core.verifold.verifold_unified",
            "core.colonies.oracle_colony",
            "core.identity.constitutional_ai_compliance",
            "core.audit.audit_decision_embedding_engine",
        ]

        import_count = 0
        failed_imports = []

        for module_name in modules:
            try:
                __import__(module_name)
                import_count += 1
            except Exception as e:
                failed_imports.append((module_name, str(e)))

        # Report results
        if failed_imports:
            error_msg = "\n".join([f"  - {name}: {error}" for name, error in failed_imports])
            pytest.fail(f"Failed to import {len(failed_imports)}/{len(modules)} modules:\n{error_msg}")

        assert import_count == len(modules), f"Expected {len(modules)} successful imports, got {import_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
