#!/usr/bin/env bash

#docker build script

set -e

IMAGE_TAG=${1:-videogen:latest}

docker build -t "$IMAGE_TAG" .

echo "built $IMAGE_TAG"

