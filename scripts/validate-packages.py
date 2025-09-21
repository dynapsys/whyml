#!/usr/bin/env python3
"""
WhyML Modular Packages Validation Script

This script validates all modular packages for PyPI publishing readiness.
It checks package structure, dependencies, metadata, and build configuration.
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import toml


class PackageValidator:
    """Validates WhyML modular packages for publishing readiness."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.packages = [
            'whyml-core',
            'whyml-scrapers', 
            'whyml-converters',
            'whyml-cli',
            'whyml'
        ]
        self.validation_results = {}
        
    def validate_all_packages(self) -> Dict[str, Dict]:
        """Validate all packages and return results."""
        print("🔍 Validating WhyML Modular Packages for PyPI Publishing...")
        print("=" * 60)
        
        for package in self.packages:
            print(f"\n📦 Validating {package}...")
            package_path = self.project_root / package
            
            if not package_path.exists():
                print(f"❌ Package directory not found: {package_path}")
                self.validation_results[package] = {
                    'valid': False,
                    'errors': [f"Package directory not found: {package_path}"]
                }
                continue
                
            result = self.validate_package(package_path)
            self.validation_results[package] = result
            
            if result['valid']:
                print(f"✅ {package} is ready for publishing!")
            else:
                print(f"❌ {package} has validation issues:")
                for error in result['errors']:
                    print(f"   • {error}")
                    
        return self.validation_results
        
    def validate_package(self, package_path: Path) -> Dict:
        """Validate a single package."""
        errors = []
        warnings = []
        
        # Check required files
        required_files = ['pyproject.toml', 'README.md', 'LICENSE']
        for file in required_files:
            if not (package_path / file).exists():
                errors.append(f"Missing required file: {file}")
                
        # Validate pyproject.toml
        pyproject_path = package_path / 'pyproject.toml'
        if pyproject_path.exists():
            pyproject_errors = self.validate_pyproject_toml(pyproject_path)
            errors.extend(pyproject_errors)
        else:
            errors.append("Missing pyproject.toml")
            
        # Check package structure
        package_name = package_path.name.replace('-', '_')
        package_dir = package_path / package_name
        
        if not package_dir.exists():
            errors.append(f"Package directory not found: {package_name}/")
        else:
            if not (package_dir / '__init__.py').exists():
                errors.append(f"Missing __init__.py in {package_name}/")
                
        # Check tests directory
        tests_dir = package_path / 'tests'
        if not tests_dir.exists():
            warnings.append("No tests directory found")
        elif not any(tests_dir.glob('test_*.py')):
            warnings.append("No test files found in tests directory")
            
        # Validate build configuration
        try:
            build_errors = self.validate_build_config(package_path)
            errors.extend(build_errors)
        except Exception as e:
            errors.append(f"Build validation failed: {str(e)}")
            
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
        
    def validate_pyproject_toml(self, pyproject_path: Path) -> List[str]:
        """Validate pyproject.toml configuration."""
        errors = []
        
        try:
            config = toml.load(pyproject_path)
        except Exception as e:
            return [f"Invalid pyproject.toml: {str(e)}"]
            
        # Check build system
        if 'build-system' not in config:
            errors.append("Missing [build-system] section")
        else:
            build_system = config['build-system']
            if 'requires' not in build_system:
                errors.append("Missing build-system.requires")
            if 'build-backend' not in build_system:
                errors.append("Missing build-system.build-backend")
                
        # Check project metadata
        if 'project' not in config:
            errors.append("Missing [project] section")
        else:
            project = config['project']
            required_fields = ['name', 'version', 'description', 'authors']
            
            for field in required_fields:
                if field not in project:
                    errors.append(f"Missing project.{field}")
                    
            # Validate dependencies
            if 'dependencies' in project:
                deps = project['dependencies']
                if not isinstance(deps, list):
                    errors.append("project.dependencies must be a list")
                    
            # Check classifiers
            if 'classifiers' in project:
                classifiers = project['classifiers']
                if not isinstance(classifiers, list):
                    errors.append("project.classifiers must be a list")
                    
        # Check setuptools configuration
        if 'tool' in config and 'setuptools' in config['tool']:
            setuptools_config = config['tool']['setuptools']
            if 'packages' in setuptools_config:
                packages = setuptools_config['packages']
                if 'find' not in packages:
                    errors.append("Missing tool.setuptools.packages.find configuration")
                    
        return errors
        
    def validate_build_config(self, package_path: Path) -> List[str]:
        """Validate that the package can be built."""
        errors = []
        
        # Try to validate the build configuration without actually building
        # This is a lightweight check
        try:
            import build
            
            # Check if build requirements can be resolved
            pyproject_path = package_path / 'pyproject.toml'
            if pyproject_path.exists():
                config = toml.load(pyproject_path)
                if 'build-system' in config:
                    build_requires = config['build-system'].get('requires', [])
                    for req in build_requires:
                        if not isinstance(req, str):
                            errors.append(f"Invalid build requirement: {req}")
                            
        except ImportError:
            # Build package not available, skip this validation
            pass
        except Exception as e:
            errors.append(f"Build configuration error: {str(e)}")
            
        return errors
        
    def check_dependencies(self) -> Dict[str, List[str]]:
        """Check inter-package dependencies."""
        dependency_issues = {}
        
        for package in self.packages:
            package_path = self.project_root / package
            pyproject_path = package_path / 'pyproject.toml'
            
            if not pyproject_path.exists():
                continue
                
            try:
                config = toml.load(pyproject_path)
                project = config.get('project', {})
                dependencies = project.get('dependencies', [])
                
                issues = []
                for dep in dependencies:
                    if dep.startswith('whyml-'):
                        # Check if the dependency package exists
                        dep_name = dep.split('>=')[0].split('==')[0].split('<')[0]
                        dep_path = self.project_root / dep_name
                        if not dep_path.exists():
                            issues.append(f"Dependency {dep_name} not found")
                            
                if issues:
                    dependency_issues[package] = issues
                    
            except Exception as e:
                dependency_issues[package] = [f"Error checking dependencies: {str(e)}"]
                
        return dependency_issues
        
    def generate_report(self) -> str:
        """Generate a comprehensive validation report."""
        report = []
        report.append("# WhyML Modular Packages Validation Report")
        report.append("=" * 50)
        report.append("")
        
        # Summary
        total_packages = len(self.packages)
        valid_packages = sum(1 for result in self.validation_results.values() if result['valid'])
        
        report.append(f"## Summary")
        report.append(f"- **Total Packages**: {total_packages}")
        report.append(f"- **Valid Packages**: {valid_packages}")
        report.append(f"- **Invalid Packages**: {total_packages - valid_packages}")
        report.append("")
        
        # Package details
        report.append("## Package Validation Details")
        report.append("")
        
        for package, result in self.validation_results.items():
            status = "✅ VALID" if result['valid'] else "❌ INVALID"
            report.append(f"### {package} - {status}")
            
            if result['errors']:
                report.append("**Errors:**")
                for error in result['errors']:
                    report.append(f"- {error}")
                    
            if result.get('warnings'):
                report.append("**Warnings:**")
                for warning in result['warnings']:
                    report.append(f"- {warning}")
                    
            report.append("")
            
        # Dependency check
        dependency_issues = self.check_dependencies()
        if dependency_issues:
            report.append("## Dependency Issues")
            report.append("")
            for package, issues in dependency_issues.items():
                report.append(f"### {package}")
                for issue in issues:
                    report.append(f"- {issue}")
                report.append("")
                
        # Recommendations
        report.append("## Publishing Readiness")
        report.append("")
        
        if valid_packages == total_packages:
            report.append("🎉 **All packages are ready for PyPI publishing!**")
            report.append("")
            report.append("### Next Steps:")
            report.append("1. Run the GitHub Actions workflow to build and test all packages")
            report.append("2. Publish to Test PyPI for final validation")
            report.append("3. Publish to production PyPI")
            report.append("4. Create GitHub release with all package versions")
        else:
            report.append("⚠️ **Some packages need fixes before publishing:**")
            report.append("")
            invalid_packages = [pkg for pkg, result in self.validation_results.items() if not result['valid']]
            for pkg in invalid_packages:
                report.append(f"- Fix issues in **{pkg}**")
            report.append("")
            report.append("Run this validation script again after fixing the issues.")
            
        return "\n".join(report)


def main():
    """Main validation function."""
    project_root = Path(__file__).parent.parent
    validator = PackageValidator(project_root)
    
    # Run validation
    results = validator.validate_all_packages()
    
    # Generate and save report
    report = validator.generate_report()
    
    print("\n" + "=" * 60)
    print("📋 VALIDATION REPORT")
    print("=" * 60)
    print(report)
    
    # Save report to file
    report_file = project_root / 'package-validation-report.md'
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\n📄 Full report saved to: {report_file}")
    
    # Exit with appropriate code
    all_valid = all(result['valid'] for result in results.values())
    sys.exit(0 if all_valid else 1)


if __name__ == '__main__':
    main()
