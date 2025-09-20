# Getting Started with WhyML

## Overview

WhyML is a powerful Python package that transforms YAML manifests into multiple output formats including HTML, React, Vue, and PHP. This guide will help you get started quickly with WhyML.

## Installation

### From PyPI (Recommended)
```bash
pip install whyml
```

### From Source
```bash
git clone https://github.com/dynapsys/whyml.git
cd whyml
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/dynapsys/whyml.git
cd whyml
pip install -e ".[dev]"
```

## Quick Start

### 1. Basic YAML to HTML Conversion

Create a simple manifest file `example.yaml`:

```yaml
metadata:
  title: "My First Page"
  description: "Learning WhyML basics"

styles:
  body:
    font-family: "Arial, sans-serif"
    margin: "0"
    padding: "20px"

structure:
  html:
    children:
      - head:
          children:
            - title:
                text: "{{ title }}"
      - body:
          children:
            - h1:
                text: "Welcome to {{ title }}"
            - p:
                text: "{{ description }}"
```

Convert to HTML:
```bash
whyml convert --from example.yaml --to example.html --as html
```

### 2. Web Scraping to YAML

Scrape an existing website and convert it to a YAML manifest:

```bash
whyml scrape https://example.com --output scraped.yaml --simplify-structure
```

### 3. Multi-format Conversion

Convert your YAML manifest to different formats:

```bash
# Convert to React component
whyml convert --from example.yaml --to Example.tsx --as react

# Convert to Vue component
whyml convert --from example.yaml --to Example.vue --as vue

# Convert to PHP component
whyml convert --from example.yaml --to Example.php --as php
```

## 🚀 Quick Start with Scripts

The easiest way to get started is using our provided scripts:

```bash
# Run the complete Example 1 workflow
./scripts/examples/run-example-1.sh

# Or run all examples at once
./scripts/run-all-examples.sh
```

These scripts will:
- ✅ Check your installation
- ✅ Use correct CLI syntax
- ✅ Generate all output formats
- ✅ Show you the results

## Core Concepts

### YAML Manifest Structure

A WhyML manifest consists of several key sections:

- **metadata**: Basic information about the component
- **variables**: Template variables for dynamic content
- **styles**: CSS styling definitions
- **structure**: HTML structure definition
- **imports**: External CSS/JS dependencies
- **interactions**: Event handlers and dynamic behavior

### Template Variables

Use `{{ variable_name }}` syntax to insert dynamic content:

```yaml
variables:
  site_name: "My Website"
  primary_color: "#007bff"

structure:
  h1:
    text: "Welcome to {{ site_name }}"
    style: "color: {{ primary_color }}"
```

### Inheritance and Dependencies

WhyML supports template inheritance for reusable components:

```yaml
extends: "base-template.yaml"

metadata:
  title: "Child Page"

# Override or extend parent template
```

## Next Steps

- [CLI Reference](cli/README.md) - Complete command-line interface documentation
- [Advanced Scraping](advanced-scraping.md) - Advanced web scraping features
- [Manifest Reference](manifest-reference.md) - Complete YAML manifest specification
- [Converters Guide](converters.md) - Detailed converter documentation
- [API Reference](api-reference.md) - Python API documentation

## Examples

Check out the [examples directory](../examples/) for complete working examples:

- [Basic Example](../examples/1/README.md) - Complete scraping and regeneration workflow
- [Advanced Scraping Examples](../examples/advanced-scraping/) - Complex scraping scenarios

## Troubleshooting

For common issues and solutions, see our [Troubleshooting Guide](troubleshooting.md).

## Contributing

See our [Contributing Guide](contributing.md) for information on how to contribute to WhyML.
