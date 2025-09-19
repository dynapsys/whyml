#!/usr/bin/env python3
"""Debug script to understand metadata detection issues."""

import xml.etree.ElementTree as ET

# Test XML content similar to what the test creates
test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" data-pasvg-version="1.0" data-project-name="Test Project">
    <!-- PASVG Metadata -->
    <metadata data-pasvg="true">
        <project-name>Test Project</project-name>
        <description>A test PASVG file</description>
        <version>1.0.0</version>
        <technologies>python,javascript</technologies>
        <platforms>web,desktop</platforms>
        <build-targets>static,docker</build-targets>
    </metadata>
    
    <!-- Source Files -->
    <foreignObject data-filename="main.py" data-type="python" data-language="python">
        <![CDATA[print("Hello from PASVG!")]]>
    </foreignObject>
    
    <rect x="0" y="0" width="800" height="600" fill="white"/>
    <text x="20" y="30" font-size="16">Test PASVG Project</text>
</svg>'''

print("=== DEBUGGING METADATA DETECTION ===")

# Parse the XML
try:
    root = ET.fromstring(test_xml)
    print(f"✓ XML parsed successfully")
    print(f"Root tag: {root.tag}")
    print(f"Root attributes: {root.attrib}")
    
    # Try different ways to find metadata
    print("\n=== METADATA SEARCH ATTEMPTS ===")
    
    # Method 1: Simple search
    metadata_1 = root.find('.//metadata')
    print(f"1. root.find('.//metadata'): {metadata_1}")
    
    # Method 2: Search with attribute
    metadata_2 = root.find('.//metadata[@data-pasvg="true"]')
    print(f"2. root.find('.//metadata[@data-pasvg=\"true\"]'): {metadata_2}")
    
    # Method 3: Search all children
    print("\n3. All direct children:")
    for i, child in enumerate(root):
        print(f"   Child {i}: tag='{child.tag}', attrib={child.attrib}")
        if 'metadata' in child.tag.lower():
            print(f"      ✓ Found metadata element!")
            # Print its children
            for j, grandchild in enumerate(child):
                print(f"        Child {j}: tag='{grandchild.tag}', text='{grandchild.text}'")
    
    # Method 4: Recursive search
    print("\n4. Recursive search:")
    def find_all_elements(element, level=0):
        indent = "  " * level
        print(f"{indent}{element.tag} - {element.attrib}")
        for child in element:
            find_all_elements(child, level + 1)
    
    find_all_elements(root)
    
except ET.ParseError as e:
    print(f"✗ XML parsing failed: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
