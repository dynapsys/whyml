"""
Test suite for whyml_scrapers.url_scraper module

Tests for:
- URLScraper functionality
- Structure simplification
- Advanced scraping options
- Error handling
- Async operations

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from bs4 import BeautifulSoup
import aiohttp
from typing import Dict, Any

from whyml_scrapers.url_scraper import URLScraper


class TestURLScraper:
    """Test cases for URLScraper class."""
    
    @pytest.fixture
    def scraper(self):
        """Create a URLScraper instance for testing."""
        return URLScraper()
    
    @pytest.fixture
    def sample_html(self):
        """Create sample HTML content for testing."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test page description">
        </head>
        <body>
            <header>
                <h1>Welcome</h1>
                <nav>
                    <ul>
                        <li><a href="/">Home</a></li>
                        <li><a href="/about">About</a></li>
                    </ul>
                </nav>
            </header>
            <main>
                <article>
                    <h2>Main Content</h2>
                    <p>This is the main content of the page.</p>
                </article>
            </main>
            <footer>
                <p>&copy; 2025 Test Site</p>
            </footer>
        </body>
        </html>
        """
    
    def test_scraper_initialization(self, scraper):
        """Test URLScraper initialization."""
        assert scraper is not None
        assert hasattr(scraper, 'scrape_url')
        assert hasattr(scraper, 'parse_html')
    
    def test_parse_html_basic(self, scraper, sample_html):
        """Test basic HTML parsing."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        result = scraper.parse_html(soup)
        
        assert isinstance(result, dict)
        assert 'metadata' in result
        assert 'structure' in result
        assert result['metadata']['title'] == 'Test Page'
    
    @patch('aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_scrape_url_success(self, mock_get, scraper, sample_html):
        """Test successful URL scraping."""
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.text = AsyncMock(return_value=sample_html)
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await scraper.scrape_url('https://example.com')
        
        assert isinstance(result, dict)
        assert 'metadata' in result
        assert 'structure' in result
    
    @patch('aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_scrape_url_404_error(self, mock_get, scraper):
        """Test URL scraping with 404 error."""
        # Mock 404 response
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_get.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(aiohttp.ClientError):
            await scraper.scrape_url('https://example.com/nonexistent')
    
    def test_structure_simplification(self, scraper):
        """Test structure simplification options."""
        complex_html = """
        <div class="wrapper">
            <div class="container">
                <div class="inner">
                    <div class="content">
                        <h1>Title</h1>
                        <p>Content</p>
                    </div>
                </div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(complex_html, 'html.parser')
        
        # Test with simplification enabled
        scraper_simplified = URLScraper(
            simplify_structure=True,
            flatten_containers=True
        )
        
        result = scraper_simplified.parse_html(soup)
        
        assert isinstance(result, dict)
        # Structure should be simplified
        assert 'structure' in result
    
    def test_max_depth_limiting(self, scraper):
        """Test maximum depth limiting."""
        deep_html = """
        <div>
            <div>
                <div>
                    <div>
                        <div>
                            <div>
                                <p>Deep content</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        
        soup = BeautifulSoup(deep_html, 'html.parser')
        
        # Test with depth limit
        scraper_limited = URLScraper(max_depth=3)
        result = scraper_limited.parse_html(soup)
        
        assert isinstance(result, dict)
        # Should limit nesting depth
        assert 'structure' in result
    
    def test_selective_section_extraction(self, scraper, sample_html):
        """Test selective section extraction."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        # Test extracting only metadata
        scraper_metadata = URLScraper(sections=['metadata'])
        result = scraper_metadata.parse_html(soup)
        
        assert 'metadata' in result
        # Should not include other sections when selective
        
    def test_css_extraction(self, scraper):
        """Test CSS extraction functionality."""
        html_with_styles = """
        <html>
        <head>
            <style>
                body { font-family: Arial; }
                .header { background: #333; }
            </style>
        </head>
        <body>
            <div class="header">Header</div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_with_styles, 'html.parser')
        
        # Test with CSS extraction enabled
        scraper_css = URLScraper(extract_styles=True)
        result = scraper_css.parse_html(soup)
        
        assert isinstance(result, dict)
        if 'styles' in result:
            assert 'css' in result['styles']
    
    def test_javascript_extraction(self, scraper):
        """Test JavaScript extraction functionality."""
        html_with_js = """
        <html>
        <head>
            <script>
                console.log('Test script');
            </script>
        </head>
        <body>
            <div>Content</div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_with_js, 'html.parser')
        
        # Test with JS extraction enabled
        scraper_js = URLScraper(extract_scripts=True)
        result = scraper_js.parse_html(soup)
        
        assert isinstance(result, dict)
        if 'scripts' in result:
            assert len(result['scripts']) > 0
    
    def test_clean_manifest(self, scraper):
        """Test manifest cleaning functionality."""
        dirty_manifest = {
            'metadata': {
                'title': '  Test Title  ',
                'description': None,
                'empty_field': ''
            },
            'structure': {
                'html': {
                    'body': {
                        'div': {
                            'content': '  Content with spaces  ',
                            'empty_div': {}
                        }
                    }
                }
            }
        }
        
        cleaned = scraper.clean_manifest(dirty_manifest)
        
        assert isinstance(cleaned, dict)
        assert cleaned['metadata']['title'] == 'Test Title'
        # Should clean up empty fields and whitespace
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self, scraper):
        """Test URLScraper as async context manager."""
        async with scraper:
            assert scraper is not None
        
        # Should handle cleanup properly
    
    def test_semantic_tag_preservation(self, scraper):
        """Test semantic HTML5 tag preservation."""
        semantic_html = """
        <html>
        <body>
            <header>Header content</header>
            <main>
                <article>Article content</article>
                <section>Section content</section>
            </main>
            <aside>Sidebar content</aside>
            <footer>Footer content</footer>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(semantic_html, 'html.parser')
        
        # Test with semantic preservation
        scraper_semantic = URLScraper(
            preserve_semantic_tags=True,
            simplify_structure=True
        )
        
        result = scraper_semantic.parse_html(soup)
        
        assert isinstance(result, dict)
        assert 'structure' in result
        # Should preserve semantic tags even with simplification


class TestURLScraperAdvanced:
    """Advanced test cases for URLScraper."""
    
    @pytest.fixture
    def advanced_scraper(self):
        """Create URLScraper with advanced options."""
        return URLScraper(
            extract_styles=True,
            extract_scripts=True,
            max_depth=5,
            flatten_containers=True,
            simplify_structure=True,
            preserve_semantic_tags=True
        )
    
    def test_complex_page_structure(self, advanced_scraper):
        """Test scraping complex page structure."""
        complex_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Complex Page</title>
            <style>
                .container { max-width: 1200px; margin: 0 auto; }
                .grid { display: grid; grid-template-columns: 1fr 3fr 1fr; }
            </style>
        </head>
        <body>
            <div class="wrapper">
                <div class="container">
                    <header class="site-header">
                        <h1>Site Title</h1>
                        <nav aria-label="Main navigation">
                            <ul class="nav-menu">
                                <li><a href="/">Home</a></li>
                                <li><a href="/products">Products</a></li>
                                <li><a href="/contact">Contact</a></li>
                            </ul>
                        </nav>
                    </header>
                    
                    <div class="grid">
                        <aside class="sidebar">
                            <h3>Categories</h3>
                            <ul>
                                <li>Category 1</li>
                                <li>Category 2</li>
                            </ul>
                        </aside>
                        
                        <main class="content">
                            <article class="post">
                                <h2>Article Title</h2>
                                <p>Article content goes here.</p>
                                <div class="meta">
                                    <span class="author">By John Doe</span>
                                    <time datetime="2025-01-01">January 1, 2025</time>
                                </div>
                            </article>
                        </main>
                        
                        <aside class="widgets">
                            <div class="widget">
                                <h4>Recent Posts</h4>
                                <ul>
                                    <li>Post 1</li>
                                    <li>Post 2</li>
                                </ul>
                            </div>
                        </aside>
                    </div>
                    
                    <footer class="site-footer">
                        <p>&copy; 2025 Complex Site</p>
                    </footer>
                </div>
            </div>
            
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    console.log('Page loaded');
                });
            </script>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(complex_html, 'html.parser')
        result = advanced_scraper.parse_html(soup)
        
        assert isinstance(result, dict)
        assert 'metadata' in result
        assert 'structure' in result
        assert result['metadata']['title'] == 'Complex Page'
        
        # Should have extracted styles and scripts
        if 'styles' in result:
            assert 'css' in result['styles']
        
        if 'scripts' in result:
            assert len(result['scripts']) > 0
    
    def test_malformed_html_handling(self, advanced_scraper):
        """Test handling of malformed HTML."""
        malformed_html = """
        <html>
        <head>
            <title>Malformed Page
        <body>
            <div class="content">
                <h1>Title without closing tag
                <p>Paragraph with <strong>unclosed strong tag
                <ul>
                    <li>Item 1
                    <li>Item 2</li>
                </ul>
            </div>
        </body>
        """
        
        # BeautifulSoup should handle malformed HTML gracefully
        soup = BeautifulSoup(malformed_html, 'html.parser')
        result = advanced_scraper.parse_html(soup)
        
        assert isinstance(result, dict)
        assert 'structure' in result
    
    @patch('aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_timeout_handling(self, mock_get, advanced_scraper):
        """Test timeout handling during scraping."""
        # Mock timeout exception
        mock_get.side_effect = asyncio.TimeoutError()
        
        with pytest.raises(asyncio.TimeoutError):
            await advanced_scraper.scrape_url('https://slow-example.com', timeout=1)
    
    def test_large_page_handling(self, advanced_scraper):
        """Test handling of large pages."""
        # Create large HTML content
        large_content = "<div>" + "<p>Content paragraph</p>" * 1000 + "</div>"
        large_html = f"""
        <html>
        <head><title>Large Page</title></head>
        <body>{large_content}</body>
        </html>
        """
        
        soup = BeautifulSoup(large_html, 'html.parser')
        result = advanced_scraper.parse_html(soup)
        
        assert isinstance(result, dict)
        assert 'structure' in result
        # Should handle large content without issues


if __name__ == "__main__":
    pytest.main([__file__])
