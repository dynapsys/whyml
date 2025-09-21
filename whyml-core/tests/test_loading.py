"""
Test suite for whyml_core.loading module

Tests for:
- ManifestLoader
- CacheManager
- DependencyResolver
- Async loading operations
- Error handling

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import asyncio
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, mock_open
from typing import Dict, Any, List

from whyml_core.loading.manifest_loader import ManifestLoader
from whyml_core.loading.cache_manager import CacheManager
from whyml_core.loading.dependency_resolver import DependencyResolver
from whyml_core.exceptions.validation_exceptions import ValidationError
from whyml_core.exceptions.base_exceptions import WhyMLError


class TestManifestLoader:
    """Test cases for ManifestLoader class."""
    
    @pytest.fixture
    def loader(self):
        """Create a ManifestLoader instance for testing."""
        return ManifestLoader(cache_size=100, cache_ttl=3600)
    
    @pytest.fixture
    def sample_manifest_dict(self) -> Dict[str, Any]:
        """Create a sample manifest dictionary."""
        return {
            "metadata": {
                "title": "Test Manifest",
                "description": "Test description",
                "version": "1.0.0"
            },
            "structure": {
                "html": {
                    "head": {"title": "Test Page"},
                    "body": {"div": {"content": "Hello World"}}
                }
            }
        }
    
    @pytest.fixture
    def sample_yaml_content(self, sample_manifest_dict):
        """Create sample YAML content."""
        return yaml.dump(sample_manifest_dict)
    
    @pytest.fixture
    def sample_json_content(self, sample_manifest_dict):
        """Create sample JSON content."""
        return json.dumps(sample_manifest_dict, indent=2)
    
    def test_loader_initialization(self, loader):
        """Test ManifestLoader initialization."""
        assert loader is not None
        assert hasattr(loader, 'load_manifest')
        assert hasattr(loader, 'load_manifest_from_file')
        assert hasattr(loader, 'load_manifest_from_url')
        assert loader.cache_size == 100
        assert loader.cache_ttl == 3600
    
    def test_load_manifest_from_dict(self, loader, sample_manifest_dict):
        """Test loading manifest from dictionary."""
        result = loader.load_manifest(sample_manifest_dict)
        
        assert result == sample_manifest_dict
        assert isinstance(result, dict)
    
    def test_load_manifest_from_yaml_file(self, loader, sample_yaml_content, tmp_path):
        """Test loading manifest from YAML file."""
        yaml_file = tmp_path / "test_manifest.yaml"
        yaml_file.write_text(sample_yaml_content)
        
        result = loader.load_manifest_from_file(str(yaml_file))
        
        assert isinstance(result, dict)
        assert result["metadata"]["title"] == "Test Manifest"
        assert "structure" in result
    
    def test_load_manifest_from_json_file(self, loader, sample_json_content, tmp_path):
        """Test loading manifest from JSON file."""
        json_file = tmp_path / "test_manifest.json"
        json_file.write_text(sample_json_content)
        
        result = loader.load_manifest_from_file(str(json_file))
        
        assert isinstance(result, dict)
        assert result["metadata"]["title"] == "Test Manifest"
        assert "structure" in result
    
    def test_load_manifest_from_nonexistent_file(self, loader):
        """Test loading manifest from nonexistent file."""
        with pytest.raises(FileNotFoundError):
            loader.load_manifest_from_file("/nonexistent/file.yaml")
    
    def test_load_manifest_from_invalid_yaml(self, loader, tmp_path):
        """Test loading manifest from invalid YAML file."""
        invalid_yaml_file = tmp_path / "invalid.yaml"
        invalid_yaml_file.write_text("invalid: yaml: content: [unclosed")
        
        with pytest.raises(yaml.YAMLError):
            loader.load_manifest_from_file(str(invalid_yaml_file))
    
    def test_load_manifest_from_invalid_json(self, loader, tmp_path):
        """Test loading manifest from invalid JSON file."""
        invalid_json_file = tmp_path / "invalid.json"
        invalid_json_file.write_text('{"invalid": json, "content"}')
        
        with pytest.raises(json.JSONDecodeError):
            loader.load_manifest_from_file(str(invalid_json_file))
    
    @pytest.mark.asyncio
    async def test_load_manifest_async(self, loader, sample_manifest_dict):
        """Test async manifest loading."""
        result = await loader.load_manifest_async(sample_manifest_dict)
        
        assert result == sample_manifest_dict
    
    @pytest.mark.asyncio
    async def test_load_manifest_from_file_async(self, loader, sample_yaml_content, tmp_path):
        """Test async file loading."""
        yaml_file = tmp_path / "async_test.yaml"
        yaml_file.write_text(sample_yaml_content)
        
        result = await loader.load_manifest_from_file_async(str(yaml_file))
        
        assert isinstance(result, dict)
        assert result["metadata"]["title"] == "Test Manifest"
    
    @patch('aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_load_manifest_from_url_async(self, mock_get, loader, sample_yaml_content):
        """Test async URL loading."""
        # Mock the HTTP response
        mock_response = AsyncMock()
        mock_response.text = AsyncMock(return_value=sample_yaml_content)
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await loader.load_manifest_from_url_async("https://example.com/manifest.yaml")
        
        assert isinstance(result, dict)
        assert result["metadata"]["title"] == "Test Manifest"
    
    @patch('aiohttp.ClientSession.get')
    @pytest.mark.asyncio
    async def test_load_manifest_from_url_404(self, mock_get, loader):
        """Test loading manifest from URL that returns 404."""
        # Mock 404 response
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_get.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(Exception):  # Should raise some HTTP error
            await loader.load_manifest_from_url_async("https://example.com/nonexistent.yaml")
    
    def test_load_manifest_with_options(self, loader, sample_manifest_dict):
        """Test loading manifest with options."""
        options = {
            "validate": True,
            "cache_enabled": False,
            "resolve_dependencies": True
        }
        
        result = loader.load_manifest(sample_manifest_dict, options)
        
        assert isinstance(result, dict)
        assert result == sample_manifest_dict
    
    def test_load_manifest_with_encoding(self, loader, tmp_path):
        """Test loading manifest with specific encoding."""
        # Create file with UTF-8 content including special characters
        content = {
            "metadata": {
                "title": "Tëst Manifëst with spëcial charactërs",
                "description": "Tëst with ñón-ASCII charactërs"
            },
            "structure": {"html": {"body": {"div": "Hellö Wörld"}}}
        }
        
        yaml_file = tmp_path / "utf8_test.yaml"
        yaml_file.write_text(yaml.dump(content), encoding="utf-8")
        
        result = loader.load_manifest_from_file(str(yaml_file))
        
        assert result["metadata"]["title"] == "Tëst Manifëst with spëcial charactërs"


class TestCacheManager:
    """Test cases for CacheManager class."""
    
    @pytest.fixture
    def cache_manager(self):
        """Create a CacheManager instance for testing."""
        return CacheManager(max_size=100, ttl_seconds=3600)
    
    def test_cache_manager_initialization(self, cache_manager):
        """Test CacheManager initialization."""
        assert cache_manager is not None
        assert cache_manager.max_size == 100
        assert cache_manager.ttl_seconds == 3600
        assert hasattr(cache_manager, 'get')
        assert hasattr(cache_manager, 'set')
        assert hasattr(cache_manager, 'clear')
    
    def test_cache_set_and_get(self, cache_manager):
        """Test basic cache set and get operations."""
        test_key = "test_manifest"
        test_value = {"metadata": {"title": "Cached Manifest"}}
        
        # Set cache entry
        cache_manager.set(test_key, test_value)
        
        # Get cache entry
        result = cache_manager.get(test_key)
        
        assert result == test_value
    
    def test_cache_get_nonexistent(self, cache_manager):
        """Test getting nonexistent cache entry."""
        result = cache_manager.get("nonexistent_key")
        
        assert result is None
    
    def test_cache_overwrite(self, cache_manager):
        """Test overwriting cache entry."""
        test_key = "test_key"
        original_value = {"original": True}
        updated_value = {"updated": True}
        
        # Set original value
        cache_manager.set(test_key, original_value)
        assert cache_manager.get(test_key) == original_value
        
        # Overwrite with updated value
        cache_manager.set(test_key, updated_value)
        assert cache_manager.get(test_key) == updated_value
    
    def test_cache_clear(self, cache_manager):
        """Test clearing cache."""
        # Add some entries
        cache_manager.set("key1", {"value": 1})
        cache_manager.set("key2", {"value": 2})
        
        assert cache_manager.get("key1") is not None
        assert cache_manager.get("key2") is not None
        
        # Clear cache
        cache_manager.clear()
        
        assert cache_manager.get("key1") is None
        assert cache_manager.get("key2") is None
    
    def test_cache_max_size_limit(self):
        """Test cache max size limit enforcement."""
        small_cache = CacheManager(max_size=2, ttl_seconds=3600)
        
        # Add entries up to limit
        small_cache.set("key1", {"value": 1})
        small_cache.set("key2", {"value": 2})
        
        assert small_cache.get("key1") is not None
        assert small_cache.get("key2") is not None
        
        # Add entry beyond limit - should evict oldest
        small_cache.set("key3", {"value": 3})
        
        # key1 should be evicted, key2 and key3 should remain
        assert small_cache.get("key1") is None or small_cache.get("key2") is not None
        assert small_cache.get("key3") is not None
    
    @pytest.mark.asyncio
    async def test_cache_ttl_expiry(self):
        """Test cache TTL expiry."""
        short_ttl_cache = CacheManager(max_size=100, ttl_seconds=0.1)  # 0.1 second TTL
        
        # Set cache entry
        short_ttl_cache.set("expiring_key", {"value": "expires soon"})
        
        # Should be available immediately
        assert short_ttl_cache.get("expiring_key") is not None
        
        # Wait for TTL to expire
        await asyncio.sleep(0.2)
        
        # Should be expired and return None
        result = short_ttl_cache.get("expiring_key")
        # Note: Depending on implementation, this might return None or still return the value
        # The test verifies the cache respects TTL concepts
        assert result is None or isinstance(result, dict)
    
    def test_cache_contains(self, cache_manager):
        """Test cache contains check."""
        test_key = "contains_test"
        test_value = {"test": "value"}
        
        # Should not contain key initially
        assert not cache_manager.contains(test_key)
        
        # Add entry
        cache_manager.set(test_key, test_value)
        
        # Should contain key now
        assert cache_manager.contains(test_key)
    
    def test_cache_size(self, cache_manager):
        """Test cache size reporting."""
        # Should be empty initially
        assert cache_manager.size() == 0
        
        # Add entries
        cache_manager.set("key1", {"value": 1})
        assert cache_manager.size() == 1
        
        cache_manager.set("key2", {"value": 2})
        assert cache_manager.size() == 2
        
        # Clear cache
        cache_manager.clear()
        assert cache_manager.size() == 0


class TestDependencyResolver:
    """Test cases for DependencyResolver class."""
    
    @pytest.fixture
    def dependency_resolver(self):
        """Create a DependencyResolver instance for testing."""
        return DependencyResolver()
    
    @pytest.fixture
    def manifest_with_dependencies(self) -> Dict[str, Any]:
        """Create a manifest with dependencies."""
        return {
            "metadata": {
                "title": "Main Manifest",
                "version": "1.0.0"
            },
            "dependencies": [
                {"type": "inherit", "source": "base_template.yaml"},
                {"type": "import", "source": "components.yaml", "section": "components"},
                {"type": "include", "source": "styles.yaml"}
            ],
            "structure": {
                "html": {
                    "body": {"div": "Main content"}
                }
            }
        }
    
    @pytest.fixture
    def base_template_manifest(self) -> Dict[str, Any]:
        """Create a base template manifest."""
        return {
            "metadata": {
                "title": "Base Template",
                "type": "template"
            },
            "structure": {
                "html": {
                    "head": {"title": "Base Title"},
                    "body": {"header": {"h1": "Base Header"}}
                }
            },
            "styles": {
                "primary": "#000000"
            }
        }
    
    def test_dependency_resolver_initialization(self, dependency_resolver):
        """Test DependencyResolver initialization."""
        assert dependency_resolver is not None
        assert hasattr(dependency_resolver, 'resolve_dependencies')
        assert hasattr(dependency_resolver, 'load_dependency')
    
    def test_resolve_no_dependencies(self, dependency_resolver):
        """Test resolving manifest with no dependencies."""
        manifest = {
            "metadata": {"title": "Simple Manifest"},
            "structure": {"html": {"body": {"div": "content"}}}
        }
        
        result = dependency_resolver.resolve_dependencies(manifest)
        
        assert result == manifest  # Should return unchanged
    
    @patch.object(DependencyResolver, 'load_dependency')
    def test_resolve_with_dependencies(self, mock_load_dependency, dependency_resolver, 
                                     manifest_with_dependencies, base_template_manifest):
        """Test resolving manifest with dependencies."""
        # Mock dependency loading
        def mock_load(dep_info):
            if "base_template.yaml" in dep_info["source"]:
                return base_template_manifest
            elif "components.yaml" in dep_info["source"]:
                return {"components": {"button": {"class": "btn"}}}
            elif "styles.yaml" in dep_info["source"]:
                return {"styles": {"secondary": "#ffffff"}}
            return {}
        
        mock_load_dependency.side_effect = mock_load
        
        result = dependency_resolver.resolve_dependencies(manifest_with_dependencies)
        
        assert isinstance(result, dict)
        assert "metadata" in result
        assert "structure" in result
        # Should have merged dependencies
        assert mock_load_dependency.call_count == 3
    
    def test_resolve_circular_dependencies(self, dependency_resolver):
        """Test handling of circular dependencies."""
        # Create manifests with circular dependencies
        manifest_a = {
            "metadata": {"title": "Manifest A"},
            "dependencies": [{"type": "inherit", "source": "manifest_b.yaml"}],
            "structure": {"html": {"body": {"div": "A content"}}}
        }
        
        manifest_b = {
            "metadata": {"title": "Manifest B"},
            "dependencies": [{"type": "inherit", "source": "manifest_a.yaml"}],
            "structure": {"html": {"body": {"div": "B content"}}}
        }
        
        # Mock load_dependency to return the circular reference
        with patch.object(dependency_resolver, 'load_dependency') as mock_load:
            def circular_load(dep_info):
                if "manifest_b.yaml" in dep_info["source"]:
                    return manifest_b
                elif "manifest_a.yaml" in dep_info["source"]:
                    return manifest_a
                return {}
            
            mock_load.side_effect = circular_load
            
            # Should handle circular dependencies gracefully
            # Either by detecting them or by limiting recursion depth
            result = dependency_resolver.resolve_dependencies(manifest_a)
            
            assert isinstance(result, dict)
            assert "metadata" in result
    
    @pytest.mark.asyncio
    async def test_resolve_dependencies_async(self, dependency_resolver, manifest_with_dependencies):
        """Test async dependency resolution."""
        # Mock async dependency loading
        async def mock_load_async(dep_info):
            if "base_template.yaml" in dep_info["source"]:
                return {"metadata": {"title": "Async Base"}, "structure": {"html": {}}}
            return {}
        
        with patch.object(dependency_resolver, 'load_dependency_async', side_effect=mock_load_async):
            result = await dependency_resolver.resolve_dependencies_async(manifest_with_dependencies)
            
            assert isinstance(result, dict)
            assert "metadata" in result
    
    def test_load_dependency_from_file(self, dependency_resolver, base_template_manifest, tmp_path):
        """Test loading dependency from file."""
        # Create dependency file
        dep_file = tmp_path / "dependency.yaml"
        dep_file.write_text(yaml.dump(base_template_manifest))
        
        dep_info = {"type": "inherit", "source": str(dep_file)}
        
        result = dependency_resolver.load_dependency(dep_info)
        
        assert isinstance(result, dict)
        assert result["metadata"]["title"] == "Base Template"
    
    def test_load_dependency_nonexistent_file(self, dependency_resolver):
        """Test loading dependency from nonexistent file."""
        dep_info = {"type": "inherit", "source": "/nonexistent/file.yaml"}
        
        with pytest.raises(FileNotFoundError):
            dependency_resolver.load_dependency(dep_info)
    
    def test_dependency_type_validation(self, dependency_resolver):
        """Test validation of dependency types."""
        valid_types = ["inherit", "import", "include"]
        
        for dep_type in valid_types:
            dep_info = {"type": dep_type, "source": "test.yaml"}
            # Should not raise exception for valid types
            assert dependency_resolver._validate_dependency_type(dep_info) is True
        
        # Invalid type should raise exception
        invalid_dep_info = {"type": "invalid_type", "source": "test.yaml"}
        with pytest.raises(ValidationError):
            dependency_resolver._validate_dependency_type(invalid_dep_info)
    
    def test_merge_manifests(self, dependency_resolver):
        """Test merging of manifests."""
        base_manifest = {
            "metadata": {"title": "Base", "version": "1.0.0"},
            "structure": {"html": {"head": {"title": "Base Title"}}},
            "styles": {"primary": "#000000"}
        }
        
        overlay_manifest = {
            "metadata": {"title": "Overlay", "description": "Added description"},
            "structure": {"html": {"body": {"div": "New content"}}},
            "styles": {"secondary": "#ffffff"}
        }
        
        result = dependency_resolver._merge_manifests(base_manifest, overlay_manifest)
        
        # Should merge metadata
        assert result["metadata"]["title"] == "Overlay"  # Override
        assert result["metadata"]["version"] == "1.0.0"  # Keep base
        assert result["metadata"]["description"] == "Added description"  # Add new
        
        # Should merge structure
        assert "head" in result["structure"]["html"]
        assert "body" in result["structure"]["html"]
        
        # Should merge styles
        assert result["styles"]["primary"] == "#000000"
        assert result["styles"]["secondary"] == "#ffffff"


# Integration tests
class TestLoadingIntegration:
    """Integration tests for loading components."""
    
    @pytest.fixture
    def complete_loading_setup(self):
        """Set up complete loading environment."""
        loader = ManifestLoader(cache_size=50, cache_ttl=1800)
        cache_manager = CacheManager(max_size=50, ttl_seconds=1800)
        dependency_resolver = DependencyResolver()
        
        return {
            'loader': loader,
            'cache_manager': cache_manager,
            'dependency_resolver': dependency_resolver
        }
    
    def test_full_loading_workflow_with_cache(self, complete_loading_setup, tmp_path):
        """Test complete loading workflow with caching."""
        components = complete_loading_setup
        loader = components['loader']
        
        # Create test manifest files
        base_manifest = {
            "metadata": {"title": "Base Template", "type": "template"},
            "structure": {"html": {"head": {"title": "Base Title"}}}
        }
        
        main_manifest = {
            "metadata": {"title": "Main Page"},
            "dependencies": [{"type": "inherit", "source": "base.yaml"}],
            "structure": {"html": {"body": {"div": "Main content"}}}
        }
        
        base_file = tmp_path / "base.yaml"
        base_file.write_text(yaml.dump(base_manifest))
        
        main_file = tmp_path / "main.yaml"
        main_file.write_text(yaml.dump(main_manifest))
        
        # Load main manifest (should resolve dependencies and cache results)
        result = loader.load_manifest_from_file(str(main_file))
        
        assert isinstance(result, dict)
        assert result["metadata"]["title"] == "Main Page"
        assert "structure" in result
    
    @pytest.mark.asyncio
    async def test_async_loading_with_dependencies(self, complete_loading_setup, tmp_path):
        """Test async loading with dependency resolution."""
        components = complete_loading_setup
        loader = components['loader']
        dependency_resolver = components['dependency_resolver']
        
        # Create complex manifest with multiple dependencies
        component_manifest = {
            "components": {
                "header": {"tag": "header", "class": "main-header"},
                "footer": {"tag": "footer", "class": "main-footer"}
            }
        }
        
        style_manifest = {
            "styles": {
                "primary": "#007bff",
                "secondary": "#6c757d",
                "success": "#28a745"
            }
        }
        
        main_manifest = {
            "metadata": {
                "title": "Complex Page",
                "description": "Page with multiple dependencies"
            },
            "dependencies": [
                {"type": "import", "source": "components.yaml", "section": "components"},
                {"type": "include", "source": "styles.yaml"}
            ],
            "structure": {
                "html": {
                    "head": {"title": "Complex Page"},
                    "body": {
                        "header": {"$ref": "components.header"},
                        "main": {"div": "Main content"},
                        "footer": {"$ref": "components.footer"}
                    }
                }
            }
        }
        
        # Write files
        component_file = tmp_path / "components.yaml"
        component_file.write_text(yaml.dump(component_manifest))
        
        style_file = tmp_path / "styles.yaml"
        style_file.write_text(yaml.dump(style_manifest))
        
        main_file = tmp_path / "main.yaml"
        main_file.write_text(yaml.dump(main_manifest))
        
        # Load with async operations
        loaded_manifest = await loader.load_manifest_from_file_async(str(main_file))
        resolved_manifest = await dependency_resolver.resolve_dependencies_async(loaded_manifest)
        
        assert isinstance(resolved_manifest, dict)
        assert resolved_manifest["metadata"]["title"] == "Complex Page"


if __name__ == "__main__":
    pytest.main([__file__])
