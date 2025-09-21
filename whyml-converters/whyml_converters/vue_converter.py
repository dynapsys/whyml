"""
WhyML Converters - Vue Converter Module

Advanced Vue.js converter with Single File Component (SFC) generation,
Composition API support, TypeScript integration, and modern Vue patterns.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import re

from whyml_core.utils import StringUtils
from whyml_core.exceptions import ProcessingError
from .base_converter import BaseConverter


class VueConverter(BaseConverter):
    """Advanced Vue.js converter with SFC and Composition API support."""
    
    def __init__(self, **kwargs):
        """Initialize Vue converter."""
        super().__init__(**kwargs)
        self.indent_size = 2
        self.current_indent = 0
        self.use_typescript = False
        self.use_composition_api = True
        self.component_name = "WhyMLComponent"
    
    def _get_output_format(self) -> str:
        """Get output format identifier."""
        return "vue"
    
    def _get_template_extension(self) -> str:
        """Get template file extension."""
        return ".vue"
    
    def _supports_components(self) -> bool:
        """Check if converter supports components."""
        return True
    
    async def convert_manifest(self, 
                              manifest: Dict[str, Any],
                              output_path: Optional[Union[str, Path]] = None,
                              **options) -> str:
        """Convert WhyML manifest to Vue SFC.
        
        Args:
            manifest: WhyML manifest dictionary
            output_path: Optional output file path
            **options: Vue-specific options
            
        Returns:
            Generated Vue SFC content
        """
        # Configure options
        self.use_typescript = options.get('typescript', False)
        self.use_composition_api = options.get('composition_api', True)
        self.component_name = options.get('component_name', 'WhyMLComponent')
        
        # Reset indentation
        self.current_indent = 0
        
        # Extract manifest sections
        metadata = self._extract_metadata(manifest)
        structure = self._extract_structure(manifest)
        styles = self._extract_styles(manifest)
        scripts = self._extract_scripts(manifest)
        imports = self._extract_imports(manifest)
        
        # Build Vue SFC
        sfc_parts = []
        
        # Template section
        template_content = await self._generate_template(structure, metadata, **options)
        sfc_parts.append(template_content)
        
        # Script section
        script_content = await self._generate_script(
            metadata, scripts, imports, **options
        )
        sfc_parts.append(script_content)
        
        # Style section
        if styles:
            style_content = self._generate_style(styles, **options)
            sfc_parts.append(style_content)
        
        return '\n\n'.join(filter(None, sfc_parts))
    
    async def _generate_template(self, 
                               structure: Dict[str, Any], 
                               metadata: Dict[str, Any],
                               **options) -> str:
        """Generate Vue template section."""
        template_lines = ["<template>"]
        
        self._increase_indent()
        
        if structure:
            template_content = await self._generate_vue_template(structure)
            template_lines.append(template_content)
        else:
            template_lines.append(self._indent() + "<div>No content</div>")
        
        self._decrease_indent()
        template_lines.append("</template>")
        
        return '\n'.join(template_lines)
    
    async def _generate_script(self, 
                             metadata: Dict[str, Any],
                             scripts: Dict[str, Any],
                             imports: Dict[str, Any],
                             **options) -> str:
        """Generate Vue script section."""
        script_lines = []
        
        # Script tag opening
        if self.use_typescript:
            script_lines.append('<script setup lang="ts">')
        else:
            script_lines.append('<script setup>')
        
        # Imports
        import_content = self._generate_vue_imports(imports, **options)
        if import_content:
            script_lines.append(import_content)
            script_lines.append('')
        
        # Component logic
        if self.use_composition_api:
            logic_content = await self._generate_composition_api_logic(
                metadata, scripts, **options
            )
        else:
            logic_content = await self._generate_options_api_logic(
                metadata, scripts, **options
            )
        
        if logic_content:
            script_lines.append(logic_content)
        
        script_lines.append('</script>')
        
        return '\n'.join(script_lines)
    
    def _generate_style(self, styles: Dict[str, Any], **options) -> str:
        """Generate Vue style section."""
        style_lines = []
        
        # Style tag opening
        style_attrs = []
        if options.get('scoped', True):
            style_attrs.append('scoped')
        
        preprocessor = options.get('css_preprocessor')
        if preprocessor:
            style_attrs.append(f'lang="{preprocessor}"')
        
        if style_attrs:
            style_lines.append(f'<style {" ".join(style_attrs)}>')
        else:
            style_lines.append('<style>')
        
        # CSS content
        css_content = self._generate_vue_css(styles)
        if css_content:
            style_lines.append(css_content)
        
        style_lines.append('</style>')
        
        return '\n'.join(style_lines)
    
    async def _generate_vue_template(self, structure: Dict[str, Any]) -> str:
        """Generate Vue template content from structure."""
        if not structure:
            return self._indent() + "<div>No content</div>"
        
        # Handle different structure formats
        if 'tag' in structure:
            # Single element
            return await self._generate_vue_element(structure)
        elif 'children' in structure:
            # Multiple elements
            return await self._generate_vue_children(structure['children'])
        else:
            # Process as container
            return await self._generate_vue_container(structure)
    
    async def _generate_vue_element(self, element: Dict[str, Any]) -> str:
        """Generate Vue template element."""
        tag = element.get('tag', 'div')
        
        # Handle self-closing tags
        self_closing_tags = {'img', 'br', 'hr', 'input', 'meta', 'link'}
        is_self_closing = tag in self_closing_tags
        
        # Build opening tag with attributes
        opening_tag = await self._build_vue_opening_tag(tag, element)
        
        if is_self_closing:
            return self._indent() + opening_tag
        
        # Handle content
        content = element.get('content', '')
        children = element.get('children', [])
        
        if not content and not children:
            # Empty element
            return self._indent() + f"<{tag}></{tag}>"
        
        if content and not children:
            # Element with text content only
            if '\n' in content or len(content) > 80:
                # Multi-line content
                return (self._indent() + opening_tag + '\n' +
                       self._indent_text(self._escape_vue_content(content), self.current_indent + 1) + '\n' +
                       self._indent() + f"</{tag}>")
            else:
                # Single line content
                return self._indent() + f"{opening_tag}{self._escape_vue_content(content)}</{tag}>"
        
        # Element with children
        element_parts = [self._indent() + opening_tag]
        
        if content:
            self._increase_indent()
            element_parts.append(self._indent() + self._escape_vue_content(content))
            self._decrease_indent()
        
        if children:
            self._increase_indent()
            children_content = await self._generate_vue_children(children)
            element_parts.append(children_content)
            self._decrease_indent()
        
        element_parts.append(self._indent() + f"</{tag}>")
        
        return '\n'.join(element_parts)
    
    async def _build_vue_opening_tag(self, tag: str, element: Dict[str, Any]) -> str:
        """Build opening Vue template tag with attributes."""
        attributes = element.get('attributes', {})
        
        attr_parts = []
        for name, value in attributes.items():
            if value is None or value is False:
                continue
            elif value is True:
                # Boolean attribute
                attr_parts.append(name)
            else:
                # Handle Vue-specific attributes
                vue_attr = self._html_to_vue_attr(name, value)
                attr_parts.append(vue_attr)
        
        if attr_parts:
            return f"<{tag} {' '.join(attr_parts)}>"
        else:
            return f"<{tag}>"
    
    async def _generate_vue_children(self, children: List[Any]) -> str:
        """Generate Vue template for list of child elements."""
        child_parts = []
        
        for child in children:
            if isinstance(child, dict):
                if child.get('type') == 'text':
                    # Text node
                    text_content = child.get('content', '')
                    if text_content:
                        child_parts.append(self._indent() + self._escape_vue_content(text_content))
                else:
                    # Element node
                    child_content = await self._generate_vue_element(child)
                    child_parts.append(child_content)
            elif isinstance(child, str):
                # Direct text content
                child_parts.append(self._indent() + self._escape_vue_content(child))
        
        return '\n'.join(child_parts)
    
    async def _generate_vue_container(self, structure: Dict[str, Any]) -> str:
        """Generate Vue template for container structure."""
        container_parts = []
        
        for key, value in structure.items():
            if isinstance(value, dict):
                element_content = await self._generate_vue_element(value)
                container_parts.append(element_content)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        element_content = await self._generate_vue_element(item)
                        container_parts.append(element_content)
        
        if len(container_parts) == 1:
            return container_parts[0]
        elif len(container_parts) > 1:
            # Wrap in template fragment for Vue 3
            return (self._indent() + "<template>\n" +
                   '\n'.join(container_parts) + '\n' +
                   self._indent() + "</template>")
        else:
            return self._indent() + "<div>No content</div>"
    
    def _generate_vue_imports(self, imports: Dict[str, Any], **options) -> str:
        """Generate Vue import statements."""
        import_lines = []
        
        # Vue imports
        vue_imports = options.get('vue_imports', [])
        if vue_imports:
            import_lines.append(f"import {{ {', '.join(vue_imports)} }} from 'vue'")
        
        # Component imports
        components = options.get('components', [])
        for component in components:
            if isinstance(component, str):
                import_lines.append(f"import {component} from './{component}.vue'")
            elif isinstance(component, dict):
                name = component.get('name')
                path = component.get('path')
                if name and path:
                    import_lines.append(f"import {name} from '{path}'")
        
        # External dependencies
        dependencies = options.get('dependencies', [])
        for dep in dependencies:
            if isinstance(dep, str):
                import_lines.append(f"import '{dep}'")
            elif isinstance(dep, dict):
                module = dep.get('module', '')
                imports_list = dep.get('imports', [])
                default_import = dep.get('default')
                
                if default_import and imports_list:
                    import_line = f"import {default_import}, {{ {', '.join(imports_list)} }} from '{module}'"
                elif default_import:
                    import_line = f"import {default_import} from '{module}'"
                elif imports_list:
                    import_line = f"import {{ {', '.join(imports_list)} }} from '{module}'"
                else:
                    import_line = f"import '{module}'"
                
                import_lines.append(import_line)
        
        return '\n'.join(import_lines)
    
    async def _generate_composition_api_logic(self, 
                                            metadata: Dict[str, Any],
                                            scripts: Dict[str, Any],
                                            **options) -> str:
        """Generate Composition API logic."""
        logic_lines = []
        
        # Reactive data
        reactive_data = options.get('data', {})
        if reactive_data:
            logic_lines.append("// Reactive data")
            for key, value in reactive_data.items():
                formatted_value = self._format_js_value(value)
                logic_lines.append(f"const {key} = ref({formatted_value})")
            logic_lines.append("")
        
        # Computed properties
        computed_props = options.get('computed', {})
        if computed_props:
            logic_lines.append("// Computed properties")
            for name, computation in computed_props.items():
                logic_lines.append(f"const {name} = computed(() => {{")
                logic_lines.append(f"  return {computation}")
                logic_lines.append("})")
            logic_lines.append("")
        
        # Methods
        methods = options.get('methods', {})
        if methods:
            logic_lines.append("// Methods")
            for name, method_body in methods.items():
                logic_lines.append(f"const {name} = ({method_body.get('params', '')}) => {{")
                logic_lines.append(f"  {method_body.get('body', '// Method implementation')}")
                logic_lines.append("}")
            logic_lines.append("")
        
        # Lifecycle hooks
        lifecycle_hooks = options.get('lifecycle', {})
        for hook_name, hook_body in lifecycle_hooks.items():
            vue_hook = self._convert_to_composition_hook(hook_name)
            if vue_hook:
                logic_lines.append(f"{vue_hook}(() => {{")
                logic_lines.append(f"  {hook_body}")
                logic_lines.append("})")
        
        # Extract logic from scripts
        if scripts:
            script_logic = self._extract_vue_logic(scripts)
            if script_logic:
                logic_lines.append("")
                logic_lines.append("// Additional logic")
                logic_lines.append(script_logic)
        
        return '\n'.join(logic_lines)
    
    async def _generate_options_api_logic(self, 
                                        metadata: Dict[str, Any],
                                        scripts: Dict[str, Any],
                                        **options) -> str:
        """Generate Options API logic."""
        logic_lines = []
        
        # Component definition
        if self.use_typescript:
            logic_lines.append("import { defineComponent } from 'vue'")
            logic_lines.append("")
            logic_lines.append("export default defineComponent({")
        else:
            logic_lines.append("export default {")
        
        self._increase_indent()
        
        # Component name
        logic_lines.append(self._indent() + f"name: '{self.component_name}',")
        logic_lines.append("")
        
        # Props
        props = options.get('props', {})
        if props:
            logic_lines.append(self._indent() + "props: {")
            self._increase_indent()
            
            for prop_name, prop_config in props.items():
                prop_def = self._generate_vue_prop_definition(prop_config)
                logic_lines.append(self._indent() + f"{prop_name}: {prop_def},")
            
            self._decrease_indent()
            logic_lines.append(self._indent() + "},")
            logic_lines.append("")
        
        # Data
        data = options.get('data', {})
        if data:
            logic_lines.append(self._indent() + "data() {")
            self._increase_indent()
            logic_lines.append(self._indent() + "return {")
            self._increase_indent()
            
            for key, value in data.items():
                formatted_value = self._format_js_value(value)
                logic_lines.append(self._indent() + f"{key}: {formatted_value},")
            
            self._decrease_indent()
            logic_lines.append(self._indent() + "}")
            self._decrease_indent()
            logic_lines.append(self._indent() + "},")
            logic_lines.append("")
        
        # Computed
        computed = options.get('computed', {})
        if computed:
            logic_lines.append(self._indent() + "computed: {")
            self._increase_indent()
            
            for name, computation in computed.items():
                logic_lines.append(self._indent() + f"{name}() {{")
                logic_lines.append(self._indent() + f"  return {computation}")
                logic_lines.append(self._indent() + "},")
            
            self._decrease_indent()
            logic_lines.append(self._indent() + "},")
            logic_lines.append("")
        
        # Methods
        methods = options.get('methods', {})
        if methods:
            logic_lines.append(self._indent() + "methods: {")
            self._increase_indent()
            
            for name, method_body in methods.items():
                logic_lines.append(self._indent() + f"{name}({method_body.get('params', '')}) {{")
                logic_lines.append(self._indent() + f"  {method_body.get('body', '// Method implementation')}")
                logic_lines.append(self._indent() + "},")
            
            self._decrease_indent()
            logic_lines.append(self._indent() + "},")
        
        self._decrease_indent()
        if self.use_typescript:
            logic_lines.append("})")
        else:
            logic_lines.append("}")
        
        return '\n'.join(logic_lines)
    
    def _generate_vue_css(self, styles: Dict[str, Any]) -> str:
        """Generate CSS content for Vue style section."""
        css_lines = []
        
        # Process inline styles
        inline_styles = styles.get('inline_styles', {})
        for element_id, properties in inline_styles.items():
            if properties:
                selector = f"#{element_id}" if not element_id.startswith('.') else element_id
                css_rule = self._generate_css_rule(selector, properties)
                css_lines.append(css_rule)
        
        # Process internal styles
        internal_styles = styles.get('internal_styles', {})
        if internal_styles:
            for style_name, rules in internal_styles.items():
                if isinstance(rules, dict):
                    for selector, properties in rules.items():
                        css_rule = self._generate_css_rule(selector, properties)
                        css_lines.append(css_rule)
        
        # Process direct CSS rules
        for key, value in styles.items():
            if key not in ['inline_styles', 'internal_styles', 'external_stylesheets']:
                if isinstance(value, dict):
                    css_rule = self._generate_css_rule(key, value)
                    css_lines.append(css_rule)
                elif isinstance(value, str) and '{' in value and '}' in value:
                    # Direct CSS string
                    css_lines.append(value)
        
        return '\n\n'.join(css_lines)
    
    def _generate_css_rule(self, selector: str, properties: Dict[str, str]) -> str:
        """Generate CSS rule from selector and properties."""
        if not properties:
            return ""
        
        css_properties = []
        for prop, value in properties.items():
            css_properties.append(f"  {prop}: {value};")
        
        return f"{selector} {\n" + '\n'.join(css_properties) + "\n}"
    
    # Helper methods
    
    def _html_to_vue_attr(self, name: str, value: Any) -> str:
        """Convert HTML attribute to Vue template attribute."""
        # Handle Vue-specific bindings
        if name == 'class' and isinstance(value, list):
            # Class array binding
            return f':class="[{", ".join(f\'"{cls}"\' for cls in value)}]"'
        elif name == 'style' and isinstance(value, dict):
            # Style object binding
            style_obj = ', '.join(f"'{k}': '{v}'" for k, v in value.items())
            return f':style="{{{{ {style_obj} }}}}"'
        elif name in ['v-if', 'v-else-if', 'v-show', 'v-for', 'v-model']:
            # Vue directives
            return f'{name}="{value}"'
        elif name.startswith('@') or name.startswith('v-on:'):
            # Event handlers
            return f'{name}="{value}"'
        elif name.startswith(':') or name.startswith('v-bind:'):
            # Property bindings
            return f'{name}="{value}"'
        else:
            # Regular attributes
            return f'{name}="{self._escape_vue_attribute(str(value))}"'
    
    def _convert_to_composition_hook(self, hook_name: str) -> Optional[str]:
        """Convert lifecycle hook name to Composition API equivalent."""
        hook_mapping = {
            'created': 'onBeforeMount',
            'mounted': 'onMounted',
            'updated': 'onUpdated',
            'destroyed': 'onUnmounted',
            'beforeDestroy': 'onBeforeUnmount'
        }
        
        return hook_mapping.get(hook_name)
    
    def _generate_vue_prop_definition(self, prop_config: Dict[str, Any]) -> str:
        """Generate Vue prop definition."""
        if isinstance(prop_config, str):
            # Simple type
            return prop_config.capitalize()
        
        prop_parts = []
        
        # Type
        prop_type = prop_config.get('type', 'String')
        prop_parts.append(f"type: {prop_type}")
        
        # Required
        if prop_config.get('required', False):
            prop_parts.append("required: true")
        
        # Default value
        default_value = prop_config.get('default')
        if default_value is not None:
            if isinstance(default_value, (dict, list)):
                prop_parts.append(f"default: () => ({self._format_js_value(default_value)})")
            else:
                prop_parts.append(f"default: {self._format_js_value(default_value)}")
        
        # Validator
        validator = prop_config.get('validator')
        if validator:
            prop_parts.append(f"validator: {validator}")
        
        return f"{{ {', '.join(prop_parts)} }}"
    
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
            items = [f"'{key}': {self._format_js_value(val)}" for key, val in value.items()]
            return f"{{{', '.join(items)}}}"
        else:
            return f"'{str(value)}'"
    
    def _escape_vue_content(self, content: str) -> str:
        """Escape content for Vue template."""
        # Basic Vue template escaping
        return content.replace('{{', '{{ "{{" }}').replace('}}', '{{ "}}" }}')
    
    def _escape_vue_attribute(self, value: str) -> str:
        """Escape attribute value for Vue template."""
        return value.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    
    def _extract_vue_logic(self, scripts: Dict[str, Any]) -> str:
        """Extract Vue component logic from scripts."""
        logic_parts = []
        
        inline_scripts = scripts.get('inline_scripts', [])
        for script in inline_scripts:
            content = script.get('content', '')
            if content:
                # Basic adaptation of JS to Vue patterns
                adapted_content = self._adapt_js_to_vue(content)
                logic_parts.append(adapted_content)
        
        return '\n\n'.join(logic_parts)
    
    def _adapt_js_to_vue(self, js_content: str) -> str:
        """Adapt JavaScript content for Vue component."""
        adapted = js_content
        
        # Replace DOM queries with Vue refs
        adapted = re.sub(r'document\.getElementById\([\'"]([^\'"]*)[\'""]\)',
                        r'/* Use $refs.\1 in Vue */', adapted)
        
        # Replace event listeners with Vue methods
        adapted = re.sub(r'addEventListener\([\'"]([^\'"]*)[\'"], ([^)]+)\)',
                        r'/* Use @\1="\2" in template */', adapted)
        
        return adapted
    
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
