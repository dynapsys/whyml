"""
Test cases for ManifestLoader

Tests for YAML manifest loading, dependency resolution, caching,
and template inheritance functionality.

Copyright 2024 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import yaml

from whyml.manifest_loader import ManifestLoader
from whyml.exceptions import (
    ManifestLoadingError, DependencyResolutionError, 
    TemplateInheritanceError, NetworkError
)


class TestManifestLoader:
    """Test cases for ManifestLoader functionality."""
    
    @pytest.fixture
    def loader(self):
        """Create a ManifestLoader instance for testing."""
        return ManifestLoader(cache_size=100, cache_ttl=300)
    
    @pytest.fixture
    def temp_manifest_dir(self):
        """Create a temporary directory with test manifests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create base manifest
            base_manifest = {
                'metadata': {
                    'title': 'Base Component',
                    'version': '1.0.0'
                },
                'styles': {
                    'container': 'width: 100%; padding: 20px;',
                    'header': 'font-size: 24px; font-weight: bold;'
                },
                'structure': {
                    'div': {
                        'class': 'container',
                        'children': {
                            'h1': {
                                'class': 'header',
                                'text': '{{ title }}'
                            }
                        }
                    }
                }
            }
            
            # Create child manifest with inheritance
            child_manifest = {
                'extends': './base.yaml',
                'metadata': {
                    'title': 'Child Component',
                    'description': 'Extends base component'
                },
                'styles': {
                    'content': 'margin: 10px 0;'
                },
                'structure': {
                    'div': {
                        'class': 'container',
                        'children': [
                            {
                                'h1': {
                                    'class': 'header',
                                    'text': '{{ title }}'
                                }
                            },
                            {
                                'p': {
                                    'class': 'content',
                                    'text': '{{ description }}'
                                }
                            }
                        ]
                    }
                }
            }
            
            # Create manifest with dependencies
            with_deps_manifest = {
                'metadata': {
                    'title': 'Component with Dependencies'
                },
                'imports': ['./base.yaml'],
                'dependencies': ['./child.yaml'],
                'structure': {
                    'div': {
                        'text': 'Component with dependencies'
                    }
                }
            }
            
            # Write manifests to files
            (temp_path / 'base.yaml').write_text(yaml.dump(base_manifest))
            (temp_path / 'child.yaml').write_text(yaml.dump(child_manifest))
            (temp_path / 'with_deps.yaml').write_text(yaml.dump(with_deps_manifest))
            
            # Invalid YAML file
            (temp_path / 'invalid.yaml').write_text('invalid: yaml: content: [')
            
            yield temp_path
    
    @pytest.mark.asyncio
    async def test_load_local_manifest(self, loader, temp_manifest_dir):
        """Test loading a local YAML manifest file."""
        manifest_path = str(temp_manifest_dir / 'base.yaml')
        result = await loader.load_manifest(manifest_path)
        
        assert result is not None
        assert result.content['metadata']['title'] == 'Base Component'
        assert 'styles' in result.content
        assert 'structure' in result.content
    
    @pytest.mark.asyncio
    async def test_load_manifest_with_inheritance(self, loader, temp_manifest_dir):
        """Test loading manifest with template inheritance."""
        manifest_path = str(temp_manifest_dir / 'child.yaml')
        result = await loader.load_manifest(manifest_path)
        
        assert result is not None
        assert result.content['metadata']['title'] == 'Child Component'
        assert result.content['metadata']['version'] == '1.0.0'  # Inherited from base
        assert 'content' in result.content['styles']  # Child styles
        assert 'container' in result.content['styles']  # Inherited styles
    
    @pytest.mark.asyncio
    async def test_dependency_resolution(self, loader, temp_manifest_dir):
        """Test dependency resolution."""
        manifest_path = str(temp_manifest_dir / 'with_deps.yaml')
        result = await loader.load_manifest(manifest_path)
        
        assert result is not None
        assert 'dependencies' in result.content
        assert len(result.content['dependencies']) > 0
    
    @pytest.mark.asyncio
    async def test_caching(self, loader, temp_manifest_dir):
        """Test that manifests are properly cached."""
        manifest_path = str(temp_manifest_dir / 'base.yaml')
        
        # Load manifest twice
        result1 = await loader.load_manifest(manifest_path)
        result2 = await loader.load_manifest(manifest_path)
        
        # Results should be identical (cached)
        assert result1 == result2
        
        # Check cache hit
        cache_key = loader._generate_cache_key(manifest_path, {})
        assert cache_key in loader.cache
    
    @pytest.mark.asyncio
    async def test_invalid_yaml_error(self, loader, temp_manifest_dir):
        """Test handling of invalid YAML files."""
        manifest_path = str(temp_manifest_dir / 'invalid.yaml')
        
        with pytest.raises(ManifestLoadingError) as exc_info:
            await loader.load_manifest(manifest_path)
        
        assert 'YAML parsing failed' in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_file_not_found_error(self, loader):
        """Test handling of non-existent files."""
        with pytest.raises(ManifestLoadingError) as exc_info:
            await loader.load_manifest('/nonexistent/manifest.yaml')
        
        assert 'Failed to load manifest' in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_circular_dependency_detection(self, loader):
        """Test detection of circular dependencies."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create circular dependency
            manifest_a = {
                'extends': './manifest_b.yaml',
                'metadata': {'title': 'A'}
            }
            manifest_b = {
                'extends': './manifest_a.yaml', 
                'metadata': {'title': 'B'}
            }
            
            (temp_path / 'manifest_a.yaml').write_text(yaml.dump(manifest_a))
            (temp_path / 'manifest_b.yaml').write_text(yaml.dump(manifest_b))
            
            with pytest.raises(DependencyResolutionError) as exc_info:
                await loader.load_manifest(str(temp_path / 'manifest_a.yaml'))
            
            assert 'Circular dependency detected' in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_load_remote_manifest(self, mock_get, loader):
        """Test loading manifest from remote URL."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=yaml.dump({
            'metadata': {'title': 'Remote Component'},
            'structure': {'div': {'text': 'Remote content'}}
        }))
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await loader.load_manifest('https://example.com/manifest.yaml')
        
        assert result is not None
        assert result.content['metadata']['title'] == 'Remote Component'
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_network_error_handling(self, mock_get, loader):
        """Test handling of network errors."""
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(NetworkError):
            await loader.load_manifest('https://example.com/manifest.yaml')
    
    @pytest.mark.asyncio
    async def test_template_variable_resolution(self, loader, temp_manifest_dir):
        """Test template variable resolution in manifests."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            manifest_with_vars = {
                'metadata': {
                    'title': 'Test Component',
                    'version': '2.0.0'
                },
                'template_vars': {
                    'primary_color': '#007bff',
                    'text_size': '16px'
                },
                'styles': {
                    'button': 'background: {{ primary_color }}; font-size: {{ text_size }};'
                }
            }
            yaml.dump(manifest_with_vars, f)
            f.flush()
            
            result = await loader.load_manifest(f.name)
            
            # Check that template variables are preserved for processing
            assert 'template_vars' in result.content
            assert result.content['template_vars']['primary_color'] == '#007bff'
        
        os.unlink(f.name)
    
    @pytest.mark.asyncio
    async def test_manifest_validation(self, loader):
        """Test basic manifest validation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            # Invalid manifest structure
            invalid_manifest = {
                'invalid_root_key': 'should not be here'
            }
            yaml.dump(invalid_manifest, f)
            f.flush()
            
            # Should load but validation might flag issues
            result = await loader.load_manifest(f.name)
            assert result is not None
        
        os.unlink(f.name)
    
    def test_cache_key_generation(self, loader):
        """Test cache key generation."""
        url = '/path/to/manifest.yaml'
        options = {'validate': True, 'resolve_deps': False}
        
        key1 = loader._generate_cache_key(url, options)
        key2 = loader._generate_cache_key(url, options)
        key3 = loader._generate_cache_key(url, {})
        
        # Same inputs should generate same key
        assert key1 == key2
        # Different options should generate different key
        assert key1 != key3
    
    @pytest.mark.asyncio
    async def test_concurrent_loading(self, loader, temp_manifest_dir):
        """Test concurrent loading of manifests."""
        manifest_path = str(temp_manifest_dir / 'base.yaml')
        
        # Load same manifest concurrently
        tasks = [loader.load_manifest(manifest_path) for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            assert result == first_result
    
    @pytest.mark.asyncio
    async def test_load_with_options(self, loader, temp_manifest_dir):
        """Test loading with various options."""
        manifest_path = str(temp_manifest_dir / 'child.yaml')
        
        # Load without dependency resolution
        result_no_deps = await loader.load_manifest(
            manifest_path, 
            options={'resolve_dependencies': False}
        )
        
        # Load with dependency resolution (default)
        result_with_deps = await loader.load_manifest(manifest_path)
        
        # Results should be different based on options
        assert result_no_deps != result_with_deps
    
    def test_url_resolution(self, loader):
        """Test URL resolution for relative paths."""
        base_url = 'https://example.com/manifests/main.yaml'
        relative_url = './child.yaml'
        
        resolved = loader._resolve_url(relative_url, base_url)
        expected = 'https://example.com/manifests/child.yaml'
        
        assert resolved == expected
    
    def test_file_path_resolution(self, loader, temp_manifest_dir):
        """Test file path resolution for relative paths."""
        base_path = str(temp_manifest_dir / 'main.yaml')
        relative_path = './base.yaml'
        
        resolved = loader._resolve_url(relative_path, base_path)
        expected = str(temp_manifest_dir / 'base.yaml')
        
        assert resolved == expected
    
    @pytest.mark.asyncio
    async def test_deep_inheritance_chain(self, loader):
        """Test deep inheritance chains."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create inheritance chain: level3 -> level2 -> level1 -> base
            manifests = {
                'base.yaml': {
                    'metadata': {'title': 'Base', 'level': 0},
                    'styles': {'base': 'color: black;'}
                },
                'level1.yaml': {
                    'extends': './base.yaml',
                    'metadata': {'title': 'Level 1', 'level': 1},
                    'styles': {'level1': 'font-weight: bold;'}
                },
                'level2.yaml': {
                    'extends': './level1.yaml',
                    'metadata': {'title': 'Level 2', 'level': 2},
                    'styles': {'level2': 'font-size: 18px;'}
                },
                'level3.yaml': {
                    'extends': './level2.yaml',
                    'metadata': {'title': 'Level 3', 'level': 3},
                    'styles': {'level3': 'margin: 10px;'}
                }
            }
            
            for filename, content in manifests.items():
                (temp_path / filename).write_text(yaml.dump(content))
            
            result = await loader.load_manifest(str(temp_path / 'level3.yaml'))
            
            assert result.content['metadata']['title'] == 'Level 3'
            assert result.content['metadata']['level'] == 3
            assert 'base' in result.content['styles']
            assert 'level1' in result.content['styles']
            assert 'level2' in result.content['styles']
            assert 'level3' in result.content['styles']


@pytest.mark.asyncio
async def test_loader_context_manager():
    """Test using ManifestLoader as async context manager."""
    async with ManifestLoader() as loader:
        assert loader.session is not None
    
    # Session should be closed after context exit
    assert loader.session is None or loader.session.closed


def test_loader_configuration():
    """Test ManifestLoader configuration options."""
    loader = ManifestLoader(
        cache_size=50,
        cache_ttl=600,
        max_depth=5,
        timeout=45
    )
    
    assert loader.cache.maxsize == 50
    assert loader.cache.ttl == 600
    assert loader.max_depth == 5
    assert loader.timeout == 45


if __name__ == '__main__':
    pytest.main([__file__])
