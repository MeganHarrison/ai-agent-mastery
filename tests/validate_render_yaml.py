#!/usr/bin/env python3
"""
Validate render.yaml configuration for deployment correctness.
Tests to ensure render.yaml is properly configured for Next.js deployment.
"""

import yaml
import sys
import os
from pathlib import Path

def load_render_yaml():
    """Load and parse the render.yaml file."""
    render_yaml_path = Path(__file__).parent.parent / 'render.yaml'

    if not render_yaml_path.exists():
        print(f"❌ render.yaml not found at {render_yaml_path}")
        return None

    try:
        with open(render_yaml_path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ Failed to parse render.yaml: {e}")
        return None

def validate_yaml_structure(config):
    """Validate the overall structure of render.yaml."""
    errors = []

    # Check for required top-level keys
    if 'services' not in config:
        errors.append("Missing 'services' key in render.yaml")

    return errors

def validate_frontend_service(config):
    """Validate the frontend service configuration."""
    errors = []
    warnings = []

    services = config.get('services', [])
    frontend_service = None

    # Find the frontend service
    for service in services:
        if service.get('name') == 'frontend':
            frontend_service = service
            break

    if not frontend_service:
        errors.append("No frontend service found in render.yaml")
        return errors, warnings

    # Check for rootDir configuration (best practice for monorepos)
    if 'rootDir' not in frontend_service:
        errors.append("Missing 'rootDir' configuration for frontend service")
    else:
        root_dir = frontend_service['rootDir']
        if not root_dir.startswith('6_Agent_Deployment/frontend'):
            warnings.append(f"Unexpected rootDir path: {root_dir}")

    # Validate build command
    build_cmd = frontend_service.get('buildCommand', '')
    if not build_cmd:
        errors.append("Missing 'buildCommand' for frontend service")
    elif 'npm run build' not in build_cmd:
        warnings.append("Build command should include 'npm run build' for Next.js")

    # Validate start command
    start_cmd = frontend_service.get('startCommand', '')
    if not start_cmd:
        errors.append("Missing 'startCommand' for frontend service")
    elif 'npm run start' not in start_cmd and 'next start' not in start_cmd:
        warnings.append("Start command should use 'npm run start' or 'next start' for production")

    # Check that we're NOT using cd commands (anti-pattern when rootDir is available)
    if 'cd ' in build_cmd or 'cd ' in start_cmd:
        errors.append("Using 'cd' commands when 'rootDir' should be used instead")

    # Verify service type
    if frontend_service.get('type') != 'web':
        warnings.append("Frontend service should be of type 'web'")

    # Check environment configuration
    if 'envVarGroups' not in frontend_service:
        warnings.append("No environment variable groups configured")

    return errors, warnings

def validate_backend_services(config):
    """Validate backend services configuration."""
    errors = []
    warnings = []

    services = config.get('services', [])

    # Check for agent-api service
    agent_api = next((s for s in services if s.get('name') == 'agent-api'), None)
    if agent_api:
        if 'rootDir' not in agent_api:
            warnings.append("agent-api service should use rootDir for consistency")

    # Check for rag-pipeline service
    rag_pipeline = next((s for s in services if s.get('name') == 'rag-pipeline'), None)
    if rag_pipeline:
        if 'rootDir' not in rag_pipeline:
            warnings.append("rag-pipeline service should use rootDir for consistency")

    return errors, warnings

def run_validation():
    """Run all validation checks."""
    print("🔍 Validating render.yaml configuration...\n")

    # Load the YAML file
    config = load_render_yaml()
    if not config:
        return False

    all_errors = []
    all_warnings = []

    # Run structural validation
    errors = validate_yaml_structure(config)
    all_errors.extend(errors)

    # Run frontend validation
    errors, warnings = validate_frontend_service(config)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # Run backend validation
    errors, warnings = validate_backend_services(config)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # Report results
    if all_errors:
        print("❌ Validation FAILED with errors:\n")
        for error in all_errors:
            print(f"  • {error}")
        print()

    if all_warnings:
        print("⚠️  Warnings:\n")
        for warning in all_warnings:
            print(f"  • {warning}")
        print()

    if not all_errors and not all_warnings:
        print("✅ render.yaml validation PASSED - all checks successful!")
    elif not all_errors:
        print("✅ render.yaml validation PASSED with warnings")

    return len(all_errors) == 0

def main():
    """Main entry point."""
    success = run_validation()

    # Additional checks for Next.js specific requirements
    print("\n🔍 Checking Next.js deployment requirements...\n")

    # Check if frontend directory exists
    frontend_dir = Path(__file__).parent.parent / '6_Agent_Deployment' / 'frontend'
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found at {frontend_dir}")
        success = False
    else:
        print(f"✅ Frontend directory exists at {frontend_dir}")

        # Check for package.json
        package_json = frontend_dir / 'package.json'
        if package_json.exists():
            print("✅ package.json found")

            # Verify Next.js build configuration
            import json
            try:
                with open(package_json, 'r') as f:
                    pkg = json.load(f)
                    scripts = pkg.get('scripts', {})

                    if 'build' not in scripts:
                        print("❌ Missing 'build' script in package.json")
                        success = False
                    else:
                        print("✅ Build script configured")

                    if 'start' not in scripts:
                        print("❌ Missing 'start' script in package.json")
                        success = False
                    else:
                        print("✅ Start script configured")

            except Exception as e:
                print(f"⚠️  Could not parse package.json: {e}")
        else:
            print("❌ package.json not found")
            success = False

        # Check for next.config.js
        next_config = frontend_dir / 'next.config.js'
        if next_config.exists():
            print("✅ next.config.js found")

            # Check for standalone output configuration
            with open(next_config, 'r') as f:
                content = f.read()
                if 'standalone' in content:
                    print("✅ Standalone output configured (optimized for production)")
                else:
                    print("⚠️  Consider setting output: 'standalone' for optimized production builds")
        else:
            next_config_mjs = frontend_dir / 'next.config.mjs'
            if next_config_mjs.exists():
                print("✅ next.config.mjs found")
            else:
                print("⚠️  No Next.js configuration file found")

    print("\n" + "="*60)
    if success:
        print("✅ All deployment validation checks PASSED!")
    else:
        print("❌ Some validation checks FAILED - review above output")
    print("="*60)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())