#!/bin/bash

# 🔄 Update Git Remote URL Script
# Run this after renaming GitHub repository from Lukhas_PWM to Lukhas

echo "🚀 LUKHAS Git Remote Update"
echo "⚛️ Updating remote URL to match new repository name..."

# Update the remote URL
git remote set-url origin https://github.com/LukhasAI/Lukhas.git

# Verify the change
echo -e "\n✅ Updated remote URLs:"
git remote -v

# Test connectivity
echo -e "\n🧠 Testing connectivity to new repository..."
if git ls-remote origin main >/dev/null 2>&1; then
    echo "✅ Successfully connected to https://github.com/LukhasAI/Lukhas.git"
    echo "🛡️ Repository URL update complete!"
else
    echo "❌ Cannot connect to new URL. Repository may not be renamed yet."
    echo "💡 Please rename the GitHub repository first, then run this script."
fi

echo -e "\n🎊 LUKHAS Git configuration updated for consciousness-aware development!"
