"""
WhyML Scrapers - Structure Analyzer Module

Advanced HTML structure analysis and conversion to WhyML manifest format
with intelligent element processing and hierarchy management.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, List, Optional, Union
from bs4 import BeautifulSoup, Tag, NavigableString

from whyml_core.utils import StringUtils


class StructureAnalyzer:
    """Advanced HTML structure analyzer for WhyML manifest generation."""
    
    def __init__(self):
        """Initialize structure analyzer."""
        self.ignored_tags = {'script', 'style', 'meta', 'link', 'title'}
        self.inline_tags = {
            'a', 'span', 'strong', 'em', 'b', 'i', 'u', 'small', 'sub', 'sup',
            'code', 'kbd', 'samp', 'var', 'mark', 'del', 'ins', 'abbr', 'cite'
        }
        self.block_tags = {
            'div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'section', 'article',
            'header', 'footer', 'main', 'nav', 'aside', 'blockquote', 'pre'
        }
    
    async def analyze_structure(self, element: Tag) -> Dict[str, Any]:
        """Analyze HTML structure and convert to WhyML format.
        
        Args:
            element: Root HTML element to analyze
            
        Returns:
            WhyML structure dictionary
        """
        return self._convert_element_to_structure(element)
    
    def _convert_element_to_structure(self, element: Tag) -> Dict[str, Any]:
        """Convert HTML element to WhyML structure format recursively.
        
        Args:
            element: HTML element to convert
            
        Returns:
            Structure dictionary
        """
        if not isinstance(element, Tag):
            return {}
        
        # Skip ignored tags
        if element.name in self.ignored_tags:
            return {}
        
        structure = {
            'tag': element.name,
        }
        
        # Extract attributes
        attrs = self._extract_attributes(element)
        if attrs:
            structure['attributes'] = attrs
        
        # Extract text content and children
        content = self._extract_content(element)
        if content:
            if isinstance(content, str):
                structure['content'] = content
            elif isinstance(content, list) and len(content) == 1 and isinstance(content[0], str):
                structure['content'] = content[0]
            else:
                structure['children'] = content
        
        # Add semantic information
        semantic_info = self._analyze_semantic_role(element)
        if semantic_info:
            structure['semantic'] = semantic_info
        
        return structure
    
    def _extract_attributes(self, element: Tag) -> Dict[str, Any]:
        """Extract and filter element attributes.
        
        Args:
            element: HTML element
            
        Returns:
            Filtered attributes dictionary
        """
        attrs = {}
        
        # Important attributes to preserve
        important_attrs = {
            'id', 'class', 'role', 'data-*', 'aria-*', 'title', 'alt',
            'href', 'src', 'type', 'name', 'value', 'placeholder',
            'action', 'method', 'target', 'rel'
        }
        
        for attr_name, attr_value in element.attrs.items():
            # Check if attribute should be preserved
            if (attr_name in important_attrs or 
                attr_name.startswith('data-') or 
                attr_name.startswith('aria-')):
                
                # Handle class attribute specially
                if attr_name == 'class' and isinstance(attr_value, list):
                    attrs[attr_name] = ' '.join(attr_value)
                else:
                    attrs[attr_name] = attr_value
        
        return attrs
    
    def _extract_content(self, element: Tag) -> Union[str, List[Any], None]:
        """Extract content from element (text and children).
        
        Args:
            element: HTML element
            
        Returns:
            Content as string, list of children, or None
        """
        children = []
        text_content = ""
        
        for child in element.children:
            if isinstance(child, NavigableString):
                # Handle text content
                text = str(child).strip()
                if text:
                    # If we already have children, add text as separate item
                    if children:
                        children.append({'type': 'text', 'content': text})
                    else:
                        text_content += text
            
            elif isinstance(child, Tag) and child.name not in self.ignored_tags:
                # Handle child elements
                if text_content.strip():
                    # If we have accumulated text, add it first
                    children.append({'type': 'text', 'content': text_content.strip()})
                    text_content = ""
                
                # Process child element
                child_structure = self._convert_element_to_structure(child)
                if child_structure:
                    children.append(child_structure)
        
        # Handle remaining text content
        if text_content.strip() and not children:
            return StringUtils.clean_text(text_content)
        elif text_content.strip() and children:
            children.append({'type': 'text', 'content': text_content.strip()})
        
        # Return appropriate content format
        if children:
            return children
        elif text_content.strip():
            return StringUtils.clean_text(text_content)
        else:
            return None
    
    def _analyze_semantic_role(self, element: Tag) -> Optional[Dict[str, Any]]:
        """Analyze semantic role and meaning of element.
        
        Args:
            element: HTML element
            
        Returns:
            Semantic information dictionary
        """
        semantic = {}
        
        # HTML5 semantic elements
        semantic_elements = {
            'header': 'page_header',
            'nav': 'navigation',
            'main': 'main_content',
            'section': 'content_section',
            'article': 'article',
            'aside': 'sidebar',
            'footer': 'page_footer'
        }
        
        if element.name in semantic_elements:
            semantic['role'] = semantic_elements[element.name]
        
        # ARIA roles
        aria_role = element.get('role')
        if aria_role:
            semantic['aria_role'] = aria_role
        
        # Content type detection
        content_type = self._detect_content_type(element)
        if content_type:
            semantic['content_type'] = content_type
        
        # Layout role detection
        layout_role = self._detect_layout_role(element)
        if layout_role:
            semantic['layout_role'] = layout_role
        
        return semantic if semantic else None
    
    def _detect_content_type(self, element: Tag) -> Optional[str]:
        """Detect content type based on element characteristics.
        
        Args:
            element: HTML element
            
        Returns:
            Content type string
        """
        # Check classes for content type hints
        classes = element.get('class', [])
        class_string = ' '.join(classes).lower() if classes else ''
        
        # Content type patterns
        content_patterns = {
            'hero': ['hero', 'banner', 'jumbotron'],
            'card': ['card', 'tile', 'box'],
            'list': ['list', 'items', 'collection'],
            'form': ['form', 'contact', 'search'],
            'media': ['media', 'gallery', 'carousel'],
            'testimonial': ['testimonial', 'review', 'quote'],
            'cta': ['cta', 'call-to-action', 'button-group'],
            'feature': ['feature', 'highlight', 'benefit']
        }
        
        for content_type, patterns in content_patterns.items():
            if any(pattern in class_string for pattern in patterns):
                return content_type
        
        # Check by tag and content
        if element.name == 'form':
            return 'form'
        elif element.name in ['ul', 'ol']:
            return 'list'  
        elif element.name == 'blockquote':
            return 'quote'
        elif element.name == 'table':
            return 'table'
        
        return None
    
    def _detect_layout_role(self, element: Tag) -> Optional[str]:
        """Detect layout role of element.
        
        Args:
            element: HTML element
            
        Returns:
            Layout role string
        """
        classes = element.get('class', [])
        class_string = ' '.join(classes).lower() if classes else ''
        
        # Layout patterns
        layout_patterns = {
            'container': ['container', 'wrapper', 'content'],
            'row': ['row', 'flex-row'],
            'column': ['col', 'column', 'flex-col'],
            'grid': ['grid', 'grid-container'],
            'sidebar': ['sidebar', 'aside', 'secondary'],
            'panel': ['panel', 'widget', 'module']
        }
        
        for layout_role, patterns in layout_patterns.items():
            if any(pattern in class_string for pattern in patterns):
                return layout_role
        
        # Check for grid/flex containers
        style = element.get('style', '')
        if 'display: grid' in style or 'display: flex' in style:
            return 'flex_container'
        
        return None
    
    def _simplify_structure(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify structure by removing unnecessary nesting.
        
        Args:
            structure: Structure dictionary
            
        Returns:
            Simplified structure
        """
        if not isinstance(structure, dict):
            return structure
        
        # If element has only one child and no meaningful attributes
        if (structure.get('children') and 
            len(structure['children']) == 1 and
            not structure.get('attributes') and
            structure.get('tag') == 'div'):
            
            child = structure['children'][0]
            if isinstance(child, dict) and child.get('tag'):
                return self._simplify_structure(child)
        
        # Recursively simplify children
        if structure.get('children'):
            structure['children'] = [
                self._simplify_structure(child) if isinstance(child, dict) else child
                for child in structure['children']
            ]
        
        return structure
    
    def _calculate_structure_metrics(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics about the structure.
        
        Args:
            structure: Structure dictionary
            
        Returns:
            Metrics dictionary
        """
        metrics = {
            'depth': 0,
            'element_count': 0,
            'text_nodes': 0,
            'semantic_elements': 0
        }
        
        def calculate_recursive(struct: Dict[str, Any], current_depth: int = 0):
            if not isinstance(struct, dict):
                return
            
            metrics['element_count'] += 1
            metrics['depth'] = max(metrics['depth'], current_depth)
            
            # Count semantic elements
            if struct.get('semantic'):
                metrics['semantic_elements'] += 1
            
            # Count text nodes
            if struct.get('content') and isinstance(struct['content'], str):
                metrics['text_nodes'] += 1
            
            # Process children
            children = struct.get('children', [])
            for child in children:
                if isinstance(child, dict):
                    if child.get('type') == 'text':
                        metrics['text_nodes'] += 1
                    else:
                        calculate_recursive(child, current_depth + 1)
        
        calculate_recursive(structure)
        return metrics
