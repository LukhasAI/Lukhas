"""
MATRIZ Node Contract v1.0.0 Validation Tests
T4-Approved: Contract compliance and validation tests

These tests ensure all MATRIZ nodes comply with the frozen v1.0.0 contract
and that the contract itself is properly validated.
"""
from uuid import uuid4
import pytest
from MATRIZ.node_contract import (
    CONTRACT_VERSION,
    GLYPH,
    MatrizMessage,
    MatrizNode,
    MatrizResult,
    Topic,
    validate_glyph,
    validate_message,
    validate_result,
)
from tests.util.mk_msg import mk_msg_from_json, mk_test_message

class DummyNode(MatrizNode):
    """Dummy node for contract testing"""
    name = 'dummy-test-node'
    version = CONTRACT_VERSION

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        return MatrizResult(
            ok=True,
            payload={
                'echo': msg.payload,
                'processed': True
            },
            trace={
                'handled_by': self.name,
                'topic': msg.topic
            },
            guardian_log=[
                f'dummy_processed_{msg.topic}'
            ]
        )

class FailingNode(MatrizNode):
    """Node that simulates failures for testing"""
    name = 'failing-test-node'
    version = CONTRACT_VERSION

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        return MatrizResult(ok=False, reasons=['Simulated failure for testing'], payload={}, trace={'error': 'simulated', 'handled_by': self.name}, guardian_log=[f'dummy_failed_{msg.topic}'])

@pytest.mark.contract
class TestGLYPHValidation:
    """Test GLYPH structure validation"""

    def test_valid_glyph(self):
        """Test that valid GLYPH passes validation"""
        glyph = GLYPH(id=uuid4(), kind='intent', version=CONTRACT_VERSION, tags={'priority': 'high'})
        assert validate_glyph(glyph)

    def test_invalid_glyph_id(self):
        """Test that invalid UUID fails validation"""
        glyph = GLYPH(id='not-a-uuid', kind='intent', version=CONTRACT_VERSION)
        assert not validate_glyph(glyph)

    def test_invalid_glyph_kind(self):
        """Test that empty kind fails validation"""
        glyph = GLYPH(id=uuid4(), kind='', version=CONTRACT_VERSION)
        assert not validate_glyph(glyph)

    def test_invalid_glyph_version(self):
        """Test that wrong version fails validation"""
        glyph = GLYPH(id=uuid4(), kind='intent', version='2.0.0')
        assert not validate_glyph(glyph)

@pytest.mark.contract
class TestMatrizMessageValidation:
    """Test MatrizMessage structure validation"""

    def test_valid_message(self):
        """Test that valid message passes validation"""
        msg = mk_test_message(topic=Topic.CONTRADICTION.value, lane='experimental', payload={'test': True})
        assert validate_message(msg)

    def test_invalid_message_lane(self):
        """Test that invalid lane fails validation"""
        msg_dict = {'lane': 'invalid-lane', 'topic': Topic.CONTRADICTION.value, 'glyph': {'id': str(uuid4()), 'kind': 'intent'}, 'payload': {'test': True}}
        msg = mk_msg_from_json(msg_dict)
        assert not validate_message(msg)

    def test_invalid_message_topic(self):
        """Test that empty topic fails validation"""
        msg = mk_test_message(topic='', lane='experimental')
        assert not validate_message(msg)

    def test_invalid_message_unknown_topic(self):
        """Test that unknown topic (not in ALLOWED_TOPICS) fails validation"""
        msg = mk_test_message(topic='test', lane='experimental')
        assert not validate_message(msg)

@pytest.mark.contract
class TestMatrizResultValidation:
    """Test MatrizResult structure validation"""

    def test_valid_result(self):
        """Test that valid result passes validation"""
        result = MatrizResult(ok=True, reasons=[], payload={'result': 'success'}, trace={'handled_by': 'test'}, guardian_log=['test_logged'])
        assert validate_result(result)

    def test_invalid_result_reasons(self):
        """Test that non-list reasons fails validation"""
        result = MatrizResult(ok=True, reasons='not-a-list', payload={}, trace={}, guardian_log=[])
        assert not validate_result(result)

    def test_invalid_result_empty_guardian_log(self):
        """Test that empty guardian_log fails validation (must contain at least one crumb)"""
        result = MatrizResult(ok=True, reasons=[], payload={}, trace={}, guardian_log=[])
        assert not validate_result(result)

    def test_invalid_result_non_json_payload(self):
        """Payload containing non-JSON-serializable values should fail validation"""
        result = MatrizResult(ok=True, reasons=[], payload={'bad': {1, 2, 3}}, trace={}, guardian_log=['crumb'])
        assert not validate_result(result)

@pytest.mark.contract
class TestNodeContractCompliance:
    """Test that nodes comply with the contract"""

    def test_dummy_node_contract_compliance(self):
        """Test that dummy node follows contract"""
        node = DummyNode()
        msg = mk_test_message(topic=Topic.TREND.value, payload={'input': 'data'})
        result = node.handle(msg)
        assert validate_result(result)
        assert result.ok
        assert 'handled_by' in result.trace
        assert result.trace['handled_by'] == 'dummy-test-node'
        assert len(result.guardian_log) > 0

    def test_failing_node_contract_compliance(self):
        """Test that failing node still follows contract"""
        node = FailingNode()
        msg = mk_test_message(topic=Topic.BREAKTHROUGH.value)
        result = node.handle(msg)
        assert validate_result(result)
        assert not result.ok
        assert len(result.reasons) > 0
        assert 'handled_by' in result.trace
        assert len(result.guardian_log) > 0

    def test_node_trace_requirements(self):
        """Test that nodes include required trace information"""
        node = DummyNode()
        msg = mk_test_message(topic='contradiction')
        result = node.handle(msg)
        assert 'handled_by' in result.trace
        assert 'topic' in result.trace
        assert result.trace['topic'] == 'contradiction'

    def test_node_guardian_logging(self):
        """Test that nodes include Guardian audit logs"""
        node = DummyNode()
        msg = mk_test_message(topic='resource')
        result = node.handle(msg)
        assert len(result.guardian_log) > 0
        assert any(('dummy_processed_resource' in log for log in result.guardian_log))

@pytest.mark.contract
class TestContractImmutability:
    """Test that contract enforces immutability where required"""

    def test_glyph_immutability(self):
        """Test that GLYPH is immutable"""
        glyph = GLYPH(id=uuid4(), kind='intent')
        with pytest.raises(AttributeError):
            glyph.kind = 'modified'

    def test_message_immutability(self):
        """Test that MatrizMessage is immutable"""
        msg = mk_test_message()
        with pytest.raises(AttributeError):
            msg.topic = 'modified'

    def test_result_mutability(self):
        """Test that MatrizResult allows updates (not frozen)"""
        result = MatrizResult(ok=True)
        result.payload['added'] = 'value'
        result.trace['updated'] = True
        assert result.payload['added'] == 'value'
        assert result.trace['updated'] is True

@pytest.mark.contract
def test_contract_golden_example():
    """Golden test with example from T4 documentation"""
    msg = mk_msg_from_json({'lane': 'experimental', 'topic': 'contradiction', 'glyph': {'id': '550e8400-e29b-41d4-a716-446655440000', 'kind': 'intent', 'tags': {'priority': 'high'}}, 'payload': {'parameter_A': 'value1', 'parameter_B': 'value2', 'target_improve': 0.8}})
    node = DummyNode()
    result = node.handle(msg)
    assert validate_message(msg)
    assert validate_result(result)
    assert result.ok
    assert result.payload['echo']['parameter_A'] == 'value1'
    assert 'handled_by' in result.trace
    assert len(result.guardian_log) > 0

@pytest.mark.contract
def test_abstract_node_implementation_required():
    """Test that abstract MatrizNode requires implementation"""
    node = MatrizNode()
    msg = mk_test_message()
    with pytest.raises(NotImplementedError):
        node.handle(msg)
if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'contract'])