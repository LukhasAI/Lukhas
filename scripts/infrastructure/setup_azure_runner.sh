#!/bin/bash
#
# This script automates the setup of a GitHub self-hosted runner environment
# on a fresh Ubuntu 22.04 LTS installation.
#
# It installs Docker, Python 3.11, and make.
# For a complete guide, including security hardening, refer to:
# docs/infrastructure/azure_runner_setup.md

set -euo pipefail

echo "--- Starting Azure Runner Setup ---"

# 1. Update package lists and install essential tools
echo "[1/4] Updating packages and installing make..."
sudo apt-get update
sudo apt-get install -y make

# 2. Install Docker
echo "[2/4] Installing Docker..."
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add the current user to the 'docker' group to run docker commands without sudo
sudo usermod -aG docker $USER
echo "Docker installed. You may need to start a new shell for the group changes to take effect."

# 3. Install Python 3.11
# Ubuntu 22.04 ships with Python 3.10. We use the deadsnakes PPA for Python 3.11.
echo "[3/4] Installing Python 3.11..."
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-pip

# 4. Security hardening reminder
echo "[4/4] Security Hardening Reminder"
echo "Base software installation is complete."
echo "IMPORTANT: Remember to apply security hardening measures as described in the documentation:"
echo "- Configure Network Security Group (NSG) firewall rules."
echo "- Set up automatic system updates."
echo "- Follow the principle of least privilege for the runner user."

echo "--- Azure Runner Setup Complete ---"
