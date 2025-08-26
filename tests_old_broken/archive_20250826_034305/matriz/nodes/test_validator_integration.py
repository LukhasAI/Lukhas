#!/usr/bin/env python3
"""
Integration Test for ValidatorNode with MathNode and FactNode

This script demonstrates how the ValidatorNode can validate outputs
from other cognitive nodes in the MATRIZ-AGI system.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nodes.validator_node import ValidatorNode
from nodes.math_node import MathNode
from nodes.fact_node import FactNode


def test_math_validation():
    """Test ValidatorNode with MathNode outputs"""
    print("=" * 60)
    print("Testing ValidatorNode with MathNode")
    print("=" * 60)
    
    math_node = MathNode()
    validator_node = ValidatorNode()
    
    test_expressions = [
        "2 + 3",
        "10 * 5", 
        "100 / 4",
        "2 ** 3",
        "((2 + 3) * 4) / 5"
    ]
    
    for expr in test_expressions:
        print(f"\nExpression: {expr}")
        print("-" * 40)
        
        # Get math node output
        math_output = math_node.process({'expression': expr})
        print(f"Math Result: {math_output['answer']}")
        print(f"Math Confidence: {math_output['confidence']:.3f}")
        
        # Validate the math output
        validation_output = validator_node.process({
            'target_output': math_output,
            'validation_type': 'mathematical'
        })
        
        print(f"Validation: {validation_output['answer']}")
        print(f"Validation Confidence: {validation_output['confidence']:.3f}")
        
        # Check if both nodes are valid
        math_valid = math_node.validate_output(math_output)
        validation_valid = validator_node.validate_output(validation_output)
        
        print(f"Math Output Valid: {math_valid}")
        print(f"Validation Output Valid: {validation_valid}")
        
        if validation_output['answer'].startswith("Validation PASSED"):
            print("✓ PASS")
        else:
            print("✗ FAIL")


def test_fact_validation():
    """Test ValidatorNode with FactNode outputs"""
    print("\n" + "=" * 60)
    print("Testing ValidatorNode with FactNode")
    print("=" * 60)
    
    fact_node = FactNode()
    validator_node = ValidatorNode()
    
    test_questions = [
        "What is the capital of France?",
        "What is the capital of Japan?",
        "What is the speed of light?",
        "How many planets are in our solar system?",
        "What is the meaning of life?"  # This should return "I don't know"
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        print("-" * 40)
        
        # Get fact node output
        fact_output = fact_node.process({'question': question})
        print(f"Fact Result: {fact_output['answer']}")
        print(f"Fact Confidence: {fact_output['confidence']:.3f}")
        
        # Validate the fact output
        validation_output = validator_node.process({
            'target_output': fact_output,
            'validation_type': 'factual'
        })
        
        print(f"Validation: {validation_output['answer']}")
        print(f"Validation Confidence: {validation_output['confidence']:.3f}")
        
        # Check if both nodes are valid
        fact_valid = fact_node.validate_output(fact_output)
        validation_valid = validator_node.validate_output(validation_output)
        
        print(f"Fact Output Valid: {fact_valid}")
        print(f"Validation Output Valid: {validation_valid}")
        
        if validation_output['answer'].startswith("Validation PASSED"):
            print("✓ PASS")
        else:
            print("✗ FAIL")


def test_comprehensive_validation():
    """Test comprehensive validation of complex outputs"""
    print("\n" + "=" * 60)
    print("Testing Comprehensive Validation")
    print("=" * 60)
    
    math_node = MathNode()
    fact_node = FactNode()
    validator_node = ValidatorNode()
    
    # Test with mathematical output
    print("\n1. Mathematical Output Validation:")
    math_output = math_node.process({'expression': 'pi * 2'})
    validation_result = validator_node.process({
        'target_output': math_output,
        'validation_type': 'comprehensive'
    })
    
    print(f"Math Answer: {math_output['answer']}")
    print(f"Validation Result: {validation_result['answer']}")
    
    # Show validation strategies used
    validation_node = validation_result['matriz_node']
    strategies = validation_node['state'].get('validation_strategies_used', [])
    print(f"Validation Strategies Used: {strategies}")
    
    # Test with factual output
    print("\n2. Factual Output Validation:")
    fact_output = fact_node.process({'question': 'What is the capital of Italy?'})
    validation_result = validator_node.process({
        'target_output': fact_output,
        'validation_type': 'comprehensive'
    })
    
    print(f"Fact Answer: {fact_output['answer']}")
    print(f"Validation Result: {validation_result['answer']}")
    
    # Show validation strategies used
    validation_node = validation_result['matriz_node']
    strategies = validation_node['state'].get('validation_strategies_used', [])
    print(f"Validation Strategies Used: {strategies}")


if __name__ == "__main__":
    print("MATRIZ ValidatorNode Integration Test")
    print("Testing validation of MathNode and FactNode outputs")
    
    try:
        test_math_validation()
        test_fact_validation()
        test_comprehensive_validation()
        
        print("\n" + "=" * 60)
        print("Integration Test Complete!")
        print("ValidatorNode successfully validated outputs from MathNode and FactNode")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nIntegration test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()