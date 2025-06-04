#!/usr/bin/env bash

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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if required files exist using relative paths
RESUME_FILE="$PROJECT_ROOT/data/inputs/resume.docx"
ACCOMPLISHMENTS_FILE="$PROJECT_ROOT/data/inputs/short_accomplishments.txt"

if [ ! -f "$RESUME_FILE" ]; then
    print_error "Resume file not found at: $RESUME_FILE"
    exit 1
fi

if [ ! -f "$ACCOMPLISHMENTS_FILE" ]; then
    print_error "Accomplishments file not found at: $ACCOMPLISHMENTS_FILE"
    exit 1
fi

# Stop any running containers
print_status "Stopping any running containers..."
docker compose -f "$PROJECT_ROOT/docker/docker-compose.yml" down

# Start the server using docker compose
print_status "Starting Resume Creator server..."
cd "$PROJECT_ROOT/docker" && docker compose up -d

# Wait for the server to be ready
print_status "Waiting for server to be ready..."
sleep 10

# Check if server is healthy
HEALTH_CHECK=$(curl -s http://localhost:8000/health)
if [[ $HEALTH_CHECK != *"healthy"* ]]; then
    print_error "Server health check failed"
    docker compose logs
    docker compose down
    exit 1
fi

print_success "Server is ready!"

# Prepare the API call
print_status "Sending resume generation request..."

# Create a temporary directory for the response
TEMP_DIR=$(mktemp -d)
RESPONSE_FILE="$TEMP_DIR/resume.docx"

# Send the API request
curl -X POST "http://localhost:8000/generate_resume" \
    -H "accept: application/json" \
    -H "Content-Type: multipart/form-data" \
    -F "resume_file=@$RESUME_FILE" \
    -F "accomplishments_file=@$ACCOMPLISHMENTS_FILE" \
    -F "job_description_link=https://www.linkedin.com/jobs/search/?currentJobId=4213163545&f_C=200394&geoId=92000000&origin=COMPANY_PAGE_JOBS_CLUSTER_EXPANSION&originToLandingJobPostings=4213163545%2C4228689541%2C4228678141%2C4228680559%2C4177222532%2C4223564902%2C4163532442%2C4213536536&trk=d_flagship3_company" \
    -F "company_base_link=https://linnovate.net/" \
    -F "use_o1_model=false" \
    --output "$RESPONSE_FILE"

# Check if the request was successful
if [ -f "$RESPONSE_FILE" ] && [ -s "$RESPONSE_FILE" ]; then
    print_success "Resume generated successfully!"
    print_status "Resume saved to: $RESPONSE_FILE"
    
    # Create result directory if it doesn't exist
    mkdir -p "$PROJECT_ROOT/data/result"
    
    # Copy the generated resume to the result directory
    cp "$RESPONSE_FILE" "$PROJECT_ROOT/data/result/test_resume.docx"
    print_status "Copied resume to: $PROJECT_ROOT/data/result/test_resume.docx"
else
    print_error "Failed to generate resume"
    docker compose logs
fi

# Cleanup
print_status "Cleaning up..."
rm -rf "$TEMP_DIR"
docker compose -f "$PROJECT_ROOT/docker/docker-compose.yml" down

print_status "Test completed!" 