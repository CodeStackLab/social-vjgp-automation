#!/bin/bash
# -----------------------------------------------------------------------------
# Social Automation Platform - VPS Master Setup
# -----------------------------------------------------------------------------
set -e

echo "🌟 Welcome to the Social Automation Dashboard Setup!"
echo "----------------------------------------------------"

# 1. Install Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 Docker not found. Installing..."
    chmod +x install_docker.sh
    ./install_docker.sh
else
    echo "✅ Docker already installed."
fi

# 2. Prepare Folders
echo "📂 Preparing Data Directories..."
mkdir -p data generated_media/permanent/videos generated_media/permanent/images generated_media/permanent/pdfs assets certbot/conf certbot/www

# 3. Check for Credentials
echo "🔑 Checking for Required Credentials..."
if [ ! -f .env ]; then
    echo "⚠️  WARNING: .env file NOT FOUND!"
    echo "Please create a .env file with your API keys (refer to .env.example)"
else
    echo "✅ .env found."
fi

if [ ! -f google_credentials.json ]; then
    echo "⚠️  WARNING: google_credentials.json NOT FOUND!"
    echo "Please upload your Google Cloud credentials to this folder."
else
    echo "✅ google_credentials.json found."
fi

# 4. Configure Nginx for First Run (Non-SSL)
echo "🌐 Configuring Nginx..."
if [ ! -f nginx/conf.d/app.conf ]; then
    mkdir -p nginx/conf.d
    # Start with standard config, we will swap to production_app.conf after SSL is issued
    cp nginx/app.conf nginx/conf.d/app.conf
    echo "✅ Nginx initial config prepared."
fi

# 5. Launch Containers
echo "🚀 Launching Social Automation Platform..."
docker compose build
docker compose up -d

echo "----------------------------------------------------"
echo "🎉 Setup Complete!"
echo "Current Container Status:"
docker compose ps

echo ""
echo "👉 NEXT STEPS:"
echo "1. Verify you can access the dashboard at your IP (over http)."
echo "2. Once your domain is pointed, run Certbot to enable HTTPS."
echo "3. Update nginx/conf.d/app.conf with nginx/production_app.conf for SSL."
