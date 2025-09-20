"""
Core file operations for the application.
"""
import os
import base64
import shutil
from pathlib import Path
from typing import Union, Optional, Tuple, BinaryIO, Generator

from pasvg.core.models import SourceFile
from .types import FileType, get_file_type, get_language_from_extension

class FileOperations:
    """Handles core file operations."""
    
    def __init__(self, max_file_size: int = 10 * 1024 * 1024):
        """Initialize with optional max file size (default: 10MB)."""
        self.max_file_size = max_file_size
    
    def read_file(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        Read file content safely.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as string or None if reading fails
        """
        result = self.read_file_content(file_path)
        return result[0] if result else None
    
    def read_file_content(self, file_path: Union[str, Path]) -> Optional[Tuple[str, str]]:
        """
        Read file content safely with encoding detection.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Tuple of (content, encoding) or None if reading fails
        """
        try:
            file_path = Path(file_path)
            if not file_path.is_file():
                return None
                
            # Check file size
            if file_path.stat().st_size > self.max_file_size:
                return None
                
            # Try to read as text first
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read(), 'utf-8'
            except UnicodeDecodeError:
                # Fall back to binary if text reading fails
                with open(file_path, 'rb') as f:
                    content = f.read()
                    return base64.b64encode(content).decode('ascii'), 'base64'
                    
        except (OSError, IOError, ValueError):
            return None
    
    def write_file(self, file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
        """
        Write content to a file, creating directories if needed.
        
        Args:
            file_path: Path where to write the file
            content: Content to write
            encoding: Encoding to use ('utf-8' or 'base64')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if encoding == 'base64':
                with open(file_path, 'wb') as f:
                    f.write(base64.b64decode(content))
            else:
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(content)
            return True
            
        except (OSError, IOError, ValueError, base64.binascii.Error):
            return False
    
    def is_binary_file(self, file_path: Union[str, Path]) -> bool:
        """
        Check if a file is binary.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if the file is binary, False otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                # Read the first few bytes to check for binary content
                chunk = f.read(1024)
                return b'\x00' in chunk
        except (IOError, OSError):
            return False
    
    def read_binary_file(self, file_path: Union[str, Path], encode_base64: bool = False) -> Optional[Union[bytes, str]]:
        """
        Read a binary file, optionally encoding as base64.
        
        Args:
            file_path: Path to the file
            encode_base64: Whether to encode the content as base64
            
        Returns:
            File content as bytes or base64-encoded string, or None if reading fails
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                if encode_base64:
                    return base64.b64encode(content).decode('ascii')
                return content
        except (IOError, OSError, ValueError):
            return None
    
    def copy_file(self, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """
        Copy a file from src to dst, creating directories if needed.
        
        Args:
            src: Source file path
            dst: Destination file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.is_file():
                return False
                
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            return True
            
        except (OSError, IOError):
            return False
    
    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            if file_path.is_file():
                file_path.unlink()
                return True
            return False
        except OSError:
            return False
    
    def create_source_file(self, file_path: Union[str, Path], base_dir: Optional[Union[str, Path]] = None) -> Optional[SourceFile]:
        """
        Create a SourceFile object from a file path.
        
        Args:
            file_path: Path to the source file
            base_dir: Optional base directory to calculate relative paths
            
        Returns:
            SourceFile object or None if creation fails
        """
        try:
            file_path = Path(file_path)
            if not file_path.is_file():
                return None
                
            # Get relative path if base_dir is provided
            rel_path = str(file_path.relative_to(base_dir)) if base_dir else file_path.name
            
            # Read file content
            content, encoding = self.read_file_content(file_path) or (None, None)
            if content is None:
                return None
                
            # Determine file type and language
            file_type = get_file_type(file_path.name)
            language = get_language_from_extension(file_path.suffix)
            
            # Create and return SourceFile
            return SourceFile(
                filename=str(rel_path),
                content=content,
                file_type=file_type,
                language=language or '',
                encoding=encoding or 'utf-8',
                size=len(content)
            )
            
        except (ValueError, OSError):
            return None
