# WhyML API Usage Guide

## REST API Server

Start the FastAPI server for REST API access:

```bash
whyml server --port 8000
```

### API Endpoints

- `POST /api/convert` - Convert manifest to specified format
- `GET /api/manifest/{name}` - Load manifest by name
- `POST /api/scrape` - Scrape URL to manifest
- `POST /api/validate` - Validate manifest structure
- `GET /api/health` - Health check endpoint

### Example API Usage

#### Convert Manifest
```bash
curl -X POST "http://localhost:8000/api/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "manifest_path": "path/to/manifest.yaml",
    "format": "html",
    "options": {
      "include_meta_tags": true,
      "css_framework": "bootstrap"
    }
  }'
```

#### Scrape URL to Manifest
```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "options": {
      "max_depth": 3,
      "simplify_structure": true
    }
  }'
```

#### Validate Manifest
```bash
curl -X POST "http://localhost:8000/api/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "manifest_path": "path/to/manifest.yaml"
  }'
```

## Python API

### Core Functionality

#### ManifestLoader
```python
from whyml_core.loading.manifest_loader import ManifestLoader

async def load_manifest():
    loader = ManifestLoader()
    async with loader:
        manifest = await loader.load_manifest('manifest.yaml')
        return manifest
```

#### ManifestProcessor  
```python
from whyml_core.processing.manifest_processor import ManifestProcessor

def process_manifest(manifest):
    processor = ManifestProcessor()
    processed = processor.process_manifest(manifest)
    return processed
```

### Converters

#### HTML Converter
```python
from whyml_converters.html_converter import HTMLConverter

converter = HTMLConverter(
    include_meta_tags=True,
    css_framework='bootstrap',
    include_responsive_meta=True
)
result = converter.convert(manifest)
result.save_to_file('output.html')
```

#### React Converter
```python
from whyml_converters.react_converter import ReactConverter

converter = ReactConverter(
    use_typescript=True,
    use_hooks=True,
    component_type='functional'
)
result = converter.convert(manifest)
result.save_to_file('Component.tsx')
```

#### Vue Converter
```python
from whyml_converters.vue_converter import VueConverter

converter = VueConverter(
    vue_version='3',
    use_composition_api=True,
    use_typescript=True
)
result = converter.convert(manifest)
result.save_to_file('Component.vue')
```

#### PHP Converter
```python
from whyml_converters.php_converter import PHPConverter

converter = PHPConverter(
    namespace='App\\Components',
    php_version='8.1',
    use_type_declarations=True
)
result = converter.convert(manifest)
result.save_to_file('Component.php')
```

### Web Scraping

#### URLScraper
```python
from whyml_scrapers.url_scraper import URLScraper

async def scrape_url():
    scraper = URLScraper()
    async with scraper:
        manifest = await scraper.scrape_url('https://example.com')
        return manifest
```

#### WebpageAnalyzer
```python
from whyml_scrapers.webpage_analyzer import WebpageAnalyzer

analyzer = WebpageAnalyzer()
analysis = analyzer.analyze_webpage(soup, url)
```

### Validation

#### ManifestValidator
```python
from whyml_core.validation.manifest_validator import ManifestValidator

validator = ManifestValidator()
result = validator.validate(manifest)
if result.is_valid:
    print("✓ Manifest is valid")
else:
    print("✗ Validation errors:", result.errors)
```

### Exception Handling

```python
from whyml_core.exceptions import (
    WhyMLError,
    ValidationError,
    ManifestLoadingError,
    ManifestProcessingError,
    ConversionError,
    DependencyResolutionError,
    ConfigurationError
)

try:
    # Your WhyML operations
    result = await processor.convert_to_html('manifest.yaml')
except ValidationError as e:
    print(f"Validation failed: {e}")
except ConversionError as e:
    print(f"Conversion failed: {e}")
except WhyMLError as e:
    print(f"WhyML error: {e}")
```

## Advanced API Usage

### Custom Converter
```python
from whyml_converters.base_converter import BaseConverter

class CustomConverter(BaseConverter):
    def __init__(self, **options):
        super().__init__()
        self.options = options
    
    def convert(self, manifest):
        # Custom conversion logic
        return self.create_result(converted_content)
```

### Custom Scraper
```python
from whyml_scrapers.base_scraper import BaseScraper

class CustomScraper(BaseScraper):
    async def scrape_url(self, url, **options):
        # Custom scraping logic
        return manifest
```

## Integration Examples

### With FastAPI
```python
from fastapi import FastAPI
from whyml import WhyMLProcessor

app = FastAPI()
processor = WhyMLProcessor()

@app.post("/convert")
async def convert_manifest(manifest_path: str, format: str):
    if format == "html":
        result = await processor.convert_to_html(manifest_path)
    elif format == "react":
        result = await processor.convert_to_react(manifest_path)
    return {"content": result.content}
```

### With Flask
```python
from flask import Flask, request, jsonify
from whyml import WhyMLProcessor
import asyncio

app = Flask(__name__)
processor = WhyMLProcessor()

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    manifest_path = data['manifest_path']
    format = data['format']
    
    if format == "html":
        result = asyncio.run(processor.convert_to_html(manifest_path))
    elif format == "react":
        result = asyncio.run(processor.convert_to_react(manifest_path))
    
    return jsonify({"content": result.content})
```

## Next Steps

- Read the [CLI Reference](cli/README.md) for command-line usage
- Explore [Advanced Features](advanced-features.md)
- Check out [Integration Examples](integration-examples.md)
