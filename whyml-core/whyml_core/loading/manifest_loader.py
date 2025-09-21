"""
WhyML Core Manifest Loader - Advanced manifest loading with dependency resolution

Provides async manifest loading from files and URLs with comprehensive caching,
dependency resolution, and error handling.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import os
import yaml
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse
from datetime import datetime
from dataclasses import dataclass

from .cache_manager import CacheManager
from .dependency_resolver import DependencyResolver, DependencyError
from ..exceptions import ManifestError, NetworkError, WhyMLError


@dataclass
class LoadedManifest:
    """Container for a loaded manifest with metadata."""
    content: Dict[str, Any]
    source_url: str
    dependencies: List[str]
    load_time: datetime
    cache_key: str
    resolved_modules: Dict[str, Any]
    template_inheritance: List[str]


class ManifestLoader:
    """Advanced manifest loader with dependency resolution and caching."""
    
    def __init__(self, 
                 cache_size: int = 1000, 
                 cache_ttl: int = 300,
                 timeout: int = 30,
                 base_path: Optional[Path] = None):
        """Initialize manifest loader.
        
        Args:
            cache_size: Maximum number of cached manifests
            cache_ttl: Cache time-to-live in seconds
            timeout: HTTP request timeout in seconds
            base_path: Base path for resolving relative file paths
        """
        self.cache_manager = CacheManager(cache_size, cache_ttl)
        self.dependency_resolver = DependencyResolver()
        self.timeout = timeout
        self.base_path = base_path or Path.cwd()
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure HTTP session is available."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'WhyML-Loader/1.0'}
            )
    
    async def close(self) -> None:
        """Close HTTP session and cleanup resources."""
        if self._session and not self._session.closed:
            await self._session.close()
        await self.cache_manager.cleanup_loading_locks()
    
    async def load_manifest(self, 
                          source: Union[str, Path], 
                          resolve_dependencies: bool = True,
                          recursive: bool = True) -> LoadedManifest:
        """Load manifest from file or URL with dependency resolution.
        
        Args:
            source: File path or URL to load manifest from
            resolve_dependencies: Whether to resolve and load dependencies
            recursive: Whether to recursively resolve nested dependencies
            
        Returns:
            Loaded manifest with resolved dependencies
            
        Raises:
            ManifestError: If manifest loading fails
            NetworkError: If network operation fails
            DependencyError: If dependency resolution fails
        """
        source_str = str(source)
        
        # Check cache first
        cached = await self.cache_manager.get(source_str)
        if cached:
            return cached
        
        # Use loading lock to prevent duplicate loads
        loading_lock = await self.cache_manager.get_loading_lock(source_str)
        
        async with loading_lock:
            # Double-check cache after acquiring lock
            cached = await self.cache_manager.get(source_str)
            if cached:
                return cached
            
            try:
                # Load the manifest content
                content = await self._load_content(source)
                
                # Create loaded manifest
                loaded_manifest = LoadedManifest(
                    content=content,
                    source_url=source_str,
                    dependencies=[],
                    load_time=datetime.now(),
                    cache_key=source_str,
                    resolved_modules={},
                    template_inheritance=[]
                )
                
                # Resolve dependencies if requested
                if resolve_dependencies:
                    await self._resolve_manifest_dependencies(
                        loaded_manifest, 
                        recursive=recursive
                    )
                
                # Cache the result
                await self.cache_manager.set(source_str, loaded_manifest)
                
                return loaded_manifest
                
            except Exception as e:
                if isinstance(e, (ManifestError, NetworkError, DependencyError)):
                    raise
                raise ManifestError(f"Failed to load manifest from {source_str}: {e}")
    
    async def _load_content(self, source: Union[str, Path]) -> Dict[str, Any]:
        """Load content from file or URL.
        
        Args:
            source: File path or URL to load from
            
        Returns:
            Parsed YAML content as dictionary
            
        Raises:
            ManifestError: If content loading fails
            NetworkError: If network operation fails
        """
        source_str = str(source)
        
        try:
            if self._is_url(source_str):
                return await self._load_from_url(source_str)
            else:
                return await self._load_from_file(source_str)
        except yaml.YAMLError as e:
            raise ManifestError(f"Invalid YAML in {source_str}: {e}")
        except Exception as e:
            if isinstance(e, (ManifestError, NetworkError)):
                raise
            raise ManifestError(f"Failed to load content from {source_str}: {e}")
    
    async def _load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load manifest from file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Parsed YAML content
            
        Raises:
            ManifestError: If file loading fails
        """
        path = Path(file_path)
        
        # Resolve relative paths against base_path
        if not path.is_absolute():
            path = self.base_path / path
        
        if not path.exists():
            raise ManifestError(f"Manifest file not found: {path}")
        
        try:
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return yaml.safe_load(content) or {}
        except Exception as e:
            raise ManifestError(f"Failed to read manifest file {path}: {e}")
    
    async def _load_from_url(self, url: str) -> Dict[str, Any]:
        """Load manifest from URL.
        
        Args:
            url: URL to load from
            
        Returns:
            Parsed YAML content
            
        Raises:
            NetworkError: If network operation fails
        """
        await self._ensure_session()
        
        try:
            async with self._session.get(url) as response:
                if response.status == 404:
                    raise NetworkError(f"Manifest not found at URL: {url}", url, 404)
                elif response.status >= 400:
                    raise NetworkError(f"HTTP {response.status} error loading {url}", url, response.status)
                
                content = await response.text()
                return yaml.safe_load(content) or {}
                
        except asyncio.TimeoutError as e:
            raise NetworkError(f"Timeout loading manifest from {url}", url)
        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error loading {url}: {e}", url)
        except Exception as e:
            if isinstance(e, NetworkError):
                raise
            raise NetworkError(f"Failed to load manifest from {url}: {e}", url)
    
    async def _resolve_manifest_dependencies(self, 
                                           manifest: LoadedManifest,
                                           recursive: bool = True) -> None:
        """Resolve and load manifest dependencies.
        
        Args:
            manifest: Manifest to resolve dependencies for
            recursive: Whether to recursively resolve nested dependencies
        """
        content = manifest.content
        
        # Extract dependencies from various sections
        dependencies = []
        
        # Import manifests
        imports = content.get('imports', {})
        if 'manifests' in imports:
            dependencies.extend(imports['manifests'])
        
        # Template inheritance
        metadata = content.get('metadata', {})
        if 'extends' in metadata:
            dependencies.append(metadata['extends'])
            manifest.template_inheritance.append(metadata['extends'])
        
        # Add to dependency resolver
        for dep in dependencies:
            self.dependency_resolver.add_dependency(manifest.source_url, dep)
        
        manifest.dependencies = dependencies
        
        if not recursive or not dependencies:
            return
        
        # Load dependencies
        for dep in dependencies:
            try:
                # Resolve relative dependencies
                resolved_dep = self._resolve_dependency_path(dep, manifest.source_url)
                
                # Load dependency recursively
                dep_manifest = await self.load_manifest(resolved_dep, recursive=True)
                manifest.resolved_modules[dep] = dep_manifest.content
                
            except Exception as e:
                # Log warning but don't fail the main load
                print(f"Warning: Failed to load dependency {dep}: {e}")
    
    def _resolve_dependency_path(self, dependency: str, base_source: str) -> str:
        """Resolve dependency path relative to base source.
        
        Args:
            dependency: Dependency path to resolve
            base_source: Base source path or URL
            
        Returns:
            Resolved absolute path or URL
        """
        if self._is_url(dependency):
            return dependency
        
        if self._is_url(base_source):
            return urljoin(base_source, dependency)
        
        # File path resolution
        base_path = Path(base_source).parent if Path(base_source).is_file() else Path(base_source)
        resolved_path = base_path / dependency
        return str(resolved_path)
    
    def _is_url(self, source: str) -> bool:
        """Check if source is a URL.
        
        Args:
            source: Source string to check
            
        Returns:
            True if source is a URL
        """
        try:
            result = urlparse(source)
            return bool(result.scheme and result.netloc)
        except:
            return False
    
    async def load_multiple(self, 
                          sources: List[Union[str, Path]],
                          resolve_dependencies: bool = True) -> List[LoadedManifest]:
        """Load multiple manifests concurrently.
        
        Args:
            sources: List of sources to load from
            resolve_dependencies: Whether to resolve dependencies
            
        Returns:
            List of loaded manifests
        """
        tasks = [
            self.load_manifest(source, resolve_dependencies=resolve_dependencies)
            for source in sources
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        manifests = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Warning: Failed to load {sources[i]}: {result}")
            else:
                manifests.append(result)
        
        return manifests
    
    def get_dependency_order(self) -> List[str]:
        """Get dependency resolution order.
        
        Returns:
            List of manifest sources in dependency resolution order
            
        Raises:
            DependencyError: If circular dependencies detected
        """
        return self.dependency_resolver.get_resolution_order()
    
    async def clear_cache(self) -> None:
        """Clear manifest cache."""
        await self.cache_manager.clear()
        self.dependency_resolver.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get loader statistics.
        
        Returns:
            Dictionary with loader statistics
        """
        return {
            'cache_stats': self.cache_manager.get_stats(),
            'dependency_stats': self.dependency_resolver.get_stats(),
            'session_closed': self._session is None or self._session.closed
        }
