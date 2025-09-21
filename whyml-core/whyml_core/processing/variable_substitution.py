"""
WhyML Core Variable Substitution - Advanced variable substitution and context management

Provides sophisticated variable substitution with context inheritance, 
scoped variables, and multiple substitution strategies.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
import copy
from typing import Any, Dict, List, Optional, Union, Callable
from .template_processor import TemplateProcessor
from ..exceptions import TemplateError


class VariableSubstitution:
    """Advanced variable substitution with context management and scoping."""
    
    def __init__(self, template_processor: Optional[TemplateProcessor] = None):
        """Initialize variable substitution.
        
        Args:
            template_processor: Optional template processor instance
        """
        self.template_processor = template_processor or TemplateProcessor()
        self.global_context: Dict[str, Any] = {}
        self.context_stack: List[Dict[str, Any]] = []
        self.custom_substituters: Dict[str, Callable] = {}
    
    def set_global_context(self, context: Dict[str, Any]) -> None:
        """Set global variable context.
        
        Args:
            context: Global context dictionary
        """
        self.global_context = copy.deepcopy(context)
    
    def push_context(self, context: Dict[str, Any]) -> None:
        """Push a new context onto the context stack.
        
        Args:
            context: Context to push
        """
        self.context_stack.append(copy.deepcopy(context))
    
    def pop_context(self) -> Optional[Dict[str, Any]]:
        """Pop the top context from the context stack.
        
        Returns:
            Popped context or None if stack is empty
        """
        return self.context_stack.pop() if self.context_stack else None
    
    def get_merged_context(self, additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get merged context from global + stack + additional.
        
        Args:
            additional_context: Additional context to merge
            
        Returns:
            Merged context dictionary
        """
        merged = copy.deepcopy(self.global_context)
        
        # Merge contexts from stack (bottom to top)
        for context in self.context_stack:
            merged.update(context)
        
        # Merge additional context
        if additional_context:
            merged.update(additional_context)
        
        return merged
    
    def substitute_in_manifest(self, 
                              manifest: Dict[str, Any], 
                              context: Optional[Dict[str, Any]] = None,
                              recursive: bool = True) -> Dict[str, Any]:
        """Substitute variables throughout a manifest.
        
        Args:
            manifest: Manifest to process
            context: Additional context variables
            recursive: Whether to recursively process nested structures
            
        Returns:
            Manifest with variables substituted
        """
        # Get merged context
        full_context = self.get_merged_context(context)
        
        # Add manifest's own template_vars to context
        if 'template_vars' in manifest:
            template_vars = manifest['template_vars']
            if isinstance(template_vars, dict):
                full_context.update(template_vars)
        
        # Process the manifest
        if recursive:
            return self._substitute_recursive(manifest, full_context)
        else:
            return self._substitute_shallow(manifest, full_context)
    
    def _substitute_recursive(self, obj: Any, context: Dict[str, Any]) -> Any:
        """Recursively substitute variables in nested structures.
        
        Args:
            obj: Object to process
            context: Variable context
            
        Returns:
            Object with variables substituted
        """
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                # Substitute in key if it's a string
                new_key = self._substitute_string(key, context) if isinstance(key, str) else key
                # Recursively substitute in value
                result[new_key] = self._substitute_recursive(value, context)
            return result
        
        elif isinstance(obj, list):
            return [self._substitute_recursive(item, context) for item in obj]
        
        elif isinstance(obj, str):
            return self._substitute_string(obj, context)
        
        else:
            # Return primitive values as-is
            return obj
    
    def _substitute_shallow(self, obj: Any, context: Dict[str, Any]) -> Any:
        """Substitute variables only at the current level (non-recursive).
        
        Args:
            obj: Object to process
            context: Variable context
            
        Returns:
            Object with variables substituted at current level
        """
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                new_key = self._substitute_string(key, context) if isinstance(key, str) else key
                new_value = self._substitute_string(value, context) if isinstance(value, str) else value
                result[new_key] = new_value
            return result
        
        elif isinstance(obj, list):
            return [self._substitute_string(item, context) if isinstance(item, str) else item for item in obj]
        
        elif isinstance(obj, str):
            return self._substitute_string(obj, context)
        
        else:
            return obj
    
    def _substitute_string(self, text: str, context: Dict[str, Any]) -> str:
        """Substitute variables in a string.
        
        Args:
            text: Text to process
            context: Variable context
            
        Returns:
            Text with variables substituted
        """
        if not text or not isinstance(text, str):
            return text
        
        # Check for custom substitution patterns
        for pattern, substituter in self.custom_substituters.items():
            if pattern in text:
                try:
                    text = substituter(text, context)
                except Exception:
                    # Continue with standard substitution if custom fails
                    pass
        
        # Use template processor for standard substitution
        return self.template_processor.substitute_template_variables(text, context)
    
    def substitute_template_vars(self, 
                               manifest: Dict[str, Any],
                               external_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process template_vars section and apply to manifest.
        
        Args:
            manifest: Manifest to process
            external_context: External context variables
            
        Returns:
            Manifest with template variables processed and applied
        """
        result = copy.deepcopy(manifest)
        
        # Extract template_vars
        template_vars = result.get('template_vars', {})
        if not isinstance(template_vars, dict):
            return result
        
        # Build context from external + template_vars
        context = copy.deepcopy(external_context) if external_context else {}
        context.update(template_vars)
        
        # Merge with global context
        full_context = self.get_merged_context(context)
        
        # First, resolve template_vars themselves (in case they reference each other)
        resolved_template_vars = self._resolve_template_vars(template_vars, full_context)
        
        # Update context with resolved vars
        full_context.update(resolved_template_vars)
        
        # Apply to entire manifest (excluding template_vars section to avoid recursion)
        for section, content in result.items():
            if section != 'template_vars':
                result[section] = self._substitute_recursive(content, full_context)
        
        # Update template_vars in result
        result['template_vars'] = resolved_template_vars
        
        return result
    
    def _resolve_template_vars(self, 
                              template_vars: Dict[str, Any], 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve template variables that may reference each other.
        
        Args:
            template_vars: Template variables dictionary
            context: Variable context
            
        Returns:
            Resolved template variables
        """
        # Detect dependencies between template vars
        dependencies = self._analyze_template_var_dependencies(template_vars)
        
        # Resolve in dependency order
        resolved = {}
        working_context = copy.deepcopy(context)
        
        # Process variables in dependency order
        processed = set()
        
        def resolve_var(var_name: str) -> Any:
            if var_name in processed:
                return resolved.get(var_name)
            
            if var_name in template_vars:
                # Resolve dependencies first
                for dep in dependencies.get(var_name, []):
                    if dep in template_vars and dep not in processed:
                        resolve_var(dep)
                
                # Resolve this variable
                var_value = template_vars[var_name]
                if isinstance(var_value, str):
                    resolved_value = self._substitute_string(var_value, working_context)
                else:
                    resolved_value = self._substitute_recursive(var_value, working_context)
                
                resolved[var_name] = resolved_value
                working_context[var_name] = resolved_value
                processed.add(var_name)
                
                return resolved_value
            
            return None
        
        # Resolve all template vars
        for var_name in template_vars:
            resolve_var(var_name)
        
        return resolved
    
    def _analyze_template_var_dependencies(self, template_vars: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analyze dependencies between template variables.
        
        Args:
            template_vars: Template variables dictionary
            
        Returns:
            Dictionary mapping variable names to their dependencies
        """
        dependencies = {}
        
        for var_name, var_value in template_vars.items():
            deps = []
            
            if isinstance(var_value, str):
                # Find variable references in the value
                deps.extend(self._extract_variable_references(var_value, template_vars.keys()))
            
            dependencies[var_name] = deps
        
        return dependencies
    
    def _extract_variable_references(self, text: str, available_vars: List[str]) -> List[str]:
        """Extract variable references from text.
        
        Args:
            text: Text to analyze
            available_vars: List of available variable names
            
        Returns:
            List of referenced variable names
        """
        references = []
        
        # Look for {{var}} patterns
        jinja_pattern = re.compile(r'\{\{([^}]+)\}\}')
        for match in jinja_pattern.finditer(text):
            var_expr = match.group(1).strip()
            
            # Check if it matches any available variable
            for var_name in available_vars:
                if var_expr == var_name or var_expr.startswith(f"{var_name}."):
                    references.append(var_name)
        
        # Look for <?=var?> patterns
        php_pattern = re.compile(r'<\?=([^?]+)\?>')
        for match in php_pattern.finditer(text):
            var_expr = match.group(1).strip()
            
            # Check if it matches any available variable
            for var_name in available_vars:
                if var_expr == var_name or var_expr.startswith(f"{var_name}."):
                    references.append(var_name)
        
        return list(set(references))  # Remove duplicates
    
    def add_custom_substituter(self, pattern: str, substituter: Callable[[str, Dict[str, Any]], str]) -> None:
        """Add a custom substitution pattern and handler.
        
        Args:
            pattern: Pattern to match in strings
            substituter: Function to handle substitution
        """
        self.custom_substituters[pattern] = substituter
    
    def remove_custom_substituter(self, pattern: str) -> None:
        """Remove a custom substitution pattern.
        
        Args:
            pattern: Pattern to remove
        """
        if pattern in self.custom_substituters:
            del self.custom_substituters[pattern]
    
    def process_external_content_syntax(self, 
                                      manifest: Dict[str, Any],
                                      content_loader: Optional[Callable] = None) -> Dict[str, Any]:
        """Process {{EXTERNAL:filename}} syntax in manifest.
        
        Args:
            manifest: Manifest to process
            content_loader: Function to load external content
            
        Returns:
            Manifest with external content loaded and integrated
        """
        if not content_loader:
            return manifest
        
        # Add external content substituter
        def external_substituter(text: str, context: Dict[str, Any]) -> str:
            external_pattern = re.compile(r'\{\{EXTERNAL:([^}]+)\}\}')
            
            def replace_external(match):
                filename = match.group(1).strip()
                try:
                    content = content_loader(filename)
                    return str(content) if content is not None else ""
                except Exception:
                    return match.group(0)  # Return original if loading fails
            
            return external_pattern.sub(replace_external, text)
        
        # Temporarily add the substituter
        self.add_custom_substituter('{{EXTERNAL:', external_substituter)
        
        try:
            # Process manifest
            result = self._substitute_recursive(manifest, {})
            return result
        finally:
            # Clean up
            self.remove_custom_substituter('{{EXTERNAL:')
    
    def clear_context(self) -> None:
        """Clear all context data."""
        self.global_context.clear()
        self.context_stack.clear()
    
    def get_context_info(self) -> Dict[str, Any]:
        """Get information about current context state.
        
        Returns:
            Dictionary with context information
        """
        return {
            'global_context_keys': list(self.global_context.keys()),
            'context_stack_depth': len(self.context_stack),
            'custom_substituters': list(self.custom_substituters.keys()),
            'merged_context_keys': list(self.get_merged_context().keys())
        }
