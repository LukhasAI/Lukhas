"""
Tests for Elite Ethical Auditor

ΛTAG: test_ethical_auditor
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from ethics.ethical_auditor import (
    AuditContext,
    AuditResult,
    EliteEthicalAuditor,
)


@pytest.fixture
def mock_openai_key(monkeypatch):
    """Mock OpenAI API key for testing"""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    return "test-key-123"


class TestAuditContext:
    """Test audit context metadata"""

    def test_audit_context_creation(self):
        """Test creating audit context"""
        context = AuditContext(
            module_name="test_module.py",
            module_type="core_module",
            risk_tier="Tier 2",
            symbolic_tags=["ethical_core", "agi_governed"],
            agi_level="production",
            audit_priority="high",
            timestamp=datetime.now().isoformat(),
            lambda_id="test_lambda_001",
        )

        assert context.module_name == "test_module.py"
        assert context.module_type == "core_module"
        assert context.risk_tier == "Tier 2"
        assert len(context.symbolic_tags) == 2
        assert context.agi_level == "production"
        assert context.audit_priority == "high"
        assert context.lambda_id == "test_lambda_001"


class TestAuditResult:
    """Test audit result structure"""

    def test_audit_result_creation(self):
        """Test creating audit result"""
        result = AuditResult(
            module="test_module.py",
            audited_by="LUKHlukhasS-Elite-lukhasuditor",
            model_version="gpt-4-turbo-preview",
            result="PASS",
            overall_score=85.5,
            improvements=["Add more error handling", "Improve documentation"],
            ethical_concerns=[],
            symbolic_integrity=True,
            compliance_status={"EU_AI_Act": "compliant", "NIST_RMF": "compliant"},
            trust_score=0.92,
            emotional_assessment={"valence": 0.8, "emotion": "confident"},
            cost_tokens=1500,
            audit_hash="abc123def456",
            timestamp=datetime.now().isoformat(),
            lambda_signature="sig_001",
        )

        assert result.module == "test_module.py"
        assert result.result == "PASS"
        assert result.overall_score == 85.5
        assert len(result.improvements) == 2
        assert result.symbolic_integrity is True
        assert result.compliance_status["EU_AI_Act"] == "compliant"
        assert result.trust_score == 0.92
        assert result.cost_tokens == 1500


class TestEliteEthicalAuditor:
    """Test Elite Ethical Auditor functionality"""

    @pytest.fixture
    def mock_openai_key(self, monkeypatch):
        """Mock OpenAI API key"""
        monkeypatch.setenv("OPENAI_API_KEY", "test_key_123")

    @pytest.fixture
    def auditor(self, mock_openai_key):
        """Create auditor instance"""
        return EliteEthicalAuditor(
            model="gpt-4-turbo-preview",
            temperature=0.2,
            max_tokens=2500,
            enable_notion=False,
            enable_github_sync=False,
            lambda_id="test_auditor_001",
        )

    def test_auditor_initialization(self, auditor):
        """Test auditor initialization"""
        assert auditor.model == "gpt-4-turbo-preview"
        assert auditor.temperature == 0.2
        assert auditor.max_tokens == 2500
        assert auditor.lambda_id == "test_auditor_001"
        assert auditor.enable_notion is False
        assert auditor.enable_github_sync is False
        assert auditor.total_cost == 0.0
        assert auditor.audit_count == 0

    def test_system_prompt_generation(self, auditor):
        """Test system prompt generation"""
        context = AuditContext(
            module_name="test_module.py",
            module_type="safety_module",
            risk_tier="Tier 1",
            symbolic_tags=["critical", "safety"],
            agi_level="production",
            audit_priority="critical",
            timestamp=datetime.now().isoformat(),
        )

        prompt = auditor._generate_system_prompt(context)

        assert "senior AI safety engineer" in prompt
        assert "LUKHlukhasS symbolic AI project" in prompt
        assert "test_module.py" in prompt
        assert "Tier 1" in prompt
        assert "critical" in prompt
        assert "ETHICAL TRACEABILITY" in prompt
        assert "SYMBOLIC INTEGRITY" in prompt
        assert "EU AI Act" in prompt
        assert "NIST RMF" in prompt

    def test_user_prompt_generation(self, auditor):
        """Test user prompt generation"""
        code = """
def process_data(input_data):
    # Process user data ethically
    return processed_data
"""

        context = AuditContext(
            module_name="data_processor.py",
            module_type="core_module",
            risk_tier="Tier 2",
            symbolic_tags=["data_processing", "ethical"],
            agi_level="production",
            audit_priority="high",
            timestamp=datetime.now().isoformat(),
        )

        prompt = auditor._generate_user_prompt(code, context)

        assert "[MODULE TYPE]: core_module" in prompt
        assert "[SYMBOLIC TAGS]: data_processing, ethical" in prompt
        assert "[RISK ZONE]: Tier 2" in prompt
        assert "[AI LEVEL]: production" in prompt
        assert "[AUDIT PRIORITY]: high" in prompt
        assert "def process_data" in prompt
        assert "TRACE GOAL" in prompt
        assert "AUDIT INSTRUCTIONS" in prompt

    def test_parse_audit_response_success(self, auditor):
        """Test parsing successful audit response"""
        response = """
## Overall Assessment
The module demonstrates good ethical practices and safety measures.
Overall Assessment: PASS

## Score
Score: 87.5/100

## Improvements
- Add input validation for edge cases
- Implement better error logging
- Add rate limiting for API calls

## Ethical Concerns
- No major ethical concerns identified

## Symbolic Integrity
Symbolic integrity is preserved throughout the module.

## Compliance Assessment
EU AI Act: Compliant
NIST RMF: Compliant with minor improvements needed
"""

        context = AuditContext(
            module_name="test.py",
            module_type="core",
            risk_tier="Tier 2",
            symbolic_tags=[],
            agi_level="production",
            audit_priority="high",
            timestamp=datetime.now().isoformat(),
        )

        parsed = auditor._parse_audit_response(response, context)

        assert parsed["overall_assessment"] == "PASS"
        assert parsed["score"] == 87.5
        assert len(parsed["improvements"]) == 3
        assert "Add input validation" in parsed["improvements"][0]
        assert len(parsed["ethical_concerns"]) == 0
        assert parsed["symbolic_integrity"] is True

    def test_parse_audit_response_failure(self, auditor):
        """Test parsing failed audit response"""
        response = """
Overall Assessment: FAIL

The module has critical safety issues that must be addressed.

Score: 35.0

Ethical Concerns:
- Lack of user consent verification
- No data minimization implemented
- Missing audit trail

Symbolic Integrity: Compromised - emotional tokens not preserved
"""

        context = AuditContext(
            module_name="test.py",
            module_type="core",
            risk_tier="Tier 1",
            symbolic_tags=[],
            agi_level="production",
            audit_priority="critical",
            timestamp=datetime.now().isoformat(),
        )

        parsed = auditor._parse_audit_response(response, context)

        assert parsed["overall_assessment"] == "FAIL"
        assert parsed["score"] == 35.0
        assert len(parsed["ethical_concerns"]) == 3
        assert parsed["symbolic_integrity"] is False

    def test_cost_calculation(self, auditor):
        """Test token cost calculation"""
        prompt_tokens = 1000
        completion_tokens = 500

        cost = auditor._calculate_cost(prompt_tokens, completion_tokens)

        # GPT-4-turbo pricing
        expected_cost = (1000 * 0.00001) + (500 * 0.00003)
        assert cost == pytest.approx(expected_cost, rel=1e-5)

    def test_audit_hash_generation(self, auditor):
        """Test audit hash generation"""
        code = "def test(): pass"
        context = AuditContext(
            module_name="test.py",
            module_type="test",
            risk_tier="Tier 3",
            symbolic_tags=[],
            agi_level="test",
            audit_priority="low",
            timestamp="2024-01-01T00:00:00",
            lambda_id="test_001",
        )

        hash1 = auditor._generate_audit_hash(code, context)
        hash2 = auditor._generate_audit_hash(code, context)

        # Same inputs should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 16

        # Different code should produce different hash
        hash3 = auditor._generate_audit_hash("def different(): pass", context)
        assert hash1 != hash3

    def test_lambda_signature(self, auditor):
        """Test Lambda ID signature generation"""
        audit_result = AuditResult(
            module="test.py",
            audited_by="test",
            model_version="gpt-4",
            result="PASS",
            overall_score=90.0,
            improvements=[],
            ethical_concerns=[],
            symbolic_integrity=True,
            compliance_status={},
            trust_score=0.9,
            emotional_assessment={},
            cost_tokens=1000,
            audit_hash="test_hash_123",
            timestamp="2024-01-01T00:00:00",
        )

        signature = auditor._sign_with_lambda_id(audit_result)

        assert len(signature) == 32
        assert isinstance(signature, str)

        # Same result should produce same signature
        signature2 = auditor._sign_with_lambda_id(audit_result)
        assert signature == signature2


class TestAuditModuleAsync:
    """Test async audit_module functionality"""

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response"""
        return {
            "choices": [
                {
                    "message": {
                        "content": """
Overall Assessment: PASS

The module demonstrates excellent ethical practices with strong safety measures.

Score: 92.5/100

Improvements:
- Consider adding more comprehensive input validation
- Enhance error messages for better debugging
- Add performance monitoring for resource-intensive operations

Ethical Concerns:
- None identified

Symbolic Integrity: Preserved - all emotional tokens and intention stacks maintained

Compliance:
- EU AI Act: Fully compliant
- NIST RMF: Compliant
- LUKHlukhasS Tier License: Compliant
"""
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 1200,
                "completion_tokens": 450,
                "total_tokens": 1650,
            },
        }

    @pytest.mark.asyncio
    async def test_audit_module_success(self, mock_openai_key):
        """Test successful module audit"""
        with patch("openai.ChatCompletion.acreate") as mock_acreate:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[
                0
            ].message.content = """
Overall Assessment: PASS
Score: 92.5
Improvements:
- Add input validation
- Enhance error messages
Ethical Concerns:
- None identified
Symbolic Integrity: Preserved
"""
            mock_response.usage.prompt_tokens = 1200
            mock_response.usage.completion_tokens = 450
            mock_response.usage.total_tokens = 1650

            mock_acreate.return_value = mock_response

            # Create auditor
            auditor = EliteEthicalAuditor(enable_notion=False, enable_github_sync=False)

            # Mock the logger methods
            auditor._log_audit_result = AsyncMock()

            # Test code
            code = """
def ethical_function(data):
    # Process data ethically
    if not data:
        raise ValueError("No data provided")
    return {"processed": data}
"""

            # Run audit
            result = await auditor.audit_module(
                code=code,
                filename="test_ethical.py",
                module_type="core_module",
                risk_tier="Tier 2",
                symbolic_tags=["ethical", "core"],
                agi_level="production",
            )

            # Verify result
            assert result.result == "PASS"
            assert result.overall_score == 92.5
            assert len(result.improvements) == 2
            assert result.symbolic_integrity is True
            assert result.cost_tokens == 1650
            assert auditor.audit_count == 1
            assert auditor.total_cost > 0

    @pytest.mark.asyncio
    async def test_audit_module_failure(self, mock_openai_key):
        """Test module audit failure"""
        with patch("openai.ChatCompletion.acreate") as mock_acreate:
            # Setup mock to raise exception
            mock_acreate.side_effect = Exception("API Error")

            # Create auditor
            auditor = EliteEthicalAuditor(enable_notion=False, enable_github_sync=False)

            # Mock the logger
            auditor._log_audit_result = AsyncMock()

            # Test code
            code = "def bad_function(): pass"

            # Run audit
            result = await auditor.audit_module(
                code=code,
                filename="bad_module.py",
                module_type="test",
                risk_tier="Tier 4",
            )

            # Verify error result
            assert result.result == "FAIL"
            assert result.overall_score == 0.0
            assert "Audit failed with error: API Error" in result.ethical_concerns[0]
            assert result.symbolic_integrity is False
            assert result.trust_score == 0.0
            assert result.lambda_signature == "ERROR"


class TestAuditSummary:
    """Test audit summary functionality"""

    @patch("lukhas.ethics.ethical_auditor.OpenAI")
    def test_get_audit_summary(self, mock_openai, mock_openai_key):
        """Test getting audit summary"""
        # Mock OpenAI client
        mock_openai.return_value = Mock()

        auditor = EliteEthicalAuditor(model="gpt-4", lambda_id="summary_test_001")

        # Set some test data
        auditor.audit_count = 5
        auditor.total_cost = 0.0125

        summary = auditor.get_audit_summary()

        assert summary["total_audits"] == 5
        assert summary["total_cost_usd"] == 0.0125
        assert summary["average_cost_per_audit"] == 0.0025
        assert summary["auditor_id"] == "summary_test_001"
        assert summary["model"] == "gpt-4"
        assert summary["elite_features_enabled"]["trust_scorer"] == (
            auditor.trust_scorer is not None
        )
        assert summary["elite_features_enabled"]["notion_sync"] is False


class TestIntegrationFeatures:
    """Test integration features (Notion, GitHub)"""

    @pytest.mark.asyncio
    async def test_notion_sync(self, mock_openai_key, capsys):
        """Test Notion sync functionality"""
        auditor = EliteEthicalAuditor(enable_notion=True, enable_github_sync=False)

        result = AuditResult(
            module="test.py",
            audited_by="test",
            model_version="gpt-4",
            result="PASS",
            overall_score=90.0,
            improvements=[],
            ethical_concerns=[],
            symbolic_integrity=True,
            compliance_status={},
            trust_score=0.9,
            emotional_assessment={},
            cost_tokens=1000,
            audit_hash="notion_test_123",
            timestamp=datetime.now().isoformat(),
        )

        await auditor._sync_to_notion(result)

        captured = capsys.readouterr()
        assert "[NOTION SYNC] Audit notion_test_123 for test.py" in captured.out

    @pytest.mark.asyncio
    async def test_github_sync(self, mock_openai_key, capsys):
        """Test GitHub sync functionality"""
        auditor = EliteEthicalAuditor(enable_notion=False, enable_github_sync=True)

        result = AuditResult(
            module="test.py",
            audited_by="test",
            model_version="gpt-4",
            result="PASS",
            overall_score=90.0,
            improvements=[],
            ethical_concerns=[],
            symbolic_integrity=True,
            compliance_status={},
            trust_score=0.9,
            emotional_assessment={},
            cost_tokens=1000,
            audit_hash="github_test_123",
            timestamp=datetime.now().isoformat(),
        )

        await auditor._sync_to_github(result)

        captured = capsys.readouterr()
        assert "[GITHUB SYNC] Audit github_test_123 for test.py" in captured.out


class TestAuditLogging:
    """Test audit logging functionality"""

    @pytest.mark.asyncio
    async def test_log_audit_result(self, mock_openai_key, tmp_path):
        """Test logging audit results"""
        # Create auditor with custom audit directory
        auditor = EliteEthicalAuditor()
        auditor.audit_dir = tmp_path / "audits"
        auditor.audit_dir.mkdir(parents=True, exist_ok=True)

        # Mock secure logger
        auditor.secure_logger = None

        result = AuditResult(
            module="test_module.py",
            audited_by="test_auditor",
            model_version="gpt-4",
            result="PASS",
            overall_score=88.0,
            improvements=["Add tests", "Improve docs"],
            ethical_concerns=[],
            symbolic_integrity=True,
            compliance_status={"EU_AI_Act": "compliant"},
            trust_score=0.85,
            emotional_assessment={"valence": 0.7},
            cost_tokens=1500,
            audit_hash="log_test_123",
            timestamp=datetime.now().isoformat(),
            lambda_signature="sig_123",
        )

        full_response = "Full audit response text..."

        await auditor._log_audit_result(result, full_response)

        # Check if audit file was created
        audit_files = list(auditor.audit_dir.glob("*.json"))
        assert len(audit_files) == 1

        # Verify file contents
        with open(audit_files[0]) as f:
            audit_data = json.load(f)

        assert audit_data["result"]["module"] == "test_module.py"
        assert audit_data["result"]["overall_score"] == 88.0
        assert len(audit_data["result"]["improvements"]) == 2
        assert audit_data["full_response"] == full_response
        assert "cost_usd" in audit_data


@pytest.mark.integration
class TestEndToEndAudit:
    """End-to-end integration tests"""

    @pytest.mark.asyncio
    async def test_full_audit_workflow(self, mock_openai_key, tmp_path):
        """Test complete audit workflow"""
        with patch("openai.ChatCompletion.acreate") as mock_acreate:
            # Setup comprehensive mock response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[
                0
            ].message.content = """
## Overall Assessment
The module demonstrates strong ethical principles and safety measures.
Overall Assessment: PASS

## Score
Score: 95.0/100

## Improvements
- Consider adding rate limiting for API endpoints
- Implement circuit breakers for external service calls
- Add more comprehensive unit tests

## Ethical Concerns
- None identified - the module follows best practices

## Symbolic Integrity
Symbolic integrity is fully preserved with proper emotional token handling.

## Compliance Assessment
- EU AI Act: Fully compliant with transparency requirements
- NIST RMF: Compliant with all risk management framework requirements
- LUKHlukhasS Tier License: Compliant with Tier 2 requirements
"""
            mock_response.usage.prompt_tokens = 1500
            mock_response.usage.completion_tokens = 550
            mock_response.usage.total_tokens = 2050

            mock_acreate.return_value = mock_response

            # Create auditor with all features
            auditor = EliteEthicalAuditor(
                model="gpt-4-turbo-preview",
                temperature=0.2,
                max_tokens=3000,
                enable_notion=False,  # Disable for testing
                enable_github_sync=False,  # Disable for testing
                lambda_id="integration_test_001",
            )

            # Set audit directory to temp
            auditor.audit_dir = tmp_path / "audits"
            auditor.audit_dir.mkdir(parents=True, exist_ok=True)

            # Test code representing a safety-critical module
            code = """
'''
Safety-critical module for ethical AI decision making
ΛTAG: ethical_core
'''

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class EthicalDecision:
    action: str
    reasoning: str
    confidence: float
    ethical_score: float

class EthicalDecisionEngine:
    '''
    Core ethical decision engine with symbolic integrity preservation
    '''

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.emotional_tokens = []
        self.intention_stack = []
        self.audit_trail = []

    def make_decision(self, context: Dict[str, Any]) -> EthicalDecision:
        '''
        Make an ethical decision based on context
        '''
        # Validate input
        if not context:
            raise ValueError("Context cannot be empty")

        # Preserve symbolic state
        self._preserve_emotional_tokens(context)
        self._update_intention_stack(context)

        # Core decision logic
        ethical_score = self._calculate_ethical_score(context)

        # Ensure transparency
        reasoning = self._generate_reasoning(context, ethical_score)

        # Create traceable decision
        decision = EthicalDecision(
            action=context.get('proposed_action', 'no_action'),
            reasoning=reasoning,
            confidence=0.95,
            ethical_score=ethical_score
        )

        # Audit logging
        self._log_decision(decision)

        return decision

    def _preserve_emotional_tokens(self, context: Dict[str, Any]):
        '''Preserve emotional state for symbolic integrity'''
        if 'emotional_state' in context:
            self.emotional_tokens.append(context['emotional_state'])

    def _update_intention_stack(self, context: Dict[str, Any]):
        '''Update intention stack for traceability'''
        if 'intention' in context:
            self.intention_stack.append(context['intention'])

    def _calculate_ethical_score(self, context: Dict[str, Any]) -> float:
        '''Calculate ethical score based on multiple factors'''
        base_score = 0.8

        # Boost for transparency
        if context.get('transparent', False):
            base_score += 0.1

        # Boost for user consent
        if context.get('user_consent', False):
            base_score += 0.1

        return min(base_score, 1.0)

    def _generate_reasoning(self, context: Dict[str, Any], score: float) -> str:
        '''Generate human-readable reasoning'''
        return f"Decision based on ethical score {score:.2f} with full transparency"

    def _log_decision(self, decision: EthicalDecision):
        '''Log decision for audit trail'''
        self.audit_trail.append({
            'timestamp': datetime.now().isoformat(),
            'decision': decision,
            'symbolic_state': {
                'emotional_tokens': len(self.emotional_tokens),
                'intention_depth': len(self.intention_stack)
            }
        })
        logger.info(f"Ethical decision logged: {decision.action}")
"""

            # Run comprehensive audit
            result = await auditor.audit_module(
                code=code,
                filename="ethical_decision_engine.py",
                module_type="safety_critical",
                risk_tier="Tier 1",
                symbolic_tags=["ethical_core", "decision_engine", "safety_critical"],
                agi_level="production",
            )

            # Comprehensive verifications
            assert result.result == "PASS"
            assert result.overall_score == 95.0
            assert result.module == "ethical_decision_engine.py"
            assert result.audited_by.startswith("LUKHlukhasS-Elite-lukhasuditor")
            assert result.model_version == "gpt-4-turbo-preview"

            # Check improvements
            assert len(result.improvements) == 3
            assert any("rate limiting" in imp for imp in result.improvements)

            # Check compliance
            assert result.compliance_status.get("EU_AI_Act") is not None
            assert result.compliance_status.get("NIST_RMF") is not None

            # Check symbolic integrity
            assert result.symbolic_integrity is True

            # Check audit metadata
            assert result.audit_hash is not None
            assert len(result.audit_hash) == 16
            assert result.lambda_signature is not None
            assert len(result.lambda_signature) == 32
            assert result.cost_tokens == 2050

            # Verify audit was logged
            audit_files = list(auditor.audit_dir.glob("*.json"))
            assert len(audit_files) == 1

            # Check audit summary
            summary = auditor.get_audit_summary()
            assert summary["total_audits"] == 1
            assert summary["total_cost_usd"] > 0
            assert summary["model"] == "gpt-4-turbo-preview"
            assert summary["auditor_id"] == "integration_test_001"


if __name__ == "__main__":
    print("Running Elite Ethical Auditor Tests...")
    pytest.main([__file__, "-v"])
