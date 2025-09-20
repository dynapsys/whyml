#!/bin/bash

# Run All WhyML Examples
# This script runs all available examples to demonstrate WhyML functionality

set -e  # Exit on any error

echo "🚀 WhyML Examples Runner"
echo "======================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the WhyML root directory"
    echo "   cd /path/to/whyml && ./scripts/run-all-examples.sh"
    exit 1
fi

# Check if WhyML is installed
if ! command -v whyml &> /dev/null; then
    echo "❌ Error: WhyML CLI not found. Please install WhyML first:"
    echo "   pip install -e ."
    exit 1
fi

echo "✅ WhyML CLI found: $(which whyml)"
echo "✅ Current directory: $(pwd)"
echo ""

# Function to run a script and handle errors
run_script() {
    local script_path="$1"
    local script_name="$2"
    
    echo "▶️  Running: $script_name"
    echo "   Script: $script_path"
    
    if [ -f "$script_path" ]; then
        if bash "$script_path"; then
            echo "✅ $script_name completed successfully"
        else
            echo "❌ $script_name failed"
            return 1
        fi
    else
        echo "❌ Script not found: $script_path"
        return 1
    fi
    
    echo ""
}

# Function to run Python script
run_python_script() {
    local script_path="$1"
    local script_name="$2"
    
    echo "▶️  Running: $script_name (Python)"
    echo "   Script: $script_path"
    
    if [ -f "$script_path" ]; then
        if python3 "$script_path"; then
            echo "✅ $script_name completed successfully"
        else
            echo "❌ $script_name failed"
            return 1
        fi
    else
        echo "❌ Script not found: $script_path"
        return 1
    fi
    
    echo ""
}

# Track success/failure
success_count=0
total_count=0

# Example 1: Complete Workflow
echo "🔥 Running Example 1: Complete Webpage Scraping and Regeneration"
echo "================================================================"

((total_count++))
if run_script "scripts/examples/run-example-1.sh" "Example 1 (CLI)"; then
    ((success_count++))
fi

echo "🐍 Running Example 1 with Python API"
echo "====================================="

((total_count++))
if run_python_script "scripts/examples/run-example-1.py" "Example 1 (Python API)"; then
    ((success_count++))
fi

# Example 2: Advanced Scraping (if exists)
if [ -f "scripts/examples/run-advanced-scraping.sh" ]; then
    echo "🕷️  Running Advanced Scraping Examples"
    echo "======================================"
    
    ((total_count++))
    if run_script "scripts/examples/run-advanced-scraping.sh" "Advanced Scraping"; then
        ((success_count++))
    fi
fi

# Example 3: Multi-format Conversion (if exists)
if [ -f "scripts/examples/run-multi-format.sh" ]; then
    echo "🔄 Running Multi-format Conversion Examples"
    echo "==========================================="
    
    ((total_count++))
    if run_script "scripts/examples/run-multi-format.sh" "Multi-format Conversion"; then
        ((success_count++))
    fi
fi

# Summary
echo "📊 SUMMARY"
echo "=========="
echo "✅ Successful: $success_count/$total_count examples"

if [ $success_count -eq $total_count ]; then
    echo "🎉 All examples completed successfully!"
    echo ""
    echo "📁 Generated files can be found in:"
    echo "   • examples/1/ - Basic workflow example"
    echo "   • examples/advanced-scraping/ - Advanced scraping examples"
    echo ""
    echo "🔍 To explore the results:"
    echo "   • View HTML files in browser"
    echo "   • Check generated React/Vue/PHP components"
    echo "   • Compare original vs regenerated content"
    echo ""
    echo "📖 For detailed documentation, see:"
    echo "   • README.md - Overview and quick start"
    echo "   • docs/ - Comprehensive documentation"
    echo "   • examples/ - Example-specific documentation"
    
    exit 0
else
    failed_count=$((total_count - success_count))
    echo "❌ $failed_count examples failed"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   • Check that WhyML is properly installed: pip install -e ."
    echo "   • Ensure internet connection for web scraping"
    echo "   • Check logs above for specific error messages"
    echo "   • See docs/troubleshooting.md for common issues"
    
    exit 1
fi
