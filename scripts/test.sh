#!/bin/bash
set -e

# sellm Test Runner Script
# Runs comprehensive e2e tests with proper dependency management

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
sellm Test Runner

Usage: $0 [OPTIONS]

OPTIONS:
  --install-deps    Install test dependencies
  --unit           Run unit tests only
  --integration    Run integration tests only  
  --performance    Run performance tests only
  --coverage       Run with coverage reporting
  --verbose        Verbose output
  --help           Show this help

EXAMPLES:
  $0                      # Run all tests
  $0 --install-deps       # Install dependencies then run tests
  $0 --unit --verbose     # Run unit tests with verbose output
  $0 --coverage           # Run tests with coverage

EOF
}

# Install test dependencies
install_deps() {
    log_step "Installing test dependencies..."
    
    cd "$PROJECT_DIR"
    
    # Install pytest and related packages
    pip install pytest pytest-asyncio pytest-cov || {
        log_warn "Standard pip install failed, trying with --break-system-packages..."
        pip install pytest pytest-asyncio pytest-cov --break-system-packages
    }
    
    # Install sellm dependencies if not already installed
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt || pip install -r requirements.txt --break-system-packages
    fi
    
    # Install sellm in development mode
    pip install -e . || pip install -e . --break-system-packages
    
    log_info "✅ Test dependencies installed"
}

# Check if test dependencies are available
check_deps() {
    log_step "Checking test dependencies..."
    
    python3 -c "import pytest, pytest_asyncio" 2>/dev/null || {
        log_warn "Test dependencies not found"
        return 1
    }
    
    log_info "✅ Test dependencies OK"
    return 0
}

# Run tests
run_tests() {
    local test_args=()
    local test_path="tests/"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --unit)
                test_args+=("-k" "not integration and not performance")
                shift
                ;;
            --integration)
                test_args+=("-k" "integration")
                shift
                ;;
            --performance)
                test_args+=("-k" "performance")
                shift
                ;;
            --coverage)
                test_args+=("--cov=." "--cov-report=html" "--cov-report=term")
                shift
                ;;
            --verbose)
                test_args+=("-v" "-s")
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    log_step "Running sellm tests..."
    
    cd "$PROJECT_DIR"
    
    # Add default verbose output if no args specified
    if [ ${#test_args[@]} -eq 0 ]; then
        test_args+=("-v")
    fi
    
    log_info "Test command: pytest ${test_args[*]} $test_path"
    
    # Run pytest
    python3 -m pytest "${test_args[@]}" "$test_path" || {
        log_error "Some tests failed"
        return 1
    }
    
    log_info "✅ All tests passed"
}

# Main execution
main() {
    log_info "🧪 sellm Test Runner"
    
    local install_deps_flag=false
    local remaining_args=()
    
    # Parse install-deps flag first
    for arg in "$@"; do
        if [[ "$arg" == "--install-deps" ]]; then
            install_deps_flag=true
        elif [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
            show_help
            exit 0
        else
            remaining_args+=("$arg")
        fi
    done
    
    # Install dependencies if requested
    if [ "$install_deps_flag" = true ]; then
        install_deps
    else
        # Check if dependencies are available
        if ! check_deps; then
            log_warn "Test dependencies missing. Run with --install-deps to install them."
            log_info "Or run: $0 --install-deps"
            exit 1
        fi
    fi
    
    # Run tests
    run_tests "${remaining_args[@]}"
}

# Execute main function
main "$@"
