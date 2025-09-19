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
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    class BeautifulSoup:
        def __init__(self, *args, **kwargs):
            pass

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
    def advanced_scraper(self):
        """Create URLScraper with advanced simplification features for testing."""
        return URLScraper(
            user_agent="WhyML-Test/1.0",
            timeout=10,
            extract_styles=True,
            extract_scripts=False,
            max_depth=3,
            flatten_containers=True,
            simplify_structure=True,
            preserve_semantic_tags=True,
            sections=['metadata', 'analysis', 'structure']
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
                .hero { background: #007bff; padding: 80px 0; color: white; }
                .btn-primary { background: #007bff; border: none; padding: 10px 20px; }
            </style>
        </head>
        <body>
            <div class="wrapper">
                <div class="container">
                    <div class="content-wrapper">
                        <header class="hero">
                            <div class="inner">
                                <h1>Welcome to Our Site</h1>
                                <p class="lead">This is a sample webpage for testing WhyML scraping</p>
                                <button class="btn btn-primary">Get Started</button>
                            </div>
                        </header>
                        <main class="content">
                            <article class="post">
                                <h2>Blog Post Title</h2>
                                <p>This is some sample content for testing.</p>
                                <img src="image.jpg" alt="Sample image" />
                            </article>
                        </main>
                    </div>
                </div>
            </div>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": "Sample Page",
                "description": "A sample webpage for testing"
            }
            </script>
        </body>
        </html>
        """
    
    @pytest.fixture
    def complex_nested_html(self):
        """Complex nested HTML for testing structure simplification."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Complex Structure</title>
            <meta name="description" content="Complex nested structure">
        </head>
        <body>
            <div class="outer-wrapper">
                <div class="middle-wrapper">
                    <div class="inner-wrapper">
                        <div class="content-container">
                            <div class="entry-data-wrapper entry-data-wrapper-archive">
                                <div class="entry-header-wrapper entry-header-wrapper-archive">
                                    <div class="entry-meta entry-meta-header-before">
                                        <ul>
                                            <li>
                                                <span class="post-first-category">
                                                    <a href="/category/idea/" title="Idea">Idea</a>
                                                </span>
                                            </li>
                                        </ul>
                                    </div>
                                    <header class="entry-header">
                                        <h1 class="entry-title">
                                            <a href="/post/sample">dev environment for fast development</a>
                                        </h1>
                                    </header>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    @pytest.fixture 
    def ecommerce_html(self):
        """E-commerce HTML for page type detection testing."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Product Page</title>
            <meta name="description" content="Buy our amazing product">
        </head>
        <body>
            <div class="product">
                <h1>Amazing Product</h1>
                <span class="price">$99.99</span>
                <button class="add-to-cart">Add to Cart</button>
            </div>
        </body>
        </html>
        """

    # ADVANCED SCRAPING FUNCTIONALITY TESTS

    @pytest.mark.asyncio
    async def test_structure_simplification_max_depth(self, advanced_scraper, complex_nested_html):
        """Test max depth limitation for structure simplification."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=complex_nested_html)
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with advanced_scraper:
                manifest = await advanced_scraper.scrape_url('https://example.com')
                
                # Verify max depth is applied
                assert 'structure' in manifest
                structure = manifest['structure']
                
                # Check that depth is limited (should be flatter than original)
                def get_depth(obj, current_depth=0):
                    if isinstance(obj, dict):
                        if 'children' in obj:
                            children = obj['children']
                            if isinstance(children, (list, dict)):
                                return get_depth(children, current_depth + 1)
                        return current_depth
                    elif isinstance(obj, list):
                        max_depth = current_depth
                        for item in obj:
                            depth = get_depth(item, current_depth)
                            max_depth = max(max_depth, depth)
                        return max_depth
                    return current_depth
                
                actual_depth = get_depth(structure)
                assert actual_depth <= 4  # Should be limited by max_depth setting

    @pytest.mark.asyncio
    async def test_container_flattening(self, advanced_scraper, complex_nested_html):
        """Test container div flattening functionality."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=complex_nested_html)
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with advanced_scraper:
                manifest = await advanced_scraper.scrape_url('https://example.com')
                
                # Verify wrapper divs are flattened
                assert 'structure' in manifest
                structure_str = str(manifest['structure'])
                
                # Should have fewer wrapper divs than original
                wrapper_count = structure_str.lower().count('wrapper')
                assert wrapper_count < 5  # Original has many wrapper divs

    @pytest.mark.asyncio
    async def test_selective_section_generation(self):
        """Test selective section generation functionality."""
        selective_scraper = URLScraper(
            sections=['metadata', 'analysis']  # Only these sections
        )
        
        sample_html = """
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
        </head>
        <body>
            <h1>Test Content</h1>
            <p>Sample content</p>
        </body>
        </html>
        """
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=sample_html)
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with selective_scraper:
                manifest = await selective_scraper.scrape_url('https://example.com')
                
                # Should only have requested sections
                assert 'metadata' in manifest
                assert 'analysis' in manifest
                assert 'structure' not in manifest  # Not requested
                assert 'styles' not in manifest     # Not requested
                assert 'imports' not in manifest    # Not requested

    @pytest.mark.asyncio
    async def test_page_analysis_detection(self, scraper, sample_html, ecommerce_html):
        """Test page type detection and analysis features."""
        # Test blog page detection
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=sample_html)
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with scraper:
                manifest = await scraper.scrape_url('https://example.com')
                
                assert 'analysis' in manifest
                analysis = manifest['analysis']
                
                # Check page type detection
                assert 'page_type' in analysis
                assert analysis['page_type'] in ['blog', 'website', 'unknown']
                
                # Check content statistics
                assert 'content_stats' in analysis
                stats = analysis['content_stats']
                assert 'word_count' in stats
                assert 'paragraph_count' in stats
                assert 'heading_count' in stats
                assert 'link_count' in stats
                assert 'image_count' in stats
                
                # Check structure complexity
                assert 'structure_complexity' in analysis
                complexity = analysis['structure_complexity']
                assert 'max_nesting_depth' in complexity
                assert 'total_elements' in complexity
                assert 'div_count' in complexity
                
                # Check SEO analysis
                assert 'seo_analysis' in analysis
                seo = analysis['seo_analysis']
                assert 'has_meta_description' in seo
                assert 'h1_count' in seo
                
                # Check accessibility analysis
                assert 'accessibility' in analysis
                accessibility = analysis['accessibility']
                assert 'images_with_alt_ratio' in accessibility
                assert 'has_lang_attribute' in accessibility

        # Test e-commerce page detection
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=ecommerce_html)
            mock_response.headers = {'content-type': 'text/html'}  
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with scraper:
                manifest = await scraper.scrape_url('https://ecommerce.com')
                
                assert 'analysis' in manifest
                assert manifest['analysis']['page_type'] == 'e-commerce'

    @pytest.mark.asyncio
    async def test_semantic_tag_preservation(self):
        """Test semantic HTML5 tag preservation during simplification."""
        semantic_html = """
        <html>
        <head><title>Semantic Test</title></head>
        <body>
            <div class="wrapper">
                <div class="container">
                    <header>
                        <h1>Header Content</h1>
                    </header>
                    <main>
                        <article>
                            <section>
                                <h2>Article Section</h2>
                                <p>Content</p>
                            </section>
                        </article>
                    </main>
                    <footer>
                        <p>Footer content</p>
                    </footer>
                </div>
            </div>
        </body>
        </html>
        """
        
        semantic_scraper = URLScraper(
            flatten_containers=True,
            preserve_semantic_tags=True
        )
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=semantic_html)
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with semantic_scraper:
                manifest = await semantic_scraper.scrape_url('https://example.com')
                
                # Semantic tags should be preserved
                structure_str = str(manifest['structure'])
                assert 'header' in structure_str
                assert 'main' in structure_str
                assert 'article' in structure_str
                assert 'section' in structure_str
                assert 'footer' in structure_str

    @pytest.mark.asyncio
    async def test_css_styles_extraction_with_simplification(self, advanced_scraper, sample_html):
        """Test CSS extraction works with structure simplification."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=sample_html)
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with advanced_scraper:
                manifest = await advanced_scraper.scrape_url('https://example.com')
                
                # Should have styles even with simplification
                assert 'styles' in manifest
                styles = manifest['styles']
                
                # Should extract inline styles from <style> tag
                assert len(styles) > 0
                assert any('container' in style_name or 'background' in str(styles) for style_name in styles)

    def test_wrapper_div_detection(self, advanced_scraper):
        """Test wrapper div detection logic."""
        # Test wrapper class detection
        wrapper_div = {
            'class': 'wrapper container inner',
            'children': [{'p': {'text': 'content'}}]
        }
        assert advanced_scraper._is_wrapper_div(wrapper_div) == True
        
        # Test non-wrapper div
        content_div = {
            'class': 'content',
            'text': 'Some content',
            'data-id': '123'
        }
        assert advanced_scraper._is_wrapper_div(content_div) == False
        
        # Test structural-only div
        structural_div = {
            'class': 'layout-grid',
            'children': [{'div': {'text': 'content'}}]
        }
        assert advanced_scraper._is_wrapper_div(structural_div) == True

    def test_depth_limiting_algorithm(self, advanced_scraper):
        """Test depth limiting algorithm."""
        deep_structure = {
            'div': {
                'children': {
                    'div': {
                        'children': {
                            'div': {
                                'children': {
                                    'div': {
                                        'text': 'deep content'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        limited = advanced_scraper._limit_depth(deep_structure, max_depth=2)
        
        # Should be limited to specified depth
        assert 'div' in limited
        # Content should be preserved at the depth limit
        def get_text_at_depth(obj, depth=0):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == 'text':
                        return value, depth
                    elif isinstance(value, dict):
                        return get_text_at_depth(value, depth + 1)
            return None, depth
        
        text, final_depth = get_text_at_depth(limited)
        assert final_depth <= 3  # Should respect max_depth

    @pytest.mark.asyncio
    async def test_no_styles_option(self):
        """Test --no-styles equivalent functionality."""
        no_styles_scraper = URLScraper(extract_styles=False)
        
        sample_html = """
        <html>
        <head>
            <style>.test { color: red; }</style>
            <title>No Styles Test</title>
        </head>
        <body><h1>Content</h1></body>
        </html>
        """
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=sample_html)
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with no_styles_scraper:
                manifest = await no_styles_scraper.scrape_url('https://example.com')
                
                # Should not have styles section when extract_styles=False
                assert 'styles' not in manifest or len(manifest.get('styles', {})) == 0

    # INTEGRATION TESTS FOR COMPLETE WORKFLOW

    @pytest.mark.asyncio
    async def test_scrape_to_html_conversion_workflow(self, scraper, sample_html):
        """Test complete scrape → YAML → HTML conversion workflow."""
        from whyml.processor import WhyMLProcessor
        from whyml.converters.html_converter import HTMLConverter
        import tempfile
        import os
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=sample_html)
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with scraper:
                # Step 1: Scrape to manifest
                manifest = await scraper.scrape_url('https://example.com')
                
                # Step 2: Convert back to HTML
                converter = HTMLConverter()
                html_result = await converter.convert(manifest)
                
                # Step 3: Validate conversion
                assert html_result.success == True
                assert len(html_result.content) > 0
                assert '<html' in html_result.content
                assert 'Welcome to Our Site' in html_result.content  # Original content preserved
                
                # Step 4: Write and read test files
                with tempfile.TemporaryDirectory() as tmpdir:
                    manifest_path = os.path.join(tmpdir, 'test_manifest.yaml')
                    html_path = os.path.join(tmpdir, 'regenerated.html')
                    
                    # Save manifest
                    import yaml
                    with open(manifest_path, 'w') as f:
                        yaml.dump(manifest, f, default_flow_style=False)
                    
                    # Save regenerated HTML
                    with open(html_path, 'w') as f:
                        f.write(html_result.content)
                    
                    # Verify files exist and have content
                    assert os.path.exists(manifest_path)
                    assert os.path.exists(html_path)
                    assert os.path.getsize(manifest_path) > 0
                    assert os.path.getsize(html_path) > 0

    @pytest.mark.asyncio 
    async def test_testing_workflow_similarity_calculation(self, scraper):
        """Test the testing workflow similarity calculation functionality."""
        original_html = """
        <html><head><title>Test</title></head>
        <body><h1>Hello World</h1><p>Content here</p></body></html>
        """
        
        regenerated_html = """
        <html><head><title>Test</title></head>
        <body><h1>Hello World</h1><p>Content here</p></body></html>
        """
        
        # Test similarity calculation method (this would be part of CLI testing functionality)
        similarity = scraper._calculate_similarity(original_html, regenerated_html)
        assert similarity >= 0.9  # Should be very similar
        
        # Test with different content
        different_html = """
        <html><head><title>Different</title></head>
        <body><h2>Different Content</h2></body></html>
        """
        
        similarity_different = scraper._calculate_similarity(original_html, different_html)
        assert similarity_different < similarity  # Should be less similar

    @pytest.mark.asyncio
    async def test_structure_comparison_metrics(self, advanced_scraper, complex_nested_html):
        """Test structure comparison and complexity metrics."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=complex_nested_html)
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with advanced_scraper:
                manifest = await advanced_scraper.scrape_url('https://example.com')
                
                # Verify analysis contains complexity metrics
                assert 'analysis' in manifest
                analysis = manifest['analysis']
                
                assert 'structure_complexity' in analysis
                complexity = analysis['structure_complexity']
                
                # Should have complexity reduction due to simplification
                assert 'max_nesting_depth' in complexity
                assert 'total_elements' in complexity
                assert 'simplification_applied' in complexity
                assert complexity['simplification_applied'] == True

    def test_manifest_validation_with_selective_sections(self):
        """Test manifest validation works with selective sections."""
        from whyml.manifest_processor import ManifestProcessor
        
        # Test manifest with only metadata and analysis
        selective_manifest = {
            'metadata': {
                'title': 'Test Page',
                'description': 'Test description',
                'version': '1.0.0'
            },
            'analysis': {
                'page_type': 'website',
                'content_stats': {'word_count': 10}
            }
        }
        
        processor = ManifestProcessor()
        errors, warnings = processor.validate_manifest(selective_manifest)
        
        # Should validate successfully without structure section
        assert len(errors) == 0
        
        # Test with only structure section  
        structure_only_manifest = {
            'metadata': {
                'title': 'Test Page',
                'description': 'Test description',
                'version': '1.0.0'
            },
            'structure': {
                'div': {'text': 'content'}
            }
        }
        
        errors, warnings = processor.validate_manifest(structure_only_manifest)
        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_error_handling_network_issues(self, scraper):
        """Test error handling for network and parsing issues."""
        # Test network timeout
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = asyncio.TimeoutError()
            
            async with scraper:
                with pytest.raises(NetworkError):
                    await scraper.scrape_url('https://timeout.example.com')
        
        # Test invalid HTML
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='<html><invalid</html>')
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with scraper:
                # Should handle invalid HTML gracefully
                manifest = await scraper.scrape_url('https://invalid.example.com')
                assert 'metadata' in manifest  # Should still extract what it can

    @pytest.mark.asyncio
    async def test_performance_with_large_pages(self, advanced_scraper):
        """Test performance and memory usage with large complex pages."""
        # Create a large HTML structure
        large_html = """
        <html>
        <head><title>Large Page</title></head>
        <body>
        """ + "\n".join([
            f'<div class="section-{i}"><h2>Section {i}</h2>' + 
            ''.join([f'<p>Paragraph {j} content here</p>' for j in range(10)]) + 
            '</div>' 
            for i in range(50)
        ]) + """
        </body>
        </html>
        """
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=large_html)
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with advanced_scraper:
                import time
                start_time = time.time()
                
                manifest = await advanced_scraper.scrape_url('https://large.example.com')
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Should complete in reasonable time (adjust based on performance requirements)
                assert processing_time < 30  # 30 seconds max
                
                # Should have simplified structure 
                assert 'structure' in manifest
                assert 'analysis' in manifest
                
                # Complexity analysis should show simplification benefits
                complexity = manifest['analysis']['structure_complexity']
                assert complexity['simplification_applied'] == True


class TestWebpageAnalyzer:
    """Test cases for webpage analyzer functionality."""
    
    @pytest.fixture
    def analyzer(self):
        """Create WebpageAnalyzer instance for testing."""
        return WebpageAnalyzer()
    
    @pytest.mark.asyncio
    async def test_analyze_blog_page(self, analyzer):
        """Test analysis of blog page structure."""
        blog_html = """
        <html>
        <head>
            <title>My Blog Post</title>
            <meta name="description" content="A great blog post">
        </head>
        <body>
            <article>
                <h1>Blog Post Title</h1>
                <div class="meta">
                    <time datetime="2024-01-01">January 1, 2024</time>
                    <span class="author">John Doe</span>
                </div>
                <div class="content">
                    <p>This is the blog post content.</p>
                    <p>More blog content here.</p>
                </div>
            </article>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(blog_html, 'html.parser')
        analysis = await analyzer.analyze_page(soup, 'https://blog.example.com')
        
        assert analysis['page_type'] == 'blog'
        assert analysis['content_stats']['paragraph_count'] >= 2
        assert analysis['seo_analysis']['has_meta_description'] == True
        assert 'article' in analysis['structure_complexity']['semantic_elements']

    @pytest.mark.asyncio  
    async def test_analyze_ecommerce_page(self, analyzer):
        """Test analysis of e-commerce page structure."""
        ecommerce_html = """
        <html>
        <head><title>Product - Amazing Item</title></head>
        <body>
            <div class="product">
                <h1>Amazing Product</h1>
                <span class="price">$99.99</span>
                <button class="add-to-cart">Add to Cart</button>
                <button class="buy-now">Buy Now</button>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(ecommerce_html, 'html.parser')
        analysis = await analyzer.analyze_page(soup, 'https://shop.example.com')
        
        assert analysis['page_type'] == 'e-commerce'
        assert 'price' in str(analysis).lower()
        assert 'cart' in str(analysis).lower() or 'buy' in str(analysis).lower()

    def test_seo_analysis_metrics(self, analyzer):
        """Test SEO analysis functionality."""
        html_with_seo = """
        <html lang="en">
        <head>
            <title>Great SEO Page</title>
            <meta name="description" content="This page has good SEO">
            <meta name="keywords" content="seo, test, page">
        </head>
        <body>
            <h1>Main Heading</h1>
            <h2>Subheading 1</h2>
            <h2>Subheading 2</h2>
            <p>Content with proper heading structure.</p>
            <img src="image.jpg" alt="Descriptive alt text">
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html_with_seo, 'html.parser')
        seo = analyzer._analyze_seo(soup)
        
        assert seo['has_meta_description'] == True
        assert seo['meta_description_length'] > 0
        assert seo['h1_count'] == 1
        assert seo['h2_count'] == 2
        assert seo['title_length'] > 0

    def test_accessibility_analysis(self, analyzer):
        """Test accessibility analysis functionality."""
        accessible_html = """
        <html lang="en">
        <head><title>Accessible Page</title></head>
        <body>
            <img src="image1.jpg" alt="Image with alt text">
            <img src="image2.jpg" alt="Another image">
            <img src="image3.jpg">  <!-- Missing alt -->
            <h1>Proper Heading Structure</h1>
            <h2>Subheading</h2>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(accessible_html, 'html.parser')
        accessibility = analyzer._analyze_accessibility(soup)
        
        assert accessibility['has_lang_attribute'] == True
        assert accessibility['images_with_alt_ratio'] == 2/3  # 2 out of 3 images have alt
        assert accessibility['heading_structure_valid'] == True

    def test_content_statistics(self, analyzer):
        """Test content statistics calculation."""
        content_html = """
        <html>
        <body>
            <h1>Title</h1>
            <h2>Subtitle</h2>
            <p>First paragraph with several words here.</p>
            <p>Second paragraph with more content.</p>
            <a href="link1.html">Link 1</a>
            <a href="link2.html">Link 2</a>
            <img src="image.jpg" alt="Image">
        </body>
        </html>
        """
        
        soup = BeautifulSoup(content_html, 'html.parser')
        stats = analyzer._calculate_content_stats(soup)
        
        assert stats['paragraph_count'] == 2
        assert stats['heading_count'] == 2
        assert stats['link_count'] == 2
        assert stats['image_count'] == 1
        assert stats['word_count'] > 10

    def test_structure_complexity_analysis(self, analyzer):
        """Test structure complexity analysis."""
        complex_html = """
        <html>
        <body>
            <div>
                <div>
                    <div>
                        <div>
                            <p>Deeply nested content</p>
                        </div>
                    </div>
                </div>
            </div>
            <header>Semantic element</header>
            <main>Another semantic element</main>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(complex_html, 'html.parser')
        complexity = analyzer._analyze_structure_complexity(soup)
        
        assert complexity['max_nesting_depth'] >= 4
        assert complexity['total_elements'] > 5
        assert complexity['div_count'] >= 4
        assert 'header' in complexity['semantic_elements']
        assert 'main' in complexity['semantic_elements']
        
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
