#!/bin/bash

# Resume Creator Full-Stack Runner
# This script properly navigates to the docker directory and runs the application

set -e

echo "🚀 Starting Resume Creator Full-Stack Application..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "📁 Project root: $PROJECT_ROOT"

# Check if .env file exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "⚠️  .env file not found. Please copy env.example to .env and fill in your credentials."
    exit 1
fi

# Navigate to docker directory
DOCKER_DIR="$PROJECT_ROOT/docker"
if [ ! -d "$DOCKER_DIR" ]; then
    echo "❌ Docker directory not found at $DOCKER_DIR"
    exit 1
fi

echo "📦 Navigating to docker directory: $DOCKER_DIR"
cd "$DOCKER_DIR"

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker compose down 2>/dev/null || true

# Build and start services
echo "🔨 Building and starting services..."
docker compose up --build

echo "✅ Resume Creator is now running!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs" 