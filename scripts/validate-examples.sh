#!/bin/bash
# Examples Validation Script for WhyML Advanced Scraping
# Tests all documentation examples and user scenarios work correctly

set -e

echo "📚 WhyML Examples Validation Script"
echo "==================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_EXAMPLES=0
PASSED_EXAMPLES=0
FAILED_EXAMPLES=0

# Function to run an example test
run_example() {
    local example_name="$1"
    local example_command="$2"
    local validation_check="$3"
    
    TOTAL_EXAMPLES=$((TOTAL_EXAMPLES + 1))
    echo -n "Testing example: $example_name... "
    
    # Run the example command
    if eval "$example_command" > /dev/null 2>&1; then
        # Run validation check if provided
        if [ -n "$validation_check" ]; then
            if eval "$validation_check" > /dev/null 2>&1; then
                echo -e "${GREEN}✅ PASSED${NC}"
                PASSED_EXAMPLES=$((PASSED_EXAMPLES + 1))
                return 0
            else
                echo -e "${RED}❌ FAILED (validation)${NC}"
                FAILED_EXAMPLES=$((FAILED_EXAMPLES + 1))
                return 1
            fi
        else
            echo -e "${GREEN}✅ PASSED${NC}"
            PASSED_EXAMPLES=$((PASSED_EXAMPLES + 1))
            return 0
        fi
    else
        echo -e "${RED}❌ FAILED (execution)${NC}"
        FAILED_EXAMPLES=$((FAILED_EXAMPLES + 1))
        return 1
    fi
}

# Cleanup function
cleanup() {
    echo "🧹 Cleaning up example test files..."
    rm -f example-*.yaml example-*.html temp-*
}

# Set trap for cleanup
trap cleanup EXIT

echo "${BLUE}1. README.md EXAMPLES${NC}"
echo "===================="

# Example 1: Basic scraping from README
run_example "Basic scraping" \
    "whyml scrape https://example.com -o example-basic.yaml" \
    "test -f example-basic.yaml && grep -q 'metadata:' example-basic.yaml"

# Example 2: Structure simplification from README
run_example "Max depth limiting" \
    "whyml scrape https://example.com --max-depth 3 -o example-depth.yaml" \
    "test -f example-depth.yaml"

# Example 3: Container flattening from README
run_example "Container flattening" \
    "whyml scrape https://example.com --flatten-containers -o example-flatten.yaml" \
    "test -f example-flatten.yaml"

# Example 4: Combined simplification from README
run_example "Combined simplification" \
    "whyml scrape https://example.com --max-depth 2 --flatten-containers --simplify-structure -o example-combined.yaml" \
    "test -f example-combined.yaml"

echo ""
echo "${BLUE}2. SELECTIVE SECTION EXAMPLES${NC}"
echo "=============================="

# Example 5: Metadata only from README
run_example "Metadata section only" \
    "whyml scrape https://example.com --section metadata -o example-metadata.yaml" \
    "test -f example-metadata.yaml && grep -q 'metadata:' example-metadata.yaml && ! grep -q 'structure:' example-metadata.yaml"

# Example 6: Analysis only from README
run_example "Analysis section only" \
    "whyml scrape https://example.com --section analysis -o example-analysis.yaml" \
    "test -f example-analysis.yaml && grep -q 'analysis:' example-analysis.yaml"

# Example 7: Multiple sections from README
run_example "Multiple sections" \
    "whyml scrape https://example.com --section metadata --section analysis -o example-multi.yaml" \
    "test -f example-multi.yaml && grep -q 'metadata:' example-multi.yaml && grep -q 'analysis:' example-multi.yaml"

echo ""
echo "${BLUE}3. TESTING WORKFLOW EXAMPLES${NC}"
echo "============================"

# Example 8: Testing workflow from README
run_example "Testing conversion workflow" \
    "whyml scrape https://example.com --test-conversion --output-html example-test.html -o example-workflow.yaml" \
    "test -f example-workflow.yaml && test -f example-test.html"

echo ""
echo "${BLUE}4. CLI DOCUMENTATION EXAMPLES${NC}"
echo "============================="

# Examples from docs/cli/scrape.md

# Example 9: Website refactoring scenario
run_example "Website refactoring scenario" \
    "whyml scrape https://example.com --max-depth 2 --simplify-structure --section structure -o example-refactor.yaml" \
    "test -f example-refactor.yaml && grep -q 'structure:' example-refactor.yaml"

# Example 10: SEO analysis scenario
run_example "SEO analysis scenario" \
    "whyml scrape https://example.com --section analysis --section metadata -o example-seo.yaml" \
    "test -f example-seo.yaml && grep -q 'analysis:' example-seo.yaml"

# Example 11: Content migration scenario
run_example "Content migration testing" \
    "whyml scrape https://example.com --test-conversion --max-depth 3 --output-html example-migration.html -o example-migration.yaml" \
    "test -f example-migration.yaml && test -f example-migration.html"

echo ""
echo "${BLUE}5. ADVANCED SCRAPING EXAMPLES${NC}"
echo "=============================="

# Examples from examples/advanced-scraping/README.md

# Example 12: Performance optimization
run_example "Performance optimization" \
    "whyml scrape https://example.com --section metadata --no-styles -o example-perf.yaml" \
    "test -f example-perf.yaml"

# Example 13: Competitive analysis
run_example "Competitive analysis setup" \
    "whyml scrape https://example.com --section analysis --section metadata --flatten-containers -o example-competitive.yaml" \
    "test -f example-competitive.yaml"

# Example 14: Quality assurance workflow
run_example "QA workflow" \
    "whyml scrape https://example.com --test-conversion --simplify-structure --output-html example-qa.html -o example-qa.yaml" \
    "test -f example-qa.yaml && test -f example-qa.html"

echo ""
echo "${BLUE}6. ERROR HANDLING EXAMPLES${NC}"
echo "=========================="

# Example 15: No styles extraction
run_example "No styles extraction" \
    "whyml scrape https://example.com --no-styles -o example-no-styles.yaml" \
    "test -f example-no-styles.yaml"

# Example 16: Script extraction
run_example "Script extraction" \
    "whyml scrape https://example.com --extract-scripts -o example-scripts.yaml" \
    "test -f example-scripts.yaml"

# Example 17: No semantic preservation
run_example "No semantic preservation" \
    "whyml scrape https://example.com --no-preserve-semantic --simplify-structure -o example-no-semantic.yaml" \
    "test -f example-no-semantic.yaml"

echo ""
echo "${BLUE}7. USER TESTING GUIDE EXAMPLES${NC}"
echo "=============================="

# Examples from docs/USER_TESTING_GUIDE.md

# Example 18: Structure simplification test
run_example "Structure simplification test" \
    "whyml scrape https://example.com --max-depth 2 --flatten-containers -o example-struct-test.yaml" \
    "test -f example-struct-test.yaml"

# Example 19: Selective sections test  
run_example "Selective sections test" \
    "whyml scrape https://example.com --section metadata --section structure -o example-select-test.yaml" \
    "test -f example-select-test.yaml && grep -q 'metadata:' example-select-test.yaml && grep -q 'structure:' example-select-test.yaml"

# Example 20: Page analysis test
run_example "Page analysis test" \
    "whyml scrape https://example.com --section analysis -o example-page-test.yaml" \
    "test -f example-page-test.yaml && grep -q 'page_type:' example-page-test.yaml"

echo ""
echo "${BLUE}8. INSTALLATION EXAMPLES${NC}"
echo "======================="

# Examples from INSTALLATION.md

# Example 21: Basic installation validation
run_example "CLI help functionality" \
    "whyml --help" \
    ""

# Example 22: Version check
run_example "Version information" \
    "whyml --version" \
    ""

# Example 23: Advanced usage example
run_example "Advanced usage from installation guide" \
    "whyml scrape https://example.com --section analysis --max-depth 2 -o example-install.yaml" \
    "test -f example-install.yaml"

echo ""
echo "${BLUE}9. FILE SIZE VALIDATION${NC}"
echo "======================"

# Validate that selective sections actually reduce file sizes
if [ -f example-basic.yaml ] && [ -f example-metadata.yaml ]; then
    basic_size=$(wc -c < example-basic.yaml)
    metadata_size=$(wc -c < example-metadata.yaml)
    
    if [ $metadata_size -lt $basic_size ]; then
        echo -e "File size optimization validation... ${GREEN}✅ PASSED${NC}"
        echo "  Basic manifest: ${basic_size} bytes"
        echo "  Metadata only: ${metadata_size} bytes" 
        echo "  Reduction: $(( (basic_size - metadata_size) * 100 / basic_size ))%"
        PASSED_EXAMPLES=$((PASSED_EXAMPLES + 1))
    else
        echo -e "File size optimization validation... ${RED}❌ FAILED${NC}"
        FAILED_EXAMPLES=$((FAILED_EXAMPLES + 1))
    fi
    TOTAL_EXAMPLES=$((TOTAL_EXAMPLES + 1))
fi

echo ""
echo "${BLUE}10. CONTENT VALIDATION${NC}"
echo "====================="

# Validate content preservation in different scenarios
content_tests=(
    "example-basic.yaml:title"
    "example-analysis.yaml:word_count"
    "example-metadata.yaml:title"
    "example-combined.yaml:metadata"
)

for test in "${content_tests[@]}"; do
    filename="${test%:*}"
    field="${test#*:}"
    
    if [ -f "$filename" ]; then
        if grep -q "$field" "$filename"; then
            echo -e "Content preservation ($filename - $field)... ${GREEN}✅ PASSED${NC}"
            PASSED_EXAMPLES=$((PASSED_EXAMPLES + 1))
        else
            echo -e "Content preservation ($filename - $field)... ${RED}❌ FAILED${NC}"
            FAILED_EXAMPLES=$((FAILED_EXAMPLES + 1))
        fi
    else
        echo -e "Content preservation ($filename - $field)... ${YELLOW}⚠️ SKIPPED${NC} (file not found)"
        FAILED_EXAMPLES=$((FAILED_EXAMPLES + 1))
    fi
    TOTAL_EXAMPLES=$((TOTAL_EXAMPLES + 1))
done

echo ""
echo "${BLUE}EXAMPLES VALIDATION SUMMARY${NC}"
echo "=========================="
echo ""

if [ $FAILED_EXAMPLES -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL EXAMPLES PASSED!${NC}"
    echo -e "${GREEN}✅ Documentation examples are working correctly${NC}"
    exit_code=0
else
    echo -e "${RED}❌ Some examples failed${NC}"
    echo -e "${YELLOW}⚠️ Review failed examples and update documentation${NC}"
    exit_code=1
fi

echo ""
echo "📊 Examples Results:"
echo "  Total Examples Tested: $TOTAL_EXAMPLES"
echo -e "  Passed: ${GREEN}$PASSED_EXAMPLES${NC}"
echo -e "  Failed: ${RED}$FAILED_EXAMPLES${NC}"
echo "  Success Rate: $(( PASSED_EXAMPLES * 100 / TOTAL_EXAMPLES ))%"

echo ""
echo "📚 Documentation Coverage:"
echo "  ✅ README.md examples"
echo "  ✅ CLI documentation examples"
echo "  ✅ Advanced scraping examples"
echo "  ✅ User testing guide examples"
echo "  ✅ Installation guide examples"

if [ $FAILED_EXAMPLES -eq 0 ]; then
    echo ""
    echo -e "${GREEN}📖 All documentation examples are validated and working!${NC}"
    echo "Users can confidently follow the documentation examples."
else
    echo ""
    echo -e "${YELLOW}📝 Action required:${NC}"
    echo "  1. Fix failing documentation examples"
    echo "  2. Update examples in relevant documentation files"
    echo "  3. Re-run this validation script"
    echo "  4. Ensure all examples work on fresh installations"
fi

echo ""
echo "🎯 Next steps:"
echo "  1. Run full production validation: ./scripts/validate-production.sh"
echo "  2. Run performance benchmarks: python3 scripts/performance-benchmark.py"
echo "  3. Review production deployment checklist"

echo ""
exit $exit_code
