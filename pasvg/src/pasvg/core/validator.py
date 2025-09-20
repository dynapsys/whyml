"""
PASVG Validator - Validates PASVG file structure and content.
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
from xml.sax.saxutils import escape

from pasvg.core.models import ValidationResult, PASVGMetadata


class Validator:
    """Validates PASVG files for structure and content integrity."""
    
    def __init__(self):
        self.namespaces = {
            'pasvg': 'http://whyml.org/pasvg/1.0',
            'svg': 'http://www.w3.org/2000/svg'
        }
        self.required_elements = [
            'metadata', 'foreignObject', 'script'
        ]
        self.allowed_file_types = [
            'manifest', 'source', 'config', 'style', 'template', 
            'docs', 'binary', 'web', 'container', 'build'
        ]
        self.schema_validator = SchemaValidator()
    
    def validate(self, pasvg_file: str) -> ValidationResult:
        """Validate a PASVG file."""
        result = ValidationResult(is_valid=True)
        pasvg_path = Path(pasvg_file)
        
        # Check file existence
        if not pasvg_path.exists():
            result.add_error(f"PASVG file not found: {pasvg_file}")
            return result
        
        # Check file extension
        if not pasvg_path.name.endswith('.pasvg.svg'):
            result.add_warning(
                f"File should have .pasvg.svg extension: {pasvg_path.name}"
            )
        
        try:
            # Read and parse SVG content
            with open(pasvg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # Parse XML tree first to catch XML errors before PASVG validation
            tree = ET.parse(pasvg_path)
            root = tree.getroot()
            
            # Now validate XML structure and PASVG requirements
            self._validate_xml_structure(svg_content, result)
            
            if result.has_errors():
                return result
            
            # Validate SVG root element
            self._validate_svg_root(root, result)
            
            # Validate metadata
            metadata = self._validate_metadata(root, result)
            result.metadata = metadata
            
            # Validate embedded files
            file_count, total_size = self._validate_embedded_files(
                svg_content, result
            )
            result.file_count = file_count
            result.total_size = total_size
            
            # Validate build configuration
            self._validate_build_config(svg_content, result)
            
            # Validate visual layout
            self._validate_visual_layout(root, result)
            
        except ET.ParseError as e:
            result.add_error(f"XML parsing error: {e}")
        except Exception as e:
            result.add_error(f"Validation error: {e}")
        
        return result
    
    def _validate_xml_structure(self, svg_content: str, result: ValidationResult):
        """Validate basic XML structure."""
        # Check for XML declaration
        if not svg_content.strip().startswith('<?xml'):
            result.add_warning("Missing XML declaration")
        
        # Check for PASVG version attribute
        if 'data-pasvg-version=' not in svg_content:
            result.add_error("Missing PASVG version attribute")
        
        # Check for proper CDATA sections
        cdata_pattern = r'<!\[CDATA\[.*?\]\]>'
        cdata_matches = re.findall(cdata_pattern, svg_content, re.DOTALL)
        if not cdata_matches:
            result.add_warning("No CDATA sections found - may not contain embedded files")
    
    def _validate_svg_root(self, root: ET.Element, result: ValidationResult):
        """Validate SVG root element."""
        # Check if root is SVG element
        svg_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
        if svg_tag != 'svg':
            result.add_error(f"Root element must be <svg>, found: {svg_tag}")
        
        # Check required attributes
        if not root.get('data-pasvg-version'):
            result.add_error("Missing data-pasvg-version attribute")
        
        if not root.get('data-project-name'):
            result.add_warning("Missing data-project-name attribute")
        
        # Check SVG dimensions
        width = root.get('width')
        height = root.get('height')
        if not width or not height:
            result.add_warning("SVG dimensions not specified")
    
    def _validate_metadata(self, root: ET.Element, result: ValidationResult) -> Optional[PASVGMetadata]:
        """Validate project metadata."""
        # Try to find metadata element with and without namespaces
        metadata_elem = root.find('.//metadata', self.namespaces)
        if metadata_elem is None:
            # Try with SVG namespace directly
            metadata_elem = root.find('.//{http://www.w3.org/2000/svg}metadata')
        if metadata_elem is None:
            # Try without namespace
            metadata_elem = root.find('.//metadata')
        
        if metadata_elem is None:
            result.add_error("Missing project metadata")
            return None
        
        metadata_dict = {}
        # Helper to process a child element into dict
        def process_child(child):
            tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            # Map project-name to name for compatibility
            if tag_name == 'project-name':
                metadata_dict['name'] = child.text or ''
            else:
                metadata_dict[tag_name.replace('-', '_')] = child.text or ''
        
        for child in metadata_elem:
            tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag_name == 'project':
                # Dive into project element to extract its fields
                for sub in child:
                    process_child(sub)
            else:
                process_child(child)
        
        if not metadata_dict.get('name'):
            result.add_error("Project name is required in metadata")
        
        if not metadata_dict.get('description'):
            result.add_warning("Project description is missing")
        
        return PASVGMetadata.from_dict(metadata_dict)
    
    def _validate_embedded_files(self, svg_content: str, result: ValidationResult) -> tuple[int, int]:
        """Validate embedded source files."""
        # Pattern to match embedded files
        file_pattern = r'<(foreignObject|pre|script)[^>]*data-filename="([^"]+)"[^>]*>.*?<!\[CDATA\[(.*?)\]\]>.*?</\1>'
        
        matches = re.findall(file_pattern, svg_content, re.DOTALL)
        file_count = len(matches)
        total_size = 0
        
        if file_count == 0:
            result.add_warning("No embedded files found")
            return 0, 0
        
        filenames = set()
        for element_type, filename, content in matches:
            # Check for duplicate filenames
            if filename in filenames:
                result.add_error(f"Duplicate filename: {filename}")
            filenames.add(filename)
            
            # Validate filename
            if not filename.strip():
                result.add_error("Empty filename found")
            
            # Check file content
            content = content.strip()
            if not content:
                result.add_warning(f"Empty file content: {filename}")
            else:
                total_size += len(content.encode('utf-8'))
            
            # Validate element type
            if element_type not in ['foreignObject', 'pre', 'script']:
                result.add_error(f"Invalid element type for file: {element_type}")
        
        # Check reasonable file count
        if file_count > 1000:
            result.add_warning(f"Large number of files: {file_count}")
        
        # Check reasonable total size (100MB limit)
        if total_size > 100 * 1024 * 1024:
            result.add_warning(f"Large total size: {total_size / 1024 / 1024:.1f}MB")
        
        return file_count, total_size
    
    def _validate_build_config(self, svg_content: str, result: ValidationResult):
        """Validate build configuration."""
        config_pattern = r'<script[^>]*data-filename="pasvg-build\.json"[^>]*>.*?<!\[CDATA\[(.*?)\]\]>.*?</script>'
        
        match = re.search(config_pattern, svg_content, re.DOTALL)
        if not match:
            result.add_warning("Missing build configuration")
            return
        
        try:
            import json
            config_data = json.loads(match.group(1).strip())
            
            # Validate required fields
            if 'project' not in config_data:
                result.add_warning("Build config missing project name")
            
            if 'targets' not in config_data:
                result.add_warning("Build config missing targets")
            
            if 'files' not in config_data:
                result.add_warning("Build config missing files list")
            
        except json.JSONDecodeError:
            result.add_error("Invalid JSON in build configuration")
    
    def _validate_visual_layout(self, root: ET.Element, result: ValidationResult):
        """Validate visual layout elements."""
        # Check for style definitions
        style_elem = root.find('.//style')
        if style_elem is None:
            result.add_warning("Missing CSS styles for visual layout")
        
        # Check for title element
        title_elems = root.findall('.//text[@class="pasvg-title"]')
        if not title_elems:
            result.add_warning("Missing title text elements")
        
        # Check for visual structure
        visual_elements = [
            'rect', 'text', 'g'  # Basic visual elements
        ]
        
        found_elements = set()
        for elem_type in visual_elements:
            if root.find(f'.//{elem_type}') is not None:
                found_elements.add(elem_type)
        
        if len(found_elements) < 2:
            result.add_warning("Minimal visual layout detected")


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class SchemaValidator:
    """Validates PASVG files against schema requirements."""
    
    def __init__(self):
        self.schema_version = "1.0"
    
    def validate_schema(self, pasvg_file: str) -> ValidationResult:
        """Validate against PASVG schema."""
        # This would implement schema validation if we had an XSD/JSON schema
        # For now, return basic structural validation
        validator = Validator()
        return validator.validate(pasvg_file)
    
    def validate_svg_structure(self, svg_content: str) -> ValidationResult:
        """Validate SVG structure."""
        result = ValidationResult(is_valid=True)
        # Basic SVG structure validation
        if not svg_content.strip().startswith('<?xml'):
            result.add_warning("Missing XML declaration")
        if '<svg' not in svg_content:
            result.add_error("Missing SVG root element")
        return result
    
    def validate_metadata(self, metadata_dict: dict) -> ValidationResult:
        """Validate metadata structure."""
        result = ValidationResult(is_valid=True)
        if not metadata_dict.get('name'):
            result.add_error("Project name is required")
        if not metadata_dict.get('description'):
            result.add_warning("Project description is recommended")
        return result
    
    def validate_embedded_files(self, files: list) -> ValidationResult:
        """Validate embedded files structure."""
        result = ValidationResult(is_valid=True)
        if not files:
            result.add_error("No embedded files found")
        filenames = set()
        for file_info in files:
            filename = file_info.get('filename')
            if filename in filenames:
                result.add_error(f"Duplicate filename: {filename}")
            filenames.add(filename)
        return result
