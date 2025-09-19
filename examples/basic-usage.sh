#!/bin/bash
# WhyML Basic Usage Examples
# Demonstrates the fundamental WhyML CLI commands

echo "🚀 WhyML Basic Usage Examples"
echo "================================"

# Display version
echo "1. Check WhyML version:"
whyml --version
echo ""

# Create a simple manifest for testing
echo "2. Creating a sample manifest..."
cat > sample-manifest.yaml << EOF
metadata:
  title: "My Sample App"
  description: "A simple WhyML application"
  version: "1.0.0"
  author: "WhyML User"

template_vars:
  primary_color: "#007bff"
  app_name: "Sample App"
  welcome_text: "Welcome to WhyML!"

styles:
  header:
    background: "{{ primary_color }}"
    color: "white"
    padding: "20px"
    text-align: "center"
  
  content:
    padding: "20px"
    max-width: "800px"
    margin: "0 auto"

structure:
  div:
    class: "app-container"
    children:
      - header:
          class: "header"
          children:
            - h1:
                text: "{{ app_name }}"
      - main:
          class: "content"
          children:
            - p:
                text: "{{ welcome_text }}"
            - button:
                text: "Get Started"
                onClick: "handleStart"
EOF

echo "✅ Sample manifest created: sample-manifest.yaml"
echo ""

# Validate the manifest
echo "3. Validating the manifest:"
whyml validate sample-manifest.yaml
echo ""

# Convert to different formats using natural language syntax
echo "4. Converting manifest to different formats:"

echo "   Converting to HTML..."
whyml convert --from sample-manifest.yaml --to output.html -as html

echo "   Converting to React component..."
whyml convert --from sample-manifest.yaml --to SampleApp.tsx -as react

echo "   Converting to Vue component..."
whyml convert --from sample-manifest.yaml --to SampleApp.vue -as vue

echo "   Converting to SPA..."
whyml convert --from sample-manifest.yaml --to spa-app.html -as spa

echo "   Converting to PWA..."
whyml convert --from sample-manifest.yaml --to pwa-app.html -as pwa

echo "✅ All conversions completed!"
echo ""

# Generate application artifacts
echo "5. Generating application artifacts:"

echo "   Generating PWA..."
whyml generate pwa -f sample-manifest.yaml -o ./pwa-output

echo "   Generating SPA..."
whyml generate spa -f sample-manifest.yaml -o ./spa-output

echo "   Generating Docker configuration..."
whyml generate docker -f sample-manifest.yaml -o ./docker-output

echo "   Generating Caddy configuration..."
whyml generate caddy -f sample-manifest.yaml -o ./Caddyfile.json

echo "✅ All artifacts generated!"
echo ""

# Start development server
echo "6. Starting development server:"
echo "   Run: whyml run -f sample-manifest.yaml -p 8080"
echo "   Or:  whyml serve -f sample-manifest.yaml --port 8080 --watch"
echo ""

echo "🎉 Basic examples completed!"
echo ""
echo "Generated files:"
echo "- output.html (HTML conversion)"
echo "- SampleApp.tsx (React component)"
echo "- SampleApp.vue (Vue component)"
echo "- spa-app.html (SPA version)"
echo "- pwa-app.html (PWA version)"
echo "- ./pwa-output/ (Complete PWA)"
echo "- ./spa-output/ (Complete SPA)"
echo "- ./docker-output/ (Docker configuration)"
echo "- ./Caddyfile.json (Caddy configuration)"
echo ""
echo "To start the development server:"
echo "whyml run -f sample-manifest.yaml"
