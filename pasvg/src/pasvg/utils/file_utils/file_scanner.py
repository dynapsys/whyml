"""
File scanning and directory traversal functionality.
"""
import fnmatch
import os
from pathlib import Path
from typing import List, Optional, Set, Iterator, Pattern, Union
import re

from .types import FileType
from .file_operations import FileOperations

class FileScanner:
    """Handles file system scanning and pattern matching."""
    
    def __init__(self, file_ops: Optional[FileOperations] = None):
        """Initialize with optional FileOperations instance."""
        self.file_ops = file_ops or FileOperations()
        self.ignored_patterns: Set[str] = {
            # Version control
            '.git', '.svn', '.hg',
            # Build artifacts
            'node_modules', '__pycache__', '.pytest_cache', 'dist', 'build',
            # IDE files
            '.vscode', '.idea', '*.swp', '*.swo',
            # System files
            '.DS_Store', 'Thumbs.db',
            # Log files
            '*.log', '*.tmp'
        }
    
    def scan_directory(
        self,
        directory: Union[str, Path],
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        max_depth: Optional[int] = None
    ) -> List[Path]:
        """
        Scan a directory for files matching the given patterns.
        
        Args:
            directory: Directory to scan
            include_patterns: List of glob patterns to include
            exclude_patterns: List of patterns to exclude
            max_depth: Maximum depth to scan (None for unlimited)
            
        Returns:
            List of matching file paths
        """
        directory = Path(directory)
        if not directory.is_dir():
            return []
            
        include_patterns = set(include_patterns or [])
        exclude_patterns = set(exclude_patterns or [])
        
        # Combine with default ignore patterns
        all_exclude_patterns = exclude_patterns.union(self.ignored_patterns)
        
        # Convert glob patterns to regex
        include_regex = self._compile_patterns(include_patterns) if include_patterns else None
        exclude_regex = self._compile_patterns(all_exclude_patterns)
        
        # Scan directory
        matching_files = []
        
        for root, _, files in os.walk(directory):
            current_depth = len(Path(root).relative_to(directory).parts)
            
            # Check max depth
            if max_depth is not None and current_depth > max_depth:
                continue
                
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(directory)
                rel_path_str = str(rel_path).replace('\\', '/')
                
                # Skip hidden files and directories
                if any(part.startswith('.') for part in rel_path.parts):
                    continue
                
                # Check exclude patterns
                if self._matches_any(rel_path_str, exclude_regex):
                    continue
                    
                # Check include patterns (if any)
                if include_regex and not self._matches_any(rel_path_str, include_regex):
                    continue
                    
                matching_files.append(file_path)
                
        return matching_files
    
    def _compile_patterns(self, patterns: Set[str]) -> List[Pattern]:
        """Compile glob patterns to regex patterns."""
        compiled = []
        for pattern in patterns:
            # Convert glob to regex
            regex = fnmatch.translate(pattern)
            compiled.append(re.compile(regex, re.IGNORECASE))
        return compiled
    
    def _matches_any(self, path: str, patterns: List[Pattern]) -> bool:
        """Check if path matches any of the compiled patterns."""
        return any(pattern.match(path) for pattern in patterns)
    
    def find_files_by_type(
        self,
        directory: Union[str, Path],
        file_types: List[FileType],
        recursive: bool = True
    ) -> List[Path]:
        """
        Find files of specific types in a directory.
        
        Args:
            directory: Directory to search in
            file_types: List of FileType enums to look for
            recursive: Whether to search recursively
            
        Returns:
            List of matching file paths
        """
        directory = Path(directory)
        if not directory.is_dir():
            return []
            
        # Convert file types to extensions
        extensions = []
        type_to_ext = {
            FileType.SOURCE_CODE: ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp', '.go', '.rs'],
            FileType.WEB: ['.html', '.htm', '.xhtml'],
            FileType.STYLESHEET: ['.css', '.scss', '.sass', '.less'],
            FileType.CONFIGURATION: ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.env'],
            FileType.DOCUMENTATION: ['.md', '.rst', '.txt'],
            FileType.BINARY: ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.pdf'],
            FileType.CONTAINER: ['.dockerfile'],
            FileType.BUILD: ['Makefile']
        }
        
        for file_type in file_types:
            extensions.extend(type_to_ext.get(file_type, []))
            
        # Convert to set for O(1) lookups
        extension_set = set(extensions)
        
        # Find files
        found_files = []
        
        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    if any(file.endswith(ext) for ext in extension_set):
                        found_files.append(Path(root) / file)
        else:
            for item in directory.iterdir():
                if item.is_file() and any(str(item).endswith(ext) for ext in extension_set):
                    found_files.append(item)
                    
        return found_files
    
    def get_directory_size(self, directory: Union[str, Path]) -> int:
        """
        Calculate total size of all files in a directory.
        
        Args:
            directory: Directory to calculate size for
            
        Returns:
            Total size in bytes
        """
        directory = Path(directory)
        if not directory.is_dir():
            return 0
            
        total_size = 0
        
        for item in directory.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
                
        return total_size
