"""
WhyML CLI Validate Command

Manifest validation command for checking WhyML manifest integrity
using the whyml-core validation functionality.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import argparse
from pathlib import Path
from typing import List, Dict, Any

from whyml_core.exceptions import ValidationError, ProcessingError
from whyml_core.validation import ValidationResult
from .base_command import BaseCommand


class ValidateCommand(BaseCommand):
    """Command for validating WhyML manifests."""
    
    def register_parser(self, subparsers) -> argparse.ArgumentParser:
        """Register validate command parser."""
        parser = subparsers.add_parser(
            'validate',
            help='Validate WhyML manifests',
            description='Check WhyML manifest files for correctness and completeness',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  whyml-cli validate manifest.yaml
  whyml-cli validate manifest.yaml --strict
  whyml-cli validate *.yaml --summary
  whyml-cli validate manifest.yaml --fix-auto --output fixed_manifest.yaml
            """
        )
        
        # Input arguments
        parser.add_argument(
            'manifests',
            nargs='+',
            type=lambda x: self.validate_file_path(x, must_exist=True),
            help='WhyML manifest files to validate'
        )
        
        # Validation options
        parser.add_argument(
            '--strict',
            action='store_true',
            help='Enable strict validation mode'
        )
        
        parser.add_argument(
            '--schema',
            type=str,
            help='Custom schema file for validation'
        )
        
        parser.add_argument(
            '--check-inheritance',
            action='store_true',
            default=True,
            help='Validate inheritance relationships (default: true)'
        )
        
        parser.add_argument(
            '--no-check-inheritance',
            dest='check_inheritance',
            action='store_false',
            help='Skip inheritance validation'
        )
        
        parser.add_argument(
            '--check-templates',
            action='store_true',
            default=True,
            help='Validate template syntax (default: true)'
        )
        
        parser.add_argument(
            '--no-check-templates',
            dest='check_templates',
            action='store_false',
            help='Skip template validation'
        )
        
        parser.add_argument(
            '--check-variables',
            action='store_true',
            default=True,
            help='Validate variable references (default: true)'
        )
        
        parser.add_argument(
            '--no-check-variables',
            dest='check_variables',
            action='store_false',
            help='Skip variable validation'
        )
        
        # Output options
        parser.add_argument(
            '--summary',
            action='store_true',
            help='Show validation summary for multiple files'
        )
        
        parser.add_argument(
            '--json-output',
            action='store_true',
            help='Output validation results in JSON format'
        )
        
        parser.add_argument(
            '--quiet', '-q',
            action='store_true',
            help='Only show errors (quiet mode)'
        )
        
        # Auto-fix options
        parser.add_argument(
            '--fix-auto',
            action='store_true',
            help='Automatically fix common validation issues'
        )
        
        parser.add_argument(
            '--fix-output',
            type=str,
            help='Output path for fixed manifest (requires --fix-auto)'
        )
        
        return parser
    
    async def execute(self, args: argparse.Namespace) -> int:
        """Execute validate command."""
        try:
            # Validate multiple manifests
            results = []
            total_errors = 0
            
            for manifest_path in args.manifests:
                if not args.quiet:
                    self.print_info(f"Validating: {manifest_path}")
                
                try:
                    result = await self._validate_single_manifest(manifest_path, args)
                    results.append((manifest_path, result))
                    
                    if not result.is_valid:
                        total_errors += len(result.errors)
                        
                except Exception as e:
                    error_result = ValidationResult(
                        is_valid=False,
                        errors=[f"Failed to validate: {e}"],
                        warnings=[],
                        info={}
                    )
                    results.append((manifest_path, error_result))
                    total_errors += 1
            
            # Output results
            if args.json_output:
                await self._output_json_results(results)
            elif args.summary and len(results) > 1:
                await self._output_summary(results, total_errors)
            else:
                await self._output_detailed_results(results, args)
            
            # Return appropriate exit code
            return 0 if total_errors == 0 else 1
            
        except Exception as e:
            self.print_error(f"Validation failed: {e}")
            return 1
    
    async def _validate_single_manifest(self, manifest_path: Path, args: argparse.Namespace) -> ValidationResult:
        """Validate a single manifest file."""
        # Load manifest
        manifest = await self.cli.load_manifest(manifest_path)
        
        # Prepare validation options
        validation_options = {
            'strict_mode': args.strict,
            'check_inheritance': args.check_inheritance,
            'check_templates': args.check_templates,
            'check_variables': args.check_variables
        }
        
        if args.schema:
            validation_options['custom_schema_path'] = args.schema
        
        # Perform validation
        result = await self.cli.validator.validate_manifest(manifest, **validation_options)
        
        # Auto-fix if requested
        if args.fix_auto and not result.is_valid:
            fixed_manifest, fix_result = await self._auto_fix_manifest(manifest, result)
            
            # Save fixed manifest if output specified
            if args.fix_output:
                await self.cli._save_manifest(fixed_manifest, args.fix_output)
                self.print_success(f"Fixed manifest saved to {args.fix_output}")
            
            # Return updated validation result
            return fix_result
        
        return result
    
    async def _auto_fix_manifest(self, manifest: Dict[str, Any], 
                                validation_result: ValidationResult) -> tuple[Dict[str, Any], ValidationResult]:
        """Attempt to automatically fix common manifest issues."""
        fixed_manifest = manifest.copy()
        fixed_errors = []
        remaining_errors = []
        
        for error in validation_result.errors:
            try:
                # Try to fix common issues
                if "missing required field" in error.lower():
                    fixed = await self._fix_missing_field(fixed_manifest, error)
                    if fixed:
                        fixed_errors.append(f"Fixed: {error}")
                        continue
                
                elif "invalid format" in error.lower():
                    fixed = await self._fix_invalid_format(fixed_manifest, error)
                    if fixed:
                        fixed_errors.append(f"Fixed: {error}")
                        continue
                
                elif "duplicate" in error.lower():
                    fixed = await self._fix_duplicates(fixed_manifest, error)
                    if fixed:
                        fixed_errors.append(f"Fixed: {error}")
                        continue
                
                # If we can't fix it, keep it as an error
                remaining_errors.append(error)
                
            except Exception:
                # If fixing fails, keep original error
                remaining_errors.append(error)
        
        # Create new validation result
        fix_result = ValidationResult(
            is_valid=len(remaining_errors) == 0,
            errors=remaining_errors,
            warnings=validation_result.warnings + fixed_errors,
            info=validation_result.info
        )
        
        return fixed_manifest, fix_result
    
    async def _fix_missing_field(self, manifest: Dict[str, Any], error: str) -> bool:
        """Fix missing required fields."""
        # Extract field name from error message
        import re
        field_match = re.search(r"field[:\s]+['\"]([^'\"]+)['\"]", error)
        if not field_match:
            return False
        
        field_name = field_match.group(1)
        
        # Add common default values for missing fields
        defaults = {
            'metadata.title': 'Untitled',
            'metadata.description': '',
            'metadata.version': '1.0.0',
            'structure': {},
            'styles': {},
            'scripts': {}
        }
        
        if field_name in defaults:
            # Navigate to parent and set field
            path_parts = field_name.split('.')
            current = manifest
            
            # Navigate to parent
            for part in path_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set field value
            current[path_parts[-1]] = defaults[field_name]
            return True
        
        return False
    
    async def _fix_invalid_format(self, manifest: Dict[str, Any], error: str) -> bool:
        """Fix invalid format issues."""
        # This is a placeholder for format fixing logic
        # In practice, would implement specific format corrections
        return False
    
    async def _fix_duplicates(self, manifest: Dict[str, Any], error: str) -> bool:
        """Fix duplicate entries."""
        # This is a placeholder for duplicate removal logic
        # In practice, would implement duplicate detection and removal
        return False
    
    async def _output_json_results(self, results: List[tuple]) -> None:
        """Output validation results in JSON format."""
        import json
        
        json_results = []
        for manifest_path, result in results:
            json_result = {
                'file': str(manifest_path),
                'valid': result.is_valid,
                'errors': result.errors,
                'warnings': result.warnings,
                'info': result.info
            }
            json_results.append(json_result)
        
        print(json.dumps(json_results, indent=2, ensure_ascii=False))
    
    async def _output_summary(self, results: List[tuple], total_errors: int) -> None:
        """Output validation summary for multiple files."""
        valid_count = sum(1 for _, result in results if result.is_valid)
        invalid_count = len(results) - valid_count
        
        print("\n" + "="*50)
        print("VALIDATION SUMMARY")
        print("="*50)
        print(f"Total files: {len(results)}")
        print(f"Valid files: {valid_count}")
        print(f"Invalid files: {invalid_count}")
        print(f"Total errors: {total_errors}")
        
        if invalid_count > 0:
            print("\nInvalid files:")
            for manifest_path, result in results:
                if not result.is_valid:
                    print(f"  ✗ {manifest_path} ({len(result.errors)} errors)")
        
        if valid_count > 0:
            print("\nValid files:")
            for manifest_path, result in results:
                if result.is_valid:
                    print(f"  ✓ {manifest_path}")
        
        # Overall result
        if total_errors == 0:
            self.print_success("All manifests are valid!")
        else:
            self.print_error(f"Found {total_errors} validation errors")
    
    async def _output_detailed_results(self, results: List[tuple], args: argparse.Namespace) -> None:
        """Output detailed validation results."""
        for manifest_path, result in results:
            if len(results) > 1 and not args.quiet:
                print(f"\n{'='*60}")
                print(f"File: {manifest_path}")
                print('='*60)
            
            if result.is_valid:
                if not args.quiet:
                    self.print_success("Manifest is valid")
            else:
                self.print_error("Manifest validation failed")
                
                if result.errors:
                    print("\nErrors:")
                    for i, error in enumerate(result.errors, 1):
                        print(f"  {i}. {error}")
                
                if result.warnings and not args.quiet:
                    print("\nWarnings:")
                    for i, warning in enumerate(result.warnings, 1):
                        print(f"  {i}. {warning}")
                
                if result.info and not args.quiet:
                    print("\nAdditional Info:")
                    for key, value in result.info.items():
                        print(f"  {key}: {value}")
