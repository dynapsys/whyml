# WhyML Installation and Setup Guide

## Overview

WhyML is a powerful CLI tool for converting manifests to various application formats including PWAs, SPAs, mobile apps, and more. This guide provides comprehensive installation and setup instructions.

## Prerequisites

- **Python 3.8+** (tested with Python 3.8, 3.9, 3.10, 3.11)
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **Virtual environment support** (recommended)

## Installation Methods

### Method 1: Development Installation (Recommended)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/dynapsys/whyml.git
   cd whyml
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On Linux/macOS:
   source venv/bin/activate
   
   # On Windows:
   # venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   # Install all required dependencies
   pip install -r requirements.txt
   
   # Install WhyML in editable mode
   pip install -e .
   ```

4. **Verify Installation**
   ```bash
   whyml --help
   whyml --version
   ```

### Method 2: Direct pip Installation (Future)

```bash
# This will be available when published to PyPI
pip install whyml
```

## Quick Start

### 1. Validate a Manifest

```bash
whyml validate test-manifest.yaml
```

### 2. Convert to HTML

```bash
whyml convert --from test-manifest.yaml --to output.html -as html
```

### 3. Generate PWA Application

```bash
whyml generate pwa -f test-manifest.yaml -o ./my-pwa
```

### 4. Start Development Server

```bash
whyml serve -f test-manifest.yaml -p 8080
```

## CLI Commands Overview

WhyML provides several powerful CLI commands:

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `validate` | Validate manifest files | `whyml validate manifest.yaml` |
| `convert` | Convert manifests to various formats | `whyml convert --from manifest.yaml --to app.html -as html` |
| `generate` | Generate complete application artifacts | `whyml generate pwa -f manifest.yaml -o ./pwa-app` |
| `serve` | Start development server | `whyml serve -f manifest.yaml -p 8080` |
| `run` | Start production server with Caddy | `whyml run -f manifest.yaml --tls-provider letsencrypt` |
| `scrape` | Scrape websites to generate manifests | `whyml scrape https://example.com -o manifest.yaml` |

### Conversion Formats

| Format | Description | File Extension |
|--------|-------------|----------------|
| `html` | Static HTML application | `.html` |
| `react` | React JSX component | `.jsx` |
| `vue` | Vue single-file component | `.vue` |
| `php` | PHP application | `.php` |

### Artifact Generation

| Type | Description | Output |
|------|-------------|---------|
| `pwa` | Progressive Web App | Complete PWA with service worker, manifest, offline page |
| `spa` | Single Page Application | SPA with router and navigation |
| `docker` | Docker configuration | Dockerfile, docker-compose.yml, .dockerignore |
| `tauri` | Desktop application | Rust-based desktop app with web frontend |
| `apk` | Mobile application | Capacitor project for Android/iOS |
| `caddy` | Production server config | Caddy reverse proxy configuration |

## Configuration

### Environment Variables

WhyML supports environment variables and `.env` files:

```bash
# Create .env file
echo "API_URL=https://api.example.com" > .env
echo "APP_NAME=MyApp" >> .env

# Use in conversion
whyml convert --from manifest.yaml --to app.html -as html --env-file .env
```

### Configuration Files

You can use JSON or YAML configuration files:

```yaml
# config.yaml
cache_size: 2000
cache_ttl: 7200
enable_validation: true
optimize_output: true
```

```bash
whyml convert --from manifest.yaml --to app.html -as html --config config.yaml
```

## Manifest Format

WhyML uses YAML-based manifests with the following structure:

```yaml
metadata:
  title: "My Application"
  description: "A sample application"
  version: "1.0.0"
  author: "Your Name"

structure:
  - element: "div"
    class: "header"
    content: "Welcome to My App"
    children:
      - element: "nav"
        class: "navigation"
        content: "Navigation"

styles:
  - selector: ".header"
    properties:
      background-color: "#007bff"
      color: "white"
      padding: "20px"
  - selector: ".navigation"
    properties:
      margin: "10px 0"
```

## Advanced Usage

### 1. PWA Generation with Custom Config

```bash
whyml generate pwa -f manifest.yaml -o ./my-pwa --config pwa-config.yaml
```

### 2. Production Deployment with Caddy

```bash
# Generate Caddy configuration
whyml run -f manifest.yaml --caddy-config Caddyfile --tls-provider letsencrypt

# Start with custom domain
whyml run -f manifest.yaml --host myapp.com --tls-provider letsencrypt
```

### 3. Development with Auto-reload

```bash
whyml serve -f manifest.yaml --watch -p 3000
```

### 4. Batch Processing

```bash
# Convert multiple formats
whyml convert --from manifest.yaml --to app.html -as html
whyml convert --from manifest.yaml --to app.jsx -as react
whyml convert --from manifest.yaml --to app.vue -as vue
whyml convert --from manifest.yaml --to app.php -as php
```

## Troubleshooting

### Common Issues

1. **Virtual Environment Issues**
   ```bash
   # Deactivate and recreate if needed
   deactivate
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Port Already in Use**
   ```bash
   # Use different port
   whyml serve -f manifest.yaml -p 8081
   ```

3. **Permission Errors**
   ```bash
   # Ensure proper permissions
   chmod +x $(which whyml)
   ```

4. **Import Errors**
   ```bash
   # Reinstall dependencies
   pip install --force-reinstall -r requirements.txt
   ```

### Validation Errors

- Ensure your manifest includes required `structure` property
- Check YAML syntax with online validators
- Use `whyml validate` to identify specific issues

### Performance Tips

- Use `--optimize-output` for production builds
- Enable caching for repeated operations
- Use `.env` files for configuration management

## Development and Contribution

### Setting up Development Environment

```bash
# Clone and setup
git clone https://github.com/dynapsys/whyml.git
cd whyml
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .

# Run tests
python -m pytest tests/

# Run with development dependencies
pip install -r requirements-dev.txt
```

### Project Structure

```
whyml/
├── whyml/              # Main package
│   ├── __init__.py
│   ├── cli.py          # CLI interface
│   ├── processor.py    # Main processing logic
│   ├── generators.py   # Code generators
│   ├── server.py       # Development server
│   ├── caddy.py        # Caddy integration
│   └── converters/     # Format converters
├── tests/              # Test suite
├── docs/               # Documentation
├── examples/           # Usage examples
└── requirements.txt    # Dependencies
```

## Support and Resources

- **Documentation**: `/docs` directory
- **Examples**: `/examples` directory
- **Issues**: GitHub Issues
- **Contributing**: See CONTRIBUTING.md

## Version Information

- **Current Version**: 0.1.0
- **Python Support**: 3.8+
- **License**: MIT
- **Status**: Active Development

---

**Happy building with WhyML!** 🚀
