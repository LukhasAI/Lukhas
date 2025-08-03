#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for LUKHAS test suite
Provides common test utilities and symbolic validation helpers
"""

import pytest
import asyncio
import sys
import tempfile
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project paths
sys.path.append(str(Path(__file__).parent.parent))

# Test configuration
pytest_plugins = ['pytest_asyncio']


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def symbolic_validator():
    """Provides symbolic glyph validation utilities"""
    
    class SymbolicValidator:
        # Define symbolic glyph categories
        GLYPH_CATEGORIES = {
            "security": ["🔐", "🔓", "🗝️", "🔑", "🔒"],
            "stability": ["🌿", "🧘", "💎", "⚓", "🏔️"],
            "chaos": ["🌪️", "🌀", "💥", "🚨", "⚡"],
            "thermal": ["🔥", "💨", "❄️", "🧊", "🌋"],
            "consciousness": ["🧠", "👁️", "🔮", "✨", "💫"],
            "protection": ["🛡️", "🏰", "⚔️", "🚨"],
            "transitions": ["→", "↔", "↑", "↓", "🔄"],
            "validation": ["✅", "❌", "⚠️", "🔄", "💪"]
        }
        
        def validate_sequence(self, sequence: List[str], expected_pattern: str = None) -> bool:
            """Validate symbolic sequence structure and coherence"""
            if not sequence:
                return False
            
            # Check for basic structure
            clean_sequence = [s for s in sequence if s != "→"]
            
            if len(clean_sequence) < 1:
                return False
            
            # If pattern specified, check exact match
            if expected_pattern:
                actual_pattern = "".join(clean_sequence)
                return actual_pattern == expected_pattern.replace("→", "")
            
            # Otherwise validate coherence
            return self.validate_coherence(clean_sequence)
        
        def validate_coherence(self, sequence: List[str]) -> bool:
            """Check if symbolic sequence has thematic coherence"""
            if len(sequence) <= 1:
                return True
            
            # Check if sequence follows logical progression
            progression_rules = [
                # Chaos to stability progressions
                (["🌪️", "🌀", "🌿"], "chaos_to_stability"),
                (["🔥", "💨", "❄️"], "thermal_cooling"),
                (["🚨", "🔒", "🛡️"], "alert_to_protection"),
                (["❌", "✅"], "error_correction"),
                (["⚓", "🧘", "🔒"], "consciousness_anchoring")
            ]
            
            for rule_sequence, rule_name in progression_rules:
                if all(glyph in sequence for glyph in rule_sequence):
                    return True
            
            # Check category consistency
            for category, glyphs in self.GLYPH_CATEGORIES.items():
                if category == "transitions":
                    continue
                
                category_count = sum(1 for glyph in sequence if glyph in glyphs)
                if category_count == len(sequence):
                    return True  # All glyphs from same category
            
            return len(sequence) <= 3  # Allow short mixed sequences
        
        def extract_transitions(self, sequence: List[str]) -> List[str]:
            """Extract state transitions from symbolic sequence"""
            clean_sequence = [s for s in sequence if s != "→"]
            transitions = []
            
            for i in range(len(clean_sequence) - 1):
                transition = f"{clean_sequence[i]}→{clean_sequence[i+1]}"
                transitions.append(transition)
            
            return transitions
        
        def get_category(self, glyph: str) -> Optional[str]:
            """Get the category of a glyph"""
            for category, glyphs in self.GLYPH_CATEGORIES.items():
                if glyph in glyphs:
                    return category
            return None
    
    return SymbolicValidator()


@pytest.fixture
def mock_consciousness_state():
    """Provides mock consciousness state data"""
    return {
        "current_state": "focused",
        "last_update": datetime.utcnow().isoformat(),
        "state_history": ["focused"],
        "system_phase": "phase_5_guardian",
        "entropy_score": 0.25,
        "drift_class": "stable"
    }


@pytest.fixture
def mock_entropy_data():
    """Provides mock entropy tracking data"""
    return {
        "metadata": {
            "version": "1.0.0",
            "window_size": 100,
            "last_updated": datetime.utcnow().isoformat(),
            "total_entries": 5
        },
        "entries": [
            {
                "timestamp": (datetime.utcnow().isoformat()),
                "entropy_score": 0.15,
                "previous_state": "neutral",
                "current_state": "open",
                "drift_class": "stable",
                "symbolic_path": ["🔐", "🌿", "🪷"],
                "transition_type": "consent_grant"
            },
            {
                "timestamp": (datetime.utcnow().isoformat()),
                "entropy_score": 0.75,
                "previous_state": "open", 
                "current_state": "turbulent",
                "drift_class": "unstable",
                "symbolic_path": ["🌪️", "⚡", "🚨"],
                "transition_type": "trust_decrease"
            }
        ]
    }


@pytest.fixture
def mock_guardian_threats():
    """Provides mock Guardian threat data"""
    return [
        {
            "threat_id": "drift_001",
            "threat_type": "drift_spike",
            "severity": 0.75,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "entropy_tracker",
            "symbolic_sequence": ["🌪️", "→", "🌀", "→", "🌿"],
            "intervention_required": True,
            "recommended_action": "drift_dampening"
        },
        {
            "threat_id": "entropy_002",
            "threat_type": "entropy_surge", 
            "severity": 0.85,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "consciousness_broadcaster",
            "symbolic_sequence": ["🔥", "→", "💨", "→", "❄️"],
            "intervention_required": True,
            "recommended_action": "entropy_cooling"
        }
    ]


@pytest.fixture
def test_config():
    """Provides test configuration settings"""
    return {
        "test_timeouts": {
            "short": 5,      # 5 seconds
            "medium": 30,    # 30 seconds
            "long": 120      # 2 minutes
        },
        "entropy_thresholds": {
            "stable": 0.3,
            "neutral": 0.7,
            "unstable": 1.0
        },
        "guardian_thresholds": {
            "low": 0.3,
            "medium": 0.5, 
            "high": 0.7,
            "critical": 0.9
        },
        "symbolic_validation": {
            "max_sequence_length": 5,
            "require_coherence": True,
            "allow_mixed_categories": False
        }
    }


@pytest.fixture
def temp_lukhas_env(tmp_path):
    """Creates temporary LUKHAS environment for testing"""
    
    # Create directory structure
    lukhas_dirs = [
        "lukhas_next_gen/stream",
        "lukhas_next_gen/entropy_log",
        "lukhas_next_gen/guardian", 
        "lukhas_next_gen/memory",
        "lukhas_next_gen/quantum",
        "lukhas_next_gen/bridge",
        "lukhas_next_gen/security",
        "transmission_bundle",
        "guardian_audit/logs",
        "guardian_audit/exports",
        "tests"
    ]
    
    for dir_path in lukhas_dirs:
        (tmp_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create essential files
    consciousness_state = {
        "current_state": "focused",
        "last_update": datetime.utcnow().isoformat(),
        "state_history": ["focused"],
        "system_phase": "phase_5_guardian"
    }
    
    with open(tmp_path / "lukhas_next_gen/stream/consciousness_state.json", 'w') as f:
        json.dump(consciousness_state, f, indent=2)
    
    # Create mock component files
    component_files = [
        "lukhas_next_gen/stream/consciousness_broadcaster.py",
        "lukhas_next_gen/entropy_log/entropy_tracker.py",
        "lukhas_next_gen/guardian/sentinel.py",
        "lukhas_next_gen/guardian/intervene.yaml",
        "transmission_bundle/launch_transmission.py"
    ]
    
    for file_path in component_files:
        (tmp_path / file_path).touch()
    
    return tmp_path


# Custom pytest markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "symbolic: mark test as symbolic glyph validation test"
    )
    config.addinivalue_line(
        "markers", "guardian: mark test as Guardian system test"
    )
    config.addinivalue_line(
        "markers", "entropy: mark test as entropy monitoring test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Test collection and reporting
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add symbolic marker to tests with 'symbolic' in name
        if 'symbolic' in item.name.lower() or 'glyph' in item.name.lower():
            item.add_marker(pytest.mark.symbolic)
        
        # Add guardian marker to guardian tests
        if 'guardian' in item.name.lower() or 'intervention' in item.name.lower():
            item.add_marker(pytest.mark.guardian)
            
        # Add entropy marker to entropy tests
        if 'entropy' in item.name.lower() or 'drift' in item.name.lower():
            item.add_marker(pytest.mark.entropy)
        
        # Add integration marker to integration tests
        if 'integration' in item.name.lower() or 'test_transmission' in item.name:
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if 'full_transmission' in item.name or 'complete' in item.name:
            item.add_marker(pytest.mark.slow)


# Helper functions for tests
def assert_symbolic_sequence(sequence: List[str], expected_pattern: str = None, 
                           coherence_required: bool = True):
    """Assert that a symbolic sequence is valid"""
    assert isinstance(sequence, list), "Sequence must be a list"
    assert len(sequence) > 0, "Sequence cannot be empty"
    
    # Clean sequence (remove arrows)
    clean_sequence = [s for s in sequence if s != "→"]
    assert len(clean_sequence) > 0, "Sequence must contain at least one glyph"
    
    # Check expected pattern if provided
    if expected_pattern:
        actual_pattern = "".join(clean_sequence)
        expected_clean = expected_pattern.replace("→", "")
        assert actual_pattern == expected_clean, \
            f"Sequence pattern mismatch: expected {expected_clean}, got {actual_pattern}"
    
    # Check coherence if required
    if coherence_required:
        # This is a simplified coherence check
        # In practice, would use the SymbolicValidator
        assert len(clean_sequence) <= 5, "Sequence should not be excessively long"
        
        # Ensure all elements are strings (valid glyphs)
        for glyph in clean_sequence:
            assert isinstance(glyph, str), f"All glyphs must be strings, got {type(glyph)}"
            assert len(glyph) > 0, "Glyphs cannot be empty strings"


def assert_entropy_range(entropy_value: float, expected_class: str = None):
    """Assert entropy value is in valid range and class"""
    assert isinstance(entropy_value, (int, float)), "Entropy must be numeric"
    assert 0.0 <= entropy_value <= 1.0, f"Entropy {entropy_value} outside valid range [0.0, 1.0]"
    
    if expected_class:
        if expected_class == "stable":
            assert entropy_value < 0.3, f"Stable entropy should be <0.3, got {entropy_value}"
        elif expected_class == "neutral":
            assert 0.3 <= entropy_value < 0.7, f"Neutral entropy should be 0.3-0.7, got {entropy_value}"
        elif expected_class == "unstable":
            assert entropy_value >= 0.7, f"Unstable entropy should be >=0.7, got {entropy_value}"


def assert_guardian_threat_level(severity: float, expected_level: str = None):
    """Assert Guardian threat severity and level"""
    assert isinstance(severity, (int, float)), "Severity must be numeric"
    assert 0.0 <= severity <= 1.0, f"Severity {severity} outside valid range [0.0, 1.0]"
    
    if expected_level:
        if expected_level == "low":
            assert severity < 0.5, f"Low threat should be <0.5, got {severity}"
        elif expected_level == "medium":
            assert 0.5 <= severity < 0.7, f"Medium threat should be 0.5-0.7, got {severity}"
        elif expected_level == "high":
            assert 0.7 <= severity < 0.9, f"High threat should be 0.7-0.9, got {severity}"
        elif expected_level == "critical":
            assert severity >= 0.9, f"Critical threat should be >=0.9, got {severity}"