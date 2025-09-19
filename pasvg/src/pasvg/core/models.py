"""
Core data models for PASVG system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum
import base64


class FileType(Enum):
    """Supported file types in PASVG."""
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


class TargetPlatform(Enum):
    """Supported target platforms."""
    CONTAINER = "Container"
    WEB_APPLICATION = "Web Application"
    DESKTOP = "Desktop"
    MOBILE_ANDROID = "Android"
    MOBILE_IOS = "iOS"
    SPA = "SPA"
    PWA = "Progressive Web App"
    APK = "APK"


@dataclass
class SourceFile:
    """Represents a source file embedded in PASVG."""
    filename: str
    content: str
    file_type: FileType
    language: str = ""
    section: str = ""
    size: int = 0
    encoding: str = "utf-8"
    
    def __post_init__(self):
        """Calculate file size after initialization."""
        if self.size == 0:
            if self.encoding == "base64":
                # For base64 content, calculate size of decoded content
                try:
                    decoded = base64.b64decode(self.content)
                    self.size = len(decoded)
                except Exception:
                    self.size = len(self.content)
            else:
                # For text content, calculate encoded size
                try:
                    self.size = len(self.content.encode(self.encoding))
                except (LookupError, UnicodeEncodeError):
                    self.size = len(self.content.encode('utf-8'))
    
    @property
    def is_binary(self) -> bool:
        """Check if file is binary based on encoding."""
        return self.encoding == "base64"


@dataclass
class PASVGMetadata:
    """Project metadata for PASVG files."""
    name: str
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    email: str = ""
    license: str = ""
    homepage: str = ""
    technologies: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    build_targets: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "email": self.email,
            "license": self.license,
            "homepage": self.homepage,
            "technologies": self.technologies,
            "platforms": self.platforms,
            "build_targets": self.build_targets,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PASVGMetadata":
        """Create metadata from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            author=data.get("author", ""),
            email=data.get("email", ""),
            license=data.get("license", ""),
            homepage=data.get("homepage", ""),
            technologies=data.get("technologies", []),
            platforms=data.get("platforms", []),
            build_targets=data.get("build_targets", []),
            tags=data.get("tags", []),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


@dataclass
class BuildConfig:
    """Build configuration for projects."""
    targets: List[str] = field(default_factory=list)
    commands: Dict[str, List[str]] = field(default_factory=dict)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: Dict[str, str] = field(default_factory=dict)
    ports: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert build config to dictionary."""
        return {
            "targets": self.targets,
            "commands": self.commands,
            "dependencies": self.dependencies,
            "environment": self.environment,
            "volumes": self.volumes,
            "ports": self.ports,
        }


@dataclass
class ProjectConfig:
    """Complete project configuration."""
    metadata: PASVGMetadata
    source_files: List[SourceFile] = field(default_factory=list)
    build_config: BuildConfig = field(default_factory=BuildConfig)
    svg_width: int = 1200
    svg_height: int = 800
    
    def add_source_file(self, file: SourceFile) -> None:
        """Add a source file to the project."""
        self.source_files.append(file)
    
    def get_files_by_type(self, file_type: FileType) -> List[SourceFile]:
        """Get all files of a specific type."""
        return [f for f in self.source_files if f.file_type == file_type]
    
    def get_file_by_name(self, filename: str) -> Optional[SourceFile]:
        """Get a file by its filename."""
        for file in self.source_files:
            if file.filename == filename:
                return file
        return None
    
    def total_size(self) -> int:
        """Calculate total size of all source files."""
        return sum(file.size for file in self.source_files)
    
    def file_count(self) -> int:
        """Get total number of source files."""
        return len(self.source_files)


@dataclass
class ValidationResult:
    """Result of PASVG validation."""
    is_valid: bool
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    metadata: Optional[PASVGMetadata] = None
    file_count: int = 0
    total_size: int = 0
    
    def add_error(self, message: str) -> None:
        """Add a validation error."""
        if self.errors is None:
            self.errors = []
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str) -> None:
        """Add a validation warning."""
        if self.warnings is None:
            self.warnings = []
        self.warnings.append(message)
    
    def has_errors(self) -> bool:
        """Check if there are validation errors."""
        return self.errors is not None and len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are validation warnings."""
        return self.warnings is not None and len(self.warnings) > 0


@dataclass
class ExtractionResult:
    """Result of PASVG extraction."""
    success: bool
    project_dir: Path
    extracted_files: List[str] = field(default_factory=list)
    metadata: Optional[PASVGMetadata] = None
    build_targets: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def add_error(self, message: str) -> None:
        """Add an extraction error."""
        self.errors.append(message)
        self.success = False
    
    def file_count(self) -> int:
        """Get number of extracted files."""
        return len(self.extracted_files)


@dataclass
class GenerationResult:
    """Result of PASVG generation."""
    success: bool
    pasvg_file: Optional[Path] = None
    metadata: Optional[PASVGMetadata] = None
    file_count: int = 0
    total_size: int = 0
    errors: List[str] = field(default_factory=list)
    
    def add_error(self, message: str) -> None:
        """Add a generation error."""
        self.errors.append(message)
        self.success = False


@dataclass
class BuildResult:
    """Result of project build operation."""
    success: bool
    built_targets: List[str] = field(default_factory=list)
    build_dir: Optional[Path] = None
    errors: List[str] = field(default_factory=list)
    
    def add_error(self, message: str) -> None:
        """Add a build error."""
        self.errors.append(message)
        self.success = False
