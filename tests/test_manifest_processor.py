"""
Test cases for ManifestProcessor

Tests for manifest validation, template inheritance processing,
style processing, and manifest transformation pipeline.

Copyright 2024 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import yaml

from whyml.manifest_processor import ManifestProcessor
from whyml.exceptions import (
    ManifestProcessingError, TemplateInheritanceError,
    ValidationError, ConfigurationError
)


class TestManifestProcessor:
    """Test cases for ManifestProcessor functionality."""
    
    @pytest.fixture
    def processor(self):
        """Create a ManifestProcessor instance for testing."""
        return ManifestProcessor()
    
    @pytest.fixture
    def sample_manifest(self):
        """Create a sample manifest for testing."""
        return {
            'metadata': {
                'title': 'Test Component',
                'version': '1.0.0',
                'description': 'A test component'
            },
            'template_vars': {
                'primary_color': '#007bff',
                'secondary_color': '#6c757d',
                'font_size': '16px'
            },
            'styles': {
                'container': 'width: 100%; background: {{ primary_color }};',
                'text': 'font-size: {{ font_size }}; color: {{ secondary_color }};'
            },
            'structure': {
                'div': {
                    'class': 'container',
                    'children': {
                        'h1': {
                            'class': 'text',
                            'text': '{{ title }}'
                        },
                        'p': {
                            'text': '{{ description }}'
                        }
                    }
                }
            }
        }
    
    @pytest.fixture
    def inheritance_manifests(self):
        """Create base and child manifests for inheritance testing."""
        base = {
            'metadata': {
                'title': 'Base Component',
                'version': '1.0.0'
            },
            'template_vars': {
                'base_color': '#ffffff'
            },
            'styles': {
                'base': 'background: {{ base_color }};',
                'container': 'width: 100%;'
            },
            'structure': {
                'div': {
                    'class': 'base container',
                    'text': '{{ title }}'
                }
            }
        }
        
        child = {
            'metadata': {
                'title': 'Child Component',
                'description': 'Extends base component'
            },
            'template_vars': {
                'child_color': '#000000'
            },
            'styles': {
                'child': 'color: {{ child_color }};',
                'container': 'width: 100%; padding: 20px;'  # Override
            },
            'structure': {
                'div': {
                    'class': 'base container child',
                    'children': [
                        {'h1': {'text': '{{ title }}'}},
                        {'p': {'text': '{{ description }}'}}
                    ]
                }
            }
        }
        
        return base, child
    
    def test_process_basic_manifest(self, processor, sample_manifest):
        """Test processing a basic manifest."""
        result = processor.process_manifest(sample_manifest)
        
        assert result is not None
        assert 'metadata' in result
        assert 'styles' in result
        assert 'structure' in result
        assert result['metadata']['title'] == 'Test Component'
    
    def test_template_variable_substitution(self, processor, sample_manifest):
        """Test template variable substitution in styles and structure."""
        result = processor.process_manifest(sample_manifest)
        
        # Check style template substitution
        assert '#007bff' in result['styles']['container']
        assert '16px' in result['styles']['text']
        assert '#6c757d' in result['styles']['text']
        
        # Check structure template substitution
        structure = result['structure']
        h1_text = structure['div']['children']['h1']['text']
        p_text = structure['div']['children']['p']['text']
        
        assert h1_text == 'Test Component'
        assert p_text == 'A test component'
    
    def test_template_inheritance_merge(self, processor, inheritance_manifests):
        """Test template inheritance merging."""
        base, child = inheritance_manifests
        
        result = processor.merge_manifests(base, child)
        
        # Check metadata merge
        assert result['metadata']['title'] == 'Child Component'  # Child overrides
        assert result['metadata']['version'] == '1.0.0'  # Inherited from base
        assert result['metadata']['description'] == 'Extends base component'  # Child only
        
        # Check template vars merge
        assert 'base_color' in result['template_vars']
        assert 'child_color' in result['template_vars']
        
        # Check styles merge (child should override base)
        assert 'base' in result['styles']
        assert 'child' in result['styles']
        assert 'padding: 20px' in result['styles']['container']  # Child override
    
    def test_style_optimization(self, processor):
        """Test CSS style optimization."""
        styles = {
            'component1': 'color: red; font-size: 16px; color: blue;',  # Duplicate property
            'component2': '  color:   red  ;  font-size:  16px  ;  ',  # Extra whitespace
            'component3': 'font-size: 16px; color: red;'  # Different order
        }
        
        optimized = processor.optimize_styles(styles)
        
        # Check duplicate removal
        assert optimized['component1'].count('color:') == 1
        assert 'blue' in optimized['component1']  # Last value wins
        
        # Check whitespace normalization
        assert '  ' not in optimized['component2']
        
        # All should be properly formatted
        for style in optimized.values():
            assert style.strip() == style  # No leading/trailing whitespace
    
    def test_structure_validation(self, processor):
        """Test structure validation."""
        # Valid structure
        valid_structure = {
            'div': {
                'class': 'container',
                'children': {
                    'h1': {'text': 'Title'}
                }
            }
        }
        
        errors = processor.validate_structure(valid_structure)
        assert len(errors) == 0
        
        # Invalid structure - unsupported element
        invalid_structure = {
            'invalid_element': {
                'text': 'This should not be allowed'
            }
        }
        
        errors = processor.validate_structure(invalid_structure)
        assert len(errors) > 0
    
    def test_metadata_validation(self, processor):
        """Test metadata validation."""
        # Valid metadata
        valid_metadata = {
            'title': 'Test Component',
            'version': '1.0.0',
            'description': 'A test component'
        }
        
        errors = processor.validate_metadata(valid_metadata)
        assert len(errors) == 0
        
        # Invalid metadata - missing required fields
        invalid_metadata = {
            'description': 'Missing title'
        }
        
        errors = processor.validate_metadata(invalid_metadata)
        assert len(errors) > 0
        assert any('title' in error for error in errors)
    
    def test_circular_template_variable_detection(self, processor):
        """Test detection of circular template variable references."""
        manifest_with_circular_vars = {
            'template_vars': {
                'var1': '{{ var2 }}',
                'var2': '{{ var1 }}'
            },
            'styles': {
                'test': 'color: {{ var1 }};'
            }
        }
        
        with pytest.raises(TemplateInheritanceError) as exc_info:
            processor.process_manifest(manifest_with_circular_vars)
        
        assert 'Circular reference' in str(exc_info.value)
    
    def test_undefined_template_variable_handling(self, processor):
        """Test handling of undefined template variables."""
        manifest_with_undefined_vars = {
            'styles': {
                'test': 'color: {{ undefined_var }};'
            },
            'structure': {
                'div': {
                    'text': '{{ another_undefined_var }}'
                }
            }
        }
        
        # Should either raise error or handle gracefully
        result = processor.process_manifest(manifest_with_undefined_vars)
        
        # Check that undefined variables are handled (either replaced or left as-is)
        assert result is not None
    
    def test_complex_structure_processing(self, processor):
        """Test processing of complex nested structures."""
        complex_structure = {
            'metadata': {'title': 'Complex Component'},
            'template_vars': {'item_count': '3'},
            'structure': {
                'div': {
                    'class': 'wrapper',
                    'children': [
                        {
                            'header': {
                                'children': {
                                    'h1': {'text': '{{ title }}'}
                                }
                            }
                        },
                        {
                            'main': {
                                'children': [
                                    {'section': {'class': f'item-{i}', 'text': f'Item {i}'}} 
                                    for i in range(1, 4)
                                ]
                            }
                        },
                        {
                            'footer': {
                                'text': 'Total items: {{ item_count }}'
                            }
                        }
                    ]
                }
            }
        }
        
        result = processor.process_manifest(complex_structure)
        
        assert result is not None
        assert 'Complex Component' in str(result)
        assert 'Total items: 3' in str(result)
    
    def test_style_preprocessing(self, processor):
        """Test CSS preprocessing functionality."""
        styles_with_nesting = {
            'component': '''
                .container {
                    width: 100%;
                    .header {
                        font-size: 24px;
                        font-weight: bold;
                    }
                    .content {
                        padding: 20px;
                    }
                }
            '''
        }
        
        # Test if processor can handle nested CSS (basic test)
        processed = processor.process_manifest({'styles': styles_with_nesting})
        assert processed is not None
    
    def test_manifest_expansion(self, processor):
        """Test manifest expansion with computed properties."""
        manifest_with_computed = {
            'metadata': {
                'title': 'Computed Component',
                'computed': {
                    'full_title': '{{ title }} - v{{ version }}',
                    'slug': '{{ title | lower | replace(" ", "-") }}'
                }
            },
            'template_vars': {
                'version': '2.0.0'
            }
        }
        
        result = processor.process_manifest(manifest_with_computed)
        
        # Check if computed properties are processed
        assert result is not None
        # Basic check - more sophisticated template processing would be needed
        # for full computed property support
    
    def test_conditional_structure_processing(self, processor):
        """Test conditional structure processing."""
        manifest_with_conditions = {
            'template_vars': {
                'show_header': True,
                'user_role': 'admin'
            },
            'structure': {
                'div': {
                    'children': [
                        {
                            'header': {
                                'condition': '{{ show_header }}',
                                'text': 'Header Content'
                            }
                        },
                        {
                            'div': {
                                'condition': '{{ user_role == "admin" }}',
                                'class': 'admin-panel',
                                'text': 'Admin Panel'
                            }
                        }
                    ]
                }
            }
        }
        
        result = processor.process_manifest(manifest_with_conditions)
        
        # Basic test - full conditional processing would require more sophisticated template engine
        assert result is not None
    
    def test_error_handling_invalid_yaml_structure(self, processor):
        """Test error handling for invalid YAML structure."""
        invalid_manifest = "not a dictionary"
        
        with pytest.raises(ManifestProcessingError):
            processor.process_manifest(invalid_manifest)
    
    def test_error_handling_missing_sections(self, processor):
        """Test handling of manifests with missing sections."""
        minimal_manifest = {
            'metadata': {'title': 'Minimal'}
        }
        
        # Should process successfully with defaults
        result = processor.process_manifest(minimal_manifest)
        assert result is not None
        assert result['metadata']['title'] == 'Minimal'
    
    def test_style_merging_strategies(self, processor):
        """Test different style merging strategies."""
        base_styles = {
            'container': 'width: 100%; height: 200px;',
            'text': 'color: black;'
        }
        
        child_styles = {
            'container': 'width: 100%; height: 300px; padding: 20px;',
            'new_style': 'border: 1px solid gray;'
        }
        
        # Test override strategy (default)
        merged = processor.merge_styles(base_styles, child_styles, strategy='override')
        assert 'height: 300px' in merged['container']
        assert 'padding: 20px' in merged['container']
        assert 'new_style' in merged
        
        # Test extend strategy
        merged = processor.merge_styles(base_styles, child_styles, strategy='extend')
        assert 'new_style' in merged
    
    def test_performance_with_large_manifest(self, processor):
        """Test performance with large manifests."""
        # Create a large manifest
        large_manifest = {
            'metadata': {'title': 'Large Component'},
            'template_vars': {f'var_{i}': f'value_{i}' for i in range(100)},
            'styles': {f'style_{i}': f'property: value_{i};' for i in range(100)},
            'structure': {
                'div': {
                    'children': [
                        {'div': {'class': f'item-{i}', 'text': f'Item {i}'}}
                        for i in range(100)
                    ]
                }
            }
        }
        
        import time
        start_time = time.time()
        result = processor.process_manifest(large_manifest)
        end_time = time.time()
        
        # Should process within reasonable time (adjust threshold as needed)
        assert (end_time - start_time) < 1.0  # Less than 1 second
        assert result is not None
    
    def test_processor_configuration(self):
        """Test ManifestProcessor configuration options."""
        processor = ManifestProcessor(
            enable_validation=False,
            template_engine='jinja2',
            style_optimization=True
        )
        
        assert processor.enable_validation == False
        assert processor.template_engine == 'jinja2'
        assert processor.style_optimization == True
    
    def test_custom_template_functions(self, processor):
        """Test custom template functions."""
        # Test built-in template functions
        manifest_with_functions = {
            'template_vars': {
                'base_name': 'test component'
            },
            'metadata': {
                'title': '{{ base_name | title }}',
                'slug': '{{ base_name | lower | replace(" ", "-") }}'
            }
        }
        
        result = processor.process_manifest(manifest_with_functions)
        
        # Check if template functions are applied
        # This would require actual Jinja2 integration
        assert result is not None


if __name__ == '__main__':
    pytest.main([__file__])
