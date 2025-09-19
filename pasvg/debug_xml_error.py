#!/usr/bin/env python3
"""Debug script to understand XML validation error messages."""

from pasvg.core.validator import Validator
import tempfile
import os

print("=== DEBUGGING XML ERROR MESSAGES ===")

# Create a temporary file with invalid XML
validator = Validator()

with tempfile.NamedTemporaryFile(mode='w', suffix='.pasvg.svg', delete=False) as f:
    f.write("This is not valid XML <unclosed tag")
    temp_file = f.name

try:
    result = validator.validate(temp_file)
    
    print(f"Validation result:")
    print(f"  is_valid: {result.is_valid}")
    print(f"  errors: {result.errors}")
    print(f"  warnings: {result.warnings}")
    
    if result.errors:
        print(f"\nError messages:")
        for i, error in enumerate(result.errors):
            print(f"  {i+1}. '{error}'")
            print(f"     Contains 'XML': {'XML' in error}")
    
finally:
    # Clean up
    os.unlink(temp_file)
