# WhyML Comprehensive Tutorials

Welcome to the complete WhyML tutorial series! These step-by-step guides will take you from basic web scraping to advanced cross-platform application development.

## 📚 Tutorial Series Overview

| Tutorial | Topic | Difficulty | Duration | Technologies |
|----------|-------|------------|----------|-------------|
| [01](01-multipage-html-php-docker.md) | Multi-page HTML sites with PHP & Docker | ⭐⭐ | 2-3 hours | HTML, PHP, Docker, YAML |
| [02](02-svg-generation-datauri-php-docker.md) | SVG generation with DataURI & PHP | ⭐⭐⭐ | 2-3 hours | SVG, DataURI, PHP, Docker |
| [03](03-tauri-app-creation.md) | Tauri desktop applications | ⭐⭐⭐ | 3-4 hours | Rust, Tauri, JavaScript |
| [04](04-react-vue-pwa-spa-workflow.md) | Modern web apps (React/Vue/PWA/SPA) | ⭐⭐⭐⭐ | 4-5 hours | React, Vue, PWA, Docker |
| [05](05-android-windows-linux-app-creation.md) | Cross-platform mobile & desktop apps | ⭐⭐⭐⭐⭐ | 5-6 hours | Android, Electron, Docker |

## 🚀 Quick Start Guide

### Prerequisites
Before starting any tutorial, ensure you have:

```bash
# Install WhyML
pip install whyml

# Verify installation
whyml --version

# Basic usage
whyml scrape https://example.com --output example.yaml
```

### Required Tools
- **Python 3.8+** with WhyML installed
- **Docker & Docker Compose** (recommended for all tutorials)
- **Node.js 18+** (for tutorials 3-5)
- **Git** (for version control)

### Optional Tools (per tutorial)
- **PHP 8+** (tutorials 1-2)
- **Rust & Cargo** (tutorial 3)
- **Android SDK** (tutorial 5)

## 📖 Tutorial Descriptions

### 🌐 Tutorial 1: Multi-page HTML Site with PHP Integration
**File:** [01-multipage-html-php-docker.md](01-multipage-html-php-docker.md)

Learn to create complete multi-page websites using WhyML's YAML dependency system.

**What you'll build:**
- Multi-page website with navigation
- YAML component system
- PHP dynamic content
- Docker deployment setup

**Key concepts:**
- `{{EXTERNAL:filename}}` syntax
- Component reusability
- Variable substitution
- Docker containerization

**Example command:**
```bash
whyml convert manifests/site.yaml --output output/
docker-compose up --build
```

### 🎨 Tutorial 2: SVG Generation with DataURI Media
**File:** [02-svg-generation-datauri-php-docker.md](02-svg-generation-datauri-php-docker.md)

Create interactive SVG applications with embedded media and PHP backends.

**What you'll build:**
- Dynamic SVG interfaces
- DataURI image embedding
- Interactive menu systems
- PHP-powered backend

**Key concepts:**
- `{{DATAURI:path}}` syntax
- SVG interactivity
- Base64 media encoding
- Offline-capable apps

**Example command:**
```bash
whyml convert manifests/svg-app.yaml --output output/
# Images automatically converted to DataURI
```

### 🖥️ Tutorial 3: Tauri Desktop Applications
**File:** [03-tauri-app-creation.md](03-tauri-app-creation.md)

Convert scraped web content into native desktop applications using Tauri.

**What you'll build:**
- Cross-platform desktop app
- Native system integration
- Modern UI with web technologies
- Rust-powered backend

**Key concepts:**
- Web-to-desktop conversion
- Tauri configuration
- Native API access
- Cross-platform packaging

**Example command:**
```bash
whyml scrape https://example.com --output scraped.yaml
# Generate Tauri app from scraped content
npm run tauri:build
```

### ⚛️ Tutorial 4: Modern Web Applications (React/Vue/PWA/SPA)
**File:** [04-react-vue-pwa-spa-workflow.md](04-react-vue-pwa-spa-workflow.md)

Build modern web applications across multiple frameworks from a single manifest.

**What you'll build:**
- React application with hooks
- Vue 3 with Composition API
- Progressive Web App (PWA)
- Single Page Application (SPA)

**Key concepts:**
- Multi-framework generation
- Component architecture
- State management
- PWA features (offline, installable)

**Example commands:**
```bash
whyml convert manifests/react-app.yaml --framework react --output apps/react-app/
whyml convert manifests/vue-app.yaml --framework vue --output apps/vue-app/
whyml convert manifests/pwa-config.yaml --type pwa --output apps/pwa-app/
```

### 📱 Tutorial 5: Cross-platform Mobile & Desktop Applications
**File:** [05-android-windows-linux-app-creation.md](05-android-windows-linux-app-creation.md)

Create applications for Android, Windows, and Linux from unified manifests.

**What you'll build:**
- Android APK application
- Windows desktop executable
- Linux packages (AppImage, Deb, RPM, Snap)
- Complete CI/CD pipeline

**Key concepts:**
- Cross-platform manifests
- Native platform integration
- Build pipeline automation
- Distribution packaging

**Example commands:**
```bash
# Build Android APK
./scripts/build-android.sh

# Build Windows app
./scripts/build-windows.sh

# Build all Linux formats
./scripts/build-linux.sh

# Build everything
./scripts/deploy-all.sh
```

## 🛠️ Common Workflows

### Workflow 1: Website to Mobile App
```bash
# 1. Scrape existing website
whyml scrape https://your-website.com --output scraped/site.yaml

# 2. Convert to Android app manifest
whyml convert scraped/site.yaml --platform android --output manifests/app.yaml

# 3. Build Android APK
./scripts/build-android.sh

# Result: Native Android app from your website
```

### Workflow 2: Multi-format Generation
```bash
# 1. Create base manifest
whyml convert manifests/base-app.yaml --output output/

# 2. Generate multiple formats
whyml convert manifests/base-app.yaml --format react --output apps/react/
whyml convert manifests/base-app.yaml --format vue --output apps/vue/
whyml convert manifests/base-app.yaml --format pwa --output apps/pwa/

# 3. Deploy all formats
docker-compose up --build
```

### Workflow 3: Full Development Pipeline
```bash
# 1. Scrape and analyze
whyml scrape https://source-site.com \
  --section metadata \
  --section analysis \
  --section structure \
  --section styles \
  --output scraped.yaml

# 2. Generate multi-platform apps
whyml convert scraped.yaml --platform android --output android/
whyml convert scraped.yaml --platform desktop --output desktop/
whyml convert scraped.yaml --platform web --output web/

# 3. Build and deploy
./scripts/deploy-all.sh
```

## 🐳 Docker Integration

All tutorials include Docker configurations for consistent development environments:

```yaml
# Example docker-compose.yml structure
version: '3.8'
services:
  web-app:
    build: .
    ports: ["3000:80"]
  
  mobile-builder:
    image: android-sdk
    volumes: ["./:/workspace"]
  
  desktop-builder:
    image: electron-builder
    volumes: ["./:/workspace"]
```

### Docker Commands
```bash
# Build all services
docker-compose build

# Run specific tutorial
docker-compose up tutorial-1

# Clean build
docker-compose down --volumes
docker-compose up --build
```

## 📋 Troubleshooting

### Common Issues

**1. WhyML Installation Problems**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install with user flag if permission issues
pip install --user whyml

# Verify installation
python -c "import whyml; print(whyml.__version__)"
```

**2. Docker Build Issues**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check Docker memory/disk space
docker system df
```

**3. Node.js/npm Issues**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Use specific Node.js version
nvm use 18
```

**4. Android Build Issues**
```bash
# Set ANDROID_HOME environment variable
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Accept SDK licenses
yes | sdkmanager --licenses

# Clean Gradle cache
./gradlew clean
```

**5. Electron/Tauri Build Issues**
```bash
# Clear Electron cache
npx electron-rebuild

# For Tauri, ensure Rust is updated
rustup update stable
cargo install tauri-cli

# Clear target directory
rm -rf src-tauri/target
```

### Getting Help

- **WhyML Documentation:** Check the main [README.md](../../README.md)
- **GitHub Issues:** Report bugs at the [project repository](https://github.com/dynapsys/whyml)
- **Community:** Join discussions in project forums
- **CLI Help:** Use `whyml --help` for command reference

## 🎯 Learning Path Recommendations

### Beginner Path (Start Here)
1. **Tutorial 1** - HTML/PHP basics
2. **Tutorial 3** - Desktop app creation
3. **Tutorial 4** - Modern web frameworks

### Advanced Path
1. **Tutorial 2** - SVG & DataURI mastery
2. **Tutorial 5** - Cross-platform development
3. Custom manifest creation

### Full-Stack Developer Path
1. **All Tutorials 1-5** in sequence
2. Experiment with hybrid approaches
3. Build production applications

## 🔧 Advanced Configuration

### Custom Manifest Templates
Create reusable templates for your projects:

```yaml
# templates/base-template.yaml
metadata:
  template_version: "1.0"
  author: "Your Name"

config:
  # Your default configurations
  
variables:
  # Your common variables
  
# Include in other manifests with:
# extends: "templates/base-template.yaml"
```

### Environment-Specific Builds
```bash
# Development build
NODE_ENV=development whyml convert manifest.yaml

# Production build
NODE_ENV=production whyml convert manifest.yaml --optimize

# Staging with custom config
whyml convert manifest.yaml --config staging.json
```

### CI/CD Integration
```yaml
# .github/workflows/build.yml
name: Build All Platforms
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup WhyML
        run: pip install whyml
      - name: Build applications
        run: ./scripts/deploy-all.sh
```

## 📊 Feature Comparison

| Feature | Tutorial 1 | Tutorial 2 | Tutorial 3 | Tutorial 4 | Tutorial 5 |
|---------|------------|------------|------------|------------|------------|
| Web Scraping | ✅ | ✅ | ✅ | ✅ | ✅ |
| YAML Manifests | ✅ | ✅ | ✅ | ✅ | ✅ |
| Docker Support | ✅ | ✅ | ⭐ | ✅ | ✅ |
| Multi-page Sites | ✅ | ⭐ | ⭐ | ✅ | ⭐ |
| Component System | ✅ | ✅ | ⭐ | ✅ | ⭐ |
| DataURI Media | ⭐ | ✅ | ⭐ | ⭐ | ⭐ |
| Interactive UI | ⭐ | ✅ | ✅ | ✅ | ✅ |
| Desktop Apps | ⭐ | ⭐ | ✅ | ⭐ | ✅ |
| Mobile Apps | ⭐ | ⭐ | ⭐ | PWA | ✅ |
| Cross-platform | ⭐ | ⭐ | ✅ | ✅ | ✅ |

**Legend:** ✅ = Full support, ⭐ = Basic/Limited support

## 🎉 What's Next?

After completing these tutorials, you'll be able to:

- **Transform any website** into multiple application formats
- **Build cross-platform applications** from unified manifests
- **Deploy production-ready applications** with Docker
- **Create reusable component libraries** with YAML
- **Automate build pipelines** for multiple platforms

### Suggested Projects
1. **Portfolio Website** → Mobile App (Tutorials 1, 5)
2. **Interactive Dashboard** → Desktop App (Tutorials 2, 3)
3. **E-commerce Site** → PWA (Tutorials 1, 4)
4. **Documentation Site** → Multi-platform (All tutorials)

### Contributing
Found an issue or want to improve a tutorial? Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Submit a pull request

---

## 📝 Tutorial Completion Checklist

Track your progress through the tutorial series:

- [ ] **Prerequisites Setup** - WhyML, Docker, Node.js installed
- [ ] **Tutorial 1** - Multi-page HTML/PHP site completed
- [ ] **Tutorial 2** - SVG/DataURI application completed  
- [ ] **Tutorial 3** - Tauri desktop app completed
- [ ] **Tutorial 4** - React/Vue/PWA apps completed
- [ ] **Tutorial 5** - Cross-platform mobile/desktop apps completed
- [ ] **Advanced Workflows** - Custom manifests created
- [ ] **Production Deployment** - Real application deployed

**Congratulations!** 🎊 You've mastered the complete WhyML ecosystem!

---

*This tutorial series is part of the WhyML project. For the latest updates and documentation, visit the [main repository](https://github.com/dynapsys/whyml).*
