#!/usr/bin/env python3
"""
WordPress MCP Server - Quick Setup Script
For public users to easily configure their MCP server
"""

import os
import shutil
import sys
from pathlib import Path

def setup_mcp():
    """Guide users through MCP server setup"""
    print("=" * 50)
    print("WordPress MCP Server - Setup")
    print("=" * 50)
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('mcp-server'):
        print("❌ Error: Please run this script from the wordpress-mcp root directory")
        sys.exit(1)
    
    # Check for .env.example
    env_example = Path('mcp-server/.env.example')
    env_file = Path('mcp-server/.env')
    
    if not env_example.exists():
        env_example = Path('.env.example')
        if not env_example.exists():
            print("❌ Error: .env.example file not found")
            sys.exit(1)
    
    # Create .env if it doesn't exist
    if not env_file.exists():
        print("Creating .env configuration file...")
        shutil.copy(env_example, env_file)
        print("✅ Created mcp-server/.env")
        print()
        print("Next steps:")
        print("1. Edit mcp-server/.env with your WordPress credentials")
        print("2. Generate an Application Password in WordPress:")
        print("   - Go to Users → Your Profile")
        print("   - Find 'Application Passwords' section")
        print("   - Create new password named 'MCP Server'")
        print("   - Copy the password to your .env file")
        print()
        print("3. Install Python dependencies:")
        print("   pip install -r mcp-server/requirements.txt")
        print()
        print("4. Test your connection:")
        print("   cd mcp-server")
        print("   python test_connection.py")
    else:
        print("✅ .env file already exists")
        print()
        print("To test your connection:")
        print("   cd mcp-server")
        print("   python test_connection.py")
    
    print()
    print("=" * 50)
    print("For more information, see README.md")
    print("=" * 50)

if __name__ == "__main__":
    setup_mcp()
