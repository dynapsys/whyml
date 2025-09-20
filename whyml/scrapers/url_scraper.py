"""
URL Scraper - Extract content and structure from web pages

Intelligent web scraping with content extraction, structure analysis,
and automatic YAML manifest generation from websites.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
import asyncio
import aiohttp
from typing import Any, Dict, List, Optional, Union, Set
from urllib.parse import urljoin, urlparse, urlunparse
try:
    from bs4 import BeautifulSoup, Tag, NavigableString
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    # Fallback classes for when BS4 is not available
    class BeautifulSoup:
        def __init__(self, *args, **kwargs):
            raise ImportError("beautifulsoup4 is required for web scraping. Install with: pip install beautifulsoup4")
    
    class Tag:
        pass
    
    class NavigableString:
        pass
import logging

from ..exceptions import NetworkError, ConversionError
from ..manifest_processor import ManifestProcessor

logger = logging.getLogger(__name__)


class URLScraper:
    """
    Scrape websites and convert them to YAML manifests.
    
    Features:
    - Intelligent content extraction
    - Structure analysis and conversion
    - CSS style extraction
    - Meta information extraction
    - Responsive design detection
    """
    
    def __init__(self, 
                 user_agent: str = "WhyML-Scraper/1.0",
                 timeout: int = 30,
                 max_redirects: int = 10,
                 extract_styles: bool = True,
                 extract_scripts: bool = False,
                 max_depth: Optional[int] = None,
                 flatten_containers: bool = False,
                 simplify_structure: bool = False,
                 preserve_semantic_tags: bool = True,
                 sections: Optional[List[str]] = None):
        """
        Initialize URL scraper with advanced simplification options.
        
        Args:
            user_agent: User agent for requests
            timeout: Request timeout in seconds
            max_redirects: Maximum redirects to follow
            extract_styles: Whether to extract CSS styles
            extract_scripts: Whether to extract JavaScript
            max_depth: Maximum nesting depth for structure (None = unlimited)
            flatten_containers: Merge wrapper/container divs with minimal content
            simplify_structure: Apply general structure simplification rules
            preserve_semantic_tags: Keep semantic HTML5 tags (article, section, etc.)
            sections: Only extract specific sections (None = all sections)
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.extract_styles = extract_styles
        self.extract_scripts = extract_scripts
        self.max_depth = max_depth
        self.flatten_containers = flatten_containers
        self.simplify_structure = simplify_structure
        self.preserve_semantic_tags = preserve_semantic_tags
        self.sections = sections or ['metadata', 'styles', 'structure', 'imports', 'analysis']
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': self.user_agent}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape a URL and convert to manifest format.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary representing YAML manifest
        """
        if not self.session:
            raise NetworkError("Session not initialized. Use async context manager.")
        
        try:
            # Fetch the webpage
            html_content = await self._fetch_url(url)
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract components
            metadata = self._extract_metadata(soup, url)
            styles = self._extract_styles(soup, url) if self.extract_styles else {}
            imports = self._extract_imports(soup, url)
            structure = self._extract_structure(soup)
            
            # Add page analysis
            analysis = self._analyze_page(soup, url)
            
            # Build full manifest
            full_manifest = {
                'metadata': metadata,
                'styles': styles,
                'structure': structure,
                'imports': imports,
                'analysis': analysis
            }
            
            # Filter sections based on user request
            manifest = self._filter_sections(full_manifest)
            
            # Apply structure simplification if requested
            if self.simplify_structure or self.flatten_containers or self.max_depth:
                manifest = self._apply_simplification(manifest)
            
            return manifest
            
        except aiohttp.ClientError as e:
            raise NetworkError(f"Failed to fetch URL: {e}", url=url)
        except Exception as e:
            raise ConversionError(f"Failed to scrape URL: {e}", source_format="html", target_format="yaml")
    
    async def _fetch_url(self, url: str) -> str:
        """Fetch URL content."""
        async with self.session.get(url) as response:
            if response.status != 200:
                raise NetworkError(
                    f"HTTP {response.status}: {response.reason}",
                    url=url,
                    status_code=response.status
                )
            
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type:
                logger.warning(f"URL may not be HTML: {content_type}")
            
            return await response.text()
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from HTML head."""
        title = self._get_title(soup)
        description = self._get_meta_content(soup, 'description')
        
        # Ensure description is always present - generate one if missing
        if not description:
            # Try to extract from Open Graph first
            og_data = self._extract_open_graph(soup)
            description = og_data.get('description') if og_data else None
            
            # If still no description, generate a default one
            if not description:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                if title:
                    description = f"Content from {title} - scraped from {domain}"
                else:
                    description = f"Web content scraped from {domain}"
        
        metadata = {
            'title': title or f"Content from {urlparse(url).netloc}",
            'description': description,
            'keywords': self._get_meta_content(soup, 'keywords'),
            'author': self._get_meta_content(soup, 'author'),
            'source_url': url,
            'extracted_at': self._get_current_timestamp()
        }
        
        # Open Graph metadata
        og_data = self._extract_open_graph(soup)
        if og_data:
            metadata['open_graph'] = og_data
        
        # Schema.org structured data
        schema_data = self._extract_schema_org(soup)
        if schema_data:
            metadata['schema_org'] = schema_data
        
        # Language
        lang = soup.html.get('lang') if soup.html else None
        if lang:
            metadata['language'] = lang
        
        return {k: v for k, v in metadata.items() if v is not None}
    
    def _get_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title."""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else None
    
    def _get_meta_content(self, soup: BeautifulSoup, name: str) -> Optional[str]:
        """Extract meta tag content."""
        meta_tag = soup.find('meta', attrs={'name': name}) or soup.find('meta', attrs={'property': name})
        return meta_tag.get('content') if meta_tag else None
    
    def _extract_open_graph(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Open Graph metadata."""
        og_data = {}
        og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:')})
        
        for tag in og_tags:
            property_name = tag.get('property')
            content = tag.get('content')
            if property_name and content:
                key = property_name.replace('og:', '')
                og_data[key] = content
        
        return og_data
    
    def _extract_schema_org(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract Schema.org structured data."""
        schema_data = []
        
        # JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                import json
                data = json.loads(script.string)
                schema_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return schema_data
    
    def _extract_styles(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        """Extract CSS styles and convert to manifest format."""
        styles = {}
        
        # Extract inline styles
        elements_with_style = soup.find_all(attrs={'style': True})
        for i, element in enumerate(elements_with_style):
            style_content = element.get('style')
            if style_content:
                # Create a unique style name
                tag_name = element.name
                element_id = element.get('id', f'element_{i}')
                style_name = f"{tag_name}_{element_id}".replace('-', '_')
                styles[style_name] = style_content.strip()
        
        # Extract CSS classes and their styles (basic extraction)
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            css_content = style_tag.string
            if css_content:
                parsed_styles = self._parse_css_content(css_content)
                styles.update(parsed_styles)
        
        return styles
    
    def _parse_css_content(self, css_content: str) -> Dict[str, str]:
        """Parse CSS content and extract class-based styles."""
        styles = {}
        
        # Simple CSS parsing (could be enhanced with a proper CSS parser)
        css_rules = re.findall(r'([^{]+)\{([^}]+)\}', css_content, re.DOTALL)
        
        for selector, rules in css_rules:
            selector = selector.strip()
            rules = rules.strip()
            
            # Convert CSS selector to manifest style name
            if selector.startswith('.'):
                style_name = selector[1:].replace('-', '_').replace(' ', '_')
                if style_name and style_name.isidentifier():
                    # Clean up CSS rules
                    cleaned_rules = '; '.join(rule.strip() for rule in rules.split(';') if rule.strip())
                    styles[style_name] = cleaned_rules
        
        return styles
    
    def _extract_imports(self, soup: BeautifulSoup, url: str) -> Dict[str, List[str]]:
        """Extract external resources (stylesheets, scripts, fonts)."""
        imports = {
            'styles': [],
            'scripts': [],
            'fonts': []
        }
        
        # Stylesheets
        link_tags = soup.find_all('link', rel='stylesheet')
        for link in link_tags:
            href = link.get('href')
            if href:
                absolute_url = urljoin(url, href)
                imports['styles'].append(absolute_url)
        
        # Scripts
        if self.extract_scripts:
            script_tags = soup.find_all('script', src=True)
            for script in script_tags:
                src = script.get('src')
                if src:
                    absolute_url = urljoin(url, src)
                    imports['scripts'].append(absolute_url)
        
        # Fonts (Google Fonts, etc.)
        font_links = soup.find_all('link', href=re.compile(r'fonts\.googleapis\.com|fonts\.gstatic\.com'))
        for link in font_links:
            href = link.get('href')
            if href:
                absolute_url = urljoin(url, href)
                imports['fonts'].append(absolute_url)
        
        return {k: v for k, v in imports.items() if v}
    
    def _extract_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract HTML structure and convert to manifest format."""
        # Find the main content area
        main_content = self._find_main_content(soup)
        
        if main_content:
            return self._convert_element_to_manifest(main_content)
        else:
            # Fallback to body
            body = soup.find('body')
            if body:
                return self._convert_element_to_manifest(body)
            else:
                return {'div': {'text': 'No content found'}}
    
    def _find_main_content(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find the main content area of the page."""
        # Try common main content selectors, prioritizing containers first
        main_selectors = [
            '.container',
            '.wrapper',
            '#container',
            '#wrapper',
            'main',
            '[role="main"]',
            '.main-content',
            '.content',
            '#main',
            '#content',
            'article',
            '.post-content',
            '.entry-content'
        ]
        
        for selector in main_selectors:
            element = soup.select_one(selector)
            if element and self._has_substantial_content(element):
                return element
        
        return None
    
    def _has_substantial_content(self, element: Tag) -> bool:
        """Check if element has substantial content."""
        text_content = element.get_text().strip()
        return len(text_content) > 100  # Arbitrary threshold
    
    def _convert_element_to_manifest(self, element: Tag) -> Dict[str, Any]:
        """Convert HTML element to manifest structure."""
        if isinstance(element, NavigableString):
            return str(element).strip()
        
        if not isinstance(element, Tag):
            return {}
        
        result = {}
        tag_name = element.name
        
        # Extract attributes
        attributes = {}
        for attr, value in element.attrs.items():
            if attr in ['class', 'id', 'style', 'src', 'href', 'alt', 'title']:
                if isinstance(value, list):
                    # Convert AttributeValueList and other list types to space-separated string
                    attributes[attr] = ' '.join(str(v) for v in value)
                else:
                    # Ensure all values are basic Python types (strings)
                    attributes[attr] = str(value) if value is not None else None
        
        # Extract children
        children = []
        text_content = []
        
        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    text_content.append(text)
            elif isinstance(child, Tag):
                child_manifest = self._convert_element_to_manifest(child)
                if child_manifest:
                    children.append(child_manifest)
        
        # Build element structure
        element_content = {}
        
        # Add attributes
        if attributes:
            element_content.update(attributes)
        
        # Add text content
        if text_content and not children:
            combined_text = ' '.join(text_content)
            if combined_text:
                element_content['text'] = combined_text
        
        # Add children
        if children:
            if len(children) == 1:
                element_content['children'] = children[0]
            else:
                element_content['children'] = children
        
        # If no content, just return empty element
        if not element_content:
            element_content = {}
        
        result[tag_name] = element_content
        return result
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def scrape_multiple_urls(self, urls: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Scrape multiple URLs concurrently.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            Dictionary mapping URLs to their manifests
        """
        tasks = [self.scrape_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        scraped_data = {}
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to scrape {url}: {result}")
                scraped_data[url] = {'error': str(result)}
            else:
                scraped_data[url] = result
        
        return scraped_data
    
    def clean_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and optimize extracted manifest."""
        # Remove empty sections
        cleaned = {}
        for key, value in manifest.items():
            if value:  # Only include non-empty values
                cleaned[key] = value
        
        # Optimize styles (remove duplicates, merge similar)
        if 'styles' in cleaned:
            cleaned['styles'] = self._optimize_styles(cleaned['styles'])
        
        # Simplify structure (remove unnecessary nesting)
        if 'structure' in cleaned:
            cleaned['structure'] = self._simplify_structure(cleaned['structure'])
        
        return cleaned
    
    def _optimize_styles(self, styles: Dict[str, str]) -> Dict[str, str]:
        """Optimize styles by removing duplicates and merging similar ones."""
        optimized = {}
        seen_styles = {}
        
        for name, css in styles.items():
            # Normalize CSS
            normalized = self._normalize_css(css)
            
            if normalized in seen_styles:
                # Style already exists, could merge names
                continue
            else:
                seen_styles[normalized] = name
                optimized[name] = css
        
        return optimized
    
    def _normalize_css(self, css: str) -> str:
        """Normalize CSS for comparison."""
        # Remove extra whitespace and normalize property order
        properties = []
        for prop in css.split(';'):
            prop = prop.strip()
            if prop:
                properties.append(prop)
        
        return '; '.join(sorted(properties))
    
    def _simplify_structure(self, structure: Any) -> Any:
        """Simplify structure by removing unnecessary nesting."""
        if isinstance(structure, dict):
            simplified = {}
            for key, value in structure.items():
                simplified_value = self._simplify_structure(value)
                if simplified_value:
                    simplified[key] = simplified_value
            return simplified
        elif isinstance(structure, list):
            simplified = []
            for item in structure:
                simplified_item = self._simplify_structure(item)
                if simplified_item:
                    simplified.append(simplified_item)
            return simplified
        else:
            return structure
    
    def _analyze_page(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Analyze page structure and content for insights."""
        analysis = {}
        
        # Page type detection
        page_type = self._detect_page_type(soup)
        analysis['page_type'] = page_type
        
        # Content statistics
        analysis['content_stats'] = self._analyze_content_stats(soup)
        
        # Structure complexity
        analysis['structure_complexity'] = self._analyze_structure_complexity(soup)
        
        # SEO analysis
        analysis['seo_analysis'] = self._analyze_seo(soup)
        
        # Accessibility analysis
        analysis['accessibility'] = self._analyze_accessibility(soup)
        
        return analysis
    
    def _detect_page_type(self, soup: BeautifulSoup) -> str:
        """Detect the type of page (blog, landing, e-commerce, etc.)."""
        # Check for common page type indicators
        if soup.find('article') or soup.find('.post-content') or soup.find('.entry-content'):
            return 'blog'
        elif soup.find('.product') or soup.find('.price') or soup.find('.add-to-cart'):
            return 'e-commerce'
        elif soup.find('form', action=re.compile(r'contact|subscribe')):
            return 'landing'
        elif soup.find('.portfolio') or soup.find('.gallery'):
            return 'portfolio'
        elif soup.find('nav', class_=re.compile(r'main|primary')):
            return 'website'
        else:
            return 'unknown'
    
    def _analyze_content_stats(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Analyze content statistics."""
        text_content = soup.get_text()
        
        return {
            'total_text_length': len(text_content),
            'word_count': len(text_content.split()),
            'paragraph_count': len(soup.find_all('p')),
            'heading_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'link_count': len(soup.find_all('a')),
            'image_count': len(soup.find_all('img')),
            'form_count': len(soup.find_all('form'))
        }
    
    def _analyze_structure_complexity(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze HTML structure complexity."""
        def get_max_depth(element, current_depth=0):
            if not hasattr(element, 'children'):
                return current_depth
            
            max_child_depth = current_depth
            for child in element.children:
                if hasattr(child, 'name') and child.name:
                    child_depth = get_max_depth(child, current_depth + 1)
                    max_child_depth = max(max_child_depth, child_depth)
            
            return max_child_depth
        
        body = soup.find('body')
        max_depth = get_max_depth(body) if body else 0
        
        return {
            'max_nesting_depth': max_depth,
            'total_elements': len(soup.find_all()),
            'div_count': len(soup.find_all('div')),
            'semantic_elements': len(soup.find_all(['article', 'section', 'header', 'footer', 'main', 'nav', 'aside']))
        }
    
    def _analyze_seo(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Basic SEO analysis."""
        h1_tags = soup.find_all('h1')
        meta_description = self._get_meta_content(soup, 'description')
        
        return {
            'has_meta_description': bool(meta_description),
            'meta_description_length': len(meta_description) if meta_description else 0,
            'h1_count': len(h1_tags),
            'has_multiple_h1': len(h1_tags) > 1,
            'has_alt_attributes': len([img for img in soup.find_all('img') if img.get('alt')]) > 0
        }
    
    def _analyze_accessibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Basic accessibility analysis."""
        images = soup.find_all('img')
        images_with_alt = [img for img in images if img.get('alt')]
        
        return {
            'images_with_alt_ratio': len(images_with_alt) / len(images) if images else 1.0,
            'has_skip_links': bool(soup.find('a', href='#main-content') or soup.find('a', href='#content')),
            'has_lang_attribute': bool(soup.html and soup.html.get('lang')),
            'heading_structure_valid': self._check_heading_structure(soup)
        }
    
    def _check_heading_structure(self, soup: BeautifulSoup) -> bool:
        """Check if heading structure follows proper hierarchy."""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if not headings:
            return True
        
        previous_level = 0
        for heading in headings:
            current_level = int(heading.name[1])
            if current_level > previous_level + 1:
                return False
            previous_level = current_level
        
        return True
    
    def _filter_sections(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Filter manifest to only include requested sections."""
        if not self.sections or self.sections == ['metadata', 'styles', 'structure', 'imports', 'analysis']:
            return manifest
        
        filtered = {}
        for section in self.sections:
            if section in manifest:
                filtered[section] = manifest[section]
        
        return filtered
    
    def _apply_simplification(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Apply structure simplification based on settings."""
        if 'structure' not in manifest:
            return manifest
        
        simplified_manifest = manifest.copy()
        structure = manifest['structure']
        
        # Apply max depth limitation
        if self.max_depth:
            structure = self._limit_depth(structure, self.max_depth)
        
        # Apply container flattening
        if self.flatten_containers:
            structure = self._flatten_container_elements(structure)
        
        # Apply general simplification
        if self.simplify_structure:
            structure = self._apply_general_simplification(structure)
        
        simplified_manifest['structure'] = structure
        return simplified_manifest
    
    def _limit_depth(self, structure: Any, max_depth: int, current_depth: int = 0) -> Any:
        """Limit structure nesting to maximum depth."""
        if current_depth >= max_depth:
            if isinstance(structure, dict) and len(structure) == 1:
                # If single element at max depth, extract its text content
                key, value = next(iter(structure.items()))
                if isinstance(value, dict) and 'text' in value:
                    return {key: {'text': value['text']}}
                elif isinstance(value, str):
                    return {key: {'text': value}}
            return {}
        
        if isinstance(structure, dict):
            limited = {}
            for key, value in structure.items():
                if key == 'children':
                    limited_children = self._limit_depth(value, max_depth, current_depth + 1)
                    if limited_children:
                        limited[key] = limited_children
                else:
                    limited[key] = value
            return limited
        elif isinstance(structure, list):
            return [self._limit_depth(item, max_depth, current_depth) for item in structure if self._limit_depth(item, max_depth, current_depth)]
        else:
            return structure
    
    def _flatten_container_elements(self, structure: Any) -> Any:
        """Flatten unnecessary container divs and wrappers."""
        if isinstance(structure, dict):
            flattened = {}
            for key, value in structure.items():
                if key == 'div' and isinstance(value, dict):
                    # Check if this div is just a wrapper
                    if self._is_wrapper_div(value):
                        # Extract children and flatten
                        children = value.get('children', [])
                        if isinstance(children, list) and len(children) == 1:
                            return self._flatten_container_elements(children[0])
                        elif isinstance(children, dict):
                            return self._flatten_container_elements(children)
                
                flattened_value = self._flatten_container_elements(value)
                flattened[key] = flattened_value
            return flattened
        elif isinstance(structure, list):
            return [self._flatten_container_elements(item) for item in structure]
        else:
            return structure
    
    def _is_wrapper_div(self, div_content: Dict[str, Any]) -> bool:
        """Check if a div is just a wrapper with minimal semantic value."""
        # A wrapper div typically has:
        # - Only class/id attributes for styling
        # - Single child or children with no direct text content
        # - CSS classes that suggest layout/wrapper purpose
        
        wrapper_classes = ['wrapper', 'container', 'inner', 'content-wrapper', 'entry-wrapper', 'post-wrapper']
        
        if 'class' in div_content:
            class_value = div_content['class'].lower()
            if any(wrapper_class in class_value for wrapper_class in wrapper_classes):
                return True
        
        # Check if div has only structural attributes and children
        non_structural_keys = set(div_content.keys()) - {'class', 'id', 'children'}
        if len(non_structural_keys) == 0 and 'children' in div_content:
            return True
        
        return False
    
    def _apply_general_simplification(self, structure: Any) -> Any:
        """Apply general structure simplification rules."""
        if isinstance(structure, dict):
            simplified = {}
            for key, value in structure.items():
                # Skip empty elements
                if not value:
                    continue
                
                # Preserve semantic HTML5 tags if requested
                if self.preserve_semantic_tags and key in ['article', 'section', 'header', 'footer', 'main', 'nav', 'aside']:
                    simplified[key] = self._apply_general_simplification(value)
                # Simplify nested structure
                elif isinstance(value, dict):
                    simplified_value = self._apply_general_simplification(value)
                    if simplified_value:
                        simplified[key] = simplified_value
                else:
                    simplified[key] = value
            
            return simplified
        elif isinstance(structure, list):
            return [self._apply_general_simplification(item) for item in structure if item]
        else:
            return structure
