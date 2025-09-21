"""
WhyML Scrapers - Webpage Analyzer Module

Comprehensive webpage analysis including content statistics, SEO analysis,
accessibility assessment, and page type detection.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Tag

from whyml_core.utils import StringUtils


class WebpageAnalyzer:
    """Comprehensive webpage analyzer for content and structure assessment."""
    
    def __init__(self):
        """Initialize webpage analyzer."""
        pass
    
    async def analyze_page(self, url: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Perform comprehensive page analysis.
        
        Args:
            url: Source URL
            soup: Parsed HTML
            
        Returns:
            Complete analysis results
        """
        analysis = {
            'page_type': self._detect_page_type(soup),
            'content_stats': self._analyze_content_statistics(soup),
            'seo_analysis': self._analyze_seo(soup),
            'accessibility': self._analyze_accessibility(soup),
            'structure_complexity': self._analyze_structure_complexity(soup),
            'performance_hints': self._analyze_performance(soup)
        }
        
        return analysis
    
    def _detect_page_type(self, soup: BeautifulSoup) -> str:
        """Detect page type based on content patterns."""
        # Blog detection
        if (soup.find('article') or 
            soup.find(class_=re.compile(r'post|blog|entry', re.I)) or
            soup.find('time', attrs={'datetime': True})):
            return 'blog'
        
        # E-commerce detection  
        if (soup.find(class_=re.compile(r'product|price|cart|buy|shop', re.I)) or
            soup.find('button', text=re.compile(r'add to cart|buy now', re.I))):
            return 'e-commerce'
        
        # Landing page detection
        if (soup.find('form', action=re.compile(r'contact|subscribe|signup', re.I)) or
            soup.find(class_=re.compile(r'hero|cta|landing', re.I))):
            return 'landing'
        
        # Portfolio detection
        if (soup.find(class_=re.compile(r'portfolio|gallery|work', re.I)) or
            len(soup.find_all('img')) > 10):
            return 'portfolio'
        
        # Corporate website
        if soup.find('nav', class_=re.compile(r'main|primary|navigation', re.I)):
            return 'website'
        
        return 'unknown'
    
    def _analyze_content_statistics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze content statistics."""
        text_content = soup.get_text()
        
        stats = {
            'word_count': StringUtils.count_words(text_content),
            'character_count': len(text_content),
            'paragraph_count': len(soup.find_all('p')),
            'heading_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'link_count': len(soup.find_all('a', href=True)),
            'image_count': len(soup.find_all('img')),
            'list_count': len(soup.find_all(['ul', 'ol'])),
            'table_count': len(soup.find_all('table')),
            'form_count': len(soup.find_all('form')),
            'reading_time': StringUtils.calculate_reading_time(text_content)
        }
        
        return stats
    
    def _analyze_seo(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze SEO factors."""
        seo = {
            'title_length': 0,
            'meta_description_length': 0,
            'has_h1': False,
            'h1_count': 0,
            'heading_structure': {},
            'alt_text_coverage': 0.0,
            'internal_links': 0,
            'external_links': 0,
            'canonical_url': None,
            'meta_robots': None,
            'structured_data': []
        }
        
        # Title analysis
        title_tag = soup.find('title')
        if title_tag:
            seo['title_length'] = len(title_tag.get_text().strip())
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            seo['meta_description_length'] = len(meta_desc['content'])
        
        # Heading analysis
        h1_tags = soup.find_all('h1')
        seo['has_h1'] = len(h1_tags) > 0
        seo['h1_count'] = len(h1_tags)
        
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            seo['heading_structure'][f'h{i}'] = len(headings)
        
        # Image alt text coverage
        images = soup.find_all('img')
        if images:
            images_with_alt = len([img for img in images if img.get('alt')])
            seo['alt_text_coverage'] = images_with_alt / len(images)
        
        # Link analysis
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if href.startswith(('http://', 'https://')):
                seo['external_links'] += 1
            else:
                seo['internal_links'] += 1
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            seo['canonical_url'] = canonical['href']
        
        # Meta robots
        meta_robots = soup.find('meta', attrs={'name': 'robots'})
        if meta_robots and meta_robots.get('content'):
            seo['meta_robots'] = meta_robots['content']
        
        return seo
    
    def _analyze_accessibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze accessibility factors."""
        accessibility = {
            'has_lang_attribute': False,
            'images_with_alt': 0,
            'images_without_alt': 0,
            'form_labels': 0,
            'form_inputs': 0,
            'heading_hierarchy_issues': [],
            'aria_labels': len(soup.find_all(attrs={'aria-label': True})),
            'skip_links': len(soup.find_all('a', href=re.compile(r'#.*skip|#main', re.I)))
        }
        
        # Language attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            accessibility['has_lang_attribute'] = True
        
        # Image alt text
        images = soup.find_all('img')
        for img in images:
            if img.get('alt') is not None:
                accessibility['images_with_alt'] += 1
            else:
                accessibility['images_without_alt'] += 1
        
        # Form accessibility
        inputs = soup.find_all(['input', 'textarea', 'select'])
        labels = soup.find_all('label')
        accessibility['form_inputs'] = len(inputs)
        accessibility['form_labels'] = len(labels)
        
        return accessibility
    
    def _analyze_structure_complexity(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze structure complexity metrics."""
        complexity = {
            'max_depth': 0,
            'total_elements': 0,
            'div_count': 0,
            'semantic_elements': 0,
            'nested_tables': 0
        }
        
        # Calculate max depth
        def calculate_depth(element, current_depth=0):
            max_child_depth = current_depth
            for child in element.children:
                if hasattr(child, 'children'):
                    child_depth = calculate_depth(child, current_depth + 1)
                    max_child_depth = max(max_child_depth, child_depth)
            return max_child_depth
        
        body = soup.find('body') or soup
        complexity['max_depth'] = calculate_depth(body)
        
        # Element counts
        complexity['total_elements'] = len(soup.find_all())
        complexity['div_count'] = len(soup.find_all('div'))
        
        # Semantic elements
        semantic_tags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
        complexity['semantic_elements'] = len(soup.find_all(semantic_tags))
        
        # Nested tables
        tables = soup.find_all('table')
        complexity['nested_tables'] = sum(1 for table in tables if table.find('table'))
        
        return complexity
    
    def _analyze_performance(self, soup: BeautifulSoup) -> List[str]:
        """Generate performance optimization hints."""
        hints = []
        
        # Image optimization
        images = soup.find_all('img')
        large_images = [img for img in images if not img.get('loading')]
        if large_images:
            hints.append(f"Consider lazy loading for {len(large_images)} images")
        
        # CSS optimization
        stylesheets = soup.find_all('link', rel='stylesheet')
        if len(stylesheets) > 5:
            hints.append(f"Consider combining {len(stylesheets)} CSS files")
        
        # JavaScript optimization
        scripts = soup.find_all('script', src=True)
        if len(scripts) > 10:
            hints.append(f"Consider optimizing {len(scripts)} script files")
        
        # Inline styles
        inline_styles = soup.find_all(attrs={'style': True})
        if len(inline_styles) > 20:
            hints.append(f"Reduce {len(inline_styles)} inline styles")
        
        return hints
