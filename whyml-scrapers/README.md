# WhyML Scrapers

Web scraping and webpage analysis components for the WhyML ecosystem.

## Features

- **URLScraper**: Comprehensive web scraping with async HTTP support
- **WebpageAnalyzer**: Advanced webpage content and structure analysis
- **ContentExtractor**: Smart content extraction and parsing
- **StructureAnalyzer**: HTML structure analysis and optimization

## Installation

```bash
pip install whyml-scrapers
```

## Quick Start

```python
from whyml_scrapers import URLScraper, WebpageAnalyzer

# Create scraper with configuration
scraper = URLScraper(
    timeout=30.0,
    max_retries=3,
    extract_styles=True,
    simplify_structure=True,
    max_depth=5
)

# Scrape website to manifest
async with scraper:
    manifest = await scraper.scrape_to_manifest("https://example.com")
    print(manifest)
```

## Advanced Features

- Structure simplification and depth limiting
- SEO and accessibility analysis
- Content statistics and performance hints
- Async context management for efficient scraping
- Flexible CSS and JavaScript extraction

## Dependencies

- aiohttp>=3.8.0
- beautifulsoup4>=4.11.0
- whyml-core>=0.1.0

## License

Apache License 2.0 - see LICENSE file for details.
