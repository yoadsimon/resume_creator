#!/bin/bash

# Fast Docker Build Script for Resume Creator
# This script enables BuildKit and other optimizations for fastest possible builds

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Enable Docker BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

print_status "🚀 Starting optimized Docker build process..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found!"
    if [ -f "env.example" ]; then
        print_status "Creating .env file from env.example..."
        cp env.example .env
        print_warning "Please edit .env file with your OpenAI credentials before running the container"
    else
        print_error "env.example file not found. Please create .env file manually."
        exit 1
    fi
fi

# Clean up old containers and images (optional - comment out if you want to keep cache)
# print_status "🧹 Cleaning up old containers..."
# docker compose down --remove-orphans 2>/dev/null || true

# Build with BuildKit optimizations
print_status "🔨 Building with Docker BuildKit optimizations..."
time docker compose build \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --parallel \
    --progress=plain

# Start the container
print_status "🚀 Starting the container..."
docker compose up -d

# Wait for health check
print_status "⏳ Waiting for health check..."
sleep 10

# Check if container is healthy
if docker compose ps | grep -q "healthy"; then
    print_success "✅ Container is running and healthy!"
    print_success "🌐 API is available at: http://localhost:8000"
    print_success "📚 Documentation at: http://localhost:8000/docs"
    print_success "❤️  Health check at: http://localhost:8000/health"
else
    print_warning "⚠️  Container started but health check may still be running..."
    print_status "📝 Check logs with: docker compose logs -f"
fi

print_status "🎉 Build and deployment completed!"
echo ""
echo "📋 Quick commands:"
echo "  - View logs:     docker compose logs -f"
echo "  - Stop:          docker compose down"
echo "  - Restart:       docker compose restart"
echo "  - Shell access:  docker compose exec resume-creator bash" 