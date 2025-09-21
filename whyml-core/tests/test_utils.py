"""
Test suite for whyml_core.utils module

Tests for:
- YAMLUtils
- AsyncUtils
- PathUtils
- StringUtils

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import asyncio
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from whyml_core.utils.yaml_utils import YAMLUtils
from whyml_core.utils.async_utils import AsyncUtils
from whyml_core.utils.path_utils import PathUtils
from whyml_core.utils.string_utils import StringUtils


class TestYAMLUtils:
    """Test cases for YAMLUtils class."""
    
    @pytest.fixture
    def yaml_utils(self):
        return YAMLUtils()
    
    def test_load_yaml_from_string(self, yaml_utils):
        yaml_content = "title: Test\ndescription: A test manifest"
        result = yaml_utils.load_from_string(yaml_content)
        
        assert result["title"] == "Test"
        assert result["description"] == "A test manifest"
    
    def test_dump_to_yaml_string(self, yaml_utils):
        data = {"title": "Test", "description": "A test manifest"}
        result = yaml_utils.dump_to_string(data)
        
        assert "title: Test" in result
        assert "description: A test manifest" in result


class TestAsyncUtils:
    """Test cases for AsyncUtils class."""
    
    @pytest.fixture
    def async_utils(self):
        return AsyncUtils()
    
    @pytest.mark.asyncio
    async def test_run_in_executor(self, async_utils):
        def sync_function(x, y):
            return x + y
        
        result = await async_utils.run_in_executor(sync_function, 2, 3)
        assert result == 5


class TestPathUtils:
    """Test cases for PathUtils class."""
    
    @pytest.fixture
    def path_utils(self):
        return PathUtils()
    
    def test_resolve_path(self, path_utils):
        result = path_utils.resolve_path("./test.yaml")
        assert isinstance(result, Path)
    
    def test_is_url(self, path_utils):
        assert path_utils.is_url("https://example.com/test.yaml") is True
        assert path_utils.is_url("./local/file.yaml") is False


class TestStringUtils:
    """Test cases for StringUtils class."""
    
    @pytest.fixture
    def string_utils(self):
        return StringUtils()
    
    def test_slugify(self, string_utils):
        result = string_utils.slugify("Test Title With Spaces")
        assert result == "test-title-with-spaces"
    
    def test_camel_to_snake(self, string_utils):
        result = string_utils.camel_to_snake("testCamelCase")
        assert result == "test_camel_case"


if __name__ == "__main__":
    pytest.main([__file__])
