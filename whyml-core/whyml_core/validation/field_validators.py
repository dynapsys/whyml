"""
WhyML Core Field Validators - Specialized field validation functions

Provides specific validation functions for different types of manifest fields.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
import urllib.parse
from typing import Any, List, Optional, Union
from datetime import datetime


class FieldValidators:
    """Collection of specialized field validation functions."""
    
    @staticmethod
    def validate_css_property(value: str) -> tuple[bool, Optional[str]]:
        """Validate CSS property format.
        
        Args:
            value: CSS property string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, str):
            return False, "CSS property must be a string"
        
        value = value.strip()
        if not value:
            return False, "CSS property cannot be empty"
        
        # Check for basic CSS property format: property: value
        css_property_pattern = re.compile(r'^[a-zA-Z-]+\s*:\s*.+$')
        if css_property_pattern.match(value):
            return True, None
        
        # Check for CSS rule block format: selector { properties }
        css_rule_pattern = re.compile(r'^\s*[a-zA-Z0-9._#\-\s,:\[\]()>+~*@]+\s*\{[^{}]*\}\s*$', re.DOTALL)
        if css_rule_pattern.match(value):
            return True, None
        
        return False, f"Invalid CSS format: '{value}'"
    
    @staticmethod
    def validate_html_element_name(name: str) -> tuple[bool, Optional[str]]:
        """Validate HTML element name.
        
        Args:
            name: HTML element name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(name, str):
            return False, "Element name must be a string"
        
        name = name.strip()
        if not name:
            return False, "Element name cannot be empty"
        
        # HTML element names must start with letter, contain only letters, numbers, hyphens
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9-]*$', name):
            return False, f"Invalid HTML element name: '{name}'"
        
        return True, None
    
    @staticmethod
    def validate_template_slot_name(name: str) -> tuple[bool, Optional[str]]:
        """Validate template slot name.
        
        Args:
            name: Template slot name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(name, str):
            return False, "Template slot name must be a string"
        
        name = name.strip()
        if not name:
            return False, "Template slot name cannot be empty"
        
        # Template slot names: start with letter/underscore, contain alphanumeric/underscore/hyphen
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', name):
            return False, f"Invalid template slot name: '{name}'"
        
        return True, None
    
    @staticmethod
    def validate_url(url: str) -> tuple[bool, Optional[str]]:
        """Validate URL format.
        
        Args:
            url: URL string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(url, str):
            return False, "URL must be a string"
        
        url = url.strip()
        if not url:
            return False, "URL cannot be empty"
        
        try:
            result = urllib.parse.urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False, f"Invalid URL format: '{url}'"
            return True, None
        except Exception as e:
            return False, f"URL validation error: {e}"
    
    @staticmethod
    def validate_version(version: str) -> tuple[bool, Optional[str]]:
        """Validate version string format.
        
        Args:
            version: Version string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(version, str):
            return False, "Version must be a string"
        
        version = version.strip()
        if not version:
            return False, "Version cannot be empty"
        
        # Basic semantic version format: major.minor.patch
        if re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$', version):
            return True, None
        
        # Alternative simple version formats
        if re.match(r'^\d+(\.\d+)*$', version):
            return True, None
        
        return False, f"Invalid version format: '{version}'"
    
    @staticmethod
    def validate_datetime(dt_str: str) -> tuple[bool, Optional[str]]:
        """Validate datetime string format.
        
        Args:
            dt_str: Datetime string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(dt_str, str):
            return False, "Datetime must be a string"
        
        dt_str = dt_str.strip()
        if not dt_str:
            return False, "Datetime cannot be empty"
        
        # Try common datetime formats
        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
        ]
        
        for fmt in formats:
            try:
                datetime.strptime(dt_str, fmt)
                return True, None
            except ValueError:
                continue
        
        return False, f"Invalid datetime format: '{dt_str}'"
    
    @staticmethod
    def validate_page_type(page_type: str) -> tuple[bool, Optional[str]]:
        """Validate page type value.
        
        Args:
            page_type: Page type string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(page_type, str):
            return False, "Page type must be a string"
        
        valid_page_types = {
            'blog', 'e-commerce', 'landing', 'portfolio', 'website', 
            'unknown', 'article', 'product', 'contact', 'about'
        }
        
        if page_type.lower() in valid_page_types:
            return True, None
        
        return False, f"Invalid page type: '{page_type}'"
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> tuple[bool, Optional[str]]:
        """Validate file extension.
        
        Args:
            filename: Filename to validate
            allowed_extensions: List of allowed extensions (with dots, e.g., ['.html', '.css'])
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(filename, str):
            return False, "Filename must be a string"
        
        filename = filename.strip()
        if not filename:
            return False, "Filename cannot be empty"
        
        file_ext = None
        for ext in allowed_extensions:
            if filename.lower().endswith(ext.lower()):
                file_ext = ext
                break
        
        if file_ext is None:
            return False, f"Invalid file extension. Allowed: {', '.join(allowed_extensions)}"
        
        return True, None
    
    @staticmethod
    def validate_color(color: str) -> tuple[bool, Optional[str]]:
        """Validate CSS color value.
        
        Args:
            color: Color string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(color, str):
            return False, "Color must be a string"
        
        color = color.strip()
        if not color:
            return False, "Color cannot be empty"
        
        # Hex colors
        if re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color):
            return True, None
        
        # RGB/RGBA
        if re.match(r'^rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(,\s*[\d.]+\s*)?\)$', color):
            return True, None
        
        # HSL/HSLA
        if re.match(r'^hsla?\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*(,\s*[\d.]+\s*)?\)$', color):
            return True, None
        
        # Named colors (basic set)
        named_colors = {
            'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink',
            'black', 'white', 'gray', 'grey', 'brown', 'cyan', 'magenta',
            'transparent', 'inherit', 'initial', 'unset'
        }
        
        if color.lower() in named_colors:
            return True, None
        
        return False, f"Invalid color format: '{color}'"
    
    @classmethod
    def validate_manifest_field(cls, field_name: str, value: Any) -> tuple[bool, Optional[str]]:
        """Validate a manifest field based on its name and value.
        
        Args:
            field_name: Name of the field to validate
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Map field names to validation functions
        field_validators = {
            'title': lambda v: (isinstance(v, str) and bool(v.strip()), "Title must be a non-empty string"),
            'description': lambda v: (isinstance(v, str), "Description must be a string"),
            'version': cls.validate_version,
            'extends': lambda v: (isinstance(v, str) and bool(v.strip()), "Extends must be a non-empty string"),
            'extracted_at': cls.validate_datetime,
            'page_type': cls.validate_page_type,
        }
        
        if field_name in field_validators:
            validator = field_validators[field_name]
            if callable(validator):
                result = validator(value)
                if isinstance(result, tuple):
                    return result
                else:
                    return result, None
        
        # Default validation - just check if value exists
        return True, None
