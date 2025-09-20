# Advanced Web Scraping

## Overview

WhyML provides powerful web scraping capabilities that can intelligently convert existing websites into clean, maintainable YAML manifests. The scraping system includes structure simplification, selective content extraction, and comprehensive page analysis.

## Basic Scraping

### Simple Website Scraping

```bash
# Basic scraping
whyml scrape https://example.com --output manifest.yaml

# With structure simplification
whyml scrape https://example.com --output manifest.yaml --simplify-structure

# Limit nesting depth
whyml scrape https://example.com --output manifest.yaml --max-depth 5
```

### Output Options

```bash
# Specify output file
whyml scrape https://example.com --output my-manifest.yaml

# Save to directory
whyml scrape https://example.com --output-dir ./scraped-sites/

# Generate multiple formats
whyml scrape https://example.com --output manifest.yaml --also-html --also-react
```

## Structure Simplification

### Max Depth Limiting

Reduce HTML nesting complexity by limiting depth:

```bash
# Limit to 3 levels of nesting
whyml scrape https://example.com --max-depth 3 --output simplified.yaml
```

**Before (complex nesting):**
```html
<div class="wrapper">
  <div class="container">
    <div class="inner">
      <div class="content">
        <div class="text-wrapper">
          <p>Content</p>
        </div>
      </div>
    </div>
  </div>
</div>
```

**After (simplified):**
```html
<div class="container">
  <div class="content">
    <p>Content</p>
  </div>
</div>
```

### Container Flattening

Remove unnecessary wrapper divs:

```bash
whyml scrape https://example.com --flatten-containers --output flattened.yaml
```

Automatically removes divs with classes like:
- `wrapper`, `container`, `inner`, `outer`
- `row`, `col`, `grid-item`
- Generic wrapper classes with no semantic value

### Semantic Preservation

Preserve important HTML5 semantic elements:

```bash
# Preserve semantic elements (default)
whyml scrape https://example.com --preserve-semantic

# Disable semantic preservation
whyml scrape https://example.com --no-preserve-semantic
```

Preserved elements:
- `header`, `main`, `article`, `section`, `footer`
- `nav`, `aside`, `figure`, `figcaption`
- Heading elements (`h1`-`h6`)
- Form elements and accessibility attributes

## Selective Section Generation

Extract only specific parts of the manifest:

```bash
# Extract only metadata and structure
whyml scrape https://example.com --section metadata --section structure

# Extract analysis data only
whyml scrape https://example.com --section analysis --output analysis.yaml

# Multiple sections
whyml scrape https://example.com \
  --section metadata \
  --section styles \
  --section imports \
  --output partial.yaml
```

### Available Sections

- `metadata` - Page title, description, author info
- `structure` - HTML structure tree
- `styles` - CSS styling information
- `imports` - External CSS/JS dependencies
- `analysis` - Page analysis and metrics
- `variables` - Extracted template variables

## Page Analysis

### Automatic Page Type Detection

WhyML automatically detects page types:

```bash
whyml scrape https://blog.example.com --analyze --output blog.yaml
```

Detected types:
- **Blog**: Articles, posts, content-heavy pages
- **E-commerce**: Product pages, shopping sites
- **Landing Page**: Marketing, promotional pages
- **Portfolio**: Personal/professional showcases
- **Corporate**: Business websites, company pages

### SEO Analysis

Comprehensive SEO analysis of scraped pages:

```yaml
analysis:
  seo:
    title_length: 65          # Optimal: 50-60 characters
    meta_description: true    # Has meta description
    meta_description_length: 155  # Optimal: 150-160 characters
    heading_structure: "good" # H1 -> H2 -> H3 hierarchy
    social_meta: true         # OpenGraph/Twitter cards
    keywords_density: 2.5     # Keyword density percentage
```

### Accessibility Analysis

Accessibility compliance checking:

```yaml
analysis:
  accessibility:
    alt_text_coverage: 85     # Percentage of images with alt text
    language_attribute: true  # Has lang attribute
    heading_hierarchy: "good" # Proper heading structure
    aria_labels: 12          # Number of ARIA labels found
    wcag_compliance: "AA"    # WCAG compliance level
```

### Content Statistics

Detailed content analysis:

```yaml
analysis:
  content:
    word_count: 1250         # Total word count
    paragraph_count: 15      # Number of paragraphs
    heading_count: 8         # Number of headings
    link_count: 23          # Number of links
    image_count: 5          # Number of images
    reading_time: "5 min"   # Estimated reading time
```

## Testing Workflow

### Round-Trip Conversion Testing

Test the accuracy of scraping and regeneration:

```bash
# Complete testing workflow
whyml scrape https://example.com \
  --test-conversion \
  --output original.yaml \
  --output-html regenerated.html
```

This workflow:
1. Scrapes the original webpage
2. Generates YAML manifest
3. Converts manifest back to HTML
4. Compares original vs regenerated content
5. Provides similarity metrics

### Similarity Metrics

```yaml
testing:
  similarity:
    content_similarity: 95.2    # Text content match percentage
    structure_similarity: 88.7  # HTML structure match
    visual_similarity: 92.1     # Layout preservation
    semantic_similarity: 96.8   # Semantic meaning preservation
```

### Quality Validation

```bash
# Validate manifest quality
whyml validate original.yaml --strict

# Test conversion accuracy
whyml test-conversion original.yaml --target-url https://example.com
```

## Advanced Options

### Custom Selectors

Target specific elements for scraping:

```bash
# Scrape only main content
whyml scrape https://example.com \
  --selector "main, .content, #main-content" \
  --output content-only.yaml

# Exclude elements
whyml scrape https://example.com \
  --exclude ".ads, .sidebar, .comments" \
  --output clean.yaml
```

### Content Filtering

Filter content during scraping:

```bash
# Skip images and media
whyml scrape https://example.com --no-images --no-media

# Skip external scripts
whyml scrape https://example.com --no-scripts

# Skip inline styles
whyml scrape https://example.com --no-inline-styles
```

### Batch Scraping

Scrape multiple URLs:

```bash
# From file list
whyml scrape-batch urls.txt --output-dir ./scraped/

# With pattern
whyml scrape https://example.com/page-{1..10} --output-dir ./pages/
```

### Configuration File

Use configuration file for complex scraping:

```yaml
# scrape-config.yaml
scraping:
  max_depth: 4
  flatten_containers: true
  preserve_semantic: true
  sections: ["metadata", "structure", "styles"]
  
  filters:
    exclude_selectors: [".ads", ".popup", ".cookie-notice"]
    include_selectors: ["main", ".content"]
    
  analysis:
    enable_seo: true
    enable_accessibility: true
    enable_performance: true
    
  output:
    format: "yaml"
    optimize: true
    minify: false
```

```bash
whyml scrape https://example.com --config scrape-config.yaml
```

## Performance Optimization

### Concurrent Scraping

```bash
# Scrape multiple pages concurrently
whyml scrape-batch urls.txt --concurrent 5 --output-dir ./results/
```

### Caching

```bash
# Enable caching for repeated scraping
whyml scrape https://example.com --cache --cache-dir ./cache/

# Use cached version if available
whyml scrape https://example.com --use-cache --max-age 3600
```

### Rate Limiting

```bash
# Add delays between requests
whyml scrape-batch urls.txt --delay 2 --output-dir ./results/

# Respect robots.txt
whyml scrape https://example.com --respect-robots
```

## Error Handling

### Network Issues

```bash
# Set timeout and retries
whyml scrape https://example.com \
  --timeout 30 \
  --retries 3 \
  --output manifest.yaml
```

### Invalid HTML

WhyML handles malformed HTML gracefully:

- Automatic HTML parsing and correction
- Missing tag closure detection
- Invalid nesting structure fixes
- Character encoding detection

### Debugging

```bash
# Enable verbose output
whyml scrape https://example.com --verbose --output debug.yaml

# Save debug information
whyml scrape https://example.com --debug --debug-output debug.json
```

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/scrape-monitor.yml
name: Website Monitoring
on:
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  scrape-and-compare:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install WhyML
        run: pip install whyml
      - name: Scrape website
        run: |
          whyml scrape https://example.com \
            --output current.yaml \
            --test-conversion \
            --compare-with baseline.yaml
```

### Monitoring Script

```python
import asyncio
from whyml import URLScraper

async def monitor_website():
    scraper = URLScraper(
        max_depth=5,
        simplify_structure=True,
        enable_analysis=True
    )
    
    result = await scraper.scrape_url("https://example.com")
    
    # Check for changes
    if result.analysis.structure_changes > 10:
        print("Significant structure changes detected!")
    
    # Save manifest
    with open("current.yaml", "w") as f:
        f.write(result.to_yaml())

asyncio.run(monitor_website())
```

## Best Practices

1. **Start Simple**: Begin with basic scraping, then add complexity
2. **Test Thoroughly**: Always use test-conversion for important sites
3. **Respect Limits**: Use appropriate delays and respect robots.txt
4. **Cache Results**: Cache scraped content for development
5. **Monitor Changes**: Set up monitoring for important websites
6. **Validate Output**: Always validate generated manifests

## Troubleshooting

### Common Issues

1. **JavaScript-heavy sites**: Use headless browser mode
2. **Rate limiting**: Increase delays between requests
3. **Complex layouts**: Adjust max-depth and simplification settings
4. **Missing content**: Check selectors and filters

### Debug Commands

```bash
# Check what WhyML sees
whyml scrape https://example.com --dry-run --verbose

# Validate scraped manifest
whyml validate scraped.yaml --detailed

# Test conversion accuracy
whyml test-conversion scraped.yaml --metrics
```
