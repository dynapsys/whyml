"""
WhyML Core YAML Utilities - Advanced YAML processing and manipulation

Provides comprehensive YAML loading, dumping, validation, and manipulation 
utilities with support for custom tags, safe loading, and structured output.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import yaml
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, IO, Callable
from io import StringIO
from ..exceptions import ValidationError, ProcessingError


class YAMLUtils:
    """Utility functions for YAML operations."""
    
    @staticmethod
    def safe_load(content: Union[str, IO]) -> Any:
        """Safely load YAML content.
        
        Args:
            content: YAML string or file-like object
            
        Returns:
            Parsed YAML data
            
        Raises:
            ValidationError: If YAML is invalid
        """
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValidationError(
                message=f"Invalid YAML content: {str(e)}",
                details={'yaml_error': str(e)}
            )
    
    @staticmethod
    def safe_dump(data: Any, 
                  stream: Optional[IO] = None,
                  indent: int = 2,
                  default_flow_style: bool = False,
                  sort_keys: bool = False,
                  width: int = 120) -> Optional[str]:
        """Safely dump data to YAML format.
        
        Args:
            data: Data to dump
            stream: Optional stream to write to
            indent: Number of spaces for indentation
            default_flow_style: Whether to use flow style
            sort_keys: Whether to sort keys
            width: Maximum line width
            
        Returns:
            YAML string if no stream provided, None otherwise
        """
        try:
            return yaml.safe_dump(
                data,
                stream=stream,
                indent=indent,
                default_flow_style=default_flow_style,
                sort_keys=sort_keys,
                width=width,
                allow_unicode=True
            )
        except yaml.YAMLError as e:
            raise ProcessingError(
                message=f"Failed to dump YAML: {str(e)}",
                details={'yaml_error': str(e)}
            )
    
    @staticmethod
    def load_file(file_path: Union[str, Path]) -> Any:
        """Load YAML from file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Parsed YAML data
            
        Raises:
            ValidationError: If file doesn't exist or YAML is invalid
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ValidationError(
                message=f"YAML file not found: {file_path}",
                details={'file_path': str(file_path)}
            )
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return YAMLUtils.safe_load(f)
        except Exception as e:
            raise ValidationError(
                message=f"Failed to load YAML file: {str(e)}",
                details={'file_path': str(file_path), 'error': str(e)}
            )
    
    @staticmethod
    def save_file(data: Any, file_path: Union[str, Path], **kwargs) -> None:
        """Save data to YAML file.
        
        Args:
            data: Data to save
            file_path: Path to save file
            **kwargs: Additional arguments for yaml.safe_dump
        """
        path = Path(file_path)
        
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                YAMLUtils.safe_dump(data, stream=f, **kwargs)
        except Exception as e:
            raise ProcessingError(
                message=f"Failed to save YAML file: {str(e)}",
                details={'file_path': str(file_path), 'error': str(e)}
            )
    
    @staticmethod
    def validate_yaml_string(content: str) -> bool:
        """Validate if string is valid YAML.
        
        Args:
            content: YAML string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            yaml.safe_load(content)
            return True
        except yaml.YAMLError:
            return False
    
    @staticmethod
    def merge_yaml_dicts(base: Dict[str, Any], 
                        overlay: Dict[str, Any], 
                        deep_merge: bool = True) -> Dict[str, Any]:
        """Merge two YAML dictionaries.
        
        Args:
            base: Base dictionary
            overlay: Dictionary to overlay on base
            deep_merge: Whether to perform deep merge
            
        Returns:
            Merged dictionary
        """
        if not deep_merge:
            result = base.copy()
            result.update(overlay)
            return result
        
        result = base.copy()
        
        for key, value in overlay.items():
            if (key in result and 
                isinstance(result[key], dict) and 
                isinstance(value, dict)):
                result[key] = YAMLUtils.merge_yaml_dicts(result[key], value, deep_merge=True)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def extract_front_matter(content: str) -> tuple[Optional[Dict[str, Any]], str]:
        """Extract YAML front matter from content.
        
        Args:
            content: Content with potential front matter
            
        Returns:
            Tuple of (front_matter_dict, remaining_content)
        """
        # Match YAML front matter pattern
        pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)
        
        if not match:
            return None, content
        
        yaml_content = match.group(1)
        remaining_content = match.group(2)
        
        try:
            front_matter = YAMLUtils.safe_load(yaml_content)
            return front_matter, remaining_content
        except ValidationError:
            return None, content


class YAMLProcessor:
    """Advanced YAML processing with custom operations."""
    
    def __init__(self):
        """Initialize YAML processor."""
        self.custom_constructors: Dict[str, Callable] = {}
        self.custom_representers: Dict[type, Callable] = {}
    
    def add_constructor(self, tag: str, constructor: Callable) -> None:
        """Add custom YAML constructor.
        
        Args:
            tag: YAML tag to handle
            constructor: Constructor function
        """
        self.custom_constructors[tag] = constructor
    
    def add_representer(self, data_type: type, representer: Callable) -> None:
        """Add custom YAML representer.
        
        Args:
            data_type: Python type to represent
            representer: Representer function
        """
        self.custom_representers[data_type] = representer
    
    def create_custom_loader(self) -> type:
        """Create custom YAML loader with registered constructors.
        
        Returns:
            Custom loader class
        """
        class CustomLoader(yaml.SafeLoader):
            pass
        
        # Add custom constructors
        for tag, constructor in self.custom_constructors.items():
            CustomLoader.add_constructor(tag, constructor)
        
        return CustomLoader
    
    def create_custom_dumper(self) -> type:
        """Create custom YAML dumper with registered representers.
        
        Returns:
            Custom dumper class
        """
        class CustomDumper(yaml.SafeDumper):
            pass
        
        # Add custom representers
        for data_type, representer in self.custom_representers.items():
            CustomDumper.add_representer(data_type, representer)
        
        return CustomDumper
    
    def load_with_custom(self, content: Union[str, IO]) -> Any:
        """Load YAML with custom constructors.
        
        Args:
            content: YAML content
            
        Returns:
            Parsed data with custom types
        """
        loader_class = self.create_custom_loader()
        try:
            return yaml.load(content, Loader=loader_class)
        except yaml.YAMLError as e:
            raise ValidationError(
                message=f"Failed to load YAML with custom constructors: {str(e)}",
                details={'yaml_error': str(e)}
            )
    
    def dump_with_custom(self, data: Any, **kwargs) -> str:
        """Dump data to YAML with custom representers.
        
        Args:
            data: Data to dump
            **kwargs: Additional dump options
            
        Returns:
            YAML string
        """
        dumper_class = self.create_custom_dumper()
        try:
            return yaml.dump(data, Dumper=dumper_class, **kwargs)
        except yaml.YAMLError as e:
            raise ProcessingError(
                message=f"Failed to dump YAML with custom representers: {str(e)}",
                details={'yaml_error': str(e)}
            )
    
    def normalize_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize manifest structure for consistent processing.
        
        Args:
            manifest: Manifest to normalize
            
        Returns:
            Normalized manifest
        """
        normalized = manifest.copy()
        
        # Ensure required sections exist
        required_sections = ['metadata', 'structure', 'styles']
        for section in required_sections:
            if section not in normalized:
                normalized[section] = {}
        
        # Normalize metadata
        metadata = normalized.get('metadata', {})
        if isinstance(metadata.get('keywords'), str):
            # Convert comma-separated keywords to list
            keywords = [kw.strip() for kw in metadata['keywords'].split(',')]
            normalized['metadata']['keywords'] = keywords
        
        # Normalize styles
        styles = normalized.get('styles', {})
        if isinstance(styles, list):
            # Convert list of styles to dict
            styles_dict = {}
            for i, style in enumerate(styles):
                if isinstance(style, dict) and len(style) == 1:
                    styles_dict.update(style)
                else:
                    styles_dict[f'style_{i}'] = style
            normalized['styles'] = styles_dict
        
        return normalized
    
    def extract_sections(self, manifest: Dict[str, Any], 
                        sections: List[str]) -> Dict[str, Any]:
        """Extract specific sections from manifest.
        
        Args:
            manifest: Source manifest
            sections: List of section names to extract
            
        Returns:
            Manifest with only requested sections
        """
        result = {}
        
        for section in sections:
            if section in manifest:
                result[section] = manifest[section]
        
        return result
    
    def validate_structure(self, manifest: Dict[str, Any]) -> List[str]:
        """Validate manifest structure and return warnings.
        
        Args:
            manifest: Manifest to validate
            
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Check for common issues
        if 'metadata' in manifest:
            metadata = manifest['metadata']
            if not metadata.get('title'):
                warnings.append("Missing title in metadata")
            if not metadata.get('description'):
                warnings.append("Missing description in metadata")
        
        if 'structure' in manifest:
            structure = manifest['structure']
            if not isinstance(structure, dict):
                warnings.append("Structure should be a dictionary")
            elif not structure:
                warnings.append("Empty structure section")
        
        if 'styles' in manifest:
            styles = manifest['styles']
            if not isinstance(styles, dict):
                warnings.append("Styles should be a dictionary")
        
        return warnings
    
    def pretty_print(self, data: Any, indent: int = 2) -> str:
        """Pretty print YAML with consistent formatting.
        
        Args:
            data: Data to print
            indent: Indentation level
            
        Returns:
            Formatted YAML string
        """
        return YAMLUtils.safe_dump(
            data,
            indent=indent,
            default_flow_style=False,
            sort_keys=False,
            width=120
        )
    
    def minify(self, yaml_content: str) -> str:
        """Minify YAML by removing unnecessary whitespace.
        
        Args:
            yaml_content: YAML content to minify
            
        Returns:
            Minified YAML string
        """
        # Parse and re-dump with minimal formatting
        data = YAMLUtils.safe_load(yaml_content)
        return YAMLUtils.safe_dump(
            data,
            indent=1,
            default_flow_style=True,
            sort_keys=True,
            width=float('inf')
        )
    
    def convert_to_json_compatible(self, data: Any) -> Any:
        """Convert YAML data to JSON-compatible format.
        
        Args:
            data: YAML data to convert
            
        Returns:
            JSON-compatible data
        """
        if isinstance(data, dict):
            return {key: self.convert_to_json_compatible(value) 
                   for key, value in data.items()}
        elif isinstance(data, list):
            return [self.convert_to_json_compatible(item) for item in data]
        elif isinstance(data, (tuple, set)):
            return [self.convert_to_json_compatible(item) for item in data]
        elif hasattr(data, '__dict__'):
            return self.convert_to_json_compatible(data.__dict__)
        else:
            # Primitive types (str, int, float, bool, None)
            return data
