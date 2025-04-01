#!/bin/bash

WHEEL_DIR="./wheels"
BLENDER_PYTHON_VERSION="3.11"
PLATFORMS=("win_amd64" "manylinux_2_17_x86_64" "macosx_11_0_arm64")

# Create wheels directory if it doesn't exist
mkdir -p "$WHEEL_DIR"

# Download wheels for each platform
for platform in "${PLATFORMS[@]}"; do
    echo "Downloading wheels for $platform"
    pip download rasterio --dest "$WHEEL_DIR" --only-binary=:all: --python-version="$BLENDER_PYTHON_VERSION" --platform="$platform"
done

# Delete numpy files
echo "Deleting numpy files..."
rm -f "$WHEEL_DIR"/numpy*

read -p "Press Enter to continue..." 