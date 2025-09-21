"""
WhyML Converters - React Converter Module

Advanced React/JSX converter with component generation, modern React patterns,
TypeScript support, and optimized JSX output.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import re

from whyml_core.utils import StringUtils
from whyml_core.exceptions import ProcessingError
from .base_converter import BaseConverter


class ReactConverter(BaseConverter):
    """Advanced React/JSX converter with modern React patterns and TypeScript support."""
    
    def __init__(self, **kwargs):
        """Initialize React converter."""
        super().__init__(**kwargs)
        self.indent_size = 2
        self.current_indent = 0
        self.use_typescript = False
        self.component_name = "WhyMLComponent"
    
    def _get_output_format(self) -> str:
        """Get output format identifier."""
        return "react"
    
    def _get_template_extension(self) -> str:
        """Get template file extension."""
        return ".jsx"
    
    def _supports_components(self) -> bool:
        """Check if converter supports components."""
        return True
    
    async def convert_manifest(self, 
                              manifest: Dict[str, Any],
                              output_path: Optional[Union[str, Path]] = None,
                              **options) -> str:
        """Convert WhyML manifest to React component.
        
        Args:
            manifest: WhyML manifest dictionary
            output_path: Optional output file path
            **options: React-specific options
            
        Returns:
            Generated React/JSX content
        """
        # Configure options
        self.use_typescript = options.get('typescript', False)
        self.component_name = options.get('component_name', 'WhyMLComponent')
        self.component_name = self._sanitize_class_name(self.component_name)
        
        # Reset indentation
        self.current_indent = 0
        
        # Extract manifest sections
        metadata = self._extract_metadata(manifest)
        structure = self._extract_structure(manifest)
        styles = self._extract_styles(manifest)
        scripts = self._extract_scripts(manifest)
        imports = self._extract_imports(manifest)
        
        # Build React component
        component_parts = []
        
        # Imports section
        component_parts.append(self._generate_imports(imports, **options))
        
        # Styles (if using CSS-in-JS)
        if options.get('css_in_js') and styles:
            component_parts.append(self._generate_css_in_js(styles))
        
        # Component definition
        component_parts.append(await self._generate_component(
            metadata, structure, styles, scripts, **options
        ))
        
        # Export statement
        component_parts.append(self._generate_export())
        
        return '\n\n'.join(filter(None, component_parts))
    
    def _generate_imports(self, imports: Dict[str, Any], **options) -> str:
        """Generate import statements."""
        import_lines = []
        
        # React import
        if self.use_typescript:
            import_lines.append("import React from 'react';")
        else:
            import_lines.append("import React from 'react';")
        
        # Additional React imports
        react_features = options.get('react_features', [])
        if react_features:
            features = ', '.join(react_features)
            import_lines.append(f"import {{ {features} }} from 'react';")
        
        # External dependencies
        external_deps = options.get('dependencies', [])
        for dep in external_deps:
            if isinstance(dep, str):
                import_lines.append(f"import '{dep}';")
            elif isinstance(dep, dict):
                module = dep.get('module', '')
                imports_list = dep.get('imports', [])
                default_import = dep.get('default')
                
                if default_import and imports_list:
                    import_line = f"import {default_import}, {{ {', '.join(imports_list)} }} from '{module}';"
                elif default_import:
                    import_line = f"import {default_import} from '{module}';"
                elif imports_list:
                    import_line = f"import {{ {', '.join(imports_list)} }} from '{module}';"
                else:
                    import_line = f"import '{module}';"
                
                import_lines.append(import_line)
        
        # CSS imports
        stylesheets = imports.get('stylesheets', [])
        for stylesheet in stylesheets:
            href = stylesheet.get('href', '')
            if href.endswith('.css'):
                import_lines.append(f"import '{href}';")
        
        return '\n'.join(import_lines)
    
    def _generate_css_in_js(self, styles: Dict[str, Any]) -> str:
        """Generate CSS-in-JS styles object."""
        css_lines = []
        
        if self.use_typescript:
            css_lines.append("const styles: { [key: string]: React.CSSProperties } = {")
        else:
            css_lines.append("const styles = {")
        
        self._increase_indent()
        
        # Process styles
        style_objects = {}
        
        # Process inline styles
        inline_styles = styles.get('inline_styles', {})
        for element_id, properties in inline_styles.items():
            if properties:
                style_name = self._sanitize_style_name(element_id)
                style_objects[style_name] = properties
        
        # Process internal styles
        internal_styles = styles.get('internal_styles', {})
        for style_name, rules in internal_styles.items():
            if isinstance(rules, dict):
                for selector, properties in rules.items():
                    style_name = self._sanitize_style_name(selector)
                    style_objects[style_name] = properties
        
        # Generate style objects
        for style_name, properties in style_objects.items():
            css_lines.append(self._indent() + f"{style_name}: {{")
            self._increase_indent()
            
            for prop, value in properties.items():
                # Convert CSS property to camelCase
                react_prop = self._css_to_camel_case(prop)
                # Handle CSS values
                css_value = self._format_css_value(value)
                css_lines.append(self._indent() + f"{react_prop}: {css_value},")
            
            self._decrease_indent()
            css_lines.append(self._indent() + "},")
        
        self._decrease_indent()
        css_lines.append("};")
        
        return '\n'.join(css_lines)
    
    async def _generate_component(self, 
                                 metadata: Dict[str, Any],
                                 structure: Dict[str, Any],
                                 styles: Dict[str, Any],
                                 scripts: Dict[str, Any],
                                 **options) -> str:
        """Generate React component definition."""
        component_lines = []
        
        # Component props interface (TypeScript)
        if self.use_typescript:
            component_lines.append(self._generate_props_interface(**options))
        
        # Component definition
        if options.get('functional', True):
            component_lines.append(await self._generate_functional_component(
                metadata, structure, styles, scripts, **options
            ))
        else:
            component_lines.append(await self._generate_class_component(
                metadata, structure, styles, scripts, **options
            ))
        
        return '\n\n'.join(filter(None, component_lines))
    
    def _generate_props_interface(self, **options) -> str:
        """Generate TypeScript props interface."""
        props = options.get('props', {})
        
        if not props:
            return f"interface {self.component_name}Props {{}}"
        
        interface_lines = [f"interface {self.component_name}Props {{"]
        
        for prop_name, prop_config in props.items():
            prop_type = prop_config.get('type', 'any')
            optional = prop_config.get('optional', True)
            description = prop_config.get('description')
            
            if description:
                interface_lines.append(f"  /** {description} */")
            
            optional_marker = '?' if optional else ''
            interface_lines.append(f"  {prop_name}{optional_marker}: {prop_type};")
        
        interface_lines.append("}")
        
        return '\n'.join(interface_lines)
    
    async def _generate_functional_component(self, 
                                           metadata: Dict[str, Any],
                                           structure: Dict[str, Any],
                                           styles: Dict[str, Any],
                                           scripts: Dict[str, Any],
                                           **options) -> str:
        """Generate functional React component."""
        component_lines = []
        
        # Component signature
        if self.use_typescript:
            props_type = f"{self.component_name}Props" if options.get('props') else "{}"
            component_lines.append(f"const {self.component_name}: React.FC<{props_type}> = (props) => {{")
        else:
            component_lines.append(f"const {self.component_name} = (props) => {{")
        
        self._increase_indent()
        
        # Hooks and state
        hooks = options.get('hooks', [])
        for hook in hooks:
            component_lines.append(self._indent() + hook)
        
        # Component logic (from scripts)
        if scripts:
            logic_code = self._extract_component_logic(scripts)
            if logic_code:
                component_lines.append('')
                component_lines.append(self._indent_text(logic_code, self.current_indent))
        
        # JSX return
        component_lines.append('')
        component_lines.append(self._indent() + "return (")
        
        self._increase_indent()
        jsx_content = await self._generate_jsx(structure, metadata, **options)
        component_lines.append(jsx_content)
        self._decrease_indent()
        
        component_lines.append(self._indent() + ");")
        
        self._decrease_indent()
        component_lines.append("};")
        
        return '\n'.join(component_lines)
    
    async def _generate_class_component(self, 
                                      metadata: Dict[str, Any],
                                      structure: Dict[str, Any],
                                      styles: Dict[str, Any],
                                      scripts: Dict[str, Any],
                                      **options) -> str:
        """Generate class-based React component."""
        component_lines = []
        
        # Class definition
        if self.use_typescript:
            props_type = f"{self.component_name}Props" if options.get('props') else "{}"
            component_lines.append(f"class {self.component_name} extends React.Component<{props_type}> {{")
        else:
            component_lines.append(f"class {self.component_name} extends React.Component {{")
        
        self._increase_indent()
        
        # Constructor
        if options.get('state') or scripts:
            component_lines.append(self._generate_constructor(**options))
        
        # Component methods (from scripts)
        if scripts:
            methods = self._extract_component_methods(scripts)
            component_lines.extend(methods)
        
        # Render method
        component_lines.append('')
        component_lines.append(self._indent() + "render() {")
        
        self._increase_indent()
        component_lines.append(self._indent() + "return (")
        
        self._increase_indent()
        jsx_content = await self._generate_jsx(structure, metadata, **options)
        component_lines.append(jsx_content)
        self._decrease_indent()
        
        component_lines.append(self._indent() + ");")
        self._decrease_indent()
        component_lines.append(self._indent() + "}")
        
        self._decrease_indent()
        component_lines.append("}")
        
        return '\n'.join(component_lines)
    
    def _generate_constructor(self, **options) -> str:
        """Generate component constructor."""
        constructor_lines = []
        
        constructor_lines.append(self._indent() + "constructor(props) {")
        self._increase_indent()
        
        constructor_lines.append(self._indent() + "super(props);")
        
        # Initial state
        state = options.get('state', {})
        if state:
            constructor_lines.append('')
            constructor_lines.append(self._indent() + "this.state = {")
            self._increase_indent()
            
            for key, value in state.items():
                formatted_value = self._format_js_value(value)
                constructor_lines.append(self._indent() + f"{key}: {formatted_value},")
            
            self._decrease_indent()
            constructor_lines.append(self._indent() + "};")
        
        # Bind methods
        methods = options.get('methods', [])
        if methods:
            constructor_lines.append('')
            for method in methods:
                constructor_lines.append(self._indent() + f"this.{method} = this.{method}.bind(this);")
        
        self._decrease_indent()
        constructor_lines.append(self._indent() + "}")
        
        return '\n'.join(constructor_lines)
    
    async def _generate_jsx(self, 
                           structure: Dict[str, Any], 
                           metadata: Dict[str, Any],
                           **options) -> str:
        """Generate JSX content from structure."""
        if not structure:
            return self._indent() + "<div>No content</div>"
        
        # Handle different structure formats
        if 'tag' in structure:
            # Single element
            return await self._generate_jsx_element(structure)
        elif 'children' in structure:
            # Fragment with children
            return await self._generate_jsx_fragment(structure['children'])
        else:
            # Process as container
            return await self._generate_jsx_container(structure)
    
    async def _generate_jsx_element(self, element: Dict[str, Any]) -> str:
        """Generate JSX element from structure definition."""
        tag = element.get('tag', 'div')
        
        # Convert HTML tags to React equivalents
        react_tag = self._html_to_react_tag(tag)
        
        # Handle self-closing tags
        self_closing_tags = {'img', 'br', 'hr', 'input', 'meta', 'link'}
        is_self_closing = react_tag in self_closing_tags
        
        # Build opening tag with props
        opening_tag = await self._build_jsx_opening_tag(react_tag, element)
        
        if is_self_closing:
            return self._indent() + opening_tag
        
        # Handle content
        content = element.get('content', '')
        children = element.get('children', [])
        
        if not content and not children:
            # Empty element
            return self._indent() + f"<{react_tag}></{react_tag}>"
        
        if content and not children:
            # Element with text content only
            if '\n' in content or len(content) > 80:
                # Multi-line content
                return (self._indent() + opening_tag + '\n' +
                       self._indent_text(self._escape_jsx_content(content), self.current_indent + 1) + '\n' +
                       self._indent() + f"</{react_tag}>")
            else:
                # Single line content
                return self._indent() + f"{opening_tag}{self._escape_jsx_content(content)}</{react_tag}>"
        
        # Element with children
        element_parts = [self._indent() + opening_tag]
        
        if content:
            self._increase_indent()
            element_parts.append(self._indent() + self._escape_jsx_content(content))
            self._decrease_indent()
        
        if children:
            self._increase_indent()
            children_content = await self._generate_jsx_children(children)
            element_parts.append(children_content)
            self._decrease_indent()
        
        element_parts.append(self._indent() + f"</{react_tag}>")
        
        return '\n'.join(element_parts)
    
    async def _build_jsx_opening_tag(self, tag: str, element: Dict[str, Any]) -> str:
        """Build opening JSX tag with props."""
        attributes = element.get('attributes', {})
        
        prop_parts = []
        for name, value in attributes.items():
            if value is None or value is False:
                continue
            elif value is True:
                # Boolean prop
                prop_parts.append(name)
            else:
                # Convert HTML attributes to React props
                react_prop = self._html_to_react_prop(name)
                
                # Handle special prop values
                if react_prop in ['style'] and isinstance(value, str):
                    # Convert inline style string to object
                    style_obj = self._parse_inline_style(value)
                    prop_value = f"{{{style_obj}}}"
                elif react_prop in ['className'] and isinstance(value, list):
                    # Handle class arrays
                    prop_value = f'"{" ".join(value)}"'
                else:
                    # Regular prop
                    prop_value = f'"{self._escape_jsx_attribute(str(value))}"'
                
                prop_parts.append(f'{react_prop}={prop_value}')
        
        if prop_parts:
            return f"<{tag} {' '.join(prop_parts)}>"
        else:
            return f"<{tag}>"
    
    async def _generate_jsx_children(self, children: List[Any]) -> str:
        """Generate JSX for list of child elements."""
        child_parts = []
        
        for child in children:
            if isinstance(child, dict):
                if child.get('type') == 'text':
                    # Text node
                    text_content = child.get('content', '')
                    if text_content:
                        child_parts.append(self._indent() + self._escape_jsx_content(text_content))
                else:
                    # Element node
                    child_content = await self._generate_jsx_element(child)
                    child_parts.append(child_content)
            elif isinstance(child, str):
                # Direct text content
                child_parts.append(self._indent() + self._escape_jsx_content(child))
        
        return '\n'.join(child_parts)
    
    async def _generate_jsx_fragment(self, children: List[Any]) -> str:
        """Generate JSX Fragment for multiple root elements."""
        fragment_parts = [self._indent() + "<React.Fragment>"]
        
        self._increase_indent()
        children_content = await self._generate_jsx_children(children)
        fragment_parts.append(children_content)
        self._decrease_indent()
        
        fragment_parts.append(self._indent() + "</React.Fragment>")
        
        return '\n'.join(fragment_parts)
    
    async def _generate_jsx_container(self, structure: Dict[str, Any]) -> str:
        """Generate JSX for container structure."""
        container_parts = []
        
        for key, value in structure.items():
            if isinstance(value, dict):
                element_content = await self._generate_jsx_element(value)
                container_parts.append(element_content)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        element_content = await self._generate_jsx_element(item)
                        container_parts.append(element_content)
        
        if len(container_parts) == 1:
            return container_parts[0]
        elif len(container_parts) > 1:
            return await self._generate_jsx_fragment([{'content': part} for part in container_parts])
        else:
            return self._indent() + "<div>No content</div>"
    
    def _generate_export(self) -> str:
        """Generate export statement."""
        return f"export default {self.component_name};"
    
    # Helper methods
    
    def _html_to_react_tag(self, html_tag: str) -> str:
        """Convert HTML tag to React equivalent."""
        # Most HTML tags work directly in React
        return html_tag
    
    def _html_to_react_prop(self, html_attr: str) -> str:
        """Convert HTML attribute to React prop."""
        # Common HTML to React prop conversions
        conversions = {
            'class': 'className',
            'for': 'htmlFor',
            'tabindex': 'tabIndex',
            'readonly': 'readOnly',
            'maxlength': 'maxLength',
            'cellpadding': 'cellPadding',
            'cellspacing': 'cellSpacing',
            'rowspan': 'rowSpan',
            'colspan': 'colSpan',
            'usemap': 'useMap',
            'frameborder': 'frameBorder'
        }
        
        return conversions.get(html_attr.lower(), html_attr)
    
    def _css_to_camel_case(self, css_prop: str) -> str:
        """Convert CSS property to camelCase."""
        parts = css_prop.split('-')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])
    
    def _sanitize_style_name(self, style_name: str) -> str:
        """Sanitize CSS selector for use as JS object key."""
        # Remove CSS selector prefixes and special characters
        cleaned = re.sub(r'^[.#]', '', style_name)
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', cleaned)
        return cleaned or 'style'
    
    def _format_css_value(self, value: str) -> str:
        """Format CSS value for JavaScript."""
        value = str(value).strip()
        
        # Numeric values (without units become numbers)
        if value.isdigit():
            return value
        
        # String values need quotes
        return f"'{value}'"
    
    def _format_js_value(self, value: Any) -> str:
        """Format Python value for JavaScript."""
        if isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            items = [self._format_js_value(item) for item in value]
            return f"[{', '.join(items)}]"
        elif isinstance(value, dict):
            items = [f"{key}: {self._format_js_value(val)}" for key, val in value.items()]
            return f"{{{', '.join(items)}}}"
        else:
            return f"'{str(value)}'"
    
    def _parse_inline_style(self, style_str: str) -> str:
        """Parse inline CSS style string to React style object."""
        style_props = []
        
        for declaration in style_str.split(';'):
            declaration = declaration.strip()
            if ':' in declaration:
                prop, value = declaration.split(':', 1)
                prop = prop.strip()
                value = value.strip()
                
                if prop and value:
                    react_prop = self._css_to_camel_case(prop)
                    formatted_value = self._format_css_value(value)
                    style_props.append(f"{react_prop}: {formatted_value}")
        
        return f"{{{', '.join(style_props)}}}"
    
    def _escape_jsx_content(self, content: str) -> str:
        """Escape content for JSX."""
        # Basic JSX escaping - braces need to be escaped
        content = content.replace('{', '\\{').replace('}', '\\}')
        return content
    
    def _escape_jsx_attribute(self, value: str) -> str:
        """Escape attribute value for JSX."""
        return value.replace('"', '\\"').replace('{', '\\{').replace('}', '\\}')
    
    def _extract_component_logic(self, scripts: Dict[str, Any]) -> str:
        """Extract component logic from scripts."""
        # Extract and adapt JavaScript for React component
        logic_parts = []
        
        inline_scripts = scripts.get('inline_scripts', [])
        for script in inline_scripts:
            content = script.get('content', '')
            if content:
                # Basic adaptation of JS to React patterns
                adapted_content = self._adapt_js_to_react(content)
                logic_parts.append(adapted_content)
        
        return '\n\n'.join(logic_parts)
    
    def _extract_component_methods(self, scripts: Dict[str, Any]) -> List[str]:
        """Extract component methods from scripts."""
        methods = []
        
        inline_scripts = scripts.get('inline_scripts', [])
        for script in inline_scripts:
            content = script.get('content', '')
            if content:
                # Extract function definitions and convert to class methods
                method_content = self._adapt_js_to_class_methods(content)
                if method_content:
                    methods.append(method_content)
        
        return methods
    
    def _adapt_js_to_react(self, js_content: str) -> str:
        """Adapt JavaScript content for React functional component."""
        # Basic adaptations - this could be more sophisticated
        adapted = js_content
        
        # Replace DOM queries with refs or state
        adapted = re.sub(r'document\.getElementById\([\'"]([^\'"]*)[\'""]\)', 
                        r'/* Use ref or state for \1 */', adapted)
        
        return adapted
    
    def _adapt_js_to_class_methods(self, js_content: str) -> str:
        """Adapt JavaScript content for React class methods."""
        # Basic adaptation to class method format
        if 'function' in js_content:
            # Convert function declarations to class methods
            adapted = re.sub(r'function\s+(\w+)\s*\([^)]*\)\s*\{',
                           r'\1() {', js_content)
            return self._indent_text(adapted, self.current_indent)
        
        return ""
    
    def _indent(self) -> str:
        """Get current indentation string."""
        return ' ' * (self.current_indent * self.indent_size)
    
    def _increase_indent(self) -> None:
        """Increase indentation level."""
        self.current_indent += 1
    
    def _decrease_indent(self) -> None:
        """Decrease indentation level."""
        self.current_indent = max(0, self.current_indent - 1)
    
    def _indent_text(self, text: str, indent_level: int) -> str:
        """Indent text content."""
        lines = text.split('\n')
        indent_str = ' ' * (indent_level * self.indent_size)
        return '\n'.join(indent_str + line if line.strip() else line for line in lines)
