"""
WhyML Core Template Processor - Advanced template processing with Jinja2

Handles template variable substitution, inheritance, and advanced template features
with support for multiple syntax styles and robust error handling.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import re
import logging
from typing import Any, Dict, Optional
from jinja2 import Template, Environment, BaseLoader, TemplateError

from ..exceptions import TemplateError as WhyMLTemplateError

logger = logging.getLogger(__name__)


class TemplateProcessor:
    """Processes template inheritance and variable substitution with Jinja2."""
    
    def __init__(self, enable_autoescape: bool = True, strict_undefined: bool = False):
        """Initialize template processor with Jinja2 environment.
        
        Args:
            enable_autoescape: Whether to enable automatic escaping
            strict_undefined: Whether to raise errors on undefined variables
        """
        self.env = Environment(
            loader=BaseLoader(),
            autoescape=enable_autoescape,
            undefined=self._get_undefined_handler(strict_undefined)
        )
        
        # Add useful globals to template environment
        self.env.globals.update({
            'range': range,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'enumerate': enumerate,
            'zip': zip,
            'min': min,
            'max': max,
            'sum': sum,
            'abs': abs,
            'round': round
        })
        
        # Add custom filters
        self.env.filters.update({
            'capitalize_first': self._capitalize_first,
            'snake_case': self._snake_case,
            'camel_case': self._camel_case,
            'pascal_case': self._pascal_case,
            'kebab_case': self._kebab_case
        })
    
    def _get_undefined_handler(self, strict_undefined: bool):
        """Get appropriate undefined handler for Jinja2.
        
        Args:
            strict_undefined: Whether to be strict about undefined variables
            
        Returns:
            Appropriate undefined handler class
        """
        if strict_undefined:
            from jinja2 import StrictUndefined
            return StrictUndefined
        else:
            from jinja2 import DebugUndefined
            return DebugUndefined
    
    def substitute_template_variables(self, 
                                    content: str, 
                                    variables: Dict[str, Any], 
                                    config: Optional[Dict[str, Any]] = None) -> str:
        """Substitute template variables in content using both {{VAR}} and <?=VAR?> syntax.
        
        Args:
            content: Content string containing template variables
            variables: Dictionary of variables to substitute
            config: Optional configuration for substitution behavior
            
        Returns:
            Content with variables substituted
            
        Raises:
            WhyMLTemplateError: If template processing fails critically
        """
        if not content:
            return content
        
        if not variables:
            variables = {}
            
        # Prepare context with variables and config
        context = {}
        context.update(variables)
        if config:
            context.update(config)
        
        try:
            # First handle {{VAR}} syntax (Jinja2 style)
            content = self._substitute_jinja_variables(content, context)
            
            # Then handle <?=VAR?> syntax (PHP-like)
            content = self._substitute_php_variables(content, context)
            
            return content
            
        except Exception as e:
            logger.warning(f"Template substitution error: {e}")
            # Return original content on non-critical errors
            return content
    
    def _substitute_jinja_variables(self, content: str, context: Dict[str, Any]) -> str:
        """Substitute Jinja2-style {{VAR}} variables.
        
        Args:
            content: Content string with Jinja2 variables
            context: Variable context dictionary
            
        Returns:
            Content with Jinja2 variables substituted
        """
        try:
            jinja_template = self.env.from_string(content)
            return jinja_template.render(**context)
        except TemplateError as e:
            logger.warning(f"Jinja2 template error: {e}")
            raise WhyMLTemplateError(f"Jinja2 template processing failed: {e}")
        except Exception as e:
            logger.warning(f"Jinja2 processing error: {e}")
            return content
    
    def _substitute_php_variables(self, content: str, context: Dict[str, Any]) -> str:
        """Substitute PHP-style <?=VAR?> variables.
        
        Args:
            content: Content string with PHP-style variables
            context: Variable context dictionary
            
        Returns:
            Content with PHP-style variables substituted
        """
        php_pattern = re.compile(r'<\?=([^?]+)\?>')
        
        def php_replacer(match):
            var_expr = match.group(1).strip()
            try:
                return self._resolve_variable_expression(var_expr, context)
            except Exception as e:
                logger.debug(f"PHP variable resolution error for '{var_expr}': {e}")
                return match.group(0)  # Return original if resolution fails
        
        return php_pattern.sub(php_replacer, content)
    
    def _resolve_variable_expression(self, expression: str, context: Dict[str, Any]) -> str:
        """Resolve a variable expression against context.
        
        Args:
            expression: Variable expression to resolve (e.g., 'var', 'obj.prop', 'arr[0]')
            context: Variable context dictionary
            
        Returns:
            Resolved variable value as string
        """
        # Simple variable lookup
        if expression in context:
            return str(context[expression])
        
        # Handle dot notation like VAR.property or VAR.nested.prop
        if '.' in expression:
            return self._resolve_dot_notation(expression, context)
        
        # Handle array notation like VAR[0] or VAR['key']
        if '[' in expression and ']' in expression:
            return self._resolve_array_notation(expression, context)
        
        # Variable not found
        raise KeyError(f"Variable '{expression}' not found in context")
    
    def _resolve_dot_notation(self, expression: str, context: Dict[str, Any]) -> str:
        """Resolve dot notation variable access.
        
        Args:
            expression: Dot notation expression (e.g., 'obj.prop.nested')
            context: Variable context dictionary
            
        Returns:
            Resolved value as string
        """
        parts = expression.split('.')
        value = context
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                raise KeyError(f"Property '{part}' not found in '{expression}'")
        
        return str(value)
    
    def _resolve_array_notation(self, expression: str, context: Dict[str, Any]) -> str:
        """Resolve array notation variable access.
        
        Args:
            expression: Array notation expression (e.g., 'arr[0]', 'obj[key]')
            context: Variable context dictionary
            
        Returns:
            Resolved value as string
        """
        # Parse array notation: var_name[index]
        match = re.match(r'([^[]+)\[([^]]+)\]', expression)
        if not match:
            raise ValueError(f"Invalid array notation: '{expression}'")
        
        var_name, index_expr = match.groups()
        
        # Get the base variable
        if var_name not in context:
            raise KeyError(f"Variable '{var_name}' not found")
        
        base_value = context[var_name]
        
        # Resolve the index
        try:
            # Try as integer index first
            if index_expr.isdigit():
                index = int(index_expr)
                return str(base_value[index])
            
            # Try as string key (remove quotes if present)
            index_key = index_expr.strip('\'"')
            return str(base_value[index_key])
            
        except (IndexError, KeyError, TypeError) as e:
            raise KeyError(f"Index '{index_expr}' not valid for '{var_name}': {e}")
    
    def render_template_string(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render a template string with full Jinja2 features.
        
        Args:
            template_str: Template string to render
            context: Template context variables
            
        Returns:
            Rendered template string
            
        Raises:
            WhyMLTemplateError: If template rendering fails
        """
        try:
            template = self.env.from_string(template_str)
            return template.render(**context)
        except TemplateError as e:
            raise WhyMLTemplateError(f"Template rendering failed: {e}", template_name="string")
        except Exception as e:
            raise WhyMLTemplateError(f"Unexpected template error: {e}")
    
    def validate_template_syntax(self, template_str: str) -> tuple[bool, Optional[str]]:
        """Validate template syntax without rendering.
        
        Args:
            template_str: Template string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            self.env.from_string(template_str)
            return True, None
        except TemplateError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {e}"
    
    # Custom filter functions
    def _capitalize_first(self, value: str) -> str:
        """Capitalize only the first letter."""
        return value[0].upper() + value[1:] if value else ""
    
    def _snake_case(self, value: str) -> str:
        """Convert to snake_case."""
        # Replace spaces and hyphens with underscores
        value = re.sub(r'[-\s]+', '_', value)
        # Insert underscores before capital letters
        value = re.sub(r'(?<!^)(?=[A-Z])', '_', value)
        return value.lower()
    
    def _camel_case(self, value: str) -> str:
        """Convert to camelCase."""
        words = re.split(r'[-_\s]+', value.lower())
        if not words:
            return ""
        return words[0] + ''.join(word.capitalize() for word in words[1:])
    
    def _pascal_case(self, value: str) -> str:
        """Convert to PascalCase."""
        words = re.split(r'[-_\s]+', value.lower())
        return ''.join(word.capitalize() for word in words)
    
    def _kebab_case(self, value: str) -> str:
        """Convert to kebab-case."""
        # Replace spaces and underscores with hyphens
        value = re.sub(r'[_\s]+', '-', value)
        # Insert hyphens before capital letters
        value = re.sub(r'(?<!^)(?=[A-Z])', '-', value)
        return value.lower()
    
    def add_custom_filter(self, name: str, filter_func) -> None:
        """Add a custom filter to the template environment.
        
        Args:
            name: Filter name
            filter_func: Filter function
        """
        self.env.filters[name] = filter_func
    
    def add_custom_global(self, name: str, value: Any) -> None:
        """Add a custom global to the template environment.
        
        Args:
            name: Global variable name
            value: Global variable value
        """
        self.env.globals[name] = value
