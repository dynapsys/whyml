"""
Manifest Processor - Core processing engine for YAML manifests

Handles validation, template inheritance, style processing, and structure
transformation with comprehensive schema validation and error reporting.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
import copy
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import yaml
import json
from datetime import datetime
from jinja2 import Template, Environment, BaseLoader, TemplateError
from jsonschema import validate, ValidationError as JsonSchemaError
import logging

from .exceptions import (
    ValidationError,
    TemplateError,
    ManifestError,
    SchemaError,
    handle_validation_errors
)
from .manifest_loader import ManifestLoader, LoadedManifest

logger = logging.getLogger(__name__)


class ManifestValidator:
    """Validates manifest structure and content against schema."""
    
    def __init__(self, schema_path: Optional[Path] = None, requested_sections: Optional[List[str]] = None):
        """Initialize validator with optional custom schema and requested sections."""
        self.requested_sections = requested_sections or []
        self.schema = self._load_schema(schema_path)
    
    def _load_schema(self, schema_path: Optional[Path]) -> Dict[str, Any]:
        """Load the manifest validation schema."""
        if schema_path and schema_path.exists():
            with open(schema_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default schema with dynamic requirements based on requested sections
        schema = {
            "type": "object",
            "properties": {
                "metadata": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "version": {"type": "string"},
                        "extends": {"type": "string"},
                        "template_type": {"type": "string"},
                        "extracted_at": {"type": "string"}
                    },
                    "required": ["title"]
                },
                "analysis": {
                    "type": "object",
                    "properties": {
                        "page_type": {"type": "string"},
                        "seo_analysis": {"type": "object"},
                        "accessibility_analysis": {"type": "object"},
                        "content_stats": {"type": "object"},
                        "structure_complexity": {"type": "object"}
                    }
                },
                "styles": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z_][a-zA-Z0-9_-]*$": {"type": "string"}
                    }
                },
                "structure": {
                    "type": "object"
                },
                "imports": {
                    "type": "object",
                    "properties": {
                        "manifests": {"type": "array", "items": {"type": "string"}},
                        "modules": {"type": "array", "items": {"type": "string"}},
                        "templates": {"type": "array", "items": {"type": "string"}},
                        "scripts": {"type": "array", "items": {"type": "string"}},
                        "styles": {"type": "array", "items": {"type": "string"}},
                        "fonts": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "interactions": {
                    "type": "object"
                },
                "template_slots": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z_][a-zA-Z0-9_-]*$": {"type": "string"}
                    }
                }
            }
        }
        
        # Dynamic required sections based on what was requested
        if self.requested_sections:
            # If specific sections are requested, only require those sections
            schema["required"] = []
            for section in self.requested_sections:
                if section in schema["properties"]:
                    schema["required"].append(section)
        else:
            # If no specific sections requested, use traditional requirement
            schema["required"] = ["metadata"]
        
        return schema
    
    def validate(self, manifest: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """
        Validate manifest against schema.
        
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        # Schema validation
        try:
            validate(instance=manifest, schema=self.schema)
        except JsonSchemaError as e:
            errors.append(f"Schema validation failed: {e.message}")
        
        # Custom validation rules
        self._validate_metadata(manifest, errors, warnings)
        self._validate_styles(manifest, errors, warnings)
        self._validate_structure(manifest, errors, warnings)
        self._validate_template_inheritance(manifest, errors, warnings)
        
        return errors, warnings
    
    def _validate_metadata(self, manifest: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate metadata section if present or required."""
        metadata = manifest.get('metadata', {})
        
        # Only validate metadata if it's present or explicitly requested
        if not metadata and self.requested_sections and 'metadata' not in self.requested_sections:
            return
        
        if metadata and not metadata.get('title'):
            errors.append("Metadata must include a title")
        
        if metadata and not metadata.get('description'):
            warnings.append("Consider adding a description to metadata")
        
        # Validate template inheritance
        if metadata and 'extends' in metadata:
            extends = metadata['extends']
            if not isinstance(extends, str) or not extends.strip():
                errors.append("Template 'extends' must be a non-empty string")
    
    def _validate_styles(self, manifest: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate styles section."""
        styles = manifest.get('styles', {})
        
        if not isinstance(styles, dict):
            errors.append("Styles must be an object/dictionary")
            return
        
        css_property_pattern = re.compile(r'^[a-zA-Z-]+\s*:\s*.+$')
        
        for style_name, style_value in styles.items():
            if not isinstance(style_value, str):
                errors.append(f"Style '{style_name}' must be a string")
                continue
            
            # Basic CSS validation
            if ';' in style_value:
                # Multiple properties
                properties = style_value.split(';')
                for prop in properties:
                    prop = prop.strip()
                    if prop and not css_property_pattern.match(prop):
                        warnings.append(f"Style '{style_name}' may have invalid CSS: '{prop}'")
            else:
                # Single property
                if style_value.strip() and not css_property_pattern.match(style_value.strip()):
                    warnings.append(f"Style '{style_name}' may have invalid CSS: '{style_value}'")
    
    def _validate_structure(self, manifest: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate structure section if present."""
        structure = manifest.get('structure')
        
        if not structure:
            # Structure is now optional - only validate if present
            return
        
        def validate_element(element, path="structure"):
            if isinstance(element, dict):
                # Check for required HTML element structure
                for key, value in element.items():
                    if key in ['children', 'text', 'style', 'class', 'id']:
                        continue
                    
                    # This should be an HTML element
                    if not re.match(r'^[a-zA-Z][a-zA-Z0-9-]*$', key):
                        warnings.append(f"Unusual element name at {path}.{key}: '{key}'")
                    
                    if isinstance(value, dict):
                        validate_element(value, f"{path}.{key}")
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            validate_element(item, f"{path}.{key}[{i}]")
            
            elif isinstance(element, list):
                for i, item in enumerate(element):
                    validate_element(item, f"{path}[{i}]")
        
        validate_element(structure)
    
    def _validate_template_inheritance(self, manifest: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate template inheritance configuration."""
        metadata = manifest.get('metadata', {})
        template_slots = manifest.get('template_slots', {})
        
        if 'extends' in metadata and template_slots:
            warnings.append("Template inheritance and template_slots both present - ensure compatibility")
        
        # Validate slot names
        for slot_name in template_slots.keys():
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', slot_name):
                errors.append(f"Invalid template slot name: '{slot_name}'")


class TemplateProcessor:
    """Processes template inheritance and variable substitution."""
    
    def __init__(self):
        """Initialize template processor with Jinja2 environment."""
        self.env = Environment(loader=BaseLoader())
        self.env.globals.update({
            'range': range,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool
        })
    
    def substitute_template_variables(self, 
                                    content: str, 
                                    variables: Dict[str, Any], 
                                    config: Optional[Dict[str, Any]] = None) -> str:
        """
        Substitute template variables in content using both {{VAR}} and <?=VAR?> syntax.
        
        Args:
            content: Content string containing template variables
            variables: Dictionary of variables to substitute
            config: Optional configuration for substitution behavior
            
        Returns:
            Content with variables substituted
        """
        if not content or not variables:
            return content
            
        # Prepare context with variables and config
        context = {}
        context.update(variables)
        if config:
            context.update(config)
        
        try:
            # Handle {{VAR}} syntax (Jinja2 style)
            jinja_template = self.env.from_string(content)
            content = jinja_template.render(**context)
            
            # Handle <?=VAR?> syntax (PHP-like)
            php_pattern = re.compile(r'<\?=([^?]+)\?>')
            
            def php_replacer(match):
                var_expr = match.group(1).strip()
                try:
                    # Simple variable lookup
                    if var_expr in context:
                        return str(context[var_expr])
                    
                    # Handle dot notation like VAR.property
                    if '.' in var_expr:
                        parts = var_expr.split('.')
                        value = context
                        for part in parts:
                            if isinstance(value, dict) and part in value:
                                value = value[part]
                            else:
                                return match.group(0)  # Return original if not found
                        return str(value)
                    
                    # Return original if variable not found
                    return match.group(0)
                except Exception:
                    return match.group(0)  # Return original on error
            
            content = php_pattern.sub(php_replacer, content)
            
            return content
            
        except TemplateError as e:
            logger.warning(f"Template substitution error: {e}")
            return content  # Return original content on error
        except Exception as e:
            logger.warning(f"Variable substitution error: {e}")
            return content
    
    def process_template_inheritance(self, 
                                   child_manifest: Dict[str, Any],
                                   parent_manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process template inheritance by merging parent and child manifests.
        
        Args:
            child_manifest: Child manifest that extends parent
            parent_manifest: Parent manifest being extended
            
        Returns:
            Merged manifest with inheritance applied
        """
        result = copy.deepcopy(parent_manifest)
        
        # Merge metadata (child overrides parent)
        if 'metadata' in child_manifest:
            result.setdefault('metadata', {}).update(child_manifest['metadata'])
        
        # Merge styles (child overrides parent)
        if 'styles' in child_manifest:
            result.setdefault('styles', {}).update(child_manifest['styles'])
        
        # Process template slots
        self._process_template_slots(result, child_manifest)
        
        # Merge other sections
        for section in ['imports', 'interactions']:
            if section in child_manifest:
                result.setdefault(section, {}).update(child_manifest[section])
        
        # Structure inheritance is more complex
        result['structure'] = self._merge_structures(
            result.get('structure', {}),
            child_manifest.get('structure', {})
        )
        
        return result
    
    def _process_template_slots(self, parent: Dict[str, Any], child: Dict[str, Any]):
        """Process template slots for content injection."""
        parent_slots = parent.get('template_slots', {})
        child_structure = child.get('structure', {})
        
        if not parent_slots:
            return
        
        def replace_slots(element):
            if isinstance(element, dict):
                # Check if this element references a slot
                if 'slot' in element:
                    slot_name = element['slot']
                    if slot_name in child_structure:
                        return child_structure[slot_name]
                
                # Recursively process children
                result = {}
                for key, value in element.items():
                    if key == 'children' and isinstance(value, list):
                        result[key] = [replace_slots(child) for child in value]
                    elif isinstance(value, (dict, list)):
                        result[key] = replace_slots(value)
                    else:
                        result[key] = value
                return result
            
            elif isinstance(element, list):
                return [replace_slots(item) for item in element]
            
            return element
        
        parent['structure'] = replace_slots(parent['structure'])
    
    def _merge_structures(self, parent: Dict[str, Any], child: Dict[str, Any]) -> Dict[str, Any]:
        """Merge structure sections with child taking precedence."""
        if not parent:
            return child
        if not child:
            return parent
        
        # If child completely overrides structure, use child
        if child.get('_override', False):
            return child
        
        # Otherwise, merge recursively
        result = copy.deepcopy(parent)
        
        def merge_element(parent_elem, child_elem):
            if isinstance(child_elem, dict) and isinstance(parent_elem, dict):
                merged = parent_elem.copy()
                for key, value in child_elem.items():
                    if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                        merged[key] = merge_element(merged[key], value)
                    else:
                        merged[key] = value
                return merged
            else:
                return child_elem
        
        return merge_element(result, child)
    
    def substitute_variables(self, manifest: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Substitute template variables in manifest content.
        
        Args:
            manifest: Manifest with template variables
            context: Context variables for substitution
            
        Returns:
            Manifest with variables substituted
        """
        context = context or {}
        
        # Add manifest metadata to context
        context.update({
            'metadata': manifest.get('metadata', {}),
            'manifest': manifest
        })
        
        def substitute_in_value(value):
            if isinstance(value, str):
                if '{{' in value and '}}' in value:
                    try:
                        template = self.env.from_string(value)
                        return template.render(**context)
                    except TemplateError as e:
                        raise TemplateError(f"Template substitution failed: {e}")
                return value
            elif isinstance(value, dict):
                return {k: substitute_in_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_in_value(item) for item in value]
            else:
                return value
        
        return substitute_in_value(manifest)


class StyleProcessor:
    """Processes and optimizes CSS styles."""
    
    def __init__(self):
        """Initialize style processor."""
        self.css_minify = True
    
    def process_styles(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process styles section with optimization and validation.
        
        Args:
            manifest: Manifest with styles section
            
        Returns:
            Manifest with processed styles
        """
        styles = manifest.get('styles', {})
        if not styles:
            return manifest
        
        processed_styles = {}
        
        for name, css in styles.items():
            processed_styles[name] = self._process_single_style(css)
        
        result = copy.deepcopy(manifest)
        result['styles'] = processed_styles
        return result
    
    def _process_single_style(self, css: str) -> str:
        """Process a single CSS style."""
        # Basic CSS cleanup
        css = css.strip()
        
        # Remove extra whitespace
        css = re.sub(r'\s+', ' ', css)
        
        # Ensure proper semicolons
        if css and not css.endswith(';'):
            css += ';'
        
        # Basic validation patterns
        self._validate_css_properties(css)
        
        return css
    
    def _validate_css_properties(self, css: str):
        """Validate CSS properties (basic check)."""
        # This is a basic implementation - could be enhanced with a full CSS parser
        properties = css.split(';')
        for prop in properties:
            prop = prop.strip()
            if prop and ':' not in prop:
                logger.warning(f"Potentially invalid CSS property: {prop}")


class ManifestProcessor:
    """
    Main processor for YAML manifests with validation, inheritance, and transformation.
    
    Integrates all processing components to provide a complete manifest processing pipeline.
    """
    
    def __init__(self, 
                 manifest_loader: Optional[ManifestLoader] = None,
                 schema_path: Optional[Path] = None,
                 strict_validation: bool = False,
                 requested_sections: Optional[List[str]] = None):
        """
        Initialize manifest processor.
        
        Args:
            manifest_loader: Loader for resolving dependencies
            schema_path: Path to custom validation schema
            strict_validation: Whether to treat warnings as errors
            requested_sections: List of sections requested for selective validation
        """
        self.loader = manifest_loader or ManifestLoader()
        self.validator = ManifestValidator(schema_path, requested_sections)
        self.template_processor = TemplateProcessor()
        self.style_processor = StyleProcessor()
        self.strict_validation = strict_validation
        self.requested_sections = requested_sections or []
    
    def process_manifest(self, 
                        manifest: Union[str, Dict[str, Any], LoadedManifest],
                        context: Dict[str, Any] = None,
                        validate: bool = True) -> Dict[str, Any]:
        """
        Process a manifest through the complete pipeline.
        
        Args:
            manifest: Manifest URL, dict, or LoadedManifest
            context: Context variables for template substitution
            validate: Whether to perform validation
            
        Returns:
            Fully processed manifest
        """
        # Load manifest if needed
        if isinstance(manifest, str):
            # For synchronous operation, we'll need to run the async load in an event loop
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If already in an async context, raise an error suggesting async usage
                    raise RuntimeError("Cannot load manifest from URL in sync context when event loop is running. Use WhyMLProcessor.process_manifest_async() instead.")
                else:
                    loaded_manifest = loop.run_until_complete(self.loader.load_manifest(manifest))
            except RuntimeError:
                # No event loop, create one
                loaded_manifest = asyncio.run(self.loader.load_manifest(manifest))
            manifest_data = loaded_manifest.content
        elif isinstance(manifest, LoadedManifest):
            manifest_data = manifest.content
        else:
            manifest_data = manifest
        
        # Validate before processing
        if validate:
            self._validate_manifest(manifest_data)
        
        # Process template inheritance
        processed_manifest = self._process_inheritance(manifest_data)
        
        # Process template variables and config
        variables = manifest_data.get('variables', {})
        config = manifest_data.get('config', {})
        
        # Merge context with manifest variables
        if context:
            variables.update(context)
        
        # Apply variable substitution if variables are present
        if variables or config:
            processed_manifest = self._apply_variable_substitution(
                processed_manifest, variables, config
            )
        
        # Process styles
        processed_manifest = self.style_processor.process_styles(processed_manifest)
        
        # Final validation
        if validate:
            self._validate_manifest(processed_manifest)
        
        return processed_manifest
    
    def merge_manifests(self, base: Dict[str, Any], child: Dict[str, Any]) -> Dict[str, Any]:
        """Merge child manifest with base manifest."""
        merged = copy.deepcopy(base)
        
        # Merge metadata (child overrides base)
        if 'metadata' in child:
            if 'metadata' not in merged:
                merged['metadata'] = {}
            merged['metadata'].update(child['metadata'])
        
        # Merge template_vars (child overrides base)
        if 'template_vars' in child:
            if 'template_vars' not in merged:
                merged['template_vars'] = {}
            merged['template_vars'].update(child['template_vars'])
        
        # Merge styles (child overrides base)
        if 'styles' in child:
            if 'styles' not in merged:
                merged['styles'] = {}
            merged['styles'].update(child['styles'])
        
        # Child structure overrides base structure
        if 'structure' in child:
            merged['structure'] = child['structure']
        
        # Merge other sections
        for key, value in child.items():
            if key not in ['metadata', 'template_vars', 'styles', 'structure']:
                merged[key] = value
        
        return merged
    
    def optimize_styles(self, styles: Dict[str, str]) -> Dict[str, str]:
        """Optimize CSS styles by removing duplicates and normalizing."""
        optimized = {}
        
        for name, css in styles.items():
            # Normalize CSS
            normalized = self._normalize_css(css)
            optimized[name] = normalized
        
        return optimized
    
    def _normalize_css(self, css: str) -> str:
        """Normalize CSS by removing extra whitespace and organizing properties."""
        # Remove extra whitespace
        css = ' '.join(css.split())
        
        # Split into properties
        properties = []
        for prop in css.split(';'):
            prop = prop.strip()
            if prop:
                # Remove duplicate properties (keep last one)
                prop_name = prop.split(':')[0].strip()
                # Remove existing property with same name
                properties = [p for p in properties if not p.strip().startswith(prop_name + ':')]
                properties.append(prop)
        
        return '; '.join(properties)
    
    def validate_structure(self, structure: Dict[str, Any]) -> List[str]:
        """Validate HTML structure."""
        errors = []
        
        def validate_element(element, path="root"):
            if isinstance(element, dict):
                for tag_name, tag_content in element.items():
                    if not self._is_valid_html_tag(tag_name):
                        errors.append(f"Invalid HTML tag '{tag_name}' at {path}")
                    
                    if isinstance(tag_content, dict):
                        if 'children' in tag_content:
                            validate_element(tag_content['children'], f"{path}.{tag_name}")
                    elif isinstance(tag_content, list):
                        for i, child in enumerate(tag_content):
                            validate_element(child, f"{path}.{tag_name}[{i}]")
            elif isinstance(element, list):
                for i, item in enumerate(element):
                    validate_element(item, f"{path}[{i}]")
        
        validate_element(structure)
        return errors
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate metadata section."""
        errors = []
        
        required_fields = ['title']
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required metadata field: {field}")
        
        return errors
    
    def merge_styles(self, base_styles: Dict[str, str], child_styles: Dict[str, str], 
                    strategy: str = 'override') -> Dict[str, str]:
        """Merge styles with specified strategy."""
        if strategy == 'override':
            merged = base_styles.copy()
            merged.update(child_styles)
            return merged
        elif strategy == 'extend':
            merged = base_styles.copy()
            for name, style in child_styles.items():
                if name in merged:
                    # Extend existing style
                    merged[name] = f"{merged[name]}; {style}"
                else:
                    merged[name] = style
            return merged
        else:
            raise ValueError(f"Unknown merge strategy: {strategy}")
    
    def _is_valid_html_tag(self, tag_name: str) -> bool:
        """Check if tag name is a valid HTML element."""
        valid_tags = {
            'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'thead', 'tbody',
            'form', 'input', 'textarea', 'select', 'option', 'button', 'label',
            'a', 'img', 'video', 'audio', 'br', 'hr',
            'header', 'nav', 'main', 'section', 'article', 'aside', 'footer'
        }
        return tag_name.lower() in valid_tags
    
    def _apply_variable_substitution(self, 
                                   manifest: Dict[str, Any], 
                                   variables: Dict[str, Any], 
                                   config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply template variable substitution to manifest content.
        
        Args:
            manifest: Manifest to process
            variables: Variables for substitution
            config: Configuration for substitution
            
        Returns:
            Manifest with variables substituted
        """
        # First, process {{EXTERNAL:...}} syntax before Jinja2 template substitution
        manifest = self._process_external_syntax_in_manifest(manifest)
        
        def substitute_recursive(obj):
            if isinstance(obj, str):
                return self.template_processor.substitute_template_variables(obj, variables, config)
            elif isinstance(obj, dict):
                return {k: substitute_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [substitute_recursive(item) for item in obj]
            else:
                return obj
        
        return substitute_recursive(manifest)
    
    def _process_external_syntax_in_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process {{EXTERNAL:filename}} syntax in manifest before Jinja2 template substitution.
        
        This custom WhyML syntax allows inline insertion of external content directly
        in the manifest structure. Must be processed before Jinja2 to avoid parsing errors.
        
        Args:
            manifest: Manifest that may contain {{EXTERNAL:...}} syntax
            
        Returns:
            Manifest with {{EXTERNAL:...}} syntax replaced by actual content
        """
        import re
        from pathlib import Path
        
        # Create external content map from manifest
        external_content_map = {}
        external_content = manifest.get('external_content', {})
        
        if external_content:
            # Handle both list and dict formats for external_content
            if isinstance(external_content, list):
                content_items = enumerate(external_content)
            else:
                content_items = external_content.items()
            
            for content_key, content_config in content_items:
                if isinstance(content_config, str):
                    source = content_config
                elif isinstance(content_config, dict):
                    source = content_config.get('source', content_config.get('url', ''))
                else:
                    continue
                
                if source:
                    try:
                        # Load external content
                        content = self._load_external_file(source)
                        # Extract filename for the map key
                        filename = Path(source).name if not source.startswith('http') else source
                        external_content_map[filename] = content
                    except Exception as e:
                        logger.warning(f"Failed to load external content from {source}: {e}")
        
        def replace_external_syntax_recursive(obj):
            if isinstance(obj, str):
                return self._replace_external_syntax(obj, external_content_map)
            elif isinstance(obj, dict):
                return {k: replace_external_syntax_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_external_syntax_recursive(item) for item in obj]
            else:
                return obj
        
        return replace_external_syntax_recursive(manifest)
    
    def _replace_external_syntax(self, content: str, external_content_map: Dict[str, str]) -> str:
        """Replace {{EXTERNAL:filename}} syntax with actual content."""
        import re
        
        def replace_external(match):
            filename = match.group(1)
            if filename in external_content_map:
                return external_content_map[filename]
            else:
                # Return placeholder if external content not found
                return f'<!-- External content not found: {filename} -->'
        
        # Replace {{EXTERNAL:filename}} with actual content
        pattern = r'\{\{EXTERNAL:([^}]+)\}\}'
        return re.sub(pattern, replace_external, content)
    
    def _load_external_file(self, source: str) -> str:
        """Load content from external file or URL."""
        from pathlib import Path
        import requests
        
        if source.startswith(('http://', 'https://')):
            # Load from URL
            response = requests.get(source, timeout=10)
            response.raise_for_status()
            return response.text
        else:
            # Load from local file
            file_path = Path(source)
            if not file_path.is_absolute():
                # Make relative to current working directory or manifest location
                file_path = Path.cwd() / file_path
            
            if file_path.exists():
                return file_path.read_text(encoding='utf-8')
            else:
                raise FileNotFoundError(f"External content file not found: {file_path}")
    
    def _validate_manifest(self, manifest: Dict[str, Any]):
        """Validate manifest and raise appropriate errors."""
        errors, warnings = self.validator.validate(manifest)
        
        if self.strict_validation and warnings:
            errors.extend(warnings)
            warnings = []
        
        if errors:
            raise handle_validation_errors(errors, warnings)
        
        if warnings:
            for warning in warnings:
                logger.warning(f"Manifest validation warning: {warning}")
    
    def _process_inheritance(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Process template inheritance chain."""
        metadata = manifest.get('metadata', {})
        extends = metadata.get('extends')
        
        if not extends:
            return manifest
        
        # Load parent template
        try:
            # Handle async loading in sync context
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    raise RuntimeError("Cannot process inheritance from URL in sync context when event loop is running.")
                else:
                    parent_loaded = loop.run_until_complete(self.loader.load_manifest(extends))
            except RuntimeError:
                parent_loaded = asyncio.run(self.loader.load_manifest(extends))
            
            parent_manifest = parent_loaded.content
            
            # Recursively process parent inheritance
            parent_processed = self._process_inheritance(parent_manifest)
            
            # Apply inheritance
            return self.template_processor.process_template_inheritance(
                manifest, parent_processed
            )
        except Exception as e:
            raise TemplateError(
                f"Failed to process template inheritance",
                template_name=extends,
                details={'original_error': str(e)}
            )
    
    def create_context(self, **kwargs) -> Dict[str, Any]:
        """Create a template context with common variables."""
        return {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            **kwargs
        }
    
    def validate_only(self, manifest: Union[str, Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """
        Validate a manifest without processing.
        
        Returns:
            Tuple of (errors, warnings)
        """
        if isinstance(manifest, str):
            # Handle async loading in sync context
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    raise RuntimeError("Cannot validate manifest from URL in sync context when event loop is running.")
                else:
                    loaded_manifest = loop.run_until_complete(self.loader.load_manifest(manifest))
            except RuntimeError:
                loaded_manifest = asyncio.run(self.loader.load_manifest(manifest))
            manifest_data = loaded_manifest.content
        else:
            manifest_data = manifest
        
        return self.validator.validate(manifest_data)
    
    def expand_manifest(self, manifest: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Expand manifest with all dependencies resolved.
        
        This is similar to process_manifest but focuses on dependency resolution
        rather than template processing.
        """
        if isinstance(manifest, str):
            # Handle async loading in sync context
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    raise RuntimeError("Cannot expand manifest from URL in sync context when event loop is running.")
                else:
                    return loop.run_until_complete(self.loader.expand_manifest(manifest))
            except RuntimeError:
                return asyncio.run(self.loader.expand_manifest(manifest))
        else:
            # For dict input, return as-is since it's already loaded
            return manifest
