"""
File utilities for the application.

This package provides various file-related utilities including:
- File operations (read/write/copy/delete)
- File type detection
- Directory scanning and pattern matching
- Path validation and sanitization
"""
from pathlib import Path
from typing import List, Optional, Set, Union, Dict, Any, Tuple

from .types import FileType, get_file_type, get_language_from_extension
from .file_operations import FileOperations
from .file_scanner import FileScanner
from .file_validator import FileValidator

# Re-export commonly used types and functions
__all__ = [
    'FileType',
    'FileOperations',
    'FileScanner',
    'FileValidator',
    'get_file_type',
    'get_language_from_extension',
]

# Create default instances for convenience
file_operations = FileOperations()
file_scanner = FileScanner(file_operations)
file_validator = FileValidator()

def read_file(file_path: Union[str, Path]) -> Optional[str]:
    """Read a file's content with default settings."""
    return file_operations.read_file(file_path)

def write_file(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """Write content to a file with default settings."""
    return file_operations.write_file(file_path, content, encoding)

def scan_directory(
    directory: Union[str, Path],
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    max_depth: Optional[int] = None
) -> List[Path]:
    """Scan a directory for files matching patterns."""
    return file_scanner.scan_directory(directory, include_patterns, exclude_patterns, max_depth)

def is_valid_path(path: Union[str, Path]) -> bool:
    """Check if a file path is valid and safe."""
    return file_validator.is_valid_path(path)

def sanitize_filename(filename: str, replacement: str = '_') -> str:
    """Sanitize a filename by removing or replacing invalid characters."""
    return file_validator.sanitize_filename(filename, replacement)
