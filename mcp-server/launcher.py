#!/usr/bin/env python
"""
WordPress MCP Server Launcher
Handles dependency installation for DXT package
"""

import subprocess
import sys
import os
from pathlib import Path

# Print debug info
print("WordPress MCP Server launcher starting...", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)

# Check Python version
if sys.version_info < (3, 9):
    print("\n" + "="*60, file=sys.stderr)
    print("ERROR: Python 3.9 or higher is required", file=sys.stderr)
    print(f"Current version: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", file=sys.stderr)
    print("\nPlease install Python 3.9+ from https://python.org", file=sys.stderr)
    print("="*60 + "\n", file=sys.stderr)
    sys.exit(1)

# Change to script directory
script_dir = Path(__file__).parent
os.chdir(script_dir)

def install_dependencies():
    """Install required dependencies"""
    required = [
        ("mcp", "mcp"),
        ("dotenv", "python-dotenv"),
        ("aiohttp", "aiohttp"),
        ("jsonschema", "jsonschema")
    ]
    
    missing = []
    for import_name, package_name in required:
        try:
            __import__(import_name)
            print(f"✓ {package_name} already installed", file=sys.stderr)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}", file=sys.stderr)
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                *missing,
                "--quiet", "--disable-pip-version-check"
            ])
            print("✓ All dependencies installed", file=sys.stderr)
        except subprocess.CalledProcessError:
            # Try with --user flag
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    *missing,
                    "--user", "--quiet", "--disable-pip-version-check"
                ])
                print("✓ All dependencies installed (user)", file=sys.stderr)
            except Exception as e:
                print(f"⚠ Installation failed: {e}", file=sys.stderr)

def main():
    """Main launcher function"""
    # Install dependencies
    print("Checking dependencies...", file=sys.stderr)
    install_dependencies()
    
    # Now try to run the server
    try:
        print("Starting WordPress MCP Server...", file=sys.stderr)
        
        # Import and run the server
        sys.path.insert(0, str(script_dir))
        from server import main as server_main
        import asyncio
        asyncio.run(server_main())
        
    except ImportError as e:
        print(f"Import error: {e}", file=sys.stderr)
        print("\nTrying to install missing package...", file=sys.stderr)
        
        # Try to identify and install the missing package
        missing = str(e).split("'")[1] if "'" in str(e) else None
        if missing:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    missing,
                    "--quiet", "--disable-pip-version-check"
                ])
                # Try again
                from server import main as server_main
                import asyncio
                asyncio.run(server_main())
            except:
                print(f"Could not install {missing}", file=sys.stderr)
                sys.exit(1)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
