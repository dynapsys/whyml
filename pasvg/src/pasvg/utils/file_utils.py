"""
File utilities for PASVG system.
"""

import os
import re
import mimetypes
from pathlib import Path
from typing import List, Dict, Optional, Set
import base64

from pasvg.core.models import SourceFile, FileType


class FileProcessor:
    """Handles file operations and processing for PASVG system."""
    
    def __init__(self):
        self.ignored_patterns = {
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
        
        self.binary_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
            '.pdf', '.zip', '.tar', '.gz', '.exe', '.dll', '.so',
            '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac'
        }
        
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
    
    def scan_directory(self, directory: Path, 
                      max_files: int = 100) -> List[SourceFile]:
        """Scan directory and return list of source files."""
        source_files = []
        
        if not directory.exists() or not directory.is_dir():
            return source_files
        
        file_count = 0
        for file_path in self._walk_directory(directory):
            if file_count >= max_files:
                break
            
            if self._should_ignore_file(file_path):
                continue
            
            try:
                source_file = self._create_source_file(file_path, directory)
                if source_file:
                    source_files.append(source_file)
                    file_count += 1
            except Exception as e:
                print(f"Warning: Could not process file {file_path}: {e}")
        
        return source_files
    
    def write_file(self, project_dir: Path, filename: str, content: str):
        """Write file to project directory, creating subdirectories as needed."""
        file_path = project_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def read_file(self, file_path: Path) -> Optional[str]:
        """Read file content safely."""
        try:
            # Check file size
            if file_path.stat().st_size > self.max_file_size:
                return None
            
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ['latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
        except Exception:
            pass
        
        return None
    
    def is_binary_file(self, file_path: Path) -> bool:
        """Check if file is binary."""
        # Check extension first
        if file_path.suffix.lower() in self.binary_extensions:
            return True
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and not mime_type.startswith('text/'):
            return True
        
        # Check file content (sample first 1024 bytes)
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\x00' in chunk:  # Null bytes indicate binary
                    return True
        except Exception:
            return True
        
        return False
    
    def get_file_type(self, file_path: Path) -> FileType:
        """Determine file type based on path and content."""
        filename = file_path.name.lower()
        suffix = file_path.suffix.lower()
        
        # Specific filenames
        if filename in ['dockerfile', 'docker-compose.yml', 'docker-compose.yaml']:
            return FileType.CONTAINER
        elif filename in ['package.json', 'pyproject.toml', 'cargo.toml']:
            return FileType.CONFIGURATION
        elif filename in ['readme.md', 'readme.txt']:
            return FileType.DOCUMENTATION
        
        # Extensions
        elif suffix in ['.yaml', '.yml']:
            return FileType.MANIFEST
        elif suffix in ['.json', '.toml', '.ini', '.cfg', '.conf']:
            return FileType.CONFIGURATION
        elif suffix in ['.css', '.scss', '.sass', '.less']:
            return FileType.STYLESHEET
        elif suffix in ['.html', '.htm']:
            return FileType.WEB
        elif suffix in ['.js', '.ts', '.py', '.php', '.java', '.cpp', '.c', '.rs']:
            return FileType.SOURCE_CODE
        elif suffix in ['.md', '.txt', '.rst']:
            return FileType.DOCUMENTATION
        elif suffix in ['.sh', '.bat', '.ps1']:
            return FileType.BUILD
        elif self.is_binary_file(file_path):
            return FileType.BINARY
        
        return FileType.SOURCE_CODE
    
    def get_language(self, file_path: Path) -> str:
        """Get programming language from file extension."""
        suffix = file_path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.php': 'php',
            '.html': 'html',
            '.css': 'css',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.sql': 'sql',
            '.sh': 'bash',
            '.bat': 'batch',
            '.ps1': 'powershell',
            '.md': 'markdown',
            '.rst': 'restructuredtext',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rs': 'rust',
            '.go': 'go',
            '.rb': 'ruby',
            '.perl': 'perl',
            '.toml': 'toml',
            '.ini': 'ini',
        }
        
        return language_map.get(suffix, '')
    
    def encode_binary_file(self, file_path: Path) -> str:
        """Encode binary file as base64 string."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return base64.b64encode(content).decode('ascii')
        except Exception:
            return ""
    
    def _walk_directory(self, directory: Path):
        """Walk directory recursively, yielding file paths."""
        try:
            for root, dirs, files in os.walk(directory):
                # Filter out ignored directories
                dirs[:] = [d for d in dirs if not self._should_ignore_path(d)]
                
                root_path = Path(root)
                for file in files:
                    if not self._should_ignore_path(file):
                        yield root_path / file
        except PermissionError:
            pass  # Skip directories we can't read
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        # Check file size
        try:
            if file_path.stat().st_size > self.max_file_size:
                return True
        except OSError:
            return True
        
        # Check ignored patterns
        return self._should_ignore_path(file_path.name)
    
    def _should_ignore_path(self, path_name: str) -> bool:
        """Check if path matches ignored patterns."""
        path_lower = path_name.lower()
        
        for pattern in self.ignored_patterns:
            if pattern.startswith('*'):
                # Wildcard pattern
                if path_lower.endswith(pattern[1:]):
                    return True
            elif pattern in path_lower:
                return True
        
        return False
    
    def _create_source_file(self, file_path: Path, base_dir: Path) -> Optional[SourceFile]:
        """Create SourceFile from file path."""
        try:
            # Get relative path
            rel_path = file_path.relative_to(base_dir)
            filename = str(rel_path).replace('\\', '/')
            
            # Read content
            if self.is_binary_file(file_path):
                content = self.encode_binary_file(file_path)
                if not content:
                    return None
            else:
                content = self.read_file(file_path)
                if content is None:
                    return None
            
            # Create source file
            return SourceFile(
                filename=filename,
                content=content,
                file_type=self.get_file_type(file_path),
                language=self.get_language(file_path),
                section="",
                size=len(content.encode('utf-8'))
            )
        except Exception:
            return None


class FileValidator:
    """Validates files for inclusion in PASVG."""
    
    def __init__(self):
        self.max_total_size = 100 * 1024 * 1024  # 100MB total
        self.max_file_count = 1000
        self.required_files = {'readme.md', 'readme.txt'}  # At least one should exist
    
    def validate_files(self, source_files: List[SourceFile]) -> Dict[str, List[str]]:
        """Validate list of source files."""
        issues = {'errors': [], 'warnings': []}
        
        # Check file count
        if len(source_files) == 0:
            issues['errors'].append("No source files found")
            return issues
        
        if len(source_files) > self.max_file_count:
            issues['warnings'].append(f"Large number of files: {len(source_files)}")
        
        # Check total size
        total_size = sum(f.size for f in source_files)
        if total_size > self.max_total_size:
            issues['errors'].append(f"Total size too large: {total_size / 1024 / 1024:.1f}MB")
        
        # Check for duplicates
        filenames = [f.filename for f in source_files]
        duplicates = set([f for f in filenames if filenames.count(f) > 1])
        if duplicates:
            issues['errors'].extend([f"Duplicate file: {f}" for f in duplicates])
        
        # Check for documentation
        has_readme = any(f.filename.lower().startswith('readme') for f in source_files)
        if not has_readme:
            issues['warnings'].append("No README file found")
        
        # Check file content
        empty_files = [f.filename for f in source_files if not f.content.strip()]
        if empty_files:
            issues['warnings'].extend([f"Empty file: {f}" for f in empty_files])
        
        return issues


class PathUtils:
    """Utility functions for path handling."""
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize path separators."""
        return path.replace('\\', '/')
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """Create safe filename by removing invalid characters."""
        # Remove/replace invalid characters
        safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
        safe = re.sub(r'\s+', '_', safe)
        return safe
    
    @staticmethod
    def get_common_prefix(paths: List[str]) -> str:
        """Get common prefix from list of paths."""
        if not paths:
            return ""
        
        common = os.path.commonpath(paths)
        return common
