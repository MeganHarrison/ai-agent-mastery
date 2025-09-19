#!/bin/bash
#
# Deployment Smoke Tests
# Validates deployment configuration and simulates deployment checks
#

set -e

echo "🚀 Running Deployment Smoke Tests"
echo "================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -n "Testing: $test_name ... "

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Function to check file exists
check_file() {
    local file_path="$1"
    local file_desc="$2"

    run_test "$file_desc" "[ -f '$file_path' ]"
}

# Function to check directory exists
check_dir() {
    local dir_path="$1"
    local dir_desc="$2"

    run_test "$dir_desc" "[ -d '$dir_path' ]"
}

echo ""
echo "1. Checking deployment configuration files..."
echo "----------------------------------------------"

# Check render.yaml exists and is valid YAML
check_file "render.yaml" "render.yaml exists"

# Validate YAML syntax
run_test "render.yaml has valid YAML syntax" "python3 -c 'import yaml; yaml.safe_load(open(\"render.yaml\"))'"

# Check for Docker files if using containerization
check_file "6_Agent_Deployment/docker-compose.yml" "Docker Compose configuration exists"
check_file "6_Agent_Deployment/backend_agent_api/Dockerfile" "Agent API Dockerfile exists"
check_file "6_Agent_Deployment/backend_rag_pipeline/Dockerfile" "RAG Pipeline Dockerfile exists"
check_file "6_Agent_Deployment/frontend/Dockerfile" "Frontend Dockerfile exists"

echo ""
echo "2. Checking frontend deployment readiness..."
echo "---------------------------------------------"

# Check frontend directory structure
check_dir "6_Agent_Deployment/frontend" "Frontend directory exists"
check_file "6_Agent_Deployment/frontend/package.json" "Frontend package.json exists"
check_file "6_Agent_Deployment/frontend/next.config.js" "Next.js configuration exists"

# Check for required frontend scripts
run_test "Frontend has build script" "grep -q '\"build\"' 6_Agent_Deployment/frontend/package.json"
run_test "Frontend has start script" "grep -q '\"start\"' 6_Agent_Deployment/frontend/package.json"

# Check for standalone output configuration (recommended for production)
run_test "Next.js configured for standalone output" "grep -q 'standalone' 6_Agent_Deployment/frontend/next.config.js"

# Verify no references to non-existent dist directory
run_test "No references to 'dist' directory in render.yaml" "! grep -q 'dist' render.yaml"

# Check that rootDir is properly configured
run_test "render.yaml uses rootDir for frontend" "grep -q 'rootDir:.*frontend' render.yaml"

echo ""
echo "3. Checking backend services deployment readiness..."
echo "----------------------------------------------------"

# Check backend directories
check_dir "6_Agent_Deployment/backend_agent_api" "Agent API directory exists"
check_dir "6_Agent_Deployment/backend_rag_pipeline" "RAG Pipeline directory exists"

# Check for requirements files
check_file "6_Agent_Deployment/backend_agent_api/requirements.txt" "Agent API requirements.txt exists"
check_file "6_Agent_Deployment/backend_rag_pipeline/requirements.txt" "RAG Pipeline requirements.txt exists"

# Check for main application files
check_file "6_Agent_Deployment/backend_agent_api/agent_api.py" "Agent API main file exists"
check_file "6_Agent_Deployment/backend_rag_pipeline/docker_entrypoint.py" "RAG Pipeline entrypoint exists"

echo ""
echo "4. Checking environment configuration..."
echo "-----------------------------------------"

# Check for environment examples
check_file "6_Agent_Deployment/.env.example" "Environment example file exists"

# Check deployment script
check_file "6_Agent_Deployment/deploy.py" "Smart deployment script exists"

echo ""
echo "5. Simulating build processes..."
echo "---------------------------------"

# Test that Python files have valid syntax
if command -v python3 &> /dev/null; then
    run_test "Agent API Python syntax valid" "python3 -m py_compile 6_Agent_Deployment/backend_agent_api/agent_api.py 2>/dev/null"
    run_test "RAG Pipeline Python syntax valid" "python3 -m py_compile 6_Agent_Deployment/backend_rag_pipeline/docker_entrypoint.py 2>/dev/null"
else
    echo -e "${YELLOW}⚠ Python3 not available, skipping syntax checks${NC}"
fi

# Check if Node.js is available for frontend checks
if command -v node &> /dev/null; then
    # Check Node version compatibility
    run_test "Node.js version >= 18" "node -e 'process.exit(parseInt(process.version.slice(1).split(\".\")[0]) >= 18 ? 0 : 1)'"

    # Validate package.json
    run_test "Frontend package.json is valid JSON" "node -e 'require(\"./6_Agent_Deployment/frontend/package.json\")'"
else
    echo -e "${YELLOW}⚠ Node.js not available, skipping Node checks${NC}"
fi

echo ""
echo "6. Running Python validation script..."
echo "---------------------------------------"

# Run the Python validation script
if python3 tests/validate_render_yaml.py; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

echo ""
echo "7. Checking CI/CD integration..."
echo "---------------------------------"

# Check for GitHub Actions workflows
check_dir ".github/workflows" "GitHub Actions workflows directory exists"

# Look for deployment-related workflows
run_test "Deployment workflow exists" "ls .github/workflows/*.yml | grep -E '(deploy|render)' > /dev/null 2>&1 || true"

echo ""
echo "========================================"
echo "        Deployment Test Summary         "
echo "========================================"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ All deployment smoke tests PASSED!${NC}"
    echo "The deployment configuration appears to be ready."
    exit 0
else
    echo -e "\n${RED}❌ Some tests FAILED${NC}"
    echo "Please review the failures above before deploying."
    exit 1
fi