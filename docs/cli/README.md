# WhyML CLI Commands

The WhyML Command Line Interface provides powerful tools for manifest processing, application generation, and development server management.

## 🚀 Quick Start

```bash
# Start development server
whyml run -f manifest.yaml --watch

# Convert manifest using natural language syntax
whyml convert --from manifest.yaml --to app.html -as pwa

# Generate application artifacts
whyml generate pwa -f manifest.yaml -o ./pwa-app
```

## 📋 Command Overview

| Command | Description | Example |
|---------|-------------|---------|
| [`run`](run.md) | Start development server | `whyml run -f manifest.yaml -p 8080` |
| [`serve`](run.md) | Alias for run command | `whyml serve --port 3000 --watch` |
| [`convert`](convert.md) | Convert manifest to different formats | `whyml convert --from manifest.yaml --to app.html -as spa` |
| [`generate`](generate.md) | Generate application artifacts | `whyml generate docker -f manifest.yaml` |
| [`validate`](validate.md) | Validate manifest files | `whyml validate manifest.yaml` |
| [`scrape`](scrape.md) | Convert websites to manifests | `whyml scrape https://example.com -o manifest.yaml` |

## 🎯 Natural Language Syntax

WhyML supports intuitive, natural language-like command syntax:

```bash
# Natural conversion syntax
whyml convert --from source.yaml --to output.html -as format

# Supported formats
whyml convert --from manifest.yaml --to app.html -as html      # HTML page
whyml convert --from manifest.yaml --to App.tsx -as react     # React component  
whyml convert --from manifest.yaml --to App.vue -as vue       # Vue component
whyml convert --from manifest.yaml --to app.php -as php       # PHP class
whyml convert --from manifest.yaml --to app.html -as spa      # Single Page App
whyml convert --from manifest.yaml --to app.html -as pwa      # Progressive Web App
```

## ⚙️ Global Options

```bash
whyml [GLOBAL_OPTIONS] <command> [COMMAND_OPTIONS]

Global Options:
  --version          Show WhyML version
  --verbose, -v      Enable verbose output
  --help            Show help message
```

## 🔧 Configuration

### Environment Variables

```bash
# Server configuration
export WHYML_HOST=localhost
export WHYML_PORT=8080
export WHYML_WATCH=true

# Application settings
export WHYML_DEFAULT_FORMAT=html
export WHYML_OUTPUT_DIR=./output
export WHYML_MANIFEST_DIR=./manifests
```

### Configuration Files

WhyML supports configuration via:
- `.env` files for environment variables
- `whyml.config.yaml` for application settings
- JSON/YAML config files for specific commands

### Example Config File

```yaml
# whyml.config.yaml
server:
  host: "localhost"
  port: 8080
  watch: true
  auto_reload: true

conversion:
  optimize_output: true
  include_meta_tags: true
  css_framework: "tailwind"

generation:
  pwa:
    theme_color: "#2196f3"
    background_color: "#ffffff"
  docker:
    node_version: "18-alpine"
    port: 8080
```

## 📱 Common Workflows

### Development Workflow

```bash
# 1. Create or edit your manifest
vim manifest.yaml

# 2. Validate the manifest
whyml validate manifest.yaml

# 3. Start development server with watching
whyml run -f manifest.yaml --watch

# 4. Test different formats
whyml convert --from manifest.yaml --to test.html -as spa
whyml convert --from manifest.yaml --to App.tsx -as react
```

### Production Deployment

```bash
# 1. Generate production artifacts
whyml generate pwa -f manifest.yaml -o ./dist
whyml generate docker -f manifest.yaml -o ./docker

# 2. Generate server configuration
whyml generate caddy -f manifest.yaml -o ./Caddyfile.json \
  --config '{"domain": "yourdomain.com", "tls_provider": "letsencrypt"}'

# 3. Deploy using generated configuration
docker-compose up -d
```

### Mobile App Development

```bash
# Generate Progressive Web App
whyml generate pwa -f manifest.yaml -o ./pwa

# Generate mobile app configuration (Capacitor)
whyml generate apk -f manifest.yaml -o ./mobile-app

# Generate desktop app (Tauri)
whyml generate tauri -f manifest.yaml -o ./desktop-app
```

## 🛠️ Advanced Usage

### Custom Configuration

```bash
# Use custom configuration file
whyml convert --from manifest.yaml --to app.html -as pwa --config pwa-config.json

# Use environment file
whyml convert --from manifest.yaml --to app.html -as spa --env-file .env.production
```

### Batch Processing

```bash
# Process multiple manifests
for manifest in manifests/*.yaml; do
  whyml convert --from "$manifest" --to "output/$(basename "$manifest" .yaml).html" -as spa
done
```

### Integration with CI/CD

```bash
# In your CI/CD pipeline
whyml validate manifest.yaml
whyml generate docker -f manifest.yaml -o ./dist
whyml generate caddy -f manifest.yaml -o ./Caddyfile.json
```

## 🔍 Debugging and Troubleshooting

### Verbose Output

```bash
# Enable verbose logging
whyml --verbose run -f manifest.yaml

# Debug specific conversions
whyml --verbose convert --from manifest.yaml --to debug.html -as pwa
```

### Common Issues

1. **Manifest Validation Errors**
   ```bash
   whyml validate manifest.yaml  # Check for syntax errors
   ```

2. **Server Won't Start**
   ```bash
   whyml --verbose run -f manifest.yaml  # Check for detailed errors
   ```

3. **Conversion Failures**
   ```bash
   # Test with minimal manifest
   whyml convert --from minimal.yaml --to test.html -as html
   ```

## 📚 See Also

- [whyml run](run.md) - Development server commands
- [whyml convert](convert.md) - Format conversion
- [whyml generate](generate.md) - Artifact generation
- [Manifest Format](../manifests/schema.md) - Manifest specification
- [Examples](../../examples/) - Usage examples
