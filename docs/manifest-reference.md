# YAML Manifest Reference

## Complete Manifest Structure

A WhyML manifest is a YAML file that defines a component or webpage structure. Here's the complete specification:

```yaml
# Basic metadata about the component
metadata:
  title: "Component Name"
  description: "Component description"
  version: "1.0.0"
  author: "Author Name"
  created: "2025-01-20"
  tags: ["tag1", "tag2"]

# Template inheritance (optional)
extends: "base-template.yaml"

# Template variables for dynamic content
variables:
  primary_color: "#007bff"
  secondary_color: "#6c757d"
  font_family: "Arial, sans-serif"
  site_name: "My Website"

# CSS styles definition
styles:
  body:
    font-family: "{{ font_family }}"
    margin: "0"
    padding: "0"
  
  .container:
    max-width: "1200px"
    margin: "0 auto"
    padding: "20px"
  
  .header:
    background: "{{ primary_color }}"
    color: "white"
    padding: "20px 0"

# HTML structure definition
structure:
  html:
    lang: "en"
    children:
      - head:
          children:
            - meta:
                charset: "utf-8"
            - title:
                text: "{{ title }}"
      - body:
          children:
            - div:
                class: "container"
                children:
                  - header:
                      class: "header"
                      children:
                        - h1:
                            text: "{{ site_name }}"

# External dependencies
imports:
  css:
    - "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
    - "custom-styles.css"
  js:
    - "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"
    - "custom-script.js"

# Interactive behavior (for React/Vue)
interactions:
  onClick: "handleClick"
  onSubmit: "handleSubmit"
  state_counter: "useState(0)"
  effect_mount: "useEffect(() => {}, [])"

# External content integration
external_content:
  header_content:
    source: "https://api.example.com/header"
    target: "header"
  footer_content:
    source: "./content/footer.html"
    target: "footer"

# Configuration options
config:
  responsive: true
  accessibility: true
  seo_optimized: true
  minify_output: false

# Dependencies on other manifests
dependencies:
  - "components/header.yaml"
  - "components/footer.yaml"

# Page analysis data (from scraping)
analysis:
  page_type: "landing_page"
  complexity_score: 3
  semantic_elements: 12
  accessibility_score: 85
  seo_score: 90
```

## Section Details

### Metadata Section

The `metadata` section contains basic information about the component:

```yaml
metadata:
  title: "Page Title"           # Required: Component/page title
  description: "Description"    # Required: Brief description
  version: "1.0.0"             # Optional: Version number
  author: "Author Name"        # Optional: Author information
  created: "2025-01-20"        # Optional: Creation date
  updated: "2025-01-20"        # Optional: Last update date
  tags: ["web", "component"]   # Optional: Tags for categorization
```

### Variables Section

Template variables allow dynamic content substitution:

```yaml
variables:
  # Basic variables
  site_name: "My Website"
  primary_color: "#007bff"
  
  # Nested variables
  theme:
    colors:
      primary: "#007bff"
      secondary: "#6c757d"
    fonts:
      heading: "Georgia, serif"
      body: "Arial, sans-serif"
```

Use variables in other sections with `{{ variable_name }}` syntax:
```yaml
structure:
  h1:
    text: "Welcome to {{ site_name }}"
    style: "color: {{ theme.colors.primary }}"
```

### Styles Section

Define CSS styles for your component:

```yaml
styles:
  # Element selectors
  body:
    font-family: "Arial, sans-serif"
    margin: "0"
    padding: "0"
  
  # Class selectors
  .container:
    max-width: "1200px"
    margin: "0 auto"
  
  # ID selectors
  "#header":
    background: "{{ primary_color }}"
  
  # Pseudo-selectors
  "a:hover":
    color: "{{ secondary_color }}"
  
  # Media queries
  "@media (max-width: 768px)":
    .container:
      padding: "10px"
```

### Structure Section

Define the HTML structure using nested YAML:

```yaml
structure:
  # Single element
  div:
    class: "container"
    id: "main-container"
    text: "Content here"
  
  # Element with children
  div:
    class: "wrapper"
    children:
      - h1:
          text: "Title"
      - p:
          text: "Paragraph content"
      - ul:
          children:
            - li:
                text: "Item 1"
            - li:
                text: "Item 2"
  
  # Element with attributes
  img:
    src: "image.jpg"
    alt: "Description"
    class: "responsive-image"
  
  # Form elements
  form:
    action: "/submit"
    method: "post"
    children:
      - input:
          type: "text"
          name: "username"
          placeholder: "Enter username"
      - button:
          type: "submit"
          text: "Submit"
```

### Imports Section

Include external CSS and JavaScript files:

```yaml
imports:
  css:
    - "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
    - "./styles/custom.css"
    - url: "https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap"
      media: "all"
  
  js:
    - "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"
    - "./scripts/custom.js"
    - url: "./scripts/analytics.js"
      async: true
      defer: true
```

### Interactions Section

Define interactive behavior for React/Vue components:

```yaml
interactions:
  # Event handlers
  onClick: "handleClick"
  onSubmit: "handleFormSubmit"
  onMouseOver: "handleHover"
  
  # React hooks
  state_counter: "useState(0)"
  state_visible: "useState(true)"
  effect_mount: "useEffect(() => { console.log('mounted'); }, [])"
  
  # Vue composition API
  data_count: "ref(0)"
  data_items: "reactive([])"
  method_increment: "count.value++"
```

### External Content Section

Load content from external sources:

```yaml
external_content:
  # Simple URL/file reference
  header_content: "https://api.example.com/header.html"
  
  # Detailed configuration
  navigation:
    source: "./content/nav.html"
    target: "nav"
    cache: true
    timeout: 5000
  
  # API with parameters
  user_data:
    source: "https://api.example.com/user/{{ user_id }}"
    target: "user-info"
    headers:
      Authorization: "Bearer {{ api_token }}"
```

### Configuration Section

Component-level configuration options:

```yaml
config:
  # Output options
  responsive: true
  accessibility: true
  seo_optimized: true
  minify_output: false
  
  # Framework-specific options
  react:
    use_typescript: true
    use_hooks: true
    css_modules: true
  
  vue:
    version: 3
    composition_api: true
    scoped_styles: true
  
  php:
    namespace: "App\\Components"
    use_type_declarations: true
```

## Template Inheritance

WhyML supports template inheritance for reusable components:

### Base Template (base.yaml)
```yaml
metadata:
  title: "Base Template"
  
variables:
  primary_color: "#007bff"
  
styles:
  body:
    font-family: "Arial, sans-serif"
    
structure:
  html:
    children:
      - head:
          children:
            - title:
                text: "{{ title }}"
      - body:
          children:
            - header:
                class: "header"
            - main:
                class: "content"
            - footer:
                class: "footer"
```

### Child Template (page.yaml)
```yaml
extends: "base.yaml"

metadata:
  title: "My Page"  # Override parent title
  
# Add new variables
variables:
  page_subtitle: "Welcome to my page"
  
# Add new styles
styles:
  .page-specific:
    color: "{{ primary_color }}"
    
# Override structure sections
structure:
  main:
    class: "content custom-content"
    children:
      - h1:
          text: "{{ title }}"
      - h2:
          text: "{{ page_subtitle }}"
```

## Validation Rules

WhyML validates manifests according to these rules:

1. **Required Fields**: `metadata.title` and `metadata.description` are required
2. **Variable References**: All `{{ variable }}` references must be defined in `variables` section
3. **Structure Validation**: HTML structure must be valid (proper nesting, required attributes)
4. **CSS Validation**: CSS properties must be valid
5. **Import Validation**: External URLs must be accessible (optional validation)

## Best Practices

1. **Use Semantic Structure**: Use proper HTML5 semantic elements
2. **Organize Styles**: Group related styles together
3. **Variable Naming**: Use descriptive variable names with consistent naming convention
4. **Template Inheritance**: Use inheritance for common layouts
5. **External Content**: Cache external content when possible
6. **Documentation**: Include clear descriptions in metadata

## Examples

See the [examples directory](../examples/) for complete working examples of different manifest types and use cases.
