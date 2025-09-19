# Deployment Validation Tests

This directory contains tests to validate deployment configurations, particularly for Render deployments.

## Test Files

### `validate_render_yaml.py`
Python script that validates the `render.yaml` configuration file:
- Checks YAML syntax and structure
- Validates service configurations
- Ensures proper use of `rootDir` instead of `cd` commands
- Verifies Next.js deployment requirements
- Checks for standalone output configuration

### `test_deployment_smoke.sh`
Bash script that runs comprehensive smoke tests:
- Verifies all deployment files exist
- Checks directory structure for frontend and backend
- Validates configuration files
- Runs Python validation scripts
- Provides detailed test summary

### `requirements-test.txt`
Python dependencies needed for running the validation tests.

## Running the Tests

### Python Validation
```bash
# Install dependencies
pip install -r tests/requirements-test.txt

# Run validation
python tests/validate_render_yaml.py
```

### Smoke Tests
```bash
# Make script executable (if needed)
chmod +x tests/test_deployment_smoke.sh

# Run smoke tests
./tests/test_deployment_smoke.sh
```

## CI/CD Integration

To add these tests to your CI/CD pipeline, add the following to your GitHub Actions workflow:

```yaml
- name: Install test dependencies
  run: pip install -r tests/requirements-test.txt

- name: Validate render.yaml
  run: python tests/validate_render_yaml.py

- name: Run deployment smoke tests
  run: |
    chmod +x tests/test_deployment_smoke.sh
    ./tests/test_deployment_smoke.sh
```

## Expected Output

When all tests pass:
- ✅ All validation checks will show as passed
- ✅ Deployment configuration will be confirmed as ready
- ✅ Exit code will be 0

When tests fail:
- ❌ Failed checks will be clearly indicated
- ⚠️ Warnings will suggest improvements
- ❌ Exit code will be non-zero

## Test Coverage

These tests validate:
1. **YAML Configuration**: Syntax and structure of render.yaml
2. **Service Configuration**: Proper setup for frontend and backend services
3. **Directory Structure**: All required directories and files exist
4. **Build Scripts**: package.json contains necessary scripts
5. **Next.js Setup**: Proper configuration for production deployment
6. **Docker Setup**: Dockerfiles and compose configurations
7. **Environment Config**: .env.example and deployment scripts