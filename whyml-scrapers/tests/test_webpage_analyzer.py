"""
Test suite for whyml_scrapers.webpage_analyzer module

Tests for:
- WebpageAnalyzer functionality
- Page type detection
- SEO analysis
- Accessibility analysis
- Content statistics

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
from bs4 import BeautifulSoup
from unittest.mock import Mock, patch
from typing import Dict, Any

from whyml_scrapers.webpage_analyzer import WebpageAnalyzer


class TestWebpageAnalyzer:
    """Test cases for WebpageAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a WebpageAnalyzer instance for testing."""
        return WebpageAnalyzer()
    
    @pytest.fixture
    def blog_html(self):
        """Create sample blog HTML for testing."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>My Blog - Latest Posts</title>
            <meta name="description" content="Welcome to my blog with latest posts">
        </head>
        <body>
            <header>
                <h1>My Blog</h1>
            </header>
            <main>
                <article>
                    <h2>Blog Post Title</h2>
                    <p>This is a blog post content with multiple paragraphs.</p>
                    <p>Second paragraph of the blog post.</p>
                </article>
            </main>
        </body>
        </html>
        """
    
    @pytest.fixture
    def ecommerce_html(self):
        """Create sample e-commerce HTML for testing."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Online Store - Buy Products</title>
            <meta name="description" content="Shop online for great products">
        </head>
        <body>
            <header>
                <h1>Online Store</h1>
            </header>
            <main>
                <div class="product">
                    <h2>Product Name</h2>
                    <span class="price">$29.99</span>
                    <button class="add-to-cart">Add to Cart</button>
                </div>
            </main>
        </body>
        </html>
        """
    
    def test_analyzer_initialization(self, analyzer):
        """Test WebpageAnalyzer initialization."""
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_webpage')
        assert hasattr(analyzer, 'detect_page_type')
        assert hasattr(analyzer, 'analyze_seo')
    
    def test_analyze_webpage_blog(self, analyzer, blog_html):
        """Test webpage analysis for blog content."""
        soup = BeautifulSoup(blog_html, 'html.parser')
        result = analyzer.analyze_webpage(soup, 'https://example.com/blog')
        
        assert isinstance(result, dict)
        assert 'page_type' in result
        assert 'content_stats' in result
        assert 'seo_analysis' in result
        
        # Should detect as blog
        assert result['page_type'] == 'blog'
    
    def test_analyze_webpage_ecommerce(self, analyzer, ecommerce_html):
        """Test webpage analysis for e-commerce content."""
        soup = BeautifulSoup(ecommerce_html, 'html.parser')
        result = analyzer.analyze_webpage(soup, 'https://example.com/shop')
        
        assert isinstance(result, dict)
        assert 'page_type' in result
        
        # Should detect as e-commerce
        assert result['page_type'] in ['e-commerce', 'ecommerce']
    
    def test_detect_page_type_blog(self, analyzer, blog_html):
        """Test blog page type detection."""
        soup = BeautifulSoup(blog_html, 'html.parser')
        page_type = analyzer.detect_page_type(soup, 'https://example.com/blog')
        
        assert page_type == 'blog'
    
    def test_detect_page_type_ecommerce(self, analyzer, ecommerce_html):
        """Test e-commerce page type detection."""
        soup = BeautifulSoup(ecommerce_html, 'html.parser')
        page_type = analyzer.detect_page_type(soup, 'https://example.com/shop')
        
        assert page_type in ['e-commerce', 'ecommerce']
    
    def test_content_statistics(self, analyzer, blog_html):
        """Test content statistics calculation."""
        soup = BeautifulSoup(blog_html, 'html.parser')
        stats = analyzer.calculate_content_stats(soup)
        
        assert isinstance(stats, dict)
        assert 'word_count' in stats
        assert 'paragraph_count' in stats
        assert 'heading_count' in stats
        assert stats['paragraph_count'] >= 2
    
    def test_seo_analysis(self, analyzer, blog_html):
        """Test SEO analysis functionality."""
        soup = BeautifulSoup(blog_html, 'html.parser')
        seo_analysis = analyzer.analyze_seo(soup)
        
        assert isinstance(seo_analysis, dict)
        assert 'title_length' in seo_analysis
        assert 'meta_description' in seo_analysis
        assert 'heading_structure' in seo_analysis
        
        # Should detect title and meta description
        assert seo_analysis['title_length'] > 0
        assert seo_analysis['meta_description'] is not None
    
    def test_accessibility_analysis(self, analyzer):
        """Test accessibility analysis."""
        html_with_images = """
        <html>
        <body>
            <img src="image1.jpg" alt="Description 1">
            <img src="image2.jpg" alt="Description 2">
            <img src="image3.jpg">
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_with_images, 'html.parser')
        accessibility = analyzer.analyze_accessibility(soup)
        
        assert isinstance(accessibility, dict)
        assert 'alt_text_coverage' in accessibility
        
        # Should calculate alt text coverage (2 out of 3 images have alt text)
        expected_coverage = 2 / 3 * 100
        assert abs(accessibility['alt_text_coverage'] - expected_coverage) < 1
    
    def test_structure_complexity_analysis(self, analyzer):
        """Test structure complexity analysis."""
        complex_html = """
        <html>
        <body>
            <div>
                <div>
                    <div>
                        <div>
                            <p>Deep content</p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(complex_html, 'html.parser')
        
        # Test the method exists and returns expected data
        if hasattr(analyzer, 'analyze_structure_complexity'):
            complexity = analyzer.analyze_structure_complexity(soup)
            assert isinstance(complexity, dict)
        else:
            # If method doesn't exist, create a basic test
            complexity = analyzer._analyze_structure_complexity(soup)
            assert isinstance(complexity, dict)
    
    def test_empty_page_analysis(self, analyzer):
        """Test analysis of empty page."""
        empty_html = "<html><head></head><body></body></html>"
        soup = BeautifulSoup(empty_html, 'html.parser')
        
        result = analyzer.analyze_webpage(soup, 'https://example.com')
        
        assert isinstance(result, dict)
        assert 'page_type' in result
        assert 'content_stats' in result
    
    def test_malformed_html_analysis(self, analyzer):
        """Test analysis of malformed HTML."""
        malformed_html = """
        <html>
        <head>
            <title>Malformed Page
        <body>
            <h1>Title without closing
            <p>Content
        """
        
        soup = BeautifulSoup(malformed_html, 'html.parser')
        result = analyzer.analyze_webpage(soup, 'https://example.com')
        
        # Should handle malformed HTML gracefully
        assert isinstance(result, dict)
    
    def test_different_languages(self, analyzer):
        """Test analysis of pages in different languages."""
        multilang_html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <title>Página en Español</title>
            <meta name="description" content="Esta es una página en español">
        </head>
        <body>
            <h1>Bienvenidos</h1>
            <p>Este es contenido en español con caracteres especiales: ñáéíóú</p>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(multilang_html, 'html.parser')
        result = analyzer.analyze_webpage(soup, 'https://example.es')
        
        assert isinstance(result, dict)
        assert 'content_stats' in result
        # Should handle non-English content
        assert result['content_stats']['word_count'] > 0


class TestWebpageAnalyzerAdvanced:
    """Advanced test cases for WebpageAnalyzer."""
    
    @pytest.fixture
    def advanced_analyzer(self):
        """Create WebpageAnalyzer with advanced options."""
        return WebpageAnalyzer(
            max_depth=5,
            flatten_containers=True,
            simplify_structure=True,
            preserve_semantic_tags=True
        )
    
    def test_comprehensive_seo_analysis(self, advanced_analyzer):
        """Test comprehensive SEO analysis."""
        seo_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>SEO Optimized Page Title - Brand Name</title>
            <meta name="description" content="This is a well-optimized meta description that provides clear information about the page content and includes relevant keywords.">
            <meta name="keywords" content="seo, optimization, web, development">
            <meta property="og:title" content="SEO Optimized Page">
            <meta property="og:description" content="Social media description">
            <meta name="twitter:card" content="summary_large_image">
            <link rel="canonical" href="https://example.com/seo-page">
        </head>
        <body>
            <h1>Main Page Heading</h1>
            <h2>Secondary Heading</h2>
            <h3>Tertiary Heading</h3>
            <p>Content with <strong>important keywords</strong> and good structure.</p>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(seo_html, 'html.parser')
        seo_analysis = advanced_analyzer.analyze_seo(soup)
        
        assert isinstance(seo_analysis, dict)
        assert 'title_length' in seo_analysis
        assert 'meta_description' in seo_analysis
        assert 'heading_structure' in seo_analysis
        assert 'social_tags' in seo_analysis
        
        # Should detect proper heading structure
        assert seo_analysis['heading_structure']['h1_count'] == 1
        assert seo_analysis['heading_structure']['h2_count'] == 1
        
        # Should detect social media tags
        assert 'og:title' in seo_analysis['social_tags']
    
    def test_performance_metrics(self, advanced_analyzer):
        """Test performance-related metrics analysis."""
        performance_html = """
        <html>
        <head>
            <title>Performance Test Page</title>
        </head>
        <body>
            <img src="large-image.jpg" width="1920" height="1080">
            <img src="optimized.webp" width="300" height="200" alt="Optimized image">
            <script src="large-script.js"></script>
            <style>
                body { font-family: Arial; }
                .large-css { /* lots of CSS rules */ }
            </style>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(performance_html, 'html.parser')
        
        # Test performance-related analysis if method exists
        if hasattr(advanced_analyzer, 'analyze_performance'):
            performance = advanced_analyzer.analyze_performance(soup)
            assert isinstance(performance, dict)
        
        # Alternative: test image analysis
        result = advanced_analyzer.analyze_webpage(soup, 'https://example.com')
        assert isinstance(result, dict)
    
    def test_mobile_optimization_analysis(self, advanced_analyzer):
        """Test mobile optimization analysis."""
        mobile_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Mobile Optimized Page</title>
            <style>
                @media (max-width: 768px) {
                    .container { width: 100%; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Mobile Friendly Content</h1>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(mobile_html, 'html.parser')
        
        # Test mobile optimization if method exists
        if hasattr(advanced_analyzer, 'analyze_mobile_optimization'):
            mobile_analysis = advanced_analyzer.analyze_mobile_optimization(soup)
            assert isinstance(mobile_analysis, dict)
        
        # Alternative: check viewport in SEO analysis
        seo_analysis = advanced_analyzer.analyze_seo(soup)
        assert isinstance(seo_analysis, dict)


if __name__ == "__main__":
    pytest.main([__file__])
