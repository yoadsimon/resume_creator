#!/bin/bash
set -e

# Move to the docker directory
cd "$(dirname "$0")/docker"

# Stop and remove all containers for this project
if docker compose ps -q | grep -q .; then
  echo "Stopping running containers..."
  docker compose down --remove-orphans
fi

# Remove dangling images (optional, for a clean build)
echo "Pruning old images..."
docker image prune -f

echo "Building and starting containers..."
docker compose up --build 