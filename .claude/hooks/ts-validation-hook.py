#!/usr/bin/env python3
"""
TypeScript Pre-Validation Hook for Claude Code
Prevents TypeScript errors by validating code before execution
"""
import json
import sys
import subprocess
import os
import tempfile
from pathlib import Path

def check_typescript_errors(file_path: str, content: str) -> list[str]:
    """Check TypeScript content for errors using tsc"""
    errors = []
    
    # Create temporary file for validation
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Run TypeScript compiler in check mode
        result = subprocess.run([
            'npx', 'tsc', 
            '--noEmit',  # Don't generate output files
            '--skipLibCheck',  # Skip lib checking for speed
            '--strict',  # Enable strict mode
            temp_file_path
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            # Parse TypeScript errors
            error_lines = result.stderr.strip().split('\n')
            for line in error_lines:
                if line.strip() and not line.startswith('Found'):
                    errors.append(line.strip())
    
    except subprocess.TimeoutExpired:
        errors.append("TypeScript compilation timed out")
    except FileNotFoundError:
        errors.append("TypeScript compiler (tsc) not found. Install with: npm install -g typescript")
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except:
            pass
    
    return errors

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    
    # Only validate TypeScript-related operations
    if tool_name not in ["Write", "Edit", "MultiEdit"]:
        sys.exit(0)
    
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")
    
    # Check if it's a TypeScript file
    if not file_path.endswith(('.ts', '.tsx')):
        sys.exit(0)
    
    # Check for TypeScript compilation errors
    ts_errors = check_typescript_errors(file_path, content)
    
    if ts_errors:
        error_summary = f"TypeScript validation failed for {file_path}:\n" + "\n".join(f"• {error}" for error in ts_errors)
        
        # Block the tool call and ask Claude to fix issues
        output = {
            "decision": "block",
            "reason": f"TypeScript validation failed. Please fix these issues first:\n{error_summary}",
        }
        print(json.dumps(output))
        sys.exit(0)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
