# Example 1: Complete Webpage Scraping and Regeneration Workflow

This example demonstrates the complete WhyML workflow: scraping a webpage, simplifying its structure, and regenerating it as HTML from a YAML manifest.

## Files in this example:

- `README.md` - This documentation
- `scraped-manifest.yaml` - YAML manifest generated from webpage scraping
- `regenerated.html` - HTML file regenerated from the YAML manifest

## Workflow Steps:

### 1. Scrape a webpage and generate YAML manifest
```bash
whyml scrape https://example.com --output scraped-manifest.yaml --simplify-structure --max-depth 5
```

### 2. Convert YAML manifest back to HTML
```bash
whyml convert --from scraped-manifest.yaml --to regenerated.html --as html
```

## 🚀 Easy Way to Run This Example

Instead of running commands manually, use our provided scripts:

### Option 1: Run with Bash Script (Recommended)
```bash
# From WhyML root directory
./scripts/examples/run-example-1.sh
```

### Option 2: Run with Python Script
```bash
# From WhyML root directory  
python3 scripts/examples/run-example-1.py
```

### Option 3: Run All Examples
```bash
# From WhyML root directory
./scripts/run-all-examples.sh
```

These scripts will:
- ✅ Check that WhyML is properly installed
- ✅ Create the examples/1/ directory
- ✅ Run all commands with correct syntax
- ✅ Generate multiple output formats (HTML, React, Vue, PHP)
- ✅ Show you exactly what was created and where

### 3. Compare original vs regenerated (optional)
```bash
whyml scrape https://example.com --test-conversion --output-html regenerated.html
```

## Key Features Demonstrated:

- **Structure Simplification**: Reduces HTML complexity while preserving content
- **Manifest Generation**: Creates clean, maintainable YAML structure
- **Multi-format Output**: Can regenerate to HTML, React, Vue, or PHP
- **Content Preservation**: Maintains semantic meaning and accessibility

## Expected Results:

The regenerated HTML should maintain the essential structure and content of the original webpage while being cleaner and more maintainable through the YAML manifest approach.
