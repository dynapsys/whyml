"""
Test suite for whyml_core.processing module

Tests for:
- ManifestProcessor
- TemplateProcessor
- InheritanceResolver
- VariableSubstitution

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from typing import Dict, Any

from whyml_core.processing.manifest_processor import ManifestProcessor
from whyml_core.processing.template_processor import TemplateProcessor
from whyml_core.processing.inheritance_resolver import InheritanceResolver
from whyml_core.processing.variable_substitution import VariableSubstitution
from whyml_core.exceptions.processing_exceptions import ProcessingError


class TestManifestProcessor:
    """Test cases for ManifestProcessor class."""
    
    @pytest.fixture
    def processor(self):
        return ManifestProcessor()
    
    @pytest.fixture
    def sample_manifest(self):
        return {
            "metadata": {"title": "Test", "version": "1.0.0"},
            "structure": {"html": {"body": {"div": "content"}}}
        }
    
    def test_processor_initialization(self, processor):
        assert processor is not None
        assert hasattr(processor, 'process_manifest')
    
    def test_process_valid_manifest(self, processor, sample_manifest):
        result = processor.process_manifest(sample_manifest)
        assert isinstance(result, dict)
        assert "metadata" in result
    
    def test_process_invalid_manifest(self, processor):
        with pytest.raises(ProcessingError):
            processor.process_manifest(None)
    
    @pytest.mark.asyncio
    async def test_process_manifest_async(self, processor, sample_manifest):
        result = await processor.process_manifest_async(sample_manifest)
        assert isinstance(result, dict)


class TestTemplateProcessor:
    """Test cases for TemplateProcessor class."""
    
    @pytest.fixture
    def template_processor(self):
        return TemplateProcessor()
    
    def test_template_processing(self, template_processor):
        template = {"title": "{{page_title}}", "content": "{{main_content}}"}
        variables = {"page_title": "Test Page", "main_content": "Hello World"}
        
        result = template_processor.process_template(template, variables)
        
        assert result["title"] == "Test Page"
        assert result["content"] == "Hello World"
    
    def test_nested_template_processing(self, template_processor):
        template = {
            "header": {"title": "{{site_name}}"},
            "main": {"sections": [{"title": "{{section_title}}", "body": "{{section_body}}"}]}
        }
        variables = {
            "site_name": "My Site",
            "section_title": "Welcome",
            "section_body": "Welcome content"
        }
        
        result = template_processor.process_template(template, variables)
        
        assert result["header"]["title"] == "My Site"
        assert result["main"]["sections"][0]["title"] == "Welcome"


class TestInheritanceResolver:
    """Test cases for InheritanceResolver class."""
    
    @pytest.fixture
    def inheritance_resolver(self):
        return InheritanceResolver()
    
    def test_simple_inheritance(self, inheritance_resolver):
        base = {"metadata": {"title": "Base"}, "structure": {"html": {"head": {}}}}
        child = {"metadata": {"title": "Child"}, "extends": "base"}
        
        result = inheritance_resolver.resolve_inheritance(child, {"base": base})
        
        assert result["metadata"]["title"] == "Child"
        assert "structure" in result


class TestVariableSubstitution:
    """Test cases for VariableSubstitution class."""
    
    @pytest.fixture
    def variable_substitution(self):
        return VariableSubstitution()
    
    def test_simple_substitution(self, variable_substitution):
        template = "Hello {{name}}"
        variables = {"name": "World"}
        
        result = variable_substitution.substitute(template, variables)
        
        assert result == "Hello World"
    
    def test_multiple_substitutions(self, variable_substitution):
        template = "{{greeting}} {{name}}, welcome to {{site}}"
        variables = {"greeting": "Hello", "name": "John", "site": "WhyML"}
        
        result = variable_substitution.substitute(template, variables)
        
        assert result == "Hello John, welcome to WhyML"


if __name__ == "__main__":
    pytest.main([__file__])
