#!/usr/bin/env python3
"""
Test rzeczywistych manifestów z HTML/Vue converterami aby zreprodukować błąd 'list.split()'
"""

import sys
import os
import traceback
import yaml

# Dodaj ścieżkę do WhyML modułów
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from whyml.converters.html_converter import HTMLConverter
from whyml.converters.vue_converter import VueConverter

def load_manifest(manifest_path):
    """Załaduj manifest YAML z pliku"""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ ERROR loading {manifest_path}: {e}")
        return None

def test_converter_with_manifest(converter_class, manifest, manifest_name):
    """Przetestuj converter z rzeczywistym manifestem"""
    print(f"\n=== TESTING {converter_class.__name__} with {manifest_name} ===")
    
    try:
        converter = converter_class()
        result = converter.convert(manifest)
        
        # Sprawdź typ wyniku
        if hasattr(result, 'content'):
            content_length = len(result.content) if result.content else 0
            print(f"✅ SUCCESS: {converter_class.__name__} converted successfully")
            print(f"Output content length: {content_length} characters")
        else:
            print(f"✅ SUCCESS: {converter_class.__name__} returned result: {type(result)}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR in {converter_class.__name__}: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Pokaż pełny traceback
        tb = traceback.format_exc()
        print("FULL TRACEBACK:")
        print(tb)
        
        # Sprawdź czy to błąd 'list.split()'
        if "'list' object has no attribute 'split'" in str(e) or "'list' object has no attribute 'split'" in tb:
            print("🎯 FOUND THE 'list.split()' ERROR!")
            
            # Znajdź linię kodu która wywołuje błąd
            lines = tb.split('\n')
            for i, line in enumerate(lines):
                if 'split' in line and 'File' in line:
                    print(f"📍 ERROR LOCATION: {line.strip()}")
                    if i + 1 < len(lines):
                        print(f"📄 CODE LINE: {lines[i + 1].strip()}")
        
        return False

def analyze_manifest_sections(manifest, manifest_name):
    """Przeanalizuj sekcje manifestu które mogą powodować problemy"""
    print(f"\n📋 ANALYZING {manifest_name} STRUCTURE:")
    
    if 'structure' in manifest:
        structure = manifest['structure']
        print(f"  structure type: {type(structure)}")
        
        if 'children' in structure:
            children = structure['children']
            print(f"  children type: {type(children)}")
            print(f"  children length: {len(children) if isinstance(children, list) else 'N/A'}")
            
            # Sprawdź czy children zawiera nieprawidłowe listy
            if isinstance(children, list) and len(children) > 0:
                first_child = children[0]
                print(f"  first child type: {type(first_child)}")
                print(f"  first child keys: {list(first_child.keys()) if isinstance(first_child, dict) else 'N/A'}")
                
                # Sprawdź czy jakieś pole w dziecku jest listą gdy powinno być stringiem
                if isinstance(first_child, dict):
                    for key, value in first_child.items():
                        if isinstance(value, list):
                            print(f"  ⚠️  POTENTIAL ISSUE: {key} is a list: {value}")
    
    if 'styles' in manifest:
        styles = manifest['styles']
        print(f"  styles type: {type(styles)}")
        if isinstance(styles, dict):
            for selector, rules in styles.items():
                if isinstance(rules, list):
                    print(f"  ⚠️  POTENTIAL ISSUE: style '{selector}' is a list: {rules}")
    
    if 'imports' in manifest:
        imports = manifest['imports']
        print(f"  imports type: {type(imports)}")
        if isinstance(imports, dict):
            for key, value in imports.items():
                if isinstance(value, list):
                    print(f"  ⚠️  POTENTIAL ISSUE: import '{key}' is a list: {value}")

def main():
    print("🔍 DEBUG: Testing real manifests with HTML/Vue converters")
    print("=" * 70)
    
    # Ścieżki do rzeczywistych manifestów
    manifests_to_test = [
        ("/home/tom/github/dynapsys/whyml/project/example_com/manifest.yaml", "example.com (working)"),
        ("/home/tom/github/dynapsys/whyml/project/tom_sapletta_pl/manifest.yaml", "tom.sapletta.pl (failing)"),
        ("/home/tom/github/dynapsys/whyml/project/bielik_ai/manifest.yaml", "bielik.ai (failing)")
    ]
    
    # Załaduj manifesty
    loaded_manifests = []
    for path, name in manifests_to_test:
        manifest = load_manifest(path)
        if manifest:
            loaded_manifests.append((manifest, name, path))
            analyze_manifest_sections(manifest, name)
        else:
            print(f"⚠️  Skipping {name} - failed to load")
    
    # Test converterów
    converters = [HTMLConverter, VueConverter]
    results = {}
    
    for converter_class in converters:
        results[converter_class.__name__] = {}
        
        for manifest, name, path in loaded_manifests:
            success = test_converter_with_manifest(converter_class, manifest, name)
            results[converter_class.__name__][name] = success
    
    # Podsumowanie wyników
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS SUMMARY:")
    for converter_name, converter_results in results.items():
        print(f"\n{converter_name}:")
        for manifest_name, success in converter_results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"  {manifest_name}: {status}")
    
    # Sprawdź czy znaleźliśmy błąd
    found_error = False
    for converter_results in results.values():
        for success in converter_results.values():
            if not success:
                found_error = True
                break
    
    if found_error:
        print(f"\n🎯 SUCCESS: Reproduced the conversion errors!")
        print("Check the traceback above to find the exact location of the 'list.split()' call")
    else:
        print(f"\n🤔 UNEXPECTED: All conversions succeeded - the error might be elsewhere")

if __name__ == "__main__":
    main()
