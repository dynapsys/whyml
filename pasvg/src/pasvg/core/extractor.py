"""
PASVG Extractor - Extracts projects from PASVG files.
"""

import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional

from pasvg.core.models import (
    PASVGMetadata, SourceFile, ExtractionResult, FileType
)
from pasvg.utils.file_utils import FileOperations, FileScanner, FileValidator
from pasvg.generators.build_script_generator import BuildScriptGenerator


class Extractor:
    """Extracts projects from PASVG files with proper CDATA handling."""
    
    def __init__(self):
        self.namespaces = {
            'pasvg': 'http://whyml.org/pasvg/1.0'
        }
        self.file_ops = FileOperations()
        self.file_scanner = FileScanner()
        self.file_validator = FileValidator()
        self.build_generator = BuildScriptGenerator()
    
    def extract(self, pasvg_file: str, output_dir: str) -> ExtractionResult:
        """Extract project from PASVG file."""
        pasvg_path = Path(pasvg_file)
        output_path = Path(output_dir)
        
        result = ExtractionResult(
            success=True,
            project_dir=output_path / "extracted-project"
        )
        
        if not pasvg_path.exists():
            result.add_error(f"PASVG file not found: {pasvg_file}")
            return result
        
        try:
            # Read raw SVG content for CDATA extraction
            with open(pasvg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # Parse SVG for metadata
            tree = ET.parse(pasvg_path)
            root = tree.getroot()
            
            # Extract project metadata
            metadata = self._extract_metadata(root)
            result.metadata = metadata
            
            if metadata and metadata.name:
                project_name = self._create_safe_dirname(metadata.name)
                result.project_dir = output_path / project_name
            
            print(f"📋 Extracting project: {metadata.name if metadata else 'Unknown'}")
            
            # Create project directory
            result.project_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract source files using raw content parsing
            extracted_files = self._extract_files_from_raw_content(
                svg_content, result.project_dir
            )
            result.extracted_files = extracted_files
            
            # Extract build configuration
            build_targets = self._extract_build_targets(svg_content)
            result.build_targets = build_targets
            
            # Generate build script
            self.build_generator.generate_build_script(
                result.project_dir, metadata, extracted_files, build_targets
            )
            
            # Generate README
            self._generate_readme(result.project_dir, metadata, extracted_files)
            
            print(f"✅ Project extracted to: {result.project_dir}")
            print(f"   📁 {len(extracted_files)} files extracted")
            print(f"   🏗️  Build targets: {', '.join(build_targets) if build_targets else 'None detected'}")
            
        except Exception as e:
            result.add_error(f"Extraction failed: {e}")
        
        return result
    
    def _extract_metadata(self, root: ET.Element) -> Optional[PASVGMetadata]:
        """Extract project metadata from SVG."""
        metadata_dict = {}
        
        # Look for metadata element
        metadata_elem = root.find('.//metadata/project', self.namespaces)
        if metadata_elem is not None:
            for child in metadata_elem:
                tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                metadata_dict[tag_name.replace('-', '_')] = child.text or ''
        
        if metadata_dict:
            return PASVGMetadata.from_dict(metadata_dict)
        
        return PASVGMetadata(name="extracted-project")
    
    def _extract_files_from_raw_content(self, svg_content: str, project_dir: Path) -> List[str]:
        """Extract embedded files using raw SVG content parsing."""
        extracted_files = []
        
        # Pattern to match CDATA sections within elements with data-filename attribute
        pattern = r'<(foreignObject|pre|script)[^>]*data-filename="([^"]+)"[^>]*>.*?<!\[CDATA\[(.*?)\]\]>.*?</\1>'
        
        matches = re.findall(pattern, svg_content, re.DOTALL)
        
        for element_type, filename, content in matches:
            # Skip build config file (handled separately)
            if filename == 'pasvg-build.json':
                continue
            
            # Clean and process the content
            cleaned_content = content.strip()
            if cleaned_content:
                self.file_utils.write_file_content(project_dir / filename, cleaned_content)
                extracted_files.append(filename)
        
        return extracted_files
    
    def _extract_build_targets(self, svg_content: str) -> List[str]:
        """Extract build targets from build configuration."""
        # Look for build configuration JSON
        config_pattern = r'<script[^>]*data-filename="pasvg-build\.json"[^>]*>.*?<!\[CDATA\[(.*?)\]\]>.*?</script>'
        
        match = re.search(config_pattern, svg_content, re.DOTALL)
        if match:
            try:
                config_data = json.loads(match.group(1).strip())
                return config_data.get('targets', [])
            except json.JSONDecodeError:
                pass
        
        return []
    
    def _create_safe_dirname(self, project_name: str) -> str:
        """Create a safe directory name from project name."""
        # Clean project name for directory
        clean_name = re.sub(r'[^a-zA-Z0-9\-_\s]', '', project_name)
        clean_name = re.sub(r'\s+', '-', clean_name.strip())
        clean_name = clean_name.lower()
        return clean_name or "extracted-project"
    
    def _generate_readme(self, project_dir: Path, metadata: Optional[PASVGMetadata], 
                        extracted_files: List[str]):
        """Generate README for the extracted project."""
        project_name = metadata.name if metadata else "PASVG Project"
        description = metadata.description if metadata else "Project extracted from PASVG artifact"
        technologies = ', '.join(metadata.technologies) if metadata and metadata.technologies else ''
        platforms = ', '.join(metadata.platforms) if metadata and metadata.platforms else ''
        
        readme_content = f"""# {project_name}

{description}

## Project Overview

This project was extracted from a PASVG (Project Artifact SVG) file - a revolutionary single-file project container that embeds all source code, configuration, and documentation within an SVG format.

### Technologies
{technologies}

### Target Platforms
{platforms}

## Extracted Files

This project contains {len(extracted_files)} extracted files:

{chr(10).join(f'- `{file}`' for file in sorted(extracted_files))}

## Building

To build this project, run:

```bash
./build.sh
```

## About PASVG

PASVG (Project Artifact SVG) is an innovative approach to project distribution that:
- ✅ **Single-source-of-truth**: Everything in one SVG file
- ✅ **Human-readable**: Visual documentation + embedded code
- ✅ **Machine-parseable**: Automated extraction and builds
- ✅ **Version control friendly**: Text-based format
- ✅ **Cross-platform**: Works everywhere SVG is supported

Generated by WhyML PASVG system.
"""
        
        with open(project_dir / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)


class ExtractionError(Exception):
    """Custom exception for extraction errors."""
    pass


class FileExtractor:
    """Specialized file extractor for different file types."""
    
    def __init__(self):
        self.extractors = {
            FileType.MANIFEST: self._extract_manifest,
            FileType.SOURCE_CODE: self._extract_source,
            FileType.CONFIGURATION: self._extract_config,
            FileType.STYLESHEET: self._extract_style,
            FileType.BINARY: self._extract_binary,
        }
    
    def extract_file(self, file_type: FileType, content: str, filename: str) -> str:
        """Extract and process file based on type."""
        extractor = self.extractors.get(file_type, self._extract_default)
        return extractor(content, filename)
    
    def _extract_manifest(self, content: str, filename: str) -> str:
        """Extract YAML manifest file."""
        # Validate YAML structure
        try:
            import yaml
            yaml.safe_load(content)
        except yaml.YAMLError:
            # Content might be malformed, but return as-is
            pass
        return content
    
    def _extract_source(self, content: str, filename: str) -> str:
        """Extract source code file."""
        return content
    
    def _extract_config(self, content: str, filename: str) -> str:
        """Extract configuration file."""
        return content
    
    def _extract_style(self, content: str, filename: str) -> str:
        """Extract CSS/style file."""
        return content
    
    def _extract_binary(self, content: str, filename: str) -> str:
        """Extract binary file (base64 encoded)."""
        # For binary files, content would be base64 encoded
        return content
    
    def _extract_default(self, content: str, filename: str) -> str:
        """Default extractor for unknown file types."""
        return content
