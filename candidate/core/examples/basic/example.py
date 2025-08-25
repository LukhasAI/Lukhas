"""
LUKHAS Core - Basic GLYPH Example
=================================

This script demonstrates the basic creation, serialization,
and deserialization of a GLYPHToken.
"""

# Ensure the script can find the 'candidate' directory
import sys
import os

# Add the root directory to the Python path
# This is a common pattern for running examples within a larger project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

try:
    from candidate.core.common.glyph import create_glyph, parse_glyph, GLYPHSymbol, validate_glyph
except ImportError:
    print("Error: Could not import GLYPH utilities.")
    print("Please ensure you are running this script from the root of the repository,")
    print("or that the 'candidate' directory is in your Python path.")
    sys.exit(1)


def main():
    """
    Demonstrates basic GLYPH token functionality.
    """
    print("--- LUKHAS Core: Basic GLYPH Token Example ---")

    # 1. Create a simple GLYPH token
    print("\n1. Creating a GLYPH token...")
    glyph_token = create_glyph(
        symbol=GLYPHSymbol.CONNECT,
        source="example_script",
        target="core.consciousness",
        payload={"message": "Hello, LUKHAS!"},
        priority="high",
        author="Jules"
    )
    print(f"   - Created token: {glyph_token.glyph_id}")
    print(f"   - Symbol: {glyph_token.symbol.value}")
    print(f"   - Source: {glyph_token.source}")
    print(f"   - Target: {glyph_token.target}")
    print(f"   - Payload: {glyph_token.payload}")

    # 2. Validate the token
    print("\n2. Validating the created token...")
    try:
        is_valid = validate_glyph(glyph_token)
        if is_valid:
            print("   - Token is valid.")
    except Exception as e:
        print(f"   - Token validation failed: {e}")

    # 3. Serialize the token to a JSON string
    print("\n3. Serializing token to JSON...")
    json_token = glyph_token.to_json()
    print(f"   - JSON representation:\n{json_token}")

    # 4. Deserialize the JSON string back into a GLYPH token
    print("\n4. Deserializing token from JSON...")
    parsed_token = parse_glyph(json_token)
    print(f"   - Parsed token ID: {parsed_token.glyph_id}")
    print(f"   - Parsed token symbol: {parsed_token.symbol}")

    # 5. Verify that the original and parsed tokens are the same
    print("\n5. Verifying data integrity...")
    if glyph_token.to_dict() == parsed_token.to_dict():
        print("   - Success: Original and parsed tokens match.")
    else:
        print("   - Error: Tokens do not match.")

    print("\n--- Example Complete ---")


if __name__ == "__main__":
    main()
