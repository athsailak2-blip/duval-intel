#!/bin/bash
# Build script for Duval County Lead Intelligence Dashboard

echo "Building Duval County Dashboard..."

# Create dist directory
mkdir -p dist

# Copy dashboard files
cp -r dashboard/* dist/

# Copy data files
cp -r data dist/ 2>/dev/null || true

echo "Build complete. Files in dist/"
echo "To deploy: push to GitHub or copy dist/ contents to web server"
