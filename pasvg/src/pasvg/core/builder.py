"""
PASVG Builder - Automated build system for extracted projects.
"""

import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from pasvg.core.models import BuildResult, PASVGMetadata
from pasvg.utils.file_utils import FileOperations, FileScanner, FileValidator


class Builder:
    """Automated build system for PASVG projects."""
    
    def __init__(self, work_dir: Optional[str] = None):
        self.work_dir = Path(work_dir) if work_dir else Path("./pasvg-builds")
        self.work_dir.mkdir(exist_ok=True)
        self.file_ops = FileOperations()
        self.file_scanner = FileScanner()
        self.file_validator = FileValidator()
    
    def build_project(self, project_dir: Path, build_targets: List[str] = None, 
                     clean: bool = False) -> BuildResult:
        """Build project with specified targets."""
        try:
            if clean:
                self._clean_build_artifacts(project_dir)
            
            # Auto-detect targets if not provided
            if not build_targets:
                build_targets = self._detect_targets(project_dir)
            
            if not build_targets:
                return BuildResult(
                    success=False,
                    built_targets=[],
                    errors=["No buildable targets detected in project"]
                )
            
            built_targets = []
            errors = []
            
            # Build each target
            for target in build_targets:
                try:
                    if self._build_target(project_dir, target):
                        built_targets.append(target)
                    else:
                        errors.append(f"Failed to build target: {target}")
                except Exception as e:
                    errors.append(f"Error building {target}: {str(e)}")
            
            return BuildResult(
                success=len(built_targets) > 0,
                built_targets=built_targets,
                errors=errors if errors else None
            )
            
        except Exception as e:
            return BuildResult(
                success=False,
                built_targets=[],
                errors=[f"Build system error: {str(e)}"]
            )
    
    def build_all_pasvg_targets(self, pasvg_dir: Path) -> Dict[str, BuildResult]:
        """Build all possible targets from all PASVG files in directory."""
        results = {}
        pasvg_files = list(pasvg_dir.glob("*.pasvg.svg"))
        
        for pasvg_file in pasvg_files:
            # First extract the project
            from pasvg.core.extractor import Extractor
            extractor = Extractor()
            extract_result = extractor.extract(str(pasvg_file), str(self.work_dir))
            
            if extract_result.success:
                # Build the extracted project
                build_result = self.build_project(
                    Path(extract_result.project_dir),
                    extract_result.build_targets
                )
                results[pasvg_file.name] = build_result
            else:
                results[pasvg_file.name] = BuildResult(
                    success=False,
                    built_targets=[],
                    errors=[f"Failed to extract: {'; '.join(extract_result.errors)}"]
                )
        
        return results
    
    def _detect_targets(self, project_dir: Path) -> List[str]:
        """Detect buildable targets in project."""
        targets = []
        
        # Check for Docker
        if (project_dir / "docker-compose.yml").exists():
            targets.append("docker-compose")
        elif (project_dir / "Dockerfile").exists():
            targets.append("docker")
        
        # Check for Node.js/React/Vue
        package_json_path = project_dir / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                dependencies = package_data.get("dependencies", {})
                dev_dependencies = package_data.get("devDependencies", {})
                all_deps = {**dependencies, **dev_dependencies}
                scripts = package_data.get("scripts", {})
                
                # Check for specific frameworks
                if "react" in all_deps:
                    targets.append("react-spa")
                if "vue" in all_deps:
                    targets.append("vue-spa")
                if "@tauri-apps/cli" in all_deps or "tauri" in scripts:
                    targets.append("tauri-desktop")
                
                # Check for PWA manifest
                pwa_manifests = [
                    project_dir / "public" / "manifest.json",
                    project_dir / "src" / "manifest.json",
                    project_dir / "manifest.json"
                ]
                if any(m.exists() for m in pwa_manifests):
                    targets.append("pwa")
                
                # Generic Node.js build if has build script
                if "build" in scripts:
                    targets.append("nodejs")
                    
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Check for Python
        if (project_dir / "requirements.txt").exists() or \
           (project_dir / "pyproject.toml").exists() or \
           (project_dir / "setup.py").exists():
            targets.append("python")
        
        # Check for Android
        if (project_dir / "build.gradle").exists() or \
           (project_dir / "android").exists():
            targets.append("android-apk")
        
        # Check for Rust/Tauri
        if (project_dir / "src-tauri" / "Cargo.toml").exists():
            targets.append("tauri-desktop")
        elif (project_dir / "Cargo.toml").exists():
            targets.append("rust")
        
        # Check for PHP
        if list(project_dir.glob("*.php")):
            targets.append("php")
        
        # Static web as fallback
        if list(project_dir.glob("*.html")):
            targets.append("static-web")
        
        return list(set(targets))  # Remove duplicates
    
    def _build_target(self, project_dir: Path, target: str) -> bool:
        """Build specific target."""
        build_methods = {
            "docker-compose": self._build_docker_compose,
            "docker": self._build_docker,
            "react-spa": self._build_react_spa,
            "vue-spa": self._build_vue_spa,
            "nodejs": self._build_nodejs,
            "pwa": self._build_pwa,
            "android-apk": self._build_android_apk,
            "tauri-desktop": self._build_tauri_desktop,
            "rust": self._build_rust,
            "python": self._build_python,
            "php": self._build_php,
            "static-web": self._build_static_web
        }
        
        build_method = build_methods.get(target)
        if build_method:
            return build_method(project_dir)
        else:
            return False
    
    def _build_docker_compose(self, project_dir: Path) -> bool:
        """Build with Docker Compose."""
        try:
            result = subprocess.run([
                "docker-compose", "build"
            ], cwd=project_dir, capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _build_docker(self, project_dir: Path) -> bool:
        """Build Docker image."""
        try:
            image_name = project_dir.name.lower().replace(' ', '-')
            result = subprocess.run([
                "docker", "build", "-t", image_name, "."
            ], cwd=project_dir, capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _build_nodejs(self, project_dir: Path) -> bool:
        """Build Node.js project."""
        try:
            # Install dependencies
            install_result = subprocess.run([
                "npm", "install"
            ], cwd=project_dir, capture_output=True, text=True, timeout=180)
            
            if install_result.returncode != 0:
                return False
            
            # Build project
            build_result = subprocess.run([
                "npm", "run", "build"
            ], cwd=project_dir, capture_output=True, text=True, timeout=180)
            
            return build_result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _build_react_spa(self, project_dir: Path) -> bool:
        """Build React SPA."""
        if not self._build_nodejs(project_dir):
            return False
        
        # Check if build directory was created
        return (project_dir / "build").exists() or (project_dir / "dist").exists()
    
    def _build_vue_spa(self, project_dir: Path) -> bool:
        """Build Vue SPA."""
        if not self._build_nodejs(project_dir):
            return False
        
        # Check if dist directory was created
        return (project_dir / "dist").exists() or (project_dir / "build").exists()
    
    def _build_pwa(self, project_dir: Path) -> bool:
        """Build Progressive Web App."""
        # First build the base application
        if not self._build_nodejs(project_dir):
            return False
        
        # Create PWA structure
        pwa_dir = project_dir / "pwa-output"
        pwa_dir.mkdir(exist_ok=True)
        
        # Copy built files
        for build_dir_name in ["build", "dist"]:
            build_dir = project_dir / build_dir_name
            if build_dir.exists():
                shutil.copytree(build_dir, pwa_dir / "app", dirs_exist_ok=True)
                break
        
        # Create service worker if not exists
        sw_path = pwa_dir / "app" / "sw.js"
        if not sw_path.exists():
            sw_content = '''
const CACHE_NAME = 'pasvg-pwa-v1';
const urlsToCache = ['/', '/static/js/', '/static/css/'];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});
'''
            with open(sw_path, 'w') as f:
                f.write(sw_content)
        
        return True
    
    def _build_android_apk(self, project_dir: Path) -> bool:
        """Build Android APK (requires Android SDK)."""
        gradle_wrapper = project_dir / "gradlew"
        
        if gradle_wrapper.exists():
            gradle_cmd = str(gradle_wrapper)
        elif shutil.which("gradle"):
            gradle_cmd = "gradle"
        else:
            return False
        
        try:
            result = subprocess.run([
                gradle_cmd, "assembleRelease"
            ], cwd=project_dir, capture_output=True, text=True, timeout=600)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _build_tauri_desktop(self, project_dir: Path) -> bool:
        """Build Tauri desktop application."""
        if not shutil.which("cargo"):
            return False
        
        try:
            # Install npm dependencies first
            npm_result = subprocess.run([
                "npm", "install"
            ], cwd=project_dir, capture_output=True, text=True, timeout=180)
            
            if npm_result.returncode != 0:
                return False
            
            # Build Tauri app
            result = subprocess.run([
                "npm", "run", "tauri:build"
            ], cwd=project_dir, capture_output=True, text=True, timeout=600)
            
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _build_rust(self, project_dir: Path) -> bool:
        """Build Rust project."""
        if not shutil.which("cargo"):
            return False
        
        try:
            result = subprocess.run([
                "cargo", "build", "--release"
            ], cwd=project_dir, capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _build_python(self, project_dir: Path) -> bool:
        """Build Python project."""
        try:
            python_cmd = shutil.which("python3") or shutil.which("python")
            if not python_cmd:
                return False
            
            # Create virtual environment
            venv_result = subprocess.run([
                python_cmd, "-m", "venv", "venv"
            ], cwd=project_dir, capture_output=True, text=True, timeout=60)
            
            if venv_result.returncode != 0:
                return False
            
            # Determine pip path
            if (project_dir / "venv" / "bin" / "pip").exists():
                pip_cmd = str(project_dir / "venv" / "bin" / "pip")
            elif (project_dir / "venv" / "Scripts" / "pip.exe").exists():
                pip_cmd = str(project_dir / "venv" / "Scripts" / "pip.exe")
            else:
                return False
            
            # Install dependencies
            if (project_dir / "requirements.txt").exists():
                install_result = subprocess.run([
                    pip_cmd, "install", "-r", "requirements.txt"
                ], cwd=project_dir, capture_output=True, text=True, timeout=180)
            elif (project_dir / "pyproject.toml").exists():
                install_result = subprocess.run([
                    pip_cmd, "install", "-e", "."
                ], cwd=project_dir, capture_output=True, text=True, timeout=180)
            else:
                return False
            
            return install_result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _build_php(self, project_dir: Path) -> bool:
        """Build PHP project."""
        # Check for Composer
        if (project_dir / "composer.json").exists() and shutil.which("composer"):
            try:
                result = subprocess.run([
                    "composer", "install"
                ], cwd=project_dir, capture_output=True, text=True, timeout=180)
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return False
        
        # For PHP projects without Composer, just verify PHP files exist
        return len(list(project_dir.glob("*.php"))) > 0
    
    def _build_static_web(self, project_dir: Path) -> bool:
        """Build static web files."""
        static_dir = project_dir / "static-output"
        static_dir.mkdir(exist_ok=True)
        
        # Copy HTML, CSS, JS files
        file_patterns = ["*.html", "*.css", "*.js", "*.json"]
        for pattern in file_patterns:
            for file in project_dir.glob(pattern):
                if file.name != "package.json":  # Skip package.json
                    shutil.copy2(file, static_dir)
        
        # Copy common asset directories
        asset_dirs = ["assets", "images", "css", "js", "fonts", "media"]
        for asset_dir in asset_dirs:
            source_dir = project_dir / asset_dir
            if source_dir.exists() and source_dir.is_dir():
                shutil.copytree(source_dir, static_dir / asset_dir, dirs_exist_ok=True)
        
        return True
    
    def _clean_build_artifacts(self, project_dir: Path):
        """Clean previous build artifacts."""
        clean_patterns = [
            "build", "dist", "target", "node_modules/.cache",
            "*.pyc", "__pycache__", ".pytest_cache",
            "pwa-output", "static-output"
        ]
        
        for pattern in clean_patterns:
            if "*" in pattern:
                # Glob pattern
                for path in project_dir.glob(pattern):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(path, ignore_errors=True)
            else:
                # Directory name
                clean_dir = project_dir / pattern
                if clean_dir.exists():
                    shutil.rmtree(clean_dir, ignore_errors=True)
    
    def generate_build_report(self, results: Dict[str, BuildResult]) -> str:
        """Generate comprehensive build report."""
        report_lines = [
            "# PASVG Build System Report",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Build Results Summary",
            ""
        ]
        
        total_pasvg = len(results)
        successful_builds = sum(1 for result in results.values() if result.success)
        total_targets = sum(len(result.built_targets) for result in results.values())
        
        report_lines.extend([
            f"- Total PASVG files processed: {total_pasvg}",
            f"- Successful builds: {successful_builds}",
            f"- Total targets built: {total_targets}",
            "",
            "## Detailed Results",
            ""
        ])
        
        for pasvg_file, result in results.items():
            report_lines.append(f"### {pasvg_file}")
            if result.success:
                report_lines.append(f"✅ Successfully built: {', '.join(result.built_targets)}")
            else:
                report_lines.append("❌ Build failed")
                if result.errors:
                    for error in result.errors:
                        report_lines.append(f"   - {error}")
            report_lines.append("")
        
        report_lines.extend([
            "",
            "## Innovation Achieved",
            "",
            "PASVG (Project Artifact SVG) demonstrates:",
            "- Single-source-of-truth project containers",
            "- Human-readable documentation + machine-extractable code",
            "- Cross-platform build automation",
            "- Seamless tutorial-to-deployment workflow"
        ])
        
        return "\n".join(report_lines)


class BuildError(Exception):
    """Custom exception for build errors."""
    pass
