# WhyML Deployment Guide

## 🚀 Import Resolution & Deployment Strategy

This guide documents the import resolution strategy for the WhyML ecosystem and provides deployment instructions for different scenarios.

## 📋 Current Architecture

### Modular Package Structure
```
whyml/                    # Main orchestration package (v0.1.28)
├── whyml-core/          # Core functionality (v0.1.28)
├── whyml-converters/    # Multi-format converters (v0.1.28) 
├── whyml-scrapers/      # Web scraping (v0.1.28)
└── whyml-cli/           # Command-line interface (v0.1.28)
```

### Dependency Chain
```
whyml (main)
├── depends on: whyml-core>=0.1.0
├── depends on: whyml-converters>=0.1.0  
├── depends on: whyml-scrapers>=0.1.0
└── optionally: whyml-cli>=1.0.0

whyml-converters
└── depends on: whyml-core>=0.1.0

whyml-scrapers  
└── depends on: whyml-core>=0.1.0

whyml-cli
├── depends on: whyml-core>=0.1.0
├── depends on: whyml-converters>=0.1.0
└── depends on: whyml-scrapers>=0.1.0
```

## 🛠 Import Resolution Strategies

### Strategy 1: Development Mode Installation (Recommended)

**When virtual environments work:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install modular packages in development mode
cd whyml-core && pip install -e . && cd ..
cd whyml-converters && pip install -e . && cd ..  
cd whyml-scrapers && pip install -e . && cd ..
cd whyml-cli && pip install -e . && cd ..

# Install main package
pip install -e .
```

**Benefits:**
- Live code changes reflected immediately
- Full import resolution
- Proper dependency management
- Suitable for development and testing

### Strategy 2: Build and Install Packages

**When virtual environments fail:**
```bash
# Build all modular packages
cd whyml-core && make build && cd ..
cd whyml-converters && make build && cd ..
cd whyml-scrapers && make build && cd ..
cd whyml-cli && make build && cd ..

# Install built packages (requires pip override)
pip install whyml-core/dist/whyml_core-*.whl --break-system-packages
pip install whyml-converters/dist/whyml_converters-*.whl --break-system-packages  
pip install whyml-scrapers/dist/whyml_scrapers-*.whl --break-system-packages
pip install whyml-cli/dist/whyml_cli-*.whl --break-system-packages

# Install main package
pip install . --break-system-packages
```

**Benefits:**
- Works with externally-managed environments
- Full functionality once installed
- Production-ready deployment

### Strategy 3: Docker Deployment

**Containerized approach (bypasses environment issues):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

# Install modular packages in order
RUN cd whyml-core && pip install .
RUN cd whyml-converters && pip install .
RUN cd whyml-scrapers && pip install . 
RUN cd whyml-cli && pip install .

# Install main package
RUN pip install .

EXPOSE 8000
CMD ["python", "-m", "whyml.server"]
```

**Benefits:**
- Isolated environment
- Consistent deployment
- Scalable for production

### Strategy 4: PyPI Publication

**Production deployment via package registry:**
```bash
# Publish modular packages to PyPI first
cd whyml-core && make publish && cd ..
cd whyml-converters && make publish && cd ..
cd whyml-scrapers && make publish && cd ..
cd whyml-cli && make publish && cd ..

# Publish main package  
make publish

# Users install normally
pip install whyml
```

**Benefits:**
- Standard Python packaging
- Easy distribution
- Version management
- Dependency resolution handled by pip

## 🔧 Troubleshooting Import Issues

### Common Problems & Solutions

#### 1. ModuleNotFoundError: No module named 'whyml_core'

**Cause:** Modular packages not installed or not in Python path

**Solutions:**
```bash
# Check installed packages
pip list | grep whyml

# Reinstall missing packages
pip install whyml-core whyml-converters whyml-scrapers

# Or use development installation
pip install -e whyml-core/ -e whyml-converters/ -e whyml-scrapers/
```

#### 2. externally-managed-environment Error

**Cause:** System Python prevents package installation

**Solutions:**
```bash
# Use virtual environment (preferred)
python3 -m venv venv && source venv/bin/activate

# Override system protection (use cautiously)
pip install --break-system-packages

# Use pipx for isolated installation
pipx install whyml

# Use conda environment
conda create -n whyml python=3.11
conda activate whyml
```

#### 3. Version Conflicts

**Cause:** Mismatched package versions

**Solutions:**
```bash
# Update all packages to latest version
pip install --upgrade whyml whyml-core whyml-converters whyml-scrapers

# Force reinstall with consistent versions
pip install whyml-core==0.1.28 whyml-converters==0.1.28 whyml-scrapers==0.1.28 whyml==0.1.28
```

#### 4. Import Path Issues

**Cause:** Backward compatibility aliases not resolving

**Solutions:**
```python
# Check import resolution
try:
    from whyml_core.loading import ManifestLoader
    print("✅ Direct import works")
except ImportError:
    print("❌ Direct import failed")

try:  
    from whyml.manifest_loader import ManifestLoader
    print("✅ Compatibility alias works")
except ImportError:
    print("❌ Compatibility alias failed")
```

## 📦 Production Deployment Checklist

### Pre-Deployment Validation
- [ ] All modular packages build successfully
- [ ] Version numbers are synchronized (currently 0.1.28)
- [ ] Dependencies are properly declared in pyproject.toml
- [ ] Backward compatibility aliases work correctly
- [ ] Test suite passes for all packages

### Deployment Steps
1. **Choose deployment strategy** (virtual env, Docker, PyPI)
2. **Install dependencies** in correct order (core → converters/scrapers → CLI → main)
3. **Verify imports** work correctly
4. **Run integration tests** to ensure functionality
5. **Monitor for import errors** in production logs

### Post-Deployment Verification
```bash
# Test core functionality
python -c "from whyml import ManifestLoader; print('✅ Core imports work')"

# Test converters
python -c "from whyml import HTMLConverter; print('✅ Converters work')"

# Test scrapers  
python -c "from whyml import URLScraper; print('✅ Scrapers work')"

# Test CLI
whyml-cli --version
```

## 🚀 Deployment Environments

### Development
- Use Strategy 1 (development mode installation)
- Enable debug logging
- Use local package builds
- Rapid iteration and testing

### Staging  
- Use Strategy 2 (build and install) or Strategy 3 (Docker)
- Production-like environment
- Full integration testing
- Performance validation

### Production
- Use Strategy 3 (Docker) or Strategy 4 (PyPI)
- Locked dependency versions
- Health monitoring
- Rollback capability

## 📊 Current Status & Next Steps

### ✅ Completed
- All modular packages build successfully
- Version synchronization (0.1.28 across ecosystem)
- Backward compatibility aliases implemented
- Documentation standardized
- pyproject.toml files unified

### 🔄 In Progress  
- Import resolution (blocked by virtual environment constraints)
- Integration testing across deployment strategies

### 📋 Pending
- PyPI publication workflow
- Docker image optimization
- CI/CD pipeline setup
- Performance benchmarking

## 🔗 Related Documentation

- [Main README](README.md) - Project overview and quick start
- [TODO.md](TODO.md) - Current development tasks
- [TEST.md](TEST.md) - Testing strategies and execution
- [Individual package READMEs](whyml-*/README.md) - Package-specific documentation

---

**Last Updated:** 2025-01-27  
**Version:** 0.1.28  
**Maintainer:** Dynapsys Team (contact@dynapsys.ai)
