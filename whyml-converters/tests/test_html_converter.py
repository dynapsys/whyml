"""
Test suite for whyml_converters.html_converter module

Tests for:
- HTMLConverter functionality
- HTML generation from manifests
- CSS integration
- JavaScript handling
- Template processing
- Error handling

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from whyml_converters.html_converter import HTMLConverter
from whyml_converters.base_converter import ConversionResult


class TestHTMLConverter:
    """Test cases for HTMLConverter class."""
    
    @pytest.fixture
    def converter(self):
        """Create an HTMLConverter instance for testing."""
        return HTMLConverter()
    
    @pytest.fixture
    def simple_manifest(self) -> Dict[str, Any]:
        """Create a simple manifest for testing."""
        return {
            "metadata": {
                "title": "Test Page",
                "description": "A test page for HTML conversion",
                "version": "1.0.0"
            },
            "structure": {
                "html": {
                    "head": {
                        "title": "Test Page",
                        "meta": [
                            {"name": "description", "content": "Test page description"},
                            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                        ]
                    },
                    "body": {
                        "header": {
                            "h1": "Welcome to Test Page"
                        },
                        "main": {
                            "div": {
                                "class": "container",
                                "content": "This is the main content"
                            }
                        },
                        "footer": {
                            "p": "© 2025 Test Site"
                        }
                    }
                }
            }
        }
    
    @pytest.fixture
    def manifest_with_styles(self) -> Dict[str, Any]:
        """Create a manifest with CSS styles."""
        return {
            "metadata": {
                "title": "Styled Page",
                "description": "Page with custom styles"
            },
            "structure": {
                "html": {
                    "body": {
                        "div": {
                            "class": "styled-content",
                            "content": "Styled content"
                        }
                    }
                }
            },
            "styles": {
                "primary": "#007bff",
                "secondary": "#6c757d",
                "css": """
                .styled-content {
                    background-color: var(--primary);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                }
                """
            }
        }
    
    def test_converter_initialization(self, converter):
        """Test HTMLConverter initialization."""
        assert converter is not None
        assert hasattr(converter, 'convert')
        assert hasattr(converter, 'generate_html')
    
    def test_simple_html_conversion(self, converter, simple_manifest):
        """Test basic HTML conversion."""
        result = converter.convert(simple_manifest)
        
        assert isinstance(result, ConversionResult)
        assert result.format_type == 'html'
        assert 'test-page.html' in result.filename
        
        # Check HTML content
        html_content = result.content
        assert '<!DOCTYPE html>' in html_content
        assert '<html' in html_content
        assert '<head>' in html_content
        assert '<body>' in html_content
        assert 'Test Page' in html_content
        assert 'Welcome to Test Page' in html_content
    
    def test_html_with_styles_conversion(self, converter, manifest_with_styles):
        """Test HTML conversion with CSS styles."""
        result = converter.convert(manifest_with_styles)
        
        assert isinstance(result, ConversionResult)
        
        html_content = result.content
        assert '<style>' in html_content or '<link' in html_content
        assert '.styled-content' in html_content
        assert '--primary' in html_content or '#007bff' in html_content
    
    def test_meta_tags_generation(self, converter, simple_manifest):
        """Test proper meta tag generation."""
        result = converter.convert(simple_manifest)
        
        html_content = result.content
        assert '<meta name="description"' in html_content
        assert '<meta name="viewport"' in html_content
        assert 'Test page description' in html_content
        assert 'width=device-width' in html_content
    
    def test_semantic_html_structure(self, converter, simple_manifest):
        """Test generation of semantic HTML structure."""
        result = converter.convert(simple_manifest)
        
        html_content = result.content
        assert '<header>' in html_content
        assert '<main>' in html_content
        assert '<footer>' in html_content
        assert '<h1>' in html_content
    
    def test_css_variables_substitution(self, converter, manifest_with_styles):
        """Test CSS variable substitution."""
        result = converter.convert(manifest_with_styles)
        
        html_content = result.content
        # Should either use CSS variables or substitute values directly
        assert ('--primary' in html_content and '#007bff' in html_content) or \
               '#007bff' in html_content.replace('var(--primary)', '#007bff')
    
    def test_conversion_with_scripts(self, converter):
        """Test HTML conversion with JavaScript."""
        manifest_with_js = {
            "metadata": {"title": "JS Page"},
            "structure": {
                "html": {
                    "body": {
                        "div": {"content": "Interactive content"}
                    }
                }
            },
            "scripts": [
                {
                    "type": "inline",
                    "content": "console.log('Hello World');"
                },
                {
                    "type": "external",
                    "src": "https://cdn.example.com/script.js"
                }
            ]
        }
        
        result = converter.convert(manifest_with_js)
        
        html_content = result.content
        assert '<script>' in html_content
        assert 'console.log' in html_content
        assert 'https://cdn.example.com/script.js' in html_content
    
    def test_conversion_with_external_resources(self, converter):
        """Test conversion with external CSS and JS resources."""
        manifest_with_externals = {
            "metadata": {"title": "External Resources Page"},
            "structure": {
                "html": {
                    "body": {"div": {"content": "Content with external resources"}}
                }
            },
            "imports": [
                {
                    "type": "css",
                    "url": "https://cdn.example.com/styles.css"
                },
                {
                    "type": "js",
                    "url": "https://cdn.example.com/script.js"
                }
            ]
        }
        
        result = converter.convert(manifest_with_externals)
        
        html_content = result.content
        assert '<link rel="stylesheet"' in html_content
        assert 'https://cdn.example.com/styles.css' in html_content
        assert '<script src=' in html_content
        assert 'https://cdn.example.com/script.js' in html_content
    
    def test_responsive_design_integration(self, converter):
        """Test responsive design features."""
        responsive_manifest = {
            "metadata": {"title": "Responsive Page"},
            "structure": {
                "html": {
                    "head": {
                        "meta": [
                            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                        ]
                    },
                    "body": {
                        "div": {
                            "class": "container-fluid",
                            "content": "Responsive content"
                        }
                    }
                }
            },
            "styles": {
                "css": """
                @media (max-width: 768px) {
                    .container-fluid { padding: 10px; }
                }
                @media (min-width: 769px) {
                    .container-fluid { padding: 20px; }
                }
                """
            }
        }
        
        result = converter.convert(responsive_manifest)
        
        html_content = result.content
        assert 'viewport' in html_content
        assert '@media' in html_content
        assert 'max-width: 768px' in html_content
    
    def test_accessibility_features(self, converter):
        """Test accessibility feature generation."""
        accessible_manifest = {
            "metadata": {"title": "Accessible Page"},
            "structure": {
                "html": {
                    "body": {
                        "header": {
                            "nav": {
                                "aria-label": "Main navigation",
                                "ul": [
                                    {"li": {"a": {"href": "/", "text": "Home"}}},
                                    {"li": {"a": {"href": "/about", "text": "About"}}}
                                ]
                            }
                        },
                        "main": {
                            "aria-label": "Main content",
                            "h1": "Page Title",
                            "p": "Main content text"
                        }
                    }
                }
            }
        }
        
        result = converter.convert(accessible_manifest)
        
        html_content = result.content
        assert 'aria-label=' in html_content
        assert 'Main navigation' in html_content
        assert 'Main content' in html_content
    
    def test_conversion_options(self, converter, simple_manifest):
        """Test conversion with various options."""
        options = {
            'minify': True,
            'include_comments': False,
            'optimize_images': True,
            'inline_css': True
        }
        
        result = converter.convert(simple_manifest, **options)
        
        assert isinstance(result, ConversionResult)
        # Should respect options in the conversion process
    
    def test_invalid_manifest_handling(self, converter):
        """Test handling of invalid manifest."""
        invalid_manifest = {
            "metadata": {},  # Missing required fields
            # Missing structure
        }
        
        # Should handle gracefully or raise appropriate exception
        try:
            result = converter.convert(invalid_manifest)
            assert isinstance(result, ConversionResult)
        except Exception as e:
            # Should be a specific conversion-related exception
            assert "manifest" in str(e).lower() or "conversion" in str(e).lower()
    
    def test_empty_manifest_handling(self, converter):
        """Test handling of empty manifest."""
        empty_manifest = {}
        
        # Should handle gracefully
        try:
            result = converter.convert(empty_manifest)
            assert isinstance(result, ConversionResult)
        except Exception as e:
            assert isinstance(e, (ValueError, TypeError))
    
    def test_complex_nested_structure(self, converter):
        """Test conversion of complex nested structures."""
        complex_manifest = {
            "metadata": {"title": "Complex Structure"},
            "structure": {
                "html": {
                    "body": {
                        "div": {
                            "class": "wrapper",
                            "children": [
                                {
                                    "header": {
                                        "class": "site-header",
                                        "children": [
                                            {"h1": "Site Title"},
                                            {
                                                "nav": {
                                                    "ul": [
                                                        {"li": {"a": {"href": "/", "text": "Home"}}},
                                                        {"li": {"a": {"href": "/about", "text": "About"}}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "main": {
                                        "class": "content",
                                        "children": [
                                            {"h2": "Main Content"},
                                            {"p": "Content paragraph"},
                                            {
                                                "div": {
                                                    "class": "sidebar",
                                                    "children": [
                                                        {"h3": "Sidebar"},
                                                        {"ul": [
                                                            {"li": "Item 1"},
                                                            {"li": "Item 2"}
                                                        ]}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(complex_manifest)
        
        html_content = result.content
        assert '<div class="wrapper">' in html_content
        assert '<header class="site-header">' in html_content
        assert '<nav>' in html_content
        assert '<main class="content">' in html_content
        assert '<div class="sidebar">' in html_content


class TestHTMLConverterAdvanced:
    """Advanced test cases for HTMLConverter."""
    
    @pytest.fixture
    def advanced_converter(self):
        """Create HTMLConverter with advanced options."""
        return HTMLConverter(
            optimize_output=True,
            minify_html=True,
            include_meta_generator=True
        )
    
    def test_seo_optimization_features(self, advanced_converter):
        """Test SEO optimization features."""
        seo_manifest = {
            "metadata": {
                "title": "SEO Optimized Page",
                "description": "This page is optimized for search engines",
                "keywords": "seo, optimization, web, development",
                "author": "Test Author",
                "canonical_url": "https://example.com/seo-page"
            },
            "structure": {
                "html": {
                    "body": {
                        "h1": "SEO Optimized Page",
                        "p": "Content optimized for search engines"
                    }
                }
            }
        }
        
        result = advanced_converter.convert(seo_manifest)
        
        html_content = result.content
        assert '<meta name="description"' in html_content
        assert '<meta name="keywords"' in html_content
        assert '<meta name="author"' in html_content
        assert '<link rel="canonical"' in html_content
        assert 'https://example.com/seo-page' in html_content
    
    def test_social_media_meta_tags(self, advanced_converter):
        """Test social media meta tag generation."""
        social_manifest = {
            "metadata": {
                "title": "Social Media Page",
                "description": "Page optimized for social media sharing",
                "image": "https://example.com/image.jpg",
                "social": {
                    "og_title": "Custom OpenGraph Title",
                    "og_description": "Custom OpenGraph Description",
                    "twitter_card": "summary_large_image",
                    "twitter_site": "@example"
                }
            },
            "structure": {
                "html": {
                    "body": {"h1": "Social Media Optimized Page"}
                }
            }
        }
        
        result = advanced_converter.convert(social_manifest)
        
        html_content = result.content
        assert '<meta property="og:title"' in html_content
        assert '<meta property="og:description"' in html_content
        assert '<meta property="og:image"' in html_content
        assert '<meta name="twitter:card"' in html_content
        assert '<meta name="twitter:site"' in html_content
    
    def test_performance_optimization(self, advanced_converter):
        """Test performance optimization features."""
        performance_manifest = {
            "metadata": {"title": "Performance Optimized Page"},
            "structure": {
                "html": {
                    "body": {
                        "div": {"content": "Optimized content"},
                        "img": {
                            "src": "image.jpg",
                            "alt": "Optimized image",
                            "loading": "lazy",
                            "decoding": "async"
                        }
                    }
                }
            },
            "styles": {
                "css": """
                .optimized { font-display: swap; }
                """
            }
        }
        
        result = advanced_converter.convert(performance_manifest)
        
        html_content = result.content
        assert 'loading="lazy"' in html_content
        assert 'decoding="async"' in html_content
        assert 'font-display: swap' in html_content


if __name__ == "__main__":
    pytest.main([__file__])
