#!/usr/bin/env python3
"""
PASVG Publishing Script - Build, test and publish the PASVG package.
"""

import subprocess
import sys
import shutil
from pathlib import Path
from typing import List, Optional
import argparse


class PASVGPublisher:
    """Handle building, testing, and publishing of the PASVG package."""
    
    def __init__(self, package_dir: Path):
        self.package_dir = package_dir
        self.build_dir = package_dir / "build"
        self.dist_dir = package_dir / "dist"
    
    def clean(self) -> bool:
        """Clean build artifacts."""
        print("🧹 Cleaning build artifacts...")
        
        dirs_to_clean = [
            self.build_dir,
            self.dist_dir,
            self.package_dir / "src" / "pasvg.egg-info",
            self.package_dir / "pasvg.egg-info"
        ]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Removed: {dir_path}")
        
        # Clean __pycache__ directories
        for pycache in self.package_dir.rglob("__pycache__"):
            shutil.rmtree(pycache)
        
        print("✅ Clean complete")
        return True
    
    def lint(self) -> bool:
        """Run linting checks."""
        print("🔍 Running linting checks...")
        
        commands = [
            ["flake8", "src/pasvg", "--max-line-length=88", "--extend-ignore=E203"],
            ["black", "--check", "src/pasvg"],
            ["isort", "--check-only", "src/pasvg"]
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd, cwd=self.package_dir, capture_output=True, text=True
                )
                if result.returncode != 0:
                    print(f"❌ Linting failed: {' '.join(cmd)}")
                    print(result.stdout)
                    print(result.stderr)
                    return False
                else:
                    print(f"✅ {cmd[0]} passed")
            except FileNotFoundError:
                print(f"⚠️  {cmd[0]} not found, skipping...")
        
        print("✅ Linting complete")
        return True
    
    def test(self) -> bool:
        """Run package tests."""
        print("🧪 Running tests...")
        
        try:
            result = subprocess.run([
                "python3", "-m", "pytest", "tests/", "-v"
            ], cwd=self.package_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ All tests passed")
                return True
            else:
                print("❌ Tests failed:")
                print(result.stdout)
                print(result.stderr)
                return False
        except FileNotFoundError:
            print("⚠️  pytest not found, creating basic test...")
            return self._create_basic_test()
    
    def _create_basic_test(self) -> bool:
        """Create and run a basic test if pytest is not available."""
        test_script = self.package_dir / "test_basic.py"
        
        test_content = '''#!/usr/bin/env python3
"""Basic test script for PASVG package."""

import sys
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that main modules can be imported."""
    try:
        from pasvg import Generator, Extractor, Validator, Builder
        from pasvg.core.models import SourceFile, PASVGMetadata
        from pasvg.utils.file_utils import FileUtils
        print("✅ All main imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality."""
    try:
        from pasvg.utils.file_utils import FileUtils
        
        file_utils = FileUtils()
        # Test file type detection
        assert file_utils.detect_file_type("test.py") == "python"
        assert file_utils.detect_file_type("test.js") == "javascript"
        assert file_utils.detect_file_type("test.html") == "html"
        
        print("✅ Basic functionality tests passed")
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running basic PASVG tests...")
    
    success = True
    success &= test_imports()
    success &= test_basic_functionality()
    
    if success:
        print("🎉 All basic tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
'''
        
        with open(test_script, 'w') as f:
            f.write(test_content)
        
        try:
            result = subprocess.run([
                "python3", str(test_script)
            ], cwd=self.package_dir, capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            return result.returncode == 0
        finally:
            test_script.unlink(missing_ok=True)
    
    def build(self) -> bool:
        """Build the package."""
        print("🔨 Building package...")
        
        try:
            result = subprocess.run([
                "python3", "-m", "build"
            ], cwd=self.package_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Package built successfully")
                
                # List built files
                if self.dist_dir.exists():
                    built_files = list(self.dist_dir.glob("*"))
                    print("📦 Built files:")
                    for file in built_files:
                        print(f"   {file.name}")
                
                return True
            else:
                print("❌ Build failed:")
                print(result.stdout)
                print(result.stderr)
                return False
        except FileNotFoundError:
            print("❌ Build tool not found. Install with: pip install build")
            return False
    
    def test_install(self) -> bool:
        """Test package installation."""
        print("📦 Testing package installation...")
        
        if not self.dist_dir.exists():
            print("❌ No dist directory found. Run build first.")
            return False
        
        # Find wheel file
        wheel_files = list(self.dist_dir.glob("*.whl"))
        if not wheel_files:
            print("❌ No wheel file found in dist/")
            return False
        
        wheel_file = wheel_files[0]
        
        try:
            # Test install in a virtual environment
            venv_dir = self.package_dir / "test_venv"
            
            # Create test venv
            subprocess.run([
                "python3", "-m", "venv", str(venv_dir)
            ], check=True, capture_output=True)
            
            # Determine pip path
            if (venv_dir / "bin" / "pip").exists():
                pip_cmd = str(venv_dir / "bin" / "pip")
                python_cmd = str(venv_dir / "bin" / "python")
            else:
                pip_cmd = str(venv_dir / "Scripts" / "pip.exe")
                python_cmd = str(venv_dir / "Scripts" / "python.exe")
            
            # Install package
            subprocess.run([
                pip_cmd, "install", str(wheel_file)
            ], check=True, capture_output=True)
            
            # Test import
            result = subprocess.run([
                python_cmd, "-c", "import pasvg; print('✅ Package import successful')"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Package installation test passed")
                success = True
            else:
                print("❌ Package installation test failed:")
                print(result.stderr)
                success = False
            
            # Clean up test venv
            shutil.rmtree(venv_dir, ignore_errors=True)
            
            return success
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation test failed: {e}")
            return False
    
    def test_cli(self) -> bool:
        """Test CLI functionality."""
        print("🖥️  Testing CLI functionality...")
        
        example_files = list((self.package_dir / "examples").glob("*.pasvg.svg"))
        if not example_files:
            print("⚠️  No example PASVG files found, skipping CLI test")
            return True
        
        example_file = example_files[0]
        
        try:
            # Test CLI commands
            commands = [
                ["python3", "-m", "pasvg.cli", "--help"],
                ["python3", "-m", "pasvg.cli", "validate", str(example_file)],
                ["python3", "-m", "pasvg.cli", "info", str(example_file)]
            ]
            
            for cmd in commands:
                result = subprocess.run(
                    cmd, cwd=self.package_dir, capture_output=True, text=True, timeout=30
                )
                if result.returncode != 0:
                    print(f"❌ CLI test failed: {' '.join(cmd)}")
                    print(result.stderr)
                    return False
                else:
                    print(f"✅ CLI command passed: {cmd[-1] if len(cmd) > 3 else 'help'}")
            
            print("✅ CLI tests passed")
            return True
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"❌ CLI test failed: {e}")
            return False
    
    def publish_to_pypi(self, test_pypi: bool = True) -> bool:
        """Publish package to PyPI."""
        if test_pypi:
            print("🚀 Publishing to Test PyPI...")
            repository_url = "https://test.pypi.org/legacy/"
        else:
            print("🚀 Publishing to PyPI...")
            repository_url = "https://upload.pypi.org/legacy/"
        
        if not self.dist_dir.exists():
            print("❌ No dist directory found. Run build first.")
            return False
        
        try:
            result = subprocess.run([
                "python3", "-m", "twine", "upload",
                "--repository-url", repository_url,
                str(self.dist_dir / "*")
            ], cwd=self.package_dir)
            
            return result.returncode == 0
            
        except FileNotFoundError:
            print("❌ twine not found. Install with: pip install twine")
            return False
    
    def full_workflow(self, skip_tests: bool = False, test_pypi: bool = True) -> bool:
        """Run the complete build and test workflow."""
        print("🚀 Starting PASVG package publishing workflow...")
        print("=" * 60)
        
        steps = [
            ("Clean", self.clean),
            ("Lint", self.lint),
        ]
        
        if not skip_tests:
            steps.append(("Test", self.test))
        
        steps.extend([
            ("Build", self.build),
            ("Test Install", self.test_install),
            ("Test CLI", self.test_cli)
        ])
        
        for step_name, step_func in steps:
            print(f"\n📋 Step: {step_name}")
            print("-" * 30)
            
            if not step_func():
                print(f"❌ Workflow failed at step: {step_name}")
                return False
        
        print("\n🎉 All steps completed successfully!")
        print("=" * 60)
        print("📦 Package is ready for publishing!")
        
        if test_pypi:
            print("📝 To publish to Test PyPI:")
            print("   python3 scripts/publish.py --publish-test")
            print("📝 To publish to PyPI:")
            print("   python3 scripts/publish.py --publish")
        
        return True


def main():
    parser = argparse.ArgumentParser(description="PASVG Package Publishing Tool")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--lint", action="store_true", help="Run linting")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--build", action="store_true", help="Build package")
    parser.add_argument("--test-install", action="store_true", help="Test installation")
    parser.add_argument("--test-cli", action="store_true", help="Test CLI")
    parser.add_argument("--publish-test", action="store_true", help="Publish to Test PyPI")
    parser.add_argument("--publish", action="store_true", help="Publish to PyPI")
    parser.add_argument("--full", action="store_true", help="Run full workflow")
    parser.add_argument("--skip-tests", action="store_true", help="Skip tests in full workflow")
    
    args = parser.parse_args()
    
    # Get package directory (parent of scripts directory)
    package_dir = Path(__file__).parent.parent
    publisher = PASVGPublisher(package_dir)
    
    success = True
    
    if args.clean:
        success &= publisher.clean()
    elif args.lint:
        success &= publisher.lint()
    elif args.test:
        success &= publisher.test()
    elif args.build:
        success &= publisher.build()
    elif args.test_install:
        success &= publisher.test_install()
    elif args.test_cli:
        success &= publisher.test_cli()
    elif args.publish_test:
        success &= publisher.publish_to_pypi(test_pypi=True)
    elif args.publish:
        success &= publisher.publish_to_pypi(test_pypi=False)
    elif args.full:
        success &= publisher.full_workflow(skip_tests=args.skip_tests)
    else:
        # Default: run full workflow
        success &= publisher.full_workflow()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
