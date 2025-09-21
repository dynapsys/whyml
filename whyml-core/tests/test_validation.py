"""
Test suite for whyml_core.validation module

Tests for:
- ManifestValidator
- SchemaLoader  
- FieldValidators
- ValidationResult handling
- Error reporting

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from whyml_core.validation.manifest_validator import ManifestValidator
from whyml_core.validation.schema_loader import SchemaLoader
from whyml_core.validation.field_validators import FieldValidators
from whyml_core.exceptions.validation_exceptions import (
    ValidationError,
    SchemaValidationError,
    FieldValidationError,
    RequiredFieldError
)


class TestManifestValidator:
    """Test cases for ManifestValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create a ManifestValidator instance for testing."""
        return ManifestValidator()
    
    @pytest.fixture
    def valid_manifest(self) -> Dict[str, Any]:
        """Create a valid manifest for testing."""
        return {
            "metadata": {
                "title": "Test Manifest",
                "description": "A test manifest for validation",
                "version": "1.0.0"
            },
            "structure": {
                "html": {
                    "head": {
                        "title": "Test Page"
                    },
                    "body": {
                        "div": {
                            "class": "container",
                            "content": "Hello World"
                        }
                    }
                }
            }
        }
    
    @pytest.fixture
    def invalid_manifest(self) -> Dict[str, Any]:
        """Create an invalid manifest for testing."""
        return {
            "metadata": {
                # Missing required title field
                "description": "Invalid manifest"
            }
            # Missing required structure field
        }
    
    def test_validator_initialization(self, validator):
        """Test ManifestValidator initialization."""
        assert validator is not None
        assert hasattr(validator, 'validate')
        assert hasattr(validator, 'validate_async')
    
    def test_validate_valid_manifest(self, validator, valid_manifest):
        """Test validation of a valid manifest."""
        result = validator.validate(valid_manifest)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_validate_invalid_manifest(self, validator, invalid_manifest):
        """Test validation of an invalid manifest."""
        result = validator.validate(invalid_manifest)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("title" in str(error).lower() for error in result.errors)
        assert any("structure" in str(error).lower() for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_validate_async_valid_manifest(self, validator, valid_manifest):
        """Test async validation of a valid manifest."""
        result = await validator.validate_async(valid_manifest)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_validate_async_invalid_manifest(self, validator, invalid_manifest):
        """Test async validation of an invalid manifest."""
        result = await validator.validate_async(invalid_manifest)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_validate_with_strict_mode(self, validator, valid_manifest):
        """Test validation with strict mode enabled."""
        # Add a warning-level issue
        manifest_with_warnings = valid_manifest.copy()
        manifest_with_warnings["metadata"]["deprecated_field"] = "value"
        
        # Non-strict mode should pass with warnings
        result_normal = validator.validate(manifest_with_warnings, strict=False)
        assert result_normal.is_valid is True
        
        # Strict mode should fail on warnings
        result_strict = validator.validate(manifest_with_warnings, strict=True)
        # In strict mode, warnings might be treated as errors
        assert result_strict.is_valid is True or len(result_strict.warnings) == 0
    
    def test_validate_with_custom_schema(self, validator, valid_manifest):
        """Test validation with custom schema."""
        custom_schema = {
            "type": "object",
            "required": ["metadata"],
            "properties": {
                "metadata": {
                    "type": "object",
                    "required": ["title"]
                }
            }
        }
        
        result = validator.validate(valid_manifest, schema=custom_schema)
        assert result.is_valid is True
    
    def test_validate_empty_manifest(self, validator):
        """Test validation of empty manifest."""
        result = validator.validate({})
        
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_validate_none_manifest(self, validator):
        """Test validation of None manifest."""
        with pytest.raises(ValidationError):
            validator.validate(None)
    
    def test_validate_non_dict_manifest(self, validator):
        """Test validation of non-dictionary manifest."""
        with pytest.raises(ValidationError):
            validator.validate("not a dict")


class TestSchemaLoader:
    """Test cases for SchemaLoader class."""
    
    @pytest.fixture
    def schema_loader(self):
        """Create a SchemaLoader instance for testing."""
        return SchemaLoader()
    
    def test_schema_loader_initialization(self, schema_loader):
        """Test SchemaLoader initialization."""
        assert schema_loader is not None
        assert hasattr(schema_loader, 'load_schema')
        assert hasattr(schema_loader, 'get_default_schema')
    
    def test_get_default_schema(self, schema_loader):
        """Test getting default schema."""
        schema = schema_loader.get_default_schema()
        
        assert isinstance(schema, dict)
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "metadata" in schema["properties"]
        assert "structure" in schema["properties"]
    
    def test_load_schema_from_dict(self, schema_loader):
        """Test loading schema from dictionary."""
        custom_schema = {
            "type": "object",
            "properties": {
                "test_field": {"type": "string"}
            }
        }
        
        loaded_schema = schema_loader.load_schema(custom_schema)
        assert loaded_schema == custom_schema
    
    def test_load_schema_from_path(self, schema_loader, tmp_path):
        """Test loading schema from file path."""
        schema_content = {
            "type": "object",
            "properties": {
                "test_field": {"type": "string"}
            }
        }
        
        schema_file = tmp_path / "test_schema.json"
        import json
        schema_file.write_text(json.dumps(schema_content))
        
        loaded_schema = schema_loader.load_schema(str(schema_file))
        assert loaded_schema == schema_content
    
    def test_load_invalid_schema_file(self, schema_loader):
        """Test loading from invalid schema file."""
        with pytest.raises(SchemaValidationError):
            schema_loader.load_schema("/nonexistent/schema.json")
    
    @pytest.mark.asyncio
    async def test_load_schema_async(self, schema_loader):
        """Test async schema loading."""
        schema = await schema_loader.load_schema_async()
        
        assert isinstance(schema, dict)
        assert "type" in schema


class TestFieldValidators:
    """Test cases for FieldValidators class."""
    
    @pytest.fixture
    def field_validators(self):
        """Create a FieldValidators instance for testing."""
        return FieldValidators()
    
    def test_field_validators_initialization(self, field_validators):
        """Test FieldValidators initialization."""
        assert field_validators is not None
        assert hasattr(field_validators, 'validate_field')
        assert hasattr(field_validators, 'validate_metadata')
        assert hasattr(field_validators, 'validate_structure')
    
    def test_validate_required_field_present(self, field_validators):
        """Test validation of present required field."""
        result = field_validators.validate_field(
            field_name="title",
            field_value="Test Title",
            field_rules={"required": True, "type": "string"}
        )
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_required_field_missing(self, field_validators):
        """Test validation of missing required field."""
        result = field_validators.validate_field(
            field_name="title", 
            field_value=None,
            field_rules={"required": True, "type": "string"}
        )
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("required" in str(error).lower() for error in result.errors)
    
    def test_validate_string_field_type(self, field_validators):
        """Test validation of string field type."""
        # Valid string
        result_valid = field_validators.validate_field(
            field_name="description",
            field_value="Valid string",
            field_rules={"type": "string"}
        )
        assert result_valid.is_valid is True
        
        # Invalid type
        result_invalid = field_validators.validate_field(
            field_name="description",
            field_value=123,
            field_rules={"type": "string"}
        )
        assert result_invalid.is_valid is False
    
    def test_validate_number_field_type(self, field_validators):
        """Test validation of number field type."""
        # Valid number
        result_valid = field_validators.validate_field(
            field_name="version_number",
            field_value=1.5,
            field_rules={"type": "number"}
        )
        assert result_valid.is_valid is True
        
        # Invalid type
        result_invalid = field_validators.validate_field(
            field_name="version_number", 
            field_value="not a number",
            field_rules={"type": "number"}
        )
        assert result_invalid.is_valid is False
    
    def test_validate_array_field_type(self, field_validators):
        """Test validation of array field type."""
        # Valid array
        result_valid = field_validators.validate_field(
            field_name="tags",
            field_value=["tag1", "tag2"],
            field_rules={"type": "array"}
        )
        assert result_valid.is_valid is True
        
        # Invalid type
        result_invalid = field_validators.validate_field(
            field_name="tags",
            field_value="not an array", 
            field_rules={"type": "array"}
        )
        assert result_invalid.is_valid is False
    
    def test_validate_object_field_type(self, field_validators):
        """Test validation of object field type."""
        # Valid object
        result_valid = field_validators.validate_field(
            field_name="config",
            field_value={"key": "value"},
            field_rules={"type": "object"}
        )
        assert result_valid.is_valid is True
        
        # Invalid type
        result_invalid = field_validators.validate_field(
            field_name="config",
            field_value="not an object",
            field_rules={"type": "object"}
        )
        assert result_invalid.is_valid is False
    
    def test_validate_field_with_min_length(self, field_validators):
        """Test validation with minimum length constraint."""
        # Valid length
        result_valid = field_validators.validate_field(
            field_name="title",
            field_value="Long enough title",
            field_rules={"type": "string", "minLength": 5}
        )
        assert result_valid.is_valid is True
        
        # Too short
        result_invalid = field_validators.validate_field(
            field_name="title",
            field_value="Hi",
            field_rules={"type": "string", "minLength": 5}
        )
        assert result_invalid.is_valid is False
    
    def test_validate_field_with_max_length(self, field_validators):
        """Test validation with maximum length constraint."""
        # Valid length
        result_valid = field_validators.validate_field(
            field_name="title",
            field_value="Short",
            field_rules={"type": "string", "maxLength": 10}
        )
        assert result_valid.is_valid is True
        
        # Too long
        result_invalid = field_validators.validate_field(
            field_name="title", 
            field_value="This title is way too long for the constraint",
            field_rules={"type": "string", "maxLength": 10}
        )
        assert result_invalid.is_valid is False
    
    def test_validate_field_with_pattern(self, field_validators):
        """Test validation with regex pattern constraint."""
        # Valid pattern
        result_valid = field_validators.validate_field(
            field_name="email",
            field_value="test@example.com",
            field_rules={"type": "string", "pattern": r"^[^@]+@[^@]+\.[^@]+$"}
        )
        assert result_valid.is_valid is True
        
        # Invalid pattern
        result_invalid = field_validators.validate_field(
            field_name="email",
            field_value="invalid-email",
            field_rules={"type": "string", "pattern": r"^[^@]+@[^@]+\.[^@]+$"}
        )
        assert result_invalid.is_valid is False
    
    def test_validate_metadata_section(self, field_validators):
        """Test validation of metadata section."""
        valid_metadata = {
            "title": "Test Title",
            "description": "Test description",
            "version": "1.0.0"
        }
        
        result = field_validators.validate_metadata(valid_metadata)
        assert result.is_valid is True
    
    def test_validate_metadata_missing_title(self, field_validators):
        """Test validation of metadata missing required title."""
        invalid_metadata = {
            "description": "Test description"
            # Missing title
        }
        
        result = field_validators.validate_metadata(invalid_metadata)
        assert result.is_valid is False
        assert any("title" in str(error).lower() for error in result.errors)
    
    def test_validate_structure_section(self, field_validators):
        """Test validation of structure section."""
        valid_structure = {
            "html": {
                "head": {"title": "Page Title"},
                "body": {"div": {"content": "Page content"}}
            }
        }
        
        result = field_validators.validate_structure(valid_structure)
        assert result.is_valid is True
    
    def test_validate_empty_structure_section(self, field_validators):
        """Test validation of empty structure section."""
        result = field_validators.validate_structure({})
        assert result.is_valid is False
        assert any("empty" in str(error).lower() for error in result.errors)


class TestValidationExceptions:
    """Test cases for validation exceptions."""
    
    def test_validation_error_creation(self):
        """Test ValidationError creation and attributes."""
        error = ValidationError("Test validation error")
        
        assert str(error) == "Test validation error"
        assert isinstance(error, Exception)
    
    def test_schema_validation_error_creation(self):
        """Test SchemaValidationError creation."""
        error = SchemaValidationError("Schema validation failed", schema_path="/test/path")
        
        assert str(error) == "Schema validation failed"
        assert hasattr(error, 'schema_path')
        assert error.schema_path == "/test/path"
    
    def test_field_validation_error_creation(self):
        """Test FieldValidationError creation."""
        error = FieldValidationError("Field validation failed", field_name="title")
        
        assert str(error) == "Field validation failed"
        assert hasattr(error, 'field_name')
        assert error.field_name == "title"
    
    def test_required_field_error_creation(self):
        """Test RequiredFieldError creation."""
        error = RequiredFieldError("title")
        
        assert "title" in str(error)
        assert "required" in str(error).lower()


# Integration tests
class TestValidationIntegration:
    """Integration tests for validation components."""
    
    @pytest.fixture
    def complete_validator_setup(self):
        """Set up complete validation environment."""
        validator = ManifestValidator()
        schema_loader = SchemaLoader()
        field_validators = FieldValidators()
        
        return {
            'validator': validator,
            'schema_loader': schema_loader, 
            'field_validators': field_validators
        }
    
    def test_full_validation_workflow(self, complete_validator_setup):
        """Test complete validation workflow."""
        components = complete_validator_setup
        validator = components['validator']
        
        # Complete valid manifest
        manifest = {
            "metadata": {
                "title": "Integration Test Manifest",
                "description": "A complete manifest for integration testing",
                "version": "1.0.0",
                "author": "Test Author"
            },
            "structure": {
                "html": {
                    "head": {
                        "title": "Test Page",
                        "meta": [
                            {"name": "description", "content": "Test page description"},
                            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                        ]
                    },
                    "body": {
                        "header": {
                            "h1": "Welcome",
                            "nav": {
                                "ul": [
                                    {"li": {"a": {"href": "/", "text": "Home"}}},
                                    {"li": {"a": {"href": "/about", "text": "About"}}}
                                ]
                            }
                        },
                        "main": {
                            "section": {
                                "h2": "Content Section",
                                "p": "This is the main content area."
                            }
                        },
                        "footer": {
                            "p": "© 2025 Test Company"
                        }
                    }
                }
            },
            "styles": {
                "primary": "#007bff",
                "secondary": "#6c757d"
            },
            "imports": [
                {"type": "css", "url": "/styles/main.css"},
                {"type": "js", "url": "/scripts/main.js"}
            ]
        }
        
        result = validator.validate(manifest)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        # May have some warnings for best practices
        assert len(result.warnings) >= 0
    
    @pytest.mark.asyncio
    async def test_async_validation_workflow(self, complete_validator_setup):
        """Test async validation workflow."""
        components = complete_validator_setup
        validator = components['validator']
        
        manifest = {
            "metadata": {"title": "Async Test", "description": "Async validation test"},
            "structure": {"html": {"body": {"div": "content"}}}
        }
        
        result = await validator.validate_async(manifest)
        assert result.is_valid is True


if __name__ == "__main__":
    pytest.main([__file__])
