#!/usr/bin/env python3
"""
Identyfikuj które reguły CSS w manifestach są listami zamiast stringów
"""

import sys
import os
import yaml

def analyze_styles_section(manifest_path, name):
    """Przeanalizuj sekcję styles w manifeście"""
    print(f"\n=== ANALYZING STYLES in {name} ===")
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)
        
        if 'styles' not in manifest:
            print("❌ No 'styles' section found")
            return
        
        styles = manifest['styles']
        print(f"📊 Found {len(styles)} CSS rules in styles section")
        
        list_rules = []
        string_rules = []
        other_rules = []
        
        for selector, rules in styles.items():
            rule_type = type(rules).__name__
            
            if isinstance(rules, list):
                list_rules.append((selector, rules))
                print(f"📋 LIST RULE: '{selector}' -> {rules}")
            elif isinstance(rules, str):
                string_rules.append((selector, rules))
                # Pokaż tylko pierwsze 100 znaków dla czytelności
                preview = rules[:100] + "..." if len(rules) > 100 else rules
                print(f"📄 STRING RULE: '{selector}' -> \"{preview}\"")
            else:
                other_rules.append((selector, rules))
                print(f"❓ OTHER RULE: '{selector}' -> {rule_type}: {rules}")
        
        print(f"\n📊 SUMMARY for {name}:")
        print(f"  ✅ String rules: {len(string_rules)}")
        print(f"  ❌ List rules: {len(list_rules)} (THESE CAUSE THE ERROR)")
        print(f"  ❓ Other types: {len(other_rules)}")
        
        if list_rules:
            print(f"\n🎯 PROBLEMATIC LIST RULES in {name}:")
            for selector, rules in list_rules:
                print(f"  - '{selector}': {rules}")
        
        return len(list_rules) > 0
        
    except Exception as e:
        print(f"❌ ERROR analyzing {manifest_path}: {e}")
        return False

def main():
    print("🔍 IDENTIFYING CSS LIST RULES that cause 'list.split()' error")
    print("=" * 60)
    
    # Manifesty do sprawdzenia
    manifests_to_check = [
        ("/home/tom/github/dynapsys/whyml/project/example_com/manifest.yaml", "example.com (working)"),
        ("/home/tom/github/dynapsys/whyml/project/tom_sapletta_pl/manifest.yaml", "tom.sapletta.pl (failing)"),
        ("/home/tom/github/dynapsys/whyml/project/bielik_ai/manifest.yaml", "bielik.ai (failing)")
    ]
    
    problems_found = False
    
    for manifest_path, name in manifests_to_check:
        has_list_rules = analyze_styles_section(manifest_path, name)
        if has_list_rules:
            problems_found = True
    
    print("\n" + "=" * 60)
    if problems_found:
        print("🎯 CONCLUSION: Found CSS rules as lists - this is the root cause!")
        print("   Next step: Fix SimpleManifestGenerator to convert all CSS rules to strings")
    else:
        print("🤔 CONCLUSION: No list rules found - may need to investigate further")

if __name__ == "__main__":
    main()
