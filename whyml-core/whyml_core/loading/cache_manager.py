"""
WhyML Core Cache Manager - Advanced caching for manifest loading

Provides intelligent caching with TTL, dependency tracking, and async safety.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import asyncio
import hashlib
import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

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
            self._ttl = ttl
            
        @property
        def maxsize(self):
            return self._maxsize
            
        @property
        def ttl(self):
            return self._ttl
            
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

from ..exceptions import WhyMLError


class CacheError(WhyMLError):
    """Raised when cache operations fail."""
    pass


class CacheManager:
    """Advanced caching system for loaded manifests with async safety."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        """Initialize cache manager.
        
        Args:
            max_size: Maximum number of items to cache
            ttl_seconds: Time-to-live for cached items in seconds
        """
        self.cache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        self.loading_locks: Dict[str, asyncio.Lock] = {}
        self._lock = asyncio.Lock()
    
    @property
    def maxsize(self) -> int:
        """Get the maximum cache size."""
        return self.cache.maxsize
    
    @property
    def ttl(self) -> int:
        """Get the cache TTL."""
        return self.cache.ttl
    
    def _generate_cache_key(self, url: str, options: Optional[Dict[str, Any]] = None) -> str:
        """Generate a unique cache key for URL and options.
        
        Args:
            url: Source URL or path
            options: Optional loading options that affect the result
            
        Returns:
            Unique cache key string
        """
        key_data = {'url': url}
        if options:
            # Sort options for consistent key generation
            key_data['options'] = dict(sorted(options.items()))
        
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get(self, url: str, options: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Get item from cache if it exists and is valid.
        
        Args:
            url: Source URL or path
            options: Optional loading options
            
        Returns:
            Cached item or None if not found/expired
        """
        cache_key = self._generate_cache_key(url, options)
        
        async with self._lock:
            return self.cache.get(cache_key)
    
    async def set(self, url: str, value: Any, options: Optional[Dict[str, Any]] = None) -> None:
        """Store item in cache.
        
        Args:
            url: Source URL or path
            value: Value to cache
            options: Optional loading options
        """
        cache_key = self._generate_cache_key(url, options)
        
        async with self._lock:
            self.cache[cache_key] = value
    
    async def invalidate(self, url: str, options: Optional[Dict[str, Any]] = None) -> bool:
        """Remove specific item from cache.
        
        Args:
            url: Source URL or path
            options: Optional loading options
            
        Returns:
            True if item was removed, False if not found
        """
        cache_key = self._generate_cache_key(url, options)
        
        async with self._lock:
            if cache_key in self.cache:
                del self.cache[cache_key]
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cached items."""
        async with self._lock:
            self.cache.clear()
            self.loading_locks.clear()
    
    async def get_loading_lock(self, url: str, options: Optional[Dict[str, Any]] = None) -> asyncio.Lock:
        """Get or create a loading lock for preventing duplicate loads.
        
        Args:
            url: Source URL or path
            options: Optional loading options
            
        Returns:
            Asyncio lock for the given URL/options combination
        """
        cache_key = self._generate_cache_key(url, options)
        
        async with self._lock:
            if cache_key not in self.loading_locks:
                self.loading_locks[cache_key] = asyncio.Lock()
            return self.loading_locks[cache_key]
    
    async def cleanup_loading_locks(self) -> None:
        """Clean up unused loading locks to prevent memory leaks."""
        async with self._lock:
            # Remove locks that are not currently held
            to_remove = []
            for key, lock in self.loading_locks.items():
                if not lock.locked():
                    to_remove.append(key)
            
            for key in to_remove:
                del self.loading_locks[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'max_size': self.maxsize,
            'ttl_seconds': self.ttl,
            'current_size': len(self.cache._cache) if hasattr(self.cache, '_cache') else 0,
            'loading_locks': len(self.loading_locks)
        }
    
    async def preload(self, items: Dict[str, Any]) -> None:
        """Preload multiple items into cache.
        
        Args:
            items: Dictionary of {url: value} pairs to preload
        """
        async with self._lock:
            for url, value in items.items():
                cache_key = self._generate_cache_key(url)
                self.cache[cache_key] = value
    
    def __len__(self) -> int:
        """Get current number of cached items."""
        return len(self.cache._cache) if hasattr(self.cache, '_cache') else 0
    
    def __contains__(self, url: str) -> bool:
        """Check if URL is cached (without options)."""
        cache_key = self._generate_cache_key(url)
        return cache_key in self.cache
