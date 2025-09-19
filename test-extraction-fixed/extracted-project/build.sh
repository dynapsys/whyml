#!/bin/bash
# Auto-generated build script for PASVG project
# Project: project

set -e

echo '🚀 Building PASVG project...'

# Docker Compose build
if [ -f docker-compose.yml ]; then
    echo '🐳 Building with Docker Compose...'
    docker-compose build
    echo '✅ Docker Compose build complete'
fi

echo '🎉 Build complete!'
echo 'Available build outputs:'
find . -name '*.html' -o -name 'dist' -o -name 'build' -type d 2>/dev/null || true