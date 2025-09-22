# WhyML Quick Start Guide

This guide will get you up and running with WhyML in just a few minutes.

## 🚀 Complete Ecosystem Usage

```python
import asyncio
from whyml import WhyMLProcessor

async def main():
    processor = WhyMLProcessor()
    
    # Convert YAML manifest to HTML
    html_result = await processor.convert_to_html('path/to/manifest.yaml')
    html_result.save_to_file('output.html')
    
    # Convert to React component
    react_result = await processor.convert_to_react('path/to/manifest.yaml')
    react_result.save_to_file('Component.tsx')

asyncio.run(main())
```

## 📦 Modular Usage

Use specific packages for targeted functionality:

```python
import asyncio
from whyml_core.loading.manifest_loader import ManifestLoader
from whyml_core.processing.manifest_processor import ManifestProcessor
from whyml_converters.html_converter import HTMLConverter
from whyml_scrapers.url_scraper import URLScraper

async def main():
    # Core functionality - load and process
    loader = ManifestLoader()
    processor = ManifestProcessor()
    
    async with loader:
        manifest = await loader.load_manifest('manifest.yaml')
        processed = processor.process_manifest(manifest)
    
    # Convert to HTML
    html_converter = HTMLConverter()
    result = html_converter.convert(processed)
    result.save_to_file('output.html')
    
    # Web scraping
    scraper = URLScraper()
    async with scraper:
        scraped_manifest = await scraper.scrape_url('https://example.com')

asyncio.run(main())
```

## ⌨️ CLI Usage

```bash
# Validate manifest using whyml-cli
whyml validate manifest.yaml

# Scrape website using whyml-scrapers  
whyml scrape https://example.com --output scraped.yaml

# Convert using whyml-converters
whyml convert manifest.yaml --format html --output result.html

# Generate applications
whyml generate pwa --manifest manifest.yaml --output ./pwa-app
```

## Example YAML Manifest

```yaml
metadata:
  title: "Landing Page"
  description: "Modern landing page component"
  version: "1.0.0"

template_vars:
  primary_color: "#007bff"
  hero_text: "Welcome to Our Product"
  cta_text: "Get Started"

styles:
  hero:
    background: "linear-gradient(135deg, {{ primary_color }}, #0056b3)"
    padding: "80px 0"
    text-align: "center"
    color: "white"
  
  cta_button:
    background: "#28a745"
    padding: "15px 30px"
    border: "none"
    border-radius: "5px"
    color: "white"
    font-weight: "bold"
    cursor: "pointer"

structure:
  main:
    class: "hero-section"
    children:
      div:
        class: "container"
        children:
          - h1:
              text: "{{ hero_text }}"
              class: "display-4"
          - p:
              text: "Transform your ideas into reality with our powerful platform"
              class: "lead"
          - button:
              text: "{{ cta_text }}"
              class: "btn btn-success btn-lg"
```

## Next Steps

- Check out the [Installation Guide](installation.md) for setup options
- Explore the [Converters Guide](converters.md) for multi-format conversion
- Learn about [Advanced Scraping](advanced-scraping.md) features
- Review the [CLI Reference](cli/README.md) for command-line usage
