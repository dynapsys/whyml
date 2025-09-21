"""
WhyML Core Path Utilities - Advanced path operations and file system utilities

Provides comprehensive path manipulation, resolution, and file system operations
with cross-platform compatibility and security features.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import os
import re
from pathlib import Path, PurePath
from typing import Union, List, Optional, Dict, Any, Generator
from urllib.parse import urlparse, unquote
from ..exceptions import ValidationError, ProcessingError


class PathUtils:
    """Utility functions for path operations and file system management."""
    
    @staticmethod
    def normalize_path(path: Union[str, Path]) -> Path:
        """Normalize path with proper separators and resolution.
        
        Args:
            path: Path to normalize
            
        Returns:
            Normalized Path object
        """
        if isinstance(path, str):
            # Handle URL-like paths
            if path.startswith(('http://', 'https://')):
                parsed = urlparse(path)
                return Path(unquote(parsed.path))
            
            # Handle Windows-style paths on Unix
            if '\\' in path:
                path = path.replace('\\', '/')
        
        path_obj = Path(path)
        
        # Resolve relative components
        try:
            return path_obj.resolve()
        except (OSError, RuntimeError):
            # Fallback for invalid paths
            return path_obj.expanduser().absolute()
    
    @staticmethod
    def safe_join(base_path: Union[str, Path], 
                  *sub_paths: Union[str, Path]) -> Path:
        """Safely join paths preventing directory traversal attacks.
        
        Args:
            base_path: Base directory path
            *sub_paths: Sub-paths to join
            
        Returns:
            Safely joined path
            
        Raises:
            ValidationError: If path traversal is detected
        """
        base = PathUtils.normalize_path(base_path)
        
        # Join all sub-paths
        result = base
        for sub_path in sub_paths:
            if isinstance(sub_path, str):
                # Check for dangerous patterns
                if '..' in sub_path or sub_path.startswith('/'):
                    raise ValidationError(
                        message=f"Unsafe path component detected: {sub_path}",
                        details={'base_path': str(base_path), 'sub_path': sub_path}
                    )
            
            result = result / sub_path
        
        # Ensure result is still under base path
        try:
            result.resolve().relative_to(base.resolve())
        except ValueError:
            raise ValidationError(
                message="Path traversal detected",
                details={'base_path': str(base_path), 'result_path': str(result)}
            )
        
        return result
    
    @staticmethod
    def get_relative_path(target: Union[str, Path], 
                         base: Union[str, Path]) -> Path:
        """Get relative path from base to target.
        
        Args:
            target: Target path
            base: Base path
            
        Returns:
            Relative path from base to target
        """
        target_path = PathUtils.normalize_path(target)
        base_path = PathUtils.normalize_path(base)
        
        try:
            return target_path.relative_to(base_path)
        except ValueError:
            # Paths are not relative, compute using os.path
            return Path(os.path.relpath(str(target_path), str(base_path)))
    
    @staticmethod
    def find_common_base(paths: List[Union[str, Path]]) -> Optional[Path]:
        """Find common base path for a list of paths.
        
        Args:
            paths: List of paths to analyze
            
        Returns:
            Common base path or None if no common base
        """
        if not paths:
            return None
        
        if len(paths) == 1:
            path = PathUtils.normalize_path(paths[0])
            return path.parent if path.is_file() else path
        
        # Normalize all paths
        normalized_paths = [PathUtils.normalize_path(p) for p in paths]
        
        # Get path parts for each path
        path_parts = [p.parts for p in normalized_paths]
        
        # Find common prefix
        if not path_parts:
            return None
        
        min_length = min(len(parts) for parts in path_parts)
        common_parts = []
        
        for i in range(min_length):
            part = path_parts[0][i]
            if all(parts[i] == part for parts in path_parts):
                common_parts.append(part)
            else:
                break
        
        if common_parts:
            return Path(*common_parts) if len(common_parts) > 1 else Path(common_parts[0])
        
        return None
    
    @staticmethod
    def validate_filename(filename: str, 
                         allow_spaces: bool = True,
                         max_length: int = 255) -> bool:
        """Validate filename for cross-platform compatibility.
        
        Args:
            filename: Filename to validate
            allow_spaces: Whether to allow spaces
            max_length: Maximum filename length
            
        Returns:
            True if filename is valid
        """
        if not filename or len(filename) > max_length:
            return False
        
        # Reserved names on Windows
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        if filename.upper() in reserved_names:
            return False
        
        # Invalid characters
        invalid_chars = '<>:"|?*'
        if any(char in filename for char in invalid_chars):
            return False
        
        # Control characters
        if any(ord(char) < 32 for char in filename):
            return False
        
        # Trailing periods or spaces on Windows
        if filename.endswith(('.', ' ')):
            return False
        
        # Check spaces if not allowed
        if not allow_spaces and ' ' in filename:
            return False
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str, 
                         replacement: str = '_',
                         max_length: int = 255) -> str:
        """Sanitize filename for cross-platform compatibility.
        
        Args:
            filename: Filename to sanitize
            replacement: Character to replace invalid characters
            max_length: Maximum filename length
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return 'untitled'
        
        # Replace invalid characters
        invalid_chars = '<>:"|?*\\'
        for char in invalid_chars:
            filename = filename.replace(char, replacement)
        
        # Replace control characters
        filename = re.sub(r'[\x00-\x1f\x7f]', replacement, filename)
        
        # Handle reserved names
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        if filename.upper() in reserved_names:
            filename = f"{filename}_{replacement}"
        
        # Remove trailing periods and spaces
        filename = filename.rstrip('. ')
        
        # Truncate if too long
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            max_name_length = max_length - len(ext)
            filename = name[:max_name_length] + ext
        
        # Ensure filename is not empty
        if not filename:
            filename = 'untitled'
        
        return filename
    
    @staticmethod
    def get_unique_path(path: Union[str, Path], 
                       suffix_format: str = "_{:03d}") -> Path:
        """Get unique path by adding numeric suffix if path exists.
        
        Args:
            path: Desired path
            suffix_format: Format string for numeric suffix
            
        Returns:
            Unique path that doesn't exist
        """
        path_obj = PathUtils.normalize_path(path)
        
        if not path_obj.exists():
            return path_obj
        
        # Split name and extension
        if path_obj.is_file() or '.' in path_obj.name:
            stem = path_obj.stem
            suffix = path_obj.suffix
        else:
            stem = path_obj.name
            suffix = ''
        
        parent = path_obj.parent
        counter = 1
        
        while True:
            new_name = f"{stem}{suffix_format.format(counter)}{suffix}"
            new_path = parent / new_name
            
            if not new_path.exists():
                return new_path
            
            counter += 1
    
    @staticmethod
    def ensure_directory(path: Union[str, Path], 
                        permissions: Optional[int] = None) -> Path:
        """Ensure directory exists, creating it if necessary.
        
        Args:
            path: Directory path to ensure
            permissions: Optional directory permissions (Unix only)
            
        Returns:
            Path to directory
        """
        dir_path = PathUtils.normalize_path(path)
        
        try:
            if permissions is not None:
                dir_path.mkdir(parents=True, exist_ok=True, mode=permissions)
            else:
                dir_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise ProcessingError(
                message=f"Failed to create directory: {str(e)}",
                details={'directory_path': str(dir_path), 'error': str(e)}
            )
        
        return dir_path
    
    @staticmethod
    def walk_directory(directory: Union[str, Path], 
                      pattern: Optional[str] = None,
                      recursive: bool = True,
                      include_dirs: bool = False) -> Generator[Path, None, None]:
        """Walk directory and yield matching paths.
        
        Args:
            directory: Directory to walk
            pattern: Optional glob pattern to match
            recursive: Whether to search recursively
            include_dirs: Whether to include directories in results
            
        Yields:
            Matching paths
        """
        dir_path = PathUtils.normalize_path(directory)
        
        if not dir_path.exists() or not dir_path.is_dir():
            return
        
        if recursive:
            search_pattern = f"**/{pattern}" if pattern else "**/*"
        else:
            search_pattern = pattern or "*"
        
        for path in dir_path.glob(search_pattern):
            if path.is_file() or (include_dirs and path.is_dir()):
                yield path
    
    @staticmethod
    def get_file_extension(path: Union[str, Path], 
                          include_dot: bool = True) -> str:
        """Get file extension from path.
        
        Args:
            path: File path
            include_dot: Whether to include the dot in extension
            
        Returns:
            File extension
        """
        path_obj = Path(path)
        extension = path_obj.suffix
        
        if not include_dot and extension.startswith('.'):
            extension = extension[1:]
        
        return extension.lower()
    
    @staticmethod
    def change_extension(path: Union[str, Path], 
                        new_extension: str) -> Path:
        """Change file extension.
        
        Args:
            path: Original file path
            new_extension: New extension (with or without dot)
            
        Returns:
            Path with new extension
        """
        path_obj = Path(path)
        
        if not new_extension.startswith('.'):
            new_extension = f".{new_extension}"
        
        return path_obj.with_suffix(new_extension)
    
    @staticmethod
    def get_size_recursive(path: Union[str, Path]) -> int:
        """Get total size of directory or file recursively.
        
        Args:
            path: Path to measure
            
        Returns:
            Total size in bytes
        """
        path_obj = PathUtils.normalize_path(path)
        
        if path_obj.is_file():
            return path_obj.stat().st_size
        elif path_obj.is_dir():
            total_size = 0
            for file_path in PathUtils.walk_directory(path_obj, recursive=True):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, FileNotFoundError):
                        # Skip files that can't be accessed
                        pass
            return total_size
        else:
            return 0
    
    @staticmethod
    def is_safe_path(path: Union[str, Path], 
                    base_directory: Optional[Union[str, Path]] = None) -> bool:
        """Check if path is safe (no directory traversal).
        
        Args:
            path: Path to check
            base_directory: Optional base directory to restrict to
            
        Returns:
            True if path is safe
        """
        try:
            path_obj = PathUtils.normalize_path(path)
            
            # Check for dangerous patterns
            path_str = str(path_obj)
            if '..' in path_str or path_str.startswith('/'):
                return False
            
            # Check against base directory if provided
            if base_directory:
                base_obj = PathUtils.normalize_path(base_directory)
                try:
                    path_obj.resolve().relative_to(base_obj.resolve())
                except ValueError:
                    return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_path_info(path: Union[str, Path]) -> Dict[str, Any]:
        """Get comprehensive information about a path.
        
        Args:
            path: Path to analyze
            
        Returns:
            Dictionary with path information
        """
        path_obj = PathUtils.normalize_path(path)
        
        info = {
            'path': str(path_obj),
            'name': path_obj.name,
            'parent': str(path_obj.parent),
            'exists': path_obj.exists(),
            'is_file': False,
            'is_dir': False,
            'is_symlink': False,
            'size': 0,
            'extension': PathUtils.get_file_extension(path_obj),
            'permissions': None
        }
        
        if path_obj.exists():
            try:
                stat = path_obj.stat()
                info.update({
                    'is_file': path_obj.is_file(),
                    'is_dir': path_obj.is_dir(),
                    'is_symlink': path_obj.is_symlink(),
                    'size': stat.st_size if path_obj.is_file() else PathUtils.get_size_recursive(path_obj),
                    'permissions': oct(stat.st_mode)[-3:],
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime,
                    'accessed': stat.st_atime
                })
            except OSError:
                # Handle permission errors gracefully
                pass
        
        return info
