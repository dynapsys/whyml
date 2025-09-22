"""
WhyML Converters - Conversion Result Module

Provides the ConversionResult class for structured conversion output
with metadata, statistics, and validation information.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConversionResult:
    """Result of a manifest conversion operation."""
    
    content: str
    """Generated content from the conversion"""
    
    format: str
    """Target format of the conversion (html, react, vue, php)"""
    
    success: bool = True
    """Whether the conversion was successful"""
    
    errors: List[str] = None
    """List of errors encountered during conversion"""
    
    warnings: List[str] = None
    """List of warnings generated during conversion"""
    
    metadata: Optional[Dict[str, Any]] = None
    """Additional metadata about the conversion"""
    
    statistics: Optional[Dict[str, Any]] = None
    """Conversion statistics (processing time, content size, etc.)"""
    
    output_path: Optional[Path] = None
    """Path where the content was saved (if applicable)"""
    
    filename: Optional[str] = None
    """Filename for the converted content (for test compatibility)"""
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}
        if self.statistics is None:
            self.statistics = {}
    
    @property
    def has_errors(self) -> bool:
        """Check if conversion has errors."""
        return bool(self.errors)
    
    @property
    def has_warnings(self) -> bool:
        """Check if conversion has warnings."""
        return bool(self.warnings)
    
    @property
    def format_type(self) -> str:
        """Get format type - alias for format property for test compatibility."""
        return self.format
    
    def add_error(self, error: str):
        """Add an error to the result."""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to the result."""
        self.metadata[key] = value
    
    def add_statistic(self, key: str, value: Any):
        """Add a statistic to the result."""
        self.statistics[key] = value
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversion result."""
        return {
            'format': self.format,
            'success': self.success,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'content_length': len(self.content) if self.content else 0,
            'output_path': str(self.output_path) if self.output_path else None,
            'metadata': self.metadata,
            'statistics': self.statistics
        }
    
    def save_to_file(self, file_path: Path) -> bool:
        """Save the conversion content to a file.
        
        Args:
            file_path: Path where to save the content
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(self.content, encoding='utf-8')
            self.output_path = file_path
            self.add_statistic('saved_to_file', True)
            return True
        except Exception as e:
            self.add_error(f"Failed to save to file: {str(e)}")
            return False
    
    def __str__(self) -> str:
        """String representation of the conversion result."""
        status = "SUCCESS" if self.success else "FAILED"
        return f"ConversionResult({self.format}, {status}, {len(self.errors)} errors, {len(self.warnings)} warnings)"
    
    def __repr__(self) -> str:
        """Detailed representation of the conversion result."""
        return (f"ConversionResult(format='{self.format}', success={self.success}, "
                f"errors={len(self.errors)}, warnings={len(self.warnings)}, "
                f"content_length={len(self.content) if self.content else 0})")


# Factory functions for common result types

def success_result(content: str, format: str, **kwargs) -> ConversionResult:
    """Create a successful conversion result."""
    return ConversionResult(
        content=content,
        format=format,
        success=True,
        **kwargs
    )


def error_result(format: str, errors: List[str], **kwargs) -> ConversionResult:
    """Create a failed conversion result."""
    return ConversionResult(
        content="",
        format=format,
        success=False,
        errors=errors,
        **kwargs
    )


def partial_result(content: str, format: str, warnings: List[str], **kwargs) -> ConversionResult:
    """Create a partially successful conversion result with warnings."""
    return ConversionResult(
        content=content,
        format=format,
        success=True,
        warnings=warnings,
        **kwargs
    )
