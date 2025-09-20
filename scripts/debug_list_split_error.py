#!/usr/bin/env python3
"""
Minimalny test case do debugowania błędu 'list.split()' w HTML/Vue converterach
"""

import sys
import os
import traceback
import yaml

# Dodaj ścieżkę do WhyML modułów
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from whyml.converters.html_converter import HTMLConverter
from whyml.converters.vue_converter import VueConverter

def create_minimal_failing_manifest():
    """Stwórz minimalny manifest który powoduje błąd 'list.split()'"""
    return {
        'metadata': {
            'title': 'Test Manifest',
            'description': 'Minimal test case for list.split() error'
        },
        'structure': {
            'children': [
                {
                    'tag': 'h1',
                    'text': 'Test Heading',
                    'type': 'heading',
                    'level': 1
                },
                {
                    'tag': 'p',
                    'text': 'Test paragraph',
                    'type': 'text'
                }
            ]
        },
        'styles': {
            'h1': 'color: blue; font-size: 24px;',
            'p': 'color: black; margin: 10px;'
        },
        'imports': {
            'inline_scripts': 'console.log("test");'
        }
    }

def create_working_manifest():
    """Stwórz manifest który działa (jak example.com)"""
    return {
        'metadata': {
            'title': 'Working Test',
            'description': 'Test manifest that should work'
        },
        'structure': {
            'children': [
                {
                    'tag': 'div',
                    'text': 'Simple div',
                    'type': 'container'
                }
            ]
        },
        'styles': {
            'div': 'width: 100%; padding: 10px;'
        },
        'imports': {
            'inline_scripts': 'console.log("working");'
        }
    }

def test_converter(converter_class, manifest, test_name):
    """Przetestuj converter z danym manifestem"""
    print(f"\n=== TESTING {converter_class.__name__} with {test_name} ===")
    
    try:
        converter = converter_class()
        result = converter.convert(manifest)
        print(f"✅ SUCCESS: {converter_class.__name__} converted successfully")
        print(f"Output length: {len(result)} characters")
        return True
        
    except Exception as e:
        print(f"❌ ERROR in {converter_class.__name__}: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Pokaż pełny traceback jeśli zawiera 'split'
        tb = traceback.format_exc()
        if 'split' in tb:
            print("TRACEBACK (contains 'split'):")
            print(tb)
        
        return False

def main():
    print("🔍 DEBUG: Investigating 'list.split()' error in WhyML converters")
    print("=" * 60)
    
    # Stwórz manifesty testowe
    failing_manifest = create_minimal_failing_manifest()
    working_manifest = create_working_manifest()
    
    print("\n📋 FAILING MANIFEST STRUCTURE:")
    print(f"structure.children type: {type(failing_manifest['structure']['children'])}")
    print(f"structure.children length: {len(failing_manifest['structure']['children'])}")
    print(f"First child: {failing_manifest['structure']['children'][0]}")
    
    print("\n📋 WORKING MANIFEST STRUCTURE:")
    print(f"structure.children type: {type(working_manifest['structure']['children'])}")
    print(f"structure.children length: {len(working_manifest['structure']['children'])}")
    
    # Test obu converterów z oboma manifestami
    converters = [HTMLConverter, VueConverter]
    manifests = [
        (working_manifest, "Working Manifest"),
        (failing_manifest, "Failing Manifest")
    ]
    
    results = {}
    
    for converter_class in converters:
        results[converter_class.__name__] = {}
        for manifest, name in manifests:
            success = test_converter(converter_class, manifest, name)
            results[converter_class.__name__][name] = success
    
    # Podsumowanie wyników
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY:")
    for converter_name, converter_results in results.items():
        print(f"\n{converter_name}:")
        for manifest_name, success in converter_results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"  {manifest_name}: {status}")
    
    # Sprawdź czy znaleźliśmy błąd
    html_failed = not results['HTMLConverter']['Failing Manifest']
    vue_failed = not results['VueConverter']['Failing Manifest']
    
    if html_failed or vue_failed:
        print(f"\n🎯 REPRODUCTION SUCCESS: Found the 'list.split()' error!")
        if html_failed:
            print("- HTMLConverter fails with failing manifest")
        if vue_failed:
            print("- VueConverter fails with failing manifest")
        print("\nNext step: Examine the traceback to find exact location of .split() call")
    else:
        print(f"\n🤔 NO ERROR REPRODUCED: Both converters work with both manifests")
        print("Need to create a more complex failing manifest or check different issue")

if __name__ == "__main__":
    main()
