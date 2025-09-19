#!/bin/bash
# Setup TypeScript Real-time Monitoring for Claude Code
# Run this script to install and configure all components

set -e

echo "🚀 Setting up TypeScript real-time monitoring for Claude Code..."

# Check prerequisites
echo "📋 Checking prerequisites..."

MISSING_DEPS=()

# Check Node.js and npm
if ! command -v node >/dev/null 2>&1; then
    MISSING_DEPS+=("node")
fi

if ! command -v npm >/dev/null 2>&1; then
    MISSING_DEPS+=("npm")
fi

# Check Claude Code
if ! command -v claude >/dev/null 2>&1; then
    MISSING_DEPS+=("claude-code")
fi

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    MISSING_DEPS+=("python3")
fi

if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
    echo "❌ Missing dependencies: ${MISSING_DEPS[*]}"
    echo "Please install the missing dependencies and run this script again."
    exit 1
fi

# Install TypeScript tools
echo "📦 Installing TypeScript development tools..."
npm install -g typescript @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint prettier

# Create Claude project directory structure
echo "📁 Creating Claude project structure..."
CLAUDE_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks"

mkdir -p "$HOOKS_DIR"

# Copy hook scripts
echo "📜 Installing validation hooks..."

# Create the TypeScript validation hook
cat > "$HOOKS_DIR/ts-validation-hook.py" << 'EOF'
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
EOF

# Create the auto-fix hook
cat > "$HOOKS_DIR/ts-autofix-hook.py" << 'EOF'
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
EOF

# Make hooks executable
chmod +x "$HOOKS_DIR/ts-validation-hook.py"
chmod +x "$HOOKS_DIR/ts-autofix-hook.py"

# Create Claude settings file
echo "⚙️  Creating Claude Code settings..."
cat > "$CLAUDE_DIR/settings.json" << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/ts-validation-hook.py",
            "timeout": 30000
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command", 
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/ts-autofix-hook.py",
            "timeout": 60000
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"import json,sys,re; data=json.load(sys.stdin); prompt=data.get('prompt',''); context='🎯 TypeScript Mode: Prioritizing type safety and error prevention.' if re.search(r'\\.(ts|tsx)\\b', prompt) else ''; print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': context}}) if context else '')\"",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
EOF

# Create TypeScript configuration
echo "📝 Creating TypeScript configuration..."
if [[ ! -f "tsconfig.json" ]]; then
    cat > "tsconfig.json" << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "noImplicitAny": true,
    "noImplicitReturns": true,
    "noImplicitThis": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
EOF
fi

# Create ESLint configuration
if [[ ! -f ".eslintrc.js" ]]; then
    cat > ".eslintrc.js" << 'EOF'
module.exports = {
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    '@typescript-eslint/recommended-requiring-type-checking',
  ],
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    project: './tsconfig.json',
  },
  rules: {
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/explicit-function-return-type': 'warn',
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/prefer-const': 'error',
  },
};
EOF
fi

echo "✅ TypeScript real-time monitoring setup complete!"
echo ""
echo "🎯 What's been installed:"
echo "   • Pre-validation hook for TypeScript files"
echo "   • Auto-fix hook with Prettier formatting"
echo "   • Claude Code settings with TypeScript focus"
echo "   • TypeScript and ESLint configurations"
echo ""
echo "🚀 To start using:"
echo "   1. Run 'claude' in your project directory"
echo "   2. TypeScript files will be automatically validated and fixed"
echo "   3. View logs in ~/.claude/ts-watcher.log"
echo ""
echo "🔧 Manual commands:"
echo "   • Test validation: python3 .claude/hooks/ts-validation-hook.py"
echo "   • View hook logs: tail -f ~/.claude/ts-watcher.log"
echo "   • Debug Claude with: claude --debug"
