# WhyML Core

[![PyPI version](https://badge.fury.io/py/whyml-core.svg)](https://badge.fury.io/py/whyml-core)
[![Python Support](https://img.shields.io/pypi/pyversions/whyml-core.svg)](https://pypi.org/project/whyml-core/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![WhyML Ecosystem](https://img.shields.io/badge/ecosystem-WhyML-blue.svg)](https://github.com/dynapsys/whyml)

**🎯 Core functionality for the WhyML ecosystem - validation, loading, processing, and manifest manipulation**

WhyML Core provides the foundational infrastructure for the WhyML ecosystem, offering robust tools for YAML manifest processing, template inheritance, dependency resolution, and async operations. Built with modern Python patterns and comprehensive error handling.

## 🔧 Recent Core Updates (2025)

**✅ EXCEPTION SYSTEM**: Enhanced exception classes with improved constructors:
- **NetworkError**: Added `details` parameter for comprehensive error context
- **ValidationError**: Improved error reporting and validation result integration
- **ProcessingError**: Enhanced processing pipeline error handling

**✅ VALIDATION FRAMEWORK**: Added `ValidationResult` class to whyml-core validation module for structured validation reporting and compatibility with existing test suites.

**✅ LOADEDMANIFEST HANDLING**: Improved LoadedManifest dataclass structure with proper `.content` attribute extraction patterns throughout the ecosystem.

**✅ BACKWARDS COMPATIBILITY**: Maintained full backwards compatibility while adding new functionality and fixing critical CLI conversion issues.

## 🚀 Key Features

- **🔍 Advanced Validation**: JSON schema validation with custom field validators and comprehensive error reporting
- **📂 Intelligent Loading**: Async manifest loading with dependency resolution, caching, and cycle detection  
- **🔄 Template Processing**: Jinja2-powered template engine with multi-syntax support (`{{VAR}}` and `<?=VAR?>`)
- **🧬 Inheritance Resolution**: Complex template inheritance with merge strategies and conflict resolution
- **⚡ Async Operations**: Full async/await support for file I/O, HTTP requests, and concurrent processing
- **🛠 Rich Utilities**: YAML processing, path manipulation, string utilities, and async file management

## 📦 Installation

```bash
pip install whyml-core
```

For development dependencies:
```bash
pip install whyml-core[dev]
```

## 🏗 Architecture

WhyML Core is organized into focused modules:

### Core Modules

- **`exceptions/`** - Comprehensive exception hierarchy
- **`validation/`** - Manifest validation with schema support
- **`loading/`** - Async manifest loading and dependency management
- **`processing/`** - Template processing and inheritance resolution
- **`utils/`** - Utility functions for common operations

### Module Details

```
whyml_core/
├── exceptions/          # Exception handling
│   ├── base_exceptions.py      # Base exception classes
│   ├── validation_exceptions.py   # Validation-specific exceptions
│   └── processing_exceptions.py   # Processing-specific exceptions
├── validation/          # Validation framework
│   ├── manifest_validator.py     # Core manifest validation
│   ├── schema_loader.py          # JSON schema management
│   └── field_validators.py       # Specialized field validators
├── loading/            # Loading and dependency management
│   ├── manifest_loader.py       # Async manifest loading
│   ├── cache_manager.py         # Advanced caching system
│   └── dependency_resolver.py    # Dependency graph resolution
├── processing/         # Template processing
│   ├── template_processor.py    # Jinja2 template engine
│   ├── inheritance_resolver.py  # Template inheritance
│   └── variable_substitution.py # Variable substitution
└── utils/             # Utilities
    ├── yaml_utils.py         # YAML processing utilities
    ├── async_utils.py        # Async operation helpers
    ├── path_utils.py         # Path manipulation
    └── string_utils.py       # String processing
```

## 🔧 Quick Start

### Basic Manifest Validation

```python
from whyml_core.validation import ManifestValidator

validator = ManifestValidator()

# Validate a manifest
manifest = {
    'metadata': {'title': 'My App', 'version': '1.0.0'},
    'structure': {'body': {'content': 'Hello World'}}
}

try:
    is_valid = await validator.validate_manifest(manifest)
    print(f"Manifest is valid: {is_valid}")
except ValidationError as e:
    print(f"Validation error: {e.message}")
```

### Async Manifest Loading

```python
from whyml_core.loading import ManifestLoader

loader = ManifestLoader()

# Load manifest with dependencies
async def load_example():
    manifest = await loader.load_manifest('manifest.yaml')
    return manifest

# With dependency resolution
manifest = await loader.load_with_dependencies('main-manifest.yaml')
```

### Template Processing

```python
from whyml_core.processing import TemplateProcessor

processor = TemplateProcessor()

# Process templates with variables
template_vars = {
    'app_name': 'MyApp',
    'version': '1.0.0'
}

processed = processor.substitute_template_variables(
    'Welcome to {{app_name}} v{{version}}',
    template_vars
)
```

### Advanced Processing Pipeline

```python
from whyml_core import (
    ManifestLoader, 
    ManifestValidator, 
    TemplateProcessor,
    InheritanceResolver
)

async def process_manifest(manifest_path: str):
    # Load manifest
    loader = ManifestLoader()
    manifest = await loader.load_manifest(manifest_path)
    
    # Validate
    validator = ManifestValidator()
    await validator.validate_manifest(manifest)
    
    # Process inheritance
    resolver = InheritanceResolver()
    resolved = await resolver.resolve_inheritance(manifest)
    
    # Process templates
    processor = TemplateProcessor()
    final_manifest = processor.substitute_template_vars(resolved)
    
    return final_manifest
```

## 🛠 Advanced Features

### Custom Validation Schemas

```python
from whyml_core.validation import SchemaLoader

schema_loader = SchemaLoader()

# Load custom schema
custom_schema = await schema_loader.load_schema('custom-schema.json')

# Use with validator
validator = ManifestValidator(schema_loader=schema_loader)
```

### Caching and Performance

```python
from whyml_core.loading import CacheManager

# Configure caching
cache_manager = CacheManager(max_size=1000, ttl=3600)

# Use with loader
loader = ManifestLoader(cache_manager=cache_manager)
```

### Async File Operations

```python
from whyml_core.utils import AsyncFileManager

async def example():
    file_manager = AsyncFileManager()
    
    # Read file with caching
    content = await file_manager.read_file('data.yaml')
    
    # Write file with directory creation
    await file_manager.write_file('output/result.yaml', content)
```

### YAML Processing

```python
from whyml_core.utils import YAMLUtils, YAMLProcessor

# Basic operations
data = YAMLUtils.load_file('manifest.yaml')
YAMLUtils.save_file(data, 'output.yaml')

# Advanced processing
processor = YAMLProcessor()
normalized = processor.normalize_manifest(manifest)
excerpt = processor.extract_sections(manifest, ['metadata', 'structure'])
```

## 🔍 Error Handling

WhyML Core provides comprehensive error handling:

```python
from whyml_core.exceptions import (
    WhyMLError,
    ValidationError,
    TemplateError,
    ManifestError
)

try:
    result = await some_operation()
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Details: {e.details}")
except TemplateError as e:
    print(f"Template processing error: {e.message}")
    print(f"Context: {e.context}")
except WhyMLError as e:
    # Base class catches all WhyML-specific errors
    print(f"WhyML error: {e}")
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install whyml-core[test]

# Run tests
pytest

# Run with coverage
pytest --cov=whyml_core --cov-report=html
```

## 🤝 Contributing

WhyML Core is part of the larger WhyML ecosystem. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📋 Requirements

- Python 3.8+
- PyYAML 6.0+
- Jinja2 3.0+
- jsonschema 4.0+
- aiohttp 3.8+
- aiofiles 23.0+
- cachetools 5.0+

## 🔗 Related Projects

WhyML Core is designed to work with other WhyML packages:

- **[whyml](https://pypi.org/project/whyml/)** - Main WhyML package
- **whyml-scrapers** - Web scraping functionality
- **whyml-converters** - Format converters (HTML, React, Vue, PHP)
- **whyml-cli** - Command-line interface

## 📄 License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

## 🔗 Links

- **Documentation**: [GitHub Repository](https://github.com/dynapsys/whyml)
- **PyPI Package**: [whyml-core](https://pypi.org/project/whyml-core/)
- **Issue Tracker**: [GitHub Issues](https://github.com/dynapsys/whyml/issues)
- **Main Project**: [WhyML](https://github.com/dynapsys/whyml)

---

*WhyML Core - Empowering modular manifest processing with robust, async-first architecture.*
