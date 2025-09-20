"""
HTML Converter - Convert YAML manifests to HTML with comprehensive templating

Generates semantic HTML with CSS styling, responsive design support,
and modern web standards compliance.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
from pathlib import Path
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
            template_vars = self.extract_template_vars(manifest)
            structure = manifest.get('structure', {})
            variables = manifest.get('variables', {})
            config = manifest.get('config', {})
            external_content = manifest.get('external_content', {})
            dependencies = manifest.get('dependencies', [])
            
            # Process external content and create content map for {{EXTERNAL:...}} syntax
            self._external_content_map = {}
            if external_content:
                structure, self._external_content_map = self._process_external_content(structure, external_content, variables, config)
            
            # Generate HTML components
            head_html = self._generate_head(metadata, styles, imports, dependencies, config)
            body_html = self._generate_body(structure, styles, variables, config)
            
            # Combine into complete HTML document
            html_content = self._generate_document(head_html, body_html)
            
            # Replace template variables ({{ hero_text }} -> "Welcome to Our Amazing Product")
            if template_vars:
                html_content = self.replace_template_variables(html_content, template_vars)
            
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
    
    def _process_external_content(self, 
                                structure: Dict[str, Any], 
                                external_content: Dict[str, Any], 
                                variables: Dict[str, Any], 
                                config: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, str]]:
        """Process external content by loading and integrating it into structure.
        
        Returns:
            tuple: (processed_structure, external_content_map)
                - processed_structure: Structure with external content integrated
                - external_content_map: Map of filename to processed content for {{EXTERNAL:...}} syntax
        """
        try:
            from pathlib import Path
            import requests
            from ..manifest_processor import TemplateProcessor
            
            processor = TemplateProcessor()
            external_content_map = {}
            
            # Handle both list and dict formats for external_content
            if isinstance(external_content, list):
                content_items = enumerate(external_content)
            else:
                content_items = external_content.items()
            
            for content_key, content_config in content_items:
                if isinstance(content_config, str):
                    # Simple URL or file path
                    source = content_config
                    target_element = f"external_content_{content_key}" if isinstance(external_content, list) else content_key
                elif isinstance(content_config, dict):
                    source = content_config.get('source', content_config.get('url', ''))
                    target_element = content_config.get('target', f"external_content_{content_key}" if isinstance(external_content, list) else content_key)
                else:
                    continue
                
                if not source:
                    continue
                
                # Load external content
                content = self._load_external_content(source)
                
                # Apply variable substitution to loaded content
                if variables or config:
                    content = processor.substitute_template_variables(content, variables, config)
                
                # Store in external content map for {{EXTERNAL:...}} syntax processing
                # Extract filename from source path for the map key
                filename = Path(source).name if not source.startswith('http') else source
                external_content_map[filename] = content
                
                # Integrate content into structure at target element
                self._integrate_external_content(structure, target_element, content)
            
            return structure, external_content_map
            
        except Exception as e:
            logger.warning(f"Failed to process external content: {e}")
            return structure, {}
    
    def _load_external_content(self, source: str) -> str:
        """Load content from external source (file or URL)."""
        try:
            from pathlib import Path
            import requests
            
            if source.startswith(('http://', 'https://')):
                # Load from URL
                response = requests.get(source, timeout=10)
                response.raise_for_status()
                return response.text
            else:
                # Load from file path
                file_path = Path(source)
                if file_path.exists():
                    return file_path.read_text(encoding='utf-8')
                else:
                    logger.warning(f"External content file not found: {source}")
                    return ""
        except Exception as e:
            logger.warning(f"Failed to load external content from {source}: {e}")
            return ""
    
    def _integrate_external_content(self, structure: Dict[str, Any], target: str, content: str):
        """Integrate external content into structure at specified target."""
        # Create a simple div container for the external content
        # This avoids the unhashable dict issues by using a straightforward approach
        try:
            # Parse the loaded HTML content and create a simple integration
            if not content.strip():
                return
                
            # For simplicity, add external content as a new div element in the structure
            external_element = {
                'tag': 'div',
                'attributes': {'class': f'external-content-{target.replace("_", "-")}'},
                'content': content,
                'type': 'raw_html'
            }
            
            # Add to structure in a safe way
            if 'external_content_container' not in structure:
                structure['external_content_container'] = {
                    'tag': 'div',
                    'attributes': {'class': 'external-content-wrapper'},
                    'children': []
                }
            
            if isinstance(structure['external_content_container'].get('children'), list):
                structure['external_content_container']['children'].append(external_element)
            else:
                structure['external_content_container']['children'] = [external_element]
                
        except Exception as e:
            logger.warning(f"Failed to integrate external content for target '{target}': {e}")
            # Fallback: just add as simple text content
            structure[f'external_{target}'] = {'content': content[:500] + '...' if len(content) > 500 else content}
    
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
                      imports: Dict[str, List[str]],
                      dependencies: List[str] = None,
                      config: Dict[str, Any] = None) -> str:
        """Generate HTML head section."""
        head_parts = ['<head>']
        
        # Character encoding
        if self.doctype == 'html5':
            head_parts.append('  <meta charset="utf-8">')
        else:
            head_parts.append('  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
        
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
        
        # Dependencies (additional CSS/JS from manifest dependencies)
        if dependencies:
            for dep in dependencies:
                if isinstance(dep, str):
                    if dep.endswith('.css'):
                        head_parts.append(f'  <link rel="stylesheet" href="{escape(dep)}">')
                    elif dep.endswith('.js'):
                        head_parts.append(f'  <script src="{escape(dep)}"></script>')
                elif isinstance(dep, dict):
                    dep_type = dep.get('type', '')
                    dep_url = dep.get('url', dep.get('src', ''))
                    if dep_type == 'css' or dep_url.endswith('.css'):
                        head_parts.append(f'  <link rel="stylesheet" href="{escape(dep_url)}">')
                    elif dep_type == 'js' or dep_url.endswith('.js'):
                        head_parts.append(f'  <script src="{escape(dep_url)}"></script>')
        
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
    
    def _generate_body(self, 
                      structure: Dict[str, Any], 
                      styles: Dict[str, str], 
                      variables: Dict[str, Any] = None, 
                      config: Dict[str, Any] = None) -> str:
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
        try:
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
        except TypeError as e:
            if "unhashable type" in str(e):
                logger.error(f"Unhashable type error in structure conversion: {e}")
                logger.error(f"Structure type: {type(structure)}")
                logger.error(f"Structure content: {str(structure)[:200]}...")
                # Return safe fallback
                return f'<!-- Error processing structure: {e} -->'
            else:
                raise
    
    def _process_external_syntax(self, content: str, external_content_map: Dict[str, str]) -> str:
        """
        Process {{EXTERNAL:filename}} syntax before Jinja2 template substitution.
        
        This custom WhyML syntax allows inline insertion of external content.
        Must be processed before Jinja2 to avoid template parsing errors.
        
        Args:
            content: Content string that may contain {{EXTERNAL:...}} syntax
            external_content_map: Map of filename to processed content
            
        Returns:
            Content with {{EXTERNAL:...}} syntax replaced by actual content
        """
        import re
        
        def replace_external(match):
            filename = match.group(1)
            if filename in external_content_map:
                return external_content_map[filename]
            else:
                # Return placeholder if external content not found
                return f'<!-- External content not found: {filename} -->'
        
        # Replace {{EXTERNAL:filename}} with actual content
        pattern = r'\{\{EXTERNAL:([^}]+)\}\}'
        return re.sub(pattern, replace_external, content)

    def _convert_element_to_html(self, element: Dict[str, Any], styles: Dict[str, str], indent: int) -> str:
        """Convert a single element to HTML."""
        indent_str = '  ' * indent
        
        # Extract element information
        tag_name = None
        attributes = {}
        content = []
        
        for key, value in element.items():
            if key in ['text', 'content']:
                # Text content - process {{EXTERNAL:...}} syntax first
                if isinstance(value, str):
                    processed_value = value
                    # Process external syntax if we have external content available
                    if hasattr(self, '_external_content_map') and self._external_content_map:
                        processed_value = self._process_external_syntax(value, self._external_content_map)
                    content.append(escape(processed_value))
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
                    # Process the element's attributes and children directly
                    for sub_key, sub_value in value.items():
                        if sub_key in ['text', 'content']:
                            if isinstance(sub_value, str):
                                processed_value = sub_value
                                if hasattr(self, '_external_content_map') and self._external_content_map:
                                    processed_value = self._process_external_syntax(sub_value, self._external_content_map)
                                content.append(escape(processed_value))
                            else:
                                content.append(str(sub_value))
                        elif sub_key == 'children':
                            if isinstance(sub_value, list):
                                for child in sub_value:
                                    child_html = self._convert_structure_to_html(child, styles, indent + 1)
                                    content.append(child_html)
                            else:
                                child_html = self._convert_structure_to_html(sub_value, styles, indent + 1)
                                content.append(child_html)
                        elif sub_key == 'style':
                            if sub_value in styles:
                                css_class = self._format_css_selector(sub_value).lstrip('.')
                                attributes['class'] = css_class
                            else:
                                attributes['style'] = sub_value
                        elif sub_key in ['class', 'id', 'src', 'href', 'alt', 'title']:
                            attributes[sub_key] = escape(str(sub_value))
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
