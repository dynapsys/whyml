# WhyML Converters

[![PyPI version](https://badge.fury.io/py/whyml-converters.svg)](https://badge.fury.io/py/whyml-converters)
[![Python Support](https://img.shields.io/pypi/pyversions/whyml-converters.svg)](https://pypi.org/project/whyml-converters/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![WhyML Ecosystem](https://img.shields.io/badge/ecosystem-WhyML-blue.svg)](https://github.com/dynapsys/whyml)

**🚀 Multi-format code generation from WhyML manifests - HTML, React, Vue.js, and PHP applications**

Advanced code generation system that converts structured YAML manifests into production-ready applications across multiple technologies. Built with modern patterns, best practices, and comprehensive framework support.

## 🔧 Recent API Updates (2025)

**✅ ENHANCED COMPATIBILITY**: All converters now include synchronous `convert()` methods that wrap the existing async `convert_manifest()` methods for better test compatibility and direct usage.

**✅ CONSTRUCTOR PARAMETERS**: Added expected constructor parameters:
- **HTMLConverter**: `include_meta_tags` parameter for meta tag generation control
- **ReactConverter**: `use_typescript` parameter for TypeScript/JSX selection  
- **VueConverter**: `vue_version` parameter for Vue 2/3 compatibility
- **PHPConverter**: `php_version` parameter for PHP version targeting

**✅ BASE CONVERTER**: Enhanced BaseConverter to accept `css_framework`, `namespace`, `use_typescript` and other common parameters via flexible kwargs system.

**✅ CONVERSION RESULT**: Added `filename` parameter and `format_type` property to ConversionResult class for enhanced compatibility.

## 🚀 Features

### Multi-Format Support
- **HTML5**: Semantic, accessible HTML with modern standards
- **React**: JSX components with Hooks, TypeScript support, and CSS-in-JS
- **Vue.js**: Single File Components with Composition API and TypeScript
- **PHP**: Modern PHP classes with security best practices

### Advanced Generation Capabilities
- **Template Processing**: Jinja2 template integration for dynamic content
- **Component Architecture**: Reusable component generation for supported frameworks
- **Style Integration**: CSS, SCSS, and framework-specific styling
- **Script Handling**: JavaScript adaptation and framework-specific patterns
- **TypeScript Support**: Type-safe code generation for modern development

### Code Quality Features
- **Semantic HTML**: Proper semantic structure and accessibility
- **Modern Patterns**: Latest framework conventions and best practices  
- **Security**: XSS protection, input sanitization, and secure coding
- **Performance**: Optimized output with minimal overhead
- **Maintainability**: Clean, readable generated code

## 📦 Installation

```bash
pip install whyml-converters
```

Or install with development dependencies:

```bash
pip install whyml-converters[dev]
```

## 🏁 Quick Start

### Basic Usage

```python
from whyml_converters import HTMLConverter, ReactConverter, VueConverter, PHPConverter

# Load your WhyML manifest
manifest = {
    "metadata": {
        "title": "My App",
        "description": "A sample application"
    },
    "structure": {
        "tag": "div",
        "attributes": {"class": "container"},
        "children": [
            {
                "tag": "h1",
                "content": "Welcome to {{title}}"
            }
        ]
    }
}

# Convert to different formats
html_converter = HTMLConverter()
html_output = await html_converter.convert_manifest(manifest)

react_converter = ReactConverter()
react_output = await react_converter.convert_manifest(
    manifest, 
    typescript=True,
    component_type='functional'
)

vue_converter = VueConverter()
vue_output = await vue_converter.convert_manifest(
    manifest,
    composition_api=True,
    scoped=True
)

php_converter = PHPConverter()
php_output = await php_converter.convert_manifest(
    manifest,
    use_classes=True,
    namespace="MyApp"
)
```

### Save to Files

```python
# Save generated code to files
await html_converter.save_to_file(manifest, "output/index.html")
await react_converter.save_to_file(manifest, "output/App.tsx", typescript=True)
await vue_converter.save_to_file(manifest, "output/App.vue")
await php_converter.save_to_file(manifest, "output/Page.php")
```

## 🎯 Converter-Specific Features

### HTML Converter

```python
html_output = await HTMLConverter().convert_manifest(
    manifest,
    doctype="html5",              # HTML5 doctype
    semantic_structure=True,      # Use semantic HTML5 tags  
    include_meta_viewport=True,   # Responsive viewport meta
    css_framework="bootstrap",    # CSS framework integration
    minify=False                  # Readable output
)
```

**Features:**
- Semantic HTML5 structure
- Accessibility attributes (ARIA, alt text)
- Meta tag generation (SEO, social media)
- CSS and JavaScript integration
- Responsive design patterns

### React Converter

```python
react_output = await ReactConverter().convert_manifest(
    manifest,
    typescript=True,              # TypeScript support
    component_type='functional',  # Functional components
    use_hooks=True,              # React Hooks
    css_in_js=True,              # CSS-in-JS styling
    props_interface=True,        # TypeScript interfaces
    export_default=True          # Default export
)
```

**Features:**
- Functional and class components
- TypeScript interfaces and types
- React Hooks (useState, useEffect, etc.)
- CSS-in-JS with styled-components pattern
- Props validation and default values
- Modern JSX patterns

### Vue.js Converter

```python
vue_output = await VueConverter().convert_manifest(
    manifest,
    composition_api=True,         # Composition API
    typescript=True,              # TypeScript in <script setup>
    scoped=True,                 # Scoped CSS
    css_preprocessor='scss',     # SCSS support
    component_name='MyComponent' # Custom component name
)
```

**Features:**
- Single File Components (SFC)
- Composition API and Options API
- TypeScript support in `<script setup>`
- Scoped CSS and preprocessors
- Vue 3 patterns and reactivity
- Template syntax and directives

### PHP Converter

```python
php_output = await PHPConverter().convert_manifest(
    manifest,
    use_classes=True,            # Class-based approach
    namespace="MyApp\\Pages",    # PSR-4 namespacing
    strict_types=True,           # Strict type declarations
    php_version="8.1",          # Target PHP version
    extends="BasePage",          # Class inheritance
    include_usage=True           # Usage examples
)
```

**Features:**
- Modern PHP classes and namespaces
- Strict type declarations
- HTML escaping and XSS protection
- Template integration
- PSR-4 autoloading compatibility
- Procedural and OOP patterns

## 🏗️ Advanced Usage

### Custom Template Variables

```python
manifest_with_variables = {
    "metadata": {
        "title": "{{app_name}}",
        "variables": {
            "app_name": "My Custom App",
            "version": "1.0.0",
            "author": "Developer Name"
        }
    },
    "structure": {
        "tag": "header",
        "children": [
            {
                "tag": "h1", 
                "content": "{{app_name}} v{{version}}"
            },
            {
                "tag": "p",
                "content": "Created by {{author}}"
            }
        ]
    }
}

# Variables will be substituted during conversion
output = await converter.convert_manifest(manifest_with_variables)
```

### Component Generation

```python
# React component with props
react_component = await ReactConverter().convert_manifest(
    manifest,
    component_name="ProductCard",
    props={
        "title": {"type": "string", "required": True},
        "price": {"type": "number", "required": True},
        "onAddToCart": {"type": "function", "required": False}
    },
    typescript=True
)

# Vue component with props
vue_component = await VueConverter().convert_manifest(
    manifest,
    component_name="ProductCard",
    props={
        "title": {"type": "String", "required": True},
        "price": {"type": "Number", "required": True}
    },
    composition_api=True
)
```

### Style Integration

```python
manifest_with_styles = {
    "structure": {...},
    "styles": {
        "inline_styles": {
            "header": {
                "background-color": "#f8f9fa",
                "padding": "1rem",
                "border-radius": "0.5rem"
            }
        },
        "internal_styles": {
            "responsive": {
                "@media (max-width: 768px)": {
                    ".container": {
                        "padding": "0.5rem"
                    }
                }
            }
        }
    }
}

# Styles will be properly integrated into each format
html_output = await HTMLConverter().convert_manifest(manifest_with_styles)
vue_output = await VueConverter().convert_manifest(manifest_with_styles, scoped=True)
```

## 🔧 Configuration

### Base Converter Settings

All converters inherit from `BaseConverter` and support:

```python
converter = HTMLConverter(
    template_engine='jinja2',     # Template engine
    auto_escape=True,            # Template auto-escaping
    validate_manifest=True,      # Input validation
    include_comments=True,       # Code comments
    format_output=True          # Pretty formatting
)
```

### Framework-Specific Options

```python
# HTML-specific
html_converter = HTMLConverter(
    html_version="5",
    include_viewport_meta=True,
    semantic_structure=True
)

# React-specific  
react_converter = ReactConverter(
    react_version="18",
    use_strict_mode=True,
    jsx_pragma="React"
)

# Vue-specific
vue_converter = VueConverter(
    vue_version="3",
    use_composition_api=True,
    enable_devtools=True
)

# PHP-specific
php_converter = PHPConverter(
    php_version="8.1",
    use_declare_strict_types=True,
    psr_compliance=True
)
```

## 📚 API Reference

### BaseConverter

The abstract base class for all converters:

```python
class BaseConverter:
    async def convert_manifest(self, manifest: Dict[str, Any], **options) -> str
    async def save_to_file(self, manifest: Dict[str, Any], output_path: Path, **options) -> None
    def validate_manifest(self, manifest: Dict[str, Any]) -> bool
    def extract_metadata(self, manifest: Dict[str, Any]) -> Dict[str, Any]
    def extract_structure(self, manifest: Dict[str, Any]) -> Dict[str, Any]
    def extract_styles(self, manifest: Dict[str, Any]) -> Dict[str, Any]
    def extract_scripts(self, manifest: Dict[str, Any]) -> Dict[str, Any]
```

### Format-Specific Converters

Each converter extends `BaseConverter` with format-specific methods:

```python
# HTML Converter
class HTMLConverter(BaseConverter):
    def generate_doctype(self, version: str) -> str
    def generate_meta_tags(self, metadata: Dict[str, Any]) -> str
    def generate_html_structure(self, structure: Dict[str, Any]) -> str

# React Converter  
class ReactConverter(BaseConverter):
    def generate_jsx_component(self, structure: Dict[str, Any]) -> str
    def generate_typescript_interface(self, props: Dict[str, Any]) -> str
    def generate_react_hooks(self, component_logic: Dict[str, Any]) -> str

# Vue Converter
class VueConverter(BaseConverter):  
    def generate_vue_template(self, structure: Dict[str, Any]) -> str
    def generate_composition_api_logic(self, component_logic: Dict[str, Any]) -> str
    def generate_vue_style(self, styles: Dict[str, Any]) -> str

# PHP Converter
class PHPConverter(BaseConverter):
    def generate_php_class(self, manifest: Dict[str, Any]) -> str
    def generate_php_methods(self, structure: Dict[str, Any]) -> str
    def generate_php_properties(self, metadata: Dict[str, Any]) -> str
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=whyml_converters --cov-report=html

# Run specific converter tests
pytest tests/test_html_converter.py
pytest tests/test_react_converter.py
pytest tests/test_vue_converter.py  
pytest tests/test_php_converter.py
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/dynapsys/whyml.git
cd whyml/whyml-converters

# Install development dependencies
pip install -e .[dev]

# Run formatting and linting
black whyml_converters/
isort whyml_converters/
flake8 whyml_converters/
mypy whyml_converters/

# Run tests
pytest
```

### Adding New Converters

To add support for a new output format:

1. Create a new converter class extending `BaseConverter`
2. Implement the required abstract methods
3. Add format-specific generation methods
4. Create comprehensive tests
5. Update documentation

Example:

```python
from whyml_converters import BaseConverter

class CustomConverter(BaseConverter):
    def _get_output_format(self) -> str:
        return "custom"
    
    def _get_template_extension(self) -> str:
        return ".custom"
    
    async def convert_manifest(self, manifest: Dict[str, Any], **options) -> str:
        # Implement conversion logic
        pass
```

## 📄 License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

## 🔗 Related Projects

- **[whyml-core](../whyml-core/)**: Core processing and validation engine
- **[whyml-scrapers](../whyml-scrapers/)**: Web scraping and manifest generation  
- **[whyml](../)**: Main WhyML package and CLI tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/dynapsys/whyml/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dynapsys/whyml/discussions)
- **Documentation**: [Project Documentation](https://github.com/dynapsys/whyml/docs)

---

**WhyML Converters** - Transform your ideas into code across multiple technologies. 🚀
