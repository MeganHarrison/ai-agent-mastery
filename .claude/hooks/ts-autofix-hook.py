#!/usr/bin/env python3
"""
TypeScript Auto-Fix PostToolUse Hook for Claude Code
Automatically fixes common TypeScript errors after file operations
"""
import json
import sys
import subprocess
import os

def auto_fix_typescript(file_path: str) -> tuple[bool, list[str]]:
    """Attempt to auto-fix TypeScript issues"""
    fixes_applied = []
    success = True
    
    try:
        # Run Prettier for formatting
        prettier_result = subprocess.run([
            'npx', 'prettier', 
            '--write',
            '--parser', 'typescript',
            file_path
        ], capture_output=True, text=True, timeout=10)
        
        if prettier_result.returncode == 0:
            fixes_applied.append("Applied Prettier formatting")
        
        # Run TypeScript compiler to check for remaining errors
        tsc_result = subprocess.run([
            'npx', 'tsc',
            '--noEmit',
            '--skipLibCheck',
            file_path
        ], capture_output=True, text=True, timeout=15)
        
        if tsc_result.returncode != 0:
            success = False
            fixes_applied.append(f"Remaining TypeScript errors detected")
    
    except Exception as e:
        success = False
        fixes_applied.append(f"Auto-fix failed: {str(e)}")
    
    return success, fixes_applied

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(1)
    
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    tool_response = input_data.get("tool_response", {})
    
    # Only process successful TypeScript file operations
    if tool_name not in ["Write", "Edit", "MultiEdit"]:
        sys.exit(0)
    
    if not tool_response.get("success", False):
        sys.exit(0)
    
    file_path = tool_input.get("file_path", "")
    
    # Check if it's a TypeScript file
    if not file_path.endswith(('.ts', '.tsx')) or not os.path.exists(file_path):
        sys.exit(0)
    
    # Attempt auto-fixes
    success, fixes_applied = auto_fix_typescript(file_path)
    
    if fixes_applied:
        print(f"Applied fixes to {file_path}: {', '.join(fixes_applied)}", file=sys.stderr)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
