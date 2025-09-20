# API Reference

## Overview

WhyML provides both a Python API and a REST API for programmatic access to all functionality. This reference covers all available classes, methods, and endpoints.

## Python API

### WhyMLProcessor

Main processor class for converting manifests to different formats.

```python
from whyml import WhyMLProcessor

processor = WhyMLProcessor()
```

#### Methods

##### `convert_to_html(manifest_path: str, **kwargs) -> ConversionResult`

Convert YAML manifest to HTML.

**Parameters:**
- `manifest_path` (str): Path to YAML manifest file
- `**kwargs`: Additional conversion options
  - `optimize_output` (bool): Minify HTML output
  - `include_meta_tags` (bool): Include SEO meta tags
  - `responsive_design` (bool): Include responsive viewport

**Returns:** `ConversionResult` object

**Example:**
```python
result = await processor.convert_to_html('manifest.yaml', optimize_output=True)
result.save_to_file('output.html')
```

##### `convert_to_react(manifest_path: str, **kwargs) -> ConversionResult`

Convert YAML manifest to React component.

**Parameters:**
- `manifest_path` (str): Path to YAML manifest file
- `**kwargs`: Additional options
  - `use_typescript` (bool): Generate TypeScript component
  - `use_hooks` (bool): Use React hooks
  - `css_modules` (bool): Use CSS modules

**Example:**
```python
result = await processor.convert_to_react(
    'manifest.yaml',
    use_typescript=True,
    css_modules=True
)
```

##### `convert_to_vue(manifest_path: str, **kwargs) -> ConversionResult`

Convert YAML manifest to Vue component.

**Parameters:**
- `manifest_path` (str): Path to YAML manifest file
- `**kwargs`: Additional options
  - `composition_api` (bool): Use Composition API
  - `typescript` (bool): Use TypeScript
  - `scoped_styles` (bool): Use scoped CSS

##### `convert_to_php(manifest_path: str, **kwargs) -> ConversionResult`

Convert YAML manifest to PHP component.

**Parameters:**
- `manifest_path` (str): Path to YAML manifest file
- `**kwargs`: Additional options
  - `namespace` (str): PHP namespace
  - `use_type_declarations` (bool): Use PHP type hints

##### `scrape_url_to_manifest(url: str, **kwargs) -> dict`

Scrape URL and convert to YAML manifest.

**Parameters:**
- `url` (str): URL to scrape
- `**kwargs`: Scraping options
  - `max_depth` (int): Maximum nesting depth
  - `simplify_structure` (bool): Simplify HTML structure
  - `sections` (list): Sections to extract

### ManifestLoader

Load and process YAML manifests with inheritance support.

```python
from whyml import ManifestLoader

loader = ManifestLoader()
```

#### Methods

##### `load_manifest(path: str) -> dict`

Load YAML manifest from file or URL.

**Parameters:**
- `path` (str): Path to manifest file or URL

**Returns:** Parsed manifest dictionary

**Example:**
```python
async with loader:
    manifest = await loader.load_manifest('manifest.yaml')
```

##### `resolve_dependencies(manifest: dict) -> dict`

Resolve template inheritance and dependencies.

**Parameters:**
- `manifest` (dict): Loaded manifest

**Returns:** Resolved manifest with all dependencies

### URLScraper

Advanced web scraping with structure analysis.

```python
from whyml.scrapers import URLScraper

scraper = URLScraper(
    max_depth=5,
    simplify_structure=True,
    preserve_semantic=True
)
```

#### Constructor Parameters

- `max_depth` (int): Maximum HTML nesting depth
- `simplify_structure` (bool): Enable structure simplification
- `flatten_containers` (bool): Remove wrapper divs
- `preserve_semantic` (bool): Preserve semantic HTML elements
- `extract_styles` (bool): Extract CSS styles
- `extract_scripts` (bool): Extract JavaScript
- `enable_analysis` (bool): Enable page analysis

#### Methods

##### `scrape_url(url: str, **kwargs) -> ScrapingResult`

Scrape URL and return structured result.

**Parameters:**
- `url` (str): URL to scrape
- `**kwargs`: Additional options

**Returns:** `ScrapingResult` object

**Example:**
```python
result = await scraper.scrape_url('https://example.com')
manifest = result.to_manifest()
```

### WebpageAnalyzer

Analyze webpage content and structure.

```python
from whyml.scrapers import WebpageAnalyzer

analyzer = WebpageAnalyzer()
```

#### Methods

##### `analyze_page(html: str, url: str) -> dict`

Analyze HTML content and return metrics.

**Parameters:**
- `html` (str): HTML content
- `url` (str): Page URL

**Returns:** Analysis dictionary with metrics

### Converters

Individual converter classes for each output format.

#### HTMLConverter

```python
from whyml.converters import HTMLConverter

converter = HTMLConverter(
    doctype="html5",
    include_meta_tags=True,
    responsive_design=True
)

result = converter.convert(manifest)
```

#### ReactConverter

```python
from whyml.converters import ReactConverter

converter = ReactConverter(
    use_typescript=True,
    use_hooks=True,
    css_framework="css-modules"
)

result = converter.convert(manifest)
```

#### VueConverter

```python
from whyml.converters import VueConverter

converter = VueConverter(
    vue_version=3,
    use_composition_api=True,
    scoped_styles=True
)

result = converter.convert(manifest)
```

#### PHPConverter

```python
from whyml.converters import PHPConverter

converter = PHPConverter(
    namespace="App\\Components",
    use_type_declarations=True
)

result = converter.convert(manifest)
```

### ConversionResult

Result object returned by all converters.

#### Properties

- `content` (str): Generated code content
- `filename` (str): Suggested filename
- `format_type` (str): Output format
- `metadata` (dict): Conversion metadata

#### Methods

##### `save_to_file(path: str) -> None`

Save content to file.

##### `get_size() -> int`

Get content size in bytes.

##### `get_lines() -> int`

Get number of lines in content.

## REST API

WhyML provides a FastAPI-based REST API for web integration.

### Starting the Server

```bash
whyml-server --host 0.0.0.0 --port 8000
```

### Base URL

```
http://localhost:8000
```

### Authentication

Currently no authentication required. API keys coming in future versions.

### Endpoints

#### Health Check

**GET** `/api/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-20T10:30:00Z"
}
```

#### Convert Manifest

**POST** `/api/convert`

Convert YAML manifest to specified format.

**Request Body:**
```json
{
  "manifest": "metadata:\n  title: Test\n...",
  "format": "html",
  "options": {
    "optimize_output": true,
    "include_meta_tags": true
  }
}
```

**Parameters:**
- `manifest` (string): YAML manifest content
- `format` (string): Output format (html, react, vue, php)
- `options` (object): Format-specific options

**Response:**
```json
{
  "success": true,
  "content": "<!DOCTYPE html>...",
  "filename": "component.html",
  "metadata": {
    "format": "html",
    "size": 1024,
    "lines": 45
  }
}
```

#### Scrape URL

**POST** `/api/scrape`

Scrape URL and return YAML manifest.

**Request Body:**
```json
{
  "url": "https://example.com",
  "options": {
    "max_depth": 5,
    "simplify_structure": true,
    "sections": ["metadata", "structure", "styles"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "manifest": "metadata:\n  title: Example\n...",
  "analysis": {
    "page_type": "landing_page",
    "complexity_score": 3,
    "seo_score": 85
  }
}
```

#### Validate Manifest

**POST** `/api/validate`

Validate YAML manifest structure.

**Request Body:**
```json
{
  "manifest": "metadata:\n  title: Test\n..."
}
```

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Missing description in metadata"
  ]
}
```

#### Batch Convert

**POST** `/api/batch-convert`

Convert multiple manifests in batch.

**Request Body:**
```json
{
  "manifests": [
    {
      "name": "page1",
      "content": "metadata:\n  title: Page 1\n..."
    },
    {
      "name": "page2", 
      "content": "metadata:\n  title: Page 2\n..."
    }
  ],
  "format": "html",
  "options": {}
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "name": "page1",
      "content": "<!DOCTYPE html>...",
      "filename": "page1.html"
    },
    {
      "name": "page2",
      "content": "<!DOCTYPE html>...",
      "filename": "page2.html"
    }
  ]
}
```

### Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid manifest structure",
    "details": {
      "line": 5,
      "column": 10,
      "field": "metadata.title"
    }
  }
}
```

### Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per IP
- Batch operations count as multiple requests

### WebSocket API

Real-time conversion and scraping via WebSocket.

#### Connect

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

#### Convert Message

```json
{
  "type": "convert",
  "data": {
    "manifest": "...",
    "format": "html"
  }
}
```

#### Response Message

```json
{
  "type": "convert_result",
  "data": {
    "content": "...",
    "filename": "..."
  }
}
```

## Error Handling

### Exception Classes

```python
from whyml.exceptions import (
    WhyMLError,
    ManifestLoadingError,
    ConversionError,
    ScrapingError,
    ValidationError
)
```

#### WhyMLError

Base exception class for all WhyML errors.

#### ManifestLoadingError

Raised when manifest loading fails.

#### ConversionError

Raised when format conversion fails.

#### ScrapingError

Raised when web scraping fails.

#### ValidationError

Raised when manifest validation fails.

### Error Handling Example

```python
try:
    result = await processor.convert_to_html('manifest.yaml')
except ManifestLoadingError as e:
    print(f"Failed to load manifest: {e}")
except ConversionError as e:
    print(f"Conversion failed: {e}")
except WhyMLError as e:
    print(f"WhyML error: {e}")
```

## Configuration

### Global Configuration

```python
from whyml import configure

configure(
    default_timeout=30,
    cache_enabled=True,
    cache_dir="~/.whyml/cache",
    log_level="INFO"
)
```

### Environment Variables

- `WHYML_CACHE_DIR`: Cache directory path
- `WHYML_LOG_LEVEL`: Logging level
- `WHYML_TIMEOUT`: Default timeout in seconds
- `WHYML_API_KEY`: API key for external services

## Examples

### Complete Workflow Example

```python
import asyncio
from whyml import WhyMLProcessor, URLScraper

async def complete_workflow():
    # Scrape website
    scraper = URLScraper(simplify_structure=True)
    scraping_result = await scraper.scrape_url('https://example.com')
    
    # Save manifest
    manifest_content = scraping_result.to_yaml()
    with open('scraped.yaml', 'w') as f:
        f.write(manifest_content)
    
    # Convert to multiple formats
    processor = WhyMLProcessor()
    
    # HTML
    html_result = await processor.convert_to_html('scraped.yaml')
    html_result.save_to_file('output.html')
    
    # React
    react_result = await processor.convert_to_react(
        'scraped.yaml',
        use_typescript=True
    )
    react_result.save_to_file('Component.tsx')
    
    # Vue
    vue_result = await processor.convert_to_vue(
        'scraped.yaml',
        composition_api=True
    )
    vue_result.save_to_file('Component.vue')

asyncio.run(complete_workflow())
```

### Custom Converter Example

```python
from whyml.converters import BaseConverter

class CustomConverter(BaseConverter):
    @property
    def format_name(self) -> str:
        return "Custom"
    
    @property
    def file_extension(self) -> str:
        return "custom"
    
    def convert(self, manifest: dict, **kwargs):
        # Custom conversion logic
        content = self.generate_custom_format(manifest)
        
        return ConversionResult(
            content=content,
            filename=self.generate_filename(manifest),
            format_type="custom"
        )
```

## Performance Tips

1. **Use async/await**: All I/O operations are async
2. **Cache manifests**: Enable caching for repeated operations
3. **Batch operations**: Use batch APIs for multiple conversions
4. **Optimize manifests**: Simplify structure for better performance
5. **Connection pooling**: Reuse HTTP connections for scraping
