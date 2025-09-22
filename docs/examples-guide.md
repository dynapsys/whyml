# WhyML Examples Guide

## 🚀 Complete Webpage Scraping & Regeneration

Here's a practical example showing how WhyML can scrape a webpage, simplify its structure, and regenerate it as clean HTML from a YAML manifest:

### Step 1: Scrape a webpage and generate YAML manifest
```bash
whyml scrape https://example.com --output scraped-manifest.yaml --simplify-structure --max-depth 5
```

### Step 2: Convert YAML manifest back to HTML
```bash
whyml convert --from scraped-manifest.yaml --to regenerated.html --as html
```

### Step 3: Compare and validate (optional)
```bash
whyml scrape https://example.com --test-conversion --output-html regenerated.html
```

**📁 Complete Example Files:**
- [`examples/1/README.md`](../examples/1/README.md) - Detailed workflow documentation
- [`examples/1/scraped-manifest.yaml`](../examples/1/scraped-manifest.yaml) - Generated YAML manifest
- [`examples/1/regenerated.html`](../examples/1/regenerated.html) - Clean HTML output

**🎯 What This Achieves:**
- Converts complex webpage to maintainable YAML structure
- Simplifies HTML while preserving semantic meaning
- Enables easy customization through template variables
- Supports regeneration to multiple formats (HTML, React, Vue, PHP)

## Multi-Format Conversion Examples

### HTML Converter
Basic HTML conversion with Bootstrap integration:

```python
from whyml.converters import HTMLConverter

converter = HTMLConverter(
    include_meta_tags=True,
    css_framework='bootstrap',
    include_responsive_meta=True
)
result = converter.convert(manifest)
```

### React Converter
Modern React components with TypeScript:

```python
from whyml.converters import ReactConverter

converter = ReactConverter(
    use_typescript=True,
    use_hooks=True,
    component_type='functional'
)
result = converter.convert(manifest)
```

### Vue Converter
Vue 3 components with Composition API:

```python
from whyml.converters import VueConverter

converter = VueConverter(
    vue_version='3',
    use_composition_api=True,
    use_typescript=True
)
result = converter.convert(manifest)
```

### PHP Converter
Modern PHP classes with templating:

```python
from whyml.converters import PHPConverter

converter = PHPConverter(
    namespace='App\\Components',
    php_version='8.1',
    use_type_declarations=True
)
result = converter.convert(manifest)
```

## Web Scraping Examples

### Basic URL Scraping
```python
from whyml.scrapers import URLScraper, WebpageAnalyzer

async with URLScraper() as scraper:
    manifest = await scraper.scrape_url('https://example.com')
    
analyzer = WebpageAnalyzer()
analysis = analyzer.analyze_webpage(soup, url)
```

### Advanced Scraping with Structure Simplification
```bash
# Limit nesting depth to reduce YAML complexity
whyml scrape https://example.com --max-depth 3

# Generate only specific sections
whyml scrape https://example.com --sections metadata,structure --output simple-manifest.yaml

# Flatten unnecessary container elements  
whyml scrape https://example.com --flatten-containers --output flattened-manifest.yaml

# Complete analysis with performance metrics
whyml scrape https://example.com --analyze-page --output analyzed-manifest.yaml
```

## Template Inheritance Examples

### Base Component
```yaml
# base-component.yaml
metadata:
  title: "Base Component"
  version: "1.0.0"

styles:
  container: "width: 100%; padding: 20px;"
  
structure:
  div:
    class: "container"
    children:
      h1:
        text: "{{ title }}"
```

### Child Component
```yaml
# child-component.yaml
extends: "./base-component.yaml"

metadata:
  title: "Child Component"
  description: "Extends base component"

styles:
  content: "margin: 10px 0;"

structure:
  div:
    class: "container"
    children:
      - h1:
          text: "{{ title }}"
      - p:
          class: "content"
          text: "{{ description }}"
```

## Interactive Elements Examples

### Form with Event Handlers
```yaml
interactions:
  button_click: "handleButtonClick"
  form_submit: "handleFormSubmit"
  state_counter: "useState(0)"
  effect_mount: "useEffect(() => {}, [])"

structure:
  form:
    onSubmit: "form_submit"
    children:
      - input:
          type: "text"
          placeholder: "Enter text"
      - button:
          onClick: "button_click"
          text: "Submit"
```

## Dependency Management Examples

### External Dependencies
```yaml
imports:
  - "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
  - "./shared/styles.css"

dependencies:
  - "./components/header.yaml"
  - "./components/footer.yaml"
```

## CLI Usage Examples

### Development Server
```bash
# Start development server (default: manifest.yaml on port 8080)
whyml run

# Custom manifest and port
whyml run -f manifest.yaml -p 8080 -h localhost

# Production deployment with TLS
whyml run -f manifest.yaml --port 443 --host yourdomain.com --tls-provider letsencrypt

# Development with file watching and auto-reload
whyml run -f manifest.yaml --watch --caddy-config Caddyfile.json
```

### Application Generation
```bash
# Generate Progressive Web App
whyml generate pwa -f manifest.yaml -o ./pwa-app

# Generate Single Page Application
whyml generate spa -f manifest.yaml -o ./spa-app

# Generate mobile app configuration (APK via Capacitor)
whyml generate apk -f manifest.yaml -o ./mobile-app

# Generate desktop app (Tauri)
whyml generate tauri -f manifest.yaml -o ./desktop-app

# Generate Docker configuration
whyml generate docker -f manifest.yaml -o ./docker-config

# Generate Caddy server configuration
whyml generate caddy -f manifest.yaml -o ./Caddyfile.json
```

## Testing Examples

### Scrape-to-HTML Testing Workflow
```bash
# Scrape website and test conversion accuracy
whyml scrape https://example.com --test-conversion --similarity-threshold 0.85

# Generate comparison report
whyml scrape https://example.com --test-conversion --generate-report comparison-report.html
```

## Next Steps

- Explore detailed examples in [`examples/`](../examples/) directory
- Check out [Advanced Scraping Guide](advanced-scraping.md)
- Read the [CLI Reference](cli/README.md) for complete command documentation
