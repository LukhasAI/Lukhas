#!/usr/bin/env python3
"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony

🔧 Simple lukhas iPhone & API Troubleshooter
==========================================
"""

import os
import socket
from pathlib import Path

import requests


def test_openai_api():
    """Test OpenAI API directly"""
    print("\n🤖 Testing OpenAI API...")
    print("=" * 40)

    # Load environment
    env_file = Path("/Users/A_G_I/CodexGPT_Lukhas/.env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not found or not configured")
        print("💡 Please set OPENAI_API_KEY in your .env file")
        return False

    print(f"🔑 API Key found: {api_key[:20]}...{api_key[-10:]}")

    # Test API call
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "gpt-4o-mini",  # Use cheaper model for testing
            "messages": [{"role": "user", "content": "Say 'OpenAI API working!'"}],
            "max_tokens": 10,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10,
        )

        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]["content"]
            print(f"✅ OpenAI API working! Response: {message}")
            return True
        else:
            print(f"❌ OpenAI API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error testing OpenAI: {e}")
        return False
    except Exception as e:
        print(f"❌ OpenAI test error: {e}")
        return False


def check_network():
    """Check network configuration"""
    print("\n🌐 Checking Network...")
    print("=" * 40)

    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        print(f"📍 Local IP: {local_ip}")

        # Check if it matches configured IP
        if local_ip == "192.168.2.41":
            print("✅ IP matches mobile interface configuration")
        else:
            print("⚠️ IP mismatch! Your mobile interface expects 192.168.2.41")
            print(f"💡 Update mobile interface to use: {local_ip}")

        return local_ip

    except Exception as e:
        print(f"❌ Network check failed: {e}")
        return None


def check_ports():
    """Check server ports"""
    print("\n🚪 Checking Server Ports...")
    print("=" * 40)

    ports = {
        8443: "HTTPS",
        8766: "Secure WebSocket",
        8767: "Fallback WebSocket",
    }

    for port, service in ports.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", port))
            sock.close()

            if result == 0:
                print(f"✅ Port {port} ({service}): Server running")
            else:
                print(f"⚠️ Port {port} ({service}): No server")

        except Exception as e:
            print(f"❌ Port {port}: Error - {e}")


def create_fixed_mobile_interface():
    """Create a mobile interface with automatic IP detection"""
    print("\n📱 Creating Fixed Mobile Interface...")
    print("=" * 40)

    # Get current IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        current_ip = s.getsockname()[0]
        s.close()
    except BaseException:
        current_ip = "192.168.2.41"  # fallback

    # Read the existing interface
    interface_path = (
        "/Users/A_G_I/CodexGPT_Lukhas/lukhas/sensors/mobile_interface_pro.html"
    )
    if not os.path.exists(interface_path):
        print(f"❌ Mobile interface not found: {interface_path}")
        return None

    with open(interface_path) as f:
        content = f.read()

    # Update IP addresses
    updated_content = content.replace("192.168.2.41", current_ip)

    # Save fixed version
    fixed_path = "/Users/A_G_I/CodexGPT_Lukhas/mobile_interface_fixed.html"
    with open(fixed_path, "w") as f:
        f.write(updated_content)

    print(f"✅ Fixed mobile interface created: {fixed_path}")
    print(f"📱 Updated IP to: {current_ip}")

    return fixed_path


def create_iphone_setup_instructions():
    """Create simple iPhone setup instructions"""
    print("\n📋 Creating iPhone Setup Instructions...")
    print("=" * 40)

    # Get current IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        current_ip = s.getsockname()[0]
        s.close()
    except BaseException:
        current_ip = "192.168.2.41"

    instructions = f"""
📱 IPHONE SETUP INSTRUCTIONS
==========================

🚨 CRITICAL: Both iPhone and MacBook MUST be on the same WiFi network!

STEP 1: Accept SSL Certificate
1. Open Safari on iPhone
2. Go to: https://{current_ip}:8443
3. Tap "Advanced" → "Proceed to {current_ip} (unsafe)"
4. Accept the security certificate

STEP 2: Access LiDAR Interface
1. Go to: https://{current_ip}:8443/mobile_interface_fixed.html
2. Tap "Enhanced Connect"
3. If that fails, tap "Connection Test"

STEP 3: Enable iOS WebSocket Features
1. Settings → Safari → Advanced → Experimental Features
2. Enable "NSURLSession WebSocket"
3. Restart Safari

TROUBLESHOOTING:
- Clear Safari cache: Settings → Safari → Clear History and Website Data
- Try different browsers: Chrome, Firefox
- Restart WiFi on iPhone
- Make sure MacBook firewall allows connections

SUCCESS INDICATORS:
✅ Green "Connected" status
✅ Server statistics showing data
✅ Ping tests working

If nothing works, the app has simulation mode that will work offline.

Current Network IP: {current_ip}
Mobile Interface: https://{current_ip}:8443/mobile_interface_fixed.html
"""

    instructions_path = "/Users/A_G_I/CodexGPT_Lukhas/iPhone_Setup_Instructions.txt"
    with open(instructions_path, "w") as f:
        f.write(instructions)

    print(f"✅ Instructions saved: {instructions_path}")
    return instructions_path


def main():
    """Main troubleshooting"""
    print("🔧 lukhas iPhone & API Quick Fix")
    print("=" * 50)

    # Test OpenAI
    openai_ok = test_openai_api()

    # Check network
    local_ip = check_network()

    # Check ports
    check_ports()

    # Create fixed interface
    create_fixed_mobile_interface()

    # Create instructions
    instructions = create_iphone_setup_instructions()

    # Summary
    print("\n📋 SUMMARY & NEXT STEPS")
    print("=" * 50)

    if openai_ok:
        print("✅ OpenAI API: Working")
    else:
        print("❌ OpenAI API: Fix your .env file with valid API key")

    if local_ip:
        print(f"✅ Network: IP detected as {local_ip}")
        if local_ip != "192.168.2.41":
            print("⚠️ Mobile interface updated with correct IP")
    else:
        print("❌ Network: Could not detect IP")

    print("\n📱 iPhone Setup:")
    print(f"   1. Read: {instructions}")
    print(
        f"   2. Use: https://{local_ip or '192.168.2.41'}:8443/mobile_interface_fixed.html"
    )
    print("   3. Accept SSL certificate first!")

    print("\n🚀 To start servers:")
    print("   cd /Users/A_G_I/CodexGPT_Lukhas")
    print("   python lukhas/sensors/enhanced_secure_server.py")


if __name__ == "__main__":
    main()

# Λ Systems 2025 www.ai
