#!/usr/bin/env python3
"""
OpenAI API Connection Test
Tests the OpenAI API key and connection before running stress tests
"""

import os
import sys

from dotenv import load_dotenv


def test_openai_connection():
    """Test OpenAI API connection"""
    print("🔑 Testing OpenAI API Connection...")

    # Load environment variables
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False

    print(f"✅ API Key found (length: {len(api_key)} characters)")

    try:
        import openai

        print("✅ OpenAI library imported successfully")

        # Initialize client
        client = openai.OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized")

        # Test with a simple completion
        print("🧪 Testing API connection with simple request...")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Say 'API test successful' if you can see this message.",
                },
            ],
            max_tokens=10,
            temperature=0,
        )

        result = response.choices[0].message.content.strip()
        print(f"✅ API Response: {result}")

        if "successful" in result.lower():
            print("🎉 OpenAI API connection test PASSED!")
            return True
        else:
            print("⚠️ API responded but unexpected content")
            return False

    except ImportError:
        print("❌ OpenAI library not installed. Run: pip install openai")
        return False
    except Exception as e:
        print(f"❌ API connection failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_openai_connection()
    sys.exit(0 if success else 1)
