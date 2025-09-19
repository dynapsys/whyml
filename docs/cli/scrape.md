# WhyML Scrape Command

The `whyml scrape` command provides advanced website scraping capabilities with structure simplification, selective section generation, and comprehensive page analysis features.

## Quick Start

```bash
# Basic website scraping
whyml scrape https://example.com -o manifest.yaml

# Advanced scraping with structure simplification
whyml scrape https://example.com \
  --max-depth 3 \
  --flatten-containers \
  --simplify-structure \
  -o simplified.yaml

# Selective section extraction
whyml scrape https://example.com \
  --section metadata \
  --section analysis \
  -o analysis-only.yaml

# Testing workflow with comparison
whyml scrape https://example.com \
  --test-conversion \
  --output-html regenerated.html \
  -o manifest.yaml
```

## Command Syntax

```bash
whyml scrape <URL> [OPTIONS]
```

## Core Options

### Required Arguments

- `URL` - The website URL to scrape

### Output Options

- `--output, -o <file>` - Output YAML manifest file path
- `--output-html <file>` - Save regenerated HTML (used with --test-conversion)

### Structure Simplification

- `--max-depth <n>` - Limit HTML nesting depth (reduces complexity)
- `--flatten-containers` - Remove unnecessary wrapper divs  
- `--simplify-structure` - Apply general structure simplification
- `--no-preserve-semantic` - Don't preserve semantic HTML5 tags during simplification

### Content Extraction

- `--no-styles` - Skip CSS style extraction
- `--extract-scripts` - Include JavaScript code in manifest
- `--section <name>` - Extract only specific manifest sections (repeatable)

### Testing & Analysis

- `--test-conversion` - Perform round-trip conversion testing
- `--verbose, -v` - Enable detailed output

## Advanced Features

### Structure Simplification

Structure simplification helps reduce complex, deeply nested HTML to cleaner, more maintainable YAML manifests:

```bash
# Limit nesting depth to 3 levels
whyml scrape https://blog.example.com --max-depth 3

# Remove wrapper divs that don't add semantic value
whyml scrape https://legacy-site.com --flatten-containers

# Apply comprehensive structure simplification
whyml scrape https://complex-site.com \
  --max-depth 2 \
  --flatten-containers \
  --simplify-structure
```

**Benefits:**
- Reduces YAML file size and complexity
- Preserves content while removing structural noise
- Maintains semantic meaning with `--preserve-semantic` (default)
- Makes manifests easier to edit and maintain

### Selective Section Generation

Extract only the manifest sections you need for specific use cases:

```bash
# Get only page analysis (page type, SEO, accessibility metrics)
whyml scrape https://competitor.com --section analysis

# Extract metadata and imports for quick inspection  
whyml scrape https://reference-site.com \
  --section metadata \
  --section imports

# Multiple sections for refactoring projects
whyml scrape https://legacy-app.com \
  --section structure \
  --section styles \
  --section metadata
```

**Available Sections:**
- `metadata` - Page title, description, version information
- `analysis` - Page type detection, content stats, SEO analysis
- `structure` - HTML structure converted to YAML
- `styles` - CSS styles extracted from the page
- `imports` - External resources (fonts, stylesheets, scripts)

### Page Analysis Features

Automatic analysis provides valuable insights about scraped pages:

**Page Type Detection:**
- Blog posts and articles
- E-commerce product pages  
- Landing pages
- Portfolio sites
- Corporate websites

**Content Statistics:**
- Word count and readability metrics
- Element counts (paragraphs, headings, links, images)
- Content distribution analysis

**SEO Analysis:**
- Meta description presence and length
- Heading structure validation (H1, H2, etc.)
- Title tag optimization
- Social media meta tags

**Accessibility Metrics:**
- Alt text coverage for images
- Language attribute presence
- Heading hierarchy validation
- ARIA labels and semantic structure

### Testing & Comparison Workflow

Validate scraping accuracy with comprehensive testing:

```bash
# Complete round-trip testing
whyml scrape https://example.com \
  --test-conversion \
  --output-html regenerated.html \
  -o manifest.yaml
```

**Testing Process:**
1. Scrape original page → YAML manifest
2. Convert YAML manifest → Regenerated HTML
3. Compare original vs regenerated content
4. Calculate similarity metrics
5. Provide recommendations for improvement

**Metrics Provided:**
- Content similarity percentage
- Structure preservation score
- Element count comparison
- Visual similarity assessment

## Real-World Use Cases

### Website Refactoring

Modernize legacy websites by creating simplified representations:

```bash
# Extract simplified structure for redesign
whyml scrape https://legacy-corporate-site.com \
  --max-depth 3 \
  --flatten-containers \
  --simplify-structure \
  --section structure \
  --section metadata \
  -o refactored-base.yaml
```

### Competitive Analysis

Monitor competitor websites for changes:

```bash
# Extract essential data for monitoring
whyml scrape https://competitor.com \
  --section analysis \
  --section metadata \
  -o competitor-$(date +%Y%m%d).yaml
```

### Cross-Platform Development

Extract website structure for mobile/desktop app development:

```bash
# Get essential structure for app conversion
whyml scrape https://web-app.example.com \
  --section structure \
  --section metadata \
  --max-depth 2 \
  --no-preserve-semantic \
  -o mobile-app-base.yaml
```

### Content Migration

Test migration accuracy for content management projects:

```bash
# Validate migration with testing workflow
whyml scrape https://source-cms.com \
  --test-conversion \
  --section structure \
  --section imports \
  --output-html migration-preview.html \
  -o migration-manifest.yaml
```

### Quality Assurance

Automated website analysis for QA processes:

```bash
# Get comprehensive analysis for QA review
whyml scrape https://staging.example.com \
  --section analysis \
  --section metadata \
  -o qa-analysis.yaml
```

## Configuration Examples

### E-commerce Monitoring Script

```bash
#!/bin/bash
# Monitor product pages for changes

PRODUCTS=(
  "https://store.com/product1"
  "https://store.com/product2"
  "https://store.com/product3"
)

for product in "${PRODUCTS[@]}"; do
  filename="product-$(basename "$product")-$(date +%Y%m%d).yaml"
  whyml scrape "$product" \
    --section analysis \
    --section metadata \
    -o "monitoring/$filename"
done
```

### Blog Content Analysis

```bash
# Analyze blog posts for SEO and accessibility
whyml scrape https://blog.example.com/latest-post \
  --section analysis \
  --section metadata \
  --verbose \
  -o blog-analysis.yaml

# Review the analysis
cat blog-analysis.yaml | grep -A 10 "seo_analysis"
cat blog-analysis.yaml | grep -A 5 "accessibility"
```

### Legacy Website Simplification

```bash
# Create simplified version of complex legacy site
whyml scrape https://complex-legacy-site.com \
  --max-depth 2 \
  --flatten-containers \
  --simplify-structure \
  --test-conversion \
  --output-html simplified-preview.html \
  -o simplified-structure.yaml

# Review simplification results
echo "Original vs Simplified comparison:"
echo "Check simplified-preview.html for visual comparison"
```

## Error Handling

### Common Issues and Solutions

**Network Errors:**
```bash
# Timeout issues
whyml scrape https://slow-site.com --timeout 30

# SSL certificate issues
whyml scrape https://self-signed-site.com --ignore-ssl
```

**Parsing Errors:**
```bash
# Invalid HTML graceful handling
whyml scrape https://broken-html-site.com --verbose
```

**Output Issues:**
```bash
# Permission errors
sudo whyml scrape https://example.com -o /protected/manifest.yaml

# Invalid path errors  
mkdir -p output/
whyml scrape https://example.com -o output/manifest.yaml
```

## Performance Optimization

### Large Page Handling

```bash
# Optimize for large, complex pages
whyml scrape https://large-site.com \
  --max-depth 2 \
  --flatten-containers \
  --section metadata \
  --section analysis \
  -o optimized-output.yaml
```

### Batch Processing

```bash
# Process multiple URLs efficiently
urls=(
  "https://site1.com"
  "https://site2.com" 
  "https://site3.com"
)

for url in "${urls[@]}"; do
  domain=$(echo "$url" | sed 's/https\?:\/\///' | sed 's/\/.*$//')
  whyml scrape "$url" \
    --section analysis \
    --section metadata \
    -o "analysis-$domain.yaml" &
done
wait # Wait for all background jobs
```

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/website-analysis.yml
name: Website Analysis
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install WhyML
        run: pip install whyml
      - name: Analyze website
        run: |
          whyml scrape https://oursite.com \
            --section analysis \
            --section metadata \
            -o website-analysis.yaml
      - name: Upload analysis
        uses: actions/upload-artifact@v3
        with:
          name: website-analysis
          path: website-analysis.yaml
```

### Monitoring with Cron

```bash
# Add to crontab: daily website monitoring
0 6 * * * /usr/local/bin/whyml scrape https://competitor.com --section analysis -o /var/log/competitor-$(date +\%Y\%m\%d).yaml
```

## Output Format

### Standard Manifest Structure

```yaml
metadata:
  title: "Page Title"
  description: "Meta description"
  version: "1.0.0"
  url: "https://example.com"
  scraped_at: "2024-01-15T10:30:00Z"

analysis:
  page_type: "blog"  # blog, e-commerce, landing, portfolio, website
  content_stats:
    word_count: 1250
    paragraph_count: 15
    heading_count: 8
    link_count: 23
    image_count: 5
  structure_complexity:
    max_nesting_depth: 6
    total_elements: 127
    div_count: 45
    semantic_elements: ["header", "main", "article", "footer"]
    simplification_applied: true
  seo_analysis:
    has_meta_description: true
    meta_description_length: 156
    h1_count: 1
    h2_count: 3
    title_length: 42
  accessibility:
    has_lang_attribute: true
    images_with_alt_ratio: 0.8
    heading_structure_valid: true

structure:
  main:
    class: "content"
    children:
      - header:
          children:
            - h1:
                text: "Page Title"
                class: "title"
      - article:
          children:
            - p:
                text: "Content here..."

styles:
  title:
    font-size: "2rem"
    color: "#333"
    margin-bottom: "1rem"

imports:
  stylesheets:
    - "https://fonts.googleapis.com/css2?family=Inter:wght@400;700"
  scripts:
    - "https://analytics.google.com/analytics.js"
```

## See Also

- [WhyML CLI Overview](README.md)
- [Manifest Format](../manifests/schema.md)
- [Convert Command](convert.md)
- [Examples](../../examples/)
