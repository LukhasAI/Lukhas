"""
Candidate Systems Phase 4 Tests
Tests feature flag functionality and adapter-only I/O pattern
"""

import os
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestPhase4FeatureFlags:
    """Test Phase 4 feature flag implementation"""

    def setup_method(self):
        """Clean environment before each test"""
        for flag in ["UL_ENABLED", "VIVOX_LITE", "QIM_SANDBOX"]:
            if flag in os.environ:
                del os.environ[flag]

        # Clear any cached modules
        modules_to_clear = [
            'lukhas.candidate.ul',
            'lukhas.candidate.vivox',
            'lukhas.candidate.qim'
        ]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]

    def test_feature_flag_configuration(self):
        """Test feature flag configuration is properly set up"""
        from lukhas.candidate import FEATURE_FLAGS, get_all_feature_flags

        # Verify all required flags are defined
        assert "UL_ENABLED" in FEATURE_FLAGS
        assert "VIVOX_LITE" in FEATURE_FLAGS
        assert "QIM_SANDBOX" in FEATURE_FLAGS

        # Verify they are all disabled by default
        flags = get_all_feature_flags()
        assert flags["UL_ENABLED"] == False
        assert flags["VIVOX_LITE"] == False
        assert flags["QIM_SANDBOX"] == False

    def test_ul_disabled_by_default(self):
        """Test UL returns stub when disabled"""
        # Import after environment cleanup
        from lukhas.candidate.ul import get_universal_language

        ul = get_universal_language()
        assert hasattr(ul, 'enabled')
        assert ul.enabled == False

        # Test adapter-only I/O pattern - should return error dict
        result = ul.translate("test")
        assert isinstance(result, dict)
        assert "error" in result
        assert "UL_ENABLED=false" in result["error"]

    def test_vivox_disabled_by_default(self):
        """Test VIVOX returns stub when disabled"""
        from lukhas.candidate.vivox import get_vivox_system

        vivox = get_vivox_system()
        assert hasattr(vivox, 'enabled')
        assert vivox.enabled == False

        # Test adapter-only I/O pattern
        result = vivox.process_experience("test")
        assert isinstance(result, dict)
        assert "error" in result
        assert "VIVOX_LITE=false" in result["error"]

    def test_qim_disabled_by_default(self):
        """Test QIM returns stub when disabled"""
        from lukhas.candidate.qim import get_qim_processor

        qim = get_qim_processor()
        assert hasattr(qim, 'enabled')
        assert qim.enabled == False

        # Test adapter-only I/O pattern
        result = qim.quantum_process("test")
        assert isinstance(result, dict)
        assert "error" in result
        assert "QIM_SANDBOX=false" in result["error"]

    def test_trinity_sync_disabled(self):
        """Test Trinity synchronization when systems are disabled"""
        from lukhas.candidate.qim import trinity_sync as qim_sync
        from lukhas.candidate.ul import trinity_sync as ul_sync
        from lukhas.candidate.vivox import trinity_sync as vivox_sync

        ul_result = ul_sync()
        vivox_result = vivox_sync()
        qim_result = qim_sync()

        # All should have Trinity symbols
        for result in [ul_result, vivox_result, qim_result]:
            assert result['identity'] == '⚛️'
            assert result['consciousness'] == '🧠'
            assert result['guardian'] == '🛡️'

        # All should show as disabled
        assert ul_result['ul_status'] == 'disabled_by_feature_flag'
        assert vivox_result['vivox_status'] == 'disabled_by_feature_flag'
        assert qim_result['qim_status'] == 'disabled_by_feature_flag'

class TestPhase4EnabledSystems:
    """Test systems when properly enabled"""

    def test_ul_enabled_functionality(self):
        """Test UL core functionality when enabled"""
        # Set flag before import
        os.environ["UL_ENABLED"] = "true"

        try:
            # Force fresh import
            if 'lukhas.candidate.ul' in sys.modules:
                del sys.modules['lukhas.candidate.ul']
            if 'lukhas.candidate.ul.core' in sys.modules:
                del sys.modules['lukhas.candidate.ul.core']

            from lukhas.candidate.ul import get_universal_language

            ul = get_universal_language()
            assert ul is not None

            # Test core functionality through adapter interface
            stats = ul.get_vocabulary_stats()
            assert isinstance(stats, dict)
            assert "total_glyphs" in stats
            assert stats["total_glyphs"] > 0
            assert stats["trinity_aligned"] == True

        finally:
            # Clean up
            if "UL_ENABLED" in os.environ:
                del os.environ["UL_ENABLED"]

    def test_vivox_enabled_functionality(self):
        """Test VIVOX core functionality when enabled"""
        os.environ["VIVOX_LITE"] = "true"

        try:
            # Force fresh import
            if 'lukhas.candidate.vivox' in sys.modules:
                del sys.modules['lukhas.candidate.vivox']
            if 'lukhas.candidate.vivox.core' in sys.modules:
                del sys.modules['lukhas.candidate.vivox.core']

            from lukhas.candidate.vivox import get_vivox_system

            vivox = get_vivox_system()
            assert vivox is not None

            # Test core functionality
            state = vivox.get_consciousness_state()
            assert isinstance(state, dict)
            assert "consciousness_level" in state
            assert state["trinity_synchronized"] == True

        finally:
            if "VIVOX_LITE" in os.environ:
                del os.environ["VIVOX_LITE"]

    def test_qim_enabled_functionality(self):
        """Test QIM core functionality when enabled"""
        os.environ["QIM_SANDBOX"] = "true"

        try:
            # Force fresh import
            if 'lukhas.candidate.qim' in sys.modules:
                del sys.modules['lukhas.candidate.qim']
            if 'lukhas.candidate.qim.core' in sys.modules:
                del sys.modules['lukhas.candidate.qim.core']

            from lukhas.candidate.qim import get_qim_processor

            qim = get_qim_processor()
            assert qim is not None

            # Test core functionality
            status = qim.get_system_status()
            assert isinstance(status, dict)
            assert "quantum_registers" in status
            assert status["quantum_registers"] > 0
            assert status["trinity_synchronized"] == True

        finally:
            if "QIM_SANDBOX" in os.environ:
                del os.environ["QIM_SANDBOX"]

class TestPhase4Integration:
    """Test Phase 4 integration features"""

    def test_candidate_system_info(self):
        """Test candidate systems information"""
        from lukhas.candidate import get_candidate_systems_info

        info = get_candidate_systems_info()

        assert info["version"] == "1.0.0-phase4"
        assert info["migration_phase"] == "Phase 4 - Candidate Systems"
        assert info["adapter_io_pattern"] == "All systems follow adapter-only I/O pattern"

        # Verify architecture notes
        notes = info["architecture_notes"]
        assert "Systems are disabled by default for safety" in notes
        assert "Feature flags control activation" in notes
        assert "Trinity Framework integration required" in notes
        assert "Adapter-only I/O prevents direct system access" in notes
        assert "Phase 4 migration complete" in notes

    def test_trinity_sync_all(self):
        """Test Trinity synchronization across all systems"""
        from lukhas.candidate import trinity_sync_all

        sync_result = trinity_sync_all()

        # Verify core Trinity elements
        assert sync_result['identity'] == '⚛️'
        assert sync_result['consciousness'] == '🧠'
        assert sync_result['guardian'] == '🛡️'
        assert sync_result['phase4_complete'] == True

        # Verify status information
        status = sync_result['candidate_systems_status']
        assert status['migration_phase'] == "Phase 4 Complete"
        assert status['enabled_count'] == 0  # All disabled by default
        assert status['disabled_count'] == 3

    def test_adapter_only_io_pattern(self):
        """Test that all systems follow adapter-only I/O pattern"""
        # Clean environment to ensure stubs are used
        for flag in ["UL_ENABLED", "VIVOX_LITE", "QIM_SANDBOX"]:
            if flag in os.environ:
                del os.environ[flag]

        # Clear cached modules to force fresh imports
        modules_to_clear = [
            'lukhas.candidate.ul',
            'lukhas.candidate.vivox',
            'lukhas.candidate.qim'
        ]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]

        from lukhas.candidate.qim import get_qim_processor
        from lukhas.candidate.ul import get_universal_language
        from lukhas.candidate.vivox import get_vivox_system

        # Get system instances (all should be stubs when disabled)
        ul = get_universal_language()
        vivox = get_vivox_system()
        qim = get_qim_processor()

        # Verify stubs are returned
        assert hasattr(ul, 'enabled')
        assert hasattr(vivox, 'enabled')
        assert hasattr(qim, 'enabled')
        assert ul.enabled == False
        assert vivox.enabled == False
        assert qim.enabled == False

        # Test that all methods return structured data (dicts) not raw objects
        ul_result = ul.translate("test")
        vivox_result = vivox.process_experience("test")
        qim_result = qim.quantum_process("test")

        # All should return dictionaries with error information
        for result in [ul_result, vivox_result, qim_result]:
            assert isinstance(result, dict)
            assert "error" in result
            assert "feature" in result
            assert result["feature"] == "disabled"

    def test_feature_flag_validation(self):
        """Test feature flag validation system"""
        from lukhas.candidate import validate_feature_flags

        validation = validate_feature_flags()

        assert validation["total_flags"] == 3
        assert validation["enabled_count"] == 0
        assert validation["disabled_count"] == 3
        assert validation["trinity_framework"] == "⚛️🧠🛡️"
        assert validation["migration_phase"] == "Phase 4 Complete"

        # Verify flags status
        flags = validation["flags_status"]
        assert flags["UL_ENABLED"] == False
        assert flags["VIVOX_LITE"] == False
        assert flags["QIM_SANDBOX"] == False

        # Verify no enabled systems
        assert validation["enabled_systems"] == []

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
