#!/usr/bin/env python3
"""
Test poprawki CSS external format na istniejących manifestach
"""

import sys
import os
import yaml
import traceback
from copy import deepcopy

# Dodaj ścieżkę do WhyML modułów
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from whyml.converters.html_converter import HTMLConverter
from whyml.converters.vue_converter import VueConverter

def load_manifest(manifest_path):
    """Załaduj manifest z pliku"""
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def fix_external_css_format(manifest):
    """Napraw format external CSS w manifeście - konwertuj listę na string"""
    if 'styles' in manifest and 'external' in manifest['styles']:
        external = manifest['styles']['external']
        if isinstance(external, list):
            # Konwertuj listę na string oddzielony średnikami
            manifest['styles']['external'] = '; '.join(external)
            return True, len(external)
        else:
            return False, 0  # Już był stringiem
    return False, 0  # Brak sekcji external

def test_converter_with_manifest(converter_class, manifest, manifest_name, is_fixed=False):
    """Przetestuj converter z manifestem"""
    status = "FIXED" if is_fixed else "ORIGINAL"
    print(f"\n🧪 Testing {converter_class.__name__} with {manifest_name} ({status})")
    
    try:
        converter = converter_class()
        result = converter.convert(manifest)
        
        # Sprawdź typ wyniku
        if hasattr(result, 'content') and result.content:
            content_length = len(result.content)
            print(f"✅ SUCCESS: Generated {content_length} characters")
        else:
            print(f"✅ SUCCESS: Result type {type(result)}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        
        # Sprawdź czy to błąd 'list.split()'
        if "'list' object has no attribute 'split'" in str(e):
            print("🎯 FOUND 'list.split()' ERROR!")
        
        return False

def main():
    print("🧪 TESTING CSS EXTERNAL FIX WITH EXISTING MANIFESTS")
    print("=" * 60)
    
    # Test z zawodzącym manifestem
    failing_manifest_path = "/home/tom/github/dynapsys/whyml/project/tom_sapletta_pl/manifest.yaml"
    
    print(f"\n📁 Loading manifest: {failing_manifest_path}")
    try:
        original_manifest = load_manifest(failing_manifest_path)
        print(f"✅ Manifest loaded successfully")
    except Exception as e:
        print(f"❌ Error loading manifest: {e}")
        return False
    
    # Sprawdź obecny format external CSS
    if 'styles' in original_manifest and 'external' in original_manifest['styles']:
        external = original_manifest['styles']['external']
        print(f"📋 Current external CSS format: {type(external).__name__}")
        if isinstance(external, list):
            print(f"   List with {len(external)} URLs")
        else:
            print(f"   String with content: {external[:100]}...")
    
    # Testuj convertery z oryginalnym manifestem
    converters = [HTMLConverter, VueConverter]
    
    print(f"\n" + "="*60)
    print("🔬 TESTING WITH ORIGINAL MANIFEST (should fail)")
    
    original_results = {}
    for converter_class in converters:
        success = test_converter_with_manifest(converter_class, original_manifest, "tom.sapletta.pl", is_fixed=False)
        original_results[converter_class.__name__] = success
    
    # Stwórz poprawioną wersję manifestu
    fixed_manifest = deepcopy(original_manifest)
    was_list, url_count = fix_external_css_format(fixed_manifest)
    
    if was_list:
        print(f"\n🔧 APPLIED FIX: Converted {url_count} external CSS URLs from list to semicolon-separated string")
    else:
        print(f"\n⚠️  WARNING: external CSS was not a list - already in correct format?")
    
    # Testuj convertery z poprawionym manifestem
    print(f"\n" + "="*60)
    print("🔬 TESTING WITH FIXED MANIFEST (should work)")
    
    fixed_results = {}
    for converter_class in converters:
        success = test_converter_with_manifest(converter_class, fixed_manifest, "tom.sapletta.pl", is_fixed=True)
        fixed_results[converter_class.__name__] = success
    
    # Podsumowanie wyników
    print(f"\n" + "="*60)
    print("📊 RESULTS SUMMARY:")
    
    for converter_name in converters:
        name = converter_name.__name__
        original_status = "✅ SUCCESS" if original_results[name] else "❌ FAILED"
        fixed_status = "✅ SUCCESS" if fixed_results[name] else "❌ FAILED"
        
        print(f"\n{name}:")
        print(f"  Original manifest: {original_status}")
        print(f"  Fixed manifest:    {fixed_status}")
        
        if not original_results[name] and fixed_results[name]:
            print(f"  🎉 FIX WORKED! Conversion now succeeds")
        elif original_results[name] and fixed_results[name]:
            print(f"  ℹ️  Both worked (unexpected)")
        elif not original_results[name] and not fixed_results[name]:
            print(f"  ⚠️  Fix didn't work - both failed")
    
    # Sprawdź czy poprawka zadziałała
    html_fixed = fixed_results['HTMLConverter'] and not original_results['HTMLConverter'] 
    vue_fixed = fixed_results['VueConverter'] and not original_results['VueConverter']
    
    if html_fixed or vue_fixed:
        print(f"\n🎉 SUCCESS: CSS external format fix works!")
        if html_fixed:
            print(f"   ✅ HTMLConverter now works")
        if vue_fixed:
            print(f"   ✅ VueConverter now works")
        print(f"\nReady to regenerate all manifests with the fix!")
        return True
    else:
        print(f"\n🤔 INCONCLUSIVE: Need to investigate further")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
