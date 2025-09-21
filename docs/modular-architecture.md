# 🏗️ WhyML Modular Architecture Guide

## Overview

WhyML has been completely refactored into a **modular ecosystem** of specialized packages, providing better maintainability, testing, and deployment flexibility. This guide explains the architecture, benefits, and usage patterns of the modular system.

## 📦 Core Packages

### whyml-core
**Purpose**: Core functionality for manifest loading, validation, processing, and utilities

**Key Components**:
- `whyml_core.loading.manifest_loader.ManifestLoader` - Async manifest loading with dependency resolution
- `whyml_core.validation.manifest_validator.ManifestValidator` - Schema validation and error reporting
- `whyml_core.processing.manifest_processor.ManifestProcessor` - Template processing and inheritance
- `whyml_core.exceptions.*` - Comprehensive exception hierarchy
- `whyml_core.utils.*` - YAML, async, path, and string utilities

**Usage**:
```python
from whyml_core.loading.manifest_loader import ManifestLoader
from whyml_core.processing.manifest_processor import ManifestProcessor

async with ManifestLoader() as loader:
    manifest = await loader.load_manifest('manifest.yaml')
    
processor = ManifestProcessor()
processed = processor.process_manifest(manifest)
```

**Installation**: `pip install whyml-core`

### whyml-scrapers
**Purpose**: Web scraping and webpage analysis capabilities

**Key Components**:
- `whyml_scrapers.url_scraper.URLScraper` - Advanced web scraping with structure simplification
- `whyml_scrapers.webpage_analyzer.WebpageAnalyzer` - Page analysis, SEO metrics, accessibility checks
- `whyml_scrapers.content_extractor.ContentExtractor` - Content extraction and processing
- `whyml_scrapers.structure_analyzer.StructureAnalyzer` - HTML structure analysis and optimization

**Features**:
- Structure simplification (max-depth, container flattening)
- Selective section generation (metadata, analysis, structure, styles)
- Page type detection (blog, e-commerce, landing page, etc.)
- SEO and accessibility analysis
- Content similarity comparison for testing

**Usage**:
```python
from whyml_scrapers.url_scraper import URLScraper

scraper = URLScraper()
async with scraper:
    manifest = await scraper.scrape_url(
        'https://example.com',
        max_depth=3,
        flatten_containers=True,
        sections=['metadata', 'structure']
    )
```

**Installation**: `pip install whyml-scrapers`

### whyml-converters
**Purpose**: Multi-format conversion (HTML, React, Vue, PHP)

**Key Components**:
- `whyml_converters.html_converter.HTMLConverter` - Semantic HTML generation
- `whyml_converters.react_converter.ReactConverter` - React/JSX/TSX components
- `whyml_converters.vue_converter.VueConverter` - Vue 3 SFC with Composition API
- `whyml_converters.php_converter.PHPConverter` - PHP pages with security features

**Features**:
- **HTML**: Semantic markup, CSS framework integration, SEO optimization
- **React**: Functional/class components, TypeScript, hooks, styled-components
- **Vue**: Vue 3 SFC, Composition/Options API, Pinia integration, TypeScript
- **PHP**: Secure pages, database integration, session management, framework support

**Usage**:
```python
from whyml_converters.react_converter import ReactConverter

converter = ReactConverter(
    use_typescript=True,
    component_type='functional',
    css_framework='tailwind'
)
result = converter.convert(manifest)
result.save_to_file('Component.tsx')
```

**Installation**: `pip install whyml-converters`

### whyml-cli
**Purpose**: Unified command-line interface integrating all packages

**Key Commands**:
- `whyml scrape` - Web scraping with advanced options
- `whyml convert` - Format conversion between HTML/React/Vue/PHP
- `whyml validate` - Manifest validation and schema checking
- `whyml generate` - Application generation (PWA, SPA, etc.)
- `whyml info` - System information and package status

**Features**:
- Comprehensive CLI with 150+ test cases
- Advanced scraping flags (--max-depth, --flatten-containers, --section)
- Multi-format conversion workflows
- Batch processing and automation support
- Integration with all modular packages

**Usage**:
```bash
# Advanced scraping
whyml scrape https://example.com --max-depth 3 --section metadata --section structure

# Multi-format conversion
whyml convert manifest.yaml --format react --typescript --output Component.tsx

# Validation
whyml validate manifest.yaml --strict

# Application generation
whyml generate pwa --manifest manifest.yaml --output ./pwa-app
```

**Installation**: `pip install whyml-cli`

### whyml (Main Package)
**Purpose**: Orchestrates all modular packages, provides unified interface

**Key Components**:
- `whyml.processor.WhyMLProcessor` - Main processor integrating all modules
- `whyml.api_handlers.*` - FastAPI handlers for REST API
- `whyml.server.WhyMLServer` - Development server with hot reload
- Unified imports from all modular packages

**Usage**:
```python
from whyml import WhyMLProcessor

processor = WhyMLProcessor()
html_result = await processor.convert_to_html('manifest.yaml')
react_result = await processor.convert_to_react('manifest.yaml')
```

**Installation**: `pip install whyml` (includes all dependencies)

## 🎯 Architecture Benefits

### 1. **Modular Installation**
Install only what you need:
```bash
# Minimal core functionality
pip install whyml-core

# Core + scraping
pip install whyml-core whyml-scrapers

# CLI interface (includes all dependencies)
pip install whyml-cli
```

### 2. **Independent Development**
- Each package has its own version, tests, and documentation
- Clear separation of concerns
- Independent release cycles
- Easier maintenance and debugging

### 3. **Comprehensive Testing**
- **450+ test cases** across all packages
- **Modular test suites** for each component
- **Integration tests** for cross-package workflows
- **Performance benchmarks** and **error handling tests**

### 4. **Scalable Architecture**
- Easy to extend with new converters or scrapers
- Plugin-friendly CLI system
- Async-first design for performance
- Clean dependency management

## 🔄 Package Dependencies

```
whyml (main package)
├── whyml-core (required)
├── whyml-scrapers (optional)
├── whyml-converters (optional)
└── whyml-cli (optional)

whyml-cli
├── whyml-core (required)
├── whyml-scrapers (required)
├── whyml-converters (required)
└── click, rich (CLI dependencies)

whyml-converters
└── whyml-core (required)

whyml-scrapers
├── whyml-core (required)
└── aiohttp, beautifulsoup4, lxml (scraping dependencies)

whyml-core
└── pyyaml, jinja2, pydantic (core dependencies)
```

## 🚀 Usage Patterns

### Pattern 1: Complete Ecosystem
Best for full-featured applications:
```python
from whyml import WhyMLProcessor

processor = WhyMLProcessor()
# Access to all functionality
```

### Pattern 2: Targeted Functionality
Best for specific use cases:
```python
from whyml_core.loading.manifest_loader import ManifestLoader
from whyml_converters.html_converter import HTMLConverter

# Only load what you need
```

### Pattern 3: CLI-First Workflow
Best for automation and scripting:
```bash
whyml scrape https://example.com | whyml convert --format react --output Component.tsx
```

### Pattern 4: Custom Integration
Best for embedding in larger applications:
```python
from whyml_scrapers.url_scraper import URLScraper
from whyml_converters.vue_converter import VueConverter

# Custom pipeline with specific components
```

## 🧪 Testing Strategy

### Package-Level Testing
Each package has comprehensive test suites:
- **whyml-core**: 100+ tests (validation, loading, processing, utils)
- **whyml-scrapers**: 80+ tests (scraping, analysis, extraction)
- **whyml-converters**: 120+ tests (HTML, React, Vue, PHP conversion)
- **whyml-cli**: 150+ tests (commands, workflows, error handling)

### Integration Testing
Cross-package workflows tested in `tests/test_modular_integration.py`:
- Core → Scrapers → Converters → CLI pipelines
- Error propagation and handling
- Performance across package boundaries
- Dependency resolution and compatibility

### Running Tests
```bash
# All packages
make test

# Specific package
cd whyml-core && pytest tests/ -v

# Integration tests
pytest tests/test_modular_integration.py -v

# Performance benchmarks
pytest tests/ -k "performance" -v
```

## 📈 Migration Guide

### From Legacy WhyML
If you're upgrading from the pre-modular WhyML:

1. **Update imports**:
   ```python
   # Old
   from whyml.manifest_loader import ManifestLoader
   
   # New (modular)
   from whyml_core.loading.manifest_loader import ManifestLoader
   
   # Or (unified)
   from whyml import ManifestLoader
   ```

2. **Install dependencies**:
   ```bash
   # Complete ecosystem
   pip install whyml
   
   # Or targeted packages
   pip install whyml-core whyml-converters
   ```

3. **Update CLI usage**:
   ```bash
   # CLI commands remain the same
   whyml scrape https://example.com --output manifest.yaml
   whyml convert manifest.yaml --format html --output result.html
   ```

## 🎯 Best Practices

### 1. **Choose the Right Installation**
- **Development/Full-featured apps**: `pip install whyml`
- **Specific functionality**: `pip install whyml-core whyml-converters`
- **CLI-only usage**: `pip install whyml-cli`

### 2. **Async Context Managers**
Always use async context managers for resource management:
```python
async with ManifestLoader() as loader:
    manifest = await loader.load_manifest('manifest.yaml')

async with URLScraper() as scraper:
    scraped = await scraper.scrape_url('https://example.com')
```

### 3. **Error Handling**
Use package-specific exceptions:
```python
from whyml_core.exceptions.validation_exceptions import ManifestValidationError
from whyml_scrapers.exceptions import ScrapingError

try:
    manifest = await loader.load_manifest('manifest.yaml')
except ManifestValidationError as e:
    print(f"Validation error: {e}")
except ScrapingError as e:
    print(f"Scraping error: {e}")
```

### 4. **Performance Optimization**
- Use caching for repeated operations
- Leverage async operations for I/O bound tasks
- Enable performance monitoring in production

## 🔮 Future Roadmap

### Planned Packages
- **whyml-plugins**: Plugin system for extensibility
- **whyml-templates**: Template marketplace and management
- **whyml-analytics**: Usage analytics and optimization
- **whyml-deploy**: Deployment automation and CI/CD

### Enhanced Features
- **Real-time collaboration** on manifest editing
- **Visual manifest editor** with drag-and-drop
- **Machine learning** for automated optimization
- **Multi-language support** for international projects

---

This modular architecture positions WhyML as a scalable, maintainable, and extensible ecosystem for modern web development workflows.
