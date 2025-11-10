#!/bin/bash
set -eo pipefail

# This script builds a container image and runs the build process inside it.
# This allows for a reproducible build environment that matches CI.

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$( cd -- "${SCRIPT_DIR}/.." &> /dev/null && pwd )
DOCKERFILE_PATH="${PROJECT_ROOT}/.github/docker/Dockerfile"
IMAGE_NAME="lukhas-build-hermetic:latest"
CONTAINER_NAME="lukhas-temp-builder"

echo "Building container image with current source code..."
# We build the image from the project root context
docker build -t "${IMAGE_NAME}" -f "${DOCKERFILE_PATH}" "${PROJECT_ROOT}"

echo "Running build and extracting artifacts..."
# Ensure the dist directory is clean before we copy new artifacts
rm -rf "${PROJECT_ROOT}/dist"

# Run the build in a new container. The container will stop after the build command completes.
# We remove any previous container with the same name to ensure a clean run.
docker rm -f "${CONTAINER_NAME}" &>/dev/null || true
docker run --name "${CONTAINER_NAME}" "${IMAGE_NAME}"

# Copy the build artifacts from the stopped container to the host's dist/ directory
docker cp "${CONTAINER_NAME}:/home/builder/dist" "${PROJECT_ROOT}/"

# Clean up the container
docker rm -v "${CONTAINER_NAME}"

echo "Build complete. Artifacts are in the '${PROJECT_ROOT}/dist' directory."
ls -l "${PROJECT_ROOT}/dist"
