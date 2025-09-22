# WhyML Installation Guide

Choose the installation method that best fits your needs.

## 🚀 Complete Ecosystem (Recommended)

```bash
# Install complete WhyML ecosystem
pip install whyml
```

This installs all modular packages: `whyml-core`, `whyml-scrapers`, `whyml-converters`, and `whyml-cli`.

## 📦 Modular Installation (Targeted)

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

## 🔧 Development Installation

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

## System Requirements

- **Python**: 3.8+ (3.9+ recommended)
- **Operating System**: Linux, macOS, Windows
- **Memory**: 512MB+ available RAM
- **Disk Space**: 100MB for complete installation

## Optional Dependencies

### For Web Scraping
```bash
pip install selenium  # For dynamic content scraping
pip install playwright  # Alternative browser automation
```

### For Advanced Features
```bash
pip install docker  # For containerized deployments
pip install caddy  # For production web server
```

## Verification

After installation, verify everything works:

```bash
# Check CLI availability
whyml --version

# Verify all modules can be imported
python -c "import whyml; print('✓ WhyML installed successfully')"

# Run basic functionality test
whyml validate --help
```

## Troubleshooting

### Common Issues

**ModuleNotFoundError for whyml_***: Install modular packages
```bash
pip install whyml-core whyml-scrapers whyml-converters whyml-cli
```

**Permission denied during installation**: Use user installation
```bash
pip install --user whyml
```

**Python version compatibility**: Upgrade to Python 3.8+
```bash
python --version  # Should be 3.8+
```

### Development Setup Issues

**Editable install fails**: Install in correct order
```bash
pip install -e ./whyml-core  # Install core first
pip install -e ./whyml-scrapers
pip install -e ./whyml-converters  
pip install -e ./whyml-cli
pip install -e .  # Install main package last
```

## Next Steps

After successful installation:

1. Try the [Quick Start Guide](quick-start.md)
2. Read the [Getting Started Guide](getting-started.md)
3. Explore [Examples](../examples/)
