#!/usr/bin/env python3
"""
Test suite for migrated top 3 modules
Verifies production modules and compatibility shims work correctly
"""

import sys
import warnings
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestMigratedModules:
    """Test the newly migrated production modules"""

    def test_drift_governor_production_import(self):
        """Test Ethical Drift Governor imports from production location"""
        from lukhas.acceptance.accepted.governance.drift_governor import (
            EthicalDriftGovernor,
            EthicalSeverity,
            InterventionType,
        )

        # Verify classes are importable
        assert EthicalDriftGovernor is not None
        assert EthicalSeverity is not None
        assert InterventionType is not None

        # Verify enums work
        assert EthicalSeverity.CRITICAL.value == "critical"
        assert InterventionType.MONITOR.value == "monitor"

        # Verify instantiation
        governor = EthicalDriftGovernor()
        assert hasattr(governor, 'governance_rules')
        assert hasattr(governor, 'active_concerns')

    def test_dna_helix_production_import(self):
        """Test DNA Helix Architecture imports from production location"""
        from lukhas.acceptance.accepted.dna.helix.dna_memory_architecture import (
            DNAMemoryArchitecture,
        )
        from lukhas.acceptance.accepted.dna.helix.helix_vault import HelixVault

        # Verify classes are importable
        assert DNAMemoryArchitecture is not None
        assert HelixVault is not None

        # Verify basic functionality
        vault = HelixVault()
        assert hasattr(vault, 'store_memory')
        assert hasattr(vault, 'retrieve_memory')

    def test_drift_tracker_production_import(self):
        """Test Memory Drift Tracker imports from production location"""
        from lukhas.acceptance.accepted.monitoring.drift_tracker import (
            MemoryDriftTracker,
        )

        # Verify class is importable
        assert MemoryDriftTracker is not None

        # Verify instantiation
        tracker = MemoryDriftTracker()
        assert hasattr(tracker, 'track_drift')
        assert hasattr(tracker, 'get_drift_metrics')

    def test_compatibility_shim_warning(self):
        """Test that compatibility shims issue deprecation warnings"""

        # Test Ethical Drift Governor shim
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Verify deprecation warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert "lukhas.acceptance.accepted.governance.drift_governor" in str(w[0].message)

    def test_compatibility_shim_functionality(self):
        """Test that shims still provide the same functionality"""

        # Import from old location (via shim)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Suppress warnings for this test
            from lukhas.acceptance.archive.memory_variants.memory.governance.ethical_drift_governor import (
                EthicalDriftGovernor as OldGovernor,
            )
            from lukhas.acceptance.archive.memory_variants.memory.governance.ethical_drift_governor import (
                EthicalSeverity as OldSeverity,
            )

        # Import from new location
        from lukhas.acceptance.accepted.governance.drift_governor import (
            EthicalDriftGovernor as NewGovernor,
        )
        from lukhas.acceptance.accepted.governance.drift_governor import (
            EthicalSeverity as NewSeverity,
        )

        # They should be the same class
        assert OldGovernor is NewGovernor
        assert OldSeverity is NewSeverity

        # Functionality should be identical
        old_instance = OldGovernor()
        new_instance = NewGovernor()

        assert type(old_instance) == type(new_instance)
        assert old_instance.__class__.__name__ == new_instance.__class__.__name__

class TestProductionIntegration:
    """Test integration with existing LUKHAS systems"""

    def test_drift_governor_guardian_alignment(self):
        """Test that Drift Governor aligns with Guardian system"""
        from lukhas.acceptance.accepted.governance.drift_governor import (
            EthicalDriftGovernor,
            EthicalSeverity,
        )

        governor = EthicalDriftGovernor()

        # Verify drift threshold is set correctly (0.15 as per spec)
        rules = governor.governance_rules
        assert any(
            rule.drift_threshold <= 0.15
            for rule in rules.values()
        )

        # Verify severity levels align with Guardian system
        assert EthicalSeverity.LOW.value == "low"
        assert EthicalSeverity.CRITICAL.value == "critical"

    def test_dna_helix_memory_integration(self):
        """Test DNA Helix integrates with memory systems"""
        from lukhas.acceptance.accepted.dna.helix.dna_memory_architecture import (
            DNAMemoryArchitecture,
        )

        # Verify it follows the memory architecture patterns
        dna_memory = DNAMemoryArchitecture()
        assert hasattr(dna_memory, 'encode_memory')
        assert hasattr(dna_memory, 'decode_memory')

    def test_trinity_framework_alignment(self):
        """Test all migrated modules align with Trinity Framework"""

        # Guardian (🛡️) - Ethical Drift Governor
        from lukhas.acceptance.accepted.governance.drift_governor import (
            EthicalDriftGovernor,
        )
        governor = EthicalDriftGovernor()
        assert hasattr(governor, 'monitor_drift')  # Guardian monitoring

        # Identity (⚛️) - DNA Helix preserves identity
        from lukhas.acceptance.accepted.dna.helix.helix_vault import HelixVault
        vault = HelixVault()
        assert hasattr(vault, 'preserve_identity')  # Identity preservation

        # Consciousness (🧠) - Drift Tracker maintains awareness
        from lukhas.acceptance.accepted.monitoring.drift_tracker import (
            MemoryDriftTracker,
        )
        tracker = MemoryDriftTracker()
        assert hasattr(tracker, 'track_drift')  # Consciousness of changes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
