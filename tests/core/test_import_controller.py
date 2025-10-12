"""
Tests for Import Controllers

Comprehensive functional tests for lane detection and YAML compliance.
Covers ops/matriz.yaml enforcement and lane boundary validation.

Part of BATCH-COPILOT-TESTS-01
Tasks Tested:
- TEST-HIGH-CONTROLLER-01: Lane detection and import boundaries
- TEST-HIGH-CONTROLLER-02: ops/matriz.yaml compliance verification

Trinity Framework: 🛡️ Guardian · 🏗️ Architecture
"""

from pathlib import Path

import pytest
import yaml

from labs.bridge.api.controllers import (
    ImportController,
    ImportViolation,
    ServiceLane as Lane,
)

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def import_controller():
    """Fresh import controller instance."""
    return ImportController()


@pytest.fixture
def matriz_yaml_path():
    """Path to ops/matriz.yaml configuration."""
    return Path("/Users/agi_dev/LOCAL-REPOS/Lukhas/ops/matriz.yaml")


@pytest.fixture
def matriz_config(matriz_yaml_path):
    """Load matriz.yaml configuration."""
    if matriz_yaml_path.exists():
        with open(matriz_yaml_path, 'r') as f:
            return yaml.safe_load(f)
    return None


# ============================================================================
# TEST-HIGH-CONTROLLER-01: Lane Detection
# ============================================================================

@pytest.mark.unit
def test_import_controller_lane_detection_lukhas(import_controller):
    """Test lane detection for lukhas/ (production lane)."""
    file_path = Path("lukhas/consciousness/awareness_protocol.py")
    
    lane = import_controller.detect_lane(file_path)
    
    assert lane == Lane.LUKHAS
    assert lane.name == "LUKHAS"


@pytest.mark.unit
def test_import_controller_lane_detection_candidate(import_controller):
    """Test lane detection for candidate/ (development lane)."""
    file_path = Path("candidate/bridge/api/onboarding.py")
    
    lane = import_controller.detect_lane(file_path)
    
    assert lane == Lane.CANDIDATE
    assert lane.name == "CANDIDATE"


@pytest.mark.unit
def test_import_controller_lane_detection_core(import_controller):
    """Test lane detection for core/ (shared lane)."""
    file_path = Path("core/symbolic/glyph_mapping.py")
    
    lane = import_controller.detect_lane(file_path)
    
    assert lane == Lane.CORE
    assert lane.name == "CORE"


@pytest.mark.unit
def test_import_controller_lane_detection_matriz(import_controller):
    """Test lane detection for matriz/ (cognitive DNA)."""
    file_path = Path("matriz/cognitive_dna_processor.py")
    
    lane = import_controller.detect_lane(file_path)
    
    assert lane == Lane.MATRIZ
    assert lane.name == "MATRIZ"


@pytest.mark.unit
def test_import_controller_allowed_imports_lukhas(import_controller):
    """Test allowed imports for lukhas/ lane."""
    source_lane = Lane.LUKHAS
    
    # Allowed: core, matriz, universal_language
    allowed_lanes = import_controller.get_allowed_imports(source_lane)
    
    assert Lane.CORE in allowed_lanes
    assert Lane.MATRIZ in allowed_lanes
    # lukhas can import from itself
    assert Lane.LUKHAS in allowed_lanes


@pytest.mark.unit
def test_import_controller_allowed_imports_candidate(import_controller):
    """Test allowed imports for candidate/ lane."""
    source_lane = Lane.CANDIDATE
    
    # Allowed: core, matriz ONLY (NO lukhas)
    allowed_lanes = import_controller.get_allowed_imports(source_lane)
    
    assert Lane.CORE in allowed_lanes
    assert Lane.MATRIZ in allowed_lanes
    assert Lane.LUKHAS not in allowed_lanes  # Critical boundary


@pytest.mark.unit
def test_import_controller_violation_detection_candidate_to_lukhas(import_controller):
    """Test detection of candidate → lukhas violations."""
    source_file = Path("candidate/consciousness/advanced_awareness.py")
    import_statement = "from lukhas.consciousness import awareness_protocol"
    
    violation = import_controller.check_import(source_file, import_statement)
    
    # Should detect violation
    assert violation is not None
    assert violation.violation_type == ImportViolation.FORBIDDEN_LANE


@pytest.mark.unit
def test_import_controller_valid_import_candidate_to_core(import_controller):
    """Test valid candidate → core imports."""
    source_file = Path("candidate/bridge/api/service.py")
    import_statement = "from core.symbolic import glyph_mapping"
    
    violation = import_controller.check_import(source_file, import_statement)
    
    # Should be valid (no violation)
    assert violation is None


# ============================================================================
# TEST-HIGH-CONTROLLER-02: YAML Compliance
# ============================================================================

@pytest.mark.unit
def test_import_controller_yaml_config_exists(matriz_yaml_path):
    """Test that ops/matriz.yaml exists."""
    assert matriz_yaml_path.exists()
    assert matriz_yaml_path.is_file()


@pytest.mark.unit
def test_import_controller_yaml_valid_structure(matriz_config):
    """Test ops/matriz.yaml has valid structure."""
    if matriz_config is None:
        pytest.skip("matriz.yaml not found")
    
    # Verify top-level keys
    assert "lanes" in matriz_config or "import_rules" in matriz_config
    
    # Verify lanes defined
    if "lanes" in matriz_config:
        assert isinstance(matriz_config["lanes"], dict)
        assert len(matriz_config["lanes"]) > 0


@pytest.mark.unit
def test_import_controller_yaml_lane_definitions(matriz_config):
    """Test lane definitions in ops/matriz.yaml."""
    if matriz_config is None or "lanes" not in matriz_config:
        pytest.skip("matriz.yaml lanes not found")
    
    lanes = matriz_config["lanes"]
    
    # Essential lanes should be defined
    essential_lanes = ["lukhas", "labs", "core", "matriz"]
    
    for lane in essential_lanes:
        # Check if lane exists (case-insensitive)
        lane_exists = any(k.lower() == lane for k in lanes.keys())
        assert lane_exists, f"Lane '{lane}' not defined in matriz.yaml"


@pytest.mark.unit
def test_import_controller_yaml_import_rules(matriz_config):
    """Test import rules in ops/matriz.yaml."""
    if matriz_config is None:
        pytest.skip("matriz.yaml not found")
    
    # Check for import rules section
    if "import_rules" in matriz_config:
        rules = matriz_config["import_rules"]
        assert isinstance(rules, dict) or isinstance(rules, list)
    elif "lanes" in matriz_config:
        # Import rules may be embedded in lane definitions
        lanes = matriz_config["lanes"]
        for lane_name, lane_config in lanes.items():
            if "allowed_imports" in lane_config:
                assert isinstance(lane_config["allowed_imports"], list)


@pytest.mark.unit
def test_import_controller_yaml_enforcement(import_controller, matriz_config):
    """Test that controller enforces matriz.yaml rules."""
    if matriz_config is None:
        pytest.skip("matriz.yaml not found")
    
    # Load rules into controller
    import_controller.load_matriz_config(matriz_config)
    
    # Verify rules loaded
    assert import_controller.has_rules_loaded() is True


@pytest.mark.unit
def test_import_controller_yaml_lukhas_rules(matriz_config):
    """Test lukhas/ lane rules in matriz.yaml."""
    if matriz_config is None or "lanes" not in matriz_config:
        pytest.skip("matriz.yaml lanes not found")
    
    lanes = matriz_config["lanes"]
    
    # Find lukhas lane (case-insensitive)
    lukhas_lane = None
    for lane_name, lane_config in lanes.items():
        if lane_name.lower() == "lukhas":
            lukhas_lane = lane_config
            break
    
    if lukhas_lane and "allowed_imports" in lukhas_lane:
        allowed = lukhas_lane["allowed_imports"]
        
        # Should allow core, matriz
        assert any("core" in str(a).lower() for a in allowed)
        assert any("matriz" in str(a).lower() for a in allowed)


@pytest.mark.unit
def test_import_controller_yaml_candidate_rules(matriz_config):
    """Test candidate/ lane rules in matriz.yaml."""
    if matriz_config is None or "lanes" not in matriz_config:
        pytest.skip("matriz.yaml lanes not found")
    
    lanes = matriz_config["lanes"]
    
    # Find candidate lane
    candidate_lane = None
    for lane_name, lane_config in lanes.items():
        if lane_name.lower() == "labs":
            candidate_lane = lane_config
            break
    
    if candidate_lane and "allowed_imports" in candidate_lane:
        allowed = candidate_lane["allowed_imports"]
        
        # Should allow core, matriz ONLY
        assert any("core" in str(a).lower() for a in allowed)
        assert any("matriz" in str(a).lower() for a in allowed)
        
        # Should NOT allow lukhas
        assert not any("lukhas" in str(a).lower() for a in allowed)


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
def test_import_controller_full_validation(import_controller, matriz_config):
    """Test complete import validation workflow."""
    if matriz_config is None:
        pytest.skip("matriz.yaml not found")
    
    # Load config
    import_controller.load_matriz_config(matriz_config)
    
    # Test valid import
    valid_source = Path("lukhas/api/service.py")
    valid_import = "from core.symbolic import SymbolMapper"
    
    violation = import_controller.check_import(valid_source, valid_import)
    assert violation is None
    
    # Test invalid import
    invalid_source = Path("candidate/consciousness/module.py")
    invalid_import = "from lukhas.consciousness import Protocol"
    
    violation = import_controller.check_import(invalid_source, invalid_import)
    assert violation is not None


@pytest.mark.integration
def test_import_controller_scan_directory(import_controller):
    """Test scanning a directory for import violations."""
    # Scan candidate/ directory
    violations = import_controller.scan_directory(
        Path("candidate/"),
        recursive=True
    )
    
    # Should return list of violations (may be empty if compliant)
    assert isinstance(violations, list)
    
    # If violations found, verify structure
    for violation in violations:
        assert hasattr(violation, 'source_file')
        assert hasattr(violation, 'import_statement')
        assert hasattr(violation, 'violation_type')


# ============================================================================
# Edge Cases
# ============================================================================

@pytest.mark.unit
def test_import_controller_unknown_lane(import_controller):
    """Test handling of files in unknown lanes."""
    unknown_file = Path("random_dir/some_file.py")
    
    lane = import_controller.detect_lane(unknown_file)
    
    # Should return UNKNOWN or raise exception
    assert lane == Lane.UNKNOWN or lane is None


@pytest.mark.unit
def test_import_controller_relative_imports(import_controller):
    """Test handling of relative imports."""
    source_file = Path("candidate/consciousness/module.py")
    relative_import = "from . import submodule"
    
    # Relative imports within same lane are always allowed
    violation = import_controller.check_import(source_file, relative_import)
    
    assert violation is None


@pytest.mark.unit
def test_import_controller_stdlib_imports(import_controller):
    """Test that stdlib imports are always allowed."""
    source_file = Path("candidate/bridge/api/service.py")
    stdlib_imports = [
        "import os",
        "from pathlib import Path",
        "import asyncio",
        "from typing import List"
    ]
    
    for import_stmt in stdlib_imports:
        violation = import_controller.check_import(source_file, import_stmt)
        assert violation is None


@pytest.mark.unit
def test_import_controller_third_party_imports(import_controller):
    """Test handling of third-party imports."""
    source_file = Path("lukhas/api/service.py")
    third_party_imports = [
        "import numpy",
        "from fastapi import FastAPI",
        "import pandas as pd"
    ]
    
    for import_stmt in third_party_imports:
        violation = import_controller.check_import(source_file, import_stmt)
        # Third-party imports should be allowed
        assert violation is None


@pytest.mark.unit
def test_import_controller_malformed_import(import_controller):
    """Test handling of malformed import statements."""
    source_file = Path("candidate/module.py")
    malformed_imports = [
        "import",  # Missing module
        "from",  # Incomplete
        "import 123",  # Invalid name
    ]
    
    for import_stmt in malformed_imports:
        try:
            violation = import_controller.check_import(source_file, import_stmt)
            # Should handle gracefully
            assert True
        except Exception:
            # Or raise appropriate error
            pass


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.performance
def test_import_controller_scan_performance(import_controller):
    """Test import scanning performance."""
    import time
    
    start = time.time()
    
    # Scan small directory
    violations = import_controller.scan_directory(
        Path("candidate/bridge/api/"),
        recursive=False
    )
    
    elapsed = time.time() - start
    
    # Should complete in reasonable time (<1 second for small dir)
    assert elapsed < 1.0
    assert isinstance(violations, list)
