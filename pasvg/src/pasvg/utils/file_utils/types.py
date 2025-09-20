"""
File type definitions and related utilities.
"""
from enum import Enum
from typing import Dict, Optional

class FileType(Enum):
    """Supported file types in the system."""
    MANIFEST = "manifest"
    SOURCE_CODE = "source"
    CONFIGURATION = "config"
    STYLESHEET = "style"
    TEMPLATE = "template"
    DOCUMENTATION = "docs"
    BINARY = "binary"
    WEB = "web"
    CONTAINER = "container"
    BUILD = "build"
    UNKNOWN = "unknown"

# Map file extensions to FileType
EXTENSION_TO_TYPE: Dict[str, FileType] = {
    # Source code
    '.py': FileType.SOURCE_CODE,
    '.js': FileType.SOURCE_CODE,
    '.jsx': FileType.SOURCE_CODE,
    '.ts': FileType.SOURCE_CODE,
    '.tsx': FileType.SOURCE_CODE,
    '.java': FileType.SOURCE_CODE,
    '.c': FileType.SOURCE_CODE,
    '.cpp': FileType.SOURCE_CODE,
    '.h': FileType.SOURCE_CODE,
    '.hpp': FileType.SOURCE_CODE,
    '.go': FileType.SOURCE_CODE,
    '.rs': FileType.SOURCE_CODE,
    
    # Web
    '.html': FileType.WEB,
    '.htm': FileType.WEB,
    '.xhtml': FileType.WEB,
    
    # Styles
    '.css': FileType.STYLESHEET,
    '.scss': FileType.STYLESHEET,
    '.sass': FileType.STYLESHEET,
    '.less': FileType.STYLESHEET,
    
    # Configuration
    '.json': FileType.CONFIGURATION,
    '.yaml': FileType.CONFIGURATION,
    '.yml': FileType.CONFIGURATION,
    '.toml': FileType.CONFIGURATION,
    '.ini': FileType.CONFIGURATION,
    '.cfg': FileType.CONFIGURATION,
    '.env': FileType.CONFIGURATION,
    
    # Documentation
    '.md': FileType.DOCUMENTATION,
    '.rst': FileType.DOCUMENTATION,
    '.txt': FileType.DOCUMENTATION,
    
    # Binary
    '.png': FileType.BINARY,
    '.jpg': FileType.BINARY,
    '.jpeg': FileType.BINARY,
    '.gif': FileType.BINARY,
    '.bmp': FileType.BINARY,
    '.ico': FileType.BINARY,
    '.svg': FileType.BINARY,
    '.pdf': FileType.BINARY,
    '.zip': FileType.BINARY,
    '.tar': FileType.BINARY,
    '.gz': FileType.BINARY,
    '.exe': FileType.BINARY,
    '.dll': FileType.BINARY,
    '.so': FileType.BINARY,
    '.dylib': FileType.BINARY,
    '.mp3': FileType.BINARY,
    '.mp4': FileType.BINARY,
    '.avi': FileType.BINARY,
    '.mov': FileType.BINARY,
    '.wav': FileType.BINARY,
    '.flac': FileType.BINARY,
}

def get_file_type(filename: str) -> FileType:
    """
    Determine file type from filename.
    
    Args:
        filename: The filename to check
        
    Returns:
        The detected FileType
    """
    # Check for special filenames first
    name = filename.lower()
    if name in SPECIAL_FILENAMES:
        return SPECIAL_FILENAMES[name]
        
    # Check file extension
    ext = f".{name.split('.')[-1].lower()}" if '.' in name else ''
    return EXTENSION_TO_TYPE.get(ext, FileType.UNKNOWN)

def get_language_from_extension(extension: str) -> Optional[str]:
    """
    Get programming language from file extension.
    
    Args:
        extension: File extension (with or without dot)
        
    Returns:
        Language name or None if unknown
    """
    if not extension:
        return None
        
    # Ensure extension starts with a dot
    if not extension.startswith('.'):
        extension = f'.{extension}'
        
    return EXTENSION_TO_LANGUAGE.get(extension.lower())

# Special filenames that don't follow extension rules
SPECIAL_FILENAMES = {
    'dockerfile': FileType.CONTAINER,
    'makefile': FileType.BUILD,
    'readme': FileType.DOCUMENTATION,
    'license': FileType.DOCUMENTATION,
    'docker-compose.yml': FileType.CONTAINER,
    'docker-compose.yaml': FileType.CONTAINER,
}

# Map file extensions to programming languages
EXTENSION_TO_LANGUAGE = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.m': 'objective-c',
    '.mm': 'objective-c++',
    '.sh': 'shell',
    '.bash': 'shell',
    '.zsh': 'shell',
    '.fish': 'shell',
    '.ps1': 'powershell',
    '.bat': 'batch',
    '.cmd': 'batch',
    '.html': 'html',
    '.htm': 'html',
    '.xhtml': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.less': 'less',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.ini': 'ini',
    '.cfg': 'ini',
    '.md': 'markdown',
    '.rst': 'restructuredtext',
    '.txt': 'text',
    '.xml': 'xml',
    '.sql': 'sql',
    '.dockerfile': 'dockerfile',
    'dockerfile': 'dockerfile',
    'makefile': 'makefile',
}
