"""
Test cases for all format converters

Tests for HTML, React, Vue, and PHP converters including
conversion accuracy, output validation, and edge cases.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import tempfile
import os
from pathlib import Path

from whyml.converters import (
    HTMLConverter, ReactConverter, VueConverter, PHPConverter,
    BaseConverter, ConversionResult
)
from whyml.exceptions import ConversionError, ValidationError


class TestBaseConverter:
    """Test cases for BaseConverter abstract functionality."""
    
    def test_conversion_result_creation(self):
        """Test ConversionResult creation and properties."""
        result = ConversionResult(
            content="<div>Test</div>",
            filename="test.html",
            format_type="html",
            metadata={"component_count": 1}
        )
        
        assert result.content == "<div>Test</div>"
        assert result.filename == "test.html"
        assert result.format_type == "html"
        assert result.metadata["component_count"] == 1
    
    def test_conversion_result_save(self):
        """Test saving ConversionResult to file."""
        result = ConversionResult(
            content="<div>Test Content</div>",
            filename="test.html",
            format_type="html"
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.html"
            result.save_to_file(str(output_path))
            
            assert output_path.exists()
            assert output_path.read_text() == "<div>Test Content</div>"


class TestHTMLConverter:
    """Test cases for HTML converter."""
    
    @pytest.fixture
    def html_converter(self):
        """Create HTMLConverter instance for testing."""
        return HTMLConverter(
            optimize_output=True,
            include_meta_tags=True,
            css_framework='bootstrap'
        )
    
    @pytest.fixture
    def sample_manifest(self):
        """Sample manifest for testing."""
        return {
            'metadata': {
                'title': 'Test Page',
                'description': 'A test page for HTML conversion',
                'version': '1.0.0'
            },
            'styles': {
                'container': 'width: 100%; max-width: 1200px; margin: 0 auto;',
                'header': 'background: #007bff; color: white; padding: 20px;',
                'content': 'padding: 20px; line-height: 1.6;'
            },
            'structure': {
                'div': {
                    'class': 'container',
                    'children': [
                        {
                            'header': {
                                'class': 'header',
                                'children': {
                                    'h1': {'text': 'Test Page'}
                                }
                            }
                        },
                        {
                            'main': {
                                'class': 'content',
                                'children': [
                                    {'p': {'text': 'This is test content.'}},
                                    {'p': {'text': 'Another paragraph.'}}
                                ]
                            }
                        }
                    ]
                }
            }
        }
    
    def test_basic_html_conversion(self, html_converter, sample_manifest):
        """Test basic HTML conversion."""
        result = html_converter.convert(sample_manifest)
        
        assert isinstance(result, ConversionResult)
        assert result.format_type == 'html'
        assert result.filename.endswith('.html')
        
        # Check HTML structure
        html_content = result.content
        assert '<!DOCTYPE html>' in html_content
        assert '<html' in html_content
        assert '<head>' in html_content
        assert '<body>' in html_content
        assert '<title>Test Page</title>' in html_content
    
    def test_meta_tags_generation(self, html_converter, sample_manifest):
        """Test meta tags generation."""
        result = html_converter.convert(sample_manifest)
        html_content = result.content
        
        assert '<meta name="description" content="A test page for HTML conversion">' in html_content
        assert '<meta name="viewport"' in html_content
        assert '<meta charset="utf-8">' in html_content
    
    def test_css_integration(self, html_converter, sample_manifest):
        """Test CSS styles integration."""
        result = html_converter.convert(sample_manifest)
        html_content = result.content
        
        # Check that styles are included
        assert '.container' in html_content
        assert 'width: 100%' in html_content
        assert '.header' in html_content
        assert 'background: #007bff' in html_content
    
    def test_structure_conversion(self, html_converter, sample_manifest):
        """Test HTML structure conversion."""
        result = html_converter.convert(sample_manifest)
        html_content = result.content
        
        # Check structural elements
        assert '<div class="container">' in html_content
        assert '<header class="header">' in html_content
        assert '<main class="content">' in html_content
        assert '<h1>Test Page</h1>' in html_content
        assert '<p>This is test content.</p>' in html_content
    
    def test_bootstrap_integration(self):
        """Test Bootstrap CSS framework integration."""
        converter = HTMLConverter(css_framework='bootstrap')
        manifest = {
            'metadata': {'title': 'Bootstrap Test'},
            'structure': {'div': {'class': 'container', 'text': 'Content'}}
        }
        
        result = converter.convert(manifest)
        html_content = result.content
        
        # Should include Bootstrap CDN link
        assert 'bootstrap' in html_content.lower()
    
    def test_semantic_html_generation(self, html_converter):
        """Test semantic HTML5 element generation."""
        manifest = {
            'metadata': {'title': 'Semantic Test'},
            'structure': {
                'div': {
                    'children': [
                        {'header': {'text': 'Header'}},
                        {'nav': {'text': 'Navigation'}},
                        {'main': {'text': 'Main content'}},
                        {'aside': {'text': 'Sidebar'}},
                        {'footer': {'text': 'Footer'}}
                    ]
                }
            }
        }
        
        result = html_converter.convert(manifest)
        html_content = result.content
        
        assert '<header>' in html_content
        assert '<nav>' in html_content
        assert '<main>' in html_content
        assert '<aside>' in html_content
        assert '<footer>' in html_content


class TestReactConverter:
    """Test cases for React converter."""
    
    @pytest.fixture
    def react_converter(self):
        """Create ReactConverter instance for testing."""
        return ReactConverter(
            use_typescript=True,
            css_framework='tailwind',
            component_type='functional'
        )
    
    @pytest.fixture
    def sample_manifest(self):
        """Sample manifest for React testing."""
        return {
            'metadata': {
                'title': 'TestComponent',
                'description': 'A test React component'
            },
            'styles': {
                'container': 'flex flex-col items-center p-4',
                'button': 'bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600'
            },
            'interactions': {
                'button_click': 'handleButtonClick',
                'form_submit': 'handleFormSubmit'
            },
            'structure': {
                'div': {
                    'class': 'container',
                    'children': [
                        {'h1': {'text': 'Hello React'}},
                        {'button': {'class': 'button', 'text': 'Click me', 'onClick': 'button_click'}}
                    ]
                }
            }
        }
    
    def test_basic_react_conversion(self, react_converter, sample_manifest):
        """Test basic React component conversion."""
        result = react_converter.convert(sample_manifest)
        
        assert isinstance(result, ConversionResult)
        assert result.format_type == 'react'
        assert result.filename.endswith('.tsx')
        
        jsx_content = result.content
        assert 'import React' in jsx_content
        assert 'const TestComponent' in jsx_content
        assert 'export default TestComponent' in jsx_content
    
    def test_typescript_generation(self, react_converter, sample_manifest):
        """Test TypeScript interface generation."""
        result = react_converter.convert(sample_manifest)
        jsx_content = result.content
        
        # Check TypeScript features
        assert 'interface' in jsx_content or 'type' in jsx_content
        assert ': React.FC' in jsx_content or ': FC' in jsx_content
    
    def test_event_handlers_generation(self, react_converter, sample_manifest):
        """Test event handler generation."""
        result = react_converter.convert(sample_manifest)
        jsx_content = result.content
        
        assert 'handleButtonClick' in jsx_content
        assert 'onClick={handleButtonClick}' in jsx_content
    
    def test_css_modules_integration(self):
        """Test CSS modules integration."""
        converter = ReactConverter(use_css_modules=True)
        manifest = {
            'metadata': {'title': 'CSSModuleTest'},
            'styles': {'container': 'padding: 20px;'},
            'structure': {'div': {'class': 'container', 'text': 'Content'}}
        }
        
        result = converter.convert(manifest)
        jsx_content = result.content
        
        assert 'import styles from' in jsx_content
        assert 'className={styles.container}' in jsx_content
    
    def test_hooks_generation(self, react_converter):
        """Test React hooks generation."""
        manifest = {
            'metadata': {'title': 'HooksTest'},
            'interactions': {
                'state_counter': 'useState(0)',
                'effect_mount': 'useEffect(() => {}, [])'
            },
            'structure': {'div': {'text': 'Component with hooks'}}
        }
        
        result = react_converter.convert(manifest)
        jsx_content = result.content
        
        assert 'useState' in jsx_content
        assert 'useEffect' in jsx_content


class TestVueConverter:
    """Test cases for Vue converter."""
    
    @pytest.fixture
    def vue_converter(self):
        """Create VueConverter instance for testing."""
        return VueConverter(
            vue_version='3',
            use_typescript=True,
            use_composition_api=True
        )
    
    @pytest.fixture
    def sample_manifest(self):
        """Sample manifest for Vue testing."""
        return {
            'metadata': {
                'title': 'TestComponent',
                'description': 'A test Vue component'
            },
            'styles': {
                'container': 'padding: 20px; background: #f5f5f5;',
                'button': 'background: #42b883; color: white; padding: 10px 20px;'
            },
            'interactions': {
                'data_count': 'ref(0)',
                'method_increment': 'count.value++'
            },
            'structure': {
                'div': {
                    'class': 'container',
                    'children': [
                        {'h1': {'text': '{{ title }}'}},
                        {'p': {'text': 'Count: {{ count }}'}},
                        {'button': {'class': 'button', 'text': 'Increment', '@click': 'increment'}}
                    ]
                }
            }
        }
    
    def test_basic_vue_conversion(self, vue_converter, sample_manifest):
        """Test basic Vue SFC conversion."""
        result = vue_converter.convert(sample_manifest)
        
        assert isinstance(result, ConversionResult)
        assert result.format_type == 'vue'
        assert result.filename.endswith('.vue')
        
        vue_content = result.content
        assert '<template>' in vue_content
        assert '<script' in vue_content
        assert '<style' in vue_content
    
    def test_composition_api_generation(self, vue_converter, sample_manifest):
        """Test Composition API generation."""
        result = vue_converter.convert(sample_manifest)
        vue_content = result.content
        
        assert 'import { ref' in vue_content
        assert 'setup()' in vue_content
        assert 'return {' in vue_content
    
    def test_scoped_styles_generation(self, vue_converter, sample_manifest):
        """Test scoped styles generation."""
        result = vue_converter.convert(sample_manifest)
        vue_content = result.content
        
        assert '<style scoped>' in vue_content
        assert '.container' in vue_content
        assert 'padding: 20px' in vue_content
    
    def test_vue_directives_generation(self, vue_converter, sample_manifest):
        """Test Vue directives generation."""
        result = vue_converter.convert(sample_manifest)
        vue_content = result.content
        
        assert '@click=' in vue_content
        assert '{{' in vue_content and '}}' in vue_content  # Template interpolation


class TestPHPConverter:
    """Test cases for PHP converter."""
    
    @pytest.fixture
    def php_converter(self):
        """Create PHPConverter instance for testing."""
        return PHPConverter(
            php_version='8.1',
            namespace='App\\Components',
            use_type_declarations=True
        )
    
    @pytest.fixture
    def sample_manifest(self):
        """Sample manifest for PHP testing."""
        return {
            'metadata': {
                'title': 'TestComponent',
                'description': 'A test PHP component'
            },
            'styles': {
                'container': 'width: 100%; padding: 20px;',
                'header': 'font-size: 24px; font-weight: bold;'
            },
            'structure': {
                'div': {
                    'class': 'container',
                    'children': [
                        {'h1': {'class': 'header', 'text': 'PHP Component'}},
                        {'p': {'text': 'Generated from YAML manifest'}}
                    ]
                }
            }
        }
    
    def test_basic_php_conversion(self, php_converter, sample_manifest):
        """Test basic PHP class conversion."""
        result = php_converter.convert(sample_manifest)
        
        assert isinstance(result, ConversionResult)
        assert result.format_type == 'php'
        assert result.filename.endswith('.php')
        
        php_content = result.content
        assert '<?php' in php_content
        assert 'namespace App\\Components;' in php_content
        assert 'class TestComponentComponent' in php_content
    
    def test_type_declarations(self, php_converter, sample_manifest):
        """Test PHP type declarations."""
        result = php_converter.convert(sample_manifest)
        php_content = result.content
        
        assert 'array $data' in php_content
        assert 'string' in php_content
        assert ': void' in php_content or ': string' in php_content
    
    def test_render_method_generation(self, php_converter, sample_manifest):
        """Test render method generation."""
        result = php_converter.convert(sample_manifest)
        php_content = result.content
        
        assert 'public function render()' in php_content
        assert '$html' in php_content
        assert 'return $html;' in php_content
    
    def test_html_escaping(self, php_converter):
        """Test HTML escaping in generated PHP."""
        manifest = {
            'metadata': {'title': 'EscapeTest'},
            'structure': {
                'div': {
                    'text': '<script>alert("XSS")</script>'
                }
            }
        }
        
        result = php_converter.convert(manifest)
        php_content = result.content
        
        assert 'escapeHtml' in php_content
        assert 'htmlspecialchars' in php_content


class TestConverterIntegration:
    """Integration tests for all converters."""
    
    @pytest.fixture
    def complex_manifest(self):
        """Complex manifest for integration testing."""
        return {
            'metadata': {
                'title': 'ComplexComponent',
                'description': 'A complex component for testing',
                'version': '2.0.0',
                'author': 'Test Suite'
            },
            'template_vars': {
                'primary_color': '#007bff',
                'secondary_color': '#6c757d',
                'border_radius': '8px'
            },
            'styles': {
                'container': 'background: {{ primary_color }}; border-radius: {{ border_radius }};',
                'text': 'color: {{ secondary_color }}; font-size: 16px;',
                'button': 'padding: 10px 20px; border: none; border-radius: {{ border_radius }};'
            },
            'imports': [
                'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css'
            ],
            'interactions': {
                'onClick': 'handleClick',
                'onSubmit': 'handleSubmit',
                'state_visible': 'true'
            },
            'structure': {
                'div': {
                    'class': 'container',
                    'children': [
                        {
                            'header': {
                                'children': {
                                    'h1': {'class': 'text', 'text': '{{ title }}'},
                                    'p': {'text': '{{ description }}'}
                                }
                            }
                        },
                        {
                            'main': {
                                'children': [
                                    {
                                        'form': {
                                            'onSubmit': 'onSubmit',
                                            'children': [
                                                {'input': {'type': 'text', 'placeholder': 'Enter text'}},
                                                {'button': {'class': 'button', 'text': 'Submit', 'onClick': 'onClick'}}
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
    
    def test_all_converters_with_complex_manifest(self, complex_manifest):
        """Test all converters with a complex manifest."""
        converters = [
            HTMLConverter(),
            ReactConverter(),
            VueConverter(),
            PHPConverter()
        ]
        
        results = []
        for converter in converters:
            try:
                result = converter.convert(complex_manifest)
                assert isinstance(result, ConversionResult)
                assert len(result.content) > 100  # Substantial content
                results.append(result)
            except Exception as e:
                pytest.fail(f"Converter {converter.__class__.__name__} failed: {e}")
        
        # Check that all converters produced results
        assert len(results) == 4
        
        # Check unique file extensions
        extensions = [result.filename.split('.')[-1] for result in results]
        assert 'html' in extensions
        assert 'tsx' in extensions or 'jsx' in extensions
        assert 'vue' in extensions
        assert 'php' in extensions
    
    def test_conversion_consistency(self, complex_manifest):
        """Test that all converters produce consistent structural elements."""
        converters = [
            HTMLConverter(),
            ReactConverter(), 
            VueConverter(),
            PHPConverter()
        ]
        
        # Elements that should appear in all conversions
        expected_elements = ['container', 'header', 'main', 'form', 'input', 'button']
        
        for converter in converters:
            result = converter.convert(complex_manifest)
            content = result.content.lower()
            
            # Check that structural elements are present
            for element in expected_elements:
                assert element in content, f"Element '{element}' missing from {converter.__class__.__name__} output"
    
    def test_output_file_saving(self, complex_manifest):
        """Test saving converted outputs to files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            converters = [
                ('html', HTMLConverter()),
                ('react', ReactConverter()),
                ('vue', VueConverter()),
                ('php', PHPConverter())
            ]
            
            for name, converter in converters:
                result = converter.convert(complex_manifest)
                output_path = Path(temp_dir) / f"test_component.{result.filename.split('.')[-1]}"
                result.save_to_file(str(output_path))
                
                assert output_path.exists()
                assert output_path.stat().st_size > 0
                
                # Verify content was written correctly
                saved_content = output_path.read_text()
                assert saved_content == result.content


if __name__ == '__main__':
    pytest.main([__file__])
