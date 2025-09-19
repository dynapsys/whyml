"""
Test cases for scrapers package

Tests for URL scraping, webpage analysis, and website-to-manifest conversion
functionality with mock responses and real HTML parsing.

Copyright 2024 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from bs4 import BeautifulSoup

from whyml.scrapers import URLScraper, WebpageAnalyzer
from whyml.exceptions import NetworkError, ConversionError


class TestURLScraper:
    """Test cases for URL scraper functionality."""
    
    @pytest.fixture
    def scraper(self):
        """Create URLScraper instance for testing."""
        return URLScraper(
            user_agent="WhyML-Test/1.0",
            timeout=10,
            extract_styles=True,
            extract_scripts=False
        )
    
    @pytest.fixture
    def sample_html(self):
        """Sample HTML content for testing."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="description" content="A sample webpage for testing">
            <meta name="keywords" content="test, sample, webpage">
            <meta property="og:title" content="Sample Page">
            <meta property="og:description" content="This is a sample page">
            <title>Sample Webpage</title>
            <link rel="stylesheet" href="styles.css">
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
            <style>
                .container { width: 100%; max-width: 1200px; margin: 0 auto; }
                .header { background: #007bff; color: white; padding: 20px; }
                .content { padding: 20px; line-height: 1.6; }
            </style>
        </head>
        <body>
            <div class="container">
                <header class="header">
                    <h1>Welcome to Sample Page</h1>
                    <nav>
                        <ul>
                            <li><a href="#home">Home</a></li>
                            <li><a href="#about">About</a></li>
                            <li><a href="#contact">Contact</a></li>
                        </ul>
                    </nav>
                </header>
                <main class="content">
                    <section id="about">
                        <h2>About Us</h2>
                        <p>This is a sample paragraph with some content.</p>
                        <img src="image.jpg" alt="Sample image" loading="lazy">
                    </section>
                    <section id="features">
                        <h2>Features</h2>
                        <div class="feature-grid">
                            <div class="feature-item">
                                <h3>Feature 1</h3>
                                <p>Description of feature 1</p>
                            </div>
                            <div class="feature-item">
                                <h3>Feature 2</h3>
                                <p>Description of feature 2</p>
                            </div>
                        </div>
                    </section>
                </main>
                <footer>
                    <p>&copy; 2024 Sample Company</p>
                </footer>
            </div>
            <script src="script.js"></script>
        </body>
        </html>
        """
    
    @pytest.mark.asyncio
    async def test_scraper_context_manager(self, scraper):
        """Test URLScraper as async context manager."""
        async with scraper as s:
            assert s.session is not None
        
        # Session should be closed after context exit
        assert scraper.session is None or scraper.session.closed
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_fetch_url_success(self, mock_get, scraper, sample_html):
        """Test successful URL fetching."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_response.text = AsyncMock(return_value=sample_html)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with scraper:
            html = await scraper._fetch_url('https://example.com')
        
        assert html == sample_html
        mock_get.assert_called_once_with('https://example.com')
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_fetch_url_http_error(self, mock_get, scraper):
        """Test handling of HTTP errors."""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.reason = 'Not Found'
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with scraper:
            with pytest.raises(NetworkError) as exc_info:
                await scraper._fetch_url('https://example.com/notfound')
        
        assert 'HTTP 404' in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_scrape_url_complete(self, mock_get, scraper, sample_html):
        """Test complete URL scraping workflow."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = AsyncMock(return_value=sample_html)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with scraper:
            manifest = await scraper.scrape_url('https://example.com')
        
        assert 'metadata' in manifest
        assert 'styles' in manifest
        assert 'structure' in manifest
        assert 'imports' in manifest
        
        # Check metadata extraction
        assert manifest['metadata']['title'] == 'Sample Webpage'
        assert 'A sample webpage for testing' in manifest['metadata']['description']
        assert 'source_url' in manifest['metadata']
    
    def test_extract_metadata(self, scraper, sample_html):
        """Test metadata extraction from HTML."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        metadata = scraper._extract_metadata(soup, 'https://example.com')
        
        assert metadata['title'] == 'Sample Webpage'
        assert metadata['description'] == 'A sample webpage for testing'
        assert metadata['keywords'] == 'test, sample, webpage'
        assert metadata['language'] == 'en'
        assert 'open_graph' in metadata
        assert metadata['open_graph']['title'] == 'Sample Page'
    
    def test_extract_styles(self, scraper, sample_html):
        """Test CSS styles extraction."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        styles = scraper._extract_styles(soup, 'https://example.com')
        
        assert 'container' in styles
        assert 'header' in styles
        assert 'content' in styles
        assert 'width: 100%' in styles['container']
        assert 'background: #007bff' in styles['header']
    
    def test_extract_imports(self, scraper, sample_html):
        """Test external resource imports extraction."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        imports = scraper._extract_imports(soup, 'https://example.com')
        
        assert 'styles' in imports
        assert 'fonts' in imports
        assert 'https://example.com/styles.css' in imports['styles']
        assert any('fonts.googleapis.com' in font for font in imports['fonts'])
    
    def test_extract_structure(self, scraper, sample_html):
        """Test HTML structure extraction."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        structure = scraper._extract_structure(soup)
        
        assert 'div' in structure
        assert 'class' in structure['div']
        assert 'children' in structure['div']
    
    def test_find_main_content(self, scraper, sample_html):
        """Test main content area detection."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        main_content = scraper._find_main_content(soup)
        
        assert main_content is not None
        assert main_content.name == 'main'
        assert 'content' in main_content.get('class', [])
    
    def test_convert_element_to_manifest(self, scraper, sample_html):
        """Test HTML element to manifest conversion."""
        soup = BeautifulSoup(sample_html, 'html.parser')
        header = soup.find('header')
        
        manifest = scraper._convert_element_to_manifest(header)
        
        assert 'header' in manifest
        assert 'class' in manifest['header']
        assert manifest['header']['class'] == 'header'
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_scrape_multiple_urls(self, mock_get, scraper, sample_html):
        """Test scraping multiple URLs concurrently."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = AsyncMock(return_value=sample_html)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        urls = [
            'https://example1.com',
            'https://example2.com',
            'https://example3.com'
        ]
        
        async with scraper:
            results = await scraper.scrape_multiple_urls(urls)
        
        assert len(results) == 3
        for url in urls:
            assert url in results
            assert 'metadata' in results[url]
    
    def test_clean_manifest(self, scraper):
        """Test manifest cleaning and optimization."""
        manifest = {
            'metadata': {'title': 'Test'},
            'styles': {
                'style1': 'color: red; font-size: 16px;',
                'style2': 'color: red; font-size: 16px;',  # Duplicate
                'style3': 'color: blue;'
            },
            'structure': {'div': {'text': 'content'}},
            'empty_section': {}
        }
        
        cleaned = scraper.clean_manifest(manifest)
        
        # Empty sections should be removed
        assert 'empty_section' not in cleaned
        
        # Styles should be optimized
        assert 'styles' in cleaned
        assert len(cleaned['styles']) <= len(manifest['styles'])


class TestWebpageAnalyzer:
    """Test cases for webpage analyzer functionality."""
    
    @pytest.fixture
    def analyzer(self):
        """Create WebpageAnalyzer instance for testing."""
        return WebpageAnalyzer(
            min_content_length=20,
            max_nesting_depth=8,
            analyze_accessibility=True
        )
    
    @pytest.fixture
    def blog_html(self):
        """Sample blog HTML for testing."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>My Blog Post</title>
            <meta name="description" content="A great blog post about testing">
        </head>
        <body>
            <header role="banner">
                <h1>My Blog</h1>
                <nav role="navigation">
                    <ul>
                        <li><a href="/">Home</a></li>
                        <li><a href="/about">About</a></li>
                    </ul>
                </nav>
            </header>
            <main role="main">
                <article>
                    <header>
                        <h1>Blog Post Title</h1>
                        <time datetime="2024-01-01">January 1, 2024</time>
                    </header>
                    <div class="post-content">
                        <p>This is a sample blog post with some content that is long enough to be considered substantial content for testing purposes.</p>
                        <img src="image.jpg" alt="Blog post image">
                        <p>Another paragraph with more content for the blog post.</p>
                    </div>
                </article>
            </main>
            <footer role="contentinfo">
                <p>&copy; 2024 My Blog</p>
            </footer>
        </body>
        </html>
        """
    
    @pytest.fixture
    def ecommerce_html(self):
        """Sample e-commerce HTML for testing."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Product Page</title>
        </head>
        <body class="bootstrap">
            <div class="container">
                <div class="product">
                    <h1 class="product-title">Amazing Product</h1>
                    <div class="price">$99.99</div>
                    <button class="add-to-cart btn btn-primary">Add to Cart</button>
                    <div class="product-description">
                        <p>This is an amazing product with great features.</p>
                    </div>
                </div>
                <div class="cart">
                    <h2>Shopping Cart</h2>
                    <div class="cart-items"></div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def test_analyze_webpage_blog(self, analyzer, blog_html):
        """Test webpage analysis for blog content."""
        soup = BeautifulSoup(blog_html, 'html.parser')
        analysis = analyzer.analyze_webpage(soup, 'https://blog.example.com/post')
        
        assert analysis['page_type'] == 'blog'
        assert analysis['layout_structure']['has_header'] == True
        assert analysis['layout_structure']['has_footer'] == True
        assert analysis['layout_structure']['has_navigation'] == True
        assert len(analysis['content_sections']) > 0
    
    def test_analyze_webpage_ecommerce(self, analyzer, ecommerce_html):
        """Test webpage analysis for e-commerce content."""
        soup = BeautifulSoup(ecommerce_html, 'html.parser')
        analysis = analyzer.analyze_webpage(soup, 'https://shop.example.com/product')
        
        assert analysis['page_type'] == 'ecommerce'
        assert analysis['layout_structure']['layout_type'] == 'bootstrap'
    
    def test_detect_page_type(self, analyzer, blog_html, ecommerce_html):
        """Test page type detection."""
        blog_soup = BeautifulSoup(blog_html, 'html.parser')
        blog_type = analyzer._detect_page_type(blog_soup)
        assert blog_type == 'blog'
        
        ecommerce_soup = BeautifulSoup(ecommerce_html, 'html.parser')
        ecommerce_type = analyzer._detect_page_type(ecommerce_soup)
        assert ecommerce_type == 'ecommerce'
    
    def test_analyze_layout_structure(self, analyzer, blog_html):
        """Test layout structure analysis."""
        soup = BeautifulSoup(blog_html, 'html.parser')
        layout = analyzer._analyze_layout_structure(soup)
        
        assert layout['has_header'] == True
        assert layout['has_footer'] == True
        assert layout['has_navigation'] == True
        assert layout['main_content_area'] is not None
    
    def test_detect_layout_type(self, analyzer, ecommerce_html):
        """Test layout type detection."""
        soup = BeautifulSoup(ecommerce_html, 'html.parser')
        layout_type = analyzer._detect_layout_type(soup)
        
        assert layout_type == 'bootstrap'
    
    def test_analyze_semantic_structure(self, analyzer, blog_html):
        """Test semantic HTML structure analysis."""
        soup = BeautifulSoup(blog_html, 'html.parser')
        semantic = analyzer._analyze_semantic_structure(soup)
        
        assert 'heading_structure' in semantic
        assert 'landmark_roles' in semantic
        assert 'semantic_elements' in semantic
        
        # Check heading structure
        assert semantic['heading_structure']['count_by_level']['h1'] > 0
        assert semantic['heading_structure']['total_count'] > 0
        
        # Check landmark roles
        assert semantic['landmark_roles']['banner'] > 0
        assert semantic['landmark_roles']['navigation'] > 0
        assert semantic['landmark_roles']['main'] > 0
        assert semantic['landmark_roles']['contentinfo'] > 0
    
    def test_analyze_accessibility(self, analyzer, blog_html):
        """Test accessibility analysis."""
        soup = BeautifulSoup(blog_html, 'html.parser')
        accessibility = analyzer._analyze_accessibility(soup)
        
        assert 'images_with_alt' in accessibility
        assert 'images_without_alt' in accessibility
        assert 'aria_labels' in accessibility
        assert accessibility['images_with_alt'] > 0  # Blog HTML has img with alt
    
    def test_find_navigation_elements(self, analyzer, blog_html):
        """Test navigation elements detection."""
        soup = BeautifulSoup(blog_html, 'html.parser')
        nav_info = analyzer._find_navigation_elements(soup)
        
        assert nav_info['main_nav'] is not None
        assert nav_info['main_nav']['tag'] == 'nav'
        assert nav_info['main_nav']['links_count'] > 0
    
    def test_analyze_media_elements(self, analyzer, blog_html):
        """Test media elements analysis."""
        soup = BeautifulSoup(blog_html, 'html.parser')
        media = analyzer._analyze_media_elements(soup)
        
        assert media['images']['count'] > 0
        assert media['images']['has_alt_text'] > 0
        assert media['videos']['count'] == 0  # No videos in sample
    
    def test_detect_responsive_breakpoints(self, analyzer):
        """Test responsive breakpoint detection."""
        html_with_responsive = """
        <div class="col-sm-12 col-md-6 col-lg-4">
            <div class="d-none d-md-block">Content</div>
        </div>
        """
        soup = BeautifulSoup(html_with_responsive, 'html.parser')
        breakpoints = analyzer._detect_responsive_breakpoints(soup)
        
        assert 'sm' in breakpoints
        assert 'md' in breakpoints
        assert 'lg' in breakpoints
    
    def test_detect_component_patterns(self, analyzer):
        """Test component pattern detection."""
        html_with_patterns = """
        <div class="card">Card 1</div>
        <div class="card">Card 2</div>
        <div class="card">Card 3</div>
        <div class="button">Button 1</div>
        <div class="button">Button 2</div>
        """
        soup = BeautifulSoup(html_with_patterns, 'html.parser')
        patterns = analyzer._detect_component_patterns(soup)
        
        assert len(patterns) > 0
        # Should detect repeated 'card' and 'button' patterns
        pattern_classes = [p['pattern'] for p in patterns]
        assert 'card' in pattern_classes
    
    def test_generate_optimization_suggestions(self, analyzer):
        """Test optimization suggestions generation."""
        html_with_issues = """
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>Title 1</h1>
            <h1>Title 2</h1>  <!-- Multiple h1s -->
            <img src="image.jpg">  <!-- Missing alt -->
            <div style="color: red;">Inline style</div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_with_issues, 'html.parser')
        suggestions = analyzer._generate_optimization_suggestions(soup)
        
        assert len(suggestions) > 0
        suggestion_text = ' '.join(suggestions)
        assert 'alt text' in suggestion_text or 'h1 tag' in suggestion_text
    
    def test_analyze_url_structure(self, analyzer):
        """Test URL structure analysis."""
        url = 'https://blog.example.com/posts/2024/sample-post?utm_source=social'
        analysis = analyzer._analyze_url_structure(url)
        
        assert analysis['domain'] == 'blog.example.com'
        assert analysis['is_secure'] == True
        assert analysis['has_query_params'] == True
        assert 'posts' in analysis['path_segments']
        assert '2024' in analysis['path_segments']
        assert 'sample-post' in analysis['path_segments']


class TestScrapersIntegration:
    """Integration tests for scrapers package."""
    
    @pytest.mark.asyncio
    async def test_scraper_and_analyzer_workflow(self):
        """Test complete workflow from scraping to analysis."""
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Integration Test Page</title>
            <meta name="description" content="Testing integration">
        </head>
        <body>
            <header>
                <h1>Test Page</h1>
            </header>
            <main>
                <section>
                    <h2>Content Section</h2>
                    <p>This is test content for integration testing.</p>
                </section>
            </main>
        </body>
        </html>
        """
        
        # Mock the HTTP request
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.text = AsyncMock(return_value=html_content)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Scrape the URL
            scraper = URLScraper()
            async with scraper:
                manifest = await scraper.scrape_url('https://test.example.com')
            
            # Analyze the webpage
            analyzer = WebpageAnalyzer()
            soup = BeautifulSoup(html_content, 'html.parser')
            analysis = analyzer.analyze_webpage(soup, 'https://test.example.com')
            
            # Verify integration
            assert manifest['metadata']['title'] == 'Integration Test Page'
            assert analysis['page_type'] in ['general', 'blog', 'landing']
            assert analysis['layout_structure']['has_header'] == True


if __name__ == '__main__':
    pytest.main([__file__])
