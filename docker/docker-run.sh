#!/bin/bash

# Resume Creator Docker Runner Script
# This script helps you build and run the Resume Creator API in Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found!"
        print_status "Creating .env file from env.example..."
        
        if [ -f "env.example" ]; then
            cp env.example .env
            print_warning "Please edit .env file with your OpenAI credentials before proceeding."
            print_status "Required variables: OPEN_AI_ORGANIZATION_ID, OPEN_AI_PROJECT_ID, OPEN_AI_TOKEN"
            read -p "Press Enter after you've updated .env file..."
        else
            print_error "env.example file not found. Please create .env file manually."
            exit 1
        fi
    fi
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    docker build -t resume-creator .
    print_success "Docker image built successfully!"
}

# Function to run with docker-compose
run_compose() {
    print_status "Starting Resume Creator with docker-compose..."
    docker-compose up -d
    print_success "Resume Creator is running!"
    print_status "API available at: http://localhost:8000"
    print_status "API docs available at: http://localhost:8000/docs"
}

# Function to run standalone container
run_standalone() {
    print_status "Starting Resume Creator container..."
    
    # Load environment variables
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    docker run -d \
        --name resume-creator-app \
        -p 8000:8000 \
        -e OPEN_AI_ORGANIZATION_ID="${OPEN_AI_ORGANIZATION_ID}" \
        -e OPEN_AI_PROJECT_ID="${OPEN_AI_PROJECT_ID}" \
        -e OPEN_AI_TOKEN="${OPEN_AI_TOKEN}" \
        -v "$(pwd)/temp:/app/temp" \
        -v "$(pwd)/result:/app/result" \
        resume-creator
    
    print_success "Resume Creator is running!"
    print_status "API available at: http://localhost:8000"
    print_status "API docs available at: http://localhost:8000/docs"
}

# Function to stop containers
stop_containers() {
    print_status "Stopping Resume Creator containers..."
    
    # Stop docker-compose if running
    if docker-compose ps | grep -q "resume-creator"; then
        docker-compose down
    fi
    
    # Stop standalone container if running
    if docker ps | grep -q "resume-creator-app"; then
        docker stop resume-creator-app
        docker rm resume-creator-app
    fi
    
    print_success "All containers stopped!"
}

# Function to view logs
view_logs() {
    if docker-compose ps | grep -q "resume-creator"; then
        print_status "Showing docker-compose logs..."
        docker-compose logs -f resume-creator
    elif docker ps | grep -q "resume-creator-app"; then
        print_status "Showing container logs..."
        docker logs -f resume-creator-app
    else
        print_error "No Resume Creator containers are running!"
    fi
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    # Remove containers
    docker-compose down 2>/dev/null || true
    docker rm -f resume-creator-app 2>/dev/null || true
    
    # Remove image
    docker rmi resume-creator 2>/dev/null || true
    
    print_success "Cleanup completed!"
}

# Main script logic
case "${1:-help}" in
    "build")
        check_env_file
        build_image
        ;;
    "run")
        check_env_file
        build_image
        run_compose
        ;;
    "run-standalone")
        check_env_file
        build_image
        run_standalone
        ;;
    "stop")
        stop_containers
        ;;
    "logs")
        view_logs
        ;;
    "restart")
        stop_containers
        check_env_file
        build_image
        run_compose
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|*)
        echo "Resume Creator Docker Runner"
        echo ""
        echo "Usage: ./docker-run.sh [command]"
        echo ""
        echo "Commands:"
        echo "  build            Build the Docker image"
        echo "  run              Build and run with docker-compose (recommended)"
        echo "  run-standalone   Build and run standalone container"
        echo "  stop             Stop all running containers"
        echo "  logs             View container logs"
        echo "  restart          Stop, rebuild, and start containers"
        echo "  cleanup          Remove all containers and images"
        echo "  help             Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./docker-run.sh run     # Start the application"
        echo "  ./docker-run.sh logs    # View logs"
        echo "  ./docker-run.sh stop    # Stop the application"
        ;;
esac 