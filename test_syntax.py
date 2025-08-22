#!/usr/bin/env python3
"""
Test script to verify Python syntax checking for CI
"""

import os
import sys
import py_compile
from pathlib import Path

def check_python_syntax(directory="mcp-server"):
    """Check syntax of all Python files in directory"""
    
    errors = []
    checked = []
    
    # Find all Python files
    for root, dirs, files in os.walk(directory):
        # Skip virtual environments and cache
        dirs[:] = [d for d in dirs if d not in {'.venv', 'venv', '__pycache__', '.git'}]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    # Attempt to compile the file
                    py_compile.compile(filepath, doraise=True)
                    print(f"✅ {filepath}")
                    checked.append(filepath)
                except py_compile.PyCompileError as e:
                    print(f"❌ {filepath}: {e}")
                    errors.append((filepath, str(e)))
    
    # Summary
    print("\n" + "="*50)
    print(f"Checked {len(checked)} Python files")
    
    if errors:
        print(f"Found {len(errors)} syntax errors:")
        for filepath, error in errors:
            print(f"  - {filepath}")
        return 1
    else:
        print("✅ All Python files have valid syntax!")
        return 0

if __name__ == "__main__":
    sys.exit(check_python_syntax())
