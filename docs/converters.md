# Converters Guide

## Overview

WhyML supports conversion to multiple output formats through specialized converters. Each converter transforms YAML manifests into format-specific code while preserving the semantic structure and styling.

## Supported Formats

- **HTML** - Semantic HTML5 with CSS styling
- **React** - JSX/TSX components with hooks and TypeScript support
- **Vue** - Single File Components (SFC) with Composition API
- **PHP** - Object-oriented PHP components with templating

## HTML Converter

### Features
- Semantic HTML5 generation
- CSS styling integration
- Responsive design support
- SEO optimization
- Accessibility compliance

### Usage

```bash
# Basic conversion
whyml convert --from manifest.yaml --to page.html --as html

# With configuration file
whyml convert --from manifest.yaml --to page.html --as html --config config.yaml
```

### Configuration Options

```yaml
config:
  html:
    doctype: "html5"           # html5, html4, xhtml
    include_meta_tags: true    # Include SEO meta tags
    responsive_design: true    # Include responsive viewport
    minify_output: false       # Minify HTML output
    semantic_elements: true    # Use semantic HTML5 elements
```

### Example Output

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title</title>
  <style>
    .container { max-width: 1200px; margin: 0 auto; }
  </style>
</head>
<body>
  <div class="container">
    <header class="header">
      <h1>Welcome</h1>
    </header>
  </div>
</body>
</html>
```

## React Converter

### Features
- Modern functional components with hooks
- TypeScript support (TSX)
- CSS Modules integration
- Props interface generation
- Event handler generation
- State management with hooks

### Usage

```bash
# TypeScript React component
whyml convert --from manifest.yaml --to Component.tsx --as react

# JavaScript React component
whyml convert --from manifest.yaml --to Component.jsx --as react
```

### Configuration Options

```yaml
config:
  react:
    use_typescript: true       # Generate TypeScript interfaces
    use_hooks: true           # Use React hooks (useState, useEffect)
    css_framework: "css-modules"  # css-modules, styled-components, emotion
    export_default: true      # Use default export
    component_type: "functional"  # functional, class
```

### Example Output

```tsx
import React, { useState, useEffect } from 'react';
import styles from './Component.module.css';

interface Props {
  className?: string;
  style?: React.CSSProperties;
}

const Component: React.FC<Props> = (props) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    console.log('Component mounted');
  }, []);

  const handleClick = () => {
    setCount(count + 1);
  };

  return (
    <div className={styles.container}>
      <h1>Welcome</h1>
      <button onClick={handleClick}>
        Count: {count}
      </button>
    </div>
  );
};

export default Component;
```

## Vue Converter

### Features
- Vue 3 Single File Components (SFC)
- Composition API support
- Scoped styles
- TypeScript support
- Reactive data binding
- Event handling with directives

### Usage

```bash
# Vue 3 with Composition API
whyml convert manifest.yaml --to vue --composition-api --output Component.vue

# Vue 2 compatible
whyml convert manifest.yaml --to vue --vue-version 2 --output Component.vue
```

### Configuration Options

```yaml
config:
  vue:
    version: 3                # Vue version (2 or 3)
    use_composition_api: true # Use Composition API (Vue 3)
    scoped_styles: true       # Use scoped CSS
    typescript: true          # Use TypeScript in script
    css_preprocessor: "scss"  # css, scss, sass, less
```

### Example Output

```vue
<template>
  <div class="container">
    <h1>{{ title }}</h1>
    <button @click="increment">
      Count: {{ count }}
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'Component',
  setup() {
    const count = ref(0);
    const title = ref('Welcome');

    const increment = () => {
      count.value++;
    };

    return {
      count,
      title,
      increment
    };
  }
});
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
```

## PHP Converter

### Features
- Object-oriented PHP classes
- Type declarations (PHP 7.4+)
- HTML templating methods
- CSS integration
- Namespace support
- Security features (HTML escaping)

### Usage

```bash
# PHP class with namespace
whyml convert manifest.yaml --to php --namespace "App\\Components" --output Component.php

# With type declarations
whyml convert manifest.yaml --to php --type-declarations --output Component.php
```

### Configuration Options

```yaml
config:
  php:
    namespace: "App\\Components"  # PHP namespace
    use_type_declarations: true  # Use PHP type hints
    class_suffix: "Component"    # Class name suffix
    extends_class: null          # Parent class to extend
    implements: []               # Interfaces to implement
```

### Example Output

```php
<?php

namespace App\Components;

class PageComponent
{
    private array $data = [];
    private array $styles = [
        'container' => 'max-width: 1200px; margin: 0 auto;'
    ];

    public function __construct(array $data = []): void
    {
        $this->data = $data;
    }

    public function render(): string
    {
        $html = '';
        $html .= '<div class="container">';
        $html .= '<h1>' . $this->escapeHtml($this->getData('title', 'Welcome')) . '</h1>';
        $html .= '</div>';
        return $html;
    }

    public function getStyles(): string
    {
        $css = '';
        foreach ($this->styles as $selector => $rules) {
            $css .= ".{$selector} { {$rules} }\n";
        }
        return $css;
    }

    private function escapeHtml(string $content): string
    {
        return htmlspecialchars($content, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    }

    private function getData(string $key, mixed $default = null): mixed
    {
        return $this->data[$key] ?? $default;
    }
}
```

## Advanced Features

### Template Variables in Converters

All converters support template variable substitution:

```yaml
variables:
  primary_color: "#007bff"
  component_name: "MyComponent"

structure:
  div:
    style: "color: {{ primary_color }}"
    text: "Welcome to {{ component_name }}"
```

### CSS Framework Integration

Converters can integrate with popular CSS frameworks:

```yaml
imports:
  css:
    - "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"

config:
  css_framework: "bootstrap"  # bootstrap, tailwind, foundation
```

### Responsive Design

All converters support responsive design patterns:

```yaml
styles:
  .container:
    max-width: "1200px"
    margin: "0 auto"
  
  "@media (max-width: 768px)":
    .container:
      padding: "10px"
```

### Accessibility Features

Converters automatically include accessibility features:

- Semantic HTML elements
- ARIA labels and roles
- Alt text for images
- Proper heading hierarchy
- Keyboard navigation support

## Converter API

### Python API Usage

```python
import asyncio
from whyml import WhyMLProcessor

async def convert_manifest():
    processor = WhyMLProcessor()
    
    # Convert to HTML
    html_result = await processor.convert_to_html('manifest.yaml')
    html_result.save_to_file('output.html')
    
    # Convert to React with options
    react_result = await processor.convert_to_react(
        'manifest.yaml',
        use_typescript=True,
        css_modules=True
    )
    react_result.save_to_file('Component.tsx')
    
    # Convert to Vue
    vue_result = await processor.convert_to_vue(
        'manifest.yaml',
        composition_api=True
    )
    vue_result.save_to_file('Component.vue')
    
    # Convert to PHP
    php_result = await processor.convert_to_php(
        'manifest.yaml',
        namespace='App\\Components'
    )
    php_result.save_to_file('Component.php')

asyncio.run(convert_manifest())
```

### Conversion Result Object

Each converter returns a `ConversionResult` object:

```python
class ConversionResult:
    content: str          # Generated code content
    filename: str         # Suggested filename
    format_type: str      # Output format (html, react, vue, php)
    metadata: dict        # Conversion metadata
    
    def save_to_file(self, path: str) -> None:
        """Save content to file"""
        
    def get_size(self) -> int:
        """Get content size in bytes"""
```

## Best Practices

### 1. Format-Specific Considerations

**HTML:**
- Use semantic elements for better SEO
- Include proper meta tags
- Optimize for accessibility

**React:**
- Use TypeScript for better type safety
- Implement proper error boundaries
- Follow React hooks best practices

**Vue:**
- Use Composition API for Vue 3
- Implement proper reactive patterns
- Use scoped styles to avoid conflicts

**PHP:**
- Use type declarations for better code quality
- Implement proper security measures
- Follow PSR standards

### 2. Performance Optimization

- Minimize CSS and JavaScript in production
- Use CSS modules to avoid style conflicts
- Implement lazy loading for large components
- Optimize images and assets

### 3. Maintainability

- Use consistent naming conventions
- Document complex logic in comments
- Implement proper error handling
- Use version control for manifest files

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Ensure all required packages are installed
2. **Template Variable Errors**: Check variable names and references
3. **CSS Conflicts**: Use CSS modules or scoped styles
4. **Type Errors**: Enable TypeScript for better error detection

### Debug Mode

Enable debug mode for detailed conversion information:

```bash
whyml convert manifest.yaml --to react --debug --output Component.tsx
```

## Examples

See the [examples directory](../examples/) for complete working examples of each converter type.
