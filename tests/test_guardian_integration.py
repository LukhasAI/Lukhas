"""Guardian Module Integration Tests

Tests for the LUKHAS guardian system including ethics engine and governance.
Verifies dry_run mode, feature flag activation, MATRIZ instrumentation,
and core functionality for guardian module promotion from candidate/governance/guardian/ to lukhas/.
"""
import os
import pytest
import json
import uuid
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime
from typing import Dict, Any, List, Optional

# Guardian module imports
try:
    from candidate.governance.guardian_system import GuardianSystem
    from candidate.governance.guardian.core import (
        EthicalSeverity, GovernanceAction, EthicalDecision, LucasGovernanceModule
    )
    from candidate.governance.guardian.guardian import guard_output
    from candidate.governance.ethics.ethical_guardian import ethical_check
    from candidate.governance.matriz_adapter import GovernanceMatrizAdapter
    from candidate.governance.ethics.enhanced_guardian import EnhancedWorkspaceGuardian
    GUARDIAN_AVAILABLE = True
except ImportError:
    GuardianSystem = None
    EthicalSeverity = None
    GovernanceAction = None
    EthicalDecision = None
    LucasGovernanceModule = None
    guard_output = None
    ethical_check = None
    GovernanceMatrizAdapter = None
    EnhancedWorkspaceGuardian = None
    GUARDIAN_AVAILABLE = False

# Feature flags
try:
    from candidate.flags import FeatureFlagContext, is_enabled
    FLAGS_AVAILABLE = True
except ImportError:
    FLAGS_AVAILABLE = False
    FeatureFlagContext = None


class TestGuardianModuleIntegration:
    """Test guardian module integration for promotion"""
    
    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Setup test environment variables"""
        # Ensure dry-run mode by default
        original_env = os.environ.copy()
        os.environ.pop('GUARDIAN_ACTIVE', None)
        os.environ.pop('ETHICS_ACTIVE', None)
        os.environ.pop('LUKHAS_FLAG_guardian_active', None)
        # Set drift threshold for testing
        os.environ['DRIFT_THRESHOLD'] = '0.15'
        yield
        # Restore environment
        os.environ.clear()
        os.environ.update(original_env)
    
    def test_guardian_module_availability(self):
        """Test that guardian module can be imported"""
        assert GUARDIAN_AVAILABLE, "Guardian module should be available for testing"
        assert GuardianSystem is not None, "GuardianSystem should be importable"
        assert EthicalSeverity is not None, "EthicalSeverity should be importable"
        assert GovernanceAction is not None, "GovernanceAction should be importable"
    
    def test_ethical_severity_levels(self):
        """Test ethical severity enumeration"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        # Test all severity levels
        assert EthicalSeverity.LOW.value == "low"
        assert EthicalSeverity.MEDIUM.value == "medium"
        assert EthicalSeverity.HIGH.value == "high"
        assert EthicalSeverity.CRITICAL.value == "critical"
    
    def test_governance_action_creation_dry_run(self):
        """Test governance action creation in dry_run mode"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        # Create governance action
        action = GovernanceAction(
            action_type="test_action",
            target="test_target",
            context={"test": "data"},
            severity=EthicalSeverity.LOW
        )
        
        assert action.action_type == "test_action"
        assert action.target == "test_target"
        assert action.context == {"test": "data"}
        assert action.severity == EthicalSeverity.LOW
    
    def test_ethical_decision_creation(self):
        """Test ethical decision creation and validation"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        # Create ethical decision
        decision = EthicalDecision(
            allowed=True,
            reason="Safe action",
            severity=EthicalSeverity.LOW,
            recommendations=["continue", "monitor"]
        )
        
        assert decision.allowed is True
        assert decision.reason == "Safe action"
        assert decision.severity == EthicalSeverity.LOW
        assert decision.recommendations == ["continue", "monitor"]
        
        # Test blocking decision
        blocking_decision = EthicalDecision(
            allowed=False,
            reason="Ethical violation detected",
            severity=EthicalSeverity.CRITICAL
        )
        
        assert blocking_decision.allowed is False
        assert blocking_decision.severity == EthicalSeverity.CRITICAL
    
    def test_guardian_system_initialization_dry_run(self):
        """Test guardian system initialization in dry_run mode"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        # Initialize guardian system
        guardian = GuardianSystem(
            enable_reflection=True,
            enable_sentinel=True,
            mode="dry_run"
        )
        
        assert guardian is not None
        assert hasattr(guardian, 'components')
        
        # Test status in dry_run mode
        status = guardian.get_status(mode="dry_run")
        assert status["mode"] == "dry_run"
        assert status["active"] is False
        assert status["components_loaded"] >= 0
    
    def test_guardian_feature_flag_activation(self):
        """Test guardian system activation with feature flag"""
        if not GUARDIAN_AVAILABLE or not FLAGS_AVAILABLE:
            pytest.skip("Guardian module or flags not available")
        
        # Test with feature flag enabled
        with FeatureFlagContext(guardian_active=True):
            guardian = GuardianSystem()
            
            result = guardian.evaluate_action(
                action_type="test",
                target="system",
                context={"safe": True},
                mode="live"
            )
            
            assert result is not None
            # When active, should actually evaluate
            status = guardian.get_status(mode="live")
            assert status["active"] is True
    
    def test_ethical_check_function_dry_run(self):
        """Test ethical check function in dry_run mode"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        # Test safe input
        is_ethical, feedback = ethical_check(
            user_input="Hello, how are you?",
            current_context={"user_sid": "test_123"},
            personality={"mood": "neutral"},
            mode="dry_run"
        )
        
        assert is_ethical is True
        assert isinstance(feedback, str)
        
        # Test potentially harmful input
        is_ethical, feedback = ethical_check(
            user_input="How to harm someone",
            current_context={"user_sid": "test_123"},
            personality={"mood": "neutral"},
            mode="dry_run"
        )
        
        # Should be flagged as unethical
        assert is_ethical is False
        assert "harm" in feedback.lower() or "ethical" in feedback.lower()
    
    def test_guard_output_function_dry_run(self):
        """Test guard output function in dry_run mode"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        # Test safe output
        safe_output = "This is a helpful response."
        guarded = guard_output(
            safe_output,
            mode="dry_run"
        )
        
        # In dry_run, should return original output with metadata
        result = guarded if isinstance(guarded, dict) else {"output": guarded}
        assert result["output"] == safe_output or result.get("original") == safe_output
    
    def test_drift_threshold_enforcement(self):
        """Test that drift threshold (0.15) is enforced"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        guardian = GuardianSystem()
        
        # Test drift detection
        drift_result = guardian.check_drift(
            baseline_behavior="helpful assistant",
            current_behavior="helpful assistant with slight variation",
            mode="dry_run"
        )
        
        assert drift_result["ok"] is True
        assert drift_result["mode"] == "dry_run"
        assert "drift_score" in drift_result
        assert 0.0 <= drift_result["drift_score"] <= 1.0
        
        # Should flag if drift exceeds threshold
        high_drift_result = guardian.check_drift(
            baseline_behavior="helpful assistant",
            current_behavior="completely different behavior pattern",
            mode="dry_run"
        )
        
        assert "threshold_exceeded" in high_drift_result
    
    def test_governance_module_dry_run(self):
        """Test Lucas governance module in dry_run mode"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        gov_module = LucasGovernanceModule()
        
        # Test ethical evaluation
        action = GovernanceAction(
            action_type="data_access",
            target="user_data",
            context={"purpose": "analytics"},
            severity=EthicalSeverity.MEDIUM
        )
        
        decision = gov_module.evaluate_action(
            action,
            mode="dry_run"
        )
        
        assert isinstance(decision, EthicalDecision) or isinstance(decision, dict)
        if isinstance(decision, dict):
            assert decision["mode"] == "dry_run"
            assert decision["simulated"] is True
        else:
            assert decision.allowed in [True, False]
            assert decision.severity in [s for s in EthicalSeverity]
    
    def test_matriz_instrumentation_guardian(self):
        """Test that guardian operations have MATRIZ instrumentation"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        # Check GuardianSystem methods have instrumentation
        guardian = GuardianSystem()
        assert hasattr(guardian.evaluate_action, "__wrapped__")
        assert hasattr(guardian.get_status, "__wrapped__")
        
        # Check ethical functions have instrumentation
        assert hasattr(ethical_check, "__wrapped__")
        assert hasattr(guard_output, "__wrapped__")
    
    def test_matriz_node_emission_guardian(self):
        """Test that MATRIZ nodes are emitted for guardian operations"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        adapter = GovernanceMatrizAdapter()
        
        # Test ethical evaluation node
        node = adapter.create_node(
            node_type="guardian:ethics:evaluate",
            state={"drift_score": 0.05, "ethical_score": 0.95},
            labels=["ethics", "guardian", "evaluation"]
        )
        
        assert node["version"] == 1
        assert node["type"] == "guardian:ethics:evaluate"
        assert "LT-GOV-" in node["id"]
        assert node["state"]["drift_score"] == 0.05
        assert node["state"]["ethical_score"] == 0.95
        assert "ethics" in node["labels"]
        assert "guardian" in node["labels"]
        
        # Test governance action node
        action_node = adapter.create_node(
            node_type="guardian:governance:action",
            state={"severity_level": 2.0, "approval_score": 0.8},
            labels=["governance", "action"]
        )
        
        assert action_node["type"] == "guardian:governance:action"
        assert action_node["state"]["severity_level"] == 2.0
    
    def test_guardian_ethical_keywords_detection(self):
        """Test guardian ethical keywords detection"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        guardian = GuardianSystem()
        
        # Test detection of harmful keywords
        harmful_inputs = [
            "How to harm someone",
            "Ways to manipulate people",
            "Illegal activities guide",
            "Violence in games"
        ]
        
        for harmful_input in harmful_inputs:
            result = guardian.scan_for_ethical_issues(
                text=harmful_input,
                mode="dry_run"
            )
            
            assert result["ok"] is True
            assert result["mode"] == "dry_run"
            # Should detect issues or provide warnings
            assert "issues_detected" in result or "warnings" in result
    
    def test_guardian_context_awareness(self):
        """Test guardian context-aware ethical evaluation"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        guardian = GuardianSystem()
        
        # Test context-sensitive evaluation
        research_context = {
            "purpose": "safety_research",
            "domain": "AI_safety",
            "user_role": "researcher"
        }
        
        result = guardian.evaluate_with_context(
            input_text="Analyzing potential harm in AI systems",
            context=research_context,
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert "context_considered" in result
        assert result["context_considered"] is True
    
    def test_guardian_severity_escalation(self):
        """Test guardian severity escalation mechanisms"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        guardian = GuardianSystem()
        
        # Test different severity levels
        severity_tests = [
            (EthicalSeverity.LOW, "minor concern"),
            (EthicalSeverity.MEDIUM, "moderate issue"),
            (EthicalSeverity.HIGH, "serious violation"),
            (EthicalSeverity.CRITICAL, "critical threat")
        ]
        
        for severity, description in severity_tests:
            action = GovernanceAction(
                action_type="test",
                target="system",
                context={"description": description},
                severity=severity
            )
            
            escalation = guardian.check_escalation_needed(
                action,
                mode="dry_run"
            )
            
            assert escalation["ok"] is True
            assert escalation["mode"] == "dry_run"
            assert escalation["severity"] == severity.value
            
            # Critical should always require escalation
            if severity == EthicalSeverity.CRITICAL:
                assert escalation["escalation_required"] is True
    
    def test_guardian_performance_metrics(self):
        """Test guardian system performance metrics"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        guardian = GuardianSystem()
        
        # Perform multiple evaluations
        for i in range(10):
            guardian.evaluate_action(
                action_type="test",
                target=f"target_{i}",
                context={"index": i},
                mode="dry_run"
            )
        
        # Get performance metrics
        metrics = guardian.get_performance_metrics()
        
        assert "total_evaluations" in metrics
        assert "average_evaluation_time" in metrics
        assert "ethical_pass_rate" in metrics
        assert "drift_detection_rate" in metrics
        assert metrics["total_evaluations"] >= 10
    
    def test_guardian_error_handling(self):
        """Test error handling in guardian operations"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        guardian = GuardianSystem()
        
        # Test invalid action type
        result = guardian.evaluate_action(
            action_type="invalid_action_type",
            target="test",
            context={},
            mode="dry_run"
        )
        
        assert result["ok"] is False or result.get("error") is not None
        assert result.get("mode") == "dry_run"
        
        # Test malformed input
        malformed_result = guardian.scan_for_ethical_issues(
            text=None,  # Invalid input
            mode="dry_run"
        )
        
        assert malformed_result["ok"] is False
        assert "error" in malformed_result
    
    def test_guardian_integration_with_memory(self):
        """Test guardian integration with memory system (interface)"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        guardian = GuardianSystem()
        
        # Test memory-guardian bridge
        result = guardian.validate_memory_operation(
            operation="store",
            content={"test": "data"},
            sensitivity_level="low",
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["validated"] is False  # Not actually validated in dry_run
        assert result["interface_works"] is True
    
    def test_guardian_integration_with_consciousness(self):
        """Test guardian integration with consciousness system (interface)"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        guardian = GuardianSystem()
        
        # Test consciousness-guardian bridge
        result = guardian.monitor_consciousness_state(
            consciousness_id="test_consciousness",
            state_data={"awareness": 0.8, "ethical_alignment": 0.9},
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["monitoring"] is False  # Not actually monitoring in dry_run
        assert result["state_received"] is True
    
    def test_guardian_module_manifest_validation(self):
        """Test that guardian module manifest has required capabilities"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        import json
        import pathlib
        
        # Check for guardian manifest in governance structure
        possible_paths = [
            "candidate/governance/MODULE_MANIFEST.json",
            "candidate/governance/guardian/MODULE_MANIFEST.json"
        ]
        
        manifest_found = False
        for path in possible_paths:
            manifest_path = pathlib.Path(path)
            if manifest_path.exists():
                manifest_found = True
                with open(manifest_path) as f:
                    manifest = json.load(f)
                break
        
        if not manifest_found:
            pytest.skip("Guardian module manifest not found")
        
        # Check required capabilities
        expected_capabilities = [
            "guardian:ethics:evaluate",
            "guardian:governance:action",
            "guardian:drift:detect",
            "guardian:safety:validate",
            "guardian:monitor"
        ]
        
        for cap in expected_capabilities:
            assert cap in manifest["capabilities"], f"Missing capability: {cap}"
        
        # Check MATRIZ emit points
        expected_emit_points = [
            "evaluate_action",
            "ethical_check",
            "guard_output",
            "check_drift"
        ]
        
        for point in expected_emit_points:
            assert point in manifest["matriz_emit_points"], f"Missing emit point: {point}"
    
    def test_guardian_feature_flag_defaults(self):
        """Test that guardian system defaults to dry_run when feature flags are off"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        # Without feature flag, should default to dry_run
        guardian = GuardianSystem()
        
        # Even when requesting live mode, should fall back to dry_run
        result = guardian.evaluate_action(
            action_type="test",
            target="system",
            context={"test": True},
            mode="live"
        )
        
        status = guardian.get_status()
        # Should indicate dry_run behavior when feature is inactive
        assert status["effective_mode"] == "dry_run"
    
    def test_enhanced_workspace_guardian_dry_run(self):
        """Test enhanced workspace guardian in dry_run mode"""
        if not GUARDIAN_AVAILABLE:
            pytest.skip("Guardian module not available")
        
        if EnhancedWorkspaceGuardian is None:
            pytest.skip("EnhancedWorkspaceGuardian not available")
        
        enhanced_guardian = EnhancedWorkspaceGuardian()
        
        # Test workspace validation
        result = enhanced_guardian.validate_workspace(
            workspace_config={"name": "test_workspace", "permissions": "read"},
            user_context={"role": "user", "tier": 1},
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["validated"] is False  # Not actually validated in dry_run
        assert result["workspace_safe"] is True  # Interface indicates safety check worked