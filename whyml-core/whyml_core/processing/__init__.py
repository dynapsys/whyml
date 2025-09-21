"""
WhyML Core Processing - Template processing and inheritance resolution

Provides comprehensive template processing functionality including template inheritance,
variable substitution, and manifest processing workflows.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from .template_processor import TemplateProcessor
from .inheritance_resolver import InheritanceResolver
from .variable_substitution import VariableSubstitution
from .manifest_processor import ManifestProcessor

__all__ = [
    'TemplateProcessor',
    'InheritanceResolver',
    'VariableSubstitution',
    'ManifestProcessor'
]
