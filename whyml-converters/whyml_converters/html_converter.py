"""
WhyML Converters - HTML Converter Module

Advanced HTML converter with template processing, semantic structure generation,
and modern HTML5 output with accessibility and SEO optimization.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import re

from whyml_core.utils import StringUtils
from whyml_core.exceptions import ProcessingError
from .base_converter import BaseConverter


class HTMLConverter(BaseConverter):
    """Advanced HTML converter with semantic structure and modern HTML5 output."""
    
    def __init__(self, **kwargs):
        """Initialize HTML converter."""
        super().__init__(**kwargs)
        self.indent_size = 2
        self.current_indent = 0
    
    def _get_output_format(self) -> str:
        """Get output format identifier."""
        return "html"
    
    def _get_template_extension(self) -> str:
        """Get template file extension."""
        return ".html"
    
    def _supports_components(self) -> bool:
        """Check if converter supports components."""
        return False  # HTML doesn't have native components
    
    async def convert_manifest(self, 
                              manifest: Dict[str, Any],
                              output_path: Optional[Union[str, Path]] = None,
                              **options) -> str:
        """Convert WhyML manifest to HTML.
        
        Args:
            manifest: WhyML manifest dictionary
            output_path: Optional output file path
            **options: HTML-specific options
            
        Returns:
            Generated HTML content
        """
        # Reset indentation
        self.current_indent = 0
        
        # Extract manifest sections
        metadata = self._extract_metadata(manifest)
        structure = self._extract_structure(manifest)
        styles = self._extract_styles(manifest)
        scripts = self._extract_scripts(manifest)
        imports = self._extract_imports(manifest)
        
        # Build HTML document
        html_parts = []
        
        # DOCTYPE and html opening
        html_parts.append(self._generate_doctype())
        html_parts.append(self._generate_html_opening(metadata))
        
        # Head section
        self._increase_indent()
        html_parts.append(self._generate_head(metadata, styles, imports, **options))
        
        # Body section
        html_parts.append(self._generate_body_opening(metadata))
        
        # Main content
        self._increase_indent()
        if structure:
            content = await self._generate_structure(structure)
            html_parts.append(content)
        
        # Scripts before closing body
        if scripts:
            html_parts.append(self._generate_scripts(scripts))
        
        self._decrease_indent()
        html_parts.append(self._generate_body_closing())
        
        self._decrease_indent()
        html_parts.append(self._generate_html_closing())
        
        return '\n'.join(html_parts)
    
    def _generate_doctype(self) -> str:
        """Generate HTML5 DOCTYPE."""
        return "<!DOCTYPE html>"
    
    def _generate_html_opening(self, metadata: Dict[str, Any]) -> str:
        """Generate opening html tag with attributes."""
        lang = metadata.get('language', 'en')
        return f'<html lang="{lang}">'
    
    def _generate_html_closing(self) -> str:
        """Generate closing html tag."""
        return "</html>"
    
    def _generate_head(self, 
                      metadata: Dict[str, Any], 
                      styles: Dict[str, Any],
                      imports: Dict[str, Any],
                      **options) -> str:
        """Generate complete head section."""
        head_parts = []
        
        # Opening head tag
        head_parts.append(self._indent() + "<head>")
        self._increase_indent()
        
        # Meta tags
        head_parts.extend(self._generate_meta_tags(metadata))
        
        # Title
        title = metadata.get('title', 'Untitled Page')
        head_parts.append(self._indent() + f"<title>{self._escape_html(title)}</title>")
        
        # External stylesheets
        if imports.get('stylesheets'):
            for stylesheet in imports['stylesheets']:
                head_parts.append(self._generate_stylesheet_link(stylesheet))
        
        # Internal styles
        if styles:
            style_content = self._generate_internal_styles(styles)
            if style_content:
                head_parts.append(style_content)
        
        # External scripts (in head)
        if imports.get('scripts'):
            for script in imports['scripts']:
                if script.get('placement') == 'head':
                    head_parts.append(self._generate_script_tag(script))
        
        # Additional head elements
        if options.get('additional_head'):
            head_parts.append(self._indent() + options['additional_head'])
        
        self._decrease_indent()
        head_parts.append(self._indent() + "</head>")
        
        return '\n'.join(head_parts)
    
    def _generate_meta_tags(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate meta tags from metadata."""
        meta_tags = []
        
        # Essential meta tags
        meta_tags.append(self._indent() + '<meta charset="UTF-8">')
        meta_tags.append(self._indent() + '<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        
        # Description
        if metadata.get('description'):
            description = self._escape_html(metadata['description'])
            meta_tags.append(self._indent() + f'<meta name="description" content="{description}">')
        
        # Keywords
        if metadata.get('keywords'):
            if isinstance(metadata['keywords'], list):
                keywords = ', '.join(metadata['keywords'])
            else:
                keywords = str(metadata['keywords'])
            keywords = self._escape_html(keywords)
            meta_tags.append(self._indent() + f'<meta name="keywords" content="{keywords}">')
        
        # Author
        if metadata.get('author'):
            author = self._escape_html(metadata['author'])
            meta_tags.append(self._indent() + f'<meta name="author" content="{author}">')
        
        # OpenGraph meta tags
        og_data = metadata.get('opengraph', {})
        for property_name, content in og_data.items():
            content = self._escape_html(str(content))
            meta_tags.append(self._indent() + f'<meta property="og:{property_name}" content="{content}">')
        
        # Twitter Card meta tags
        twitter_data = metadata.get('twitter', {})
        for name, content in twitter_data.items():
            content = self._escape_html(str(content))
            meta_tags.append(self._indent() + f'<meta name="twitter:{name}" content="{content}">')
        
        return meta_tags
    
    def _generate_stylesheet_link(self, stylesheet: Dict[str, Any]) -> str:
        """Generate stylesheet link tag."""
        href = stylesheet.get('href', '')
        media = stylesheet.get('media', 'all')
        
        attrs = [f'rel="stylesheet"', f'href="{href}"']
        
        if media != 'all':
            attrs.append(f'media="{media}"')
        
        if stylesheet.get('integrity'):
            attrs.append(f'integrity="{stylesheet["integrity"]}"')
        
        if stylesheet.get('crossorigin'):
            attrs.append(f'crossorigin="{stylesheet["crossorigin"]}"')
        
        return self._indent() + f'<link {" ".join(attrs)}>'
    
    def _generate_internal_styles(self, styles: Dict[str, Any]) -> str:
        """Generate internal CSS styles."""
        css_parts = []
        
        # Process inline styles
        inline_styles = styles.get('inline_styles', {})
        if inline_styles:
            for element_id, properties in inline_styles.items():
                if properties:
                    selector = f"#{element_id}" if not element_id.startswith('.') else element_id
                    css_rule = self._generate_css_rule(selector, properties)
                    css_parts.append(css_rule)
        
        # Process internal styles
        internal_styles = styles.get('internal_styles', {})
        if internal_styles:
            for style_name, rules in internal_styles.items():
                if isinstance(rules, dict):
                    for selector, properties in rules.items():
                        css_rule = self._generate_css_rule(selector, properties)
                        css_parts.append(css_rule)
        
        # Process direct CSS rules
        for key, value in styles.items():
            if key not in ['inline_styles', 'internal_styles', 'external_stylesheets']:
                if isinstance(value, dict):
                    css_rule = self._generate_css_rule(key, value)
                    css_parts.append(css_rule)
                elif isinstance(value, str) and '{' in value and '}' in value:
                    # Direct CSS string
                    css_parts.append(value)
        
        if css_parts:
            css_content = '\n'.join(css_parts)
            return (self._indent() + "<style>\n" + 
                   self._indent_text(css_content, self.current_indent + 1) + "\n" +
                   self._indent() + "</style>")
        
        return ""
    
    def _generate_css_rule(self, selector: str, properties: Dict[str, str]) -> str:
        """Generate CSS rule from selector and properties."""
        if not properties:
            return ""
        
        css_properties = []
        for prop, value in properties.items():
            css_properties.append(f"  {prop}: {value};")
        
        return f"{selector} {{\n" + '\n'.join(css_properties) + "\n}"
    
    def _generate_body_opening(self, metadata: Dict[str, Any]) -> str:
        """Generate opening body tag."""
        body_class = metadata.get('body_class', '')
        if body_class:
            return f'<body class="{body_class}">'
        return '<body>'
    
    def _generate_body_closing(self) -> str:
        """Generate closing body tag."""
        return "</body>"
    
    async def _generate_structure(self, structure: Dict[str, Any]) -> str:
        """Generate HTML structure from manifest structure."""
        if not structure:
            return ""
        
        # Handle different structure formats
        if 'tag' in structure:
            # Single element
            return await self._generate_element(structure)
        elif 'children' in structure:
            # Container with children
            return await self._generate_children(structure['children'])
        else:
            # Process as container
            content_parts = []
            for key, value in structure.items():
                if isinstance(value, dict):
                    element_content = await self._generate_element(value, tag_override=key)
                    content_parts.append(element_content)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            element_content = await self._generate_element(item)
                            content_parts.append(element_content)
            
            return '\n'.join(content_parts)
    
    async def _generate_element(self, 
                               element: Dict[str, Any], 
                               tag_override: Optional[str] = None) -> str:
        """Generate HTML element from structure definition."""
        tag = tag_override or element.get('tag', 'div')
        
        # Handle self-closing tags
        self_closing_tags = {'img', 'br', 'hr', 'input', 'meta', 'link'}
        is_self_closing = tag in self_closing_tags
        
        # Build opening tag
        opening_tag = await self._build_opening_tag(tag, element)
        
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
                       self._indent_text(content, self.current_indent + 1) + '\n' +
                       self._indent() + f"</{tag}>")
            else:
                # Single line content
                return self._indent() + f"{opening_tag}{self._escape_html(content)}</{tag}>"
        
        # Element with children
        element_parts = [self._indent() + opening_tag]
        
        if content:
            self._increase_indent()
            element_parts.append(self._indent() + self._escape_html(content))
            self._decrease_indent()
        
        if children:
            self._increase_indent()
            children_content = await self._generate_children(children)
            element_parts.append(children_content)
            self._decrease_indent()
        
        element_parts.append(self._indent() + f"</{tag}>")
        
        return '\n'.join(element_parts)
    
    async def _build_opening_tag(self, tag: str, element: Dict[str, Any]) -> str:
        """Build opening HTML tag with attributes."""
        attributes = element.get('attributes', {})
        
        attr_parts = []
        for name, value in attributes.items():
            if value is None or value is False:
                continue
            elif value is True:
                # Boolean attribute
                attr_parts.append(name)
            else:
                # Regular attribute
                escaped_value = self._escape_html(str(value))
                attr_parts.append(f'{name}="{escaped_value}"')
        
        if attr_parts:
            return f"<{tag} {' '.join(attr_parts)}>"
        else:
            return f"<{tag}>"
    
    async def _generate_children(self, children: List[Any]) -> str:
        """Generate HTML for list of child elements."""
        child_parts = []
        
        for child in children:
            if isinstance(child, dict):
                if child.get('type') == 'text':
                    # Text node
                    text_content = child.get('content', '')
                    if text_content:
                        child_parts.append(self._indent() + self._escape_html(text_content))
                else:
                    # Element node
                    child_content = await self._generate_element(child)
                    child_parts.append(child_content)
            elif isinstance(child, str):
                # Direct text content
                child_parts.append(self._indent() + self._escape_html(child))
        
        return '\n'.join(child_parts)
    
    def _generate_script_tag(self, script: Dict[str, Any]) -> str:
        """Generate script tag."""
        if script.get('src'):
            # External script
            attrs = [f'src="{script["src"]}"']
            
            if script.get('type') != 'text/javascript':
                attrs.append(f'type="{script["type"]}"')
            
            if script.get('async'):
                attrs.append('async')
            
            if script.get('defer'):
                attrs.append('defer')
            
            if script.get('integrity'):
                attrs.append(f'integrity="{script["integrity"]}"')
            
            if script.get('crossorigin'):
                attrs.append(f'crossorigin="{script["crossorigin"]}"')
            
            return self._indent() + f'<script {" ".join(attrs)}></script>'
        else:
            # Inline script
            script_content = script.get('content', '')
            if script_content:
                return (self._indent() + '<script>\n' +
                       self._indent_text(script_content, self.current_indent + 1) + '\n' +
                       self._indent() + '</script>')
            else:
                return self._indent() + '<script></script>'
    
    def _generate_scripts(self, scripts: Dict[str, Any]) -> str:
        """Generate script tags from scripts definition."""
        script_parts = []
        
        # External scripts
        external_scripts = scripts.get('external_scripts', [])
        for script in external_scripts:
            script_tag = self._generate_script_tag(script)
            script_parts.append(script_tag)
        
        # Inline scripts
        inline_scripts = scripts.get('inline_scripts', [])
        for script in inline_scripts:
            script_tag = self._generate_script_tag(script)
            script_parts.append(script_tag)
        
        return '\n'.join(script_parts)
    
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
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML entities in text."""
        return StringUtils.escape_html(text)
    
    async def _format_content(self, content: str) -> str:
        """Format HTML content for readability."""
        # Basic HTML formatting - could be enhanced with proper HTML formatter
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped:
                formatted_lines.append(line)
            elif formatted_lines and formatted_lines[-1].strip():
                # Preserve single empty lines between content blocks
                formatted_lines.append('')
        
        return '\n'.join(formatted_lines)
    
    async def _minify_content(self, content: str) -> str:
        """Minify HTML content."""
        # Remove comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove whitespace around tags
        content = re.sub(r'>\s+<', '><', content)
        
        return content.strip()
