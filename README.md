# WhyML - Modular YAML Manifest Ecosystem

```bash
 ██╗    ██╗██╗  ██╗██╗   ██╗███╗   ███╗██╗     
 ██║    ██║██║  ██║╚██╗ ██╔╝████╗ ████║██║     
 ██║ █╗ ██║███████║ ╚████╔╝ ██╔████╔██║██║     
 ██║███╗██║██╔══██║  ╚██╔╝  ██║╚██╔╝██║██║     
 ╚███╔███╔╝██║  ██║   ██║   ██║ ╚═╝ ██║███████╗
  ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝╚══════╝
```

**🏗️ Transform websites into maintainable YAML manifests and generate multi-format applications**

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-127_collected_117_passing-brightgreen.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-85%25+-brightgreen.svg)](#testing)
[![Modular](https://img.shields.io/badge/architecture-modular-blue.svg)](#modular-architecture)

## 🚀 Quick Start

```bash
# Install WhyML ecosystem
pip install whyml whyml-cli whyml-core whyml-converters whyml-scrapers

# Scrape a website to YAML manifest
whyml scrape https://example.com -o data/manifest.yaml

# Convert to multiple formats
whyml convert data/manifest.yaml --format html -o output.html
whyml convert data/manifest.yaml --format react -o Component.tsx
whyml convert data/manifest.yaml --format vue -o Component.vue
```

**📖 [Complete Installation Guide →](INSTALLATION.md)**

## 📚 Documentation

### 🏁 Getting Started
- **[📖 Installation Guide](INSTALLATION.md)** - Complete setup instructions
- **[🚀 Quick Start](docs/getting-started.md)** - Get running in 5 minutes
- **[🎯 Examples](examples/)** - Real-world usage examples

### 📋 Core Documentation
- **[📝 Manifest Reference](docs/manifest-reference.md)** - YAML specification
- **[🔄 Converters Guide](docs/converters.md)** - Multi-format conversion
- **[🕷️ Advanced Scraping](docs/advanced-scraping.md)** - Web scraping features
- **[🔧 CLI Reference](docs/cli/README.md)** - Command-line interface
- **[🌐 API Reference](docs/api-reference.md)** - Python & REST API

## 🏗️ Modular Architecture

WhyML is built as a **modular ecosystem** of specialized packages:

### 📦 Core Packages

- **`whyml-core`** - Core functionality (validation, loading, processing, utilities)
- **`whyml-scrapers`** - Web scraping and analysis capabilities  
- **`whyml-converters`** - Multi-format conversion (HTML, React, Vue, PHP)
- **`whyml-cli`** - Unified command-line interface
- **`whyml`** - Main package orchestrating all modules
  
**📖 [View Modular Package Documentation →](whyml-core/README.md) | [whyml-converters →](whyml-converters/README.md) | [whyml-scrapers →](whyml-scrapers/README.md) | [whyml-cli →](whyml-cli/README.md)**

### 🎯 Key Features

- 🚀 **Multi-Format Conversion**: Generate HTML, React, Vue, and PHP from YAML manifests
- 🕷️ **Advanced Web Scraping**: Intelligent website-to-manifest conversion with structure simplification
- 🔗 **Template Inheritance**: Advanced inheritance system with dependency resolution
- ⚡ **Async Processing**: High-performance asynchronous manifest loading and processing
- 🧪 **Comprehensive Testing**: 127+ test cases with 85%+ coverage across all packages
- 🛠️ **CLI & API**: Command-line interface and FastAPI server for integration

## ⚡ Example YAML Manifest

```yaml
metadata:
  title: "Landing Page"
  description: "Modern landing page component"
  version: "1.0.0"

template_vars:
  hero_text: "Welcome to Our Product"
  cta_text: "Get Started"

styles:
  hero:
    background: "linear-gradient(135deg, #007bff, #0056b3)"
    padding: "80px 0"
    text-align: "center"
    color: "white"

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
          - button:
              text: "{{ cta_text }}"
              class: "btn btn-success btn-lg"
```

**📁 [View More Examples →](examples/) | [Data Samples →](data/)**

## 🚀 Development

### Testing

Each package includes comprehensive testing with Makefiles:

```bash
# Test specific packages
cd whyml-core && make test
cd whyml-converters && make test-coverage
cd whyml-scrapers && make test-watch
cd whyml-cli && make test-integration

# Test all packages
make test
```

### Building & Publishing

```bash
# Build specific packages
cd whyml-converters && make build
cd whyml-core && make publish-test

# Clean all packages
find . -name "Makefile" -execdir make clean \;
```

## 🧪 Testing & Development

### Current Status
- **127+ test cases** across all modular packages
- **117+ passing** tests (85%+ coverage)
- Each package includes dedicated Makefiles with test targets

### Package Development
```bash
# Individual package development
cd whyml-core && make test-coverage
cd whyml-converters && make test-html test-react test-vue test-php
cd whyml-scrapers && make test-scraper test-analyzer
cd whyml-cli && make test-integration

# Cross-package integration testing
make test
```

**📖 [Complete Testing Guide →](TEST.md)**

## 📄 Contributing & License

### Development Setup
```bash
git clone https://github.com/dynapsys/whyml.git
cd whyml
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Contributing
We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### License
Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

---

### 📞 Support & Links

- 📖 **[Complete Documentation →](docs/)**
- 🐛 **[Issue Tracker →](https://github.com/dynapsys/whyml/issues)**
- 💬 **[Discussions →](https://github.com/dynapsys/whyml/discussions)**
- 📧 **[Contact →](mailto:info@softreck.dev)**

---

<div align="center">

**⭐ Star this repo if WhyML helps you build better applications!**

Made with ❤️ by [Tom Sapletta](https://softreck.dev)
</div>
