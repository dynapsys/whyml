"""Tests for PASVG core models."""

import pytest
from pathlib import Path
from datetime import datetime

from pasvg.core.models import (
    SourceFile, PASVGMetadata, BuildConfig, ProjectConfig,
    ValidationResult, ExtractionResult, GenerationResult, BuildResult
)


class TestSourceFile:
    """Test SourceFile model."""
    
    def test_source_file_creation(self):
        """Test SourceFile creation."""
        source_file = SourceFile(
            filename="test.py",
            content="print('hello')",
            file_type="python",
            language="python"
        )
        
        assert source_file.filename == "test.py"
        assert source_file.content == "print('hello')"
        assert source_file.file_type == "python"
        assert source_file.language == "python"
    
    def test_source_file_encoding(self):
        """Test SourceFile with binary encoding."""
        source_file = SourceFile(
            filename="image.png",
            content="iVBORw0KGgoAAAANSU",
            file_type="image",
            encoding="base64"
        )
        
        assert source_file.encoding == "base64"
        assert source_file.is_binary == True


class TestPASVGMetadata:
    """Test PASVGMetadata model."""
    
    def test_metadata_creation(self):
        """Test metadata creation."""
        metadata = PASVGMetadata(
            name="Test Project",
            description="A test project",
            version="1.0.0",
            technologies=["python", "javascript"],
            platforms=["web", "desktop"],
            build_targets=["docker", "static"]
        )
        
        assert metadata.name == "Test Project"
        assert metadata.description == "A test project"
        assert metadata.version == "1.0.0"
        assert "python" in metadata.technologies
        assert "web" in metadata.platforms
        assert "docker" in metadata.build_targets
    
    def test_metadata_with_timestamps(self):
        """Test metadata with timestamps."""
        created_at = datetime.now()
        metadata = PASVGMetadata(
            name="Test Project",
            description="A test project",
            created_at=created_at
        )
        
        assert metadata.created_at == created_at


class TestBuildConfig:
    """Test BuildConfig model."""
    
    def test_build_config_creation(self):
        """Test build config creation."""
        config = BuildConfig(
            targets=["docker", "nodejs"],
            environment={"NODE_ENV": "production"},
            dependencies=["package.json", "Dockerfile"]
        )
        
        assert "docker" in config.targets
        assert "nodejs" in config.targets
        assert config.environment["NODE_ENV"] == "production"
        assert "package.json" in config.dependencies


class TestProjectConfig:
    """Test ProjectConfig model."""
    
    def test_project_config_creation(self):
        """Test project config creation."""
        metadata = PASVGMetadata(
            name="Test Project",
            description="A test project"
        )
        
        source_files = [
            SourceFile(filename="main.py", content="print('hello')", file_type="python")
        ]
        
        build_config = BuildConfig(targets=["python"])
        
        project_config = ProjectConfig(
            metadata=metadata,
            source_files=source_files,
            build_config=build_config
        )
        
        assert project_config.metadata.name == "Test Project"
        assert len(project_config.source_files) == 1
        assert project_config.source_files[0].filename == "main.py"
        assert "python" in project_config.build_config.targets


class TestResultModels:
    """Test result models."""
    
    def test_validation_result_success(self):
        """Test successful validation result."""
        result = ValidationResult(
            is_valid=True,
            file_count=5,
            total_size=1024,
            metadata=PASVGMetadata(name="Test", description="Test")
        )
        
        assert result.is_valid == True
        assert result.file_count == 5
        assert result.total_size == 1024
        assert result.errors is None
        assert result.warnings is None
    
    def test_validation_result_failure(self):
        """Test failed validation result."""
        result = ValidationResult(
            is_valid=False,
            file_count=0,
            total_size=0,
            errors=["Invalid XML structure"],
            warnings=["Missing metadata"]
        )
        
        assert result.is_valid == False
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert "Invalid XML structure" in result.errors
    
    def test_extraction_result(self):
        """Test extraction result."""
        result = ExtractionResult(
            success=True,
            project_dir="/path/to/project",
            extracted_files=["main.py", "README.md"],
            build_targets=["python", "static"]
        )
        
        assert result.success == True
        assert result.project_dir == "/path/to/project"
        assert len(result.extracted_files) == 2
        assert "main.py" in result.extracted_files
        assert "python" in result.build_targets
    
    def test_generation_result(self):
        """Test generation result."""
        result = GenerationResult(
            success=True,
            pasvg_file="/path/to/output.pasvg.svg",
            file_count=3,
            total_size=2048
        )
        
        assert result.success == True
        assert result.pasvg_file == "/path/to/output.pasvg.svg"
        assert result.file_count == 3
        assert result.total_size == 2048
    
    def test_build_result(self):
        """Test build result."""
        result = BuildResult(
            success=True,
            built_targets=["docker", "nodejs"],
            errors=None
        )
        
        assert result.success == True
        assert len(result.built_targets) == 2
        assert "docker" in result.built_targets
        assert result.errors is None
