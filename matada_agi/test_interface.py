#!/usr/bin/env python3
"""
Test script for the MATADA CognitiveNode interface.

This script demonstrates the complete functionality of the interface
and validates that all components work correctly together.
"""

import json
import sys
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from matada_agi.core import CognitiveNode, NodeState, NodeLink, CognitiveOrchestrator
from matada_agi.core.example_node import MathReasoningNode


def test_node_state():
    """Test NodeState creation and validation"""
    print("Testing NodeState...")
    
    # Basic state
    state = NodeState(confidence=0.8, salience=0.9)
    assert state.confidence == 0.8
    assert state.salience == 0.9
    assert state.valence is None
    
    # Full state with optional fields
    full_state = NodeState(
        confidence=0.9,
        salience=0.8,
        valence=0.5,
        arousal=0.7,
        novelty=0.6,
        urgency=0.3,
        risk=0.2,
        utility=0.8
    )
    assert full_state.valence == 0.5
    assert full_state.arousal == 0.7
    
    print("✓ NodeState tests passed")


def test_node_link():
    """Test NodeLink creation"""
    print("Testing NodeLink...")
    
    link = NodeLink(
        target_node_id="node-123",
        link_type="causal",
        direction="unidirectional",
        weight=0.8,
        explanation="This caused that"
    )
    
    assert link.target_node_id == "node-123"
    assert link.link_type == "causal"
    assert link.weight == 0.8
    
    print("✓ NodeLink tests passed")


def test_math_node():
    """Test the MathReasoningNode implementation"""
    print("Testing MathReasoningNode...")
    
    node = MathReasoningNode()
    
    # Test successful math
    result = node.process({'query': 'What is 15 * 3?'})
    assert result['confidence'] > 0.9
    assert '45' in result['answer']
    assert node.validate_output(result)
    
    # Test the MATADA node structure
    matada_node = result['matada_node']
    assert matada_node['type'] == 'DECISION'
    assert 'confidence' in matada_node['state']
    assert 'salience' in matada_node['state']
    assert matada_node['state']['result'] == 45.0
    
    # Test non-math query
    result2 = node.process({'query': 'Hello, how are you?'})
    assert result2['confidence'] < 0.2
    assert node.validate_output(result2)
    
    # Test error case
    result3 = node.process({'query': 'What is 1/0?'})
    assert result3['confidence'] < 0.5
    assert 'error' in result3['matada_node']['state']
    
    print("✓ MathReasoningNode tests passed")


def test_matada_node_creation():
    """Test MATADA node creation and validation"""
    print("Testing MATADA node creation...")
    
    node = MathReasoningNode()
    
    # Create a simple MATADA node
    state = NodeState(confidence=0.8, salience=0.9, valence=0.5)
    matada_node = node.create_matada_node(
        node_type="EMOTION",
        state=state,
        additional_data={'mood': 'happy'}
    )
    
    # Validate structure
    assert matada_node['version'] == 1
    assert matada_node['type'] == 'EMOTION'
    assert matada_node['state']['confidence'] == 0.8
    assert matada_node['state']['salience'] == 0.9
    assert matada_node['state']['valence'] == 0.5
    assert matada_node['state']['mood'] == 'happy'
    assert 'id' in matada_node
    assert 'timestamps' in matada_node
    assert 'provenance' in matada_node
    
    # Validate using the validation method
    assert node.validate_matada_node(matada_node)
    
    print("✓ MATADA node creation tests passed")


def test_deterministic_hashing():
    """Test deterministic hash generation"""
    print("Testing deterministic hashing...")
    
    node = MathReasoningNode()
    
    input1 = {'query': 'What is 2+2?', 'context': 'test'}
    input2 = {'context': 'test', 'query': 'What is 2+2?'}  # Different order
    
    hash1 = node.get_deterministic_hash(input1)
    hash2 = node.get_deterministic_hash(input2)
    
    # Should be the same despite different key order
    assert hash1 == hash2
    
    # Different input should produce different hash
    input3 = {'query': 'What is 3+3?', 'context': 'test'}
    hash3 = node.get_deterministic_hash(input3)
    assert hash1 != hash3
    
    print("✓ Deterministic hashing tests passed")


def test_orchestrator_integration():
    """Test integration with the CognitiveOrchestrator"""
    print("Testing orchestrator integration...")
    
    # Create orchestrator and register our math node
    orchestrator = CognitiveOrchestrator()
    math_node = MathReasoningNode()
    
    orchestrator.register_node('math', math_node)
    
    # Process a mathematical query
    result = orchestrator.process_query('What is 5 + 7?')
    
    assert 'answer' in result
    assert 'matada_nodes' in result
    assert 'trace' in result
    assert 'reasoning_chain' in result
    
    # Should have multiple MATADA nodes in the graph
    matada_nodes = result['matada_nodes']
    assert len(matada_nodes) >= 2  # At least INTENT and DECISION nodes
    
    # Check node types
    node_types = [node['type'] for node in matada_nodes]
    assert 'INTENT' in node_types
    assert 'DECISION' in node_types
    
    print("✓ Orchestrator integration tests passed")


def demonstrate_full_workflow():
    """Demonstrate a complete MATADA workflow"""
    print("\n" + "="*50)
    print("MATADA COGNITIVE NODE INTERFACE DEMONSTRATION")
    print("="*50)
    
    # Create and configure system
    orchestrator = CognitiveOrchestrator()
    math_node = MathReasoningNode()
    orchestrator.register_node('math', math_node)
    
    # Process a query
    query = "What is (15 + 5) * 2?"
    print(f"\nUser Query: {query}")
    
    result = orchestrator.process_query(query)
    
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result.get('confidence', 'N/A')}")
    
    # Show the reasoning chain
    print("\nReasoning Chain:")
    for step in result['reasoning_chain']:
        print(f"  → {step}")
    
    # Show MATADA nodes created
    print(f"\nMATADA Nodes Created: {len(result['matada_nodes'])}")
    for i, node in enumerate(result['matada_nodes'], 1):
        print(f"  {i}. {node['type']} (ID: {node['id'][:8]}...)")
        print(f"     Confidence: {node['state']['confidence']:.2f}, "
              f"Salience: {node['state']['salience']:.2f}")
        if node['reflections']:
            print(f"     Reflection: {node['reflections'][0]['reflection_type']}")
    
    # Show traceability
    print(f"\nFull Trace Available: {len(orchestrator.execution_trace)} executions")
    
    # Demonstrate causal chain reconstruction
    if result['matada_nodes']:
        last_node_id = result['matada_nodes'][-1]['id']
        causal_chain = orchestrator.get_causal_chain(last_node_id)
        print(f"Causal Chain Length: {len(causal_chain)} nodes")
    
    print("\n✓ Full workflow demonstration completed successfully!")


if __name__ == "__main__":
    try:
        # Run all tests
        test_node_state()
        test_node_link()
        test_math_node()
        test_matada_node_creation()
        test_deterministic_hashing()
        test_orchestrator_integration()
        
        print("\n🎉 All tests passed!")
        
        # Run the demonstration
        demonstrate_full_workflow()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)