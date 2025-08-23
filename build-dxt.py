#!/usr/bin/env python3
"""
WordPress MCP - DXT Package Builder 🚀

Creates a .dxt package for Anthropic Desktop Extensions.
This script packages everything needed for one-click Claude Desktop installation.

Usage: python build-dxt.py

Made with ❤️ by Breuk & Claude
Intelligence Combined 🧠
"""

import os
import json
import shutil
import tarfile
import tempfile
from pathlib import Path

VERSION = "1.1.1"
OUTPUT_NAME = f"wordpress-mcp-v{VERSION}.dxt"

def create_dxt_package():
    """Create the DXT package for WordPress MCP"""
    
    print("=====================================")
    print("📦 Building WordPress MCP DXT Package")
    print("=====================================")
    print()
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"Creating package structure in {temp_dir}...")
        
        # Create directory structure
        (temp_path / "mcp-server").mkdir()
        (temp_path / "wp-mcp-plugin").mkdir()
        
        # Copy manifest
        print("📄 Copying manifest...")
        shutil.copy2("dxt-manifest.json", temp_path / "manifest.json")
        
        # Copy MCP server files
        print("🐍 Copying MCP server files...")
        mcp_source = Path("mcp-server")
        mcp_dest = temp_path / "mcp-server"
        
        # Copy Python files
        for py_file in mcp_source.glob("**/*.py"):
            rel_path = py_file.relative_to(mcp_source)
            dest_file = mcp_dest / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(py_file, dest_file)
        
        # Copy requirements and example env
        if (mcp_source / "requirements.txt").exists():
            shutil.copy2(mcp_source / "requirements.txt", mcp_dest / "requirements.txt")
        if (mcp_source / ".env.example").exists():
            shutil.copy2(mcp_source / ".env.example", mcp_dest / ".env.example")
        
        # Copy WordPress plugin files
        print("📝 Copying WordPress plugin...")
        wp_source = Path("wp-mcp-plugin")
        wp_dest = temp_path / "wp-mcp-plugin"
        
        # Copy PHP files and directories
        for item in wp_source.iterdir():
            if item.is_file() and item.suffix in ['.php', '.txt', '.md']:
                shutil.copy2(item, wp_dest / item.name)
            elif item.is_dir() and item.name not in ['vendor', 'node_modules', '.git']:
                shutil.copytree(item, wp_dest / item.name, dirs_exist_ok=True)
        
        # Copy documentation
        print("📚 Copying documentation...")
        for doc in ["README.md", "LICENSE", "QUICKSTART.md", "CHANGELOG.md"]:
            if Path(doc).exists():
                shutil.copy2(doc, temp_path / doc)
        
        # Create the DXT package (tar.gz)
        print()
        print("🎁 Creating DXT package...")
        with tarfile.open(OUTPUT_NAME, "w:gz") as tar:
            for item in temp_path.iterdir():
                tar.add(item, arcname=item.name)
        
    # Verify the package
    if Path(OUTPUT_NAME).exists():
        size_mb = Path(OUTPUT_NAME).stat().st_size / (1024 * 1024)
        print(f"✅ Created {OUTPUT_NAME} ({size_mb:.2f} MB)")
    else:
        print("❌ Failed to create package")
        return False
    
    print()
    print("=====================================")
    print("📦 DXT Package Build Complete!")
    print("=====================================")
    print()
    print(f"Package: {OUTPUT_NAME}")
    print(f"Version: {VERSION}")
    print()
    print("Next steps:")
    print("1. Test locally: dxt install " + OUTPUT_NAME)
    print("2. Submit to Anthropic via their submission process")
    print("3. Share with the community!")
    print()
    print('"Intelligence Combined 🧠"')
    print("=====================================")
    
    return True

if __name__ == "__main__":
    create_dxt_package()
