# WhyML CLI

Unified command-line interface for the WhyML ecosystem. Scrape websites, convert manifests, validate configurations, and generate code - all from a single, powerful CLI tool.

## 🔧 Recent Updates (2025)

**✅ MAJOR FIX**: Resolved LoadedManifest conversion error that was preventing CLI convert commands from working properly. The CLI now correctly extracts `.content` from LoadedManifest objects before processing.

**✅ API COMPATIBILITY**: Fixed constructor parameters and method signatures to ensure compatibility with test suite and external usage patterns.

**✅ INSTALLATION VERIFIED**: All modular dependencies now install correctly with proper project name references (fixed EDPMT → WhyML).

## 🚀 Quick Start

### Installation

```bash
# Install CLI with core functionality
pip install whyml-cli

# Install with full ecosystem (recommended)
pip install whyml-cli[full]

# Install with specific functionality
pip install whyml-cli[scraping]     # Web scraping only
pip install whyml-cli[conversion]   # Code generation only
```

### Basic Usage

```bash
# Display help
whyml-cli --help

# Scrape a website to WhyML manifest
whyml-cli scrape https://example.com --output site.yaml

# Convert manifest to HTML
whyml-cli convert site.yaml --format html --output index.html

# Validate a manifest
whyml-cli validate site.yaml

# Generate a new React component
whyml-cli generate --format react --name UserProfile --typescript --output src/

# Show ecosystem information
whyml-cli info --all
```

## 📋 Available Commands

### `scrape` - Web Scraping

Convert websites to structured WhyML manifests with advanced scraping features:

```bash
# Basic scraping
whyml-cli scrape https://example.com --output manifest.yaml

# Advanced scraping with structure simplification
whyml-cli scrape https://example.com \
  --sections metadata structure styles \
  --max-depth 3 \
  --simplify \
  --flatten-containers

# Selective section extraction
whyml-cli scrape https://example.com \
  --sections metadata analysis \
  --output analysis.yaml

# Test conversion round-trip
whyml-cli scrape https://example.com \
  --test-conversion \
  --output-html regenerated.html
```

**Advanced Options:**
- `--sections`: Extract specific sections (metadata, structure, styles, scripts, analysis, imports)
- `--max-depth N`: Limit HTML nesting depth
- `--simplify`: Enable structure simplification
- `--flatten-containers`: Remove wrapper div containers
- `--preserve-semantic`: Keep HTML5 semantic elements
- `--extract-styles/--no-extract-styles`: CSS extraction control
- `--extract-scripts`: Include JavaScript code
- `--analyze-page/--no-analyze-page`: Page analysis control

### `convert` - Code Generation

Generate code from WhyML manifests in multiple formats:

```bash
# HTML generation
whyml-cli convert manifest.yaml --format html --output index.html

# React component with TypeScript
whyml-cli convert manifest.yaml \
  --format react \
  --typescript \
  --component-type functional \
  --css-in-js \
  --output App.tsx

# Vue.js Single File Component
whyml-cli convert manifest.yaml \
  --format vue \
  --composition-api \
  --typescript \
  --scoped-css \
  --output Component.vue

# PHP class with namespace
whyml-cli convert manifest.yaml \
  --format php \
  --namespace "App\\Pages" \
  --class-name HomePage \
  --output HomePage.php
```

**Format-Specific Options:**

**HTML:**
- `--html-version`: HTML version (5, html5, 4.01)
- `--semantic-structure`: Use semantic HTML5 elements
- `--css-framework`: CSS framework integration (bootstrap, tailwind, bulma)
- `--minify`: Minify HTML output

**React:**
- `--typescript`: Generate TypeScript code
- `--component-type`: functional or class components
- `--use-hooks`: Enable React Hooks
- `--css-in-js`: Use CSS-in-JS styling
- `--component-name`: Custom component name

**Vue:**
- `--composition-api/--options-api`: API style choice
- `--scoped-css`: Use scoped CSS
- `--css-preprocessor`: SCSS, Sass, Less, or Stylus

**PHP:**
- `--namespace`: PHP namespace
- `--class-name`: Custom class name
- `--procedural`: Use procedural style instead of classes
- `--php-version`: Target PHP version (7.4-8.3)
- `--strict-types`: Use strict type declarations

### `validate` - Manifest Validation

Validate WhyML manifests for correctness and completeness:

```bash
# Basic validation
whyml-cli validate manifest.yaml

# Strict validation mode
whyml-cli validate manifest.yaml --strict

# Validate multiple files with summary
whyml-cli validate *.yaml --summary

# Auto-fix common issues
whyml-cli validate manifest.yaml --fix-auto --fix-output fixed.yaml

# JSON output for automation
whyml-cli validate manifest.yaml --json-output
```

**Validation Options:**
- `--strict`: Enable strict validation mode
- `--schema`: Custom schema file
- `--check-inheritance/--no-check-inheritance`: Inheritance validation
- `--check-templates/--no-check-templates`: Template syntax validation
- `--check-variables/--no-check-variables`: Variable reference validation
- `--fix-auto`: Automatically fix common issues
- `--summary`: Show validation summary for multiple files
- `--json-output`: Output results in JSON format

### `generate` - Project Generation

Create new projects and components from templates:

```bash
# Generate from template
whyml-cli generate \
  --template basic-page \
  --name "My Homepage" \
  --output my-site/ \
  --template-vars author="John Doe" theme="dark"

# Generate component in specific format
whyml-cli generate \
  --format react \
  --name UserProfile \
  --typescript \
  --include-tests \
  --include-styles \
  --output src/components/

# Generate Vue component with full setup
whyml-cli generate \
  --format vue \
  --name ProductCard \
  --composition-api \
  --include-tests \
  --include-docs \
  --output src/components/
```

**Available Templates:**
- `basic-page`: Simple web page with header and content
- `blog-post`: Blog article with metadata and content structure
- `landing-page`: Marketing landing page with CTA sections

**Generation Options:**
- `--template`: Generate from predefined template
- `--format`: Generate component in specific format
- `--name`: Component/project name (required)
- `--description`: Description for generated content
- `--template-vars`: Template variables (KEY=VALUE format)
- `--include-styles`: Generate CSS/style files
- `--include-tests`: Generate test files
- `--include-docs`: Generate documentation files

### `info` - System Information

Display information about the WhyML ecosystem and system status:

```bash
# Show all information
whyml-cli info --all

# Show available formats
whyml-cli info --formats

# Show package status
whyml-cli info --packages

# Show system information
whyml-cli info --system

# JSON output for automation
whyml-cli info --all --json
```

## 🎯 Use Cases

### Website Migration
```bash
# 1. Scrape existing site
whyml-cli scrape https://old-site.com --output old-site.yaml

# 2. Convert to modern React
whyml-cli convert old-site.yaml --format react --typescript --output new-site/

# 3. Validate the result
whyml-cli validate old-site.yaml
```

### Component Library Development
```bash
# Generate base components
whyml-cli generate --format react --name Button --typescript --output src/components/
whyml-cli generate --format react --name Card --typescript --output src/components/
whyml-cli generate --format react --name Modal --typescript --output src/components/

# Convert design system manifests
whyml-cli convert button.yaml --format react --typescript --output src/Button/
whyml-cli convert card.yaml --format vue --composition-api --output src/Card/
```

### Multi-Framework Support
```bash
# Convert single manifest to multiple formats
whyml-cli convert app.yaml --format html --output dist/index.html
whyml-cli convert app.yaml --format react --typescript --output src/App.tsx
whyml-cli convert app.yaml --format vue --composition-api --output src/App.vue
whyml-cli convert app.yaml --format php --namespace "App" --output app/Page.php
```

### Quality Assurance
```bash
# Validate entire project
whyml-cli validate manifests/*.yaml --summary --json-output > validation-report.json

# Test conversion accuracy
whyml-cli scrape https://production-site.com --test-conversion --output-html test.html

# Auto-fix validation issues
whyml-cli validate manifest.yaml --fix-auto --fix-output fixed-manifest.yaml
```

## ⚙️ Configuration

### Configuration Files

WhyML CLI looks for configuration in these locations (in order):
1. `--config` command line option
2. `whyml.config.yaml` in current directory
3. `.whyml.yaml` in current directory
4. `~/.whyml/config.yaml` in home directory

### Sample Configuration

```yaml
# whyml.config.yaml
core:
  validation:
    strict_mode: true
    check_inheritance: true
  loading:
    cache_enabled: true
    cache_ttl: 3600

converters:
  html:
    semantic_structure: true
    css_framework: "bootstrap"
  react:
    typescript: true
    component_type: "functional"
  vue:
    composition_api: true
    scoped_css: true
  php:
    strict_types: true
    php_version: "8.1"

scraper:
  max_depth: 5
  simplify_structure: true
  preserve_semantic: true
  extract_styles: true
```

### Environment Variables

- `WHYML_CONFIG`: Path to configuration file
- `WHYML_DEBUG`: Enable debug output
- `WHYML_CACHE_DIR`: Custom cache directory

## 🧪 Testing

### Running Tests

```bash
# Install with test dependencies
pip install whyml-cli[test]

# Run all tests
pytest

# Run with coverage
pytest --cov=whyml_cli --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m cli           # CLI tests only
```

### Testing CLI Commands

```bash
# Test scraping functionality
whyml-cli scrape https://httpbin.org/html --output test.yaml
whyml-cli validate test.yaml

# Test conversion pipeline
whyml-cli convert test.yaml --format html --output test.html
whyml-cli convert test.yaml --format react --typescript --output Test.tsx

# Test generation
whyml-cli generate --template basic-page --name "Test Page" --output test-output/
```

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/dynapsys/whyml.git
cd whyml/whyml-cli

# Install in development mode
pip install -e .[dev,full]

# Run formatting and linting
black whyml_cli/
isort whyml_cli/
flake8 whyml_cli/
mypy whyml_cli/

# Run tests
pytest
```

### Adding New Commands

1. Create command class in `whyml_cli/commands/`
2. Extend `BaseCommand` class
3. Implement `register_parser()` and `execute()` methods
4. Add to `__init__.py` exports
5. Register in `cli.py`

### Adding New Output Formats

1. Install `whyml-converters` package
2. Create converter class extending `BaseConverter`
3. Register converter in CLI initialization
4. Add format validation to `validate_format()`

## 📚 Documentation

- **[WhyML Core](../whyml-core/)**: Core processing and validation engine
- **[WhyML Scrapers](../whyml-scrapers/)**: Web scraping and manifest generation
- **[WhyML Converters](../whyml-converters/)**: Multi-format code generation
- **[Main Project](../)**: Complete WhyML documentation

## 🔧 Troubleshooting

### Common Issues

**Command not found:**
```bash
# Ensure CLI is installed
pip install whyml-cli

# Check installation
whyml-cli --version
```

**Missing functionality:**
```bash
# Install full ecosystem
pip install whyml-cli[full]

# Check package status
whyml-cli info --packages
```

**Scraping fails:**
```bash
# Install scrapers package
pip install whyml-scrapers

# Check scraper availability
whyml-cli info --packages
```

**Conversion fails:**
```bash
# Install converters package
pip install whyml-converters

# Check available formats
whyml-cli info --formats
```

### Debug Mode

```bash
# Enable verbose output
whyml-cli --verbose <command>

# Enable debug output
whyml-cli --debug <command>

# Check system status
whyml-cli info --system
```

## 📄 License

Licensed under the Apache License, Version 2.0. See [LICENSE](../LICENSE) for details.

## 🔗 Related Projects

- **[whyml-core](../whyml-core/)**: Core processing and validation engine
- **[whyml-scrapers](../whyml-scrapers/)**: Web scraping and manifest generation
- **[whyml-converters](../whyml-converters/)**: Multi-format code generation
- **[whyml](../)**: Main WhyML package and ecosystem

---

**WhyML CLI** - Your unified gateway to the WhyML ecosystem. 🚀
