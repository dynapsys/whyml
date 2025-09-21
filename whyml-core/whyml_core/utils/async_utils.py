"""
WhyML Core Async Utilities - Advanced async operations and file management

Provides comprehensive async utilities including file operations, HTTP requests,
context management, and concurrent processing with proper error handling.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, AsyncGenerator, Coroutine
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
import time
import logging
from ..exceptions import ProcessingError, NetworkError


class AsyncUtils:
    """Utility functions for async operations."""
    
    @staticmethod
    async def run_with_timeout(coro: Coroutine, timeout: float) -> Any:
        """Run coroutine with timeout.
        
        Args:
            coro: Coroutine to run
            timeout: Timeout in seconds
            
        Returns:
            Coroutine result
            
        Raises:
            ProcessingError: If timeout exceeded
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise ProcessingError(
                message=f"Operation timed out after {timeout} seconds",
                details={'timeout': timeout}
            )
    
    @staticmethod
    async def gather_with_limit(coroutines: List[Coroutine], 
                               limit: int = 10,
                               return_exceptions: bool = False) -> List[Any]:
        """Run coroutines with concurrency limit.
        
        Args:
            coroutines: List of coroutines to run
            limit: Maximum concurrent operations
            return_exceptions: Whether to return exceptions in results
            
        Returns:
            List of results
        """
        semaphore = asyncio.Semaphore(limit)
        
        async def limited_coro(coro):
            async with semaphore:
                return await coro
        
        limited_coroutines = [limited_coro(coro) for coro in coroutines]
        return await asyncio.gather(*limited_coroutines, return_exceptions=return_exceptions)
    
    @staticmethod
    async def retry_async(func: Callable, 
                         max_retries: int = 3,
                         delay: float = 1.0,
                         backoff_factor: float = 2.0,
                         exceptions: tuple = (Exception,)) -> Any:
        """Retry async function with exponential backoff.
        
        Args:
            func: Async function to retry
            max_retries: Maximum number of retries
            delay: Initial delay between retries
            backoff_factor: Multiplier for delay after each retry
            exceptions: Exception types to catch and retry
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        current_delay = delay
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func()
                else:
                    return func()
            except exceptions as e:
                last_exception = e
                if attempt < max_retries:
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor
                else:
                    raise last_exception
        
        return None
    
    @staticmethod
    async def process_in_batches(items: List[Any], 
                                batch_size: int,
                                processor: Callable,
                                max_concurrent: int = 5) -> List[Any]:
        """Process items in batches with concurrency control.
        
        Args:
            items: Items to process
            batch_size: Size of each batch
            processor: Async function to process each item
            max_concurrent: Maximum concurrent batches
            
        Returns:
            List of processed results
        """
        results = []
        
        # Split items into batches
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
        
        async def process_batch(batch):
            batch_results = []
            for item in batch:
                if asyncio.iscoroutinefunction(processor):
                    result = await processor(item)
                else:
                    result = processor(item)
                batch_results.append(result)
            return batch_results
        
        # Process batches with concurrency limit
        batch_coroutines = [process_batch(batch) for batch in batches]
        batch_results = await AsyncUtils.gather_with_limit(
            batch_coroutines, 
            limit=max_concurrent
        )
        
        # Flatten results
        for batch_result in batch_results:
            results.extend(batch_result)
        
        return results


class AsyncFileManager:
    """Advanced async file management with caching and safety features."""
    
    def __init__(self, cache_size: int = 100):
        """Initialize async file manager.
        
        Args:
            cache_size: Maximum number of cached file contents
        """
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, float] = {}
        self.max_cache_size = cache_size
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    @asynccontextmanager
    async def open_file(self, file_path: Union[str, Path], mode: str = 'r', **kwargs):
        """Async context manager for file operations.
        
        Args:
            file_path: Path to file
            mode: File open mode
            **kwargs: Additional arguments for aiofiles.open
            
        Yields:
            Async file object
        """
        path = Path(file_path)
        
        try:
            async with aiofiles.open(path, mode=mode, **kwargs) as file:
                yield file
        except Exception as e:
            raise ProcessingError(
                message=f"Failed to open file: {str(e)}",
                details={'file_path': str(file_path), 'mode': mode, 'error': str(e)}
            )
    
    async def read_file(self, file_path: Union[str, Path], 
                       encoding: str = 'utf-8',
                       use_cache: bool = True) -> str:
        """Read file content asynchronously.
        
        Args:
            file_path: Path to file
            encoding: File encoding
            use_cache: Whether to use cache
            
        Returns:
            File content as string
        """
        path_str = str(file_path)
        
        # Check cache if enabled
        if use_cache and path_str in self.cache:
            # Check if file was modified since cache
            path = Path(file_path)
            if path.exists():
                current_mtime = path.stat().st_mtime
                cache_time = self.cache_timestamps.get(path_str, 0)
                if current_mtime <= cache_time:
                    return self.cache[path_str]
        
        try:
            async with self.open_file(file_path, mode='r', encoding=encoding) as f:
                content = await f.read()
            
            # Update cache
            if use_cache:
                self._update_cache(path_str, content)
            
            return content
            
        except Exception as e:
            raise ProcessingError(
                message=f"Failed to read file: {str(e)}",
                details={'file_path': path_str, 'encoding': encoding, 'error': str(e)}
            )
    
    async def write_file(self, file_path: Union[str, Path], 
                        content: str,
                        encoding: str = 'utf-8',
                        create_dirs: bool = True) -> None:
        """Write content to file asynchronously.
        
        Args:
            file_path: Path to file
            content: Content to write
            encoding: File encoding
            create_dirs: Whether to create parent directories
        """
        path = Path(file_path)
        
        # Create parent directories if needed
        if create_dirs and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with self.open_file(path, mode='w', encoding=encoding) as f:
                await f.write(content)
            
            # Clear from cache since file was modified
            path_str = str(file_path)
            if path_str in self.cache:
                del self.cache[path_str]
                del self.cache_timestamps[path_str]
            
        except Exception as e:
            raise ProcessingError(
                message=f"Failed to write file: {str(e)}",
                details={'file_path': str(file_path), 'encoding': encoding, 'error': str(e)}
            )
    
    async def read_json_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Read and parse JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data
        """
        import json
        
        content = await self.read_file(file_path)
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ProcessingError(
                message=f"Invalid JSON file: {str(e)}",
                details={'file_path': str(file_path), 'json_error': str(e)}
            )
    
    async def write_json_file(self, file_path: Union[str, Path], 
                             data: Any,
                             indent: int = 2) -> None:
        """Write data to JSON file.
        
        Args:
            file_path: Path to JSON file
            data: Data to write
            indent: JSON indentation
        """
        import json
        
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            await self.write_file(file_path, content)
        except (TypeError, ValueError) as e:
            raise ProcessingError(
                message=f"Failed to serialize JSON: {str(e)}",
                details={'file_path': str(file_path), 'json_error': str(e)}
            )
    
    async def copy_file(self, source: Union[str, Path], 
                       destination: Union[str, Path]) -> None:
        """Copy file asynchronously.
        
        Args:
            source: Source file path
            destination: Destination file path
        """
        content = await self.read_file(source, use_cache=False)
        await self.write_file(destination, content)
    
    async def file_exists(self, file_path: Union[str, Path]) -> bool:
        """Check if file exists asynchronously.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file exists
        """
        path = Path(file_path)
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, path.exists
        )
    
    async def get_file_size(self, file_path: Union[str, Path]) -> int:
        """Get file size asynchronously.
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in bytes
        """
        path = Path(file_path)
        
        def _get_size():
            if path.exists():
                return path.stat().st_size
            return 0
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _get_size
        )
    
    async def list_files(self, directory: Union[str, Path], 
                        pattern: str = "*",
                        recursive: bool = False) -> List[Path]:
        """List files in directory asynchronously.
        
        Args:
            directory: Directory to scan
            pattern: File pattern to match
            recursive: Whether to search recursively
            
        Returns:
            List of matching file paths
        """
        dir_path = Path(directory)
        
        def _list_files():
            if recursive:
                return list(dir_path.rglob(pattern))
            else:
                return list(dir_path.glob(pattern))
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, _list_files
        )
    
    def _update_cache(self, path_str: str, content: str) -> None:
        """Update file cache with content.
        
        Args:
            path_str: File path as string
            content: File content
        """
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_path = min(self.cache_timestamps.keys(), 
                            key=lambda k: self.cache_timestamps[k])
            del self.cache[oldest_path]
            del self.cache_timestamps[oldest_path]
        
        self.cache[path_str] = content
        self.cache_timestamps[path_str] = time.time()
    
    def clear_cache(self) -> None:
        """Clear file cache."""
        self.cache.clear()
        self.cache_timestamps.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information.
        
        Returns:
            Cache statistics
        """
        return {
            'cached_files': len(self.cache),
            'max_cache_size': self.max_cache_size,
            'cache_paths': list(self.cache.keys())
        }


class AsyncHTTPManager:
    """Async HTTP client with retry and caching capabilities."""
    
    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        """Initialize HTTP manager.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get(self, url: str, **kwargs) -> str:
        """GET request with retry logic.
        
        Args:
            url: URL to request
            **kwargs: Additional request arguments
            
        Returns:
            Response text
        """
        if not self.session:
            raise ProcessingError("HTTP manager not initialized. Use as context manager.")
        
        async def make_request():
            async with self.session.get(url, **kwargs) as response:
                response.raise_for_status()
                return await response.text()
        
        try:
            return await AsyncUtils.retry_async(
                make_request,
                max_retries=self.max_retries,
                exceptions=(aiohttp.ClientError,)
            )
        except Exception as e:
            raise NetworkError(
                message=f"Failed to fetch URL: {str(e)}",
                details={'url': url, 'error': str(e)}
            )
    
    async def post(self, url: str, data: Any = None, json: Any = None, **kwargs) -> str:
        """POST request with retry logic.
        
        Args:
            url: URL to request
            data: Form data
            json: JSON data
            **kwargs: Additional request arguments
            
        Returns:
            Response text
        """
        if not self.session:
            raise ProcessingError("HTTP manager not initialized. Use as context manager.")
        
        async def make_request():
            async with self.session.post(url, data=data, json=json, **kwargs) as response:
                response.raise_for_status()
                return await response.text()
        
        try:
            return await AsyncUtils.retry_async(
                make_request,
                max_retries=self.max_retries,
                exceptions=(aiohttp.ClientError,)
            )
        except Exception as e:
            raise NetworkError(
                message=f"Failed to POST to URL: {str(e)}",
                details={'url': url, 'error': str(e)}
            )
    
    async def download_file(self, url: str, file_path: Union[str, Path]) -> None:
        """Download file from URL.
        
        Args:
            url: URL to download
            file_path: Local path to save file
        """
        if not self.session:
            raise ProcessingError("HTTP manager not initialized. Use as context manager.")
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                
                async with aiofiles.open(path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                        
        except Exception as e:
            raise NetworkError(
                message=f"Failed to download file: {str(e)}",
                details={'url': url, 'file_path': str(file_path), 'error': str(e)}
            )
