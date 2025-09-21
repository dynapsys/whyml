"""
WhyML Scrapers - URL Scraper Module

Advanced web scraping with structure analysis, content extraction,
and manifest generation using WhyML Core functionality.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import asyncio
import re
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag, NavigableString
import aiohttp

# WhyML Core imports
from whyml_core.exceptions import NetworkError, ProcessingError, ValidationError
from whyml_core.utils import AsyncHTTPManager, StringUtils, PathUtils
from whyml_core.loading import ManifestLoader

from .webpage_analyzer import WebpageAnalyzer
from .content_extractor import ContentExtractor
from .structure_analyzer import StructureAnalyzer


class URLScraper:
    """Advanced URL scraper with intelligent content extraction and manifest generation."""
    
    def __init__(self, 
                 timeout: float = 30.0,
                 max_retries: int = 3,
                 user_agent: str = None):
        """Initialize URL scraper.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent or (
            "Mozilla/5.0 (compatible; WhyML-Scraper/1.0; "
            "+https://github.com/dynapsys/whyml)"
        )
        
        # Initialize analyzers
        self.webpage_analyzer = WebpageAnalyzer()
        self.content_extractor = ContentExtractor()
        self.structure_analyzer = StructureAnalyzer()
    
    async def scrape_to_manifest(self, 
                                url: str,
                                sections: Optional[List[str]] = None,
                                **scraping_options) -> Dict[str, Any]:
        """Scrape URL and generate WhyML manifest.
        
        Args:
            url: URL to scrape
            sections: Optional list of sections to include
            **scraping_options: Additional scraping options
            
        Returns:
            WhyML manifest dictionary
        """
        # Download and parse HTML
        soup = await self._fetch_and_parse(url)
        
        # Generate manifest sections
        manifest = {}
        
        # Determine sections to include
        if sections is None:
            sections = ['metadata', 'structure', 'styles', 'analysis']
        
        # Generate each requested section
        if 'metadata' in sections:
            manifest['metadata'] = await self._extract_metadata(url, soup)
        
        if 'structure' in sections:
            manifest['structure'] = await self._extract_structure(
                soup, **scraping_options
            )
        
        if 'styles' in sections:
            manifest['styles'] = await self._extract_styles(soup)
        
        if 'analysis' in sections:
            manifest['analysis'] = await self._analyze_page(url, soup)
        
        if 'imports' in sections:
            manifest['imports'] = await self._extract_imports(url, soup)
        
        return manifest
    
    async def _fetch_and_parse(self, url: str) -> BeautifulSoup:
        """Fetch URL content and parse with BeautifulSoup.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object
        """
        headers = {'User-Agent': self.user_agent}
        
        async with AsyncHTTPManager(
            timeout=self.timeout, 
            max_retries=self.max_retries
        ) as http_manager:
            try:
                html_content = await http_manager.get(url, headers=headers)
                return BeautifulSoup(html_content, 'html.parser')
            except Exception as e:
                raise NetworkError(
                    message=f"Failed to fetch and parse URL: {str(e)}",
                    details={'url': url, 'error': str(e)}
                )
    
    async def _extract_metadata(self, url: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from webpage.
        
        Args:
            url: Source URL
            soup: Parsed HTML
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'source_url': url,
            'title': self._get_page_title(soup),
            'description': self._get_meta_description(soup),
        }
        
        # Optional metadata
        keywords = self._get_meta_keywords(soup)
        if keywords:
            metadata['keywords'] = keywords
        
        author = self._get_meta_author(soup)
        if author:
            metadata['author'] = author
        
        # OpenGraph metadata
        og_data = self._extract_opengraph(soup)
        if og_data:
            metadata['opengraph'] = og_data
        
        # Twitter Card metadata  
        twitter_data = self._extract_twitter_card(soup)
        if twitter_data:
            metadata['twitter'] = twitter_data
        
        return metadata
    
    async def _extract_structure(self, 
                                soup: BeautifulSoup,
                                max_depth: Optional[int] = None,
                                flatten_containers: bool = False,
                                simplify_structure: bool = False,
                                preserve_semantic: bool = True) -> Dict[str, Any]:
        """Extract page structure.
        
        Args:
            soup: Parsed HTML
            max_depth: Maximum nesting depth
            flatten_containers: Whether to flatten wrapper containers
            simplify_structure: Whether to apply general simplification
            preserve_semantic: Whether to preserve semantic elements
            
        Returns:
            Structure dictionary
        """
        # Get main content container
        main_content = self._find_main_content(soup)
        
        if main_content is None:
            # Fallback to body
            main_content = soup.find('body') or soup
        
        # Apply structure modifications if requested
        if simplify_structure:
            main_content = self._simplify_structure(
                main_content,
                preserve_semantic=preserve_semantic
            )
        
        if flatten_containers:
            main_content = self._flatten_containers(main_content)
        
        if max_depth:
            main_content = self._limit_depth(main_content, max_depth)
        
        # Convert to structure dictionary
        return await self.structure_analyzer.analyze_structure(main_content)
    
    async def _extract_styles(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract styles from webpage.
        
        Args:
            soup: Parsed HTML
            
        Returns:
            Styles dictionary
        """
        return await self.content_extractor.extract_styles(soup)
    
    async def _analyze_page(self, url: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze webpage characteristics.
        
        Args:
            url: Source URL
            soup: Parsed HTML
            
        Returns:
            Analysis results
        """
        return await self.webpage_analyzer.analyze_page(url, soup)
    
    async def _extract_imports(self, url: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract external resources and imports.
        
        Args:
            url: Source URL
            soup: Parsed HTML
            
        Returns:
            Imports dictionary
        """
        imports = {
            'stylesheets': [],
            'scripts': [],
            'fonts': [],
            'images': []
        }
        
        base_url = self._get_base_url(url, soup)
        
        # Extract stylesheets
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                imports['stylesheets'].append({
                    'url': absolute_url,
                    'media': link.get('media', 'all'),
                    'integrity': link.get('integrity'),
                    'crossorigin': link.get('crossorigin')
                })
        
        # Extract scripts
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                absolute_url = urljoin(base_url, src)
                imports['scripts'].append({
                    'url': absolute_url,
                    'type': script.get('type', 'text/javascript'),
                    'async': script.has_attr('async'),
                    'defer': script.has_attr('defer'),
                    'integrity': script.get('integrity'),
                    'crossorigin': script.get('crossorigin')
                })
        
        # Extract font imports from CSS
        for style in soup.find_all('style'):
            css_content = style.get_text()
            font_urls = re.findall(r'@import\s+["\']([^"\']*font[^"\']*)["\']', css_content)
            for font_url in font_urls:
                absolute_url = urljoin(base_url, font_url)
                imports['fonts'].append({'url': absolute_url})
        
        # Extract images
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src and not src.startswith('data:'):
                absolute_url = urljoin(base_url, src)
                imports['images'].append({
                    'url': absolute_url,
                    'alt': img.get('alt', ''),
                    'width': img.get('width'),
                    'height': img.get('height'),
                    'loading': img.get('loading'),
                    'sizes': img.get('sizes'),
                    'srcset': img.get('srcset')
                })
        
        return imports
    
    def _get_page_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag:
            return StringUtils.clean_text(title_tag.get_text().strip())
        
        # Fallback to h1
        h1_tag = soup.find('h1')
        if h1_tag:
            return StringUtils.clean_text(h1_tag.get_text().strip())
        
        return "Untitled"
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return StringUtils.clean_text(meta_desc['content'])
        
        # Fallback to OpenGraph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return StringUtils.clean_text(og_desc['content'])
        
        return ""
    
    def _get_meta_keywords(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Extract meta keywords."""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords = [kw.strip() for kw in meta_keywords['content'].split(',')]
            return [kw for kw in keywords if kw]
        return None
    
    def _get_meta_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract meta author."""
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author and meta_author.get('content'):
            return StringUtils.clean_text(meta_author['content'])
        return None
    
    def _extract_opengraph(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract OpenGraph metadata."""
        og_data = {}
        
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            property_name = tag['property'][3:]  # Remove 'og:' prefix
            content = tag.get('content')
            if content:
                og_data[property_name] = StringUtils.clean_text(content)
        
        return og_data
    
    def _extract_twitter_card(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Twitter Card metadata."""
        twitter_data = {}
        
        twitter_tags = soup.find_all('meta', name=lambda x: x and x.startswith('twitter:'))
        for tag in twitter_tags:
            name = tag['name'][8:]  # Remove 'twitter:' prefix
            content = tag.get('content')
            if content:
                twitter_data[name] = StringUtils.clean_text(content)
        
        return twitter_data
    
    def _find_main_content(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find main content container."""
        # Try semantic HTML5 elements first
        for tag_name in ['main', 'article']:
            element = soup.find(tag_name)
            if element:
                return element
        
        # Try common content selectors
        selectors = [
            '#content', '#main', '#main-content',
            '.content', '.main', '.main-content',
            '[role="main"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element
        
        return None
    
    def _get_base_url(self, url: str, soup: BeautifulSoup) -> str:
        """Get base URL for resolving relative URLs."""
        # Check for <base> tag
        base_tag = soup.find('base', href=True)
        if base_tag:
            return base_tag['href']
        
        # Use original URL
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _simplify_structure(self, element: Tag, preserve_semantic: bool = True) -> Tag:
        """Apply general structure simplification."""
        # Remove empty elements
        for empty in element.find_all(lambda tag: (
            tag.name and 
            not tag.get_text(strip=True) and 
            not tag.find_all(['img', 'input', 'br', 'hr'])
        )):
            empty.decompose()
        
        # Remove wrapper divs
        if not preserve_semantic:
            for wrapper in element.find_all('div'):
                if self._is_wrapper_div(wrapper):
                    wrapper.unwrap()
        
        return element
    
    def _flatten_containers(self, element: Tag) -> Tag:
        """Flatten unnecessary container elements."""
        wrapper_classes = [
            'wrapper', 'container', 'inner', 'outer', 'content-wrapper',
            'main-wrapper', 'page-wrapper', 'site-wrapper'
        ]
        
        for wrapper in element.find_all('div'):
            classes = wrapper.get('class', [])
            if any(cls in wrapper_classes for cls in classes):
                # Only unwrap if it has a single child or only contains other wrappers
                children = [child for child in wrapper.children if isinstance(child, Tag)]
                if len(children) <= 1:
                    wrapper.unwrap()
        
        return element
    
    def _limit_depth(self, element: Tag, max_depth: int) -> Tag:
        """Limit nesting depth of elements."""
        def _limit_recursive(elem: Tag, current_depth: int) -> Tag:
            if current_depth >= max_depth:
                # Convert to text content
                text_content = elem.get_text(strip=True)
                if text_content:
                    elem.clear()
                    elem.string = text_content
                return elem
            
            # Process children
            for child in list(elem.children):
                if isinstance(child, Tag):
                    _limit_recursive(child, current_depth + 1)
            
            return elem
        
        return _limit_recursive(element, 0)
    
    def _is_wrapper_div(self, element: Tag) -> bool:
        """Check if element is a wrapper div with no semantic value."""
        if element.name != 'div':
            return False
        
        # Has no meaningful attributes
        attrs = element.attrs
        meaningful_attrs = {'id', 'class', 'data-*', 'role', 'aria-*'}
        
        has_meaningful_attr = any(
            attr in meaningful_attrs or attr.startswith(('data-', 'aria-'))
            for attr in attrs.keys()
        )
        
        if has_meaningful_attr:
            return False
        
        # Contains only other block elements or text
        children = [child for child in element.children if isinstance(child, Tag)]
        
        if len(children) == 1:
            # Single child - likely wrapper
            return True
        elif len(children) == 0:
            # Only text content
            return bool(element.get_text(strip=True))
        
        return False
