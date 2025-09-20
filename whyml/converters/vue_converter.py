"""
Vue Converter - Convert YAML manifests to Vue Single File Components (SFC)

Generates modern Vue 3 composition API components with TypeScript support,
reactive data, and comprehensive styling integration.

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


class VueConverter(BaseConverter):
    """Convert YAML manifests to Vue Single File Components."""
    
    def __init__(self, 
                 vue_version: str = "3",
                 use_composition_api: bool = True,
                 use_typescript: bool = True,
                 scoped_styles: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        self.vue_version = vue_version
        self.use_composition_api = use_composition_api
        self.use_typescript = use_typescript
        self.scoped_styles = scoped_styles
        self.walker = StructureWalker(self)
        self.vue_imports: Set[str] = set()
    
    @property
    def format_name(self) -> str:
        return "Vue"
    
    @property
    def file_extension(self) -> str:
        return "vue"
    
    def convert(self, manifest: Dict[str, Any], **kwargs) -> ConversionResult:
        """Convert manifest to Vue SFC."""
        try:
            self.vue_imports.clear()
            
            metadata = self.extract_metadata(manifest)
            styles = self.extract_styles(manifest)
            template_vars = self.extract_template_vars(manifest)
            structure = manifest.get('structure', {})
            self.interactions = manifest.get('interactions', {})  # Store interactions for access in methods
            
            # Replace template variables in structure BEFORE Vue conversion
            if template_vars:
                structure = self._replace_template_vars_in_structure(structure, template_vars)
            
            component_name = self._generate_component_name(metadata)
            self._analyze_structure_for_imports(structure, self.interactions)
            
            template_section = self._generate_template_section(structure, styles)
            script_section = self._generate_script_section(component_name, metadata, self.interactions)
            style_section = self._generate_style_section(styles)
            
            vue_content = self._combine_sfc_sections(template_section, script_section, style_section)
            
            # Replace template variables ({{ hero_text }} -> "Welcome to Our Amazing Product")
            if template_vars:
                vue_content = self.replace_template_variables(vue_content, template_vars)
            
            if self.optimize_output:
                vue_content = self.optimize_code(vue_content)
            
            vue_content = self.add_header_comment(vue_content, manifest)
            filename = f"{component_name}.vue"
            
            return ConversionResult(
                content=vue_content,
                filename=filename,
                format_type=self.format_name.lower(),
                metadata={
                    'component_name': component_name,
                    'vue_version': self.vue_version,
                    'uses_composition_api': self.use_composition_api
                }
            )
            
        except Exception as e:
            raise self.handle_conversion_error(e, "Vue conversion")
    
    def _generate_component_name(self, metadata: Dict[str, Any]) -> str:
        """Generate valid Vue component name."""
        title = metadata.get('title', 'Component')
        name = re.sub(r'[^\w\s]', '', title)
        name = ''.join(word.capitalize() for word in name.split())
        if not name or not name[0].isupper():
            name = f"Generated{name}"
        return name
    
    def _analyze_structure_for_imports(self, structure: Any, interactions: Dict[str, Any]):
        """Analyze structure to determine required Vue imports."""
        if self.use_composition_api:
            self.vue_imports.add('defineComponent')
            if self._has_reactive_data(structure, interactions):
                self.vue_imports.add('ref')
                self.vue_imports.add('reactive')
    
    def _has_reactive_data(self, structure: Any, interactions: Dict[str, Any]) -> bool:
        """Check if component needs reactive data."""
        return any(key.startswith('data') or key.startswith('state') for key in interactions.keys())
    
    def _generate_template_section(self, structure: Any, styles: Dict[str, str]) -> str:
        """Generate Vue template section."""
        template_content = self._convert_structure_to_vue_template(structure, styles)
        return f"<template>\n{template_content}\n</template>"
    
    def _generate_script_section(self, component_name: str, metadata: Dict[str, Any], interactions: Dict[str, Any]) -> str:
        """Generate Vue script section."""
        script_parts = []
        
        if self.use_typescript:
            script_parts.append('<script lang="ts">')
        else:
            script_parts.append('<script>')
        
        # Always import defineComponent for Vue 3
        vue_imports = set(['defineComponent'])
        
        # Add ref import if we have interactions (for reactive data or handlers)
        if interactions:
            vue_imports.add('ref')
            
        # Add any other imports from analysis
        if self.vue_imports:
            vue_imports.update(self.vue_imports)
            
        vue_import = ', '.join(sorted(vue_imports))
        script_parts.append(f"import {{ {vue_import} }} from 'vue';")
        script_parts.append("")
        
        if self.use_composition_api:
            component_code = self._generate_composition_api_component(component_name, interactions)
        else:
            component_code = self._generate_options_api_component(component_name, interactions)
        
        script_parts.append(component_code)
        script_parts.append("</script>")
        
        return '\n'.join(script_parts)
    
    def _generate_composition_api_component(self, component_name: str, interactions: Dict[str, Any]) -> str:
        """Generate Composition API component."""
        component_parts = [
            f"export default defineComponent({{",
            f"  name: '{component_name}',",
            "  setup() {"
        ]
        
        # Reactive data
        for key, value in interactions.items():
            if key.startswith('data_') or key.startswith('state_'):
                var_name = key.replace('data_', '').replace('state_', '').lower()
                if var_name and isinstance(value, str):
                    if value.startswith('ref('):
                        # Extract initial value from ref(value) -> value
                        initial_value = value[4:-1]  # Remove 'ref(' and ')'
                        component_parts.append(f"    const {var_name} = ref({initial_value});")
                    else:
                        # Default ref initialization
                        component_parts.append(f"    const {var_name} = ref({value});")
        
        # Methods and computed properties
        for key, value in interactions.items():
            if key.startswith('method_'):
                method_name = key.replace('method_', '')
                if isinstance(value, str):
                    # Generate method with the actual code
                    component_parts.append(f"    const {method_name} = () => {{")
                    component_parts.append(f"      {value}")
                    component_parts.append(f"    }};")
                    component_parts.append("")
        
        # Return statement
        return_items = []
        
        # Add reactive data variables
        for key in interactions.keys():
            if key.startswith('data_') or key.startswith('state_'):
                var_name = key.replace('data_', '').replace('state_', '').lower()
                if var_name:
                    return_items.append(var_name)
        
        # Add methods
        for key in interactions.keys():
            if key.startswith('method_'):
                method_name = key.replace('method_', '')
                return_items.append(method_name)
        
        if return_items:
            component_parts.append(f"    return {{ {', '.join(return_items)} }};")
        else:
            component_parts.append("    return {};")
        
        component_parts.extend(["  }", "});"])
        return '\n'.join(component_parts)
    
    def _generate_options_api_component(self, component_name: str, interactions: Dict[str, Any]) -> str:
        """Generate Options API component."""
        component_parts = [f"export default {{", f"  name: '{component_name}',"]
        
        # Data
        data_props = {}
        for key, value in interactions.items():
            if key.startswith('data') or key.startswith('state'):
                prop_name = key.replace('data', '').replace('state', '').lower()
                if prop_name:
                    data_props[prop_name] = 'null'
        
        if data_props:
            component_parts.append("  data() {")
            component_parts.append("    return {")
            for prop_name, initial_value in data_props.items():
                component_parts.append(f"      {prop_name}: {initial_value},")
            component_parts.append("    };")
            component_parts.append("  }")
        
        component_parts.append("};")
        return '\n'.join(component_parts)
    
    def _convert_structure_to_vue_template(self, structure: Any, styles: Dict[str, str], indent: int = 1) -> str:
        """Convert manifest structure to Vue template."""
        if isinstance(structure, dict):
            return self._convert_element_to_vue_template(structure, styles, indent)
        elif isinstance(structure, list):
            return '\n'.join(self._convert_structure_to_vue_template(item, styles, indent) for item in structure)
        elif isinstance(structure, str):
            return escape(structure)
        else:
            return str(structure)
    
    def _convert_element_to_vue_template(self, element: Dict[str, Any], styles: Dict[str, str], indent: int) -> str:
        """Convert a single element to Vue template."""
        # Check if this element is a simple HTML element structure
        html_keys = [key for key in element.keys() if self._is_html_element(key)]
        
        if len(html_keys) == 1 and len(element) == 1:
            # This is a single HTML element structure like { h1: { text: "...", class: "..." } }
            tag_name = html_keys[0]
            element_data = element[tag_name]
            
            # Process the element data directly instead of recursive call
            indent_str = '  ' * indent
            attributes = {}
            children = []
            text_content = None
            
            if isinstance(element_data, dict):
                for nested_key, nested_value in element_data.items():
                    if nested_key in ['text', 'content']:
                        text_content = nested_value
                    elif nested_key == 'children':
                        if isinstance(nested_value, list):
                            children.extend(nested_value)
                        else:
                            children.append(nested_value)
                    elif nested_key == 'class':
                        attributes['class'] = nested_value
                    elif nested_key in ['id', 'src', 'href', 'alt', 'title']:
                        attributes[nested_key] = nested_value
                    elif nested_key.startswith('@') or nested_key.startswith(':'):
                        # Handle Vue directives like @click, :class, etc.
                        attributes[nested_key] = nested_value
                    elif nested_key == 'onClick':
                        # Handle onClick interactions for Vue @click directives
                        interaction_handler = self._get_interaction_handler(nested_value)
                        if interaction_handler:
                            attributes['@click'] = interaction_handler
                    elif nested_key == 'style':
                        if nested_value in styles:
                            attributes['class'] = nested_value
                        else:
                            attributes[':style'] = f"'{nested_value}'"
            else:
                text_content = element_data
            
            attrs_str = self._format_vue_attributes(attributes)
            
            if text_content is not None:
                content = escape(str(text_content))
                return f"{indent_str}<{tag_name}{attrs_str}>{content}</{tag_name}>"
            elif children:
                children_templates = [self._convert_structure_to_vue_template(child, styles, indent + 1) for child in children]
                children_str = '\n'.join(children_templates)
                return f"{indent_str}<{tag_name}{attrs_str}>\n{children_str}\n{indent_str}</{tag_name}>"
            else:
                return f"{indent_str}<{tag_name}{attrs_str}></{tag_name}>"
        
        indent_str = '  ' * indent
        
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
                    attributes[':style'] = f"'{value}'"
            elif key == 'class':
                attributes['class'] = value
            elif key in ['id', 'src', 'href', 'alt', 'title']:
                attributes[key] = value
            elif key.startswith('@') or key.startswith(':'):
                # Handle Vue directives like @click, :class, etc.
                attributes[key] = value
            elif self._is_html_element(key):
                tag_name = key
                if isinstance(value, dict):
                    # Process the nested element structure
                    for nested_key, nested_value in value.items():
                        if nested_key in ['text', 'content']:
                            text_content = nested_value
                        elif nested_key == 'children':
                            if isinstance(nested_value, list):
                                children.extend(nested_value)
                            else:
                                children.append(nested_value)
                        elif nested_key == 'class':
                            attributes['class'] = nested_value
                        elif nested_key in ['id', 'src', 'href', 'alt', 'title']:
                            attributes[nested_key] = nested_value
                        elif nested_key.startswith('@') or nested_key.startswith(':'):
                            # Handle Vue directives like @click, :class, etc.
                            attributes[nested_key] = nested_value
                        elif nested_key == 'style':
                            if nested_value in styles:
                                attributes['class'] = nested_value
                            else:
                                attributes[':style'] = f"'{nested_value}'"
                else:
                    text_content = value
        
        attrs_str = self._format_vue_attributes(attributes)
        
        if text_content is not None:
            content = escape(str(text_content))
            return f"{indent_str}<{tag_name}{attrs_str}>{content}</{tag_name}>"
        elif children:
            children_templates = [self._convert_structure_to_vue_template(child, styles, indent + 1) for child in children]
            children_str = '\n'.join(children_templates)
            return f"{indent_str}<{tag_name}{attrs_str}>\n{children_str}\n{indent_str}</{tag_name}>"
        else:
            return f"{indent_str}<{tag_name}{attrs_str}></{tag_name}>"
    
    def _is_html_element(self, name: str) -> bool:
        """Check if name is a valid HTML element."""
        return name.lower() in {
            'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
            'ul', 'ol', 'li', 'a', 'img', 'button', 'input', 'textarea', 'select', 'form', 
            'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot',
            'section', 'article', 'header', 'footer', 'nav', 'aside', 'main',
            'figure', 'figcaption', 'details', 'summary', 'time', 'mark', 'code', 'pre'
        }
    
    def _format_vue_attributes(self, attributes: Dict[str, Any]) -> str:
        """Format Vue template attributes."""
        if not attributes:
            return ""
        
        attr_parts = []
        for key, value in attributes.items():
            escaped_value = escape(str(value))
            attr_parts.append(f'{key}="{escaped_value}"')
        
        return ' ' + ' '.join(attr_parts)
    
    def _generate_style_section(self, styles: Dict[str, str]) -> str:
        """Generate Vue style section."""
        if not styles:
            return ""
        
        style_tag = "<style scoped>" if self.scoped_styles else "<style>"
        style_lines = [style_tag]
        
        for selector, rules in styles.items():
            css_selector = f".{selector.replace('_', '-')}"
            style_lines.append(f"{css_selector} {{")
            for rule in rules.split(';'):
                rule = rule.strip()
                if rule:
                    style_lines.append(f"  {rule};")
            style_lines.append("}")
        
        style_lines.append("</style>")
        return '\n'.join(style_lines)
    
    def _get_interaction_handler(self, interaction_key: str) -> str:
        """Get the Vue interaction handler for a given interaction key."""
        if hasattr(self, 'interactions') and interaction_key in self.interactions:
            return self.interactions[interaction_key]
        return None
    
    def _combine_sfc_sections(self, template: str, script: str, style: str) -> str:
        """Combine SFC sections into complete Vue file."""
        sections = [template, script]
        if style.strip():
            sections.append(style)
        return '\n\n'.join(sections)
    
    def _format_header_comment(self, title: str, description: str) -> str:
        """Format Vue header comment."""
        parts = [f"Generated by WhyML - {title}"]
        if description:
            parts.append(f"Description: {description}")
        comment_content = "\n".join(f"  {part}" for part in parts)
        return f"<!--\n{comment_content}\n-->"
    
    def _replace_template_vars_in_structure(self, structure: Any, template_vars: Dict[str, str]) -> Any:
        """Replace template variables in structure before Vue conversion."""
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
