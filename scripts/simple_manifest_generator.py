#!/usr/bin/env python3
"""
Simple Manifest Generator - Fallback for when beautifulsoup4 is not available

Creates basic YAML manifests from HTML content using simple regex parsing
instead of full DOM parsing. This allows batch processing to continue
even without beautifulsoup4 dependency.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
import yaml
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse


class SimpleManifestGenerator:
    """
    Simple HTML to YAML manifest generator using regex parsing.
    
    This is a fallback solution when beautifulsoup4 is not available.
    It creates basic but functional manifests for conversion purposes.
    """
    
    def __init__(self):
        self.url = None
        self.domain = None
        
    def generate_manifest_from_html(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Generate a basic YAML manifest from HTML content.
        
        Args:
            html_content: Raw HTML string
            url: Source URL for the content
            
        Returns:
            Dictionary representing the YAML manifest
        """
        self.url = url
        parsed_url = urlparse(url)
        self.domain = parsed_url.netloc
        
        manifest = {
            'metadata': self._extract_metadata(html_content),
            'styles': self._extract_styles(html_content),
            'structure': self._extract_structure(html_content),
            'imports': self._extract_imports(html_content),
            'analysis': self._generate_analysis(html_content)
        }
        
        return manifest
    
    def _extract_metadata(self, html: str) -> Dict[str, Any]:
        """Extract basic metadata from HTML."""
        metadata = {
            'title': self._extract_title(html),
            'description': self._extract_meta_content(html, 'description'),
            'keywords': self._extract_meta_content(html, 'keywords'),
            'author': self._extract_meta_content(html, 'author'),
            'charset': self._extract_charset(html),
            'viewport': self._extract_meta_content(html, 'viewport'),
            'source_url': self.url,
            'domain': self.domain,
            'generator': 'WhyML Simple Manifest Generator'
        }
        
        # Clean up None values
        return {k: v for k, v in metadata.items() if v is not None}
    
    def _extract_title(self, html: str) -> Optional[str]:
        """Extract page title."""
        match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if match:
            return self._clean_text(match.group(1))
        return None
    
    def _extract_meta_content(self, html: str, name: str) -> Optional[str]:
        """Extract meta tag content by name."""
        patterns = [
            rf'<meta\s+name=["\']?{name}["\']?\s+content=["\']([^"\']*)["\']',
            rf'<meta\s+content=["\']([^"\']*)["\']?\s+name=["\']?{name}["\']'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))
        return None
    
    def _extract_charset(self, html: str) -> Optional[str]:
        """Extract charset information."""
        patterns = [
            r'<meta\s+charset=["\']?([^"\'>\s]*)',
            r'<meta\s+http-equiv=["\']?content-type["\']?\s+content=["\'][^;]*;\s*charset=([^"\']*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return 'utf-8'  # Default
    
    def _extract_styles(self, html: str) -> Dict[str, Any]:
        """Extract basic CSS styles in converter-compatible format."""
        styles = {}
        
        # Extract inline styles
        style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.IGNORECASE | re.DOTALL)
        if style_blocks:
            combined_css = '\n'.join(style_blocks)
            cleaned_css = self._clean_css(combined_css)
            
            # Convert to converter-compatible format
            # Instead of {inline: 'css'}, create individual selectors
            if cleaned_css:
                # Create a simplified structure that converters can handle
                styles['global'] = cleaned_css  # Single string for all CSS
                
                # Also try to extract some basic selectors for better compatibility
                basic_selectors = self._extract_basic_selectors(cleaned_css)
                styles.update(basic_selectors)
        
        # Extract external stylesheets
        link_matches = re.findall(r'<link[^>]+rel=["\']?stylesheet["\']?[^>]+href=["\']([^"\']*)["\']', html, re.IGNORECASE)
        if link_matches:
            # Convert list of URLs to semicolon-separated string for converter compatibility
            external_urls = [urljoin(self.url, link) for link in link_matches]
            styles['external'] = '; '.join(external_urls)
        
        return styles
    
    def _extract_basic_selectors(self, css: str) -> Dict[str, str]:
        """Extract basic CSS selectors from CSS string."""
        selectors = {}
        
        # Try to extract simple CSS rules
        # This is a basic implementation that works with common patterns
        css_rules = re.findall(r'([^{]+)\{([^}]+)\}', css, re.DOTALL)
        
        for selector, rules in css_rules[:10]:  # Limit to first 10 rules to avoid overwhelming
            # Clean selector and rules
            selector = selector.strip()
            rules = rules.strip()
            
            if selector and rules and len(selector) < 100:  # Skip overly complex selectors
                # Create a safe key name
                safe_key = re.sub(r'[^a-zA-Z0-9_-]', '_', selector)[:50]
                if safe_key and not safe_key.startswith('_'):
                    selectors[safe_key] = rules
        
        return selectors
    
    def _extract_structure(self, html: str) -> Dict[str, Any]:
        """Extract basic page structure."""
        structure = {
            'type': 'container',
            'tag': 'div',
            'class': 'page-container',
            'children': []
        }
        
        # Extract main content areas
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.IGNORECASE | re.DOTALL)
        if body_match:
            body_content = body_match.group(1)
            structure['children'] = self._parse_basic_elements(body_content)
        
        return structure
    
    def _parse_basic_elements(self, content: str) -> List[Dict[str, Any]]:
        """Parse basic HTML elements."""
        elements = []
        
        # Extract headings
        for level in range(1, 7):
            headings = re.findall(rf'<h{level}[^>]*>(.*?)</h{level}>', content, re.IGNORECASE | re.DOTALL)
            for heading in headings:
                elements.append({
                    'type': 'heading',
                    'tag': f'h{level}',
                    'text': self._clean_text(heading),
                    'level': level
                })
        
        # Extract paragraphs
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
        for para in paragraphs:
            text = self._clean_text(para)
            if text and len(text.strip()) > 0:
                elements.append({
                    'type': 'paragraph',
                    'tag': 'p',
                    'text': text
                })
        
        # Extract images
        images = re.findall(r'<img[^>]+src=["\']([^"\']*)["\'][^>]*(?:alt=["\']([^"\']*)["\'])?', content, re.IGNORECASE)
        for img_src, img_alt in images:
            elements.append({
                'type': 'image',
                'tag': 'img',
                'src': urljoin(self.url, img_src),
                'alt': img_alt or ''
            })
        
        # Extract links
        links = re.findall(r'<a[^>]+href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', content, re.IGNORECASE | re.DOTALL)
        for link_href, link_text in links:
            elements.append({
                'type': 'link',
                'tag': 'a',
                'href': urljoin(self.url, link_href),
                'text': self._clean_text(link_text)
            })
        
        return elements
    
    def _extract_imports(self, html: str) -> Dict[str, Any]:
        """Extract JavaScript and other imports."""
        imports = {}
        
        # Extract script tags
        script_matches = re.findall(r'<script[^>]+src=["\']([^"\']*)["\']', html, re.IGNORECASE)
        if script_matches:
            imports['scripts'] = [urljoin(self.url, script) for script in script_matches]
        
        # Extract inline scripts - combine into single string for compatibility
        inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.IGNORECASE | re.DOTALL)
        if inline_scripts:
            # Clean and combine scripts, avoiding very long content that causes converter issues
            cleaned_scripts = []
            for script in inline_scripts:
                script = script.strip()
                if script and len(script) < 10000:  # Limit script length to avoid converter issues
                    cleaned_scripts.append(script)
            
            if cleaned_scripts:
                # Convert to single string instead of list for converter compatibility
                imports['inline_scripts'] = '\n\n'.join(cleaned_scripts)
        
        return imports
    
    def _generate_analysis(self, html: str) -> Dict[str, Any]:
        """Generate basic analysis of the page."""
        analysis = {
            'page_type': self._detect_page_type(html),
            'content_stats': self._calculate_content_stats(html),
            'seo_analysis': self._basic_seo_analysis(html),
            'generated_by': 'SimpleManifestGenerator',
            'parsing_method': 'regex'
        }
        
        return analysis
    
    def _detect_page_type(self, html: str) -> str:
        """Detect basic page type."""
        html_lower = html.lower()
        
        if any(word in html_lower for word in ['blog', 'article', 'post']):
            return 'blog'
        elif any(word in html_lower for word in ['shop', 'cart', 'buy', 'product', 'price', '$']):
            return 'e-commerce'
        elif any(word in html_lower for word in ['portfolio', 'gallery', 'work', 'projects']):
            return 'portfolio'
        elif any(word in html_lower for word in ['contact', 'about', 'company', 'business']):
            return 'corporate'
        else:
            return 'general'
    
    def _calculate_content_stats(self, html: str) -> Dict[str, int]:
        """Calculate basic content statistics."""
        stats = {}
        
        # Count elements
        stats['headings'] = len(re.findall(r'<h[1-6][^>]*>', html, re.IGNORECASE))
        stats['paragraphs'] = len(re.findall(r'<p[^>]*>', html, re.IGNORECASE))
        stats['images'] = len(re.findall(r'<img[^>]*>', html, re.IGNORECASE))
        stats['links'] = len(re.findall(r'<a[^>]*>', html, re.IGNORECASE))
        
        # Word count (rough estimate)
        text_content = re.sub(r'<[^>]+>', ' ', html)
        words = text_content.split()
        stats['word_count'] = len([word for word in words if len(word) > 2])
        
        return stats
    
    def _basic_seo_analysis(self, html: str) -> Dict[str, Any]:
        """Basic SEO analysis."""
        seo = {}
        
        # Check for essential meta tags
        seo['has_title'] = bool(re.search(r'<title[^>]*>', html, re.IGNORECASE))
        seo['has_description'] = bool(re.search(r'<meta[^>]+name=["\']?description["\']?', html, re.IGNORECASE))
        seo['has_keywords'] = bool(re.search(r'<meta[^>]+name=["\']?keywords["\']?', html, re.IGNORECASE))
        seo['has_h1'] = bool(re.search(r'<h1[^>]*>', html, re.IGNORECASE))
        
        return seo
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ''
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _clean_css(self, css: str) -> str:
        """Clean and normalize CSS content."""
        if not css:
            return ''
        
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        # Normalize whitespace
        css = re.sub(r'\s+', ' ', css)
        # Strip leading/trailing whitespace
        css = css.strip()
        
        return css


def generate_simple_manifest(html_content: str, url: str) -> str:
    """
    Convenience function to generate a YAML manifest from HTML.
    
    Args:
        html_content: Raw HTML string
        url: Source URL
        
    Returns:
        YAML manifest as string
    """
    generator = SimpleManifestGenerator()
    manifest_dict = generator.generate_manifest_from_html(html_content, url)
    
    return yaml.dump(manifest_dict, default_flow_style=False, allow_unicode=True, indent=2)


if __name__ == '__main__':
    # Test with a simple HTML example
    test_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="This is a test page">
        <style>body { font-family: Arial; }</style>
    </head>
    <body>
        <h1>Welcome</h1>
        <p>This is a test paragraph.</p>
        <img src="test.jpg" alt="Test image">
        <a href="/about">About Us</a>
    </body>
    </html>
    '''
    
    result = generate_simple_manifest(test_html, 'https://example.com')
    print(result)
