"""
HTML Converter - Convert YAML manifests to HTML with comprehensive templating

Generates semantic HTML with CSS styling, responsive design support,
and modern web standards compliance.

Copyright 2024 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
from typing import Any, Dict, List, Optional, Union
from html import escape
import logging

from .base_converter import BaseConverter, ConversionResult, StructureWalker, CSSProcessor
from ..exceptions import ConversionError

logger = logging.getLogger(__name__)


class HTMLConverter(BaseConverter):
    """
    Convert YAML manifests to HTML format.
    
    Features:
    - Semantic HTML generation
    - CSS styling integration
    - Responsive design support
    - Modern web standards compliance
    - SEO optimization
    """
    
    def __init__(self, 
                 doctype: str = "html5",
                 include_meta_tags: bool = True,
                 responsive_design: bool = True,
                 **kwargs):
        """
        Initialize HTML converter.
        
        Args:
            doctype: HTML doctype (html5, html4, xhtml)
            include_meta_tags: Whether to include standard meta tags
            responsive_design: Whether to include responsive design elements
            **kwargs: Additional options passed to base converter
        """
        super().__init__(**kwargs)
        self.doctype = doctype
        self.include_meta_tags = include_meta_tags
        self.responsive_design = responsive_design
        self.walker = StructureWalker(self)
    
    @property
    def format_name(self) -> str:
        """Return format name."""
        return "HTML"
    
    @property
    def file_extension(self) -> str:
        """Return file extension."""
        return "html"
    
    def convert(self, manifest: Dict[str, Any], **kwargs) -> ConversionResult:
        """
        Convert manifest to HTML.
        
        Args:
            manifest: Processed YAML manifest
            **kwargs: Additional conversion options
            
        Returns:
            ConversionResult with HTML content
        """
        try:
            # Extract components
            metadata = self.extract_metadata(manifest)
            styles = self.extract_styles(manifest)
            imports = self.extract_imports(manifest)
            structure = manifest.get('structure', {})
            
            # Generate HTML components
            head_html = self._generate_head(metadata, styles, imports)
            body_html = self._generate_body(structure, styles)
            
            # Combine into complete HTML document
            html_content = self._generate_document(head_html, body_html)
            
            # Apply optimizations
            if self.optimize_output:
                html_content = self.optimize_code(html_content)
            
            # Add header comment
            html_content = self.add_header_comment(html_content, manifest)
            
            # Generate filename
            filename = self.generate_filename(manifest, kwargs.get('filename'))
            
            return ConversionResult(
                content=html_content,
                filename=filename,
                format_type=self.format_name.lower(),
                metadata={
                    'title': metadata.get('title', 'Untitled'),
                    'has_styles': bool(styles),
                    'has_imports': bool(any(imports.values())),
                    'element_count': self._count_elements(structure)
                }
            )
            
        except Exception as e:
            raise self.handle_conversion_error(e, "HTML conversion")
    
    def _generate_document(self, head_html: str, body_html: str) -> str:
        """Generate complete HTML document."""
        doctype_map = {
            'html5': '<!DOCTYPE html>',
            'html4': '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">',
            'xhtml': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
        }
        
        doctype = doctype_map.get(self.doctype, doctype_map['html5'])
        lang_attr = 'lang="en"' if self.doctype == 'html5' else 'lang="en" xml:lang="en"'
        
        return f"""{doctype}
<html {lang_attr}>
{head_html}
{body_html}
</html>"""
    
    def _generate_head(self, 
                      metadata: Dict[str, Any], 
                      styles: Dict[str, str], 
                      imports: Dict[str, List[str]]) -> str:
        """Generate HTML head section."""
        head_parts = ['<head>']
        
        # Character encoding
        if self.doctype == 'html5':
            head_parts.append('  <meta charset="UTF-8">')
        else:
            head_parts.append('  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">')
        
        # Responsive viewport
        if self.responsive_design:
            head_parts.append('  <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        
        # Standard meta tags
        if self.include_meta_tags:
            head_parts.extend(self._generate_meta_tags(metadata))
        
        # Title
        title = escape(metadata.get('title', 'Untitled'))
        head_parts.append(f'  <title>{title}</title>')
        
        # External stylesheets
        for style_url in imports.get('styles', []):
            head_parts.append(f'  <link rel="stylesheet" href="{escape(style_url)}">')
        
        # Font imports
        for font_url in imports.get('fonts', []):
            head_parts.append(f'  <link rel="preconnect" href="https://fonts.googleapis.com">')
            head_parts.append(f'  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
            head_parts.append(f'  <link rel="stylesheet" href="{escape(font_url)}">')
        
        # Internal styles
        if styles:
            head_parts.append('  <style>')
            head_parts.extend(self._generate_css(styles))
            head_parts.append('  </style>')
        
        head_parts.append('</head>')
        return '\n'.join(head_parts)
    
    def _generate_meta_tags(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate standard meta tags."""
        meta_tags = []
        
        description = metadata.get('description')
        if description:
            meta_tags.append(f'  <meta name="description" content="{escape(description)}">')
        
        author = metadata.get('author')
        if author:
            meta_tags.append(f'  <meta name="author" content="{escape(author)}">')
        
        keywords = metadata.get('keywords')
        if keywords:
            if isinstance(keywords, list):
                keywords = ', '.join(keywords)
            meta_tags.append(f'  <meta name="keywords" content="{escape(keywords)}">')
        
        # Open Graph tags
        title = metadata.get('title')
        if title:
            meta_tags.append(f'  <meta property="og:title" content="{escape(title)}">')
        
        if description:
            meta_tags.append(f'  <meta property="og:description" content="{escape(description)}">')
        
        meta_tags.append('  <meta property="og:type" content="website">')
        
        return meta_tags
    
    def _generate_css(self, styles: Dict[str, str]) -> List[str]:
        """Generate CSS from styles dictionary."""
        css_lines = []
        
        for selector, rules in styles.items():
            # Convert camelCase to kebab-case for CSS classes
            css_selector = self._format_css_selector(selector)
            
            # Format CSS rules
            formatted_rules = self._format_css_rules(rules)
            
            css_lines.append(f'    {css_selector} {{')
            for rule in formatted_rules:
                css_lines.append(f'      {rule}')
            css_lines.append('    }')
            css_lines.append('')
        
        return css_lines
    
    def _format_css_selector(self, selector: str) -> str:
        """Format CSS selector from style name."""
        # Convert camelCase to kebab-case
        kebab_case = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', selector).lower()
        
        # Add class prefix if not already present
        if not kebab_case.startswith('.') and not kebab_case.startswith('#'):
            kebab_case = f'.{kebab_case}'
        
        return kebab_case
    
    def _format_css_rules(self, rules: str) -> List[str]:
        """Format CSS rules string into individual rules."""
        if not rules:
            return []
        
        # Parse individual CSS properties
        properties = []
        for rule in rules.split(';'):
            rule = rule.strip()
            if rule:
                if not rule.endswith(';'):
                    rule += ';'
                properties.append(rule)
        
        return properties
    
    def _generate_body(self, structure: Dict[str, Any], styles: Dict[str, str]) -> str:
        """Generate HTML body section."""
        body_parts = ['<body>']
        
        # Convert structure to HTML
        if structure:
            body_content = self._convert_structure_to_html(structure, styles)
            body_parts.append(body_content)
        
        body_parts.append('</body>')
        return '\n'.join(body_parts)
    
    def _convert_structure_to_html(self, structure: Any, styles: Dict[str, str], indent: int = 1) -> str:
        """
        Convert manifest structure to HTML elements.
        
        Args:
            structure: Structure element to convert
            styles: Available styles
            indent: Current indentation level
            
        Returns:
            HTML string
        """
        if isinstance(structure, dict):
            return self._convert_element_to_html(structure, styles, indent)
        elif isinstance(structure, list):
            return '\n'.join(
                self._convert_structure_to_html(item, styles, indent) 
                for item in structure
            )
        elif isinstance(structure, str):
            return escape(structure)
        else:
            return str(structure)
    
    def _convert_element_to_html(self, element: Dict[str, Any], styles: Dict[str, str], indent: int) -> str:
        """Convert a single element to HTML."""
        indent_str = '  ' * indent
        
        # Extract element information
        tag_name = None
        attributes = {}
        content = []
        
        for key, value in element.items():
            if key in ['text', 'content']:
                # Text content
                if isinstance(value, str):
                    content.append(escape(value))
                else:
                    content.append(str(value))
            elif key == 'children':
                # Child elements
                if isinstance(value, list):
                    for child in value:
                        child_html = self._convert_structure_to_html(child, styles, indent + 1)
                        content.append(child_html)
                else:
                    child_html = self._convert_structure_to_html(value, styles, indent + 1)
                    content.append(child_html)
            elif key == 'style':
                # Style reference or inline style
                if value in styles:
                    # Reference to defined style
                    css_class = self._format_css_selector(value).lstrip('.')
                    attributes['class'] = css_class
                else:
                    # Inline style
                    attributes['style'] = value
            elif key in ['class', 'id', 'src', 'href', 'alt', 'title']:
                # Standard HTML attributes
                attributes[key] = escape(str(value))
            elif self._is_html_element(key):
                # This key represents an HTML element
                tag_name = key
                if isinstance(value, dict):
                    # Element with attributes and children
                    child_html = self._convert_element_to_html(value, styles, indent + 1)
                    content.append(child_html)
                else:
                    # Element with text content
                    content.append(escape(str(value)))
        
        # If no tag name found, use first key as tag name
        if tag_name is None:
            first_key = next(iter(element.keys()))
            if self._is_html_element(first_key):
                tag_name = first_key
            else:
                tag_name = 'div'  # Default fallback
        
        # Generate attributes string
        attr_str = self._format_attributes(attributes)
        
        # Generate HTML
        if not content:
            # Self-closing or empty element
            if tag_name in ['img', 'br', 'hr', 'input', 'meta', 'link']:
                return f'{indent_str}<{tag_name}{attr_str}>'
            else:
                return f'{indent_str}<{tag_name}{attr_str}></{tag_name}>'
        elif len(content) == 1 and not '\n' in content[0]:
            # Single line content
            return f'{indent_str}<{tag_name}{attr_str}>{content[0]}</{tag_name}>'
        else:
            # Multi-line content
            html_parts = [f'{indent_str}<{tag_name}{attr_str}>']
            for item in content:
                if item.strip():
                    html_parts.append(f'  {indent_str}{item}')
            html_parts.append(f'{indent_str}</{tag_name}>')
            return '\n'.join(html_parts)
    
    def _is_html_element(self, name: str) -> bool:
        """Check if name is a valid HTML element."""
        html_elements = {
            # Common HTML elements
            'html', 'head', 'body', 'title', 'meta', 'link', 'style', 'script',
            'div', 'span', 'p', 'br', 'hr',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'dl', 'dt', 'dd',
            'table', 'thead', 'tbody', 'tr', 'td', 'th',
            'form', 'input', 'textarea', 'select', 'option', 'button', 'label',
            'a', 'img', 'video', 'audio', 'source',
            'header', 'nav', 'main', 'section', 'article', 'aside', 'footer',
            'figure', 'figcaption', 'details', 'summary'
        }
        return name.lower() in html_elements
    
    def _format_attributes(self, attributes: Dict[str, str]) -> str:
        """Format HTML attributes."""
        if not attributes:
            return ''
        
        attr_parts = []
        for key, value in attributes.items():
            attr_parts.append(f'{key}="{value}"')
        
        return ' ' + ' '.join(attr_parts)
    
    def _count_elements(self, structure: Any) -> int:
        """Count total number of elements in structure."""
        count = 0
        
        def count_callback(element, context):
            nonlocal count
            if isinstance(element, dict) and any(self._is_html_element(k) for k in element.keys()):
                count += 1
            return element
        
        self.walker.walk(structure, count_callback)
        return count
    
    def _format_header_comment(self, title: str, description: str) -> str:
        """Format HTML header comment."""
        parts = [f"Generated by WhyML - {title}"]
        if description:
            parts.append(f"Description: {description}")
        parts.append(f"Generated on: {ConversionResult(content='', filename='', format_type='').timestamp}")
        
        comment_content = "\n".join(f"  {part}" for part in parts)
        return f"<!--\n{comment_content}\n-->"
    
    def optimize_code(self, code: str) -> str:
        """Apply HTML-specific optimizations."""
        if not self.optimize_output:
            return code
        
        # Apply base optimizations
        code = super().optimize_code(code)
        
        if self.minify:
            # Remove extra whitespace between tags
            code = re.sub(r'>\s+<', '><', code)
            
            # Remove comments (except IE conditionals)
            code = re.sub(r'<!--(?!\[if).*?-->', '', code, flags=re.DOTALL)
        
        return code
