"""
WhyML Core Manifest Processor - Main processing orchestrator

Coordinates template processing, inheritance resolution, and variable substitution
to provide a unified interface for manifest processing operations.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, Optional, List
from pathlib import Path

from .template_processor import TemplateProcessor
from .inheritance_resolver import InheritanceResolver
from .variable_substitution import VariableSubstitution
from ..exceptions import ProcessingError, ValidationError
from ..validation.manifest_validator import ManifestValidator


class ManifestProcessor:
    """Main manifest processor coordinating all processing operations."""
    
    def __init__(self, 
                 enable_validation: bool = True,
                 enable_inheritance: bool = True,
                 enable_variables: bool = True,
                 strict_validation: Optional[bool] = None,
                 requested_sections: Optional[List[str]] = None):
        """Initialize manifest processor.
        
        Args:
            enable_validation: Whether to validate manifests during processing
            enable_inheritance: Whether to process template inheritance
            enable_variables: Whether to process variable substitution
            strict_validation: Alternative parameter name for enable_validation (for backward compatibility)
            requested_sections: Optional list of specific sections to process
        """
        # Handle backward compatibility for strict_validation parameter
        if strict_validation is not None:
            self.enable_validation = strict_validation
        else:
            self.enable_validation = enable_validation
            
        self.enable_inheritance = enable_inheritance
        self.enable_variables = enable_variables
        self.requested_sections = requested_sections
        
        # Initialize processing components
        self.template_processor = TemplateProcessor()
        self.inheritance_resolver = InheritanceResolver()
        self.variable_substitution = VariableSubstitution()
        
        if enable_validation:
            self.validator = ManifestValidator()
    
    def process_manifest(self, 
                        manifest_data: Dict[str, Any], 
                        base_path: Optional[Path] = None,
                        variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a manifest with all enabled features.
        
        Args:
            manifest_data: Raw manifest data to process
            base_path: Base path for resolving relative includes
            variables: Additional variables for substitution
            
        Returns:
            Processed manifest data
            
        Raises:
            ProcessingError: If processing fails
            ValidationError: If validation fails
        """
        try:
            processed_data = manifest_data.copy()
            
            # Step 1: Validate input if enabled
            if self.enable_validation:
                validation_result = self.validator.validate_manifest(processed_data)
                if not validation_result.is_valid:
                    raise ValidationError(
                        f"Manifest validation failed: {validation_result.errors}",
                        details={'errors': validation_result.errors}
                    )
            
            # Step 2: Resolve inheritance if enabled
            if self.enable_inheritance and 'extends' in processed_data:
                processed_data = self.inheritance_resolver.resolve_inheritance(
                    processed_data, 
                    base_path=base_path
                )
            
            # Step 3: Process templates if enabled
            if self.enable_variables:
                # Merge provided variables with manifest variables
                all_variables = {}
                if 'template_vars' in processed_data:
                    all_variables.update(processed_data['template_vars'])
                if variables:
                    all_variables.update(variables)
                
                # Apply variable substitution
                processed_data = self.variable_substitution.substitute_variables(
                    processed_data,
                    variables=all_variables
                )
                
                # Process Jinja2 templates
                processed_data = self.template_processor.process_templates(
                    processed_data,
                    variables=all_variables
                )
            
            # Step 4: Final validation if enabled
            if self.enable_validation:
                final_validation = self.validator.validate_manifest(processed_data)
                if not final_validation.is_valid:
                    raise ValidationError(
                        f"Final manifest validation failed: {final_validation.errors}",
                        details={'errors': final_validation.errors}
                    )
            
            return processed_data
            
        except Exception as e:
            if isinstance(e, (ProcessingError, ValidationError)):
                raise
            raise ProcessingError(
                f"Manifest processing failed: {str(e)}",
                details={'error': str(e), 'manifest_keys': list(manifest_data.keys())}
            )
    
    def process_template_string(self, 
                               template_string: str, 
                               variables: Dict[str, Any]) -> str:
        """Process a template string with variables.
        
        Args:
            template_string: Template string to process
            variables: Variables for substitution
            
        Returns:
            Processed string
        """
        return self.template_processor.render_template_string(
            template_string, 
            variables
        )
    
    def validate_manifest(self, manifest_data: Dict[str, Any]) -> bool:
        """Validate a manifest.
        
        Args:
            manifest_data: Manifest data to validate
            
        Returns:
            True if valid, raises ValidationError if invalid
            
        Raises:
            ValidationError: If validation fails
        """
        if not self.enable_validation:
            return True
            
        validation_result = self.validator.validate_manifest(manifest_data)
        if not validation_result.is_valid:
            raise ValidationError(
                f"Manifest validation failed: {validation_result.errors}",
                details={'errors': validation_result.errors}
            )
        return True
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        return {
            'validation_enabled': self.enable_validation,
            'inheritance_enabled': self.enable_inheritance,
            'variables_enabled': self.enable_variables,
            'template_processor_stats': self.template_processor.get_stats() if hasattr(self.template_processor, 'get_stats') else {},
            'inheritance_resolver_stats': self.inheritance_resolver.get_stats() if hasattr(self.inheritance_resolver, 'get_stats') else {},
            'variable_substitution_stats': self.variable_substitution.get_stats() if hasattr(self.variable_substitution, 'get_stats') else {}
        }


# Convenience function for direct processing
def process_manifest(manifest_data: Dict[str, Any], 
                    base_path: Optional[Path] = None,
                    variables: Optional[Dict[str, Any]] = None,
                    **kwargs) -> Dict[str, Any]:
    """Convenience function to process a manifest with default settings.
    
    Args:
        manifest_data: Raw manifest data to process
        base_path: Base path for resolving relative includes
        variables: Additional variables for substitution
        **kwargs: Additional arguments for ManifestProcessor
        
    Returns:
        Processed manifest data
    """
    processor = ManifestProcessor(**kwargs)
    return processor.process_manifest(manifest_data, base_path, variables)
