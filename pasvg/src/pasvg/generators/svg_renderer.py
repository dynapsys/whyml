"""
SVG Renderer - Renders PASVG files with embedded content and visual layout.
"""

import json
from typing import List, Dict
from xml.sax.saxutils import escape
from datetime import datetime

from pasvg.core.models import ProjectConfig, SourceFile


class SVGRenderer:
    """Renders ProjectConfig into SVG format with embedded content."""
    
    def __init__(self, svg_width: int = 1200, svg_height: int = 800):
        self.svg_width = svg_width
        self.svg_height = svg_height
        self.pasvg_version = "1.0"
    
    def render(self, project_config: ProjectConfig) -> str:
        """Render complete PASVG SVG content."""
        metadata = project_config.metadata
        source_files = project_config.source_files
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{self.svg_width}" height="{self.svg_height}" 
     viewBox="0 0 {self.svg_width} {self.svg_height}"
     data-pasvg-version="{self.pasvg_version}"
     data-project-name="{escape(metadata.name)}">

<!-- PASVG: Project Artifact SVG -->
{self._render_styles()}

{self._render_metadata(metadata)}

{self._render_visual_layout(metadata, source_files)}

{self._render_embedded_files(source_files)}

{self._render_build_config(project_config)}

</svg>'''
        
        return svg_content
    
    def _render_styles(self) -> str:
        """Render CSS styles for visual elements."""
        return '''<defs>
    <style><![CDATA[
        .pasvg-title { font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; fill: #2563eb; }
        .pasvg-subtitle { font-family: Arial, sans-serif; font-size: 14px; fill: #6b7280; }
        .pasvg-section { font-family: Arial, sans-serif; font-size: 12px; fill: #374151; }
        .pasvg-code { font-family: monospace; font-size: 10px; fill: #1f2937; }
        .pasvg-tech-badge { font-family: Arial, sans-serif; font-size: 10px; fill: #ffffff; }
        .pasvg-file-item { font-family: monospace; font-size: 9px; fill: #4b5563; }
    ]]></style>
</defs>'''
    
    def _render_metadata(self, metadata) -> str:
        """Render project metadata."""
        return f'''<!-- Project metadata -->
<metadata>
    <project xmlns="http://whyml.org/pasvg/1.0">
        <name>{escape(metadata.name)}</name>
        <description>{escape(metadata.description)}</description>
        <version>{escape(metadata.version)}</version>
        <author>{escape(metadata.author)}</author>
        <technologies>{escape(', '.join(metadata.technologies))}</technologies>
        <platforms>{escape(', '.join(metadata.platforms))}</platforms>
        <build-targets>{escape(', '.join(metadata.build_targets))}</build-targets>
        <created-at>{escape(metadata.created_at)}</created-at>
    </project>
</metadata>'''
    
    def _render_visual_layout(self, metadata, source_files: List[SourceFile]) -> str:
        """Render visual layout with project information."""
        layout = f'''<!-- Visual Layout -->
<rect width="100%" height="100%" fill="#ffffff"/>
<rect x="0" y="0" width="{self.svg_width}" height="80" fill="#dbeafe" stroke="#3b82f6"/>

<text x="20" y="35" class="pasvg-title">{escape(metadata.name)}</text>
<text x="20" y="55" class="pasvg-subtitle">{escape(metadata.description)}</text>

<!-- Technology badges -->
<g transform="translate(20, 90)">
{self._render_tech_badges(metadata.technologies)}
</g>

<!-- File overview -->
<g transform="translate(20, 150)">
    <text x="0" y="0" class="pasvg-title" font-size="18">Project Files ({len(source_files)})</text>
{self._render_file_overview(source_files)}
</g>

<!-- Project stats -->
<g transform="translate({self.svg_width - 200}, 90)">
    <text x="0" y="0" class="pasvg-section">Project Statistics</text>
    <text x="0" y="20" class="pasvg-code">Files: {len(source_files)}</text>
    <text x="0" y="35" class="pasvg-code">Size: {sum(f.size for f in source_files)} bytes</text>
    <text x="0" y="50" class="pasvg-code">Generated: {datetime.now().strftime('%Y-%m-%d')}</text>
</g>'''
        
        return layout
    
    def _render_tech_badges(self, technologies: List[str]) -> str:
        """Render technology badges."""
        badges = []
        x_offset = 0
        
        colors = {
            'Docker': '#2496ed', 'PHP': '#777bb4', 'Python': '#3776ab',
            'JavaScript': '#f7df1e', 'React': '#61dafb', 'Vue': '#4fc08d',
            'Tauri': '#ffc131', 'Rust': '#000000', 'YAML': '#cb171e',
            'CSS': '#1572b6', 'HTML': '#e34f26', 'Node': '#339933'
        }
        
        for tech in technologies:
            color = colors.get(tech, '#6b7280')
            badge_width = len(tech) * 7 + 16
            
            badges.append(f'''
    <rect x="{x_offset}" y="0" width="{badge_width}" height="20" fill="{color}" rx="3"/>
    <text x="{x_offset + badge_width//2}" y="14" class="pasvg-tech-badge" text-anchor="middle">{escape(tech)}</text>''')
            
            x_offset += badge_width + 8
        
        return ''.join(badges)
    
    def _render_file_overview(self, source_files: List[SourceFile]) -> str:
        """Render file overview list."""
        file_items = []
        y_offset = 25
        
        # Group files by type
        files_by_type = {}
        for file in source_files:
            file_type = file.file_type.value
            if file_type not in files_by_type:
                files_by_type[file_type] = []
            files_by_type[file_type].append(file)
        
        # Render grouped files
        for file_type, files in files_by_type.items():
            # Type header
            file_items.append(f'''
    <text x="0" y="{y_offset}" class="pasvg-section">{file_type.title()} Files ({len(files)}):</text>''')
            y_offset += 18
            
            # File list
            for file in files[:5]:  # Limit to 5 files per type for space
                size_kb = file.size / 1024
                file_items.append(f'''
    <text x="20" y="{y_offset}" class="pasvg-file-item">📄 {escape(file.filename)} ({size_kb:.1f}KB)</text>''')
                y_offset += 14
            
            if len(files) > 5:
                file_items.append(f'''
    <text x="20" y="{y_offset}" class="pasvg-file-item">... and {len(files) - 5} more files</text>''')
                y_offset += 14
            
            y_offset += 10
        
        return ''.join(file_items)
    
    def _render_embedded_files(self, source_files: List[SourceFile]) -> str:
        """Render embedded source files with CDATA sections."""
        embedded = ['<!-- Embedded Source Files -->']
        
        for i, file in enumerate(source_files):
            file_id = f"file_{i}"
            embedded.append(f'''
<foreignObject id="{file_id}" data-filename="{escape(file.filename)}" 
              data-type="{file.file_type.value}" data-language="{file.language}" 
              data-section="{escape(file.section)}" style="display: none;">
    <![CDATA[{file.content}]]>
</foreignObject>''')
        
        return '\n'.join(embedded)
    
    def _render_build_config(self, project_config: ProjectConfig) -> str:
        """Render build configuration and instructions."""
        build_config = {
            'project': project_config.metadata.name,
            'targets': project_config.build_config.targets,
            'files': [
                {'filename': f.filename, 'type': f.file_type.value} 
                for f in project_config.source_files
            ]
        }
        
        # Create safe filename for instructions
        safe_filename = self._create_safe_filename(project_config.metadata.name)
        
        return f'''
<!-- Build Configuration -->
<script type="application/json" data-filename="pasvg-build.json">
    <![CDATA[{json.dumps(build_config, indent=2)}]]>
</script>

<!-- Build Instructions -->
<g transform="translate(20, 400)">
    <text x="0" y="0" class="pasvg-title" font-size="16">Build Instructions</text>
    <text x="0" y="25" class="pasvg-code">1. Extract: python -m pasvg extract {escape(safe_filename)}.pasvg.svg</text>
    <text x="0" y="40" class="pasvg-code">2. Build: cd extracted &amp;&amp; ./build.sh</text>
    <text x="0" y="60" class="pasvg-section">Targets: {escape(', '.join(project_config.build_config.targets))}</text>
</g>'''
    
    def _create_safe_filename(self, project_name: str) -> str:
        """Create safe filename from project name."""
        import re
        safe_name = re.sub(r'[^a-zA-Z0-9\-_]', '-', project_name.lower())
        return safe_name


class VisualLayoutRenderer:
    """Specialized renderer for visual layout components."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
    
    def render_header(self, title: str, subtitle: str) -> str:
        """Render header section."""
        return f'''<g id="header">
    <rect x="0" y="0" width="{self.width}" height="80" fill="#f8fafc" stroke="#e2e8f0"/>
    <text x="20" y="35" class="pasvg-title">{escape(title)}</text>
    <text x="20" y="55" class="pasvg-subtitle">{escape(subtitle)}</text>
</g>'''
    
    def render_sidebar(self, items: List[str]) -> str:
        """Render sidebar with items."""
        sidebar_items = []
        y = 20
        
        for item in items:
            sidebar_items.append(f'''
    <text x="10" y="{y}" class="pasvg-section">{escape(item)}</text>''')
            y += 20
        
        return f'''<g id="sidebar">
    <rect x="{self.width - 200}" y="80" width="200" height="{self.height - 80}" fill="#f1f5f9"/>
    {''.join(sidebar_items)}
</g>'''
    
    def render_diagram(self, elements: List[Dict]) -> str:
        """Render architectural diagram."""
        diagram_elements = []
        
        for element in elements:
            elem_type = element.get('type', 'rect')
            if elem_type == 'rect':
                diagram_elements.append(f'''
    <rect x="{element['x']}" y="{element['y']}" 
          width="{element['width']}" height="{element['height']}" 
          fill="{element.get('fill', '#ddd')}" stroke="{element.get('stroke', '#999')}"/>''')
            elif elem_type == 'text':
                diagram_elements.append(f'''
    <text x="{element['x']}" y="{element['y']}" 
          class="{element.get('class', 'pasvg-section')}">{escape(element['text'])}</text>''')
        
        return f'''<g id="diagram">
    {''.join(diagram_elements)}
</g>'''


class RenderError(Exception):
    """Custom exception for rendering errors."""
    pass
