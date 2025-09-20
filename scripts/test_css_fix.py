#!/usr/bin/env python3
"""
Test poprawki CSS external format w SimpleManifestGenerator
"""

import sys
import os
import requests
import traceback

# Dodaj ścieżkę do WhyML modułów
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.simple_manifest_generator import SimpleManifestGenerator
from whyml.converters.html_converter import HTMLConverter
from whyml.converters.vue_converter import VueConverter

def test_css_fix():
    print("🧪 TESTING CSS EXTERNAL FORMAT FIX")
    print("=" * 50)
    
    # Użyj problematycznego URL który wcześniej zawodził
    test_url = "https://tom.sapletta.pl"
    
    print(f"📥 Pobieranie HTML z {test_url}...")
    try:
        response = requests.get(test_url, timeout=10)
        response.raise_for_status()
        html_content = response.text
        print(f"✅ Pobrano {len(html_content)} znaków HTML")
    except Exception as e:
        print(f"❌ Błąd pobierania HTML: {e}")
        return False
    
    # Stwórz manifest z poprawionym SimpleManifestGenerator
    print(f"\n🏗️  Generowanie manifestu z poprawionym SimpleManifestGenerator...")
    try:
        generator = SimpleManifestGenerator(test_url)
        manifest = generator.generate_manifest(html_content)
        print(f"✅ Manifest wygenerowany pomyślnie")
        
        # Sprawdź format sekcji styles.external
        if 'styles' in manifest and 'external' in manifest['styles']:
            external_css = manifest['styles']['external']
            external_type = type(external_css).__name__
            print(f"📋 styles.external type: {external_type}")
            
            if isinstance(external_css, str):
                url_count = len(external_css.split(';')) if external_css else 0
                print(f"✅ POPRAWKA DZIAŁA! external to string z {url_count} URL-ami")
                print(f"   Preview: {external_css[:100]}..." if len(external_css) > 100 else f"   Content: {external_css}")
            else:
                print(f"❌ BŁĄD: external nadal to {external_type}, nie string!")
                print(f"   Content: {external_css}")
                return False
        else:
            print("ℹ️  Brak sekcji external CSS w manifeście")
        
    except Exception as e:
        print(f"❌ Błąd generowania manifestu: {e}")
        traceback.print_exc()
        return False
    
    # Testuj HTML converter
    print(f"\n🧪 Testowanie HTML Converter...")
    try:
        html_converter = HTMLConverter()
        html_result = html_converter.convert(manifest)
        
        if hasattr(html_result, 'content') and html_result.content:
            print(f"✅ HTML Converter SUKCES! Wygenerowano {len(html_result.content)} znaków")
        else:
            print(f"✅ HTML Converter SUKCES! Result type: {type(html_result)}")
    except Exception as e:
        print(f"❌ HTML Converter BŁĄD: {e}")
        if "'list' object has no attribute 'split'" in str(e):
            print("🎯 NADAL BŁĄD 'list.split()' - poprawka nie zadziałała!")
        traceback.print_exc()
        return False
    
    # Testuj Vue converter  
    print(f"\n🧪 Testowanie Vue Converter...")
    try:
        vue_converter = VueConverter()
        vue_result = vue_converter.convert(manifest)
        
        if hasattr(vue_result, 'content') and vue_result.content:
            print(f"✅ Vue Converter SUKCES! Wygenerowano {len(vue_result.content)} znaków")
        else:
            print(f"✅ Vue Converter SUKCES! Result type: {type(vue_result)}")
    except Exception as e:
        print(f"❌ Vue Converter BŁĄD: {e}")
        if "'list' object has no attribute 'split'" in str(e):
            print("🎯 NADAL BŁĄD 'list.split()' - poprawka nie zadziałała!")
        traceback.print_exc()
        return False
    
    print(f"\n🎉 WSZYSTKIE TESTY PRZESZŁY POMYŚLNIE!")
    print(f"✅ SimpleManifestGenerator poprawka działa")
    print(f"✅ HTML Converter działa z nowym formatem")
    print(f"✅ Vue Converter działa z nowym formatem")
    print(f"\nGotowe do regeneracji wszystkich manifestów!")
    
    return True

if __name__ == "__main__":
    success = test_css_fix()
    exit(0 if success else 1)
