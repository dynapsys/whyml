"""
Manifest Loader - Core system for loading and resolving modular YAML manifests

Supports URL-based loading, dependency resolution, template inheritance,
and comprehensive caching for optimal performance.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import os
import yaml
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Set
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta
import hashlib
import json
from dataclasses import dataclass
try:
    from cachetools import TTLCache
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False
    # Fallback simple cache implementation
    class TTLCache:
        def __init__(self, maxsize, ttl):
            self._cache = {}
            self._maxsize = maxsize
            
        def get(self, key, default=None):
            return self._cache.get(key, default)
            
        def __setitem__(self, key, value):
            if len(self._cache) >= self._maxsize:
                # Simple eviction - remove oldest
                if self._cache:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
            self._cache[key] = value
            
        def __getitem__(self, key):
            return self._cache[key]
            
        def __contains__(self, key):
            return key in self._cache
import logging

from .exceptions import (
    LoaderError, 
    ManifestError, 
    DependencyError, 
    CacheError,
    handle_yaml_error
)

logger = logging.getLogger(__name__)


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


class DependencyResolver:
    """Handles dependency resolution and circular dependency detection."""
    
    def __init__(self):
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.resolution_order: List[str] = []
    
    def add_dependency(self, module: str, depends_on: str) -> None:
        """Add a dependency relationship."""
        if module not in self.dependency_graph:
            self.dependency_graph[module] = set()
        self.dependency_graph[module].add(depends_on)
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the graph."""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependency_graph.get(node, []):
                dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        for node in self.dependency_graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def get_resolution_order(self) -> List[str]:
        """Get the topological order for dependency resolution."""
        in_degree = {node: 0 for node in self.dependency_graph}
        
        # Calculate in-degrees
        for node in self.dependency_graph:
            for dep in self.dependency_graph[node]:
                in_degree[dep] = in_degree.get(dep, 0) + 1
        
        # Kahn's algorithm
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in self.dependency_graph.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(self.dependency_graph):
            # Circular dependency exists
            cycles = self.detect_circular_dependencies()
            raise DependencyError(
                "Circular dependencies detected",
                circular_dependencies=[" -> ".join(cycle) for cycle in cycles]
            )
        
        return result


class ManifestCache:
    """Advanced caching system for loaded manifests."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.cache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        self.loading_locks: Dict[str, asyncio.Lock] = {}
    
    @property
    def maxsize(self) -> int:
        """Get the maximum cache size."""
        return self.cache.maxsize
    
    @property
    def ttl(self) -> int:
        """Get the cache TTL."""
        return self.cache.ttl
    
    def _generate_cache_key(self, url: str, options: Dict[str, Any]) -> str:
        """Generate a unique cache key for the request."""
        key_data = {
            'url': url,
            'options': sorted(options.items()) if options else []
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, url: str, options: Dict[str, Any] = None) -> Optional[LoadedManifest]:
        """Get a cached manifest."""
        cache_key = self._generate_cache_key(url, options or {})
        return self.cache.get(cache_key)
    
    async def set(self, url: str, manifest: LoadedManifest, options: Dict[str, Any] = None) -> None:
        """Cache a loaded manifest."""
        cache_key = self._generate_cache_key(url, options or {})
        manifest.cache_key = cache_key
        self.cache[cache_key] = manifest
    
    async def get_lock(self, url: str) -> asyncio.Lock:
        """Get a lock for preventing duplicate loading."""
        if url not in self.loading_locks:
            self.loading_locks[url] = asyncio.Lock()
        return self.loading_locks[url]
    
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        self.loading_locks.clear()
    
    def __contains__(self, cache_key: str) -> bool:
        """Check if a cache key exists in the cache."""
        return cache_key in self.cache


class ManifestLoader:
    """
    Core system for loading and resolving modular YAML manifests.
    
    Features:
    - URL-based and file-based loading
    - Dependency resolution and circular dependency detection
    - Template inheritance support
    - Comprehensive caching
    - Async loading for performance
    """
    
    def __init__(self, 
                 base_url: str = "",
                 base_dir: Union[str, Path] = None,
                 cache_ttl: int = 300,
                 cache_size: int = 1000,
                 max_depth: int = 10,
                 timeout: int = 30):
        """
        Initialize the manifest loader.
        
        Args:
            base_url: Base URL for resolving relative URLs
            base_dir: Base directory for resolving relative file paths
            cache_ttl: Cache time-to-live in seconds
            cache_size: Maximum number of items in cache
            max_depth: Maximum dependency resolution depth
            timeout: Timeout for network requests in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.max_depth = max_depth
        self.timeout = timeout
        
        self.cache = ManifestCache(cache_size, cache_ttl)
        self.resolver = DependencyResolver()
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _resolve_url(self, url: str, base: str = None) -> str:
        """Resolve a URL relative to a base URL or the loader's base URL."""
        if urlparse(url).scheme:
            return url  # Already absolute
        
        base = base or self.base_url
        if base:
            return urljoin(base, url)
        
        # If no base URL, treat as file path
        if not os.path.isabs(url):
            return str(self.base_dir / url)
        return url
    
    async def _load_from_url(self, url: str) -> str:
        """Load content from a URL."""
        if not self.session:
            raise LoaderError("Session not initialized. Use async context manager.")
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise LoaderError(
                        f"Failed to load manifest from URL",
                        url=url,
                        status_code=response.status
                    )
                return await response.text()
        except aiohttp.ClientError as e:
            raise LoaderError(f"Network error loading manifest: {e}", url=url)
    
    async def _load_from_file(self, file_path: str) -> str:
        """Load content from a file."""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        except FileNotFoundError:
            raise LoaderError(f"Manifest file not found: {file_path}", url=file_path)
        except IOError as e:
            raise LoaderError(f"Failed to read manifest file: {e}", url=file_path)
    
    async def _load_raw_content(self, url: str) -> str:
        """Load raw content from URL or file."""
        if urlparse(url).scheme in ('http', 'https'):
            return await self._load_from_url(url)
        else:
            return await self._load_from_file(url)
    
    def _parse_yaml(self, content: str, source_url: str) -> Dict[str, Any]:
        """Parse YAML content with error handling."""
        try:
            return yaml.safe_load(content) or {}
        except yaml.YAMLError as e:
            raise handle_yaml_error(e, source_url)
    
    def _extract_dependencies(self, manifest: Dict[str, Any]) -> List[str]:
        """Extract dependency URLs from a manifest."""
        dependencies = []
        
        # Check imports section
        imports = manifest.get('imports', {})
        if isinstance(imports, dict):
            for import_type in ['manifests', 'modules', 'templates']:
                items = imports.get(import_type, [])
                if isinstance(items, list):
                    dependencies.extend(items)
                elif isinstance(items, str):
                    dependencies.append(items)
        
        # Check template inheritance
        metadata = manifest.get('metadata', {})
        if 'extends' in metadata:
            dependencies.append(metadata['extends'])
        
        # Check modules in structure
        def find_modules(obj):
            if isinstance(obj, dict):
                if 'module' in obj:
                    module_ref = obj['module']
                    if isinstance(module_ref, str) and module_ref.startswith('http'):
                        dependencies.append(module_ref)
                for value in obj.values():
                    find_modules(value)
            elif isinstance(obj, list):
                for item in obj:
                    find_modules(item)
        
        find_modules(manifest.get('structure', {}))
        
        return dependencies
    
    async def _resolve_dependencies(self, 
                                   manifest: Dict[str, Any], 
                                   source_url: str,
                                   depth: int = 0,
                                   loading_chain: List[str] = None) -> Dict[str, LoadedManifest]:
        """Recursively resolve all dependencies."""
        if depth >= self.max_depth:
            raise DependencyError(f"Maximum dependency depth ({self.max_depth}) exceeded")
        
        loading_chain = loading_chain or []
        if source_url in loading_chain:
            raise DependencyError(
                "Circular dependency detected",
                circular_dependencies=loading_chain + [source_url]
            )
        
        dependencies = self._extract_dependencies(manifest)
        resolved = {}
        
        for dep_url in dependencies:
            resolved_url = self._resolve_url(dep_url, source_url)
            
            # Add to dependency graph
            self.resolver.add_dependency(source_url, resolved_url)
            
            # Load dependency
            dep_manifest = await self.load_manifest(
                resolved_url,
                depth=depth + 1,
                loading_chain=loading_chain + [source_url]
            )
            resolved[dep_url] = dep_manifest
        
        return resolved
    
    async def load_manifest(self, 
                           url: str,
                           options: Dict[str, Any] = None,
                           depth: int = 0,
                           loading_chain: List[str] = None) -> LoadedManifest:
        """
        Load a manifest with full dependency resolution.
        
        Args:
            url: URL or file path to the manifest
            options: Loading options (e.g., ignore_cache, validate_schema)
            depth: Current loading depth (for recursion control)
            loading_chain: Chain of URLs being loaded (for circular dependency detection)
        
        Returns:
            LoadedManifest with resolved dependencies
        """
        options = options or {}
        loading_chain = loading_chain or []
        
        # Resolve the URL
        resolved_url = self._resolve_url(url)
        
        # Check cache first
        if not options.get('ignore_cache', False):
            cached = await self.cache.get(resolved_url, options)
            if cached:
                logger.debug(f"Cache hit for manifest: {resolved_url}")
                return cached
        
        # Prevent duplicate loading
        lock = await self.cache.get_lock(resolved_url)
        async with lock:
            # Double-check cache after acquiring lock
            if not options.get('ignore_cache', False):
                cached = await self.cache.get(resolved_url, options)
                if cached:
                    return cached
            
            logger.info(f"Loading manifest: {resolved_url}")
            
            # Load raw content
            raw_content = await self._load_raw_content(resolved_url)
            
            # Parse YAML
            manifest_data = self._parse_yaml(raw_content, resolved_url)
            
            # Process template inheritance if present
            if 'extends' in manifest_data:
                manifest_data = await self.expand_manifest(manifest_data, resolved_url)
            
            # Resolve dependencies
            resolved_modules = await self._resolve_dependencies(
                manifest_data, resolved_url, depth, loading_chain
            )
            
            # Create loaded manifest
            loaded_manifest = LoadedManifest(
                content=manifest_data,
                source_url=resolved_url,
                dependencies=self._extract_dependencies(manifest_data),
                load_time=datetime.now(),
                cache_key="",  # Will be set by cache
                resolved_modules=resolved_modules,
                template_inheritance=self._extract_template_chain(manifest_data)
            )
            
            # Cache the result
            await self.cache.set(resolved_url, loaded_manifest, options)
            
            logger.debug(f"Successfully loaded manifest: {resolved_url}")
            return loaded_manifest
    
    def _extract_template_chain(self, manifest: Dict[str, Any]) -> List[str]:
        """Extract the template inheritance chain."""
        chain = []
        current = manifest
        
        while current and isinstance(current, dict):
            metadata = current.get('metadata', {})
            extends = metadata.get('extends')
            if extends:
                chain.append(extends)
                # In a real implementation, we'd need to load the parent template
                # For now, just return the immediate parent
                break
            else:
                break
        
        return chain
    
    async def expand_manifest(self, manifest: Dict[str, Any], base_url: str = None) -> Dict[str, Any]:
        """
        Expand a manifest by resolving all imports and template inheritance.
        
        This creates a fully resolved manifest with all dependencies merged.
        """
        # Load the manifest if it's not already loaded
        if isinstance(manifest, str):
            loaded = await self.load_manifest(manifest)
            manifest = loaded.content
        
        # Start with a copy of the original manifest
        expanded = manifest.copy()
        
        # Process template inheritance first (bottom-up)
        # Check for extends at root level first, then in metadata
        extends_url = None
        if 'extends' in expanded:
            extends_url = expanded['extends']
        elif 'metadata' in expanded and 'extends' in expanded['metadata']:
            extends_url = expanded['metadata']['extends']
        
        if extends_url:
            # Resolve the extends URL relative to the base URL
            resolved_extends_url = self._resolve_url(extends_url, base_url)
            parent_loaded = await self.load_manifest(resolved_extends_url)
            parent_expanded = await self.expand_manifest(parent_loaded.content, resolved_extends_url)
            
            # Merge parent into current (parent provides defaults)
            expanded = self._merge_manifests(parent_expanded, expanded)
            
            # Remove the extends field as it's been processed
            if 'extends' in expanded:
                del expanded['extends']
        
        # Process imports and modules
        resolved_modules = {}
        imports = expanded.get('imports', {})
        
        for import_type, import_list in imports.items():
            if not isinstance(import_list, list):
                import_list = [import_list]
            
            for module_url in import_list:
                module_loaded = await self.load_manifest(module_url)
                module_expanded = await self.expand_manifest(module_loaded.content)
                resolved_modules[module_url] = module_expanded
        
        # Store resolved modules for reference
        expanded['_resolved_modules'] = resolved_modules
        
        return expanded
    
    def _merge_manifests(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two manifests with override taking precedence.
        
        This implements the template inheritance logic where child manifests
        can override or extend parent manifest properties.
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursive merge for dictionaries
                result[key] = self._merge_manifests(result[key], value)
            else:
                # Direct override for other types
                result[key] = value
        
        return result
    
    def clear_cache(self) -> None:
        """Clear the manifest cache."""
        self.cache.clear()
    
    def get_dependency_graph(self) -> Dict[str, Set[str]]:
        """Get the current dependency graph."""
        return self.resolver.dependency_graph.copy()
    
    async def validate_dependencies(self) -> List[str]:
        """Validate the dependency graph and return any issues."""
        issues = []
        
        # Check for circular dependencies
        try:
            self.resolver.get_resolution_order()
        except DependencyError as e:
            issues.extend(e.details.get('circular_dependencies', []))
        
        return issues
    
    def _generate_cache_key(self, url: str, options: Dict[str, Any] = None) -> str:
        """Generate a cache key for the given URL and options."""
        options = options or {}
        # Use the cache's key generation method for consistency
        return self.cache._generate_cache_key(url, options)
