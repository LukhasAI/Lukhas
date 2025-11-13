#!/bin/bash
# Quick Claude API setup script

echo ""
echo "🔐 Claude API Quick Setup"
echo "=========================================="
echo ""

# Check if key is in keychain
KEYCHAIN_KEY=$(security find-generic-password -s "LUKHASAI.ANTHROPIC_API_KEY" -w 2>/dev/null)

if [ -n "$KEYCHAIN_KEY" ]; then
    echo "✅ Found existing key in keychain: ${KEYCHAIN_KEY:0:20}..."
    echo ""
    echo "⚠️  Key returned 401 (invalid/revoked)"
    echo ""
fi

echo "📋 Steps to update API key:"
echo ""
echo "1. Visit: https://console.anthropic.com/settings/keys"
echo "   (Login with your Anthropic account)"
echo ""
echo "2. Click 'Create Key' button"
echo ""
echo "3. Copy the new key (starts with sk-ant-...)"
echo ""
echo "4. Run the update script:"
echo "   python3 scripts/update_keychain_key.py"
echo ""
echo "5. Test the connection:"
echo "   python3 scripts/test_claude_simple.py"
echo ""
echo "=========================================="
echo ""

read -p "Do you want to open Anthropic console now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    open "https://console.anthropic.com/settings/keys"
    echo ""
    echo "✅ Opening browser..."
    echo ""
fi

read -p "Do you have your new API key ready? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    python3 scripts/update_keychain_key.py
else
    echo ""
    echo "No problem! Run this when ready:"
    echo "  python3 scripts/update_keychain_key.py"
    echo ""
fi
