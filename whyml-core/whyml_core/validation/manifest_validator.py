"""
WhyML Core Manifest Validator - Comprehensive manifest validation

Validates manifest structure and content against schema with custom validation rules.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
import yaml
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from jsonschema import validate, ValidationError as JsonSchemaError

from ..exceptions import ValidationError, SchemaError


class ManifestValidator:
    """Validates manifest structure and content against schema."""
    
    def __init__(self, schema_path: Optional[Path] = None, requested_sections: Optional[List[str]] = None):
        """Initialize validator with optional custom schema and requested sections.
        
        Args:
            schema_path: Path to custom validation schema file
            requested_sections: List of sections to validate (enables selective validation)
        """
        self.requested_sections = requested_sections or []
        self.schema = self._load_schema(schema_path)
    
    def _load_schema(self, schema_path: Optional[Path]) -> Dict[str, Any]:
        """Load the manifest validation schema.
        
        Args:
            schema_path: Optional path to custom schema file
            
        Returns:
            Validation schema dictionary
            
        Raises:
            SchemaError: If schema loading fails
        """
        if schema_path and schema_path.exists():
            try:
                with open(schema_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                raise SchemaError(f"Failed to load custom schema: {e}", str(schema_path))
        
        # Default schema with dynamic requirements based on requested sections
        schema = {
            "type": "object",
            "properties": {
                "metadata": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "version": {"type": "string"},
                        "extends": {"type": "string"},
                        "template_type": {"type": "string"},
                        "extracted_at": {"type": "string"}
                    },
                    "required": ["title"]
                },
                "analysis": {
                    "type": "object",
                    "properties": {
                        "page_type": {"type": "string"},
                        "seo_analysis": {"type": "object"},
                        "accessibility_analysis": {"type": "object"},
                        "content_stats": {"type": "object"},
                        "structure_complexity": {"type": "object"}
                    }
                },
                "styles": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z_][a-zA-Z0-9_-]*$": {"type": "string"}
                    }
                },
                "structure": {
                    "type": "object"
                },
                "imports": {
                    "type": "object",
                    "properties": {
                        "manifests": {"type": "array", "items": {"type": "string"}},
                        "modules": {"type": "array", "items": {"type": "string"}},
                        "templates": {"type": "array", "items": {"type": "string"}},
                        "scripts": {"type": "array", "items": {"type": "string"}},
                        "styles": {"type": "array", "items": {"type": "string"}},
                        "fonts": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "interactions": {
                    "type": "object"
                },
                "template_slots": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z_][a-zA-Z0-9_-]*$": {"type": "string"}
                    }
                }
            }
        }
        
        # Dynamic required sections based on what was requested
        if self.requested_sections:
            # If specific sections are requested, only require those sections
            schema["required"] = []
            for section in self.requested_sections:
                if section in schema["properties"]:
                    schema["required"].append(section)
        else:
            # If no specific sections requested, don't require any sections by default
            # This allows for flexible manifests without forcing metadata
            schema["required"] = []
        
        return schema
    
    def validate(self, manifest: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate manifest against schema.
        
        Args:
            manifest: Manifest dictionary to validate
            
        Returns:
            Tuple of (errors, warnings)
            
        Raises:
            ValidationError: If validation fails with critical errors
        """
        errors = []
        warnings = []
        
        # Schema validation
        try:
            validate(instance=manifest, schema=self.schema)
        except JsonSchemaError as e:
            errors.append(f"Schema validation failed: {e.message}")
        
        # Custom validation rules
        self._validate_metadata(manifest, errors, warnings)
        self._validate_styles(manifest, errors, warnings)
        self._validate_structure(manifest, errors, warnings)
        self._validate_template_inheritance(manifest, errors, warnings)
        
        return errors, warnings
    
    def validate_and_raise(self, manifest: Dict[str, Any]) -> None:
        """Validate manifest and raise exception if errors found.
        
        Args:
            manifest: Manifest dictionary to validate
            
        Raises:
            ValidationError: If validation errors are found
        """
        errors, warnings = self.validate(manifest)
        if errors:
            raise ValidationError("Manifest validation failed", errors, warnings)
    
    def _validate_metadata(self, manifest: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate metadata section if present or required.
        
        Args:
            manifest: Manifest dictionary
            errors: List to append validation errors
            warnings: List to append validation warnings
        """
        metadata = manifest.get('metadata', {})
        
        # Only validate metadata if it's present or explicitly requested
        if not metadata and self.requested_sections and 'metadata' not in self.requested_sections:
            return
        
        if metadata and not metadata.get('title'):
            errors.append("Metadata must include a title")
        
        if metadata and not metadata.get('description'):
            warnings.append("Consider adding a description to metadata")
        
        # Validate template inheritance
        if metadata and 'extends' in metadata:
            extends = metadata['extends']
            if not isinstance(extends, str) or not extends.strip():
                errors.append("Template 'extends' must be a non-empty string")
    
    def _validate_styles(self, manifest: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate styles section.
        
        Args:
            manifest: Manifest dictionary
            errors: List to append validation errors
            warnings: List to append validation warnings
        """
        styles = manifest.get('styles', {})
        
        if not isinstance(styles, dict):
            errors.append("Styles must be an object/dictionary")
            return
        
        css_property_pattern = re.compile(r'^[a-zA-Z-]+\s*:\s*.+$')
        css_rule_pattern = re.compile(r'^\s*[a-zA-Z0-9._#\-\s,:\[\]()>+~*@]+\s*\{[^{}]*\}\s*$', re.DOTALL)
        
        for style_name, style_value in styles.items():
            if not isinstance(style_value, str):
                errors.append(f"Style '{style_name}' must be a string")
                continue
            
            # Skip validation for CSS rule blocks (selector { properties })
            if '{' in style_value and '}' in style_value:
                # This is likely a CSS rule block, skip detailed validation for now
                # Only check for severe brace mismatches (allow minor formatting issues)
                open_braces = style_value.count('{')
                close_braces = style_value.count('}')
                if abs(open_braces - close_braces) > 1:  # Allow some tolerance
                    warnings.append(f"Style '{style_name}' may have significantly unmatched braces")
                continue
            
            # Basic CSS validation for properties
            if ';' in style_value:
                # Multiple properties
                properties = style_value.split(';')
                for prop in properties:
                    prop = prop.strip()
                    if prop and not css_property_pattern.match(prop):
                        warnings.append(f"Style '{style_name}' may have invalid CSS property: '{prop}'")
            else:
                # Single property
                if style_value.strip() and not css_property_pattern.match(style_value.strip()):
                    warnings.append(f"Style '{style_name}' may have invalid CSS property: '{style_value}'")
    
    def _validate_structure(self, manifest: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate structure section if present.
        
        Args:
            manifest: Manifest dictionary
            errors: List to append validation errors
            warnings: List to append validation warnings
        """
        structure = manifest.get('structure')
        
        if not structure:
            # Structure is now optional - only validate if present
            return
        
        def validate_element(element, path="structure"):
            if isinstance(element, dict):
                # Check for required HTML element structure
                for key, value in element.items():
                    if key in ['children', 'text', 'style', 'class', 'id']:
                        continue
                    
                    # This should be an HTML element
                    if not re.match(r'^[a-zA-Z][a-zA-Z0-9-]*$', key):
                        warnings.append(f"Unusual element name at {path}.{key}: '{key}'")
                    
                    if isinstance(value, dict):
                        validate_element(value, f"{path}.{key}")
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            validate_element(item, f"{path}.{key}[{i}]")
            
            elif isinstance(element, list):
                for i, item in enumerate(element):
                    validate_element(item, f"{path}[{i}]")
        
        validate_element(structure)
    
    def _validate_template_inheritance(self, manifest: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate template inheritance configuration.
        
        Args:
            manifest: Manifest dictionary
            errors: List to append validation errors
            warnings: List to append validation warnings
        """
        metadata = manifest.get('metadata', {})
        template_slots = manifest.get('template_slots', {})
        
        if 'extends' in metadata and template_slots:
            warnings.append("Template inheritance and template_slots both present - ensure compatibility")
        
        # Validate slot names
        for slot_name in template_slots.keys():
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', slot_name):
                errors.append(f"Invalid template slot name: '{slot_name}'")
