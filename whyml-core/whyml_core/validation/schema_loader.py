"""
WhyML Core Schema Loader - Schema loading and management

Handles loading, caching, and management of validation schemas for WhyML manifests.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import yaml
import json
from typing import Any, Dict, Optional
from pathlib import Path
from functools import lru_cache

from ..exceptions import SchemaError


class SchemaLoader:
    """Loads and manages validation schemas for WhyML manifests."""
    
    def __init__(self, default_schema_dir: Optional[Path] = None):
        """Initialize schema loader with optional default schema directory.
        
        Args:
            default_schema_dir: Directory containing default schema files
        """
        self.default_schema_dir = default_schema_dir or Path(__file__).parent / "schemas"
        self._schema_cache = {}
    
    @lru_cache(maxsize=128)
    def load_schema(self, schema_path: Optional[Path] = None, schema_name: Optional[str] = None) -> Dict[str, Any]:
        """Load validation schema from file or return default schema.
        
        Args:
            schema_path: Path to custom schema file
            schema_name: Name of predefined schema (e.g., 'basic', 'full', 'scraping')
            
        Returns:
            Schema dictionary
            
        Raises:
            SchemaError: If schema loading fails
        """
        # Load custom schema from path
        if schema_path:
            return self._load_schema_from_path(schema_path)
        
        # Load predefined schema by name
        if schema_name:
            return self._load_predefined_schema(schema_name)
        
        # Return default schema
        return self._get_default_schema()
    
    def _load_schema_from_path(self, schema_path: Path) -> Dict[str, Any]:
        """Load schema from file path.
        
        Args:
            schema_path: Path to schema file
            
        Returns:
            Schema dictionary
            
        Raises:
            SchemaError: If schema loading fails
        """
        if not schema_path.exists():
            raise SchemaError(f"Schema file not found: {schema_path}", str(schema_path))
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                if schema_path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    return yaml.safe_load(f)
        except Exception as e:
            raise SchemaError(f"Failed to load schema from {schema_path}: {e}", str(schema_path))
    
    def _load_predefined_schema(self, schema_name: str) -> Dict[str, Any]:
        """Load predefined schema by name.
        
        Args:
            schema_name: Name of predefined schema
            
        Returns:
            Schema dictionary
            
        Raises:
            SchemaError: If schema not found
        """
        schema_file = self.default_schema_dir / f"{schema_name}.yaml"
        
        if not schema_file.exists():
            # Try JSON extension
            schema_file = self.default_schema_dir / f"{schema_name}.json"
        
        if not schema_file.exists():
            raise SchemaError(f"Predefined schema '{schema_name}' not found")
        
        return self._load_schema_from_path(schema_file)
    
    def _get_default_schema(self) -> Dict[str, Any]:
        """Get default WhyML manifest validation schema.
        
        Returns:
            Default schema dictionary
        """
        return {
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
            },
            "required": []  # Flexible by default
        }
    
    def get_schema_for_sections(self, requested_sections: list) -> Dict[str, Any]:
        """Get schema customized for specific sections.
        
        Args:
            requested_sections: List of sections to validate
            
        Returns:
            Customized schema dictionary
        """
        base_schema = self._get_default_schema()
        
        if requested_sections:
            # Only require requested sections
            base_schema["required"] = []
            for section in requested_sections:
                if section in base_schema["properties"]:
                    base_schema["required"].append(section)
        
        return base_schema
    
    def validate_schema(self, schema: Dict[str, Any]) -> bool:
        """Validate that a schema is properly formatted.
        
        Args:
            schema: Schema to validate
            
        Returns:
            True if schema is valid
            
        Raises:
            SchemaError: If schema is invalid
        """
        required_keys = ["type", "properties"]
        
        for key in required_keys:
            if key not in schema:
                raise SchemaError(f"Schema missing required key: {key}")
        
        if not isinstance(schema["properties"], dict):
            raise SchemaError("Schema 'properties' must be a dictionary")
        
        return True
    
    def clear_cache(self):
        """Clear the schema cache."""
        self.load_schema.cache_clear()
        self._schema_cache.clear()
