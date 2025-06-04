#!/bin/bash

# Resume Creator Full-Stack Runner
# This script builds and runs both frontend and backend using Docker Compose

set -e

echo "🚀 Starting Resume Creator Full-Stack Application..."

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

echo "📦 Building and starting services..."

# Navigate to docker directory and run docker-compose
cd docker

# Build and start services
docker-compose up --build

echo "✅ Resume Creator is now running!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs" 