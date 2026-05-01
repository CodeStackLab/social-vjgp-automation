#!/bin/bash
# -----------------------------------------------------------------------------
# Docker & Dependencies Installer for Social Automation VPS
# -----------------------------------------------------------------------------
set -e

echo "🚀 Starting System Update..."
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release git unzip

# Add Docker's official GPG key:
echo "🔑 Adding Docker GPG Key..."
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo "📦 Adding Docker Repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker:
echo "🐳 Installing Docker & Compose Plugin..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Check status
echo "✅ Checking Versions:"
sudo docker --version
sudo docker compose version

# Add current user to docker group (optional but recommended)
echo "👤 Adding User to Docker group..."
sudo usermod -aG docker $USER

echo "🎉 Docker Setup Complete! Please log out and back in for group changes to take effect."
