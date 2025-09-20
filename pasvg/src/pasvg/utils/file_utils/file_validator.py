"""
File validation and path sanitization utilities.
"""
import re
import os
from pathlib import Path
from typing import Set, List, Optional, Pattern, Union

class FileValidator:
    """Handles file path validation and sanitization."""
    
    # Windows reserved filenames (case-insensitive)
    WINDOWS_RESERVED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'PT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    # Invalid characters in filenames (Windows + Unix)
    INVALID_CHARS = r'[<>:"/\\|?*\x00-\x1F]'
    
    # Compiled regex for invalid characters
    INVALID_CHARS_PATTERN = re.compile(INVALID_CHARS)
    
    def __init__(self):
        """Initialize the file validator."""
        self._compiled_patterns: List[Pattern] = []
    
    def is_valid_path(self, path: Union[str, Path]) -> bool:
        """
        Check if a file path is valid and safe.
        
        Args:
            path: The path to validate
            
        Returns:
            bool: True if the path is valid, False otherwise
        """
        try:
            path_str = str(path)
            
            # Check for empty path
            if not path_str.strip():
                return False
                
            # Check for path traversal attempts
            if '..' in Path(path_str).parts:
                return False
                
            # Check for invalid characters
            if self.INVALID_CHARS_PATTERN.search(path_str):
                return False
                
            # Check for reserved Windows filenames
            filename = Path(path_str).name
            if not filename.strip():
                return False
                
            # Check base name (without extension) against reserved names
            base_name = os.path.splitext(filename)[0].upper()
            if base_name in self.WINDOWS_RESERVED_NAMES:
                return False
                
            # Check if filename starts with a reserved name followed by a dot
            for reserved in self.WINDOWS_RESERVED_NAMES:
                if filename.upper().startswith(f"{reserved}."):
                    return False
                    
            # Check for absolute paths (if not allowed)
            if os.path.isabs(path_str) and not self._allow_absolute_paths():
                return False
                
            return True
            
        except (ValueError, OSError):
            return False
    
    def sanitize_filename(self, filename: str, replacement: str = '_') -> str:
        """
        Sanitize a filename by removing or replacing invalid characters.
        
        Args:
            filename: The filename to sanitize
            replacement: Character to replace invalid characters with
            
        Returns:
            str: Sanitized filename
        """
        if not filename:
            return 'unnamed'
            
        # Replace invalid characters
        safe = self.INVALID_CHARS_PATTERN.sub(replacement, filename)
        
        # Remove leading/trailing whitespace and dots
        safe = safe.strip('. ')
        
        # Ensure the filename is not empty after sanitization
        if not safe:
            return 'unnamed'
            
        # Check for reserved names
        base_name, ext = os.path.splitext(safe)
        if base_name.upper() in self.WINDOWS_RESERVED_NAMES:
            safe = f"{base_name}_{'file' if not ext else ext[1:]}{ext}"
            
        return safe
    
    def is_safe_to_create(self, path: Union[str, Path], check_exists: bool = True) -> bool:
        """
        Check if it's safe to create a file at the given path.
        
        Args:
            path: The path to check
            check_exists: Whether to check if the file already exists
            
        Returns:
            bool: True if safe to create, False otherwise
        """
        try:
            path = Path(path).resolve()
            
            # Check if path is valid
            if not self.is_valid_path(str(path)):
                return False
                
            # Check if file already exists
            if check_exists and path.exists():
                return False
                
            # Check parent directory
            parent = path.parent
            if not parent.exists():
                # Try to create parent directories as a test
                try:
                    parent.mkdir(parents=True, exist_ok=True)
                    parent.rmdir()  # Clean up
                except (OSError, IOError):
                    return False
                    
            return True
            
        except (ValueError, OSError):
            return False
    
    def find_available_filename(
        self,
        directory: Union[str, Path],
        base_name: str,
        extension: str = '',
        max_attempts: int = 100
    ) -> Optional[Path]:
        """
        Find an available filename in the given directory.
        
        Args:
            directory: Directory to create the file in
            base_name: Base name for the file
            extension: File extension (with or without dot)
            max_attempts: Maximum number of attempts to find an available name
            
        Returns:
            Path object with an available filename, or None if not found
        """
        directory = Path(directory)
        
        # Ensure extension starts with a dot
        if extension and not extension.startswith('.'):
            extension = f'.{extension}'
            
        # Sanitize base name
        base_name = self.sanitize_filename(base_name)
        
        # Try the exact name first
        if not (directory / f"{base_name}{extension}").exists():
            return directory / f"{base_name}{extension}"
            
        # Try with incrementing numbers
        for i in range(1, max_attempts + 1):
            candidate = directory / f"{base_name}_{i}{extension}"
            if not candidate.exists():
                return candidate
                
        return None
    
    def _allow_absolute_paths(self) -> bool:
        """
        Check if absolute paths are allowed.
        Can be overridden by subclasses to change behavior.
        """
        return False
