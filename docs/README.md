# WhyML Documentation

Welcome to the comprehensive WhyML documentation. This directory contains detailed guides, API references, and examples for using WhyML - the Advanced YAML Manifest System.

## 📚 Documentation Structure

### Getting Started
- [Installation Guide](installation.md) - Install and set up WhyML
- [Quick Start](quickstart.md) - Get up and running in minutes
- [Basic Concepts](concepts.md) - Understand WhyML fundamentals

### CLI Reference
- [CLI Commands](cli/README.md) - Complete CLI command reference
- [whyml run](cli/run.md) - Development server commands
- [whyml convert](cli/convert.md) - Format conversion commands  
- [whyml generate](cli/generate.md) - Artifact generation commands

### Manifest Format
- [Manifest Schema](manifests/schema.md) - Complete manifest specification
- [Template Variables](manifests/templates.md) - Using variables and templating
- [Inheritance](manifests/inheritance.md) - Template inheritance system
- [Styling](manifests/styling.md) - CSS and style management

### Converters
- [HTML Converter](converters/html.md) - Generate semantic HTML
- [React Converter](converters/react.md) - Create React components
- [Vue Converter](converters/vue.md) - Generate Vue.js components  
- [PHP Converter](converters/php.md) - Generate PHP classes

### Application Generation
- [Progressive Web Apps (PWA)](generators/pwa.md) - Build PWAs
- [Single Page Applications (SPA)](generators/spa.md) - Create SPAs
- [Mobile Apps (APK)](generators/apk.md) - Generate mobile apps
- [Desktop Apps (Tauri)](generators/tauri.md) - Build desktop applications
- [Docker Containers](generators/docker.md) - Containerization

### Server & Deployment
- [Development Server](server/development.md) - Local development setup
- [Production Deployment](server/production.md) - Production configurations
- [Caddy Integration](server/caddy.md) - Web server setup
- [Environment Configuration](server/environment.md) - Environment management

### Advanced Topics
- [Web Scraping](advanced/scraping.md) - Website to manifest conversion
- [API Integration](advanced/api.md) - REST API and WebSocket support
- [Real-time Features](advanced/realtime.md) - Live reload and collaboration
- [Custom Extensions](advanced/extensions.md) - Extend WhyML functionality

### Examples & Tutorials
- [Basic Examples](../examples/) - Simple usage examples
- [Advanced Tutorials](tutorials/) - Step-by-step guides
- [Sample Projects](samples/) - Complete project examples
- [Best Practices](best-practices.md) - Recommended patterns

### API Reference
- [Python API](api/python.md) - Python library reference
- [REST API](api/rest.md) - HTTP API endpoints
- [WebSocket API](api/websocket.md) - Real-time communication

### Contributing
- [Development Guide](contributing/development.md) - Set up development environment
- [Architecture Overview](contributing/architecture.md) - System design
- [Testing Guide](contributing/testing.md) - Running and writing tests

## 🚀 Quick Navigation

### New to WhyML?
1. Start with [Installation Guide](installation.md)
2. Follow the [Quick Start](quickstart.md)
3. Try the [Basic Examples](../examples/basic-usage.sh)

### Building Applications?
- **Web Apps**: [PWA Guide](generators/pwa.md) → [SPA Guide](generators/spa.md)
- **Mobile Apps**: [APK Generation](generators/apk.md)
- **Desktop Apps**: [Tauri Guide](generators/tauri.md)
- **Deployment**: [Production Guide](server/production.md)

### Converting Existing Code?
- **From HTML**: [Web Scraping](advanced/scraping.md)
- **To React**: [React Converter](converters/react.md)
- **To Vue**: [Vue Converter](converters/vue.md)

### Need Help?
- 📖 [API Reference](api/)
- 💬 [Discussions](https://github.com/dynapsys/whyml/discussions)
- 🐛 [Issue Tracker](https://github.com/dynapsys/whyml/issues)

## 📱 Command Quick Reference

```bash
# Development server
whyml run -f manifest.yaml --watch

# Convert formats  
whyml convert --from manifest.yaml --to output.html -as spa

# Generate applications
whyml generate pwa -f manifest.yaml -o ./pwa-app
whyml generate docker -f manifest.yaml -o ./docker-config

# Production deployment
whyml run -f manifest.yaml --port 443 --host yourdomain.com --tls-provider letsencrypt
```

## 🔗 External Resources

- [WhyML GitHub Repository](https://github.com/dynapsys/whyml)
- [PyPI Package](https://pypi.org/project/whyml/)
- [Community Examples](https://github.com/dynapsys/whyml-examples)
- [Video Tutorials](https://youtube.com/playlist?list=whyml-tutorials)

---

**Last Updated**: January 2025 | **Version**: 1.0.1+ | **License**: Apache 2.0
