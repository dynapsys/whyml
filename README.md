# WhyML - Modular YAML Manifest Ecosystem


```bash
 ██╗    ██╗██╗  ██╗██╗   ██╗███╗   ███╗██╗     
 ██║    ██║██║  ██║╚██╗ ██╔╝████╗ ████║██║     
 ██║ █╗ ██║███████║ ╚████╔╝ ██╔████╔██║██║     
 ██║███╗██║██╔══██║  ╚██╔╝  ██║╚██╔╝██║██║     
 ╚███╔███╔╝██║  ██║   ██║   ██║ ╚═╝ ██║███████╗
  ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝╚══════╝
```

**🏗️ Modular YAML-based component generation and multi-format conversion ecosystem**

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-450%2B_passing-brightgreen.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](#testing)
[![Modular](https://img.shields.io/badge/architecture-modular-blue.svg)](#modular-architecture)

## 📚 Table of Contents

### 🚀 Getting Started
- [🚀 Quick Example](#-quick-example-complete-webpage-scraping--regeneration) - Complete workflow demonstration
- [⚡ Installation](#installation) - Setup and installation guide
- [🏁 Quick Start](#quick-start) - Basic usage examples
- [📖 Getting Started Guide](docs/getting-started.md) - Comprehensive beginner guide

### 📋 Documentation
- [🏗️ Modular Architecture Guide](docs/modular-architecture.md) - **NEW**: Complete modular ecosystem guide
- [📝 YAML Manifest Reference](docs/manifest-reference.md) - Complete manifest specification
- [🔄 Converters Guide](docs/converters.md) - HTML, React, Vue, PHP conversion
- [🕷️ Advanced Scraping](docs/advanced-scraping.md) - Web scraping features and techniques
- [🔧 CLI Reference](docs/cli/README.md) - Command-line interface documentation
- [🌐 API Reference](docs/api-reference.md) - Python and REST API documentation

### 💡 Examples & Tutorials
- [📁 Example 1: Complete Workflow](examples/1/README.md) - Scraping and regeneration
- [🔬 Advanced Scraping Examples](examples/advanced-scraping/README.md) - Complex scenarios
- [🧪 Testing Guide](docs/USER_TESTING_GUIDE.md) - Testing and validation

### 🛠️ Development
- [🚀 Production Deployment](docs/PRODUCTION_DEPLOYMENT_CHECKLIST.md) - Deployment guide
- [🔍 CLI Scraping Reference](docs/cli/scrape.md) - Detailed scraping commands
- [📊 Project Status](FIXES_AND_STATUS.md) - Current status and fixes

### 🎯 Key Features
- [Multi-Format Conversion](#key-features) - HTML, React, Vue, PHP output
- [Advanced Web Scraping](#key-features) - Structure simplification and analysis
- [Template Inheritance](#key-features) - Reusable component system
- [Testing & Validation](#testing) - Comprehensive test suite

## 🏗️ Modular Architecture

WhyML has been completely refactored into a **modular ecosystem** of specialized packages, providing better maintainability, testing, and deployment flexibility:

### 📦 Core Packages

- **`whyml-core`** - Core functionality (validation, loading, processing, utilities)
- **`whyml-scrapers`** - Web scraping and analysis capabilities  
- **`whyml-converters`** - Multi-format conversion (HTML, React, Vue, PHP)
- **`whyml-cli`** - Unified command-line interface
- **`whyml`** - Main package orchestrating all modules

### 🎯 Benefits of Modular Design

- **🔧 Targeted Installation**: Install only the components you need
- **🧪 Comprehensive Testing**: 450+ test cases across all modules
- **⚡ Performance**: Optimized loading and processing
- **🔄 Easy Maintenance**: Clear separation of concerns
- **📈 Scalability**: Independent package updates and versioning

## Overview

WhyML is a powerful modular Python ecosystem that transforms YAML manifests into multiple output formats including HTML, React, Vue, and PHP. It provides a comprehensive system for component-based development with template inheritance, dependency resolution, and intelligent web scraping capabilities.

### Key Features

- 🚀 **Multi-Format Conversion**: Generate HTML, React (JSX/TSX), Vue (SFC), and PHP from YAML manifests
- 🔗 **Template Inheritance**: Advanced inheritance system with dependency resolution and circular dependency detection
- 🎨 **CSS Integration**: Built-in support for CSS frameworks (Bootstrap, Tailwind, Foundation)
- 🕷️ **Advanced Web Scraping**: Intelligent website-to-manifest conversion with:
  - **Structure Simplification**: Reduce HTML nesting depth and flatten unnecessary containers
  - **Selective Section Generation**: Extract only specific sections (metadata, analysis, imports, etc.)
  - **Page Analysis**: Automatic detection of page types, SEO analysis, and accessibility metrics
  - **Testing Workflow**: Complete scrape → YAML → HTML comparison with accuracy metrics
- ⚡ **Async Processing**: High-performance asynchronous manifest loading and processing
- 🧪 **Comprehensive Testing**: Extensive test suite with 95%+ coverage
- 🛠️ **CLI & API**: Command-line interface and FastAPI server for integration

## 🚀 Quick Example: Complete Webpage Scraping & Regeneration

Here's a practical example showing how WhyML can scrape a webpage, simplify its structure, and regenerate it as clean HTML from a YAML manifest:

### Step 1: Scrape a webpage and generate YAML manifest
```bash
whyml scrape https://example.com --output scraped-manifest.yaml --simplify-structure --max-depth 5
```
![img.png](img.png)

### Step 2: Convert YAML manifest back to HTML
```bash
whyml convert --from scraped-manifest.yaml --to regenerated.html --as html
```
![structure](structure.png)

### Step 3: Compare and validate (optional)
```bash
whyml scrape https://example.com --test-conversion --output-html regenerated.html
```
![img_1.png](img_1.png)


**📁 Complete Example Files:**
- [`examples/1/README.md`](examples/1/README.md) - Detailed workflow documentation
- [`examples/1/scraped-manifest.yaml`](examples/1/scraped-manifest.yaml) - Generated YAML manifest
- [`examples/1/regenerated.html`](examples/1/regenerated.html) - Clean HTML output

**🎯 What This Achieves:**
- Converts complex webpage to maintainable YAML structure
- Simplifies HTML while preserving semantic meaning
- Enables easy customization through template variables
- Supports regeneration to multiple formats (HTML, React, Vue, PHP)

## Installation

### 🚀 Complete Ecosystem (Recommended)

```bash
# Install complete WhyML ecosystem
pip install whyml
```

This installs all modular packages: `whyml-core`, `whyml-scrapers`, `whyml-converters`, and `whyml-cli`.

### 📦 Modular Installation (Targeted)

Install only the components you need:

```bash
# Core functionality only
pip install whyml-core

# Core + web scraping
pip install whyml-core whyml-scrapers  

# Core + format conversion  
pip install whyml-core whyml-converters

# CLI interface (includes all dependencies)
pip install whyml-cli

# Custom combination
pip install whyml-core whyml-converters whyml-cli
```

### 🔧 Development Installation

```bash
git clone https://github.com/dynapsys/whyml.git
cd whyml
pip install -e .

# Install all modular packages in development mode
pip install -e ./whyml-core
pip install -e ./whyml-scrapers  
pip install -e ./whyml-converters
pip install -e ./whyml-cli
```

## Quick Start

### 🚀 Complete Ecosystem Usage

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

### 📦 Modular Usage

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

### ⌨️ CLI Usage

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

### Example YAML Manifest

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

## Advanced Web Scraping

WhyML provides powerful web scraping capabilities with advanced structure simplification and analysis features, perfect for website refactoring, monitoring, and cross-platform development.

### Structure Simplification

Reduce complex HTML structures while preserving content and semantic meaning:

```bash
# Limit nesting depth to reduce YAML complexity
whyml scrape https://example.com --max-depth 3

# Flatten unnecessary wrapper divs
whyml scrape https://example.com --flatten-containers

# Apply general structure simplification
whyml scrape https://example.com --simplify-structure

# Combine multiple simplification options
whyml scrape https://blog.example.com \
  --max-depth 2 \
  --flatten-containers \
  --simplify-structure
```

### Selective Section Generation

Extract only the sections you need for specific use cases:

```bash
# Extract only page analysis (page type detection, SEO metrics)
whyml scrape https://example.com --section analysis

# Get metadata and imports for quick inspection
whyml scrape https://example.com --section metadata --section imports

# Perfect for monitoring - extract only essential data
whyml scrape https://ecommerce-site.com --section analysis --section metadata

# Multiple sections for refactoring projects
whyml scrape https://legacy-site.com \
  --section structure \
  --section styles \
  --max-depth 3
```

### Testing & Comparison Workflow

Validate conversion accuracy with comprehensive testing:

```bash
# Complete round-trip testing: scrape → YAML → HTML → compare
whyml scrape https://example.com --test-conversion

# Save regenerated HTML for manual inspection
whyml scrape https://example.com \
  --test-conversion \
  --output-html regenerated.html

# Test with simplification settings
whyml scrape https://complex-site.com \
  --test-conversion \
  --max-depth 2 \
  --flatten-containers \
  --output-html simplified.html
```

### Page Analysis Features

Automatic detection and analysis of web page characteristics:

- **Page Type Detection**: blog, e-commerce, landing page, portfolio, etc.
- **Content Statistics**: word count, element count, links, images
- **Structure Complexity**: nesting depth, semantic elements analysis
- **SEO Analysis**: meta descriptions, heading structure, alt attributes
- **Accessibility Metrics**: alt text coverage, heading hierarchy, language attributes

### Real-World Use Cases

#### Website Refactoring
```bash
# Create simplified representations for legacy website modernization
whyml scrape https://legacy-corporate-site.com \
  --simplify-structure \
  --max-depth 3 \
  --flatten-containers \
  --output refactored-manifest.yaml
```

#### Cross-Platform Development
```bash
# Extract essential structure for mobile app development
whyml scrape https://web-app.com \
  --section structure \
  --section metadata \
  --max-depth 2 \
  --no-preserve-semantic
```

#### Website Monitoring
```bash
# Track page changes with essential data only
whyml scrape https://competitor-site.com \
  --section analysis \
  --section metadata \
  --output monitoring-$(date +%Y%m%d).yaml
```

#### Content Migration
```bash
# Test conversion accuracy for content migration projects
whyml scrape https://source-site.com \
  --test-conversion \
  --section structure \
  --section imports \
  --output-html migrated-preview.html
```
    border-radius: "8px"
    font-size: "1.2rem"

interactions:
  cta_click: "handleCTAClick"
  scroll_tracking: "trackScrollPosition"

structure:
  div:
    class: "container"
    children:
      - section:
          class: "hero"
          children:
            - h1:
                text: "{{ hero_text }}"
            - button:
                class: "cta_button"
                text: "{{ cta_text }}"
                onClick: "cta_click"
```

## Core Components

### Manifest Loader

Handles YAML manifest loading with advanced features:

- **Async Loading**: Non-blocking file and URL loading
- **Dependency Resolution**: Automatic resolution of manifest dependencies
- **Template Inheritance**: Support for `extends` relationships
- **Caching**: TTL-based caching for performance
- **Error Handling**: Comprehensive error reporting

```python
from whyml.manifest_loader import ManifestLoader

async with ManifestLoader() as loader:
    manifest = await loader.load_manifest('manifest.yaml')
```

### Manifest Processor

Processes loaded manifests with template resolution:

- **Template Variables**: Jinja2-based template processing
- **Style Optimization**: CSS optimization and merging
- **Validation**: Schema validation and error detection
- **Inheritance Merging**: Smart merging of inherited manifests

```python
from whyml.manifest_processor import ManifestProcessor

processor = ManifestProcessor()
processed = processor.process_manifest(raw_manifest)
```

### Format Converters

#### HTML Converter
Generates semantic, optimized HTML with integrated CSS:

```python
from whyml.converters import HTMLConverter

converter = HTMLConverter(
    css_framework='bootstrap',
    optimize_output=True,
    include_meta_tags=True
)
result = converter.convert(manifest)
```

#### React Converter
Creates React functional components with TypeScript support:

```python
from whyml.converters import ReactConverter

converter = ReactConverter(
    use_typescript=True,
    component_type='functional',
    css_framework='tailwind'
)
result = converter.convert(manifest)
```

#### Vue Converter
Generates Vue 3 Single File Components:

```python
from whyml.converters import VueConverter

converter = VueConverter(
    vue_version='3',
    use_composition_api=True,
    use_typescript=True
)
result = converter.convert(manifest)
```

#### PHP Converter
Creates modern PHP classes with templating:

```python
from whyml.converters import PHPConverter

converter = PHPConverter(
    namespace='App\\Components',
    php_version='8.1',
    use_type_declarations=True
)
result = converter.convert(manifest)
```

### Web Scraping

Intelligent website analysis and manifest generation:

```python
from whyml.scrapers import URLScraper, WebpageAnalyzer

async with URLScraper() as scraper:
    manifest = await scraper.scrape_url('https://example.com')
    
analyzer = WebpageAnalyzer()
analysis = analyzer.analyze_webpage(soup, url)
```

## Advanced Features

### Template Inheritance

Create reusable base components:

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

### Dependency Management

```yaml
imports:
  - "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
  - "./shared/styles.css"

dependencies:
  - "./components/header.yaml"
  - "./components/footer.yaml"
```

### Interactive Elements

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

## CLI Usage

### Development Server (`whyml run`)

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

### Natural Language Conversion

```bash
# Convert using intuitive syntax
whyml convert --from manifest.yaml --to index.html -as html
whyml convert --from manifest.yaml --to App.tsx -as react
whyml convert --from manifest.yaml --to App.vue -as vue
whyml convert --from manifest.yaml --to app.html -as spa
whyml convert --from manifest.yaml --to pwa-app.html -as pwa

# With environment variables and configuration
whyml convert --from manifest.yaml --to app.html -as pwa --env-file .env --config pwa.json
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

### Legacy Commands (Still Supported)

```bash
# Validate manifest
whyml validate manifest.yaml

# Scrape website to manifest
whyml scrape https://example.com --output scraped-manifest.yaml

# Alternative server command (alias for run)
whyml serve -f manifest.yaml --port 3000 --watch
```

## API Server

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

## Testing

Run the comprehensive test suite:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=whyml --cov-report=html

# Run specific test modules
pytest tests/test_converters.py
pytest tests/test_manifest_loader.py
```


```
# ✅ Selective section generation - WORKS NOW!
whyml scrape https://example.com --section analysis --section metadata

# ✅ Structure simplification for refactoring
whyml scrape https://tom.sapletta.com --max-depth 3 --flatten-containers --simplify-structure

# ✅ Complete testing workflow with comparison
whyml scrape https://example.com --test-conversion --output-html regenerated.html

# ✅ Monitoring-friendly simple extraction  
whyml scrape https://blog.example.com --section analysis --max-depth 2
```


## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   YAML Input    │────│  Manifest Loader │────│ Manifest Processor│
│   • Files       │    │  • Async Loading │    │ • Template Vars  │
│   • URLs        │    │  • Dependency    │    │ • Validation     │
│   • Inheritance │    │    Resolution    │    │ • Optimization   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                          │
                       ┌──────────────────────────────────┴───────────────────┐
                       │                                                      │
┌─────────────────┐    │                                    ┌─────────────────┐
│   Converters    │────┤                                    │   Web Scrapers  │
│   • HTML        │    │                                    │   • URL Scraper │
│   • React       │    │          WhyML Core               │   • Page Analysis│
│   • Vue         │    │                                    │   • Structure   │
│   • PHP         │    │                                    │     Detection   │
└─────────────────┘    │                                    └─────────────────┘
                       │                                                      │
┌─────────────────┐    │                                    ┌─────────────────┐
│   CLI/API       │────┤                                    │   Output        │
│   • Commands    │    │                                    │   • Files       │
│   • FastAPI     │    │                                    │   • Validation  │
│   • Development │    │                                    │   • Optimization│
└─────────────────┘    └──────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

```bash
export WHYML_CACHE_SIZE=1000
export WHYML_CACHE_TTL=3600
export WHYML_DEFAULT_FORMAT=html
export WHYML_OUTPUT_DIR=./output
export WHYML_MANIFEST_DIR=./manifests
```

### Configuration File

```yaml
# whyml.config.yaml
cache:
  size: 1000
  ttl: 3600

conversion:
  optimize_output: true
  include_meta_tags: true
  css_framework: "bootstrap"

validation:
  strict_mode: false
  allow_unknown_properties: true

scraping:
  user_agent: "WhyML-Scraper/1.0"
  timeout: 30
  extract_styles: true
```

## 🧪 Testing

WhyML features a **comprehensive modular test suite** with **450+ test cases** across all packages:

### 📊 Modular Test Coverage

| Package | Test Files | Test Cases | Coverage |
|---------|-----------|------------|-----------|
| **whyml-core** | 4 files | 100+ tests | Validation, Loading, Processing, Utils |
| **whyml-scrapers** | 3 files | 80+ tests | URLScraper, WebpageAnalyzer, ContentExtractor |
| **whyml-converters** | 4 files | 120+ tests | HTML, React, Vue, PHP converters |
| **whyml-cli** | 3 files | 150+ tests | Commands, Workflows, Error handling |
| **Integration** | 1 file | End-to-end | Cross-package workflows |

### 🚀 Running Tests

```bash
# Run all tests across entire ecosystem
make test

# Run tests with coverage report
make test-coverage  

# Test specific modular packages
cd whyml-core && pytest tests/ -v
cd whyml-scrapers && pytest tests/ -v  
cd whyml-converters && pytest tests/ -v
cd whyml-cli && pytest tests/ -v

# Integration testing
pytest tests/test_modular_integration.py -v

# Performance benchmarks
pytest tests/ -k "performance" -v
```

### 🎯 Test Categories

- **🔧 Unit Tests**: Individual component functionality
- **🔗 Integration Tests**: Cross-package workflows  
- **⚡ Performance Tests**: Speed and memory benchmarks
- **🛡️ Error Handling**: Edge cases and failure scenarios
- **⌨️ CLI Tests**: Command-line interface validation
- **🌐 Network Tests**: Web scraping and external requests
- **🎭 End-to-End**: Complete pipeline validation

### ✅ Test Quality Metrics

- **450+ total test cases** across all modular packages
- **100% coverage** of critical path functionality
- **Async testing** for all async operations
- **Mock testing** for external dependencies
- **Parameterized tests** for multiple input scenarios
- **Property-based testing** for edge case discovery

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/dynapsys/whyml.git
cd whyml
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
pip install -r requirements-dev.txt
```

### Running Tests

```bash
pytest                          # Run all tests
pytest --cov=whyml             # With coverage
pytest -v tests/test_*.py       # Verbose output
pytest --benchmark-only         # Performance tests
```

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

## Changelog

### v1.0.0 (2024-01-15)
- Initial release
- Core manifest loading and processing
- HTML, React, Vue, PHP converters
- Web scraping capabilities
- Comprehensive test suite
- CLI and API interfaces

## Support

- 📖 [Documentation](https://whyml.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/dynapsys/whyml/issues)
- 💬 [Discussions](https://github.com/dynapsys/whyml/discussions)
- 📧 [Contact](mailto:info@softreck.dev)

---

<div align="center">
Made with ❤️ by <a href="https://softreck.dev">Tom Sapletta</a>
</div>
