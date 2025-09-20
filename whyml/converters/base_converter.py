"""
Base Converter - Abstract base class for all format converters

Provides common functionality and interface for converting YAML manifests
to various output formats with extensible architecture.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
import logging

from ..exceptions import ConversionError, ValidationError

logger = logging.getLogger(__name__)


class ConversionResult:
    """Container for conversion results with metadata."""
    
    def __init__(self, 
                 content: str,
                 filename: str,
                 format_type: str,
                 metadata: Dict[str, Any] = None):
        """
        Initialize conversion result.
        
        Args:
            content: Generated content
            filename: Suggested filename for output
            format_type: Target format (html, react, vue, php)
            metadata: Additional metadata about the conversion
        """
        self.content = content
        self.filename = filename
        self.format_type = format_type
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.size = len(content.encode('utf-8'))
    
    def save_to_file(self, output_path: Union[str, Path]) -> Path:
        """Save conversion result to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.content)
        
        logger.info(f"Saved {self.format_type} output to {output_path}")
        return output_path
    
    def __str__(self) -> str:
        return f"ConversionResult({self.format_type}, {self.size} bytes)"


class BaseConverter(ABC):
    """
    Abstract base class for all format converters.
    
    Provides common functionality for converting YAML manifests to various
    output formats with consistent error handling and optimization.
    """
    
    def __init__(self, 
                 optimize_output: bool = True,
                 minify: bool = False,
                 include_comments: bool = True,
                 **kwargs):
        """
        Initialize base converter.
        
        Args:
            optimize_output: Whether to optimize generated code
            minify: Whether to minify the output
            include_comments: Whether to include generated comments
            **kwargs: Additional converter-specific options
        """
        self.optimize_output = optimize_output
        self.minify = minify
        self.include_comments = include_comments
        self.conversion_stats = {
            'conversions': 0,
            'errors': 0,
            'warnings': 0
        }
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the name of the target format."""
        pass
    
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Return the file extension for this format."""
        pass
    
    @abstractmethod
    def convert(self, manifest: Dict[str, Any], **kwargs) -> ConversionResult:
        """
        Convert a manifest to the target format.
        
        Args:
            manifest: Processed YAML manifest
            **kwargs: Additional conversion options
            
        Returns:
            ConversionResult containing generated content
        """
        pass
    
    def validate_manifest(self, manifest: Dict[str, Any]) -> None:
        """
        Validate manifest for conversion to this format.
        
        Args:
            manifest: Manifest to validate
            
        Raises:
            ValidationError: If manifest is invalid for this format
        """
        if not isinstance(manifest, dict):
            raise ValidationError("Manifest must be a dictionary")
        
        required_sections = ['metadata', 'structure']
        missing_sections = [section for section in required_sections 
                          if section not in manifest]
        
        if missing_sections:
            raise ValidationError(
                f"Missing required sections for {self.format_name} conversion",
                errors=[f"Missing section: {section}" for section in missing_sections]
            )
    
    def generate_filename(self, manifest: Dict[str, Any], base_name: str = None) -> str:
        """
        Generate appropriate filename for the converted output.
        
        Args:
            manifest: Source manifest
            base_name: Optional base name
            
        Returns:
            Generated filename with appropriate extension
        """
        if base_name:
            name = base_name
        else:
            metadata = manifest.get('metadata', {})
            name = metadata.get('title', 'untitled')
            
            # Sanitize filename
            name = re.sub(r'[^\w\-_.]', '_', name.lower())
        
        return f"{name}.{self.file_extension}"
    
    def extract_styles(self, manifest: Dict[str, Any]) -> Dict[str, str]:
        """Extract and process styles from manifest."""
        return manifest.get('styles', {})
    
    def extract_metadata(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from manifest."""
        return manifest.get('metadata', {})
    
    def extract_template_vars(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Extract template variables from manifest."""
        return manifest.get('template_vars', {})
    
    def replace_template_variables(self, content: str, template_vars: Dict[str, Any]) -> str:
        """
        Replace template variables in content.
        
        Replaces {{ variable_name }} placeholders with actual values from template_vars.
        
        Args:
            content: Content string containing template placeholders
            template_vars: Dictionary of variable names to values
            
        Returns:
            Content with template variables replaced
        """
        import re
        
        if not template_vars:
            return content
        
        def replace_var(match):
            var_name = match.group(1).strip()
            if var_name in template_vars:
                return str(template_vars[var_name])
            else:
                # Keep placeholder if variable not found
                return match.group(0)
        
        # Replace {{ variable_name }} with actual values
        pattern = r'\{\{\s*([^}]+)\s*\}\}'
        return re.sub(pattern, replace_var, content)
    
    def extract_imports(self, manifest: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract imports from manifest."""
        imports = manifest.get('imports', {})
        if not isinstance(imports, dict):
            return {}
        
        # Normalize imports to lists
        normalized = {}
        for key, value in imports.items():
            if isinstance(value, str):
                normalized[key] = [value]
            elif isinstance(value, list):
                normalized[key] = value
            else:
                normalized[key] = []
        
        return normalized
    
    def process_structure(self, structure: Dict[str, Any]) -> Any:
        """
        Process the manifest structure for conversion.
        
        This method should be overridden by specific converters to handle
        format-specific structure processing.
        """
        return structure
    
    def optimize_code(self, code: str) -> str:
        """
        Apply format-specific optimizations to generated code.
        
        Args:
            code: Generated code to optimize
            
        Returns:
            Optimized code
        """
        if not self.optimize_output:
            return code
        
        # Basic optimizations (can be overridden by specific converters)
        
        # Remove extra whitespace
        lines = code.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            
            # Skip empty lines if minifying
            if self.minify and not line.strip():
                continue
            
            optimized_lines.append(line)
        
        # Remove consecutive empty lines
        result_lines = []
        prev_empty = False
        
        for line in optimized_lines:
            is_empty = not line.strip()
            
            if is_empty and prev_empty and self.minify:
                continue
            
            result_lines.append(line)
            prev_empty = is_empty
        
        return '\n'.join(result_lines)
    
    def add_header_comment(self, content: str, manifest: Dict[str, Any]) -> str:
        """
        Add header comment to generated content.
        
        Args:
            content: Generated content
            manifest: Source manifest
            
        Returns:
            Content with header comment
        """
        if not self.include_comments:
            return content
        
        metadata = self.extract_metadata(manifest)
        title = metadata.get('title', 'Untitled')
        description = metadata.get('description', '')
        
        header = self._format_header_comment(title, description)
        return f"{header}\n\n{content}"
    
    def _format_header_comment(self, title: str, description: str) -> str:
        """Format header comment for specific format (to be overridden)."""
        return f"/* Generated by WhyML - {title} */"
    
    def handle_conversion_error(self, error: Exception, context: str = "") -> ConversionError:
        """
        Handle and format conversion errors.
        
        Args:
            error: Original error
            context: Additional context information
            
        Returns:
            Formatted ConversionError
        """
        self.conversion_stats['errors'] += 1
        
        return ConversionError(
            f"Conversion to {self.format_name} failed: {str(error)}",
            source_format="yaml",
            target_format=self.format_name,
            context=context,
            original_error=str(error)
        )
    
    def log_warning(self, message: str, details: Dict[str, Any] = None):
        """Log a conversion warning."""
        self.conversion_stats['warnings'] += 1
        logger.warning(f"{self.format_name} converter: {message}", extra=details or {})
    
    def get_conversion_stats(self) -> Dict[str, int]:
        """Get conversion statistics."""
        return self.conversion_stats.copy()
    
    def reset_stats(self) -> None:
        """Reset conversion statistics."""
        self.conversion_stats = {'conversions': 0, 'errors': 0, 'warnings': 0}
    
    def convert_safe(self, manifest: Dict[str, Any], **kwargs) -> ConversionResult:
        """
        Safe wrapper for conversion with error handling.
        
        Args:
            manifest: Manifest to convert
            **kwargs: Additional conversion options
            
        Returns:
            ConversionResult or raises ConversionError
        """
        try:
            self.validate_manifest(manifest)
            result = self.convert(manifest, **kwargs)
            self.conversion_stats['conversions'] += 1
            return result
        except Exception as e:
            raise self.handle_conversion_error(e, f"Converting {self.format_name}")


class StructureWalker:
    """
    Utility class for walking through manifest structure trees.
    
    Provides methods for traversing and transforming nested structure
    elements in a consistent way across different converters.
    """
    
    def __init__(self, converter: BaseConverter):
        """Initialize with reference to converter."""
        self.converter = converter
    
    def walk(self, element: Any, callback, parent_context: Dict[str, Any] = None) -> Any:
        """
        Walk through structure element and apply callback.
        
        Args:
            element: Structure element to walk
            callback: Function to call for each element
            parent_context: Context from parent element
            
        Returns:
            Transformed element
        """
        context = parent_context or {}
        
        if isinstance(element, dict):
            return self._walk_dict(element, callback, context)
        elif isinstance(element, list):
            return self._walk_list(element, callback, context)
        else:
            return callback(element, context)
    
    def _walk_dict(self, element: Dict[str, Any], callback, context: Dict[str, Any]) -> Dict[str, Any]:
        """Walk through dictionary element."""
        result = {}
        
        # Update context with current element
        new_context = context.copy()
        new_context.update({
            'element_type': 'dict',
            'element': element
        })
        
        for key, value in element.items():
            if key == 'children':
                # Special handling for children
                if isinstance(value, list):
                    result[key] = [self.walk(child, callback, new_context) for child in value]
                else:
                    result[key] = self.walk(value, callback, new_context)
            else:
                result[key] = self.walk(value, callback, new_context)
        
        return callback(result, new_context)
    
    def _walk_list(self, element: List[Any], callback, context: Dict[str, Any]) -> List[Any]:
        """Walk through list element."""
        new_context = context.copy()
        new_context.update({
            'element_type': 'list',
            'element': element
        })
        
        result = [self.walk(item, callback, new_context) for item in element]
        return callback(result, new_context)
    
    def find_elements(self, structure: Any, predicate) -> List[Any]:
        """Find all elements matching predicate."""
        found = []
        
        def find_callback(element, context):
            if predicate(element, context):
                found.append(element)
            return element
        
        self.walk(structure, find_callback)
        return found
    
    def transform_elements(self, structure: Any, transformer) -> Any:
        """Transform elements using transformer function."""
        return self.walk(structure, transformer)


class CSSProcessor:
    """Utility class for processing CSS styles."""
    
    @staticmethod
    def parse_style_string(style_string: str) -> Dict[str, str]:
        """Parse CSS style string into property dict."""
        properties = {}
        
        if not style_string:
            return properties
        
        # Split by semicolon and process each property
        for prop in style_string.split(';'):
            prop = prop.strip()
            if ':' in prop:
                key, value = prop.split(':', 1)
                properties[key.strip()] = value.strip()
        
        return properties
    
    @staticmethod
    def format_style_string(properties: Dict[str, str]) -> str:
        """Format property dict back to CSS style string."""
        return '; '.join(f"{key}: {value}" for key, value in properties.items())
    
    @staticmethod
    def merge_styles(*style_strings: str) -> str:
        """Merge multiple CSS style strings."""
        merged_props = {}
        
        for style_string in style_strings:
            props = CSSProcessor.parse_style_string(style_string)
            merged_props.update(props)
        
        return CSSProcessor.format_style_string(merged_props)
    
    @staticmethod
    def minify_css(css: str) -> str:
        """Basic CSS minification."""
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        
        # Remove extra whitespace
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r';\s*}', '}', css)
        css = re.sub(r'{\s*', '{', css)
        css = re.sub(r';\s*', ';', css)
        
        return css.strip()
