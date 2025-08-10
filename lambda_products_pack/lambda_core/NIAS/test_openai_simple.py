#!/usr/bin/env python3
"""
Simple test to verify OpenAI API connection
"""

import os
import sys
from pathlib import Path

# Try to load dotenv
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent.parent.parent / ".env"
    load_dotenv(env_path)
    print(f"✅ Loaded .env from: {env_path}")
except ImportError:
    print("⚠️ python-dotenv not installed")

# Check API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"✅ OpenAI API Key found: {api_key[:20]}...{api_key[-4:]}")
else:
    print("❌ No OpenAI API key found")
    sys.exit(1)

# Try to import and use OpenAI
try:
    from openai import OpenAI

    print("\n🔄 Testing OpenAI connection...")

    client = OpenAI(api_key=api_key)

    # Simple test - just check if we can create a completion
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use cheaper model for testing
            messages=[
                {"role": "system", "content": "You are a poetic dream weaver."},
                {
                    "role": "user",
                    "content": "Write a single sentence about winter dreams.",
                },
            ],
            max_tokens=50,
            temperature=0.7,
        )

        result = response.choices[0].message.content
        print("\n✅ OpenAI API Working!")
        print(f"📝 Test response: '{result}'")

    except Exception as e:
        print(f"\n❌ OpenAI API Error: {e}")
        if "api_key" in str(e).lower():
            print("   The API key might be invalid or expired")
        elif "rate_limit" in str(e).lower():
            print("   Rate limit exceeded")
        else:
            print(f"   Error details: {e}")

except ImportError:
    print("\n❌ OpenAI library not installed")
    print("   Install with: pip install openai")

print("\n" + "=" * 60)
print("📊 Summary:")
print("=" * 60)
print(f"• Environment file: {'✅ Found' if os.path.exists('.env') else '❌ Not found'}")
print(f"• API Key in env: {'✅ Yes' if api_key else '❌ No'}")
print(
    f"• OpenAI library: {'✅ Installed' if 'openai' in sys.modules else '⚠️ Check needed'}"
)
