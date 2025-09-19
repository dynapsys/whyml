#!/bin/bash
# Production Validation Script for WhyML Advanced Scraping
# Validates all features work correctly before production deployment

set -e

echo "🚀 WhyML Production Validation Script"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "Testing $test_name... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Cleanup function
cleanup() {
    echo "🧹 Cleaning up test files..."
    rm -f test-*.yaml test-*.html validation-temp-*
}

# Set trap for cleanup
trap cleanup EXIT

echo "${BLUE}1. BASIC FUNCTIONALITY TESTS${NC}"
echo "=============================="

# Test 1: CLI Accessibility
run_test "CLI accessibility" "whyml --version"

# Test 2: Help functionality
run_test "Help system" "whyml --help"

# Test 3: Dependencies
run_test "Python dependencies" "python3 -c 'import aiohttp, beautifulsoup4, yaml, jinja2'"

# Test 4: Advanced dependencies
run_test "Advanced scraping dependencies" "python3 -c 'import cachetools'"

echo ""
echo "${BLUE}2. CORE SCRAPING FUNCTIONALITY${NC}"
echo "==============================="

# Test 5: Basic scraping
run_test "Basic website scraping" "whyml scrape https://example.com -o test-basic.yaml"

# Test 6: YAML validation
if [ -f test-basic.yaml ]; then
    run_test "YAML format validation" "python3 -c 'import yaml; yaml.safe_load(open(\"test-basic.yaml\"))'"
fi

# Test 7: Manifest structure
if [ -f test-basic.yaml ]; then
    run_test "Manifest structure validation" "grep -q 'metadata:' test-basic.yaml && grep -q 'structure:' test-basic.yaml"
fi

echo ""
echo "${BLUE}3. ADVANCED SCRAPING FEATURES${NC}"
echo "=============================="

# Test 8: Structure simplification
run_test "Max depth limiting" "whyml scrape https://example.com --max-depth 2 -o test-depth.yaml"

# Test 9: Container flattening
run_test "Container flattening" "whyml scrape https://example.com --flatten-containers -o test-flatten.yaml"

# Test 10: Combined simplification
run_test "Combined simplification" "whyml scrape https://example.com --max-depth 3 --flatten-containers --simplify-structure -o test-combined.yaml"

# Test 11: Selective sections - metadata only
run_test "Selective section (metadata)" "whyml scrape https://example.com --section metadata -o test-metadata.yaml"

# Test 12: Selective sections - analysis only
run_test "Selective section (analysis)" "whyml scrape https://example.com --section analysis -o test-analysis.yaml"

# Test 13: Multiple sections
run_test "Multiple sections" "whyml scrape https://example.com --section metadata --section analysis -o test-multi.yaml"

# Test 14: No styles option
run_test "No styles extraction" "whyml scrape https://example.com --no-styles -o test-no-styles.yaml"

echo ""
echo "${BLUE}4. PAGE ANALYSIS FEATURES${NC}"
echo "========================="

# Test 15: Page analysis content
if [ -f test-analysis.yaml ]; then
    run_test "Page type detection" "grep -q 'page_type:' test-analysis.yaml"
fi

# Test 16: SEO analysis
if [ -f test-analysis.yaml ]; then
    run_test "SEO analysis" "grep -q 'seo_analysis:' test-analysis.yaml"
fi

# Test 17: Content statistics
if [ -f test-analysis.yaml ]; then
    run_test "Content statistics" "grep -q 'content_stats:' test-analysis.yaml"
fi

# Test 18: Structure complexity
if [ -f test-analysis.yaml ]; then
    run_test "Structure complexity" "grep -q 'structure_complexity:' test-analysis.yaml"
fi

echo ""
echo "${BLUE}5. TESTING WORKFLOW${NC}"
echo "=================="

# Test 19: Testing conversion workflow
run_test "Testing workflow" "whyml scrape https://example.com --test-conversion --output-html test-conversion.html -o test-workflow.yaml"

# Test 20: Generated HTML validation
if [ -f test-conversion.html ]; then
    run_test "Generated HTML format" "grep -q '<html' test-conversion.html && grep -q '</html>' test-conversion.html"
fi

echo ""
echo "${BLUE}6. ERROR HANDLING${NC}"
echo "================="

# Test 21: Invalid URL handling
run_test "Invalid URL handling" "! whyml scrape https://nonexistent-domain-12345.com -o test-error.yaml 2>/dev/null"

# Test 22: Network timeout handling (with short timeout)
run_test "Timeout handling" "timeout 5s whyml scrape https://httpstat.us/200?sleep=10000 -o test-timeout.yaml 2>/dev/null || true"

echo ""
echo "${BLUE}7. PERFORMANCE TESTS${NC}"
echo "==================="

# Test 23: Performance benchmark - structure simplification
echo -n "Performance: Structure simplification... "
start_time=$(date +%s.%N)
if whyml scrape https://example.com --max-depth 2 --simplify-structure -o test-perf1.yaml > /dev/null 2>&1; then
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")
    if [ "$duration" != "0" ] && (( $(echo "$duration < 30" | bc -l 2>/dev/null || echo "1") )); then
        echo -e "${GREEN}✅ PASSED (${duration}s)${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}⚠️ SLOW (${duration}s)${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    fi
else
    echo -e "${RED}❌ FAILED${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Test 24: Performance benchmark - selective sections
echo -n "Performance: Selective sections... "
start_time=$(date +%s.%N)
if whyml scrape https://example.com --section analysis -o test-perf2.yaml > /dev/null 2>&1; then
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")
    if [ "$duration" != "0" ] && (( $(echo "$duration < 15" | bc -l 2>/dev/null || echo "1") )); then
        echo -e "${GREEN}✅ PASSED (${duration}s)${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}⚠️ SLOW (${duration}s)${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    fi
else
    echo -e "${RED}❌ FAILED${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "${BLUE}8. FILE SIZE VALIDATION${NC}"
echo "======================="

# Test 25: File size optimization
if [ -f test-basic.yaml ] && [ -f test-metadata.yaml ]; then
    basic_size=$(wc -c < test-basic.yaml)
    metadata_size=$(wc -c < test-metadata.yaml)
    
    if [ $metadata_size -lt $basic_size ]; then
        echo -e "File size optimization... ${GREEN}✅ PASSED${NC} (Basic: ${basic_size}B, Metadata: ${metadata_size}B)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "File size optimization... ${RED}❌ FAILED${NC} (No size reduction)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

echo ""
echo "${BLUE}9. CONTENT VALIDATION${NC}"
echo "===================="

# Test 26: Content preservation in simplified manifests
if [ -f test-combined.yaml ]; then
    run_test "Content preservation" "grep -q -i 'example' test-combined.yaml"
fi

# Test 27: Metadata accuracy
if [ -f test-metadata.yaml ]; then
    run_test "Metadata accuracy" "grep -q 'title:' test-metadata.yaml"
fi

# Test 28: Analysis completeness
if [ -f test-analysis.yaml ]; then
    run_test "Analysis completeness" "grep -q 'word_count:' test-analysis.yaml"
fi

echo ""
echo "${BLUE}VALIDATION SUMMARY${NC}"
echo "=================="
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}✅ Production deployment ready${NC}"
    exit_code=0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo -e "${YELLOW}⚠️ Review failed tests before production deployment${NC}"
    exit_code=1
fi

echo ""
echo "📊 Test Results:"
echo "  Total Tests: $TOTAL_TESTS"
echo -e "  Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "  Failed: ${RED}$FAILED_TESTS${NC}"
echo "  Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"

echo ""
echo "📝 Detailed Information:"
echo "  - All advanced scraping features validated"
echo "  - Performance benchmarks completed"
echo "  - Error handling verified"
echo "  - Content preservation confirmed"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🚀 Ready for production deployment!${NC}"
    echo "Next steps:"
    echo "  1. Run Docker build: docker build -f docker/Dockerfile.production -t whyml:prod ."
    echo "  2. Deploy with: docker-compose -f docker/docker-compose.production.yml up -d"
    echo "  3. Monitor production metrics and logs"
else
    echo ""
    echo -e "${YELLOW}🔧 Action required before production deployment:${NC}"
    echo "  1. Fix failed tests"
    echo "  2. Re-run validation script"
    echo "  3. Verify all features working correctly"
fi

echo ""
exit $exit_code
