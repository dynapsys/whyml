"""
PASVG - Project Artifact SVG
============================

Revolutionary single-file project distribution system using SVG containers.

This package provides tools for:
- Generating PASVG files from project sources
- Extracting projects from PASVG files
- Validating PASVG file structure
- Building projects from PASVG artifacts
- Importing various project formats

Example usage:
    >>> from pasvg import Generator, Extractor, Validator
    >>> 
    >>> # Generate PASVG from project
    >>> generator = Generator()
    >>> pasvg_file = generator.generate_from_markdown("tutorial.md", "output/")
    >>> 
    >>> # Extract project from PASVG
    >>> extractor = Extractor()
    >>> project_dir = extractor.extract("project.pasvg.svg", "extracted/")
    >>> 
    >>> # Validate PASVG file
    >>> validator = Validator()
    >>> is_valid = validator.validate("project.pasvg.svg")
"""

__version__ = "1.0.0"
__author__ = "WhyML PASVG System"
__email__ = "pasvg@whyml.org"

from pasvg.core.generator import Generator
from pasvg.core.extractor import Extractor
from pasvg.core.validator import Validator
from pasvg.core.builder import Builder
from pasvg.core.models import PASVGMetadata, SourceFile, ProjectConfig

__all__ = [
    "Generator",
    "Extractor", 
    "Validator",
    "Builder",
    "PASVGMetadata",
    "SourceFile",
    "ProjectConfig",
]
