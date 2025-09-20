"""
PASVG Generator - Creates PASVG files from project sources.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Optional
from xml.sax.saxutils import escape
from datetime import datetime

from pasvg.core.models import (
    PASVGMetadata, SourceFile, ProjectConfig, GenerationResult, FileType
)
from pasvg.importers.markdown_importer import MarkdownImporter
from pasvg.generators.svg_renderer import SVGRenderer
from pasvg.utils.file_utils import FileOperations, FileScanner, FileValidator


class Generator:
    """Generates PASVG files from various project sources."""
    
    def __init__(self, svg_width: int = 1200, svg_height: int = 800):
        self.svg_width = svg_width
        self.svg_height = svg_height
        self.markdown_importer = MarkdownImporter()
        self.svg_renderer = SVGRenderer(svg_width, svg_height)
        self.file_ops = FileOperations()
        self.file_scanner = FileScanner()
        self.file_validator = FileValidator()
    
    def generate_from_markdown(self, markdown_file: str, output_dir: str) -> GenerationResult:
        """Generate PASVG from markdown tutorial file."""
        result = GenerationResult(success=True)
        
        try:
            # Import project from markdown
            project_config = self.markdown_importer.import_from_markdown(markdown_file)
            
            if not project_config:
                result.add_error("Failed to import project from markdown")
                return result
            
            # Generate PASVG file
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            pasvg_filename = self._create_pasvg_filename(project_config.metadata.name)
            pasvg_path = output_path / pasvg_filename
            
            # Generate SVG content
            svg_content = self.svg_renderer.render(project_config)
            
            # Write PASVG file
            with open(pasvg_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            result.pasvg_file = pasvg_path
            result.metadata = project_config.metadata
            result.file_count = project_config.file_count()
            result.total_size = project_config.total_size()
            
            print(f"✅ Generated PASVG: {pasvg_path}")
            print(f"   📁 {result.file_count} source files embedded")
            print(f"   🏗️  Targets: {', '.join(project_config.build_config.targets)}")
            
        except Exception as e:
            result.add_error(f"Generation failed: {e}")
        
        return result
    
    def generate_from_directory(self, project_dir: str, output_dir: str, 
                               metadata: Optional[PASVGMetadata] = None) -> GenerationResult:
        """Generate PASVG from project directory."""
        result = GenerationResult(success=True)
        
        try:
            project_path = Path(project_dir)
            if not project_path.exists():
                result.add_error(f"Project directory not found: {project_dir}")
                return result
            
            # Create project config
            if metadata is None:
                metadata = PASVGMetadata(
                    name=project_path.name,
                    description=f"Project generated from {project_path}",
                    created_at=datetime.now().isoformat()
                )
            
            project_config = ProjectConfig(
                metadata=metadata,
                svg_width=self.svg_width,
                svg_height=self.svg_height
            )
            
            # Scan and add source files
            source_files = self.file_utils.scan_directory(project_path)
            for source_file in source_files:
                project_config.add_source_file(source_file)
            
            # Detect build targets
            build_targets = self._detect_build_targets(source_files)
            project_config.build_config.targets = build_targets
            
            # Generate PASVG
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            pasvg_filename = self._create_pasvg_filename(metadata.name)
            pasvg_path = output_path / pasvg_filename
            
            svg_content = self.svg_renderer.render(project_config)
            
            with open(pasvg_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            result.pasvg_file = pasvg_path
            result.metadata = metadata
            result.file_count = len(source_files)
            result.total_size = sum(f.size for f in source_files)
            
        except Exception as e:
            result.add_error(f"Generation failed: {e}")
        
        return result
    
    def generate_from_config(self, config_file: str, output_dir: str) -> GenerationResult:
        """Generate PASVG from configuration file."""
        result = GenerationResult(success=True)
        
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                result.add_error(f"Config file not found: {config_file}")
                return result
            
            # Load configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                else:
                    import yaml
                    config_data = yaml.safe_load(f)
            
            # Create project config from data
            project_config = self._create_project_from_config(config_data)
            
            # Generate PASVG
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            pasvg_filename = self._create_pasvg_filename(project_config.metadata.name)
            pasvg_path = output_path / pasvg_filename
            
            svg_content = self.svg_renderer.render(project_config)
            
            with open(pasvg_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            result.pasvg_file = pasvg_path
            result.metadata = project_config.metadata
            result.file_count = project_config.file_count()
            result.total_size = project_config.total_size()
            
        except Exception as e:
            result.add_error(f"Generation failed: {e}")
        
        return result
    
    def _create_pasvg_filename(self, project_name: str) -> str:
        """Create a valid PASVG filename from project name."""
        # Clean project name for filename
        clean_name = re.sub(r'[^a-zA-Z0-9\-_\s]', '', project_name)
        clean_name = re.sub(r'\s+', '-', clean_name.strip())
        clean_name = clean_name.lower()
        return f"{clean_name}.pasvg.svg"
    
    def _detect_build_targets(self, source_files: List[SourceFile]) -> List[str]:
        """Detect possible build targets from source files."""
        targets = set()
        
        for file in source_files:
            filename = file.filename.lower()
            content = file.content.lower()
            
            # Docker targets
            if 'docker' in filename or 'dockerfile' in filename:
                targets.add("Container")
            
            # Web targets
            if filename.endswith(('.html', '.css', '.js')):
                targets.add("Web Application")
            
            # Node.js/React/Vue
            if filename == 'package.json':
                if 'react' in content:
                    targets.add("SPA")
                if 'vue' in content:
                    targets.add("SPA")
                if 'manifest.json' in content or 'workbox' in content:
                    targets.add("Progressive Web App")
            
            # Mobile targets
            if filename.endswith('.gradle') or 'android' in filename:
                targets.add("APK")
            
            # Desktop targets
            if 'tauri' in content or filename.endswith('.rs'):
                targets.add("Desktop")
        
        return list(targets)
    
    def _create_project_from_config(self, config_data: Dict) -> ProjectConfig:
        """Create ProjectConfig from configuration data."""
        metadata_data = config_data.get('metadata', {})
        metadata = PASVGMetadata.from_dict(metadata_data)
        
        project_config = ProjectConfig(
            metadata=metadata,
            svg_width=config_data.get('svg_width', self.svg_width),
            svg_height=config_data.get('svg_height', self.svg_height)
        )
        
        # Add source files from config
        files_data = config_data.get('files', [])
        for file_data in files_data:
            source_file = SourceFile(
                filename=file_data['filename'],
                content=file_data['content'],
                file_type=FileType(file_data.get('type', 'source')),
                language=file_data.get('language', ''),
                section=file_data.get('section', '')
            )
            project_config.add_source_file(source_file)
        
        # Set build targets
        build_data = config_data.get('build', {})
        project_config.build_config.targets = build_data.get('targets', [])
        
        return project_config


class GeneratorError(Exception):
    """Custom exception for generator errors."""
    pass
