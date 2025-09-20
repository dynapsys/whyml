#!/bin/bash

# Example 1: Complete Webpage Scraping and Regeneration Workflow
# This script demonstrates the complete WhyML workflow

set -e  # Exit on any error

echo "🚀 Running Example 1: Complete Webpage Scraping and Regeneration Workflow"
echo "=================================================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the WhyML root directory"
    exit 1
fi

# Create examples/1 directory if it doesn't exist
mkdir -p examples/1

# Step 1: Scrape a webpage and generate YAML manifest
echo "📥 Step 1: Scraping https://example.com..."
whyml scrape https://example.com \
    --output examples/1/scraped-manifest.yaml \
    --simplify-structure \
    --max-depth 5

if [ $? -eq 0 ]; then
    echo "✅ Successfully scraped webpage to examples/1/scraped-manifest.yaml"
else
    echo "❌ Failed to scrape webpage"
    exit 1
fi

# Step 2: Convert YAML manifest back to HTML
echo "🔄 Step 2: Converting YAML manifest to HTML..."
whyml convert \
    --from examples/1/scraped-manifest.yaml \
    --to examples/1/regenerated.html \
    --as html

if [ $? -eq 0 ]; then
    echo "✅ Successfully converted manifest to examples/1/regenerated.html"
else
    echo "❌ Failed to convert manifest to HTML"
    exit 1
fi

# Step 3: Convert to other formats (optional)
echo "🔄 Step 3: Converting to other formats..."

# Convert to React
whyml convert \
    --from examples/1/scraped-manifest.yaml \
    --to examples/1/Component.tsx \
    --as react

if [ $? -eq 0 ]; then
    echo "✅ Successfully converted to React component: examples/1/Component.tsx"
fi

# Convert to Vue
whyml convert \
    --from examples/1/scraped-manifest.yaml \
    --to examples/1/Component.vue \
    --as vue

if [ $? -eq 0 ]; then
    echo "✅ Successfully converted to Vue component: examples/1/Component.vue"
fi

# Convert to PHP
whyml convert \
    --from examples/1/scraped-manifest.yaml \
    --to examples/1/Component.php \
    --as php

if [ $? -eq 0 ]; then
    echo "✅ Successfully converted to PHP component: examples/1/Component.php"
fi

# Display results
echo ""
echo "🎉 Example 1 completed successfully!"
echo "📁 Generated files in examples/1/:"
ls -la examples/1/

echo ""
echo "🔍 To view the results:"
echo "  • Original manifest: cat examples/1/scraped-manifest.yaml"
echo "  • Generated HTML: open examples/1/regenerated.html"
echo "  • React component: cat examples/1/Component.tsx"
echo "  • Vue component: cat examples/1/Component.vue"
echo "  • PHP component: cat examples/1/Component.php"

echo ""
echo "📖 For more details, see: examples/1/README.md"
