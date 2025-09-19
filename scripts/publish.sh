#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo "${YELLOW}📦 Publishing to PyPI with automatic version increment...${NC}"

# Ensure setuptools, twine, and build are installed
echo "${YELLOW}Checking dependencies...${NC}"
if ! python3 -c "import setuptools" &> /dev/null; then
    echo "${YELLOW}Installing setuptools...${NC}"
    python3 -m pip install setuptools
fi

if ! python3 -c "import build" &> /dev/null; then
    echo "${YELLOW}Installing build...${NC}"
    python3 -m pip install build
fi

if ! command -v twine &> /dev/null; then
    echo "${YELLOW}Installing twine...${NC}"
    python3 -m pip install twine
fi

# Auto-increment patch version
echo "${YELLOW}🔢 Auto-incrementing patch version...${NC}"
if python3 scripts/version_manager.py patch; then
    echo "${GREEN}✅ Version incremented successfully${NC}"
else
    echo "${RED}❌ Failed to increment version${NC}"
    exit 1
fi

# Clean previous builds
echo "${YELLOW}🧹 Cleaning previous builds...${NC}"
rm -rf build/ dist/ *.egg-info/

# Build the package
echo "${YELLOW}🏗️ Building package...${NC}"
if python3 -m build; then
    echo "${GREEN}✅ Package built successfully${NC}"
else
    echo "${RED}❌ Package build failed${NC}"
    exit 1
fi

# Upload to PyPI
echo "${YELLOW}🚀 Uploading to PyPI...${NC}"
if twine upload dist/*; then
    echo "${GREEN}✅ Published to PyPI successfully${NC}"
    
    # Get the new version for confirmation
    NEW_VERSION=$(python3 -c "from setup import version; print(version)")
    echo "${GREEN}🎉 New version ${NEW_VERSION} is now live on PyPI!${NC}"
else
    echo "${RED}❌ Upload to PyPI failed${NC}"
    exit 1
fi
