"""
WhyML Converters - Base Converter Module

Abstract base class providing common functionality for all WhyML converters
with template processing, validation, and output generation capabilities.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from whyml_core.validation import ManifestValidator
from whyml_core.processing import TemplateProcessor, VariableSubstitution
from whyml_core.utils import StringUtils, PathUtils
from whyml_core.exceptions import ValidationError, ProcessingError


class BaseConverter(ABC):
    """Abstract base class for all WhyML converters."""
    
    def __init__(self, 
                 template_processor: Optional[TemplateProcessor] = None,
                 validator: Optional[ManifestValidator] = None):
        """Initialize base converter.
        
        Args:
            template_processor: Optional template processor instance
            validator: Optional manifest validator instance
        """
        self.template_processor = template_processor or TemplateProcessor()
        self.validator = validator or ManifestValidator()
        self.variable_substitution = VariableSubstitution(self.template_processor)
        
        # Converter-specific settings
        self.output_format = self._get_output_format()
        self.template_extension = self._get_template_extension()
        self.supports_components = self._supports_components()
    
    @abstractmethod
    def _get_output_format(self) -> str:
        """Get output format identifier.
        
        Returns:
            Format identifier string
        """
        pass
    
    @abstractmethod
    def _get_template_extension(self) -> str:
        """Get template file extension.
        
        Returns:
            File extension (e.g., '.html', '.jsx')
        """
        pass
    
    @abstractmethod
    def _supports_components(self) -> bool:
        """Check if converter supports component-based architecture.
        
        Returns:
            True if components are supported
        """
        pass
    
    @abstractmethod
    async def convert_manifest(self, 
                              manifest: Dict[str, Any],
                              output_path: Optional[Union[str, Path]] = None,
                              **options) -> str:
        """Convert manifest to target format.
        
        Args:
            manifest: WhyML manifest dictionary
            output_path: Optional output file path
            **options: Converter-specific options
            
        Returns:
            Generated content as string
        """
        pass
    
    async def validate_and_convert(self, 
                                  manifest: Dict[str, Any],
                                  output_path: Optional[Union[str, Path]] = None,
                                  validate: bool = True,
                                  **options) -> str:
        """Validate manifest and convert to target format.
        
        Args:
            manifest: WhyML manifest dictionary
            output_path: Optional output file path
            validate: Whether to validate manifest before conversion
            **options: Converter-specific options
            
        Returns:
            Generated content as string
        """
        # Validate manifest if requested
        if validate:
            await self._validate_manifest(manifest)
        
        # Process template variables
        processed_manifest = await self._process_template_variables(manifest)
        
        # Convert to target format
        content = await self.convert_manifest(
            processed_manifest,
            output_path=output_path,
            **options
        )
        
        # Post-process content
        content = await self._post_process_content(content, **options)
        
        # Save to file if path provided
        if output_path:
            await self._save_to_file(content, output_path)
        
        return content
    
    async def _validate_manifest(self, manifest: Dict[str, Any]) -> None:
        """Validate manifest structure and content.
        
        Args:
            manifest: Manifest to validate
            
        Raises:
            ValidationError: If manifest is invalid
        """
        try:
            await self.validator.validate_manifest(manifest)
        except Exception as e:
            raise ValidationError(
                message=f"Manifest validation failed: {str(e)}",
                details={'manifest_keys': list(manifest.keys()), 'error': str(e)}
            )
    
    async def _process_template_variables(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Process template variables in manifest.
        
        Args:
            manifest: Original manifest
            
        Returns:
            Manifest with processed template variables
        """
        return self.variable_substitution.substitute_template_vars(manifest)
    
    async def _post_process_content(self, content: str, **options) -> str:
        """Post-process generated content.
        
        Args:
            content: Generated content
            **options: Processing options
            
        Returns:
            Post-processed content
        """
        # Minify if requested
        if options.get('minify', False):
            content = await self._minify_content(content)
        
        # Format if requested
        if options.get('format', True):
            content = await self._format_content(content)
        
        return content
    
    async def _minify_content(self, content: str) -> str:
        """Minify content by removing unnecessary whitespace.
        
        Args:
            content: Content to minify
            
        Returns:
            Minified content
        """
        # Basic minification - remove extra whitespace
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    async def _format_content(self, content: str) -> str:
        """Format content for readability.
        
        Args:
            content: Content to format
            
        Returns:
            Formatted content
        """
        # Default implementation - return as-is
        # Subclasses can override for format-specific formatting
        return content
    
    async def _save_to_file(self, content: str, file_path: Union[str, Path]) -> None:
        """Save content to file.
        
        Args:
            content: Content to save
            file_path: Target file path
        """
        path = PathUtils.normalize_path(file_path)
        
        # Ensure directory exists
        PathUtils.ensure_directory(path.parent)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise ProcessingError(
                message=f"Failed to save file: {str(e)}",
                details={'file_path': str(file_path), 'error': str(e)}
            )
    
    def _extract_metadata(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from manifest.
        
        Args:
            manifest: WhyML manifest
            
        Returns:
            Metadata dictionary
        """
        return manifest.get('metadata', {})
    
    def _extract_structure(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structure from manifest.
        
        Args:
            manifest: WhyML manifest
            
        Returns:
            Structure dictionary
        """
        return manifest.get('structure', {})
    
    def _extract_styles(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Extract styles from manifest.
        
        Args:
            manifest: WhyML manifest
            
        Returns:
            Styles dictionary
        """
        return manifest.get('styles', {})
    
    def _extract_scripts(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Extract scripts from manifest.
        
        Args:
            manifest: WhyML manifest
            
        Returns:
            Scripts dictionary
        """
        return manifest.get('scripts', {})
    
    def _extract_imports(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Extract imports from manifest.
        
        Args:
            manifest: WhyML manifest
            
        Returns:
            Imports dictionary
        """
        return manifest.get('imports', {})
    
    def _generate_unique_id(self, prefix: str = "whyml") -> str:
        """Generate unique identifier.
        
        Args:
            prefix: ID prefix
            
        Returns:
            Unique identifier string
        """
        import uuid
        return f"{prefix}_{uuid.uuid4().hex[:8]}"
    
    def _sanitize_class_name(self, name: str) -> str:
        """Sanitize string for use as class/component name.
        
        Args:
            name: Original name
            
        Returns:
            Sanitized class name
        """
        # Remove special characters and convert to PascalCase
        sanitized = ''.join(word.capitalize() for word in name.split() if word.isalnum())
        
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = f"Component{sanitized}"
        
        return sanitized or "Component"
    
    def _sanitize_attribute_name(self, name: str) -> str:
        """Sanitize string for use as attribute name.
        
        Args:
            name: Original name
            
        Returns:
            Sanitized attribute name
        """
        # Convert to camelCase and remove invalid characters
        words = name.split()
        if not words:
            return "attr"
        
        # First word lowercase, subsequent words capitalized
        result = words[0].lower()
        for word in words[1:]:
            result += word.capitalize()
        
        # Remove non-alphanumeric characters
        result = ''.join(c for c in result if c.isalnum())
        
        # Ensure it starts with a letter
        if result and not result[0].isalpha():
            result = f"attr{result}"
        
        return result or "attr"
    
    def _process_external_content(self, 
                                 content: str,
                                 external_content: Dict[str, Any]) -> str:
        """Process external content references in template.
        
        Args:
            content: Template content with external references
            external_content: Dictionary of external content
            
        Returns:
            Content with external references resolved
        """
        import re
        
        def replace_external(match):
            filename = match.group(1).strip()
            return str(external_content.get(filename, f"<!-- External content not found: {filename} -->"))
        
        # Replace {{EXTERNAL:filename}} patterns
        pattern = r'\{\{EXTERNAL:([^}]+)\}\}'
        return re.sub(pattern, replace_external, content)
    
    def _get_converter_info(self) -> Dict[str, Any]:
        """Get converter information and capabilities.
        
        Returns:
            Converter information dictionary
        """
        return {
            'format': self.output_format,
            'template_extension': self.template_extension,
            'supports_components': self.supports_components,
            'class_name': self.__class__.__name__
        }
