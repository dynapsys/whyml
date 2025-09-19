#!/usr/bin/env python3
"""
PASVG Generator - Project Artifact SVG Creator
Creates self-contained SVG files that embed entire projects.
"""

import re
import json
import base64
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from xml.sax.saxutils import escape


@dataclass
class SourceFile:
    filename: str
    content: str
    file_type: str
    language: str
    section: str


@dataclass
class ProjectMetadata:
    name: str
    description: str
    version: str
    platforms: List[str]
    technologies: List[str]
    build_targets: List[str]


class TutorialParser:
    def __init__(self):
        self.file_header_pattern = re.compile(
            r'\*\*([^*]+\.(yaml|yml|json|js|py|php|html|css|dockerfile|sh|xml)):\*\*'
        )
        
    def parse_tutorial(self, content: str, tutorial_name: str) -> Tuple[ProjectMetadata, List[SourceFile]]:
        lines = content.split('\n')
        metadata = self._extract_metadata(lines, tutorial_name)
        source_files = self._extract_source_files(content)
        return metadata, source_files
    
    def _extract_metadata(self, lines: List[str], tutorial_name: str) -> ProjectMetadata:
        name = lines[0][2:].strip() if lines[0].startswith('# ') else "Unknown Project"
        description = "Project generated from WhyML tutorial"
        
        # Find overview section
        for i, line in enumerate(lines):
            if line.startswith('## Overview') and i+1 < len(lines):
                description = lines[i+1].strip() if lines[i+1].strip() else description
                break
        
        content_lower = '\n'.join(lines).lower()
        technologies = []
        platforms = []
        build_targets = []
        
        # Extract technologies
        if 'docker' in content_lower:
            technologies.append('Docker')
            build_targets.append('Container')
        if 'react' in content_lower:
            technologies.append('React')
            build_targets.append('SPA')
        if 'vue' in content_lower:
            technologies.append('Vue.js')
            build_targets.append('SPA')
        if 'android' in content_lower or 'apk' in content_lower:
            platforms.append('Android')
            build_targets.append('APK')
        if 'tauri' in content_lower:
            technologies.append('Tauri')
            platforms.extend(['Windows', 'Linux'])
            build_targets.append('Desktop')
        if 'pwa' in content_lower:
            technologies.append('PWA')
            build_targets.append('Progressive Web App')
        if 'php' in content_lower:
            technologies.append('PHP')
            build_targets.append('Web Application')
        
        return ProjectMetadata(
            name=name,
            description=description,
            version="1.0.0",
            platforms=platforms or ['Web'],
            technologies=technologies or ['HTML', 'CSS', 'JavaScript'],
            build_targets=build_targets or ['Web Application']
        )
    
    def _extract_source_files(self, content: str) -> List[SourceFile]:
        source_files = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            file_match = self.file_header_pattern.search(line)
            
            if file_match:
                filename = file_match.group(1)
                
                # Look for code block
                j = i + 1
                while j < len(lines) and not lines[j].startswith('```'):
                    j += 1
                
                if j < len(lines):
                    language = lines[j][3:].strip() or self._detect_language(filename)
                    j += 1
                    code_lines = []
                    
                    while j < len(lines) and not lines[j].startswith('```'):
                        code_lines.append(lines[j])
                        j += 1
                    
                    if code_lines:
                        source_file = SourceFile(
                            filename=filename,
                            content='\n'.join(code_lines),
                            file_type=self._get_file_type(filename),
                            language=language,
                            section=self._get_current_section(lines, i)
                        )
                        source_files.append(source_file)
                        i = j
                        continue
            i += 1
        
        return source_files
    
    def _detect_language(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.html': 'html',
            '.css': 'css', '.yaml': 'yaml', '.yml': 'yaml',
            '.json': 'json', '.php': 'php', '.sh': 'bash',
            '.xml': 'xml', '.dockerfile': 'dockerfile'
        }
        return lang_map.get(ext, 'text')
    
    def _get_file_type(self, filename: str) -> str:
        if 'docker' in filename.lower():
            return 'container'
        elif filename.endswith(('.yaml', '.yml')):
            return 'manifest'
        elif filename.endswith('.json'):
            return 'config'
        elif filename.endswith(('.py', '.js', '.php')):
            return 'source'
        elif filename.endswith(('.html', '.css')):
            return 'web'
        elif filename.endswith('.sh'):
            return 'script'
        return 'resource'
    
    def _get_current_section(self, lines: List[str], current_line: int) -> str:
        for i in range(current_line, -1, -1):
            line = lines[i]
            if line.startswith('## '):
                return line[3:].strip()
        return "Unknown Section"


class PASVGGenerator:
    def __init__(self):
        self.parser = TutorialParser()
        self.svg_width = 1400
        self.svg_height = 1000
        
    def generate_pasvg(self, tutorial_path: str, output_path: str) -> str:
        with open(tutorial_path, 'r', encoding='utf-8') as f:
            tutorial_content = f.read()
        
        tutorial_name = Path(tutorial_path).stem
        metadata, source_files = self.parser.parse_tutorial(tutorial_content, tutorial_name)
        
        svg_content = self._create_svg(metadata, source_files)
        
        pasvg_path = Path(output_path) / f"{tutorial_name}.pasvg.svg"
        pasvg_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(pasvg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"✅ Generated PASVG: {pasvg_path}")
        print(f"   📁 {len(source_files)} source files embedded")
        print(f"   🏗️  Targets: {', '.join(metadata.build_targets)}")
        
        return str(pasvg_path)
    
    def _create_svg(self, metadata: ProjectMetadata, source_files: List[SourceFile]) -> str:
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     viewBox="0 0 {self.svg_width} {self.svg_height}"
     data-pasvg-version="1.0"
     data-project-name="{escape(metadata.name)}">

<!-- PASVG: Project Artifact SVG -->
<defs>
    <style><![CDATA[
        .pasvg-title {{ font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; fill: #2563eb; }}
        .pasvg-subtitle {{ font-family: Arial, sans-serif; font-size: 14px; fill: #6b7280; }}
        .pasvg-section {{ font-family: Arial, sans-serif; font-size: 12px; fill: #374151; }}
        .pasvg-code {{ font-family: monospace; font-size: 10px; fill: #1f2937; }}
    ]]></style>
</defs>

<!-- Project metadata -->
<metadata>
    <project xmlns="http://whyml.org/pasvg/1.0">
        <name>{escape(metadata.name)}</name>
        <description>{escape(metadata.description)}</description>
        <version>{escape(metadata.version)}</version>
        <platforms>{escape(', '.join(metadata.platforms))}</platforms>
        <technologies>{escape(', '.join(metadata.technologies))}</technologies>
        <build-targets>{escape(', '.join(metadata.build_targets))}</build-targets>
    </project>
</metadata>

{self._create_visual_layout(metadata, source_files)}

{self._embed_source_files(source_files)}

{self._create_build_config(metadata, source_files)}

</svg>'''
    
    def _create_visual_layout(self, metadata: ProjectMetadata, source_files: List[SourceFile]) -> str:
        return f'''<!-- Visual Layout -->
<rect width="100%" height="100%" fill="#ffffff"/>
<rect x="0" y="0" width="{self.svg_width}" height="80" fill="#dbeafe" stroke="#3b82f6"/>

<text x="20" y="35" class="pasvg-title">{escape(metadata.name)}</text>
<text x="20" y="55" class="pasvg-subtitle">{escape(metadata.description)}</text>

<!-- Technology badges -->
<g transform="translate(20, 90)">
{self._create_tech_badges(metadata.technologies)}
</g>

<!-- File overview -->
<g transform="translate(20, 150)">
    <text x="0" y="0" class="pasvg-title" font-size="18">Project Files ({len(source_files)})</text>
{self._create_file_overview(source_files)}
</g>'''
    
    def _create_tech_badges(self, technologies: List[str]) -> str:
        badges = []
        x_offset = 0
        for tech in technologies:
            width = len(tech) * 8 + 20
            badges.append(f'''
    <g transform="translate({x_offset}, 0)">
        <rect width="{width}" height="20" rx="10" fill="#3b82f6" opacity="0.1"/>
        <text x="{width//2}" y="14" text-anchor="middle" class="pasvg-section" fill="#3b82f6">{tech}</text>
    </g>''')
            x_offset += width + 10
        return '\n'.join(badges)
    
    def _create_file_overview(self, source_files: List[SourceFile]) -> str:
        files_display = []
        y_pos = 20
        for i, file in enumerate(source_files[:10]):  # Show first 10 files
            files_display.append(f'''
    <text x="0" y="{y_pos}" class="pasvg-section">📄 {file.filename} ({file.file_type})</text>''')
            y_pos += 18
        
        if len(source_files) > 10:
            files_display.append(f'''
    <text x="0" y="{y_pos}" class="pasvg-section">... and {len(source_files)-10} more files</text>''')
        
        return '\n'.join(files_display)
    
    def _embed_source_files(self, source_files: List[SourceFile]) -> str:
        embedded = ['<!-- Embedded Source Files -->']
        
        for i, file in enumerate(source_files):
            file_id = f"file_{i}"
            embedded.append(f'''
<foreignObject id="{file_id}" data-filename="{escape(file.filename)}" 
              data-type="{file.file_type}" data-language="{file.language}" 
              data-section="{escape(file.section)}" style="display: none;">
    <![CDATA[{file.content}]]>
</foreignObject>''')
        
        return '\n'.join(embedded)
    
    def _create_build_config(self, metadata: ProjectMetadata, source_files: List[SourceFile]) -> str:
        build_config = {
            'project': metadata.name,
            'targets': metadata.build_targets,
            'files': [{'filename': f.filename, 'type': f.file_type} for f in source_files]
        }
        
        # Create safe filename for instructions
        safe_filename = re.sub(r'[^a-zA-Z0-9\-_]', '-', metadata.name.lower())
        
        return f'''
<!-- Build Configuration -->
<script type="application/json" data-filename="pasvg-build.json">
    <![CDATA[{json.dumps(build_config, indent=2)}]]>
</script>

<!-- Build Instructions -->
<g transform="translate(20, 400)">
    <text x="0" y="0" class="pasvg-title" font-size="16">Build Instructions</text>
    <text x="0" y="25" class="pasvg-code">1. Extract: python pasvg_extractor.py {escape(safe_filename)}.pasvg.svg</text>
    <text x="0" y="40" class="pasvg-code">2. Build: cd extracted &amp;&amp; ./build.sh</text>
    <text x="0" y="60" class="pasvg-section">Targets: {escape(', '.join(metadata.build_targets))}</text>
</g>'''


def main():
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python pasvg_generator.py <tutorial_file> <output_directory>")
        sys.exit(1)
    
    generator = PASVGGenerator()
    tutorial_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    pasvg_path = generator.generate_pasvg(tutorial_file, output_dir)
    print(f"PASVG generated: {pasvg_path}")


if __name__ == "__main__":
    main()
