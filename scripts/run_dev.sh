#!/bin/bash

# Resume Creator Development Runner
# This script runs the application in development mode with hot reload

set -e

echo "🛠️  Starting Resume Creator in Development Mode..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please copy env.example to .env and fill in your credentials."
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
if [ -z "$OPEN_AI_TOKEN" ]; then
    echo "❌ OPEN_AI_TOKEN is not set in .env file"
    exit 1
fi

echo "📦 Building and starting development services..."

# Navigate to docker directory and run development docker-compose
cd docker

# Build and start development services with hot reload
docker-compose -f docker-compose.dev.yml up --build

echo "✅ Resume Creator Development Environment is now running!"
echo "🌐 Frontend (with hot reload): http://localhost:3000"
echo "🔧 Backend API (with hot reload): http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs" 