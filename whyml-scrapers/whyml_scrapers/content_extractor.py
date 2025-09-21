"""
WhyML Scrapers - Content Extractor Module

Advanced content extraction including styles, scripts, and structured data
with intelligent parsing and conversion capabilities.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
import json
from typing import Dict, Any, List, Optional, Set, Union
from bs4 import BeautifulSoup, Tag, NavigableString

from whyml_core.utils import StringUtils


class ContentExtractor:
    """Advanced content extraction with intelligent parsing and conversion."""
    
    def __init__(self):
        """Initialize content extractor."""
        pass
    
    async def extract_styles(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract and process CSS styles from webpage.
        
        Args:
            soup: Parsed HTML
            
        Returns:
            Styles dictionary with organized CSS rules
        """
        styles = {
            'inline_styles': {},
            'internal_styles': {},
            'external_stylesheets': []
        }
        
        # Extract inline styles
        elements_with_style = soup.find_all(attrs={'style': True})
        for i, element in enumerate(elements_with_style):
            style_content = element['style']
            if style_content.strip():
                # Create unique identifier for inline style
                element_id = element.get('id') or f"element_{i}"
                styles['inline_styles'][element_id] = self._parse_css_properties(style_content)
        
        # Extract internal styles
        style_tags = soup.find_all('style')
        for i, style_tag in enumerate(style_tags):
            css_content = style_tag.get_text()
            if css_content.strip():
                parsed_rules = self._parse_css_rules(css_content)
                styles['internal_styles'][f'style_block_{i}'] = parsed_rules
        
        # Extract external stylesheet references
        link_tags = soup.find_all('link', rel='stylesheet')
        for link in link_tags:
            href = link.get('href')
            if href:
                stylesheet_info = {
                    'href': href,
                    'media': link.get('media', 'all'),
                    'type': link.get('type', 'text/css')
                }
                if link.get('integrity'):
                    stylesheet_info['integrity'] = link['integrity']
                if link.get('crossorigin'):
                    stylesheet_info['crossorigin'] = link['crossorigin']
                
                styles['external_stylesheets'].append(stylesheet_info)
        
        return styles
    
    def _parse_css_properties(self, css_text: str) -> Dict[str, str]:
        """Parse CSS properties from inline style attribute.
        
        Args:
            css_text: CSS property string
            
        Returns:
            Dictionary of CSS properties
        """
        properties = {}
        
        # Split by semicolon and process each property
        for declaration in css_text.split(';'):
            declaration = declaration.strip()
            if ':' in declaration:
                property_name, property_value = declaration.split(':', 1)
                property_name = property_name.strip()
                property_value = property_value.strip()
                
                if property_name and property_value:
                    properties[property_name] = property_value
        
        return properties
    
    def _parse_css_rules(self, css_content: str) -> Dict[str, Any]:
        """Parse CSS rules from style block content.
        
        Args:
            css_content: CSS rule text
            
        Returns:
            Dictionary of parsed CSS rules
        """
        rules = {}
        
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Find CSS rules with regex
        rule_pattern = r'([^{]+)\{([^}]+)\}'
        matches = re.finditer(rule_pattern, css_content, re.MULTILINE)
        
        for i, match in enumerate(matches):
            selector = match.group(1).strip()
            declarations = match.group(2).strip()
            
            if selector and declarations:
                # Parse declarations
                properties = self._parse_css_properties(declarations)
                
                # Handle multiple selectors
                selectors = [s.strip() for s in selector.split(',')]
                for sel in selectors:
                    if sel:
                        rule_key = sel if len(selectors) == 1 else f"{sel}_{i}"
                        rules[rule_key] = properties
        
        return rules
    
    async def extract_scripts(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract JavaScript content and references.
        
        Args:
            soup: Parsed HTML
            
        Returns:
            Scripts dictionary
        """
        scripts = {
            'inline_scripts': [],
            'external_scripts': [],
            'event_handlers': {}
        }
        
        # Extract inline scripts
        script_tags = soup.find_all('script', src=False)
        for i, script in enumerate(script_tags):
            content = script.get_text()
            if content.strip():
                script_info = {
                    'content': content.strip(),
                    'type': script.get('type', 'text/javascript'),
                    'id': script.get('id') or f'inline_script_{i}'
                }
                scripts['inline_scripts'].append(script_info)
        
        # Extract external scripts
        external_scripts = soup.find_all('script', src=True)
        for script in external_scripts:
            script_info = {
                'src': script['src'],
                'type': script.get('type', 'text/javascript'),
                'async': script.has_attr('async'),
                'defer': script.has_attr('defer')
            }
            
            if script.get('integrity'):
                script_info['integrity'] = script['integrity']
            if script.get('crossorigin'):
                script_info['crossorigin'] = script['crossorigin']
            
            scripts['external_scripts'].append(script_info)
        
        # Extract event handlers
        event_attrs = ['onclick', 'onload', 'onchange', 'onsubmit', 'onmouseover', 'onmouseout']
        for attr in event_attrs:
            elements = soup.find_all(attrs={attr: True})
            if elements:
                scripts['event_handlers'][attr] = []
                for element in elements:
                    scripts['event_handlers'][attr].append({
                        'element': element.name,
                        'handler': element[attr],
                        'id': element.get('id'),
                        'class': element.get('class')
                    })
        
        return scripts
    
    async def extract_media(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract media content (images, videos, audio).
        
        Args:
            soup: Parsed HTML
            
        Returns:
            Media dictionary
        """
        media = {
            'images': [],
            'videos': [],
            'audio': [],
            'background_images': []
        }
        
        # Extract images
        images = soup.find_all('img')
        for img in images:
            image_info = {
                'src': img.get('src'),
                'alt': img.get('alt', ''),
                'title': img.get('title'),
                'width': img.get('width'),
                'height': img.get('height'),
                'loading': img.get('loading'),
                'sizes': img.get('sizes'),
                'srcset': img.get('srcset')
            }
            
            # Remove None values
            image_info = {k: v for k, v in image_info.items() if v is not None}
            media['images'].append(image_info)
        
        # Extract videos
        videos = soup.find_all('video')
        for video in videos:
            video_info = {
                'src': video.get('src'),
                'poster': video.get('poster'),
                'controls': video.has_attr('controls'),
                'autoplay': video.has_attr('autoplay'),
                'loop': video.has_attr('loop'),
                'muted': video.has_attr('muted'),
                'width': video.get('width'),
                'height': video.get('height')
            }
            
            # Extract source elements
            sources = video.find_all('source')
            if sources:
                video_info['sources'] = []
                for source in sources:
                    video_info['sources'].append({
                        'src': source.get('src'),
                        'type': source.get('type'),
                        'media': source.get('media')
                    })
            
            media['videos'].append(video_info)
        
        # Extract audio
        audio_elements = soup.find_all('audio')
        for audio in audio_elements:
            audio_info = {
                'src': audio.get('src'),
                'controls': audio.has_attr('controls'),
                'autoplay': audio.has_attr('autoplay'),
                'loop': audio.has_attr('loop'),
                'muted': audio.has_attr('muted')
            }
            
            # Extract source elements
            sources = audio.find_all('source')
            if sources:
                audio_info['sources'] = []
                for source in sources:
                    audio_info['sources'].append({
                        'src': source.get('src'),
                        'type': source.get('type')
                    })
            
            media['audio'].append(audio_info)
        
        # Extract background images from CSS
        style_elements = soup.find_all(attrs={'style': True})
        for element in style_elements:
            style = element['style']
            bg_image_match = re.search(r'background-image\s*:\s*url\(["\']?([^"\']+)["\']?\)', style)
            if bg_image_match:
                media['background_images'].append({
                    'url': bg_image_match.group(1),
                    'element': element.name,
                    'id': element.get('id'),
                    'class': element.get('class')
                })
        
        return media
    
    async def extract_forms(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract form elements and structure.
        
        Args:
            soup: Parsed HTML
            
        Returns:
            Forms dictionary
        """
        forms = []
        
        form_elements = soup.find_all('form')
        for i, form in enumerate(form_elements):
            form_info = {
                'id': form.get('id') or f'form_{i}',
                'action': form.get('action'),
                'method': form.get('method', 'GET').upper(),
                'enctype': form.get('enctype'),
                'fields': []
            }
            
            # Extract form fields
            inputs = form.find_all(['input', 'select', 'textarea', 'button'])
            for field in inputs:
                field_info = {
                    'tag': field.name,
                    'type': field.get('type'),
                    'name': field.get('name'),
                    'id': field.get('id'),
                    'placeholder': field.get('placeholder'),
                    'required': field.has_attr('required'),
                    'disabled': field.has_attr('disabled'),
                    'readonly': field.has_attr('readonly')
                }
                
                # Handle select options
                if field.name == 'select':
                    options = field.find_all('option')
                    field_info['options'] = []
                    for option in options:
                        field_info['options'].append({
                            'value': option.get('value'),
                            'text': option.get_text().strip(),
                            'selected': option.has_attr('selected')
                        })
                
                # Handle textarea content
                elif field.name == 'textarea':
                    field_info['value'] = field.get_text().strip()
                
                # Handle input value
                elif field.name == 'input':
                    field_info['value'] = field.get('value')
                
                form_info['fields'].append(field_info)
            
            forms.append(form_info)
        
        return {'forms': forms}
    
    async def extract_structured_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract structured data (JSON-LD, microdata, etc.).
        
        Args:
            soup: Parsed HTML
            
        Returns:
            List of structured data objects
        """
        structured_data = []
        
        # Extract JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.get_text())
                structured_data.append({
                    'type': 'json-ld',
                    'data': data
                })
            except json.JSONDecodeError:
                # Skip invalid JSON
                pass
        
        # Extract microdata
        microdata_elements = soup.find_all(attrs={'itemscope': True})
        for element in microdata_elements:
            microdata = {
                'type': 'microdata',
                'itemtype': element.get('itemtype'),
                'properties': {}
            }
            
            # Find itemprop elements within this scope
            props = element.find_all(attrs={'itemprop': True})
            for prop in props:
                prop_name = prop.get('itemprop')
                prop_value = self._extract_microdata_value(prop)
                
                if prop_name and prop_value:
                    if prop_name in microdata['properties']:
                        # Handle multiple values
                        if not isinstance(microdata['properties'][prop_name], list):
                            microdata['properties'][prop_name] = [microdata['properties'][prop_name]]
                        microdata['properties'][prop_name].append(prop_value)
                    else:
                        microdata['properties'][prop_name] = prop_value
            
            if microdata['properties']:
                structured_data.append(microdata)
        
        return structured_data
    
    def _extract_microdata_value(self, element: Tag) -> Optional[str]:
        """Extract value from microdata element.
        
        Args:
            element: HTML element with itemprop
            
        Returns:
            Extracted value or None
        """
        # Handle different element types
        if element.name == 'meta':
            return element.get('content')
        elif element.name in ['img', 'audio', 'video']:
            return element.get('src')
        elif element.name == 'a':
            return element.get('href')
        elif element.name == 'time':
            return element.get('datetime') or element.get_text().strip()
        else:
            return element.get_text().strip()
    
    async def extract_navigation(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract navigation structure.
        
        Args:
            soup: Parsed HTML
            
        Returns:
            Navigation dictionary
        """
        navigation = {
            'main_nav': None,
            'breadcrumbs': None,
            'footer_nav': None,
            'sidebar_nav': None
        }
        
        # Extract main navigation
        main_nav = soup.find('nav') or soup.find(attrs={'role': 'navigation'})
        if main_nav:
            navigation['main_nav'] = self._extract_nav_structure(main_nav)
        
        # Extract breadcrumbs
        breadcrumb_selectors = [
            '.breadcrumb', '.breadcrumbs', '[aria-label*="breadcrumb"]',
            '.bc', '.trail'
        ]
        
        for selector in breadcrumb_selectors:
            breadcrumb = soup.select_one(selector)
            if breadcrumb:
                navigation['breadcrumbs'] = self._extract_breadcrumb_structure(breadcrumb)
                break
        
        # Extract footer navigation
        footer = soup.find('footer')
        if footer:
            footer_nav = footer.find(['nav', 'ul'])
            if footer_nav:
                navigation['footer_nav'] = self._extract_nav_structure(footer_nav)
        
        return navigation
    
    def _extract_nav_structure(self, nav_element: Tag) -> Dict[str, Any]:
        """Extract navigation structure from nav element.
        
        Args:
            nav_element: Navigation HTML element
            
        Returns:
            Navigation structure
        """
        nav_data = {
            'type': 'navigation',
            'items': []
        }
        
        # Find all links in navigation
        links = nav_element.find_all('a', href=True)
        
        for link in links:
            item = {
                'text': link.get_text().strip(),
                'href': link['href'],
                'title': link.get('title')
            }
            
            # Check if it's active/current
            if 'active' in link.get('class', []) or 'current' in link.get('class', []):
                item['active'] = True
            
            nav_data['items'].append(item)
        
        return nav_data
    
    def _extract_breadcrumb_structure(self, breadcrumb_element: Tag) -> Dict[str, Any]:
        """Extract breadcrumb structure.
        
        Args:
            breadcrumb_element: Breadcrumb HTML element
            
        Returns:
            Breadcrumb structure
        """
        breadcrumb = {
            'type': 'breadcrumb',
            'items': []
        }
        
        # Extract breadcrumb items
        links = breadcrumb_element.find_all('a')
        
        for i, link in enumerate(links):
            item = {
                'text': link.get_text().strip(),
                'href': link.get('href'),
                'position': i + 1
            }
            breadcrumb['items'].append(item)
        
        # Check for current page (non-link item)
        current_items = breadcrumb_element.find_all(text=True)
        for text in current_items:
            text = text.strip()
            if text and text not in [item['text'] for item in breadcrumb['items']]:
                breadcrumb['items'].append({
                    'text': text,
                    'href': None,
                    'current': True,
                    'position': len(breadcrumb['items']) + 1
                })
        
        return breadcrumb
