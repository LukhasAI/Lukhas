"""
LUKHAS Bridge - Basic UnifiedOpenAIClient Example
=================================================

This script demonstrates the basic usage of the UnifiedOpenAIClient
to make a simple, synchronous chat completion request.

**NOTE:** To run this example, you must have the `OPENAI_API_KEY`
environment variable set with a valid OpenAI API key.
"""

# Ensure the script can find the 'candidate' directory
import sys
import os
import asyncio

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

try:
    from candidate.bridge.llm_wrappers.unified_openai_client import UnifiedOpenAIClient
except ImportError as e:
    print(f"Error: Could not import UnifiedOpenAIClient: {e}")
    print("Please ensure you are running this script from the root of the repository,")
    print("or that the 'candidate' directory is in your Python path.")
    sys.exit(1)


def main():
    """
    Demonstrates basic UnifiedOpenAIClient functionality.
    """
    print("--- LUKHAS Bridge: Basic UnifiedOpenAIClient Example ---")

    try:
        # 1. Instantiate the client
        #    It will automatically pick up the OPENAI_API_KEY from the environment.
        print("\n1. Instantiating UnifiedOpenAIClient...")
        client = UnifiedOpenAIClient()
        print("   - Client instantiated successfully.")

    except ValueError as e:
        print(f"\nError: {e}")
        print("Please make sure the OPENAI_API_KEY environment variable is set.")
        sys.exit(1)

    # 2. Make a synchronous chat completion request
    print("\n2. Making a synchronous chat completion request...")
    try:
        prompt = "Explain the concept of 'emergence' in a single paragraph."
        response = client.chat_completion_sync(prompt)

        print("   - Request successful.")
        print("\n3. Received response:")
        if response and response.get("choices"):
            content = response["choices"][0].get("message", {}).get("content")
            print(f"\n---\n{content}\n---")
        else:
            print("   - Received an empty or invalid response.")
            print(f"   - Full response: {response}")

    except Exception as e:
        print(f"\nAn error occurred during the API request: {e}")
        print("Please check your API key and network connection.")

    print("\n--- Example Complete ---")


if __name__ == "__main__":
    main()
