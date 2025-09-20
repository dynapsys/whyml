"""
PHP Converter - Convert YAML manifests to PHP classes and templates

Generates modern PHP classes with templating support, HTML generation,
and comprehensive styling integration.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
from typing import Any, Dict, List, Optional, Union
from html import escape
import logging

from .base_converter import BaseConverter, ConversionResult, StructureWalker, CSSProcessor
from ..exceptions import ConversionError

logger = logging.getLogger(__name__)


class PHPConverter(BaseConverter):
    """
    Convert YAML manifests to PHP classes and templates.
    
    Features:
    - Modern PHP 8+ class generation
    - HTML templating methods
    - CSS integration
    - PSR-4 namespace support
    - Type declarations
    - Documentation generation
    """
    
    def __init__(self, 
                 php_version: str = "8.1",
                 namespace: str = "App\\Components",
                 use_type_declarations: bool = True,
                 generate_docs: bool = True,
                 **kwargs):
        """
        Initialize PHP converter.
        
        Args:
            php_version: Target PHP version
            namespace: PHP namespace for generated classes
            use_type_declarations: Use PHP type declarations
            generate_docs: Generate PHPDoc comments
            **kwargs: Additional options passed to base converter
        """
        super().__init__(**kwargs)
        self.php_version = php_version
        self.namespace = namespace
        self.use_type_declarations = use_type_declarations
        self.generate_docs = generate_docs
        self.walker = StructureWalker(self)
    
    @property
    def format_name(self) -> str:
        """Return format name."""
        return "PHP"
    
    @property
    def file_extension(self) -> str:
        """Return file extension."""
        return "php"
    
    def convert(self, manifest: Dict[str, Any], **kwargs) -> ConversionResult:
        """
        Convert manifest to PHP class.
        
        Args:
            manifest: Processed YAML manifest
            **kwargs: Additional conversion options
            
        Returns:
            ConversionResult with PHP content
        """
        try:
            # Extract components
            metadata = self.extract_metadata(manifest)
            styles = self.extract_styles(manifest)
            imports = self.extract_imports(manifest)
            structure = manifest.get('structure', {})
            interactions = manifest.get('interactions', {})
            
            # Generate class name
            class_name = self._generate_class_name(metadata)
            
            # Generate PHP class components
            class_header = self._generate_class_header(class_name, metadata)
            properties = self._generate_properties(metadata, styles, interactions)
            constructor = self._generate_constructor(metadata, interactions)
            methods = self._generate_methods(structure, styles, interactions)
            
            # Combine into complete PHP class
            php_content = self._combine_class_sections(
                class_header, properties, constructor, methods
            )
            
            # Apply optimizations
            if self.optimize_output:
                php_content = self.optimize_code(php_content)
            
            # Add header comment
            php_content = self.add_header_comment(php_content, manifest)
            
            # Generate filename
            filename = self.generate_filename(manifest, kwargs.get('filename'))
            if not filename.endswith('.php'):
                filename = f"{class_name}.php"
            
            return ConversionResult(
                content=php_content,
                filename=filename,
                format_type=self.format_name.lower(),
                metadata={
                    'class_name': class_name,
                    'namespace': self.namespace,
                    'php_version': self.php_version,
                    'has_styles': bool(styles),
                    'method_count': len(self._extract_methods_from_interactions(interactions)) + 2  # +render +getStyles
                }
            )
            
        except Exception as e:
            raise self.handle_conversion_error(e, "PHP conversion")
    
    def _generate_class_name(self, metadata: Dict[str, Any]) -> str:
        """Generate valid PHP class name."""
        title = metadata.get('title', 'Component')
        
        # Remove special chars but preserve word boundaries
        name = re.sub(r'[^\w\s]', '', title)
        
        # If already PascalCase (no spaces), preserve it if valid
        if ' ' not in name and name and name[0].isupper():
            # Always add Component suffix for PHP classes
            name += 'Component'
            return name
        
        # Convert to PascalCase from space-separated words
        words = name.split()
        name = ''.join(word.capitalize() for word in words)
        
        # Ensure it starts with uppercase letter
        if not name or not name[0].isupper():
            name = f"Generated{name}"
        
        # Always add Component suffix for PHP classes
        name += 'Component'
        
        return name
    
    def _generate_class_header(self, class_name: str, metadata: Dict[str, Any]) -> str:
        """Generate PHP class header with namespace and use statements."""
        header_parts = ['<?php']
        header_parts.append('')
        
        # Namespace
        if self.namespace:
            header_parts.append(f'namespace {self.namespace};')
            header_parts.append('')
        
        # Use statements (common dependencies)
        header_parts.append('use InvalidArgumentException;')
        header_parts.append('use RuntimeException;')
        header_parts.append('')
        
        # Class declaration with PHPDoc
        if self.generate_docs:
            description = metadata.get('description', f'{class_name} - Generated by WhyML')
            version = metadata.get('version', '1.0.0')
            
            header_parts.extend([
                '/**',
                f' * {description}',
                ' *',
                f' * @version {version}',
                ' * @author WhyML Generator',
                ' * @package ' + (self.namespace or 'App\\Components'),
                ' */'
            ])
        
        header_parts.append(f'class {class_name}')
        header_parts.append('{')
        
        return '\n'.join(header_parts)
    
    def _generate_properties(self, 
                           metadata: Dict[str, Any], 
                           styles: Dict[str, str], 
                           interactions: Dict[str, Any]) -> List[str]:
        """Generate class properties."""
        properties = []
        
        # Component data properties
        if self.generate_docs:
            properties.extend([
                '    /**',
                '     * Component data',
                '     * @var array',
                '     */'
            ])
        
        if self.use_type_declarations:
            properties.append('    private array $data = [];')
        else:
            properties.append('    private $data = [];')
        
        properties.append('')
        
        # Styles property
        if styles:
            if self.generate_docs:
                properties.extend([
                    '    /**',
                    '     * Component styles',
                    '     * @var array',
                    '     */'
                ])
            
            styles_array = self._format_php_array(styles, 2)
            if self.use_type_declarations:
                properties.append(f'    private array $styles = {styles_array};')
            else:
                properties.append(f'    private $styles = {styles_array};')
            
            properties.append('')
        
        # Configuration properties from interactions
        for key, value in interactions.items():
            if key.startswith('config') or key.startswith('setting'):
                prop_name = key.replace('config', '').replace('setting', '').lower()
                if prop_name:
                    if self.generate_docs:
                        properties.extend([
                            f'    /**',
                            f'     * {prop_name.capitalize()} configuration',
                            f'     * @var mixed',
                            f'     */'
                        ])
                    
                    php_value = self._convert_value_to_php(value)
                    properties.append(f'    private ${prop_name} = {php_value};')
                    properties.append('')
        
        return properties
    
    def _generate_constructor(self, metadata: Dict[str, Any], interactions: Dict[str, Any]) -> List[str]:
        """Generate class constructor."""
        constructor = []
        
        # Constructor parameters
        params = []
        if self.use_type_declarations:
            params.append('array $data = []')
        else:
            params.append('$data = []')
        
        # PHPDoc
        if self.generate_docs:
            constructor.extend([
                '    /**',
                '     * Constructor',
                '     * @param array $data Initial component data',
                '     */'
            ])
        
        # Constructor signature
        if self.use_type_declarations:
            constructor.append(f'    public function __construct({", ".join(params)}): void')
        else:
            constructor.append(f'    public function __construct({", ".join(params)})')
        
        constructor.append('    {')
        constructor.append('        $this->data = $data;')
        
        # Initialize configuration from interactions
        for key, value in interactions.items():
            if key.startswith('config') or key.startswith('setting'):
                prop_name = key.replace('config', '').replace('setting', '').lower()
                if prop_name:
                    constructor.append(f'        $this->{prop_name} = $data[\'{prop_name}\'] ?? $this->{prop_name};')
        
        constructor.append('    }')
        constructor.append('')
        
        return constructor
    
    def _generate_methods(self, 
                         structure: Dict[str, Any], 
                         styles: Dict[str, str], 
                         interactions: Dict[str, Any]) -> List[str]:
        """Generate class methods."""
        methods = []
        
        # Main render method
        methods.extend(self._generate_render_method(structure, styles))
        methods.append('')
        
        # Styles method
        if styles:
            methods.extend(self._generate_styles_method(styles))
            methods.append('')
        
        # Data manipulation methods
        methods.extend(self._generate_data_methods())
        methods.append('')
        
        # Custom methods from interactions
        custom_methods = self._extract_methods_from_interactions(interactions)
        for method_name, method_body in custom_methods.items():
            methods.extend(self._generate_custom_method(method_name, method_body))
            methods.append('')
        
        # HTML utility methods
        methods.extend(self._generate_html_utility_methods())
        
        return methods
    
    def _generate_render_method(self, structure: Dict[str, Any], styles: Dict[str, str]) -> List[str]:
        """Generate main render method."""
        method = []
        
        if self.generate_docs:
            method.extend([
                '    /**',
                '     * Render the component',
                '     * @return string HTML output',
                '     */'
            ])
        
        if self.use_type_declarations:
            method.append('    public function render(): string')
        else:
            method.append('    public function render()')
        
        method.append('    {')
        method.append('        $html = \'\';')
        method.append('')
        
        # Generate HTML from structure
        html_generation = self._generate_html_from_structure(structure, styles)
        method.extend([f'        {line}' for line in html_generation])
        
        method.append('')
        method.append('        return $html;')
        method.append('    }')
        
        return method
    
    def _generate_styles_method(self, styles: Dict[str, str]) -> List[str]:
        """Generate styles method."""
        method = []
        
        if self.generate_docs:
            method.extend([
                '    /**',
                '     * Get component styles as CSS',
                '     * @return string CSS styles',
                '     */'
            ])
        
        if self.use_type_declarations:
            method.append('    public function getStyles(): string')
        else:
            method.append('    public function getStyles()')
        
        method.append('    {')
        method.append('        $css = \'\';')
        method.append('')
        
        # Generate CSS from styles
        for selector, rules in styles.items():
            css_selector = self._format_css_selector(selector)
            method.append(f'        $css .= \'{css_selector} {{ {rules} }}\' . "\\n";')
        
        method.append('')
        method.append('        return $css;')
        method.append('    }')
        
        return method
    
    def _generate_data_methods(self) -> List[str]:
        """Generate data manipulation methods."""
        methods = []
        
        # Set data method
        if self.generate_docs:
            methods.extend([
                '    /**',
                '     * Set component data',
                '     * @param string $key Data key',
                '     * @param mixed $value Data value',
                '     * @return self',
                '     */'
            ])
        
        if self.use_type_declarations:
            methods.append('    public function setData(string $key, mixed $value): self')
        else:
            methods.append('    public function setData($key, $value)')
        
        methods.extend([
            '    {',
            '        $this->data[$key] = $value;',
            '        return $this;',
            '    }',
            ''
        ])
        
        # Get data method
        if self.generate_docs:
            methods.extend([
                '    /**',
                '     * Get component data',
                '     * @param string $key Data key',
                '     * @param mixed $default Default value',
                '     * @return mixed',
                '     */'
            ])
        
        if self.use_type_declarations:
            methods.append('    public function getData(string $key, mixed $default = null): mixed')
        else:
            methods.append('    public function getData($key, $default = null)')
        
        methods.extend([
            '    {',
            '        return $this->data[$key] ?? $default;',
            '    }',
            ''
        ])
        
        return methods
    
    def _generate_custom_method(self, method_name: str, method_body: str) -> List[str]:
        """Generate custom method from interactions."""
        method = []
        
        if self.generate_docs:
            method.extend([
                '    /**',
                f'     * {method_name.capitalize()} method',
                '     * @return mixed',
                '     */'
            ])
        
        formatted_name = re.sub(r'[^a-zA-Z0-9_]', '', method_name)
        
        if self.use_type_declarations:
            method.append(f'    public function {formatted_name}(): mixed')
        else:
            method.append(f'    public function {formatted_name}()')
        
        method.append('    {')
        
        # Convert method body to PHP
        php_body = self._convert_method_body_to_php(method_body)
        method.extend([f'        {line}' for line in php_body])
        
        method.append('    }')
        
        return method
    
    def _generate_html_utility_methods(self) -> List[str]:
        """Generate HTML utility methods."""
        methods = []
        
        # HTML escape method
        if self.generate_docs:
            methods.extend([
                '    /**',
                '     * Escape HTML content',
                '     * @param string $content Content to escape',
                '     * @return string Escaped content',
                '     */'
            ])
        
        if self.use_type_declarations:
            methods.append('    private function escapeHtml(string $content): string')
        else:
            methods.append('    private function escapeHtml($content)')
        
        methods.extend([
            '    {',
            '        return htmlspecialchars($content, ENT_QUOTES | ENT_HTML5, \'UTF-8\');',
            '    }',
            ''
        ])
        
        # Build attributes method
        if self.generate_docs:
            methods.extend([
                '    /**',
                '     * Build HTML attributes string',
                '     * @param array $attributes Attributes array',
                '     * @return string Attributes string',
                '     */'
            ])
        
        if self.use_type_declarations:
            methods.append('    private function buildAttributes(array $attributes): string')
        else:
            methods.append('    private function buildAttributes($attributes)')
        
        methods.extend([
            '    {',
            '        $attr = [];',
            '        foreach ($attributes as $key => $value) {',
            '            if ($value !== null && $value !== false) {',
            '                $attr[] = $key . \'="\' . $this->escapeHtml($value) . \'"\';',
            '            }',
            '        }',
            '        return empty($attr) ? \'\' : \' \' . implode(\' \', $attr);',
            '    }'
        ])
        
        return methods
    
    def _generate_html_from_structure(self, structure: Dict[str, Any], styles: Dict[str, str]) -> List[str]:
        """Generate HTML building code from structure."""
        html_code = []
        
        def process_element(element, indent=0):
            if isinstance(element, dict):
                # Find the HTML element
                tag_name = 'div'
                attributes = {}
                children = []
                text_content = None
                
                for key, value in element.items():
                    if key in ['text', 'content']:
                        text_content = value
                    elif key == 'children':
                        if isinstance(value, list):
                            children.extend(value)
                        else:
                            children.append(value)
                    elif key == 'style':
                        if value in styles:
                            attributes['class'] = value
                        else:
                            attributes['style'] = value
                    elif key in ['class', 'id', 'src', 'href', 'alt', 'title']:
                        attributes[key] = value
                    elif self._is_html_element(key):
                        tag_name = key
                        if isinstance(value, dict):
                            children.append(value)
                        else:
                            text_content = value
                
                # Generate PHP code for this element
                attr_code = self._generate_attributes_code(attributes)
                
                if text_content is not None:
                    content_var = f'$this->escapeHtml({self._convert_value_to_php(text_content)})'
                    html_code.append(f'$html .= \'<{tag_name}\' . {attr_code} . \'>\' . {content_var} . \'</{tag_name}>\';')
                elif children:
                    html_code.append(f'$html .= \'<{tag_name}\' . {attr_code} . \'>\';')
                    for child in children:
                        process_element(child, indent + 1)
                    html_code.append(f'$html .= \'</{tag_name}>\';')
                else:
                    if tag_name in ['img', 'br', 'hr', 'input']:
                        html_code.append(f'$html .= \'<{tag_name}\' . {attr_code} . \'>\';')
                    else:
                        html_code.append(f'$html .= \'<{tag_name}\' . {attr_code} . \'></{tag_name}>\';')
            
            elif isinstance(element, list):
                for item in element:
                    process_element(item, indent)
            else:
                # Text content
                content_var = f'$this->escapeHtml({self._convert_value_to_php(element)})'
                html_code.append(f'$html .= {content_var};')
        
        process_element(structure)
        return html_code
    
    def _generate_attributes_code(self, attributes: Dict[str, Any]) -> str:
        """Generate PHP code for building HTML attributes."""
        if not attributes:
            return '\'\''
        
        attr_array = []
        for key, value in attributes.items():
            php_value = self._convert_value_to_php(value)
            attr_array.append(f'\'{key}\' => {php_value}')
        
        return f'$this->buildAttributes([{", ".join(attr_array)}])'
    
    def _extract_methods_from_interactions(self, interactions: Dict[str, Any]) -> Dict[str, str]:
        """Extract custom methods from interactions."""
        methods = {}
        
        for key, value in interactions.items():
            if key.startswith('method') or key.startswith('function'):
                method_name = key.replace('method', '').replace('function', '').lower()
                if method_name:
                    methods[method_name] = str(value)
        
        return methods
    
    def _convert_method_body_to_php(self, body: str) -> List[str]:
        """Convert method body to PHP code."""
        # Basic conversion - this could be enhanced
        lines = body.split('\n')
        php_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Ensure line ends with semicolon if it's a statement
                if not line.endswith((';', '{', '}')):
                    line += ';'
                php_lines.append(line)
        
        return php_lines if php_lines else ['// TODO: Implement method']
    
    def _combine_class_sections(self, header: str, properties: List[str], constructor: List[str], methods: List[str]) -> str:
        """Combine all class sections into complete PHP class."""
        class_parts = [header]
        
        if properties:
            class_parts.extend(properties)
        
        if constructor:
            class_parts.extend(constructor)
        
        if methods:
            class_parts.extend(methods)
        
        class_parts.append('}')
        
        return '\n'.join(class_parts)
    
    def _format_php_array(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Format PHP array from dictionary."""
        if not data:
            return '[]'
        
        indent_str = '    ' * indent
        items = []
        
        for key, value in data.items():
            php_key = f"'{key}'"
            php_value = self._convert_value_to_php(value)
            items.append(f'{indent_str}    {php_key} => {php_value}')
        
        return '[\n' + ',\n'.join(items) + f'\n{indent_str}]'
    
    def _convert_value_to_php(self, value: Any) -> str:
        """Convert Python value to PHP representation."""
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            # Escape single quotes and wrap in single quotes
            escaped = value.replace("'", "\\'")
            return f"'{escaped}'"
        elif isinstance(value, list):
            php_items = [self._convert_value_to_php(item) for item in value]
            return '[' + ', '.join(php_items) + ']'
        elif isinstance(value, dict):
            return self._format_php_array(value)
        else:
            return f"'{str(value)}'"
    
    def _format_css_selector(self, selector: str) -> str:
        """Format CSS selector from style name."""
        kebab_case = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', selector).lower()
        if not kebab_case.startswith('.') and not kebab_case.startswith('#'):
            kebab_case = f'.{kebab_case}'
        return kebab_case
    
    def _is_html_element(self, name: str) -> bool:
        """Check if name is a valid HTML element."""
        return name.lower() in {
            'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'thead', 'tbody',
            'form', 'input', 'textarea', 'select', 'option', 'button', 'label',
            'a', 'img', 'video', 'audio', 'br', 'hr',
            'header', 'nav', 'main', 'section', 'article', 'aside', 'footer'
        }
    
    def _format_header_comment(self, title: str, description: str) -> str:
        """Format PHP header comment."""
        parts = [f"Generated by WhyML - {title}"]
        if description:
            parts.append(f"Description: {description}")
        parts.append("PHP Component Class")
        
        comment_content = "\n".join(f" * {part}" for part in parts)
        return f"<?php\n/**\n{comment_content}\n */"
