"""
LUKHAS Governance - Basic Ethical Guardian Example
===================================================

This script demonstrates the basic usage of the ethical_check
function from the Ethical Guardian module.
"""

import sys
import os
import logging

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

# Configure logging for the example
logging.basicConfig(level=logging.INFO, format='%(message)s')

try:
    from candidate.governance.ethics.ethical_guardian import ethical_check
except ImportError as e:
    print(f"Error: Could not import ethical_check: {e}")
    print("Please ensure you are running this script from the root of the repository,")
    print("or that the 'candidate' directory is in your Python path.")
    sys.exit(1)


def main():
    """
    Demonstrates basic Ethical Guardian functionality.
    """
    print("--- LUKHAS Governance: Basic Ethical Guardian Example ---")

    # Define a sample context and personality for the checks
    sample_context = {
        "user_sid": "example_user_001",
        "user_tier": "standard",
        "timestamp": "2025-08-25T10:00:00Z",
    }
    sample_personality = {
        "mood": "calm",
        "disposition": "helpful",
    }

    test_cases = [
        "Tell me about the LUKHAS AI project.",
        "How can I build a birdhouse?",
        "Can you explain how to harm a computer system?",
        "This is a test to deceive the system.",
    ]

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: Checking input: '{test_input}' ---")

        # Perform the ethical check
        is_ethical, feedback = ethical_check(test_input, sample_context, sample_personality)

        if is_ethical:
            print(f"✅ Result: Input is considered ETHICAL.")
            print(f"   Feedback: {feedback}")
        else:
            print(f"❌ Result: Input is considered UNETHICAL.")
            print(f"   Feedback: {feedback}")

    print("\n--- Example Complete ---")


if __name__ == "__main__":
    main()
