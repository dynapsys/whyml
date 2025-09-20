"""
React Converter - Convert YAML manifests to React JSX components

Generates modern React functional components with hooks, TypeScript support,
and comprehensive styling integration.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
from typing import Any, Dict, List, Optional, Union, Set
from html import escape
import logging

from .base_converter import BaseConverter, ConversionResult, StructureWalker, CSSProcessor
from ..exceptions import ConversionError

logger = logging.getLogger(__name__)


class ReactConverter(BaseConverter):
    """
    Convert YAML manifests to React JSX components.
    
    Features:
    - Modern functional components with hooks
    - TypeScript support
    - CSS Modules and styled-components integration
    - Props interface generation
    - Event handler generation
    - Responsive design support
    """
    
    def __init__(self, 
                 use_typescript: bool = True,
                 use_hooks: bool = True,
                 css_framework: str = "css-modules",  # css-modules, styled-components, emotion
                 export_default: bool = True,
                 **kwargs):
        """
        Initialize React converter.
        
        Args:
            use_typescript: Generate TypeScript interfaces
            use_hooks: Use React hooks (useState, useEffect)
            css_framework: CSS framework to use
            export_default: Use default export
            **kwargs: Additional options passed to base converter
        """
        super().__init__(**kwargs)
        self.use_typescript = use_typescript
        self.use_hooks = use_hooks
        self.css_framework = css_framework
        self.export_default = export_default
        self.walker = StructureWalker(self)
        
        # Track imports needed
        self.required_imports: Set[str] = set()
        self.react_imports: Set[str] = {'React'}
    
    @property
    def format_name(self) -> str:
        """Return format name."""
        return "React"
    
    @property
    def file_extension(self) -> str:
        """Return file extension."""
        return "tsx" if self.use_typescript else "jsx"
    
    def convert(self, manifest: Dict[str, Any], **kwargs) -> ConversionResult:
        """
        Convert manifest to React component.
        
        Args:
            manifest: Processed YAML manifest
            **kwargs: Additional conversion options
            
        Returns:
            ConversionResult with React JSX content
        """
        try:
            # Reset imports for this conversion
            self.required_imports.clear()
            self.react_imports = {'React'}
            
            # Extract components
            metadata = self.extract_metadata(manifest)
            styles = self.extract_styles(manifest)
            imports = self.extract_imports(manifest)
            template_vars = self.extract_template_vars(manifest)
            structure = manifest.get('structure', {})
            interactions = manifest.get('interactions', {})
            
            # Replace template variables in structure BEFORE JSX conversion
            if template_vars:
                structure = self._replace_template_vars_in_structure(structure, template_vars)
            
            # Generate component name
            component_name = self._generate_component_name(metadata)
            
            # Analyze structure for required imports
            self._analyze_structure_for_imports(structure, interactions)
            
            # Generate TypeScript interfaces if enabled
            interfaces = ""
            if self.use_typescript:
                interfaces = self._generate_interfaces(metadata, structure, interactions)
            
            # Generate imports section
            imports_section = self._generate_imports(imports)
            
            # Generate styles
            styles_section = self._generate_styles(styles, component_name)
            
            # Generate component
            component_code = self._generate_component(
                component_name, structure, styles, interactions, metadata
            )
            
            # Combine all sections
            jsx_content = self._combine_sections(
                imports_section, interfaces, styles_section, component_code
            )
            
            # Replace template variables ({{ hero_text }} -> "Welcome to Our Amazing Product")
            if template_vars:
                jsx_content = self.replace_template_variables(jsx_content, template_vars)
            
            # Apply optimizations
            if self.optimize_output:
                jsx_content = self.optimize_code(jsx_content)
            
            # Add header comment
            jsx_content = self.add_header_comment(jsx_content, manifest)
            
            # Generate filename
            filename = self.generate_filename(manifest, kwargs.get('filename'))
            if not filename.endswith(('.jsx', '.tsx')):
                filename = f"{component_name}.{self.file_extension}"
            
            return ConversionResult(
                content=jsx_content,
                filename=filename,
                format_type=self.format_name.lower(),
                metadata={
                    'component_name': component_name,
                    'uses_typescript': self.use_typescript,
                    'uses_hooks': self.use_hooks,
                    'css_framework': self.css_framework,
                    'has_interactions': bool(interactions),
                    'required_imports': list(self.required_imports)
                }
            )
            
        except Exception as e:
            raise self.handle_conversion_error(e, "React conversion")
    
    def _generate_component_name(self, metadata: Dict[str, Any]) -> str:
        """Generate valid React component name."""
        title = metadata.get('title', 'Component')
        
        # Remove special chars but preserve word boundaries
        name = re.sub(r'[^\w\s]', '', title)
        
        # If already PascalCase (no spaces), return as-is if valid
        if ' ' not in name and name and name[0].isupper():
            return name
        
        # Convert to PascalCase from space-separated words
        words = name.split()
        name = ''.join(word.capitalize() for word in words)
        
        # Ensure it starts with uppercase letter
        if not name or not name[0].isupper():
            name = f"Generated{name}"
        
        return name
    
    def _analyze_structure_for_imports(self, structure: Any, interactions: Dict[str, Any]):
        """Analyze structure to determine required React imports."""
        # Check for state usage
        if interactions or self._has_dynamic_content(structure):
            if self.use_hooks:
                self.react_imports.add('useState')
            
        # Check for lifecycle methods
        if self._needs_lifecycle_methods(structure, interactions):
            if self.use_hooks:
                self.react_imports.add('useEffect')
    
    def _has_dynamic_content(self, structure: Any) -> bool:
        """Check if structure contains dynamic content requiring state."""
        def check_dynamic(element, context):
            if isinstance(element, dict):
                # Check for dynamic attributes
                for key, value in element.items():
                    if isinstance(value, str) and ('{{' in value or 'useState' in value):
                        return True
            return False
        
        found = self.walker.find_elements(structure, check_dynamic)
        return len(found) > 0
    
    def _needs_lifecycle_methods(self, structure: Any, interactions: Dict[str, Any]) -> bool:
        """Check if component needs lifecycle methods."""
        return bool(interactions.get('onMount') or interactions.get('onUnmount'))
    
    def _generate_interfaces(self, 
                           metadata: Dict[str, Any], 
                           structure: Any, 
                           interactions: Dict[str, Any]) -> str:
        """Generate TypeScript interfaces."""
        if not self.use_typescript:
            return ""
        
        interfaces = []
        
        # Props interface
        props_interface = self._generate_props_interface(metadata, structure)
        if props_interface:
            interfaces.append(props_interface)
        
        # State interface if using state
        if self._has_dynamic_content(structure) or interactions:
            state_interface = self._generate_state_interface(structure, interactions)
            if state_interface:
                interfaces.append(state_interface)
        
        return '\n\n'.join(interfaces) + '\n\n' if interfaces else ""
    
    def _generate_props_interface(self, metadata: Dict[str, Any], structure: Any) -> str:
        """Generate Props interface."""
        props = []
        
        # Standard props
        props.append("  className?: string;")
        props.append("  style?: React.CSSProperties;")
        
        # Extract props from structure
        structure_props = self._extract_props_from_structure(structure)
        props.extend(structure_props)
        
        if not props:
            return ""
        
        return f"""interface Props {{
{chr(10).join(props)}
}}"""
    
    def _generate_state_interface(self, structure: Any, interactions: Dict[str, Any]) -> str:
        """Generate State interface."""
        state_props = []
        
        # Extract state from interactions
        for key, value in interactions.items():
            if key.startswith('state'):
                prop_name = key.replace('state', '').lower()
                state_props.append(f"  {prop_name}: any;")
        
        # Extract state from dynamic content
        structure_state = self._extract_state_from_structure(structure)
        state_props.extend(structure_state)
        
        if not state_props:
            return ""
        
        return f"""interface State {{
{chr(10).join(state_props)}
}}"""
    
    def _extract_props_from_structure(self, structure: Any) -> List[str]:
        """Extract prop definitions from structure."""
        props = []
        
        def extract_callback(element, context):
            if isinstance(element, dict):
                for key, value in element.items():
                    if isinstance(value, str) and value.startswith('props.'):
                        prop_name = value.replace('props.', '').split('.')[0]
                        props.append(f"  {prop_name}?: any;")
            return element
        
        self.walker.walk(structure, extract_callback)
        return list(set(props))  # Remove duplicates
    
    def _extract_state_from_structure(self, structure: Any) -> List[str]:
        """Extract state definitions from structure."""
        state_props = []
        
        def extract_callback(element, context):
            if isinstance(element, dict):
                for key, value in element.items():
                    if isinstance(value, str) and 'useState' in value:
                        # Extract state variable name from useState call
                        match = re.search(r'(\w+),\s*set\w+\s*=\s*useState', value)
                        if match:
                            var_name = match.group(1)
                            state_props.append(f"  {var_name}: any;")
            return element
        
        self.walker.walk(structure, extract_callback)
        return list(set(state_props))
    
    def _generate_imports(self, imports: Dict[str, List[str]]) -> str:
        """Generate import statements."""
        import_lines = []
        
        # React imports
        react_import = ', '.join(sorted(self.react_imports))
        import_lines.append(f"import {react_import} from 'react';")
        
        # External library imports
        for script in imports.get('scripts', []):
            if script.startswith('http'):
                # External CDN - add as comment
                import_lines.append(f"// External script: {script}")
            else:
                # Local module
                module_name = script.split('/')[-1].replace('.js', '').replace('.ts', '')
                import_lines.append(f"import {module_name} from '{script}';")
        
        # CSS imports
        if self.css_framework == 'css-modules':
            import_lines.append("import styles from './styles.module.css';")
        elif self.css_framework == 'styled-components':
            import_lines.append("import styled from 'styled-components';")
            self.required_imports.add('styled-components')
        
        # Additional required imports
        for import_name in sorted(self.required_imports):
            import_lines.append(f"import '{import_name}';")
        
        return '\n'.join(import_lines) + '\n\n'
    
    def _generate_styles(self, styles: Dict[str, str], component_name: str) -> str:
        """Generate styles section based on CSS framework."""
        if not styles:
            return ""
        
        if self.css_framework == 'styled-components':
            return self._generate_styled_components(styles, component_name)
        elif self.css_framework == 'emotion':
            return self._generate_emotion_styles(styles)
        else:
            # CSS modules - styles are imported
            return ""
    
    def _generate_styled_components(self, styles: Dict[str, str], component_name: str) -> str:
        """Generate styled-components."""
        styled_components = []
        
        for style_name, css_rules in styles.items():
            component_name_styled = f"Styled{style_name.capitalize()}"
            
            # Parse CSS rules
            css_props = CSSProcessor.parse_style_string(css_rules)
            
            # Convert to styled-components format
            styled_rules = []
            for prop, value in css_props.items():
                # Convert kebab-case to camelCase for JS
                js_prop = re.sub(r'-([a-z])', lambda m: m.group(1).upper(), prop)
                styled_rules.append(f"  {js_prop}: '{value}';")
            
            styled_component = f"""const {component_name_styled} = styled.div`
{chr(10).join(styled_rules)}
`;"""
            styled_components.append(styled_component)
        
        return '\n\n'.join(styled_components) + '\n\n'
    
    def _generate_emotion_styles(self, styles: Dict[str, str]) -> str:
        """Generate emotion styles."""
        # This would require @emotion/react
        self.required_imports.add('@emotion/react')
        
        emotion_styles = []
        for style_name, css_rules in styles.items():
            css_props = CSSProcessor.parse_style_string(css_rules)
            
            js_props = []
            for prop, value in css_props.items():
                js_prop = re.sub(r'-([a-z])', lambda m: m.group(1).upper(), prop)
                js_props.append(f"  {js_prop}: '{value}'")
            
            emotion_style = f"""const {style_name}Style = {{
{','.join(js_props)}
}};"""
            emotion_styles.append(emotion_style)
        
        return '\n\n'.join(emotion_styles) + '\n\n'
    
    def _generate_component(self, 
                          component_name: str,
                          structure: Any,
                          styles: Dict[str, str],
                          interactions: Dict[str, Any],
                          metadata: Dict[str, Any]) -> str:
        """Generate the main React component."""
        # Component signature
        if self.use_typescript:
            signature = f"const {component_name}: React.FC<Props> = (props) => {{"
        else:
            signature = f"const {component_name} = (props) => {{"
        
        # Component body parts
        body_parts = []
        
        # State hooks
        if self.use_hooks:
            state_hooks = self._generate_state_hooks(structure, interactions)
            if state_hooks:
                body_parts.extend(state_hooks)
                body_parts.append("")
        
        # Effect hooks
        if self.use_hooks:
            effect_hooks = self._generate_effect_hooks(interactions)
            if effect_hooks:
                body_parts.extend(effect_hooks)
                body_parts.append("")
        
        # Event handlers
        event_handlers = self._generate_event_handlers(interactions)
        if event_handlers:
            body_parts.extend(event_handlers)
            body_parts.append("")
        
        # JSX return
        jsx_content = self._convert_structure_to_jsx(structure, styles, 1)
        body_parts.append("  return (")
        body_parts.append(f"    {jsx_content}")
        body_parts.append("  );")
        
        # Close component
        body_parts.append("};")
        
        # Export
        if self.export_default:
            body_parts.append("")
            body_parts.append(f"export default {component_name};")
        
        # Combine
        component_lines = [signature]
        for part in body_parts:
            if part:
                component_lines.append(f"  {part}")
            else:
                component_lines.append("")
        
        return '\n'.join(component_lines)
    
    def _generate_state_hooks(self, structure: Any, interactions: Dict[str, Any]) -> List[str]:
        """Generate useState hooks."""
        hooks = []
        
        # From interactions
        for key, value in interactions.items():
            if key.startswith('state'):
                state_name = key.replace('state', '').lower()
                if isinstance(value, dict):
                    initial_value = value.get('initial', 'null')
                else:
                    # Handle string values directly (e.g., 'true', 'useState(0)')
                    initial_value = value if isinstance(value, str) else 'null'
                hooks.append(f"const [{state_name}, set{state_name.capitalize()}] = useState({initial_value});")
        
        # From structure analysis
        state_vars = self._extract_state_variables(structure)
        for var_name, initial_value in state_vars.items():
            hooks.append(f"const [{var_name}, set{var_name.capitalize()}] = useState({initial_value});")
        
        return hooks
    
    def _generate_effect_hooks(self, interactions: Dict[str, Any]) -> List[str]:
        """Generate useEffect hooks."""
        hooks = []
        
        if 'onMount' in interactions:
            mount_code = interactions['onMount']
            hooks.append("useEffect(() => {")
            hooks.append(f"  {mount_code}")
            hooks.append("}, []);")
        
        if 'onUnmount' in interactions:
            unmount_code = interactions['onUnmount']
            hooks.append("useEffect(() => {")
            hooks.append("  return () => {")
            hooks.append(f"    {unmount_code}")
            hooks.append("  };")
            hooks.append("}, []);")
        
        return hooks
    
    def _generate_event_handlers(self, interactions: Dict[str, Any]) -> List[str]:
        """Generate event handler functions."""
        handlers = []
        
        for key, value in interactions.items():
            if key.startswith('handle') or key.startswith('on'):
                handler_name = key if key.startswith('handle') else f"handle{key.capitalize()}"
                handler_code = value if isinstance(value, str) else str(value)
                
                handlers.append(f"const {handler_name} = () => {{")
                handlers.append(f"  {handler_code}")
                handlers.append("};")
                handlers.append("")
        
        return handlers
    
    def _extract_state_variables(self, structure: Any) -> Dict[str, str]:
        """Extract state variables from structure."""
        state_vars = {}
        
        def extract_callback(element, context):
            if isinstance(element, dict):
                for key, value in element.items():
                    if isinstance(value, str) and 'useState' in value:
                        # Parse useState declarations
                        match = re.search(r'(\w+),\s*set\w+\s*=\s*useState\(([^)]+)\)', value)
                        if match:
                            var_name = match.group(1)
                            initial_value = match.group(2)
                            state_vars[var_name] = initial_value
            return element
        
        self.walker.walk(structure, extract_callback)
        return state_vars
    
    def _replace_template_vars_in_structure(self, structure: Any, template_vars: Dict[str, str]) -> Any:
        """Replace template variables in structure before JSX conversion."""
        if isinstance(structure, dict):
            # Process dictionary recursively
            result = {}
            for key, value in structure.items():
                result[key] = self._replace_template_vars_in_structure(value, template_vars)
            return result
        elif isinstance(structure, list):
            # Process list recursively
            return [self._replace_template_vars_in_structure(item, template_vars) for item in structure]
        elif isinstance(structure, str):
            # Replace template variables in strings
            return self.replace_template_variables(structure, template_vars)
        else:
            # Return other types as-is
            return structure
    
    def _convert_structure_to_jsx(self, structure: Any, styles: Dict[str, str], indent: int = 0) -> str:
        """Convert manifest structure to JSX."""
        if isinstance(structure, dict):
            return self._convert_element_to_jsx(structure, styles, indent)
        elif isinstance(structure, list):
            jsx_elements = []
            for i, item in enumerate(structure):
                jsx = self._convert_structure_to_jsx(item, styles, indent)
                jsx_elements.append(jsx)
            return '{[\n' + ',\n'.join(jsx_elements) + '\n]}'
        elif isinstance(structure, str):
            # Handle template literals
            if '{{' in structure and '}}' in structure:
                # Convert template syntax to JSX expression
                jsx_expr = re.sub(r'\{\{([^}]+)\}\}', r'{\1}', structure)
                return f'"{jsx_expr}"'
            else:
                return f'"{escape(structure)}"'
        else:
            return str(structure)
    
    def _convert_element_to_jsx(self, element: Dict[str, Any], styles: Dict[str, str], indent: int) -> str:
        """Convert a single element to JSX."""
        # Extract element information
        tag_name = None
        props = {}
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
                    # CSS class reference
                    if self.css_framework == 'css-modules':
                        props['className'] = f"styles.{value}"
                    elif self.css_framework == 'styled-components':
                        # Use styled component
                        tag_name = f"Styled{value.capitalize()}"
                    else:
                        props['className'] = value
                else:
                    # Inline style object
                    props['style'] = self._convert_inline_style(value)
            elif key == 'class':
                props['className'] = value
            elif key in ['id', 'src', 'href', 'alt', 'title', 'type', 'placeholder']:
                props[key] = value
            elif key.startswith('on'):
                # Event handler
                handler_name = f"handle{key[2:].capitalize()}"
                props[key] = f"{{{handler_name}}}"
            elif self._is_html_element(key):
                tag_name = key
                if isinstance(value, dict):
                    # Nested element
                    children.append(value)
                else:
                    text_content = value
        
        # Default tag if none specified
        if tag_name is None:
            tag_name = 'div'
        
        # Format props
        props_str = self._format_jsx_props(props)
        
        # Generate JSX
        if text_content is not None:
            # Element with text content
            content = self._format_jsx_text(text_content)
            return f"<{tag_name}{props_str}>{content}</{tag_name}>"
        elif children:
            # Element with children
            children_jsx = []
            for child in children:
                child_jsx = self._convert_structure_to_jsx(child, styles, indent + 1)
                children_jsx.append(child_jsx)
            
            if len(children_jsx) == 1:
                return f"<{tag_name}{props_str}>{children_jsx[0]}</{tag_name}>"
            else:
                children_str = ',\n'.join(children_jsx)
                return f"<{tag_name}{props_str}>\n{children_str}\n</{tag_name}>"
        else:
            # Self-closing element
            return f"<{tag_name}{props_str} />"
    
    def _is_html_element(self, name: str) -> bool:
        """Check if name is a valid HTML element for JSX."""
        return name.lower() in {
            'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'thead', 'tbody',
            'form', 'input', 'textarea', 'select', 'option', 'button', 'label',
            'a', 'img', 'video', 'audio', 'br', 'hr',
            'header', 'nav', 'main', 'section', 'article', 'aside', 'footer'
        }
    
    def _format_jsx_props(self, props: Dict[str, Any]) -> str:
        """Format JSX props."""
        if not props:
            return ""
        
        prop_parts = []
        for key, value in props.items():
            if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                # JSX expression
                prop_parts.append(f'{key}={value}')
            elif isinstance(value, str):
                # String literal
                escaped_value = escape(value)
                prop_parts.append(f'{key}="{escaped_value}"')
            else:
                # Other types as JSX expressions
                prop_parts.append(f'{key}={{{value}}}')
        
        return ' ' + ' '.join(prop_parts)
    
    def _format_jsx_text(self, text: Any) -> str:
        """Format text content for JSX."""
        if isinstance(text, str):
            # Handle template expressions
            if '{{' in text and '}}' in text:
                return '{' + re.sub(r'\{\{([^}]+)\}\}', r'\1', text) + '}'
            else:
                return escape(text)
        else:
            return f"{{{text}}}"
    
    def _convert_inline_style(self, style_str: str) -> str:
        """Convert CSS style string to JSX style object."""
        props = CSSProcessor.parse_style_string(style_str)
        
        js_props = []
        for prop, value in props.items():
            # Convert kebab-case to camelCase
            js_prop = re.sub(r'-([a-z])', lambda m: m.group(1).upper(), prop)
            js_props.append(f"'{js_prop}': '{value}'")
        
        return '{' + ', '.join(js_props) + '}'
    
    def _combine_sections(self, *sections: str) -> str:
        """Combine all sections into final component code."""
        return ''.join(section for section in sections if section.strip())
    
    def _format_header_comment(self, title: str, description: str) -> str:
        """Format React header comment."""
        parts = [f"Generated by WhyML - {title}"]
        if description:
            parts.append(f"Description: {description}")
        parts.append("React Component")
        
        comment_content = "\n".join(f" * {part}" for part in parts)
        return f"/**\n{comment_content}\n */"
