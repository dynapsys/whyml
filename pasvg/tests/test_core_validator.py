"""Tests for PASVG validator."""

import pytest
import tempfile
from pathlib import Path

from pasvg.core.validator import Validator
from pasvg.core.models import ValidationResult


class TestValidator:
    """Test PASVG validator functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.validator = Validator()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validator_creation(self):
        """Test validator creation."""
        validator = Validator()
        assert validator is not None
    
    def test_validate_invalid_file(self):
        """Test validation of non-existent file."""
        non_existent_file = self.temp_dir / "nonexistent.pasvg.svg"
        
        result = self.validator.validate(str(non_existent_file))
        
        assert isinstance(result, ValidationResult)
        assert not result.is_valid
        assert result.errors is not None
        assert len(result.errors) > 0
    
    def test_validate_invalid_xml(self):
        """Test validation of invalid XML file."""
        invalid_xml_file = self.temp_dir / "invalid.pasvg.svg"
        
        # Create file with invalid XML
        with open(invalid_xml_file, 'w') as f:
            f.write("This is not valid XML <unclosed tag")
        
        result = self.validator.validate(str(invalid_xml_file))
        
        assert not result.is_valid
        assert result.errors is not None
        assert any("XML" in error for error in result.errors)
    
    def test_validate_non_svg_file(self):
        """Test validation of non-SVG file."""
        non_svg_file = self.temp_dir / "test.pasvg.svg"
        
        # Create valid XML but not SVG
        with open(non_svg_file, 'w') as f:
            f.write('<?xml version="1.0"?><root><item>test</item></root>')
        
        result = self.validator.validate(str(non_svg_file))
        
        assert not result.is_valid
        assert result.errors is not None
        assert any("SVG" in error for error in result.errors)
    
    def test_validate_minimal_svg(self):
        """Test validation of minimal valid SVG."""
        minimal_svg_file = self.temp_dir / "minimal.pasvg.svg"
        
        # Create minimal valid SVG
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">
    <rect x="0" y="0" width="800" height="600" fill="white"/>
    <text x="20" y="30" font-size="16">Minimal PASVG</text>
</svg>'''
        
        with open(minimal_svg_file, 'w') as f:
            f.write(svg_content)
        
        result = self.validator.validate(str(minimal_svg_file))
        
        # Should be valid SVG but may have warnings about missing PASVG elements
        assert result.is_valid or result.warnings is not None
    
    def test_validate_pasvg_with_metadata(self):
        """Test validation of PASVG with metadata."""
        pasvg_file = self.temp_dir / "with_metadata.pasvg.svg"
        
        # Create PASVG with metadata
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" data-pasvg-version="1.0" data-project-name="Test Project">
    <!-- PASVG Metadata -->
    <metadata data-pasvg="true">
        <project-name>Test Project</project-name>
        <description>A test PASVG file</description>
        <version>1.0.0</version>
        <technologies>python,javascript</technologies>
        <platforms>web,desktop</platforms>
        <build-targets>static,docker</build-targets>
    </metadata>
    
    <!-- Source Files -->
    <foreignObject data-filename="main.py" data-type="python" data-language="python">
        <![CDATA[print("Hello from PASVG!")]]>
    </foreignObject>
    
    <rect x="0" y="0" width="800" height="600" fill="white"/>
    <text x="20" y="30" font-size="16">Test PASVG Project</text>
</svg>'''
        
        with open(pasvg_file, 'w') as f:
            f.write(svg_content)
        
        result = self.validator.validate(str(pasvg_file))
        
        assert result.is_valid
        assert result.metadata is not None
        assert result.metadata.name == "Test Project"
        assert result.file_count >= 1
        assert result.total_size > 0
    
    def test_validate_pasvg_with_embedded_files(self):
        """Test validation of PASVG with multiple embedded files."""
        pasvg_file = self.temp_dir / "with_files.pasvg.svg"
        
        # Create PASVG with multiple embedded files
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" data-pasvg-version="1.0" data-project-name="Multi-File Project">
    <!-- PASVG Metadata -->
    <metadata data-pasvg="true">
        <project-name>Multi-File Project</project-name>
        <description>Project with multiple files</description>
    </metadata>
    
    <!-- Python File -->
    <foreignObject data-filename="app.py" data-type="python" data-language="python">
        <![CDATA[
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run()
        ]]>
    </foreignObject>
    
    <!-- HTML File -->
    <foreignObject data-filename="index.html" data-type="html" data-language="html">
        <![CDATA[
<!DOCTYPE html>
<html>
<head><title>Test App</title></head>
<body><h1>Hello, World!</h1></body>
</html>
        ]]>
    </foreignObject>
    
    <!-- CSS File -->
    <foreignObject data-filename="style.css" data-type="css" data-language="css">
        <![CDATA[
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}
        ]]>
    </foreignObject>
    
    <rect x="0" y="0" width="800" height="600" fill="white"/>
    <text x="20" y="30" font-size="16">Multi-File PASVG Project</text>
</svg>'''
        
        with open(pasvg_file, 'w') as f:
            f.write(svg_content)
        
        result = self.validator.validate(str(pasvg_file))
        
        assert result.is_valid
        assert result.file_count == 3
        assert result.metadata.name == "Multi-File Project"
    
    def test_schema_validation(self):
        """Test schema validation functionality."""
        # Test that the validator has schema validation capabilities
        schema_validator = self.validator.schema_validator
        assert schema_validator is not None
        
        # Test basic schema validation methods exist
        assert hasattr(schema_validator, 'validate_svg_structure')
        assert hasattr(schema_validator, 'validate_metadata')
        assert hasattr(schema_validator, 'validate_embedded_files')
    
    def test_validation_with_warnings(self):
        """Test validation that produces warnings."""
        pasvg_file = self.temp_dir / "with_warnings.pasvg.svg"
        
        # Create PASVG that might generate warnings
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" data-pasvg-version="1.0" data-project-name="Incomplete Project">
    <!-- Missing some recommended metadata -->
    <metadata data-pasvg="true">
        <project-name>Incomplete Project</project-name>
        <!-- Missing description, version, etc. -->
    </metadata>
    
    <!-- File without proper data attributes -->
    <foreignObject>
        <![CDATA[console.log("Hello");]]>
    </foreignObject>
    
    <rect x="0" y="0" width="800" height="600" fill="white"/>
</svg>'''
        
        with open(pasvg_file, 'w') as f:
            f.write(svg_content)
        
        result = self.validator.validate(str(pasvg_file))
        
        # Should still be valid but have warnings
        assert result.is_valid
        assert result.warnings is not None
        assert len(result.warnings) > 0
