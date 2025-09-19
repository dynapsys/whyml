"""
Integration tests for WhyML package

End-to-end tests covering complete workflows from manifest loading
through processing to conversion across all supported formats.

Copyright 2024 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
import yaml
from unittest.mock import patch, AsyncMock

from whyml import WhyMLProcessor
from whyml.manifest_loader import ManifestLoader
from whyml.manifest_processor import ManifestProcessor
from whyml.converters import HTMLConverter, ReactConverter, VueConverter, PHPConverter
from whyml.scrapers import URLScraper, WebpageAnalyzer
from whyml.exceptions import WhyMLError


class TestEndToEndWorkflows:
    """End-to-end workflow tests."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with manifests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create project structure
            manifests_dir = project_path / 'manifests'
            output_dir = project_path / 'output'
            manifests_dir.mkdir()
            output_dir.mkdir()
            
            # Base component manifest
            base_component = {
                'metadata': {
                    'title': 'BaseComponent',
                    'version': '1.0.0',
                    'description': 'Base component for inheritance',
                    'author': 'WhyML Test Suite'
                },
                'template_vars': {
                    'primary_color': '#007bff',
                    'secondary_color': '#6c757d',
                    'font_family': 'Arial, sans-serif',
                    'border_radius': '8px'
                },
                'styles': {
                    'base': 'font-family: {{ font_family }}; color: {{ secondary_color }};',
                    'container': 'width: 100%; max-width: 1200px; margin: 0 auto;',
                    'button': 'background: {{ primary_color }}; border-radius: {{ border_radius }}; border: none; padding: 10px 20px; color: white;'
                },
                'structure': {
                    'div': {
                        'class': 'container',
                        'children': {
                            'header': {
                                'class': 'base',
                                'children': {
                                    'h1': {'text': '{{ title }}'}
                                }
                            }
                        }
                    }
                }
            }
            
            # Landing page component
            landing_page = {
                'extends': './base-component.yaml',
                'metadata': {
                    'title': 'Landing Page',
                    'description': 'Modern landing page component',
                    'keywords': ['landing', 'marketing', 'conversion']
                },
                'template_vars': {
                    'hero_text': 'Welcome to Our Amazing Product',
                    'cta_text': 'Get Started Now',
                    'features_count': '3'
                },
                'styles': {
                    'hero': 'background: linear-gradient(135deg, {{ primary_color }}, #0056b3); padding: 80px 0; text-align: center; color: white;',
                    'hero_title': 'font-size: 3rem; font-weight: bold; margin-bottom: 20px;',
                    'cta_button': 'background: #28a745; font-size: 1.2rem; padding: 15px 30px; border-radius: {{ border_radius }};',
                    'features': 'display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; padding: 60px 0;',
                    'feature_card': 'background: #f8f9fa; padding: 30px; border-radius: {{ border_radius }}; text-align: center;'
                },
                'interactions': {
                    'cta_click': 'handleCTAClick',
                    'feature_hover': 'handleFeatureHover',
                    'scroll_tracking': 'trackScrollPosition'
                },
                'structure': {
                    'div': {
                        'class': 'container',
                        'children': [
                            {
                                'section': {
                                    'class': 'hero',
                                    'children': [
                                        {
                                            'h1': {
                                                'class': 'hero_title',
                                                'text': '{{ hero_text }}'
                                            }
                                        },
                                        {
                                            'p': {
                                                'text': '{{ description }}'
                                            }
                                        },
                                        {
                                            'button': {
                                                'class': 'cta_button',
                                                'text': '{{ cta_text }}',
                                                'onClick': 'cta_click'
                                            }
                                        }
                                    ]
                                }
                            },
                            {
                                'section': {
                                    'class': 'features',
                                    'children': [
                                        {
                                            'div': {
                                                'class': 'feature_card',
                                                'onMouseEnter': 'feature_hover',
                                                'children': [
                                                    {'h3': {'text': 'Fast Performance'}},
                                                    {'p': {'text': 'Lightning-fast load times and optimized performance.'}}
                                                ]
                                            }
                                        },
                                        {
                                            'div': {
                                                'class': 'feature_card',
                                                'onMouseEnter': 'feature_hover',
                                                'children': [
                                                    {'h3': {'text': 'Easy Integration'}},
                                                    {'p': {'text': 'Simple setup and seamless integration with your workflow.'}}
                                                ]
                                            }
                                        },
                                        {
                                            'div': {
                                                'class': 'feature_card',
                                                'onMouseEnter': 'feature_hover',
                                                'children': [
                                                    {'h3': {'text': 'Scalable Solution'}},
                                                    {'p': {'text': 'Grows with your business and handles increasing demands.'}}
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
            
            # Blog post component
            blog_post = {
                'metadata': {
                    'title': 'Blog Post',
                    'description': 'Responsive blog post component',
                    'version': '1.2.0'
                },
                'template_vars': {
                    'post_title': 'Understanding Modern Web Development',
                    'post_author': 'John Doe',
                    'post_date': '2024-01-15',
                    'reading_time': '5 min read'
                },
                'styles': {
                    'article': 'max-width: 800px; margin: 0 auto; padding: 40px 20px; line-height: 1.8;',
                    'article_header': 'margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px;',
                    'post_title': 'font-size: 2.5rem; font-weight: bold; margin-bottom: 15px; color: #333;',
                    'post_meta': 'color: #666; font-size: 0.9rem; display: flex; gap: 20px;',
                    'post_content': 'font-size: 1.1rem; color: #444;',
                    'paragraph': 'margin-bottom: 20px;',
                    'code_block': 'background: #f4f4f4; padding: 20px; border-radius: 5px; font-family: monospace; overflow-x: auto;'
                },
                'structure': {
                    'article': {
                        'class': 'article',
                        'children': [
                            {
                                'header': {
                                    'class': 'article_header',
                                    'children': [
                                        {
                                            'h1': {
                                                'class': 'post_title',
                                                'text': '{{ post_title }}'
                                            }
                                        },
                                        {
                                            'div': {
                                                'class': 'post_meta',
                                                'children': [
                                                    {'span': {'text': 'By {{ post_author }}'}},
                                                    {'span': {'text': '{{ post_date }}'}},
                                                    {'span': {'text': '{{ reading_time }}'}}
                                                ]
                                            }
                                        }
                                    ]
                                }
                            },
                            {
                                'div': {
                                    'class': 'post_content',
                                    'children': [
                                        {
                                            'p': {
                                                'class': 'paragraph',
                                                'text': 'Modern web development has evolved significantly over the past decade. From simple static websites to complex, interactive applications, the landscape continues to change rapidly.'
                                            }
                                        },
                                        {
                                            'p': {
                                                'class': 'paragraph',
                                                'text': 'In this article, we will explore the key trends, tools, and methodologies that are shaping the future of web development.'
                                            }
                                        },
                                        {
                                            'pre': {
                                                'class': 'code_block',
                                                'children': {
                                                    'code': {
                                                        'text': 'const modernFramework = {\n  performance: "optimized",\n  developer_experience: "enhanced",\n  scalability: "built-in"\n};'
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
            
            # Write manifest files
            (manifests_dir / 'base-component.yaml').write_text(yaml.dump(base_component))
            (manifests_dir / 'landing-page.yaml').write_text(yaml.dump(landing_page))
            (manifests_dir / 'blog-post.yaml').write_text(yaml.dump(blog_post))
            
            yield {
                'project_path': project_path,
                'manifests_dir': manifests_dir,
                'output_dir': output_dir
            }
    
    @pytest.mark.asyncio
    async def test_complete_manifest_to_html_workflow(self, temp_project_dir):
        """Test complete workflow from manifest loading to HTML generation."""
        manifests_dir = temp_project_dir['manifests_dir']
        output_dir = temp_project_dir['output_dir']
        
        # Load and process manifest
        loader = ManifestLoader()
        processor = ManifestProcessor()
        converter = HTMLConverter(optimize_output=True, include_meta_tags=True)
        
        async with loader:
            # Load landing page manifest (with inheritance)
            raw_manifest = await loader.load_manifest(str(manifests_dir / 'landing-page.yaml'))
            
            # Process manifest
            processed_manifest = processor.process_manifest(raw_manifest)
            
            # Convert to HTML
            result = converter.convert(processed_manifest)
            
            # Save result
            output_file = output_dir / result.filename
            result.save_to_file(str(output_file))
            
            # Verify results
            assert output_file.exists()
            html_content = output_file.read_text()
            
            # Check HTML structure
            assert '<!DOCTYPE html>' in html_content
            assert '<title>Landing Page</title>' in html_content
            assert 'Welcome to Our Amazing Product' in html_content
            assert 'Get Started Now' in html_content
            assert 'Fast Performance' in html_content
            
            # Check CSS integration
            assert '.hero' in html_content
            assert '.cta_button' in html_content
            assert '.features' in html_content
            assert 'background: linear-gradient' in html_content
    
    @pytest.mark.asyncio
    async def test_complete_manifest_to_react_workflow(self, temp_project_dir):
        """Test complete workflow from manifest loading to React generation."""
        manifests_dir = temp_project_dir['manifests_dir']
        output_dir = temp_project_dir['output_dir']
        
        loader = ManifestLoader()
        processor = ManifestProcessor()
        converter = ReactConverter(use_typescript=True, component_type='functional')
        
        async with loader:
            # Load blog post manifest
            raw_manifest = await loader.load_manifest(str(manifests_dir / 'blog-post.yaml'))
            
            # Process manifest
            processed_manifest = processor.process_manifest(raw_manifest)
            
            # Convert to React
            result = converter.convert(processed_manifest)
            
            # Save result
            output_file = output_dir / result.filename
            result.save_to_file(str(output_file))
            
            # Verify results
            assert output_file.exists()
            react_content = output_file.read_text()
            
            # Check React structure
            assert 'import React' in react_content
            assert 'const BlogPost' in react_content or 'function BlogPost' in react_content
            assert 'export default' in react_content
            
            # Check component content
            assert 'Understanding Modern Web Development' in react_content
            assert 'John Doe' in react_content
            assert 'article' in react_content.lower()
    
    @pytest.mark.asyncio
    async def test_complete_manifest_to_vue_workflow(self, temp_project_dir):
        """Test complete workflow from manifest loading to Vue generation."""
        manifests_dir = temp_project_dir['manifests_dir']
        output_dir = temp_project_dir['output_dir']
        
        loader = ManifestLoader()
        processor = ManifestProcessor()
        converter = VueConverter(vue_version='3', use_composition_api=True)
        
        async with loader:
            # Load landing page manifest
            raw_manifest = await loader.load_manifest(str(manifests_dir / 'landing-page.yaml'))
            
            # Process manifest
            processed_manifest = processor.process_manifest(raw_manifest)
            
            # Convert to Vue
            result = converter.convert(processed_manifest)
            
            # Save result
            output_file = output_dir / result.filename
            result.save_to_file(str(output_file))
            
            # Verify results
            assert output_file.exists()
            vue_content = output_file.read_text()
            
            # Check Vue SFC structure
            assert '<template>' in vue_content
            assert '<script' in vue_content
            assert '<style' in vue_content
            
            # Check component content
            assert 'Welcome to Our Amazing Product' in vue_content
            assert 'handleCTAClick' in vue_content
    
    @pytest.mark.asyncio
    async def test_complete_manifest_to_php_workflow(self, temp_project_dir):
        """Test complete workflow from manifest loading to PHP generation."""
        manifests_dir = temp_project_dir['manifests_dir']
        output_dir = temp_project_dir['output_dir']
        
        loader = ManifestLoader()
        processor = ManifestProcessor()
        converter = PHPConverter(namespace='App\\Components', use_type_declarations=True)
        
        async with loader:
            # Load blog post manifest
            raw_manifest = await loader.load_manifest(str(manifests_dir / 'blog-post.yaml'))
            
            # Process manifest
            processed_manifest = processor.process_manifest(raw_manifest)
            
            # Convert to PHP
            result = converter.convert(processed_manifest)
            
            # Save result
            output_file = output_dir / result.filename
            result.save_to_file(str(output_file))
            
            # Verify results
            assert output_file.exists()
            php_content = output_file.read_text()
            
            # Check PHP structure
            assert '<?php' in php_content
            assert 'namespace App\\Components;' in php_content
            assert 'class BlogPostComponent' in php_content
            assert 'public function render()' in php_content
            
            # Check component content
            assert 'Understanding Modern Web Development' in php_content
            assert 'escapeHtml' in php_content
    
    @pytest.mark.asyncio
    async def test_multi_format_conversion_workflow(self, temp_project_dir):
        """Test converting single manifest to multiple formats."""
        manifests_dir = temp_project_dir['manifests_dir']
        output_dir = temp_project_dir['output_dir']
        
        loader = ManifestLoader()
        processor = ManifestProcessor()
        
        converters = [
            ('html', HTMLConverter()),
            ('react', ReactConverter()),
            ('vue', VueConverter()),
            ('php', PHPConverter())
        ]
        
        async with loader:
            # Load base component manifest
            raw_manifest = await loader.load_manifest(str(manifests_dir / 'base-component.yaml'))
            
            # Process once
            processed_manifest = processor.process_manifest(raw_manifest)
            
            # Convert to all formats
            results = []
            for format_name, converter in converters:
                result = converter.convert(processed_manifest)
                
                # Save to format-specific subdirectory
                format_dir = output_dir / format_name
                format_dir.mkdir(exist_ok=True)
                output_file = format_dir / result.filename
                result.save_to_file(str(output_file))
                
                results.append((format_name, result, output_file))
            
            # Verify all conversions
            assert len(results) == 4
            
            for format_name, result, output_file in results:
                assert output_file.exists()
                assert output_file.stat().st_size > 0
                
                content = output_file.read_text()
                assert 'BaseComponent' in content
                
                # Format-specific checks
                if format_name == 'html':
                    assert '<!DOCTYPE html>' in content
                elif format_name == 'react':
                    assert 'import React' in content
                elif format_name == 'vue':
                    assert '<template>' in content
                elif format_name == 'php':
                    assert '<?php' in content
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_url_scraping_to_conversion_workflow(self, mock_get, temp_project_dir):
        """Test complete workflow from URL scraping to format conversion."""
        output_dir = temp_project_dir['output_dir']
        
        # Mock HTML response
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Scraped Page</title>
            <meta name="description" content="A page scraped for testing">
            <style>
                .header { background: #007bff; color: white; padding: 20px; }
                .content { padding: 20px; }
            </style>
        </head>
        <body>
            <header class="header">
                <h1>Scraped Website</h1>
            </header>
            <main class="content">
                <p>This content was scraped from a website.</p>
            </main>
        </body>
        </html>
        """
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = AsyncMock(return_value=sample_html)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Scrape URL and convert
        scraper = URLScraper()
        processor = ManifestProcessor()
        converter = HTMLConverter()
        
        async with scraper:
            # Scrape website to manifest
            scraped_manifest = await scraper.scrape_url('https://example.com')
            
            # Clean and optimize manifest
            cleaned_manifest = scraper.clean_manifest(scraped_manifest)
            
            # Process manifest
            processed_manifest = processor.process_manifest(cleaned_manifest)
            
            # Convert back to HTML (cleaned version)
            result = converter.convert(processed_manifest)
            
            # Save result
            output_file = output_dir / 'scraped_converted.html'
            result.save_to_file(str(output_file))
            
            # Verify workflow
            assert output_file.exists()
            html_content = output_file.read_text()
            
            assert 'Scraped Page' in html_content
            assert 'Scraped Website' in html_content
            assert 'scraped from a website' in html_content
    
    def test_error_handling_in_workflows(self, temp_project_dir):
        """Test error handling throughout complete workflows."""
        manifests_dir = temp_project_dir['manifests_dir']
        
        # Create invalid manifest
        invalid_manifest = "invalid: yaml: content: ["
        invalid_file = manifests_dir / 'invalid.yaml'
        invalid_file.write_text(invalid_manifest)
        
        # Test error propagation
        with pytest.raises(WhyMLError):
            loader = ManifestLoader()
            asyncio.run(loader.load_manifest(str(invalid_file)))
    
    @pytest.mark.asyncio
    async def test_performance_with_large_project(self, temp_project_dir):
        """Test performance with larger project structures."""
        manifests_dir = temp_project_dir['manifests_dir']
        output_dir = temp_project_dir['output_dir']
        
        # Create multiple interconnected manifests
        for i in range(10):
            manifest = {
                'metadata': {
                    'title': f'Component {i}',
                    'version': '1.0.0'
                },
                'styles': {
                    f'component_{i}': f'color: hsl({i * 36}, 70%, 50%);'
                },
                'structure': {
                    'div': {
                        'class': f'component_{i}',
                        'text': f'Component {i} content'
                    }
                }
            }
            
            if i > 0:
                manifest['extends'] = f'./component_{i-1}.yaml'
            
            (manifests_dir / f'component_{i}.yaml').write_text(yaml.dump(manifest))
        
        # Test loading and converting all components
        loader = ManifestLoader()
        processor = ManifestProcessor()
        converter = HTMLConverter()
        
        import time
        start_time = time.time()
        
        async with loader:
            for i in range(10):
                manifest_file = manifests_dir / f'component_{i}.yaml'
                raw_manifest = await loader.load_manifest(str(manifest_file))
                processed_manifest = processor.process_manifest(raw_manifest)
                result = converter.convert(processed_manifest)
                
                output_file = output_dir / f'component_{i}.html'
                result.save_to_file(str(output_file))
        
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 5.0  # Less than 5 seconds
        
        # Verify all files were created
        for i in range(10):
            output_file = output_dir / f'component_{i}.html'
            assert output_file.exists()


class TestWhyMLProcessorIntegration:
    """Test the main WhyMLProcessor class integration."""
    
    def test_whyml_processor_initialization(self):
        """Test WhyMLProcessor initialization."""
        processor = WhyMLProcessor(
            cache_size=200,
            enable_validation=True,
            optimize_output=True
        )
        
        assert processor is not None
        assert hasattr(processor, 'loader')
        assert hasattr(processor, 'processor')
    
    @pytest.mark.asyncio
    async def test_whyml_processor_load_and_convert(self, temp_project_dir):
        """Test WhyMLProcessor load and convert workflow."""
        manifests_dir = temp_project_dir['manifests_dir']
        
        processor = WhyMLProcessor()
        
        # Load and convert to multiple formats
        manifest_path = str(manifests_dir / 'landing-page.yaml')
        
        # Convert to HTML
        html_result = await processor.convert_to_html(manifest_path)
        assert html_result is not None
        assert 'Landing Page' in html_result.content
        
        # Convert to React
        react_result = await processor.convert_to_react(manifest_path)
        assert react_result is not None
        assert 'React' in react_result.content or 'import' in react_result.content
        
        # Convert to Vue
        vue_result = await processor.convert_to_vue(manifest_path)
        assert vue_result is not None
        assert '<template>' in vue_result.content
        
        # Convert to PHP
        php_result = await processor.convert_to_php(manifest_path)
        assert php_result is not None
        assert '<?php' in php_result.content


if __name__ == '__main__':
    pytest.main([__file__])
