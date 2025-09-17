#!/bin/bash

echo "Building videogen Docker image..."
docker build -t videogen:latest .

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo ""
    echo "To run the container:"
    echo "  docker run --gpus all -p 8000:8000 videogen:latest"
    echo ""
    echo "Or use docker-compose:"
    echo "  docker-compose up"
else
    echo "Build failed!"
    exit 1
fi
