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
whyml convert scraped-manifest.yaml --to html --output regenerated.html
```

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
