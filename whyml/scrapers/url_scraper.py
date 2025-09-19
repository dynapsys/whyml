"""
URL Scraper - Extract content and structure from web pages

Intelligent web scraping with content extraction, structure analysis,
and automatic YAML manifest generation from websites.

Copyright 2024 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
import asyncio
import aiohttp
from typing import Any, Dict, List, Optional, Union, Set
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup, Tag, NavigableString
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
                 extract_scripts: bool = False):
        """
        Initialize URL scraper.
        
        Args:
            user_agent: User agent for requests
            timeout: Request timeout in seconds
            max_redirects: Maximum redirects to follow
            extract_styles: Whether to extract CSS styles
            extract_scripts: Whether to extract JavaScript
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.extract_styles = extract_styles
        self.extract_scripts = extract_scripts
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
            
            # Build manifest
            manifest = {
                'metadata': metadata,
                'styles': styles,
                'structure': structure,
                'imports': imports
            }
            
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
                if attr == 'class' and isinstance(value, list):
                    attributes[attr] = ' '.join(value)
                else:
                    attributes[attr] = value
        
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
