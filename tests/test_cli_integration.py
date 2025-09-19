"""
Integration tests for CLI with advanced scraping functionality.

Tests the complete CLI workflow including all new scraping flags,
structure simplification, selective section generation, and testing workflow.

Copyright 2024 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import asyncio
import tempfile
import os
import yaml
from unittest.mock import Mock, patch, AsyncMock
from click.testing import CliRunner

from whyml.cli_wrapper import cli
from whyml.exceptions import NetworkError


class TestCLIAdvancedScraping:
    """Test CLI integration with advanced scraping features."""
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def sample_html(self):
        """Sample HTML for testing."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="description" content="Sample test page">
            <title>Sample Test Page</title>
            <style>
                .container { max-width: 1200px; margin: 0 auto; }
                .hero { background: #007bff; padding: 80px 0; color: white; }
            </style>
        </head>
        <body>
            <div class="wrapper">
                <div class="container">
                    <div class="content-wrapper">
                        <header class="hero">
                            <h1>Welcome to Test Site</h1>
                            <p>This is a test page for CLI scraping</p>
                        </header>
                        <main>
                            <article>
                                <h2>Article Title</h2>
                                <p>Sample content for testing.</p>
                            </article>
                        </main>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    def test_basic_scrape_command(self, runner, sample_html):
        """Test basic scrape command functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'output.yaml')
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=sample_html)
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = runner.invoke(cli, [
                    'scrape', 
                    'https://example.com',
                    '--output', output_file
                ])
                
                assert result.exit_code == 0
                assert os.path.exists(output_file)
                
                # Verify YAML content
                with open(output_file, 'r') as f:
                    manifest = yaml.safe_load(f)
                
                assert 'metadata' in manifest
                assert 'structure' in manifest
                assert manifest['metadata']['title'] == 'Sample Test Page'

    def test_structure_simplification_flags(self, runner, sample_html):
        """Test structure simplification CLI flags."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'simplified.yaml')
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=sample_html)
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = runner.invoke(cli, [
                    'scrape',
                    'https://example.com',
                    '--output', output_file,
                    '--max-depth', '2',
                    '--flatten-containers',
                    '--simplify-structure'
                ])
                
                assert result.exit_code == 0
                
                with open(output_file, 'r') as f:
                    manifest = yaml.safe_load(f)
                
                # Should have analysis showing simplification was applied
                assert 'analysis' in manifest
                assert 'structure_complexity' in manifest['analysis']
                complexity = manifest['analysis']['structure_complexity']
                assert complexity.get('simplification_applied') == True

    def test_selective_section_generation(self, runner, sample_html):
        """Test selective section generation with --section flags."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'selective.yaml')
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=sample_html)
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = runner.invoke(cli, [
                    'scrape',
                    'https://example.com',
                    '--output', output_file,
                    '--section', 'metadata',
                    '--section', 'analysis'
                ])
                
                assert result.exit_code == 0
                
                with open(output_file, 'r') as f:
                    manifest = yaml.safe_load(f)
                
                # Should only have requested sections
                assert 'metadata' in manifest
                assert 'analysis' in manifest
                assert 'structure' not in manifest
                assert 'styles' not in manifest

    def test_no_styles_flag(self, runner, sample_html):
        """Test --no-styles flag functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'no_styles.yaml')
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=sample_html)
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = runner.invoke(cli, [
                    'scrape',
                    'https://example.com',
                    '--output', output_file,
                    '--no-styles'
                ])
                
                assert result.exit_code == 0
                
                with open(output_file, 'r') as f:
                    manifest = yaml.safe_load(f)
                
                # Should not have styles section
                assert 'styles' not in manifest or len(manifest.get('styles', {})) == 0

    def test_extract_scripts_flag(self, runner):
        """Test --extract-scripts flag functionality."""
        html_with_scripts = """
        <html>
        <head>
            <title>Scripts Test</title>
            <script>console.log('inline script');</script>
        </head>
        <body>
            <h1>Content</h1>
            <script src="external.js"></script>
        </body>
        </html>
        """
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'with_scripts.yaml')
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=html_with_scripts)
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = runner.invoke(cli, [
                    'scrape',
                    'https://example.com',
                    '--output', output_file,
                    '--extract-scripts'
                ])
                
                assert result.exit_code == 0
                
                with open(output_file, 'r') as f:
                    manifest = yaml.safe_load(f)
                
                # Should have scripts section
                assert 'scripts' in manifest or 'imports' in manifest

    def test_no_preserve_semantic_flag(self, runner):
        """Test --no-preserve-semantic flag functionality."""
        semantic_html = """
        <html>
        <head><title>Semantic Test</title></head>
        <body>
            <div class="wrapper">
                <header><h1>Header</h1></header>
                <main><p>Content</p></main>
                <footer><p>Footer</p></footer>
            </div>
        </body>
        </html>
        """
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'no_semantic.yaml')
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=semantic_html)
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = runner.invoke(cli, [
                    'scrape',
                    'https://example.com',
                    '--output', output_file,
                    '--flatten-containers',
                    '--no-preserve-semantic'
                ])
                
                assert result.exit_code == 0

    def test_testing_workflow_flag(self, runner, sample_html):
        """Test --test-conversion flag functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'test_conversion.yaml')
            html_output = os.path.join(tmpdir, 'regenerated.html')
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                # Mock original page fetch
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=sample_html)
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = runner.invoke(cli, [
                    'scrape',
                    'https://example.com',
                    '--output', output_file,
                    '--test-conversion',
                    '--output-html', html_output
                ])
                
                assert result.exit_code == 0
                
                # Should create both YAML manifest and regenerated HTML
                assert os.path.exists(output_file)
                assert os.path.exists(html_output)
                
                # Should output testing metrics
                assert 'Testing Results:' in result.output or 'Similarity:' in result.output

    def test_combined_advanced_flags(self, runner, sample_html):
        """Test combination of multiple advanced flags."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'combined.yaml')
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=sample_html)
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = runner.invoke(cli, [
                    'scrape',
                    'https://example.com',
                    '--output', output_file,
                    '--max-depth', '3',
                    '--flatten-containers',
                    '--simplify-structure',
                    '--section', 'structure',
                    '--section', 'metadata',
                    '--section', 'analysis',
                    '--no-styles'
                ])
                
                assert result.exit_code == 0
                
                with open(output_file, 'r') as f:
                    manifest = yaml.safe_load(f)
                
                # Should have only requested sections
                assert 'metadata' in manifest
                assert 'structure' in manifest
                assert 'analysis' in manifest
                assert 'styles' not in manifest
                
                # Should show simplification was applied
                assert manifest['analysis']['structure_complexity']['simplification_applied'] == True

    def test_error_handling_invalid_url(self, runner):
        """Test CLI error handling for invalid URLs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'error.yaml')
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_get.side_effect = Exception("Network error")
                
                result = runner.invoke(cli, [
                    'scrape',
                    'https://invalid-url.example.com',
                    '--output', output_file
                ])
                
                assert result.exit_code == 1
                assert 'Error scraping URL' in result.output

    def test_error_handling_invalid_output_path(self, runner, sample_html):
        """Test CLI error handling for invalid output paths."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=sample_html)
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = runner.invoke(cli, [
                'scrape',
                'https://example.com',
                '--output', '/nonexistent/directory/output.yaml'
            ])
            
            assert result.exit_code == 1

    def test_verbose_output_flag(self, runner, sample_html):
        """Test verbose output provides detailed information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'verbose.yaml')
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=sample_html)
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = runner.invoke(cli, [
                    'scrape',
                    'https://example.com',
                    '--output', output_file,
                    '--verbose'
                ], catch_exceptions=False)
                
                assert result.exit_code == 0
                
                # Should provide detailed output information
                assert 'Scraping URL:' in result.output or 'Processing' in result.output

    def test_help_text_includes_new_options(self, runner):
        """Test that help text includes all new advanced scraping options."""
        result = runner.invoke(cli, ['scrape', '--help'])
        
        assert result.exit_code == 0
        
        # Check for new flags in help text
        help_text = result.output
        assert '--max-depth' in help_text
        assert '--flatten-containers' in help_text
        assert '--simplify-structure' in help_text
        assert '--section' in help_text
        assert '--test-conversion' in help_text
        assert '--no-styles' in help_text
        assert '--extract-scripts' in help_text
        assert '--no-preserve-semantic' in help_text

    def test_flag_validation(self, runner):
        """Test validation of flag combinations and values."""
        # Test invalid max-depth value
        result = runner.invoke(cli, [
            'scrape',
            'https://example.com',
            '--max-depth', '-1'
        ])
        assert result.exit_code != 0
        
        # Test invalid section name
        result = runner.invoke(cli, [
            'scrape',
            'https://example.com',
            '--section', 'invalid_section'
        ])
        # Should handle gracefully or show warning


class TestCLIScrapingWorkflow:
    """Test complete CLI scraping workflows."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_real_world_blog_scraping_workflow(self, runner):
        """Test realistic blog scraping scenario."""
        blog_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="description" content="A great blog post about web development">
            <title>How to Build Modern Websites | Tech Blog</title>
            <style>
                .post { max-width: 800px; margin: 0 auto; }
                .meta { color: #666; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <article class="post">
                <header>
                    <h1>How to Build Modern Websites</h1>
                    <div class="meta">
                        <time datetime="2024-01-15">January 15, 2024</time>
                        <span class="author">by Jane Developer</span>
                    </div>
                </header>
                <div class="content">
                    <p>Modern web development has evolved significantly...</p>
                    <h2>Key Technologies</h2>
                    <p>The most important technologies to learn are:</p>
                    <ul>
                        <li>HTML5 and semantic markup</li>
                        <li>CSS3 and responsive design</li>
                        <li>JavaScript and modern frameworks</li>
                    </ul>
                </div>
            </article>
        </body>
        </html>
        """
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'blog_analysis.yaml')
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=blog_html)
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = runner.invoke(cli, [
                    'scrape',
                    'https://blog.example.com/modern-websites',
                    '--output', output_file,
                    '--section', 'analysis',
                    '--section', 'metadata',
                    '--simplify-structure'
                ])
                
                assert result.exit_code == 0
                
                with open(output_file, 'r') as f:
                    manifest = yaml.safe_load(f)
                
                # Should detect blog page type
                assert manifest['analysis']['page_type'] == 'blog'
                assert manifest['metadata']['title'] == 'How to Build Modern Websites | Tech Blog'

    def test_ecommerce_monitoring_workflow(self, runner):
        """Test e-commerce page monitoring scenario."""
        ecommerce_html = """
        <html>
        <head>
            <title>Premium Headphones - $199.99 | Audio Store</title>
            <meta name="description" content="High-quality premium headphones with noise cancellation">
        </head>
        <body>
            <div class="product-page">
                <div class="product-info">
                    <h1>Premium Wireless Headphones</h1>
                    <div class="price-section">
                        <span class="price">$199.99</span>
                        <span class="original-price">$299.99</span>
                    </div>
                    <button class="add-to-cart">Add to Cart</button>
                </div>
            </div>
        </body>
        </html>
        """
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'product_monitoring.yaml')
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=ecommerce_html)
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = runner.invoke(cli, [
                    'scrape',
                    'https://store.example.com/headphones',
                    '--output', output_file,
                    '--section', 'analysis',
                    '--section', 'metadata'
                ])
                
                assert result.exit_code == 0
                
                with open(output_file, 'r') as f:
                    manifest = yaml.safe_load(f)
                
                # Should detect e-commerce page
                assert manifest['analysis']['page_type'] == 'e-commerce'
                assert '$199.99' in str(manifest)

    def test_legacy_refactoring_workflow(self, runner):
        """Test legacy website refactoring scenario."""
        legacy_html = """
        <html>
        <head><title>Old Corporate Site</title></head>
        <body>
            <table width="100%" cellspacing="0" cellpadding="0">
                <tr>
                    <td>
                        <table width="800" align="center">
                            <tr>
                                <td>
                                    <font face="Arial" size="4"><b>Welcome to Our Company</b></font>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <font face="Arial" size="2">We provide excellent services...</font>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'legacy_refactor.yaml')
            html_output = os.path.join(tmpdir, 'modernized.html')
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value=legacy_html)
                mock_response.headers = {'content-type': 'text/html'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = runner.invoke(cli, [
                    'scrape',
                    'https://legacy.example.com',
                    '--output', output_file,
                    '--max-depth', '2',
                    '--flatten-containers',
                    '--simplify-structure',
                    '--test-conversion',
                    '--output-html', html_output
                ])
                
                assert result.exit_code == 0
                assert os.path.exists(output_file)
                assert os.path.exists(html_output)
                
                # Should show significant simplification
                with open(output_file, 'r') as f:
                    manifest = yaml.safe_load(f)
                
                complexity = manifest['analysis']['structure_complexity']
                assert complexity['simplification_applied'] == True
